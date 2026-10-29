import os

from ollama import Client

MODEL_NAME = "qwen3:4b"


def ask_llm(question: str) -> str:
    """Generate an answer using an Ollama server."""

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    client = Client(host=host)

    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
    )

    answer = response.message.content

    if not answer:
        raise RuntimeError("Ollama returned an empty response.")

    return answer.strip()
