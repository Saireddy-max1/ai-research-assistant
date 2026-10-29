from app.rag.embeddings import embed_text
from app.rag.vector_store import search_documents

MAX_DISTANCE = 0.70


def retrieve(
    question: str,
    n_results: int = 3,
    source_id: str | None = None,
) -> list[dict]:
    query_embedding = embed_text(question)

    results = search_documents(
        query_embedding=query_embedding,
        n_results=n_results,
        source_id=source_id,
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_documents = []

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        if distance > MAX_DISTANCE:
            continue

        retrieved_documents.append({
            "text": document,
            "page": metadata.get("page"),
            "source": metadata.get("source"),
            "distance": distance,
        })

    return retrieved_documents
