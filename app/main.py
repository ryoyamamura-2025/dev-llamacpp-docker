import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from llama_cpp import Llama

from google.cloud import storage
from google.api_core.exceptions import NotFound

# --- FastAPIアプリの初期化 ---
app = FastAPI()

# --- モデルの読み込み ---
# ローカルに保存するモデルのパス
LOCAL_MODEL_DIR = "./models"
LOCAL_MODEL_FILENAME = "model.gguf"
LOCAL_MODEL_PATH = os.path.join(LOCAL_MODEL_DIR, LOCAL_MODEL_FILENAME)

def download_model_from_gcs(bucket_name: str, source_blob_name: str, destination_file_name: str):
    """GCSからファイルをダウンロードする"""
    try:
        storage_client = storage.Client() # Fallback to default credentials (e.g., ADC)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        print(f"Downloading model from gs://{bucket_name}/{source_blob_name} to {destination_file_name}...")
        
        # 保存先ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
        
        blob.download_to_filename(destination_file_name)
        print("Model downloaded successfully.")
    except NotFound:
        raise FileNotFoundError(f"Model file not found in GCS: gs://{bucket_name}/{source_blob_name}")
    except Exception as e:
        raise RuntimeError(f"Failed to download model from GCS: {e}")

# ローカルにモデルファイルが存在しない場合、GCSからダウンロードを試みる
if not os.path.exists(LOCAL_MODEL_PATH):
    print(f"Model not found locally at {LOCAL_MODEL_PATH}.")
    GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
    GCS_MODEL_BLOB_NAME = os.environ.get("GCS_MODEL_BLOB_NAME")
    if GCS_BUCKET_NAME and GCS_MODEL_BLOB_NAME:
        download_model_from_gcs(GCS_BUCKET_NAME, GCS_MODEL_BLOB_NAME, LOCAL_MODEL_PATH)
    else:
        raise FileNotFoundError(
            f"Model file not found at {LOCAL_MODEL_PATH} and GCS environment variables "
            "(GCS_BUCKET_NAME, GCS_MODEL_BLOB_NAME) are not set."
        )
    
# モデルをメモリにロード
print(f"Loading model from {LOCAL_MODEL_PATH}...")
llm = Llama(
    model_path=LOCAL_MODEL_PATH,
    n_gpu_layers=0,   # GPUにオフロードするレイヤー数 (-1は全て。今回はCPUなので0)
    n_ctx=2048,       # コンテキストサイズ
    verbose=False     # 冗長なログを無効化
)
print("Model loaded successfully.")

# --- APIのリクエストボディの定義 ---
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 256

# --- 静的ファイル（HTML/JS）の配信設定 ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """ルートパスにアクセスした際にindex.htmlを返す"""
    return FileResponse("static/index.html")

# --- 推論APIのエンドポイント ---
@app.post("/generate")
async def generate(request: PromptRequest):
    """プロンプトを受け取り、LLMからの応答を生成して返す"""
    
    # Gemma用のチャットテンプレート形式
    messages = [
        {"role": "user", "content": request.prompt}
    ]
    
    # Llama.cppでチャット形式のプロンプトを生成
    response_json = llm.create_chat_completion(messages=messages)

    response_text = response_json["choices"][0]["message"]["content"].strip()
    return {"response": response_text}

print("Server is ready.")