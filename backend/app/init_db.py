# backend/app/init_db.py
from sqlalchemy.orm import Session

from . import crud, database, models


def init_db():
    db = database.SessionLocal()
    try:
        # テーブルの作成
        models.Base.metadata.create_all(bind=database.engine)

        # お題が既に存在するか確認
        topics = db.query(models.Topic).all()
        if not topics:
            initial_topics = [
                {"name": "ロボット", "prompt": "masterpiece, cute, robot"},
                {
                    "name": "うちゅうせん",
                    "prompt": "masterpiece, spaceship, space, galaxy, stars, ",
                },
                {"name": "ねこ", "prompt": "masterpiece, cat, cute"},
                # 必要に応じて追加
            ]
            for topic in initial_topics:
                db_topic = models.Topic(name=topic["name"], prompt=topic["prompt"])
                db.add(db_topic)
            db.commit()
            print("初期お題データを追加しました。")
        else:
            print("お題データは既に存在します。")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
