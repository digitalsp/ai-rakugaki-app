# ベースイメージとして公式のPythonイメージを使用
FROM nvidia/cuda:12.6.2-cudnn-runtime-ubuntu22.04

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

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev



# Copy the application into the container.
COPY . /app

# Install the application dependencies.
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# アプリケーションコードをコピー
COPY app /app/app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []


# サービスの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
