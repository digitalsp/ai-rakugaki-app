# ベースイメージとして公式のPythonイメージを使用
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# 環境変数の設定
# Huggingfaceのキャッシュ先ディレクトリ変更
ENV HF_HOME=/app/.cache/huggingface
ENV DEBIAN_FRONTEND=noninteractive
# .pycを作らないように
ENV PYTHONDONTWRITEBYTECODE=1
# バッファの無効化
ENV PYTHONUNBUFFERED=1
# torchvisionでpretrainedのモデルを保存する場所
ENV TORCH_HOME=/app/.cache/torchvision

# システム依存パッケージのインストール
RUN apt update && \
    apt install -y bash \
    build-essential \
    git \
    git-lfs \
    curl \
    ca-certificates \
    libsndfile1-dev \
    libgl1 \
    python3.11 \
    python3-pip \
    python3.11-venv && \
    rm -rf /var/lib/apt/lists

# 作業ディレクトリの作成
WORKDIR /app


# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# アプリケーションコードをコピー
COPY app /app/app


# ポートの設定
EXPOSE 8000

# サービスの起動
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
