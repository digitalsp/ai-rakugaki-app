# backend/app/main.py

import asyncio
import json  # 追加: jsonをインポート
import logging
import uuid
from typing import Dict

from fastapi import (BackgroundTasks, Depends, FastAPI, HTTPException, Query,
                     WebSocket, WebSocketDisconnect)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image  # 追加: PIL.Imageをインポート
from sqlalchemy.orm import Session

from . import crud, database, image_generater, models, schemas, utils

app = FastAPI()

# 既存のコードの後に追加
app.mount(
    "/saved-images",
    StaticFiles(directory=database.saved_images_dir),
    name="saved-images",
)
app.mount(
    "/generated-images",
    StaticFiles(directory=database.generated_images_dir),
    name="generated-images",
)

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
    allow_origins=origins,  # 必要なオリジンのみ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベースの初期化


@app.on_event("startup")
def on_startup():
    import app.init_db

    app.init_db.init_db()
    # パイプラインの初期化
    logger.info("Initializing image generation pipeline...")
    global pipe, canny_detector
    try:
        # image_generater.pyからグローバルパイプラインとCannyDetectorを取得
        from .image_generater import canny_detector, pipe
        logger.info("Image generation pipeline initialized successfully.")
    except Exception as e:
        logger.exception(
            f"Failed to initialize image generation pipeline: {e}")
        raise e

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
def verify_device(request: schemas.DeviceVerifyRequest, db: Session = Depends(get_db)):
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
    latest_image = (
        db.query(models.Image)
        .filter(models.Image.device_id == device_id)
        .order_by(models.Image.request_time.desc())
        .first()
    )
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
def get_new_topic(device_id: str, db: Session = Depends(get_db)):
    """
    新しいお題を取得し、デバイスに関連付けるエンドポイント
    """
    # お題のリスト（例）
    topics = ["ねこ", "いぬ", "うさぎ", "りんご", "さくら"]

    # ランダムなお題を選択
    new_topic = random.choice(topics)

    # 画像エントリを作成
    image_id = str(uuid.uuid4())
    image = models.Image(
        id=image_id,
        device_id=device_id,
        canvas_image_filename="",  # まだ描かれていない
        generated_image_filename="",  # まだ生成されていない
        request_time=datetime.datetime.utcnow(),
        topic=new_topic
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    return schemas.GetNewTopicResponse(
        success=True,
        topic=new_topic,
        image_id=image_id
    )


@app.post("/save-canvas", response_model=schemas.SaveCanvasResponse)
def save_canvas(
    device_id: str,
    image_id: str,
    image_data: str,
    negative_prompt: Optional[str] = "",
    db: Session = Depends(get_db)
):
    """
    キャンバス画像を保存し、生成画像を生成するエンドポイント
    """
    db_image = crud.get_image_by_id(db, image_id)
    if not db_image or db_image.device_id != device_id:
        raise HTTPException(status_code=404, detail="画像エントリが見つかりません。")

    # 画像データをデコードして保存
    image_filename = f"{image_id}.png"
    image_path = os.path.join(database.saved_images_dir, image_filename)
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data.split(",")[1]))
    db_image.canvas_image_filename = image_filename

    db.commit()

    # 画像生成のロジックをここに追加
    # 例: AIモデルを呼び出して生成画像を保存
    generated_image_filename = generate_image(
        image_path, db_image.topic, negative_prompt)
    if not generated_image_filename:
        raise HTTPException(status_code=500, detail="画像生成に失敗しました。")

    db_image.generated_image_filename = generated_image_filename
    db.commit()

    # 生成画像のURLを作成
    generated_image_url = f"http://localhost:8000/generated-images/{generated_image_filename}"

    # レスポンスを返す
    return schemas.SaveCanvasResponse(
        success=True,
        file_name=image_filename,
        generated_image_url=generated_image_url
    )


