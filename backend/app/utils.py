# backend/app/utils.py

import base64
import logging
import os
import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


def save_image(image_data: str, save_dir: str) -> Image.Image:
    """
    Base64エンコードされた画像データをデコードしてPIL Imageオブジェクトとして返す。
    """
    try:
        # データURLからBase64部分を抽出
        header, encoded = image_data.split(",", 1)
        # Base64デコード
        decoded = base64.b64decode(encoded)
        # バイトストリームから画像を開く
        image = Image.open(BytesIO(decoded)).convert("RGB")
        return image
    except Exception as e:
        logger.exception(f"画像データの保存に失敗しました: {e}")
        raise


def save_generated_image(image: Image.Image, save_dir: str) -> Path:
    """
    生成された画像を指定されたディレクトリに保存し、ファイルパスを返す。
    """
    try:
        filename = f"generated_{uuid.uuid4().hex}.png"
        file_path = Path(save_dir) / filename
        image.save(file_path, format="PNG")
        logger.info(f"生成画像を保存しました: {file_path}")
        return file_path
    except Exception as e:
        logger.exception(f"生成画像の保存に失敗しました: {e}")
        return None
