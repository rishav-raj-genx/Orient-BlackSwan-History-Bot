# Orient BlackSwan History Bot RAG System

A local Streamlit application for querying the Orient BlackSwan History
2024–25 catalogue through a strictly grounded retrieval-augmented generation
(RAG) pipeline.

## Web Application Architecture

The application separates the web interface from document retrieval and answer
generation:

1. `app.py` renders the Streamlit interface and passes the user's question,
   unchanged, to `ask_question`.
2. `src/ingest.py` loads `data/History_2024-25.pdf` with LangChain's
   `PyPDFLoader`, splits its pages into overlapping chunks, and embeds them with
   Hugging Face's `all-MiniLM-L6-v2` model.
3. ChromaDB persists the embeddings in the local `chroma_db/` directory.
4. `src/rag_pipeline.py` retrieves the four most relevant chunks for each
   question and sends that context to Gemini through a LangChain retrieval
   chain.
5. The generated answer returns to the Streamlit UI in a highlighted result
   box.

The system prompt remains the final grounding boundary. It requires Gemini to
answer only from retrieved catalogue content, provide an exact page, title, or
section reference, and return exactly `Not found` when evidence is absent or a
question is subjective. It explicitly prohibits guessing, inference, and
outside knowledge.

## Project Structure

```text
.
├── app.py                    # Streamlit web interface
├── data/
│   └── History_2024-25.pdf   # Source catalogue
├── main.py                   # Terminal evaluation utility
├── requirements.txt          # Python dependencies
└── src/
    ├── ingest.py             # PDF ingestion and ChromaDB persistence
    └── rag_pipeline.py       # Retrieval, grounding prompt, and Gemini calls
```

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) for Python environment and dependency
  management
- A valid Google Gemini API key
- `data/History_2024-25.pdf`
- Internet access for dependency installation, the initial embedding-model
  download, and Gemini requests

## Setup Instructions

Run these commands from the repository root:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Create a `.env` file containing the Gemini API key:

```dotenv
GOOGLE_API_KEY=your_gemini_api_key
```

Build the local ChromaDB vector store:

```bash
uv run python src/ingest.py
```

Launch the web application:

```bash
streamlit run app.py
```

Open the local URL displayed by Streamlit, normally
`http://localhost:8501`. The ingestion command must complete before questions
are submitted through the UI.

## Evaluation

For each required assignment question, enter the text exactly as shown in the
web interface and select **Search Catalogue**.

### Question 1

**Question:** On what date were the prices in this catalogue last updated?

Type this question into the UI and select **Search Catalogue**.

**Expected grounded answer:** 20-01-2025, with a catalogue page reference.

![UI Q1 Answer](./images/ui_q1.png)

### Question 2

**Question:** In which year was the publisher (Orient BlackSwan) incorporated?

Type this question into the UI and select **Search Catalogue**.

**Expected grounded answer:** 1948, with a catalogue page reference.

![UI Q2 Answer](./images/ui_q2.png)

### Question 3

**Question:** What is the price of a Physics textbook?

Type this question into the UI and select **Search Catalogue**.

**Expected grounded answer:** `Not found`

![UI Q3 Answer](./images/ui_q3.png)

### Question 4

**Question:** Who is the current Minister of Education?

Type this question into the UI and select **Search Catalogue**.

**Expected grounded answer:** `Not found`

![UI Q4 Answer](./images/ui_q4.png)

### Question 5

**Question:** Which is the "best" history book for a beginner?

Type this question into the UI and select **Search Catalogue**.

**Expected grounded answer:** `Not found`

![UI Q5 Answer](./images/ui_q5.png)
