# backend/app/models.py
import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    images = relationship("Image", back_populates="device")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    prompt = Column(String)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))  # 追加
    canvas_image_filename = Column(String)
    generated_image_filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    device = relationship("Device", back_populates="images")
    topic = relationship("Topic")  # 追加
