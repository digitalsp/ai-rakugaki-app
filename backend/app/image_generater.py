# backend/app/image_generator.py

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# モデルのロード（事前に必要なモデルをダウンロードしておく）
model_id = "CompVis/stable-diffusion-v1-4"
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = StableDiffusionPipeline.from_pretrained(model_id)
pipe = pipe.to(device)

def main(input_image_path: str, prompt: str, output_image_path: str):
    """
    AIによる画像生成を実行するメイン関数。
    input_image_path: キャンバス画像のパス
    prompt: 画像生成のプロンプト
    output_image_path: 生成画像の出力パス
    """
    try:
        # 入力画像の読み込み
        input_image = Image.open(input_image_path).convert("RGB")

        # 画像生成
        generated_image = pipe(prompt=prompt, init_image=input_image, strength=0.8).images[0]

        # 生成画像の保存
        generated_image.save(output_image_path)
    except Exception as e:
        raise RuntimeError(f"画像生成中にエラーが発生しました: {e}")


# import torch
# from PIL import Image
# import cv2
# from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
# from transformers import CLIPTextModel, CLIPTokenizer
# from diffusers.utils import load_image

# # GPUが利用可能かチェック
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # ControlNet Scribble モデルの読み込み
# controlnet = ControlNetModel.from_pretrained(
#     "lllyasviel/sd-controlnet-scribble", torch_dtype=torch.float16
# ).to(device)

# # Stable Diffusion XL Turbo モデルの読み込み
# pipe = StableDiffusionControlNetPipeline.from_pretrained(
#     "stabilityai/stable-diffusion-xl-turbo", controlnet=controlnet, torch_dtype=torch.float16
# ).to(device)

# # 高速化のためにmemory efficient attentionを有効化
# pipe.enable_xformers_memory_efficient_attention()

# # 手書きScribble画像の読み込みと前処理
# def preprocess_image(image_path):
#     image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # 画像をグレースケールで読み込む
#     image = cv2.resize(image, (512, 512))  # Stable Diffusionが要求するサイズにリサイズ
#     image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)  # 3チャンネルに変換
#     pil_image = Image.fromarray(image)  # PIL形式に変換
#     return pil_image

# # Scribble画像とテキストプロンプトを指定
# scribble_image_path = "scribble.png"  # 手書きのScribble画像のパス
# scribble_image = preprocess_image(scribble_image_path)
# text_prompt = "a futuristic cityscape with neon lights at night"

# # 画像生成
# generated_images = pipe(prompt=text_prompt, image=scribble_image, num_inference_steps=50).images

# # 生成された画像を保存
# generated_image = generated_images[0]
# generated_image.save("generated_image.png")

# print("画像生成が完了しました。結果は 'generated_image.png' に保存されました。")
