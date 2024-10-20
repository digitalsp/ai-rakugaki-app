# backend/app/database.py

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

# 画像保存用ディレクトリの定義
saved_images_dir = Path("saved-images")
generated_images_dir = Path("generated-images")

# ディレクトリが存在しない場合は作成
saved_images_dir.mkdir(parents=True, exist_ok=True)
generated_images_dir.mkdir(parents=True, exist_ok=True)
