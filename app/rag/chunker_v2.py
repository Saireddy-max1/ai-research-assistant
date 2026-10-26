def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200
) -> list[dict]:

    chunks = []

    for page in pages:

        page_number = page["page"]
        text = page["text"]

        start = 0
        chunk_number = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": f"page-{page_number}-chunk-{chunk_number}",
                "page": page_number,
                "text": chunk_text
            })

            chunk_number += 1

            start = end - overlap

    return chunks