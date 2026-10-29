# Hybrid AI Knowledge

An interactive Python prototype demonstrating how **deterministic knowledge routing** and **local semantic retrieval** can work together.

The central idea: not every question needs the same retrieval strategy.

## How it works

The application routes a question to one of two knowledge paths:

### 1. Deterministic OKF-Inspired Route

For questions about APIs, protocols, schemas, and rules, the system uses keyword-based routing to select structured Markdown knowledge with explicit metadata.

### 2. Semantic Retrieval Route

For conversational or exploratory questions, the system uses **TF-IDF vectors and cosine similarity** to retrieve the closest matching text from local knowledge files.

The application exposes the selected route, routing reason, source file, answer, and—when semantic retrieval is used—similarity score.

## Architecture

```text
              User question
                    |
                    v
                  Router
                 /      \
                v        v
       Structured      Semantic
        knowledge      retrieval
            |              |
     Markdown +         TF-IDF +
      metadata       cosine similarity
            |              |
            +------ Answer +
                    evidence
```

## Try the live demo

[**Open Hybrid AI Knowledge**](https://hybrid-ai-knowledge-krwft2mst7r8lv5sfcr.streamlit.app/)

## Example questions

| Question | Expected route |
|---|---|
| What is the authentication protocol? | Deterministic OKF-Inspired Route |
| What fields are in the user schema? | Deterministic OKF-Inspired Route |
| Why is the dashboard incomplete? | Semantic Retrieval Route |
| What changed after the nightly refresh? | Semantic Retrieval Route |

These examples demonstrate the intended routing behavior for the current knowledge base.

## Run locally

Requirements: Python and pip.

```bash
git clone https://github.com/harry21711/hybrid-ai-knowledge.git
cd hybrid-ai-knowledge
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS**
```bash
source .venv/bin/activate
```

Install dependencies and run the app:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
streamlit run app.py
```

Streamlit will provide a local URL, usually `http://localhost:8501`.

## Project structure

```text
.
├── app.py
├── hybrid_knowledge.py
├── okf_knowledge/
├── rag_knowledge/
├── tests/
├── screenshots/
├── requirements.txt
└── .devcontainer/
```

- `app.py` — Streamlit interface
- `hybrid_knowledge.py` — Routing and retrieval logic
- `okf_knowledge/` — Structured Markdown knowledge files
- `rag_knowledge/` — Local text used for semantic retrieval
- `tests/` — Automated tests
- `screenshots/` — Application screenshots
- `.devcontainer/` — GitHub Codespaces development configuration

## Design principle

> Use deterministic logic where explicitness and traceability matter, and semantic retrieval where discovery matters.

This is an **educational prototype**, not a production-grade RAG platform. The structured knowledge approach is inspired by the Open Knowledge Framework (OKF) concept; this repository is not an official Google OKF implementation.

The current prototype uses local files, keyword-based routing, TF-IDF, cosine similarity, Python, and Streamlit. It does not require a cloud AI API or an external vector database.
