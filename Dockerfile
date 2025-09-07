# --- ステージ1: ビルド環境 ---
FROM python:3.11-slim as builder

# ビルドに必要なパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# pip自身をアップグレード
RUN pip install --upgrade pip

# requirements.txtからホイールを作成
WORKDIR /wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# --- ステージ2: 実行環境 ---
FROM python:3.11-slim

# llama.cppがCPUで並列処理を行うために必要なライブラリ
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# ビルド環境からホイールをコピーしてインストール
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl
RUN rm -rf /wheels

# アプリケーションのコードをコピー
COPY ./app /app

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]