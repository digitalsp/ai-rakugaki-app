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
        # "data:image/png;base64,..." を除去
        base64_data = image_data.split(",")[1]
    except IndexError as e:
        print("image_data の形式が不正です。カンマが含まれていません。", e)
        return None

    try:
        image_bytes = base64.b64decode(base64_data)
    except base64.binascii.Error as e:
        print("Base64デコードに失敗しました。", e)
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        print("PILが画像を開く際にエラーが発生しました。", e)
        return None

    # ユニークなファイル名を生成
    file_name = f"{uuid.uuid4()}.png"

    # 保存ディレクトリを作成（既に作成済みの場合はスキップ）
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print("ディレクトリの作成中にエラーが発生しました。", e)
        return None

    file_path = directory / file_name

    try:
        image.save(file_path)
        print(f"画像を保存しました: {file_path}")
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
