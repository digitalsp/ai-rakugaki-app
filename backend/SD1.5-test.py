# import torch
# from controlnet_aux import CannyDetector
# from diffusers import DDIMScheduler  # 高速なスケジューラのインポート
# from diffusers import (AutoencoderKL, AutoPipelineForText2Image,
#                        EulerAncestralDiscreteScheduler)
# from diffusers.utils import load_image
# from PIL import Image

# # cuDNNの最適化設定
# # torch.backends.cudnn.benchmark = True

# # GPUが使用可能か確認
# device = "cuda" if torch.cuda.is_available() else "cpu"


# # IP-Adapter をロードする
# pipe.load_ip_adapter(
#     "h94/IP-Adapter",
#     subfolder="models",
#     weight_name="ip-adapter_sd15.bin"
# )
# pipe.set_ip_adapter_scale(0.6)

# model_id = 'syaimu/7th_Layer/7th_anime_v3_C'

# # # スケジューラの読み込み（DDIMSchedulerを使用）

# # scheduler = DDIMScheduler.from_pretrained(model_id, subfolder="scheduler")

# # スケジューラーの準備
# euler_a = EulerAncestralDiscreteScheduler.from_pretrained(
#     "",
#     subfolder="scheduler"
# )

# # VAEの読み込み（torch_dtypeをfloat32に設定）
# vae = AutoencoderKL.from_pretrained(
#     "madebyollin/sdxl-vae-fp16-fix",
#     torch_dtype=torch.float16  # float16からfloat32に変更
# ).to(device)

# # パイプラインの構築（torch_dtypeをfloat32に設定）
# pipe = AutoPipelineForText2Image.from_pretrained(
#     model_id,  # model_id,
#     vae=vae,
#     adapter=t2i_adapter_model,
#     scheduler=euler_a,
#     torch_dtype=torch.float16,
#     varient="fp16"  # float16からfloat32に変更
# ).to(device)

# # Attention Slicingの有効化
# pipe.enable_attention_slicing()

# # CannyDetectorを使ってエッジ検出
# canny_detector = CannyDetector()
# image_path = "./saved-images/cf5fa3b1-e11f-4e7d-9a03-b5483f182bae.png"
# image = load_image(image_path)
# image = canny_detector(image, detect_resolution=384, image_resolution=1024)

# # テキストプロンプト
# # prompt = "masterpiece, flying ufo, flying object, space, stars, moon, earth"
# # negative_prompt = "bad quality, low quality, lowres, displeasing, very displeasing, bad anatomy, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, low quality, glitch, deformed"

# prompt="masterpiece, cool, robot, futuristic"
# negative_prompt="low quality, bad anatomy, missing limbs, bad quality, lowres, displeasing, very displeasing, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality, glitch, deformed, text, error, missing, watermark, unfinished, signature, username, abstract"

# # 画像生成（推論ステップ数10）
# gen_images = pipe(
#     prompt=prompt,
#     negative_prompt=negative_prompt,
#     image=image,
#     num_inference_steps=25,  # 推論ステップ数
#     guidance_scale=5.5,
#     adapter_conditioning_scale=0.8
# ).images[0]

# # 生成された画像を保存
# gen_images.save('generated_image.png')

# import torch
# from controlnet_aux import CannyDetector
# from diffusers import (AutoencoderKL, ControlNetModel,
#                        StableDiffusionControlNetPipeline,
#                        UniPCMultistepScheduler)
# from diffusers.utils import load_image
# from PIL import Image

# # GPUが使用可能か確認
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # model_id = "syaimu/7th_Layer"
# model_id = "runwayml/stable-diffusion-v1-5"

# # ControlNetのScribbleモデルの読み込み
# controlnet = ControlNetModel.from_pretrained(
#     "lllyasviel/control_v11p_sd15_scribble",
#     torch_dtype=torch.float16
# ).to(device)

# # VAEの読み込み
# vae = AutoencoderKL.from_pretrained(
#     "stabilityai/sd-vae-ft-mse",
#     torch_dtype=torch.float16  # VAE用の適切なモデルに変更
# ).to(device)

# # DPM++ 2M Karrasサンプラーの設定
# # scheduler = DPMSolverMultistepScheduler.from_pretrained(
# #     model_id,  # モデルIDに合わせる
# #     subfolder="scheduler",
# # )

# # パイプラインの構築（Stable DiffusionとControlNetを使用）
# pipe = StableDiffusionControlNetPipeline.from_pretrained(
#     model_id,
#     controlnet=controlnet,
#     vae=vae,
#     # scheduler=scheduler,
#     torch_dtype=torch.float16,  # FP16で高速化
#     use_safetensors=True
# ).to(device)

# # Attention Slicingの有効化
# pipe.enable_attention_slicing()

# # Cannyエッジ検出器を利用して画像の前処理
# canny_detector = CannyDetector()
# image_path = "./saved-images/cf5fa3b1-e11f-4e7d-9a03-b5483f182bae.png"
# image = load_image(image_path)
# image = canny_detector(image, detect_resolution=384, image_resolution=1024)

# # テキストプロンプトとネガティブプロンプト
# prompt = "masterpiece, cool, robot, futuristic"
# negative_prompt = "low quality, bad anatomy, missing limbs, bad quality, lowres, displeasing, very displeasing, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality"

