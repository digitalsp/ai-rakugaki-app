# backend/app/models.py

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Device(Base):
    __tablename__ = 'devices'
    device_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    images = relationship("Image", back_populates="device")


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    prompt = Column(String)

    images = relationship("Image", back_populates="topic")


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey('devices.device_id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))
    request_time = Column(DateTime, default=datetime.datetime.utcnow)
    canvas_image_filename = Column(String)
    controlnet_image_filename = Column(String, nullable=True)
    generated_image_filename = Column(String, nullable=True)

    device = relationship("Device", back_populates="images")
    topic = relationship("Topic", back_populates="images")
