import chromadb

DB_PATH = "./data/chroma"

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="research_documents_local"
)


def add_document(
    chunk_id: str,
    text: str,
    embedding: list[float],
    metadata: dict | None = None,
):
    collection.upsert(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata or {}],
    )


def search_documents(
    query_embedding: list[float],
    n_results: int = 3,
    source_id: str | None = None,
):
    search_options = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
    }

    if source_id:
        search_options["where"] = {"source_id": source_id}

    return collection.query(**search_options)


def delete_document(chunk_id: str):
    collection.delete(ids=[chunk_id])


def delete_source_documents(source_id: str):
    """Delete all chunks belonging to one uploaded document."""
    collection.delete(where={"source_id": source_id})

