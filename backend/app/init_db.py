# backend/app/init_db.py
from sqlalchemy.orm import Session

from . import crud, database, models

# def init_db():
#     db = database.SessionLocal()
#     try:
#         # テーブルの作成
#         models.Base.metadata.create_all(bind=database.engine)

#         # お題が既に存在するか確認
#         topics = db.query(models.Topic).all()
#         if not topics:
#             initial_topics = [
#                 {"name": "ロボット", "prompt": "masterpiece, cute, robot"},
#                 {
#                     "name": "うちゅうせん",
#                     "prompt": "masterpiece, spaceship, space, galaxy, stars, ",
#                 },
#                 {"name": "ねこ", "prompt": "masterpiece, cat, cute"},
#                 # 必要に応じて追加
#             ]
#             for topic in initial_topics:
#                 db_topic = models.Topic(name=topic["name"], prompt=topic["prompt"])
#                 db.add(db_topic)
#             db.commit()
#             print("初期お題データを追加しました。")
#         else:
#             print("お題データは既に存在します。")
#     finally:
#         db.close()
# backend/app/init_db.py


def init_db():
    models.Base.metadata.create_all(bind=database.engine)
    # 初期お題データの追加（必要に応じて）
    with Session(database.engine) as db:
        if not db.query(models.Topic).first():
            initial_topics = [
                models.Topic(
                    name="お題1", prompt="masterpiece, cool, cute, robot"),
                models.Topic(
                    name="うちゅうせん", prompt="masterpiece, spaceship, space, galaxy, stars"),
                models.Topic(name="ねこ", prompt="masterpiece, cat, cute"),
            ]
            db.add_all(initial_topics)
            db.commit()
            print("初期お題データを追加しました。")


if __name__ == "__main__":
    init_db()
