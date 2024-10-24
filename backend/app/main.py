# backend/app/main.py

import asyncio
import datetime
import json
import logging
import os
import uuid
from typing import Dict, List, Optional

from fastapi import (BackgroundTasks, Depends, FastAPI, HTTPException, Query,
                     WebSocket, WebSocketDisconnect, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from sqlalchemy.orm import Session

from . import crud, database, image_generater, models, schemas, utils

app = FastAPI()

# 画像保存ディレクトリをマウント
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
    logger.info("画像生成パイプラインを初期化中...")
    global pipe, canny_detector
    try:
        from .image_generater import canny_detector, pipe
        logger.info("画像生成パイプラインが正常に初期化されました。")
    except Exception as e:
        logger.exception(f"画像生成パイプラインの初期化に失敗しました: {e}")
        raise e

# Dependency


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket接続管理クラス


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info(f"WebSocket接続確立: device_id={device_id}")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"WebSocket接続切断: device_id={device_id}")

    async def send_message(self, device_id: str, message: str):
        websocket = self.active_connections.get(device_id)
        if websocket:
            try:
                await websocket.send_text(message)
                logger.info(
                    f"メッセージを送信: device_id={device_id}, message={message}")
            except Exception as e:
                logger.exception(f"メッセージ送信に失敗しました: {e}")


manager = ConnectionManager()

# デバイス登録エンドポイント


