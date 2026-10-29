from app.rag.loader import load_pdf
from app.rag.cleaner import clean_text
from app.rag.chunker_v2 import chunk_pages
from app.rag.embeddings import embed_text
from app.rag.vector_store import add_document


def index_pdf(
    pdf_path: str,
    source_id: str | None = None,
    source_name: str | None = None,
):
    print("Loading PDF...")

    pages = load_pdf(pdf_path)
    print(f"Loaded {len(pages)} pages.")

    for page in pages:
        page["text"] = clean_text(page["text"])

    chunks = chunk_pages(pages)
    print(f"Created {len(chunks)} chunks.")

    document_source_id = source_id or pdf_path

    for i, chunk in enumerate(chunks, start=1):
        embedding = embed_text(chunk["text"])

        unique_chunk_id = (
            f"{document_source_id}_{chunk['chunk_id']}"
        )

        metadata = {
            "source": source_name or pdf_path,
            "source_id": document_source_id,
            "page": chunk["page"],
            "chunk_id": chunk["chunk_id"],
        }

        add_document(
            chunk_id=unique_chunk_id,
            text=chunk["text"],
            embedding=embedding,
            metadata=metadata,
        )

        print(f"Indexed chunk {i}/{len(chunks)}")

    print("Indexing complete!")
