# backend/app/utils.py

import base64
import io
import os
import uuid
from pathlib import Path
from typing import Optional  # Optional をインポート

from PIL import Image


def save_image(image_data: str, directory: Path) -> Optional[Path]:
    """Base64エンコードされた画像データをデコードして保存し、ファイルパスを返す"""
    try:
        base64_data = image_data.split(",")[1]  # "data:image/png;base64,..." を除去
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print("画像データのデコード中にエラーが発生しました:", e)
        return None

    # ユニークなファイル名を生成
    file_name = f"{uuid.uuid4()}.png"

    # 保存ディレクトリを作成（既に作成済みの場合はスキップ）
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / file_name

    try:
        image.save(file_path)
        return file_path
    except Exception as e:
        print("画像の保存中にエラーが発生しました:", e)
        return None


def save_generated_image(
    generated_image: Image.Image, directory: Path
) -> Optional[Path]:
    """生成された画像を保存し、ファイルパスを返す"""
    try:
        buffered = io.BytesIO()
        generated_image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print("生成画像の処理中にエラーが発生しました:", e)
        return None

    # ユニークなファイル名を生成
    file_name = f"{uuid.uuid4()}.png"

    # 保存ディレクトリを作成（既に作成済みの場合はスキップ）
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / file_name

    try:
        image.save(file_path)
        return file_path
    except Exception as e:
        print("生成画像の保存中にエラーが発生しました:", e)
        return None
