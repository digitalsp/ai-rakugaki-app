# backend/app/init_db.py

from sqlalchemy.orm import Session

from . import models
from .database import engine


def init_db():
    models.Base.metadata.create_all(bind=engine)
    # 初期お題データの追加（必要に応じて）
    with Session(engine) as db:
        if not db.query(models.Topic).first():
            initial_topics = [
                models.Topic(
                    name="ロボット",
                    prompt="masterpiece, cool, robot, futureristic",
                    negative_prompt="low quality, bad anatomy, missing limbs, bad quality, low quality, lowres, displeasing, very displeasing, bad anatomy, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed, lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, chromatic aberration, signature, extra digits, artistic error, username, scan, abstract"
                ),
                models.Topic(
                    name="うちゅうせん",
                    prompt="masterpiece, spaceship, space, galaxy, stars",
                    negative_prompt="low quality, blurry, bad lighting, bad quality, low quality, lowres, displeasing, very displeasing, bad anatomy, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed, lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, chromatic aberration, signature, extra digits, artistic error, username, scan, abstract"
                ),
                models.Topic(
                    name="ねこ",
                    prompt="masterpiece, cat, cute, ",
                    negative_prompt="low quality, bad fur, bad quality, low quality, lowres, displeasing, very displeasing, bad anatomy, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed, lowres, (bad), text, error, fewer, extra, missing, worst quality, jpeg artifacts, low quality, watermark, unfinished, displeasing, oldest, early, chromatic aberration, signature, extra digits, artistic error, username, scan, abstract"
                ),
            ]
            db.add_all(initial_topics)
            db.commit()
            print("初期お題データを追加しました。")


if __name__ == "__main__":
    init_db()
