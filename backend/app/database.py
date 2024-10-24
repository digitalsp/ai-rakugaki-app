# backend/app/database.py

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベースURLの設定（SQLiteを使用）
DATABASE_URL = "sqlite:///./app.db"

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特有の設定
    pool_pre_ping=True  # 接続の健全性を確認
)

# セッションローカルの作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ベースクラスの定義
Base = declarative_base()

# 画像保存用ディレクトリの定義
saved_images_dir = Path("saved-images")
generated_images_dir = Path("generated-images")

# ディレクトリが存在しない場合は作成
saved_images_dir.mkdir(parents=True, exist_ok=True)
generated_images_dir.mkdir(parents=True, exist_ok=True)
