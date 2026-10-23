# Orient BlackSwan History Bot RAG System

A retrieval-augmented generation (RAG) system that answers questions from the
Orient BlackSwan history catalogue while refusing unsupported or subjective
answers.

## System Flow

`src/ingest.py` loads `data/History_2024-25.pdf` with LangChain's
`PyPDFLoader`, splits the extracted pages into overlapping text chunks, and
embeds them with Hugging Face's `all-MiniLM-L6-v2` model. ChromaDB persists
those embeddings in `chroma_db/`.

For each question, `src/rag_pipeline.py` retrieves the four most relevant
chunks from ChromaDB and sends them to Gemini through a LangChain retrieval
chain. Its strict grounding prompt requires the model to:

- answer only from the retrieved catalogue context;
- cite the relevant page, title, or section;
- return exactly `Not found` when the required evidence is absent or the
  question asks for an unsupported opinion; and
- avoid guessing, inference, and outside knowledge.

`main.py` initializes this pipeline and runs the five assignment questions.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) for Python environment and dependency
  management
- A Google Gemini API key
- `data/History_2024-25.pdf`
- Internet access for dependency installation, the first embedding-model
  download, and Gemini requests

## Setup and Run

Run the following commands from the repository root:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Create a `.env` file containing your Gemini API key:

```dotenv
GOOGLE_API_KEY=your_gemini_api_key
```

Build the local ChromaDB vector store:

```bash
uv run python src/ingest.py
```

Run the five-question evaluation:

```bash
uv run python main.py
```

The ingestion step must run before the evaluation so that `chroma_db/` exists.

## Evaluation

### Question 1

**Question:** On what date were the prices in this catalogue last updated?

**Answer:** 20-01-2025 (source: *History_2024-25*, printed catalogue page 1).

![Terminal Output Q1](./images/q1_terminal.png)

### Question 2

**Question:** In which year was the publisher (Orient BlackSwan) incorporated?

**Answer:** 1948 (source: *History_2024-25*, printed catalogue page 1).

![Terminal Output Q2](./images/q2_terminal.png)

### Question 3

**Question:** What is the price of a Physics textbook?

**Answer:** Not found

![Terminal Output Q3](./images/q3_terminal.png)

### Question 4

**Question:** Who is the current Minister of Education?

**Answer:** Not found

![Terminal Output Q4](./images/q4_terminal.png)

### Question 5

**Question:** Which is the "best" history book for a beginner?

**Answer:** Not found

![Terminal Output Q5](./images/q5_terminal.png)
