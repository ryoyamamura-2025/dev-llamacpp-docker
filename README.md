# Llama-cpp and FastAPI Simple App
Gemma を llama-cpp-python で動かして FastAPI で Web アプリ化し Cloud run にデプロイするプロジェクト

## やりたいこと
-  `.gguf` 形式のモデルを搭載し、
- HTML/CSS/JavaScript で作られたフロントエンドを持ち、
- FastAPI でサーブされ、Cloud run でホストされる
Web アプリを作成する  

⇒ OSS の LLM を組み込んだ Web アプリを作成する能力が身につく

## 環境構築 & デプロイ
Cloud run でのデプロイを見越して Docker で環境を構築 。

1. `docker build -t llama-fastapi-app:latest .` でビルド。 `bash restart-container.sh` でコンテナ起動。
    - マルチステージビルドで Docker イメージを軽量化 & Llama-cpp を動かすための C++ のコンパイラを最終的なイメージから分離
2. `bash deploy.sh` でデプロイ


### 参考

Gemma からのレスポンス
```
{
  "response": {
    "id": "chatcmpl-79f362b9-de48-4587-a1b5-039bff781336",
    "object": "chat.completion",
    "created": 1757337445,
    "model": "./models/gemma-3-270m-it-Q4_K_M.gguf",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "I am Gemma, a large language model, created by Google DeepMind.\n"
        },
        "logprobs": null,
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 15,
      "completion_tokens": 16,
      "total_tokens": 31
    }
  }
}
```