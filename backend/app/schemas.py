# backend/app/schemas.py

from typing import Optional

from pydantic import BaseModel


class GetNewTopicRequest(BaseModel):
    device_id: str


class GetNewTopicResponse(BaseModel):
    success: bool
    topic: str
    image_id: str

    class Config:
        orm_mode = True


class GetTopicResponse(BaseModel):
    success: bool
    topic: str

    class Config:
        orm_mode = True


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
        orm_mode = True


class GetLatestImageResponse(BaseModel):
    success: bool
    generatedImageUrl: Optional[str] = None

    class Config:
        orm_mode = True
