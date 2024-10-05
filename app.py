import streamlit as st
import tempfile
import os
from llm import load_and_process_pdf, create_vectorstore, create_rag_chain, get_response

st.set_page_config(page_title="PDF Q&A Chatbot", page_icon="📚")
st.title("PDF Q&A Chatbot")

# Initialize session state for vector store and chain
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'rag_chain' not in st.session_state:
    st.session_state.rag_chain = None

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

# Process the PDFs when uploaded and no vectorstore exists
if uploaded_files and st.session_state.vectorstore is None:
    combined_splits = []

    # Save the uploaded files temporarily and process them
    def save_temp_file(uploaded_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name

    with st.spinner("Processing PDFs..."):
        for uploaded_file in uploaded_files:
            tmp_file_path = save_temp_file(uploaded_file)
            splits = load_and_process_pdf(tmp_file_path)
            combined_splits += splits  # Combine splits from all PDFs
            os.unlink(tmp_file_path)  # Clean up temporary file

        st.session_state.vectorstore = create_vectorstore(combined_splits)
        st.session_state.rag_chain = create_rag_chain()

    st.success("PDFs processed successfully! Now you can ask questions.")

# Question input
if st.session_state.vectorstore is not None:
    question = st.text_input("Ask a question about the PDFs:")

    if question:
        with st.spinner("Generating answer..."):
            answer = get_response(st.session_state.rag_chain, st.session_state.vectorstore, question)
        st.write("Answer:", answer)
else:
    st.info("Please upload one or more PDF files to get started.")
