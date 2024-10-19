# backend/app/main.py
import asyncio
import os
from pathlib import Path
from typing import Dict

from fastapi import (Depends, FastAPI, HTTPException, WebSocket,
                     WebSocketDisconnect)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 必要なインポートを追加
from PIL import Image
from sqlalchemy.orm import Session

from . import crud, database, models, schemas, utils

app = FastAPI()

# CORS設定
origins = [
    "http://localhost:3000",  # フロントエンドのURL
    # 必要に応じて他のオリジンを追加
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # フロントエンドのオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベースの初期化
models.Base.metadata.create_all(bind=database.engine)


# 依存関係
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# WebSocketマネージャー
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        """WebSocket接続を確立し、接続をマネージャーに追加する"""
        await websocket.accept()
        self.active_connections[device_id] = websocket

    def disconnect(self, device_id: str):
        """WebSocket接続をマネージャーから削除する"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]

    async def send_message(self, device_id: str, message: str):
        """特定のデバイスにメッセージを送信する"""
        websocket = self.active_connections.get(device_id)
        if websocket:
            await websocket.send_text(message)


manager = ConnectionManager()

# 必要なディレクトリの作成
BASE_DIR = Path(__file__).resolve().parent.parent  # appディレクトリの親ディレクトリ
SAVED_IMAGES_DIR = BASE_DIR / "saved-images"
GENERATED_IMAGES_DIR = BASE_DIR / "generated-images"

for directory in [SAVED_IMAGES_DIR, GENERATED_IMAGES_DIR]:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        print(f"ディレクトリ '{directory}' を作成しました。")

# エンドポイント


@app.post("/register-device", response_model=schemas.DeviceRegisterResponse)
def register_device(
    request: schemas.DeviceRegisterRequest, db: Session = Depends(get_db)
):
    """
    デバイスを登録し、一意のデバイスIDとランダムなお題を返すエンドポイント
    """
    db_device = crud.create_device(db)
    db_topic = crud.get_random_topic(db)
    topic_name = db_topic.name if db_topic else None
    return schemas.DeviceRegisterResponse(
        success=True, device_id=db_device.device_id, topic=topic_name
    )


@app.post("/save-canvas", response_model=schemas.SaveCanvasResponse)
def save_canvas(request: schemas.SaveCanvasRequest, db: Session = Depends(get_db)):
    """
    キャンバス画像を保存し、画像生成プロセスを開始するエンドポイント
    """
    # 画像を保存
    file_path = utils.save_image(request.image_data, directory=SAVED_IMAGES_DIR)
    if not file_path:
        raise HTTPException(status_code=500, detail="画像の保存に失敗しました")

    # お題の取得
    db_topic = crud.get_random_topic(db)
    if not db_topic:
        raise HTTPException(status_code=500, detail="お題の取得に失敗しました")

    # DBに画像情報を保存
    db_image = crud.create_image(db, request.device_id, file_path.name, db_topic.id)

    # 画像生成プロセスを非同期タスクとして実行
    asyncio.create_task(process_image_generation(db_image.id, request.device_id))

    return schemas.SaveCanvasResponse(
        success=True, file_name=db_image.canvas_image_filename
    )


@app.get("/latest-images", response_model=schemas.LatestImagesResponse)
def get_latest_images(device_id: str, db: Session = Depends(get_db)):
    """
    指定されたデバイスの最新のキャンバス画像と生成画像のURLを返すエンドポイント
    """
    db_image = crud.get_latest_images(db, device_id)
    if db_image:
        canvas_image_url = (
            f"http://localhost:8000/saved-images/{db_image.canvas_image_filename}"
            if db_image.canvas_image_filename
            else None
        )
        generated_image_url = (
            f"http://localhost:8000/generated-images/{db_image.generated_image_filename}"
            if db_image.generated_image_filename
            else None
        )
        return schemas.LatestImagesResponse(
            success=True,
            canvas_image_url=canvas_image_url,
            generated_image_url=generated_image_url,
        )
    else:
        return schemas.LatestImagesResponse(
            success=False, canvas_image_url=None, generated_image_url=None
        )


# 静的ファイルの提供
app.mount("/saved-images", StaticFiles(directory=SAVED_IMAGES_DIR), name="saved-images")
app.mount(
    "/generated-images",
    StaticFiles(directory=GENERATED_IMAGES_DIR),
    name="generated-images",
)


# 画像生成処理
async def process_image_generation(image_id: int, device_id: str):
    """
    キャンバス画像を基にAIによる画像生成を行い、生成画像を保存してWebSocket経由で通知する
    """
    db = database.SessionLocal()
    try:
        # プロンプトの取得
        prompt = crud.get_latest_topic_prompt(db, device_id)
        if not prompt:
            print(f"デバイスID {device_id} に対応するプロンプトが見つかりません")
            return

        # キャンバス画像の取得
        db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
        if not db_image:
            print(f"画像ID {image_id} に対応する画像が見つかりません")
            return
        canvas_file_path = SAVED_IMAGES_DIR / db_image.canvas_image_filename
        if not canvas_file_path.exists():
            print(f"キャンバス画像ファイル {canvas_file_path} が存在しません")
            return

        # ControlNet処理の適用（ダミー実装）
        # 実際にはControlNetを適用する処理を実装
        canvas_image = Image.open(canvas_file_path)
        controlnet_image = canvas_image  # ダミー

        # Stable Diffusionによる画像生成（ダミー実装）
        # 実際にはStable Diffusionを使用して画像生成を行う
        generated_image = controlnet_image  # ダミー

        # 生成画像の保存
        generated_file_path = utils.save_generated_image(
            generated_image, directory=GENERATED_IMAGES_DIR
        )
        if not generated_file_path:
            print("生成画像の保存に失敗しました")
            return

        # DBに生成画像情報を保存
        crud.update_generated_image(db, image_id, generated_file_path.name)

        # WebSocketを通じてフロントエンドに通知
        generated_image_url = (
            f"http://localhost:8000/generated-images/{generated_file_path.name}"
        )
        await manager.send_message(device_id, generated_image_url)

    except Exception as e:
        print(f"画像生成プロセス中にエラーが発生しました: {e}")
    finally:
        db.close()


# WebSocketエンドポイント
@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    """
    指定されたデバイスIDでWebSocket接続を確立するエンドポイント
    """
    await manager.connect(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # クライアントからのメッセージを必要に応じて処理
            # 今回は通知のみ
    except WebSocketDisconnect:
        manager.disconnect(device_id)
