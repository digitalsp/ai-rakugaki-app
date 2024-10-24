# backend/app/utils.py

import base64
import io
import logging
import os
import uuid
from pathlib import Path
from typing import Optional  # Optional をインポート

from PIL import Image

logger = logging.getLogger(__name__)


def save_image(image_data: str, directory: Path) -> Optional[Path]:
    """Base64エンコードされた画像データをデコードして保存し、ファイルパスを返す"""
    try:
        # "data:image/png;base64,..." を除去
        base64_data = image_data.split(",", 1)[1]
    except IndexError as e:
        logger.error("image_data の形式が不正です。カンマが含まれていません。", exc_info=True)
        return None

    try:
        image_bytes = base64.b64decode(base64_data)
    except base64.binascii.Error as e:
        logger.error("Base64デコードに失敗しました。", exc_info=True)
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.error("PILが画像を開く際にエラーが発生しました。", exc_info=True)
        return None

    # ユニークなファイル名を生成
    file_name = f"{uuid.uuid4()}.png"

    # 保存ディレクトリを作成（既に作成済みの場合はスキップ）
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error("ディレクトリの作成中にエラーが発生しました。", exc_info=True)
        return None

    file_path = directory / file_name

    try:
        image.save(file_path)
        logger.info(f"画像を保存しました: {file_path}")
        return file_path
    except Exception as e:
        logger.error("画像の保存中にエラーが発生しました:", exc_info=True)
        return None


def save_generated_image(generated_image: Image.Image, directory: Path) -> Optional[Path]:
    """
    PIL.Image.Image オブジェクトを保存し、ファイルパスを返す関数
    :param generated_image: PIL Image object
    :param directory: 保存先ディレクトリ
    :return: 保存されたファイルのPathオブジェクト
    """
    try:
        # ユニークなファイル名を生成
        unique_suffix = uuid.uuid4().hex
        file_name = f"generated_{unique_suffix}.png"
        file_path = directory / file_name

        # 保存ディレクトリを作成（既に作成済みの場合はスキップ）
        directory.mkdir(parents=True, exist_ok=True)

        # 画像を保存
        generated_image.save(file_path, format="PNG")
        logger.info(f"Generated image saved to {file_path}")
        return file_path
    except Exception as e:
        logger.exception("Failed to save generated image", exc_info=True)
        return None
