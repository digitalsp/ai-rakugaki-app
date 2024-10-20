# backend/app/schemas.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DeviceRegisterRequest(BaseModel):
    pass


class DeviceRegisterResponse(BaseModel):
    success: bool
    device_id: Optional[str] = None
    topic: Optional[str] = None
    detail: Optional[str] = None


class DeviceVerifyRequest(BaseModel):
    device_id: str


class DeviceVerifyResponse(BaseModel):
    success: bool
    device_id: Optional[str] = None
    topic: Optional[str] = None
    detail: Optional[str] = None


class SaveCanvasRequest(BaseModel):
    device_id: str
    image_data: str  # Base64-encoded image data


class SaveCanvasResponse(BaseModel):
    success: bool
    file_name: Optional[str] = None
    detail: Optional[str] = None


class ImageEntry(BaseModel):
    id: int
    topic: str
    request_time: datetime
    canvas_image_filename: str
    controlnet_image_filename: Optional[str]
    generated_image_filename: Optional[str]


class GetImagesResponse(BaseModel):
    success: bool
    images: Optional[List[ImageEntry]] = None
    detail: Optional[str] = None

# 新規追加


class GetNewTopicRequest(BaseModel):
    device_id: str


class GetNewTopicResponse(BaseModel):
    success: bool
    topic: Optional[str] = None
    detail: Optional[str] = None
