# backend/app/models.py

import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    images = relationship("Image", back_populates="device",
                          cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, index=True, unique=True)
    name = Column(String(100), unique=True, nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    images = relationship("Image", back_populates="topic")


class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, index=True, unique=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    topic_id = Column(String, ForeignKey("topics.id"), nullable=False)
    canvas_image_filename = Column(String, nullable=True)
    generated_image_filename = Column(String, nullable=True)
    request_time = Column(DateTime, default=datetime.datetime.utcnow)
    negative_prompt = Column(Text, nullable=True)

    device = relationship("Device", back_populates="images")
    topic = relationship("Topic", back_populates="images")

    __table_args__ = (
        UniqueConstraint('device_id', 'id', name='unique_device_image'),
    )
