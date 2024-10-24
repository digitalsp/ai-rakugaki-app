# backend/app/schemas.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TopicBase(BaseModel):
    name: str
    prompt: str
    negative_prompt: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2用に変更


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceBase(BaseModel):
    id: str

    class Config:
        from_attributes = True


class DeviceCreate(DeviceBase):
    pass


class ImageBase(BaseModel):
    id: str
    device_id: str
    topic_id: str
    canvas_image_filename: Optional[str] = None
    generated_image_filename: Optional[str] = None
    request_time: datetime
    negative_prompt: Optional[str] = None

    class Config:
        from_attributes = True


class ImageCreate(BaseModel):
    device_id: str
    topic_id: str
    negative_prompt: Optional[str] = None


class ImageResponse(ImageBase):
    topic: TopicResponse

    class Config:
        from_attributes = True


class DeviceResponse(DeviceBase):
    created_at: datetime
    images: List[ImageResponse] = []

    class Config:
        from_attributes = True


class GetNewTopicRequest(BaseModel):
    device_id: str


class GetNewTopicResponse(BaseModel):
    success: bool
    topic: str
    image_id: str

    class Config:
        from_attributes = True


class DeviceVerifyRequest(BaseModel):
    device_id: str


class DeviceVerifyResponse(DeviceResponse):
    pass


class SaveCanvasRequest(BaseModel):
    device_id: str
    image_id: str
    image_data: str
    negative_prompt: Optional[str] = ""


class SaveCanvasResponse(BaseModel):
    success: bool
    file_name: str
    generated_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class GetLatestImageResponse(BaseModel):
    success: bool
    generatedImageUrl: Optional[str] = None

    class Config:
        from_attributes = True


class GetImagesResponse(BaseModel):
    success: bool
    images: Optional[List[ImageResponse]] = None
    detail: Optional[str] = None

    class Config:
        from_attributes = True