@app.get("/get-latest-image", response_model=schemas.GetLatestImageResponse)
def get_latest_image(device_id: str = Query(...), db: Session = Depends(get_db)):
    """
    指定されたデバイスIDの最新の画像の生成画像URLを取得するエンドポイント
    """
    db_image = crud.get_latest_image(db, device_id)
    if not db_image or not db_image.generated_image_filename:
        raise HTTPException(status_code=404, detail="生成画像が見つかりません。")
    generated_image_url = f"http://localhost:8000/generated-images/{db_image.generated_image_filename}"
    return schemas.GetLatestImageResponse(success=True, generatedImageUrl=generated_image_url)


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket, device_id: str, db: Session = Depends(get_db)
):
    try:
        # Verify device_id before accepting WebSocket connection
        db_device = crud.get_device(db, device_id)
        if not db_device:
            await websocket.close(code=1008, reason="Invalid device_id")
            logger.warning(
                f"WebSocket connection rejected: invalid device_id={device_id}"
            )
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
        # キャンバス画像の取得
        db_image = db.query(models.Image).filter(
            models.Image.id == image_id).first()
        if not db_image:
            logger.error(f"画像ID {image_id} に対応する画像が見つかりません")
            return
        if not db_image.topic:
            logger.error(f"画像ID {image_id} に対応するトピックが見つかりません")
            return

        prompt = db_image.topic.prompt
        negative_prompt = db_image.negative_prompt or ""
        logger.info(f"Prompt for image_id={image_id}: {prompt}")
        logger.info(
            f"Negative Prompt for image_id={image_id}: {negative_prompt}")

        SAVED_IMAGES_DIR = database.saved_images_dir
        GENERATED_IMAGES_DIR = database.generated_images_dir
        canvas_file_path = SAVED_IMAGES_DIR / db_image.canvas_image_filename
        if not canvas_file_path.exists():
            logger.error(f"キャンバス画像ファイル {canvas_file_path} が存在しません")
            return

        # 画像を開いてPIL Imageオブジェクトに変換
        try:
            image = Image.open(canvas_file_path).convert("RGB")
        except Exception as e:
            logger.exception(f"キャンバス画像の読み込みに失敗しました: {e}")
            return

        # 画像生成の実行
        logger.info(f"image_id={image_id}の画像生成を開始")
        try:
            # グローバルなパイプラインを使用
            global pipe, canny_detector

            # 画像生成
            gen_image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image,  # PathではなくImageオブジェクトを渡す
                num_inference_steps=25,  # 推論ステップ数
                guidance_scale=5.5,
                adapter_conditioning_scale=0.8
            ).images[0]
        except Exception as e:
            logger.exception(f"画像生成に失敗しました: {e}")
            return

        # 生成された画像を保存
        generated_file_path = utils.save_generated_image(
            gen_image, GENERATED_IMAGES_DIR)  # 修正: app.utils -> utils
        if not generated_file_path:
            logger.error("生成画像の保存に失敗しました。")
            return
        logger.info(f"生成画像が保存されました: {generated_file_path}")

        # DBに生成画像情報を保存
        crud.update_generated_image(db, image_id, generated_file_path.name)
        logger.info(
            f"DB updated with generated image: {generated_file_path.name}")

        # WebSocketを通じてフロントエンドに通知
        generated_image_url = (
            f"http://localhost:8000/generated-images/{generated_file_path.name}"
        )
        canvas_image_url = (
            f"http://localhost:8000/saved-images/{db_image.canvas_image_filename}"
        )
        topic = db_image.topic.name if db_image.topic else ""

        # WebSocketメッセージに必要な情報を含める
        notification = {
            "canvasImageUrl": canvas_image_url,
            "generatedImageUrl": generated_image_url,
            "topic": topic,
        }
        await manager.send_message(device_id, json.dumps(notification))
        logger.info(f"通知をdevice_id={device_id}に送信しました")

    except Exception as e:
        logger.exception(f"画像生成プロセス中にエラーが発生しました: {e}")
    finally:
        db.close()


@app.get("/list-devices")
def list_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    return [
        {"device_id": device.device_id, "created_at": device.created_at}
        for device in devices
    ]


@app.get("/images/{device_id}", response_model=schemas.GetImagesResponse)
def get_images(device_id: str, db: Session = Depends(get_db)):
    images = crud.get_images_by_device(db, device_id)
    if not images:
        return schemas.GetImagesResponse(
            success=False, detail="指定されたデバイスIDに関連する画像が見つかりません。"
        )
    image_list = []
    for img in images:
        image_list.append(
            {
                "id": img.id,
                "topic": img.topic.name if img.topic else "",
                "request_time": img.request_time,
                "canvas_image_filename": img.canvas_image_filename,
                "controlnet_image_filename": img.controlnet_image_filename,
                "generated_image_filename": img.generated_image_filename,
                "negative_prompt": img.negative_prompt,  # 追加
            }
        )
    return schemas.GetImagesResponse(success=True, images=image_list)
