
import hashlib
import os
import tempfile
import uuid

import streamlit as st

from app.rag.indexer import index_pdf
from app.rag.pipeline import ask_question_with_sources
from app.rag.vector_store import delete_source_documents


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Research PDF Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("📚 Research PDF Assistant")
st.caption("Upload a PDF and ask questions about its contents.")


# --------------------------------------------------
# Initialize session state
# --------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex

if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_source_id" not in st.session_state:
    st.session_state.indexed_source_id = None

if "indexed_filename" not in st.session_state:
    st.session_state.indexed_filename = None


# --------------------------------------------------
# Sidebar: PDF upload and document management
# --------------------------------------------------

with st.sidebar:
    st.header("Upload your document")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()

        # Give this browser session its own document ID.
        source_id = hashlib.sha256(
            f"{st.session_state.session_id}:{file_hash}".encode()
        ).hexdigest()

        if st.button("Process PDF", type="primary", use_container_width=True):
            temp_path = None

            try:
                with st.spinner("Processing your PDF..."):
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf",
                    ) as temp_file:
                        temp_file.write(file_bytes)
                        temp_path = temp_file.name

                    # Remove the previous document's chunks when replacing it.
                    previous_source_id = (
                        st.session_state.indexed_source_id
                    )

                    if previous_source_id:
                        delete_source_documents(previous_source_id)

                    index_pdf(
                        pdf_path=temp_path,
                        source_id=source_id,
                        source_name=uploaded_file.name,
                    )

                    st.session_state.indexed_source_id = source_id
                    st.session_state.indexed_filename = uploaded_file.name
                    st.session_state.messages = []

                st.success("PDF processed successfully!")

            except Exception as error:
                st.error(f"Could not process PDF: {error}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    # Show the active document.
    if st.session_state.indexed_filename:
        st.caption(
            f"Active document: {st.session_state.indexed_filename}"
        )

    st.divider()

    # Clear chat history without removing the indexed PDF.
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Remove the active document and its indexed chunks.
    if st.button("Remove document", use_container_width=True):
        source_id = st.session_state.indexed_source_id

        try:
            if source_id:
                delete_source_documents(source_id)

            st.session_state.indexed_source_id = None
            st.session_state.indexed_filename = None
            st.session_state.messages = []

            st.success("Document removed successfully!")
            st.rerun()

        except Exception as error:
            st.error(f"Could not remove document: {error}")


# --------------------------------------------------
# Display previous conversation
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show citations again when displaying previous answers.
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(
                        f"- **{source['filename']}** "
                        f"— Page {source['page']}"
                    )


# --------------------------------------------------
# Ask questions
# --------------------------------------------------

if st.session_state.indexed_source_id is None:
    st.info("Upload a PDF and click Process PDF to begin.")

question = st.chat_input(
    "Ask a question about your PDF...",
    disabled=st.session_state.indexed_source_id is None,
)

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your PDF and generating an answer..."):
            try:
                result = ask_question_with_sources(
                    question,
                    source_id=st.session_state.indexed_source_id,
                )

                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.markdown(
                                f"- **{source['filename']}** "
                                f"— Page {source['page']}"
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as error:
                st.error(f"Something went wrong: {error}")
