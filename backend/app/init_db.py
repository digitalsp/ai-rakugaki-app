# backend/app/init_db.py

import uuid

from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine


def init_db():
    """データベースを初期化し、初期データを追加する"""
    models.Base.metadata.create_all(bind=engine)

    # 初期お題データの追加（必要に応じて）
    with Session(bind=engine) as db:
        existing_topics = db.query(models.Topic).count()
        if existing_topics == 0:
            initial_topics = [
                schemas.TopicCreate(
                    name="ロボット",
                    prompt="masterpiece, cool, robot, futuristic",
                    negative_prompt="low quality, bad anatomy, missing limbs, bad quality, lowres, displeasing, very displeasing, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, glitch, deformed, text, error, missing, watermark, unfinished, signature, username, abstract"
                ),
                schemas.TopicCreate(
                    name="うちゅうせん",
                    prompt="masterpiece, spaceship, space, galaxy, stars",
                    negative_prompt="low quality, blurry, bad lighting, lowres, displeasing, very displeasing, bad anatomy, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, glitch, deformed, text, error, watermark, unfinished, signature, username, abstract"
                ),
                schemas.TopicCreate(
                    name="ねこ",
                    prompt="masterpiece, cat, cute",
                    negative_prompt="low quality, bad fur, lowres, displeasing, very displeasing, bad anatomy, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, glitch, deformed, text, error, watermark, unfinished, signature, username, abstract"
                ),
                # 必要に応じて他のお題を追加
            ]
            for topic in initial_topics:
                crud.create_topic(db, topic)
            print("初期お題データを追加しました。")
        else:
            print("既にお題データが存在します。初期化をスキップします。")


if __name__ == "__main__":
    init_db()
