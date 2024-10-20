# backend/app/main.py

import asyncio
import logging
import uuid
from typing import Dict

from fastapi import (Depends, FastAPI, HTTPException, WebSocket,
                     WebSocketDisconnect)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, database, models, schemas

app = FastAPI()

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS設定
origins = [
    "http://localhost:3000",  # フロントエンドのURL
    # 必要に応じて他のオリジンを追加
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 必要なオリジンのみ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベースの初期化


@app.on_event("startup")
def on_startup():
    import app.init_db
    app.init_db.init_db()

# Dependency


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket connection manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info(f"WebSocket connected: device_id={device_id}")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"WebSocket disconnected: device_id={device_id}")

    async def send_message(self, device_id: str, message: str):
        websocket = self.active_connections.get(device_id)
        if websocket:
            await websocket.send_text(message)
            logger.info(f"Sent message to device_id={device_id}: {message}")


manager = ConnectionManager()


@app.post("/register-device", response_model=schemas.DeviceRegisterResponse)
def register_device(
    request: schemas.DeviceRegisterRequest, db: Session = Depends(get_db)
):
    """
    デバイスを登録し、一意のデバイスIDとランダムなお題を返すエンドポイント
    """
    db_device = crud.create_device(db)
    logger.info(f"Device registered: {db_device.device_id}")
    db_topic = crud.get_random_topic(db)
    if not db_topic:
        logger.error("Failed to retrieve a random topic.")
        raise HTTPException(status_code=500, detail="お題の取得に失敗しました")
    topic_name = db_topic.name
    logger.info(
        f"Assigned topic '{topic_name}' to device '{db_device.device_id}'")
    return schemas.DeviceRegisterResponse(
        success=True, device_id=db_device.device_id, topic=topic_name
    )


@app.post("/verify-device", response_model=schemas.DeviceVerifyResponse)
def verify_device(
    request: schemas.DeviceVerifyRequest, db: Session = Depends(get_db)
):
    """
    デバイスIDがデータベースに存在するかを確認し、存在すればデバイスIDと現在のお題を返す
    """
    device_id = request.device_id
    db_device = crud.get_device(db, device_id)
    if not db_device:
        return schemas.DeviceVerifyResponse(
            success=False, detail="デバイスIDが存在しません。"
        )
    # Get latest image assigned to device via latest image
    latest_image = db.query(models.Image).filter(
        models.Image.device_id == device_id).order_by(models.Image.request_time.desc()).first()
    if latest_image and latest_image.topic:
        topic_name = latest_image.topic.name
    else:
        # Assign a new topic if none exists
        db_topic = crud.get_random_topic(db)
        if not db_topic:
            raise HTTPException(status_code=500, detail="お題の取得に失敗しました")
        topic_name = db_topic.name
    return schemas.DeviceVerifyResponse(
        success=True, device_id=db_device.device_id, topic=topic_name
    )


@app.post("/get-new-topic", response_model=schemas.GetNewTopicResponse)
def get_new_topic(
    request: schemas.GetNewTopicRequest, db: Session = Depends(get_db)
):
    """
    指定されたデバイスIDに新しいお題を割り当てて返すエンドポイント
    """
    device_id = request.device_id
    db_device = crud.get_device(db, device_id)
    if not db_device:
        raise HTTPException(status_code=400, detail="デバイスIDが無効です。")

    db_topic = crud.get_random_topic(db)
    if not db_topic:
        raise HTTPException(status_code=500, detail="お題の取得に失敗しました。")

    # Optionally, create a new Image entry with the new topic
    db_image = crud.create_image(
        db, device_id, db_topic.id, canvas_image_filename=""
    )
    logger.info(
        f"Assigned new topic '{db_topic.name}' to device '{device_id}', Image ID: {db_image.id}")

    return schemas.GetNewTopicResponse(
        success=True, topic=db_topic.name
    )


