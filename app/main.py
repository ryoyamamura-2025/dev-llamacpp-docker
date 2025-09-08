from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from llama_cpp import Llama
import os

# --- FastAPIアプリの初期化 ---
app = FastAPI()

# --- モデルの読み込み ---
model_path = "./models/gemma-3-270m-it-Q4_K_M.gguf"

if not os.path.exists(model_path):
    raise FileNotFoundError(
        f"Model file not found at {model_path}. "
        "Make sure you have downloaded the model and mounted the 'models' directory correctly."
    )

# モデルをメモリにロード
llm = Llama(
    model_path=model_path,
    n_gpu_layers=0,   # GPUにオフロードするレイヤー数 (-1は全て。今回はCPUなので0)
    n_ctx=2048,       # コンテキストサイズ
    verbose=False     # 冗長なログを無効化
)

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