# # 画像生成
# gen_images = pipe(
#     prompt=prompt,
#     negative_prompt=negative_prompt,
#     image=image,
#     num_inference_steps=25,  # 推論ステップ数
#     guidance_scale=8,  # ガイダンススケールの調整
#     controlnet_conditioning_scale=0.8  # ControlNet用のスケール
# ).images[0]

# # 生成された画像を保存
# gen_images.save('generated_image.png')

# import torch
# from controlnet_aux import CannyDetector
# from diffusers import DDIMScheduler, DPM++2M KarrasScheduler  # DPM++ 2M Karrasスケジューラのインポート
# from diffusers import (AutoencoderKL, AutoPipelineForText2Image, EulerAncestralDiscreteScheduler)
# from diffusers.utils import load_image
# from PIL import Image

# # cuDNNの最適化設定
# # torch.backends.cudnn.benchmark = True

# # GPUが使用可能か確認
# device = "cuda" if torch.cuda.is_available() else "cpu"

# model_id = 'syaimu/7th_Layer/7th_layer_v3_C'

# # スケジューラーの準備
# euler_a = DPM++2M KarrasScheduler.from_pretrained(
#     model_id,
#     subfolder="scheduler"
# )

# # VAEの読み込み
# vae = AutoencoderKL.from_pretrained(
#     "stabilityai/sd-vae-ft-mse",
#     torch_dtype=torch.float16
# ).to(device)

# # パイプラインの構築
# pipe = AutoPipelineForText2Image.from_pretrained(
#     model_id,
#     vae=vae,
#     scheduler=euler_a,
#     torch_dtype=torch.float16,
#     variant="fp16"
# ).to(device)

# # Attention Slicingの有効化
# pipe.enable_attention_slicing()

# image_path = "./saved-images/cf5fa3b1-e11f-4e7d-9a03-b5483f182bae.png"
# image = load_image(image_path)
# image = CannyDetector()(image, detect_resolution=384, image_resolution=1024)

# # テキストプロンプト
# prompt="masterpiece, cool, robot, futuristic"
# negative_prompt="low quality, bad anatomy, missing limbs, bad quality, lowres, displeasing, very displeasing, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality"

# # 画像生成
# gen_images = pipe(
#     prompt=prompt,
#     negative_prompt=negative_prompt,
#     image=image,
#     num_inference_steps=25,
#     guidance_scale=8,
# ).images[0]

# # 生成された画像を保存
# gen_images.save('generated_image.png')

import torch
from controlnet_aux import HEDdetector
from diffusers import AutoencoderKL  # UniPCMultistepScheduler,
from diffusers import (ControlNetModel, EulerAncestralDiscreteScheduler,
                       StableDiffusionControlNetPipeline)
from diffusers.utils import load_image
from PIL import Image

# GPUが使用可能か確認
device = "cuda" if torch.cuda.is_available() else "cpu"

# モデルID
model_id = "nablaThetaA5LinesAndColors_v10.safetensors"
model_PATH = "./app/weight/nablaThetaA5LinesAndColors_v10.safetensors"
controlnet_checkpoint = "lllyasviel/control_v11p_sd15_scribble"

# HED検出器を使用した前処理
image_path = "./saved-images/cf5fa3b1-e11f-4e7d-9a03-b5483f182bae.png"
image = load_image(image_path)

# HED検出器を使って画像を前処理
processor = HEDdetector.from_pretrained('lllyasviel/Annotators')
control_image = processor(image, scribble=True)
control_image.save("./pretreatmented-images/control.png")  # 前処理された画像を保存

# ControlNetのモデルを読み込み
controlnet = ControlNetModel.from_pretrained(
    controlnet_checkpoint,
    torch_dtype=torch.float16
).to(device)

# パイプラインの構築（Stable DiffusionとControlNetを使用）
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    # model_id,
    pretrained_model_name_or_path = model_PATH,
    controlnet=controlnet,
    torch_dtype=torch.float16,  # FP16で高速化
).to(device)

# スケジューラの設定（UniPCMultistepSchedulerを使用）
# pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
# euler_a = EulerAncestralDiscreteScheduler.from_pretrained(
#     "",
#     subfolder="scheduler"
# )

SCHEDULERS_LIST = {
    'EulerAncestralDiscrete' : EulerAncestralDiscreteScheduler,
    # 'EulerDiscrete' : EulerDiscreteScheduler,
}

CACHE_DIR = './cache'

pipe.scheduler = SCHEDULERS_LIST[EulerAncestralDiscrete].from_pretrained(
    pretrained_model_name_or_path="EulerAncestralDiscrete",
    torch_dtype=torch.float16,
    cache_dir=CACHE_DIR,
    subfolder='scheduler'
)

# Attention Slicingの有効化（メモリ節約）
pipe.enable_attention_slicing()

# テキストプロンプトとネガティブプロンプト
prompt = "masterpiece, cool, robot, futuristic"
negative_prompt = "low quality, bad anatomy, missing limbs, bad quality, lowres, displeasing, very displeasing, bad hands, scan artifacts, monochrome, guro, extra digit, fewer digits, cropped, worst quality"

# シード値の設定（再現性のため）
# generator = torch.manual_seed(0)

# 画像生成
gen_images = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=control_image,  # 前処理された画像を使用
    num_inference_steps=30,  # 推論ステップ数
    guidance_scale=6.0,  # ガイダンススケールの調整
    controlnet_conditioning_scale=0.9,  # ControlNet用のスケール
    # generator=generator
).images[0]

# 生成された画像を保存
gen_images.save('generated_image.png')
