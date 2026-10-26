
import time

from app.rag.retriever import retrieve
from app.rag.generation import generate_answer


def ask_question_with_sources(
    question: str,
    source_id: str | None = None
) -> dict:
    start_time = time.perf_counter()

    documents = retrieve(
        question,
        n_results=3,
        source_id=source_id
    )

    retrieval_time = time.perf_counter() - start_time

    generation_start = time.perf_counter()
    answer = generate_answer(question, documents)
    generation_time = time.perf_counter() - generation_start

    total_time = time.perf_counter() - start_time

    print(f"Retrieval time: {retrieval_time:.2f} seconds")
    print(f"Generation time: {generation_time:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    sources = []

    # Show citations only when the answer appears to use PDF context.
    is_general_answer = answer.startswith(
        "General knowledge (not verified against the PDF):"
    )

    if documents and not is_general_answer:
        seen = set()

        for document in documents:
            source = document.get("source", "Unknown PDF")
            page = document.get("page", "Unknown")

            citation = (source, page)

            if citation not in seen:
                seen.add(citation)
                sources.append({
                    "filename": source,
                    "page": page
                })

    return {
        "answer": answer,
        "sources": sources
    }


def ask_question(
    question: str,
    source_id: str | None = None
) -> str:
    result = ask_question_with_sources(
        question,
        source_id=source_id
    )

    return result["answer"]
