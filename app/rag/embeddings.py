import streamlit as st
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@st.cache_resource
def get_embedding_model():
    """Load the embedding model once."""
    return SentenceTransformer(MODEL_NAME, device="cpu")


def embed_text(text: str) -> list[float]:
    """Convert one text into an embedding vector."""
    model = get_embedding_model()

    vector = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convert multiple texts into embedding vectors."""
    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return vectors.tolist()
