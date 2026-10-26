
from ollama import chat

MODEL_NAME = "qwen2.5:3b"


def ask_llm(question: str) -> str:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": question + "\n/no_think"
            }
        ],
        think=False,
        keep_alive="10m",
        options={
            "num_predict": 128,
            "temperature": 0.2
        }
    )

    return response.message.content.strip()
