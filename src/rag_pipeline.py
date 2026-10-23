import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Ensure compatibility across LangChain versions for langchain.chains imports
try:
    import langchain.chains  # noqa: F401
except (ImportError, ModuleNotFoundError):
    try:
        import langchain_classic.chains as _chains
        import langchain_classic.chains.combine_documents as _combine_docs
        import langchain_classic.chains.retrieval as _retrieval

        sys.modules["langchain.chains"] = _chains
        sys.modules["langchain.chains.combine_documents"] = _combine_docs
        sys.modules["langchain.chains.retrieval"] = _retrieval
    except (ImportError, ModuleNotFoundError):
        pass

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
CHROMA_DIR: Path = PROJECT_ROOT / "chroma_db"
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
MODEL_NAME: str = "gemini-3.5-flash-lite"

SYSTEM_PROMPT: str = (
    "You are a strict, precise assistant tasked with answering questions based ONLY on the provided context document. Your instructions are absolute:\n"
    "1. If the answer is present in the context, answer the question and explicitly state the reference (e.g., page number, book title, or section) where the answer was found.\n"
    "2. If the context does not contain the exact information needed to answer the question, or if the question asks for a subjective opinion not explicitly stated as a fact in the text, you must reply with exactly two words: 'Not found'.\n"
    "3. Do not attempt to guess, infer, or use outside knowledge.\n"
    "4. Do not include introductory or concluding conversational text.\n\n"
    "Context:\n"
    "{context}"
)

_rag_chain_instance: Optional[Runnable] = None


def verify_gemini_connection() -> bool:
    """Verifies that GOOGLE_API_KEY is configured and test invokes gemini-1.5-flash."""
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key.strip() == "your_gemini_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY is not configured or contains placeholder text in '.env'."
        )

    try:
        test_llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=api_key,
            temperature=0.0,
        )
        response = test_llm.invoke("Diagnostic test: reply with 'OK'")
        if not response or not response.content:
            raise RuntimeError("Gemini diagnostic test returned an empty response.")
        print(
            f"[Diagnostic] Google Gemini API connection verified successfully using '{MODEL_NAME}'."
        )
        return True
    except Exception as exc:
        raise RuntimeError(
            f"Google Gemini API diagnostic verification failed for '{MODEL_NAME}': {exc}"
        ) from exc


def _format_answer_output(raw_answer: Any) -> str:
    if isinstance(raw_answer, str):
        return raw_answer.strip()
    if isinstance(raw_answer, list):
        extracted: List[str] = []
        for part in raw_answer:
            if isinstance(part, dict):
                extracted.append(part.get("text", ""))
            elif hasattr(part, "text"):
                extracted.append(str(part.text))
            else:
                extracted.append(str(part))
        return "".join(extracted).strip()
    return str(raw_answer).strip()


def init_rag_chain() -> Runnable:
    global _rag_chain_instance
    if _rag_chain_instance is not None:
        return _rag_chain_instance

    verify_gemini_connection()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Chroma DB directory not found at '{CHROMA_DIR}'. "
            "Run 'python src/ingest.py' first to build the vector store."
        )

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.0,
        google_api_key=api_key,
    )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    _rag_chain_instance = create_retrieval_chain(retriever, question_answer_chain)
    return _rag_chain_instance


def ask_question(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("Query string cannot be empty.")

    chain = init_rag_chain()
    response: Dict[str, Any] = chain.invoke({"input": query.strip()})
    raw_answer = _format_answer_output(response.get("answer", ""))

    # Programmatic gatekeeper: ensure exact 'Not found' whenever not found appears
    if "not found" in raw_answer.lower():
        return "Not found"

    return raw_answer


if __name__ == "__main__":
    test_query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "On what date were the prices in this catalogue last updated?"
    )
    try:
        result = ask_question(test_query)
        print(f"Question:\n{test_query}\nAnswer:\n{result}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
