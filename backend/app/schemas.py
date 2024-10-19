# backend/app/schemas.py
from typing import Optional

from pydantic import BaseModel


# デバイス登録リクエスト
class DeviceRegisterRequest(BaseModel):
    pass  # 特にデータは不要、デバイスを登録するのみ


# デバイス登録レスポンス
class DeviceRegisterResponse(BaseModel):
    success: bool
    device_id: str
    topic: Optional[str] = None


# 新しいお題取得リクエスト
class GetNewTopicRequest(BaseModel):
    device_id: str


# 新しいお題取得レスポンス
class GetNewTopicResponse(BaseModel):
    success: bool
    topic: Optional[str] = None


# キャンバス画像保存リクエスト
class SaveCanvasRequest(BaseModel):
    device_id: str
    image_data: str  # Base64エンコードされた画像データ


# キャンバス画像保存レスポンス
class SaveCanvasResponse(BaseModel):
    success: bool
    file_name: str


# 最新画像取得レスポンス
class LatestImagesResponse(BaseModel):
    success: bool
    canvas_image_url: Optional[str] = None
    generated_image_url: Optional[str] = None
