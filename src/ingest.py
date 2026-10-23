import os
import shutil
import sys
from pathlib import Path
from typing import List
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH: Path = PROJECT_ROOT / "data" / "History_2024-25.pdf"
DEFAULT_CHROMA_PATH: Path = PROJECT_ROOT / "chroma_db"
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"


def load_pdf(pdf_path: Path) -> List[Document]:
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Target PDF was not found at '{pdf_path}'. "
            "Please ensure 'History_2024-25.pdf' is placed inside the 'data/' directory."
        )
    print(f"[Ingest] Loading document: {pdf_path}")
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()
    if not documents:
        raise ValueError(f"No content could be extracted from '{pdf_path}'.")
    print(f"[Ingest] Successfully extracted {len(documents)} pages from PDF.")
    return documents


def split_documents(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> List[Document]:
    print(
        f"[Ingest] Splitting documents (chunk_size={chunk_size}, chunk_overlap={chunk_overlap})..."
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise ValueError("Document splitting resulted in 0 chunks.")
    print(f"[Ingest] Successfully generated {len(chunks)} text chunks.")
    return chunks


def create_vector_store(
    chunks: List[Document],
    persist_dir: Path,
    model_name: str = EMBEDDING_MODEL_NAME,
) -> Chroma:
    persist_dir_path = str(persist_dir)
    # Safely delete existing vector database to prevent duplicate vectors
    if os.path.exists(persist_dir_path):
        print(f"[Ingest] Cleaning existing vector database directory at '{persist_dir_path}'...")
        shutil.rmtree(persist_dir_path)

    print(f"[Ingest] Initializing HuggingFace embeddings model: '{model_name}'...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    print(f"[Ingest] Writing {len(chunks)} chunks to Chroma DB at '{persist_dir}'...")
    persist_dir.mkdir(parents=True, exist_ok=True)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir_path,
    )

    # Verification of persistence
    db_files = list(persist_dir.glob("*"))
    if not db_files:
        raise RuntimeError(
            f"Chroma persistence verification failed: '{persist_dir}' is empty."
        )

    print(
        f"[Ingest] Verified: {len(chunks)} chunks stored across {len(db_files)} database artifacts in '{persist_dir}'."
    )
    return vector_store


def run_ingestion(
    pdf_path: Path = DEFAULT_DATA_PATH,
    persist_dir: Path = DEFAULT_CHROMA_PATH,
) -> Chroma:
    raw_docs = load_pdf(pdf_path)
    chunks = split_documents(raw_docs)
    vector_store = create_vector_store(chunks, persist_dir)
    return vector_store


if __name__ == "__main__":
    try:
        run_ingestion()
        print("[Ingest] Ingestion pipeline completed successfully.")
    except Exception as exc:
        print(f"[Ingest Error] Ingestion failed: {exc}", file=sys.stderr)
        sys.exit(1)
