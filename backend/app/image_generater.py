# backend/app/image_generator.py

import os
from pathlib import Path
from typing import Optional

import torch
from diffusers import ControlNetModel, StableDiffusionControlNetPipeline
from PIL import Image
from transformers import CLIPTextModel, CLIPTokenizer

# 環境変数や設定
CONTROLNET_MODEL_NAME = "lllyasviel/control_v11p_sd15_scribble"
STABLE_DIFFUSION_MODEL_NAME = "runwayml/stable-diffusion-v1-5"

# デバイス設定
device = "cuda" if torch.cuda.is_available() else "cpu"

# モデルのロード


def load_models():
    print("Loading ControlNet model...")
    controlnet = ControlNetModel.from_pretrained(
        CONTROLNET_MODEL_NAME, torch_dtype=torch.float16 if device == "cuda" else torch.float32)
    print("Loading Stable Diffusion model with ControlNet...")
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        STABLE_DIFFUSION_MODEL_NAME,
        controlnet=controlnet,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    pipe = pipe.to(device)
    pipe.enable_xformers_memory_efficient_attention()
    return pipe

# 画像生成関数


def generate_image(pipe, input_image_path: str, prompt: str, output_image_path: str, guidance_scale: float = 7.5, num_inference_steps: int = 50):
    try:
        print(f"Processing input image: {input_image_path}")
        init_image = Image.open(input_image_path).convert("RGB")
        init_image = init_image.resize((768, 768))  # サイズ調整

        print(f"Generating image with prompt: {prompt}")
        output = pipe(
            prompt=prompt,
            control_image=init_image,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images[0]

        output.save(output_image_path)
        print(f"Generated image saved to: {output_image_path}")
    except Exception as e:
        print(f"Error during image generation: {e}")

# メイン関数


def main(input_image_path: str, prompt: str, output_image_path: str):
    if not os.path.exists(input_image_path):
        print(f"Input image does not exist: {input_image_path}")
        return

    pipe = load_models()
    generate_image(pipe, input_image_path, prompt, output_image_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate image using ControlNet and Stable Diffusion.")
    parser.add_argument("--input", type=str, required=True,
                        help="Path to the input scribble image.")
    parser.add_argument("--prompt", type=str, required=True,
                        help="Text prompt for image generation.")
    parser.add_argument("--output", type=str, required=True,
                        help="Path to save the generated image.")

    args = parser.parse_args()
    main(args.input, args.prompt, args.output)
