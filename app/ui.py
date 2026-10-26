
import hashlib
import os
import tempfile

import streamlit as st

from app.rag.indexer import index_pdf
from app.rag.pipeline import ask_question_with_sources

st.set_page_config(
    page_title="Research PDF Assistant",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Research PDF Assistant")
st.caption("Upload a PDF and ask questions about its contents.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_source_id" not in st.session_state:
    st.session_state.indexed_source_id = None

if "indexed_filename" not in st.session_state:
    st.session_state.indexed_filename = None

with st.sidebar:
    st.header("Upload your document")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        source_id = hashlib.sha256(file_bytes).hexdigest()

        if st.button("Process PDF", type="primary"):
            with st.spinner("Indexing your PDF..."):
                temp_path = None

                try:
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:
                        temp_file.write(file_bytes)
                        temp_path = temp_file.name

                    index_pdf(
                        pdf_path=temp_path,
                        source_id=source_id,
                        source_name=uploaded_file.name
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

    if st.session_state.indexed_filename:
        st.caption(
            f"Active document: {st.session_state.indexed_filename}"
        )

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.indexed_source_id is None:
    st.info("Upload a PDF and click Process PDF to begin.")

question = st.chat_input(
    "Ask a question about your PDF...",
    disabled=st.session_state.indexed_source_id is None
)


if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching your PDF and generating an answer..."):
            try:
                result = ask_question_with_sources(
                    question,
                    source_id=st.session_state.indexed_source_id
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

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as error:
                st.error(f"Something went wrong: {error}")