@app.post("/register-device", response_model=schemas.DeviceResponse)
def register_device(db: Session = Depends(get_db)):
    """
    デバイスを登録し、一意のデバイスIDと初期データを返すエンドポイント
    """
    try:
        db_device = crud.create_device(db)
        db_topic = crud.get_random_topic(db)
        if not db_topic:
            raise HTTPException(status_code=500, detail="お題の取得に失敗しました。")

        # 画像エントリを作成
        db_image = crud.create_image(db, schemas.ImageCreate(
            device_id=db_device.id,
            topic_id=db_topic.id,
            negative_prompt=db_topic.negative_prompt
        ))

        return schemas.DeviceResponse(
            id=db_device.id,
            created_at=db_device.created_at,
            images=[schemas.ImageResponse.from_orm(db_image)]
        )
    except Exception as e:
        logger.exception(f"デバイス登録中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="デバイスの登録中にエラーが発生しました。")

# デバイス検証エンドポイント


@app.post("/verify-device", response_model=schemas.DeviceVerifyResponse)
def verify_device(request: schemas.DeviceVerifyRequest, db: Session = Depends(get_db)):
    """
    クライアントから送信されたデバイスIDが存在するかを確認し、存在する場合はデバイス情報と最新の画像エントリを返すエンドポイント
    """
    db_device = crud.get_device(db, request.device_id)
    if not db_device:
        logger.warning(f"デバイスIDが存在しません: device_id={request.device_id}")
        raise HTTPException(status_code=404, detail="デバイスIDが存在しません。")

    # 最新の画像エントリを取得
    latest_image = crud.get_latest_image(db, request.device_id)
    if not latest_image:
        raise HTTPException(
            status_code=404, detail="指定されたデバイスIDに関連する画像が見つかりません。")

    # デバイス情報と最新画像をレスポンスに含める
    device_response = schemas.DeviceVerifyResponse.from_orm(db_device)
    device_response.images = [schemas.ImageResponse.from_orm(latest_image)]

    return device_response

# 新しいトピック取得エンドポイント


@app.post("/get-new-topic", response_model=schemas.GetNewTopicResponse)
def get_new_topic(request: schemas.GetNewTopicRequest, db: Session = Depends(get_db)):
    """
    指定されたデバイスIDに対して新しいトピックをランダムに選択し、関連する画像エントリを作成します。
    """
    db_device = crud.get_device(db, request.device_id)
    if not db_device:
        logger.warning(f"デバイスIDが存在しません: device_id={request.device_id}")
        raise HTTPException(status_code=404, detail="デバイスIDが存在しません。")

    db_topic = crud.get_random_topic(db)
    if not db_topic:
        raise HTTPException(status_code=500, detail="お題の取得に失敗しました。")

    db_image = crud.create_image(db, schemas.ImageCreate(
        device_id=request.device_id,
        topic_id=db_topic.id,
        negative_prompt=db_topic.negative_prompt
    ))

    logger.info(
        f"新しいお題を割り当てました: device_id={request.device_id}, topic_id={db_topic.id}")

    return schemas.GetNewTopicResponse(
        success=True,
        topic=db_topic.name,
        image_id=db_image.id
    )

# キャンバス画像保存エンドポイント


@app.post("/save-canvas", response_model=schemas.SaveCanvasResponse)
def save_canvas(
    request: schemas.SaveCanvasRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    キャンバス画像を保存し、画像生成を非同期で開始するエンドポイント
    """
    db_image = crud.get_image_by_id(db, request.image_id)
    if not db_image or db_image.device_id != request.device_id:
        logger.warning(
            f"画像エントリが見つかりません: image_id={request.image_id}, device_id={request.device_id}")
        raise HTTPException(status_code=404, detail="画像エントリが見つかりません。")

    # 画像データをデコードして保存
    image_filename = f"{db_image.id}.png"
    image_path = os.path.join(database.saved_images_dir, image_filename)
    try:
        # `utils.save_image`がPIL Imageオブジェクトを返すと仮定
        image = utils.save_image(request.image_data, database.saved_images_dir)
        image.save(image_path)
        db_image.canvas_image_filename = image_filename
        db.commit()
        logger.info(f"キャンバス画像を保存しました: {image_filename}")
    except Exception as e:
        logger.exception(f"キャンバス画像の保存に失敗しました: {e}")
        raise HTTPException(status_code=500, detail="キャンバス画像の保存に失敗しました。")

    # 画像生成をバックグラウンドタスクとして開始
    background_tasks.add_task(process_image_generation,
                              db_image.id, db_image.device_id)

    # 生成画像URLはバックグラウンドタスクで生成されるため、現時点ではNone
    generated_image_url = None

    logger.info(
        f"キャンバス画像を保存しました: {image_filename}, 生成画像URL: {generated_image_url}")

    return schemas.SaveCanvasResponse(
        success=True,
        file_name=image_filename,
        generated_image_url=generated_image_url
    )

# デバイス一覧取得エンドポイント


@app.get("/list-devices", response_model=List[schemas.DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    """
    登録されている全デバイスの一覧を取得するエンドポイント
    """
    devices = db.query(models.Device).all()
    return [schemas.DeviceResponse.from_orm(device) for device in devices]

# デバイスごとの画像一覧取得エンドポイント


@app.get("/images/{device_id}", response_model=schemas.GetImagesResponse)
def get_images(device_id: str, db: Session = Depends(get_db)):
    """
    指定されたデバイスIDに関連する全ての画像を取得するエンドポイント
    """
    db_device = crud.get_device(db, device_id)
    if not db_device:
        logger.warning(f"デバイスIDが存在しません: device_id={device_id}")
        raise HTTPException(status_code=404, detail="デバイスIDが存在しません。")

    images = crud.get_images_by_device(db, device_id)
    if not images:
        return schemas.GetImagesResponse(
            success=False, detail="指定されたデバイスIDに関連する画像が見つかりません。"
        )

    image_responses = [schemas.ImageResponse.from_orm(img) for img in images]
    return schemas.GetImagesResponse(success=True, images=image_responses)

# WebSocketエンドポイント


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str, db: Session = Depends(get_db)):
    """
    指定されたデバイスIDに対応するWebSocket接続を管理するエンドポイント
    """
    try:
        # デバイスIDの検証
        db_device = crud.get_device(db, device_id)
        if not db_device:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid device_id")
            logger.warning(f"WebSocket接続拒否: 無効なdevice_id={device_id}")
            return

        await manager.connect(device_id, websocket)
        while True:
            data = await websocket.receive_text()
            # 必要に応じてメッセージの処理を実装
    except WebSocketDisconnect:
        manager.disconnect(device_id)
    except Exception as e:
        logger.exception(f"WebSocket接続エラー: {e}")
        manager.disconnect(device_id)

# バックグラウンドタスクとして画像生成を処理


async def process_image_generation(image_id: str, device_id: str):
    """
    キャンバス画像を基にAIによる画像生成を行い、生成画像を保存してWebSocket経由で通知する
    """
    db = database.SessionLocal()
    try:
        db_image = crud.get_image_by_id(db, image_id)
        if not db_image:
            logger.error(f"画像ID {image_id} に対応する画像が見つかりません。")
            return
        if not db_image.topic:
            logger.error(f"画像ID {image_id} に対応するトピックが見つかりません。")
            return

        prompt = db_image.topic.prompt
        negative_prompt = db_image.negative_prompt or ""
        logger.info(f"画像生成開始: image_id={image_id}, prompt={prompt}")

        SAVED_IMAGES_DIR = database.saved_images_dir
        GENERATED_IMAGES_DIR = database.generated_images_dir
        canvas_file_path = os.path.join(
            SAVED_IMAGES_DIR, db_image.canvas_image_filename)
        if not os.path.exists(canvas_file_path):
            logger.error(f"キャンバス画像ファイルが存在しません: {canvas_file_path}")
            return

        # キャンバス画像を開く
        try:
            image = Image.open(canvas_file_path).convert("RGB")
        except Exception as e:
            logger.exception(f"キャンバス画像の読み込みに失敗しました: {e}")
            return

        # 画像生成を実行
        try:
            global pipe, canny_detector
            gen_image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=image,
                num_inference_steps=100,
                guidance_scale=6.5,
                adapter_conditioning_scale=0.7
            ).images[0]
        except Exception as e:
            logger.exception(f"画像生成に失敗しました: {e}")
            return

        # 生成画像を保存
        generated_file_path = utils.save_generated_image(
            gen_image, GENERATED_IMAGES_DIR)
        if not generated_file_path:
            logger.error("生成画像の保存に失敗しました。")
            return
        logger.info(f"生成画像を保存しました: {generated_file_path}")

        # データベースを更新
        crud.update_generated_image(db, image_id, generated_file_path.name)
        logger.info(f"データベースを更新しました: {generated_file_path.name}")

        # WebSocketを通じてフロントエンドに通知
        generated_image_url = f"http://localhost:8000/generated-images/{generated_file_path.name}"
        canvas_image_url = f"http://localhost:8000/saved-images/{db_image.canvas_image_filename}"
        topic = db_image.topic.name if db_image.topic else ""

        notification = {
            "canvasImageUrl": canvas_image_url,
            "generatedImageUrl": generated_image_url,
            "topic": topic,
        }
        await manager.send_message(device_id, json.dumps(notification))
        logger.info(f"WebSocket経由で通知を送信しました: device_id={device_id}")
    except Exception as e:
        logger.exception(f"画像生成プロセス中にエラーが発生しました: {e}")
    finally:
        db.close()
