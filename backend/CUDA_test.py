# import torch
# from diffusers import StableDiffusionXLAdapterPipeline, T2IAdapter
# from PIL import Image
# from transformers import CLIPTextModel, CLIPTokenizer

# # GPUが使用可能か確認
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # SDXLとT2I-Adapterのモデルを読み込む
# sdxl_model = "OnomaAIResearch/Illustrious-xl-early-release-v0"

# # T2I-Adapterの準備
# adapter = T2IAdapter.from_pretrained(
#     "TencentARC/t2i-adapter-canny-sdxl-1.0",  # canny
#     torch_dtype=torch.float16,
#     varient="fp16"
# ).to("cuda")

# # 必要なコンポーネントを全て読み込む
# pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
#     sdxl_model,
#     adapter=adapter,  # ここでT2IAdapterオブジェクトを渡す
#     feature_extractor="stabilityai/clip-vit-large-patch14",  # feature_extractorを追加
#     image_encoder="stabilityai/sdxl-image-encoder",  # image_encoderを追加
#     torch_dtype=torch.float16
# ).to(device)

# # VAEを適用する場合
# vae_model = "stabilityai/sdxl-vae"
# pipe.vae = AutoencoderKL.from_pretrained(
#     vae_model, torch_dtype=torch.float16).to(device)

# # テキストプロンプト
# prompt = "A futuristic cityscape with neon lights at night"

# # 画像プロンプト (画像の事前処理を行う)


# def load_image(image_path):
#     image = Image.open(image_path).convert("RGB")
#     image = image.resize((512, 512))
#     return image


# image_path = "backend/saved-images/bda1df4e-92e5-4535-bb79-a7cc68b92ffc.png"
# image = load_image(image_path)

# # 画像生成
# result = pipe(prompt=prompt, image=image, num_inference_steps=50).images

# # 生成された画像を保存
# result[0].save("generated_image.png")

# import torch
# from controlnet_aux.canny import CannyDetector
# from diffusers import (AutoencoderKL, EulerAncestralDiscreteScheduler,
#                        StableDiffusionXLAdapterPipeline, T2IAdapter)
# from diffusers.utils import load_image
# from PIL import Image

# # GPUが使用可能か確認
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # T2I-Adapterの読み込み
# t2i_adapter_model = T2IAdapter.from_pretrained(
#     "TencentARC/t2i-adapter-canny-sdxl-1.0", torch_dtype=torch.float16, variant="fp16").to(device)

# # スケジューラの読み込み
# model_id = 'stabilityai/stable-diffusion-xl-base-1.0'
# euler_a = EulerAncestralDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
# vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)

# # パイプラインの構築
# pipe = StableDiffusionXLAdapterPipeline.from_pretrained(
#     model_id, vae=vae, adapter=t2i_adapter_model, scheduler=euler_a, torch_dtype=torch.float16, variant="fp16").to(device)

# # メモリ効率化のための設定
# # pipe.enable_xformers_memory_efficient_attention()

# # CannyDetectorを使ってエッジ検出
# canny_detector = CannyDetector()
# image_url = "https://huggingface.co/Adapter/t2iadapter/resolve/main/figs_SDXLV1.0/org_canny.jpg"
# image = load_image(image_url)
# image = canny_detector(image, detect_resolution=384, image_resolution=1024)

# # テキストプロンプト
# prompt = "A futuristic cityscape with neon lights at night"
# negative_prompt = "extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed"

# # 画像生成
# gen_images = pipe(
#     prompt=prompt,
#     negative_prompt=negative_prompt,
#     image=image,
#     num_inference_steps=30,
#     guidance_scale=7.5,
#     adapter_conditioning_scale=0.8
# ).images[0]

# # 生成された画像を保存
# gen_images.save('generated_image.png')

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
    "TencentARC/t2i-adapter-canny-sdxl-1.0",
    torch_dtype=torch.float16, varient="fp16"  # float16からfloat32に変更
).to(device)

model_id = 'stabilityai/stable-diffusion-xl-base-1.0'
# # スケジューラの読み込み（DDIMSchedulerを使用）

# scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")

# スケジューラーの準備
euler_a = EulerAncestralDiscreteScheduler.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
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
# image_url = "https://huggingface.co/Adapter/t2iadapter/resolve/main/figs_SDXLV1.0/org_canny.jpg"
image_path = "./saved-images/bda1df4e-92e5-4535-bb79-a7cc68b92ffc.png"
image = load_image(image_path)
image = canny_detector(image, detect_resolution=384, image_resolution=1024)

# テキストプロンプト
prompt = "A futuristic cityscape with neon lights at night"
negative_prompt = "extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed"

# 画像生成（推論ステップ数を30から20に削減）
gen_images = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=image,
    num_inference_steps=20,  # 推論ステップ数の削減
    guidance_scale=7.5,
    adapter_conditioning_scale=0.8
).images[0]

# 生成された画像を保存
gen_images.save('generated_image.png')
