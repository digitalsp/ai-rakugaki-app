# backend/app/crud.py

import random
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models


def create_device(db: Session) -> models.Device:
    """新しいデバイスを作成し、デバイスIDを生成する"""
    unique_id = str(uuid.uuid4())
    db_device = models.Device(device_id=unique_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device(db: Session, device_id: str) -> Optional[models.Device]:
    """指定されたdevice_idのデバイスを取得する"""
    return db.query(models.Device).filter(models.Device.device_id == device_id).first()


def get_random_topic(db: Session) -> Optional[models.Topic]:
    """ランダムなお題を取得する"""
    topics = db.query(models.Topic).all()
    if not topics:
        return None
    return random.choice(topics)


def create_image(
    db: Session, device_id: str, topic_id: int, canvas_image_filename: str
) -> models.Image:
    """キャンバス画像を保存し、Imageエントリを作成する"""
    db_image = models.Image(
        device_id=device_id,
        topic_id=topic_id,
        canvas_image_filename=canvas_image_filename,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_generated_image(
    db: Session, image_id: int, generated_image_filename: str
) -> models.Image:
    """生成後の画像ファイル名を更新する"""
    db_image = db.query(models.Image).filter(
        models.Image.id == image_id).first()
    if db_image:
        db_image.generated_image_filename = generated_image_filename
        db.commit()
        db.refresh(db_image)
    return db_image


def get_images_by_device(db: Session, device_id: str) -> List[models.Image]:
    """指定されたデバイスIDに関連する画像を取得する"""
    return db.query(models.Image).filter(models.Image.device_id == device_id).all()
