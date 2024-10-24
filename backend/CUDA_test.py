import torch
from controlnet_aux import CannyDetector
from diffusers import DDIMScheduler  # 高速なスケジューラのインポート
from diffusers import (AutoencoderKL, EulerAncestralDiscreteScheduler,
                       StableDiffusionXLAdapterPipeline, T2IAdapter)
from diffusers.utils import load_image
from PIL import Image

# cuDNNの最適化設定
# torch.backends.cudnn.benchmark = True

# GPUが使用可能か確認
device = "cuda" if torch.cuda.is_available() else "cpu"

# T2I-Adapterの読み込み（torch_dtypeをfloat32に設定）
t2i_adapter_model = T2IAdapter.from_pretrained(
    "TencentARC/t2i-adapter-sketch-sdxl-1.0",
    torch_dtype=torch.float16, varient="fp16"  # float16からfloat32に変更
).to(device)

model_id = 'OnomaAIResearch/Illustrious-xl-early-release-v0'

# # スケジューラの読み込み（DDIMSchedulerを使用）

# scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")

# スケジューラーの準備
euler_a = EulerAncestralDiscreteScheduler.from_pretrained(
    "OnomaAIResearch/Illustrious-xl-early-release-v0",
    subfolder="scheduler"
)

# VAEの読み込み（torch_dtypeをfloat32に設定）
vae = AutoencoderKL.from_pretrained(
    "madebyollin/sdxl-vae-fp16-fix",
    torch_dtype=torch.float16  # float16からfloat32に変更
).to(device)

# パイプラインの構築（torch_dtypeをfloat32に設定）
pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
    model_id,  # model_id,
    vae=vae,
    adapter=t2i_adapter_model,
    scheduler=euler_a,
    torch_dtype=torch.float16,
    varient="fp16"  # float16からfloat32に変更
).to(device)

# Attention Slicingの有効化
pipe.enable_attention_slicing()

# CannyDetectorを使ってエッジ検出
canny_detector = CannyDetector()
image_path = "./saved-images/a1dca005-edf6-4364-ad5c-969c20ba3cf4.png"
image = load_image(image_path)
image = canny_detector(image, detect_resolution=384, image_resolution=1024)

# テキストプロンプト
prompt = "masterpiece, flying ufo, flying object, space, stars, moon, earth"
negative_prompt = "bad quality, low quality, lowres, displeasing, very displeasing, bad anatomy, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed"

# 画像生成（推論ステップ数10）
gen_images = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=image,
    num_inference_steps=25,  # 推論ステップ数
    guidance_scale=5.5,
    adapter_conditioning_scale=0.8
).images[0]

# 生成された画像を保存
gen_images.save('generated_image.png')
