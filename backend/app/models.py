# backend/app/models.py

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)
    images = relationship("Image", back_populates="device")

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True)  # 一意の画像ID
    device_id = Column(String, ForeignKey("devices.id"))
    canvas_image_filename = Column(String, nullable=True)
    generated_image_filename = Column(String, nullable=True)
    request_time = Column(DateTime, default=datetime.datetime.utcnow)
    topic = Column(String, nullable=False)

    device = relationship("Device", back_populates="images")

    __table_args__ = (
        UniqueConstraint('device_id', 'id', name='unique_device_image'),
    )
