# backend/app/crud.py

import datetime
import random
import uuid
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import models, schemas


def create_device(db: Session) -> models.Device:
    """新しいデバイスを作成し、デバイスIDを生成する"""
    unique_id = str(uuid.uuid4())
    db_device = models.Device(id=unique_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device(db: Session, device_id: str) -> Optional[models.Device]:
    """指定されたdevice_idのデバイスを取得する"""
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def create_topic(db: Session, topic: schemas.TopicCreate) -> models.Topic:
    """新しいトピックを作成する"""
    topic_id = str(uuid.uuid4())
    db_topic = models.Topic(
        id=topic_id,
        name=topic.name,
        prompt=topic.prompt,
        negative_prompt=topic.negative_prompt
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


def get_random_topic(db: Session) -> Optional[models.Topic]:
    """ランダムなお題を取得する"""
    topics = db.query(models.Topic).all()
    if not topics:
        return None
    return random.choice(topics)


def create_image(db: Session, image: schemas.ImageCreate) -> models.Image:
    """新しい画像エントリを作成する"""
    image_id = str(uuid.uuid4())
    db_image = models.Image(
        id=image_id,
        device_id=image.device_id,
        topic_id=image.topic_id,
        negative_prompt=image.negative_prompt
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_generated_image(
    db: Session, image_id: str, generated_image_filename: str
) -> Optional[models.Image]:
    """生成後の画像ファイル名を更新する"""
    db_image = db.query(models.Image).filter(
        models.Image.id == image_id).first()
    if db_image:
        db_image.generated_image_filename = generated_image_filename
        db.commit()
        db.refresh(db_image)
    return db_image


def get_image_by_id(db: Session, image_id: str) -> Optional[models.Image]:
    """指定された画像IDの画像を取得する"""
    return db.query(models.Image).filter(models.Image.id == image_id).first()


def get_latest_image(db: Session, device_id: str) -> Optional[models.Image]:
    """指定されたデバイスIDの最新の画像を取得する"""
    return db.query(models.Image).filter(models.Image.device_id == device_id).order_by(desc(models.Image.request_time)).first()


def get_images_by_device(db: Session, device_id: str) -> List[models.Image]:
    """指定されたデバイスIDに関連する全ての画像を取得する"""
    return db.query(models.Image).filter(models.Image.device_id == device_id).order_by(desc(models.Image.request_time)).all()
