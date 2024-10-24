# backend/app/image_generater.py

import logging

import torch
from controlnet_aux import CannyDetector
from diffusers import (AutoencoderKL, EulerAncestralDiscreteScheduler,
                       StableDiffusionXLAdapterPipeline, T2IAdapter)
from diffusers.utils import load_image
from PIL import Image

# ロギングの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# GPUが使用可能か確認
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

# T2I-Adapterの読み込み（torch_dtypeをfloat16に設定）
try:
    t2i_adapter_model = T2IAdapter.from_pretrained(
        "TencentARC/t2i-adapter-sketch-sdxl-1.0",
        torch_dtype=torch.float16, varient="fp16"
    ).to(device)
    logger.info("T2I-Adapter model loaded successfully.")
except Exception as e:
    logger.exception(f"Failed to load T2I-Adapter model: {e}")
    raise e

model_id = 'OnomaAIResearch/Illustrious-xl-early-release-v0'

# スケジューラーの準備
try:
    euler_a = EulerAncestralDiscreteScheduler.from_pretrained(
        model_id,
        subfolder="scheduler"
    )
    logger.info("Scheduler loaded successfully.")
except Exception as e:
    logger.exception(f"Failed to load scheduler: {e}")
    raise e

# VAEの読み込み（torch_dtypeをfloat16に設定）

try:
    vae = AutoencoderKL.from_pretrained(
        "madebyollin/sdxl-vae-fp16-fix",
        torch_dtype=torch.float16
    ).to(device)
    logger.info("VAE loaded successfully.")
except Exception as e:
    logger.exception(f"Failed to load VAE: {e}")
    raise e

# パイプラインの構築（torch_dtypeをfloat16に設定）
try:
    pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
        model_id,
        vae=vae,
        adapter=t2i_adapter_model,
        scheduler=euler_a,
        torch_dtype=torch.float16,
        varient="fp16"
    ).to(device)
    logger.info("Image generation pipeline loaded successfully.")
except Exception as e:
    logger.exception(f"Failed to load image generation pipeline: {e}")
    raise e

# Attention Slicingの有効化
pipe.enable_attention_slicing()
logger.info("Attention slicing enabled.")

# CannyDetectorの初期化
canny_detector = CannyDetector()
logger.info("CannyDetector initialized successfully.")

# パイプラインをグローバルに保持
__all__ = ['pipe', 'canny_detector']
