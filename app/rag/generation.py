
from app.llm.client import ask_llm

NOT_FOUND = "NOT_FOUND"
GENERAL_PREFIX = "General knowledge (not verified against the PDF):"


def generate_answer(question: str, documents: list[dict]) -> str:
    if not documents:
        return generate_general_answer(question)

    context_parts = []

    for doc in documents:
        context_parts.append(
            f"PDF page {doc.get('page', 'unknown')}:\n{doc['text']}"
        )

    context = "\n\n".join(context_parts)
    print(f"[DEBUG] Context characters: {len(context)}")
    print(f"[DEBUG] Context words: {len(context.split())}")

    document_prompt = f"""
You are a PDF question-answering assistant.

Answer using ONLY the provided document context.

Rules:
- Answer directly and clearly.
- Do not use general knowledge.
- Do not invent information.
- A heading or table of contents alone is not a complete answer.
- If the context does not contain enough information to answer,
  output exactly: NOT_FOUND
- Do not show reasoning.

Document context:
{context}

Question: {question}

Answer:
"""

    document_answer = ask_llm(document_prompt).strip()
    print("\n[DEBUG] Document answer:")
    print(document_answer)

    if (
        not document_answer
        or NOT_FOUND in document_answer.upper()
    ):
        print("[DEBUG] Using general-knowledge fallback")
        answer = generate_general_answer(question)

        if not answer.startswith(GENERAL_PREFIX):
            answer = f"{GENERAL_PREFIX}\n\n{answer}"

        return answer
    print("[DEBUG] Using document answer")
    return document_answer


def generate_general_answer(question: str) -> str:
    general_prompt = f"""
You are a helpful general-knowledge assistant.

Rules:
- Answer directly in simple language.
- Do not show reasoning.
- If uncertain, say so.
- Do not claim that the answer came from the PDF.

Question: {question}

Answer:
"""

    answer = ask_llm(general_prompt).strip()

    if not answer:
        answer = "I couldn't generate an answer. Please try again."

    if not answer.startswith(GENERAL_PREFIX):
        answer = f"{GENERAL_PREFIX}\n\n{answer}"

    return answer