@app.post("/save-canvas", response_model=schemas.SaveCanvasResponse)
async def save_canvas(request: schemas.SaveCanvasRequest, db: Session = Depends(get_db)):
    """
    キャンバス画像を保存し、画像生成プロセスを開始するエンドポイント
    """
    logger.info(
        f"Received /save-canvas request: device_id={request.device_id}")

    # デバイスの存在確認
    db_device = crud.get_device(db, request.device_id)
    if not db_device:
        logger.error(f"デバイスID {request.device_id} が存在しません。")
        raise HTTPException(status_code=400, detail="デバイスIDが無効です。")

    # 画像の保存
    import app.utils
    SAVED_IMAGES_DIR = database.saved_images_dir
    file_path = app.utils.save_image(
        request.image_data, directory=SAVED_IMAGES_DIR)
    if not file_path:
        logger.error("画像の保存に失敗しました。")
        raise HTTPException(
            status_code=400, detail="画像の保存に失敗しました。データ形式を確認してください。")

    logger.info(f"画像を保存しました: {file_path}")

    # ランダムなお題の取得
    db_topic = crud.get_random_topic(db)
    if not db_topic:
        logger.error("お題の取得に失敗しました。")
        raise HTTPException(
            status_code=500, detail="お題の取得に失敗しました。データベースを確認してください。")

    # データベースに画像情報を保存
    db_image = crud.create_image(
        db, request.device_id, db_topic.id, file_path.name)
    logger.info(f"Image entry created: {db_image.id}")

    # 非同期で画像生成プロセスを開始
    asyncio.create_task(process_image_generation(
        db_image.id, request.device_id))

    return schemas.SaveCanvasResponse(
        success=True, file_name=db_image.canvas_image_filename
    )


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str, db: Session = Depends(get_db)):
    try:
        # Verify device_id before accepting WebSocket connection
        db_device = crud.get_device(db, device_id)
        if not db_device:
            await websocket.close(code=1008, reason="Invalid device_id")
            logger.warning(
                f"WebSocket connection rejected: invalid device_id={device_id}")
            return

        await manager.connect(device_id, websocket)
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if necessary
    except WebSocketDisconnect:
        manager.disconnect(device_id)
    except Exception as e:
        logger.exception(f"WebSocket connection error: {e}")
        manager.disconnect(device_id)


async def process_image_generation(image_id: int, device_id: str):
    """
    キャンバス画像を基にAIによる画像生成を行い、生成画像を保存してWebSocket経由で通知する
    """
    db = database.SessionLocal()
    try:
        # プロンプトの取得
        latest_image = db.query(models.Image).filter(
            models.Image.device_id == device_id).order_by(models.Image.request_time.desc()).first()
        if not latest_image or not latest_image.topic:
            logger.error(f"デバイスID {device_id} に対応するプロンプトが見つかりません")
            return

        prompt = latest_image.topic.prompt
        logger.info(f"Prompt for image_id={image_id}: {prompt}")

        # キャンバス画像の取得
        db_image = db.query(models.Image).filter(
            models.Image.id == image_id).first()
        if not db_image:
            logger.error(f"画像ID {image_id} に対応する画像が見つかりません")
            return
        SAVED_IMAGES_DIR = database.saved_images_dir
        GENERATED_IMAGES_DIR = database.generated_images_dir
        canvas_file_path = SAVED_IMAGES_DIR / db_image.canvas_image_filename
        if not canvas_file_path.exists():
            logger.error(f"キャンバス画像ファイル {canvas_file_path} が存在しません")
            return

        # 生成画像のパスを設定
        generated_file_path = GENERATED_IMAGES_DIR / \
            f"generated_{db_image.id}.png"

        # 画像生成の実行
        import app.image_generator
        try:
            app.image_generator.main(
                input_image_path=str(canvas_file_path),
                prompt=prompt,
                output_image_path=str(generated_file_path)
            )
        except Exception as e:
            logger.exception(f"画像生成に失敗しました: {e}")
            return

        # DBに生成画像情報を保存
        crud.update_generated_image(db, image_id, generated_file_path.name)
        logger.info(f"Generated image saved: {generated_file_path}")

        # WebSocketを通じてフロントエンドに通知
        generated_image_url = f"http://localhost:8000/generated-images/{generated_file_path.name}"
        await manager.send_message(device_id, generated_image_url)

    except Exception as e:
        logger.exception(f"画像生成プロセス中にエラーが発生しました: {e}")
    finally:
        db.close()


@app.get("/list-devices")
def list_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    return [{"device_id": device.device_id, "created_at": device.created_at} for device in devices]


@app.get("/images/{device_id}", response_model=schemas.GetImagesResponse)
def get_images(device_id: str, db: Session = Depends(get_db)):
    images = crud.get_images_by_device(db, device_id)
    if not images:
        return schemas.GetImagesResponse(
            success=False, detail="指定されたデバイスIDに関連する画像が見つかりません。"
        )
    image_list = []
    for img in images:
        image_list.append({
            "id": img.id,
            "topic": img.topic.name if img.topic else "",
            "request_time": img.request_time,
            "canvas_image_filename": img.canvas_image_filename,
            "controlnet_image_filename": img.controlnet_image_filename,
            "generated_image_filename": img.generated_image_filename,
        })
    return schemas.GetImagesResponse(
        success=True,
        images=image_list
    )
