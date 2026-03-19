# Autonomous Multi-Agent AI System

A production-grade multi-agent pipeline that decomposes complex queries into subtasks, retrieves information from documents (RAG) and the web, synthesizes answers, and self-evaluates — all orchestrated through four specialised agents.

## Architecture

```
User Query
    │
    ▼
┌────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  PLANNER   │────▶│  RESEARCHER  │────▶│   REASONER   │────▶│   CRITIC   │
│            │     │              │     │              │     │            │
│ • Rewrite  │     │ • FAISS RAG  │     │ • Synthesize │     │ • Score    │
│ • Decompose│     │ • Web search │     │ • Multi-doc  │     │ • Approve  │
│ • Assign   │     │ • Re-rank    │     │ • Cite       │     │ • Improve  │
└────────────┘     └──────────────┘     └──────────────┘     └────────────┘
```

### Agent Responsibilities

| Agent | Input | Output | LLM Calls |
|-------|-------|--------|-----------|
| **Planner** | Raw user query | Rewritten query + subtask list with tool assignments | 1 |
| **Researcher** | Subtask list | Retrieved chunks (RAG) + web snippets per subtask | 0 (tool calls only) |
| **Reasoner** | Plan + research + chat history | Markdown answer with sources and confidence | 1 |
| **Critic** | Query + plan + research + answer | Scores (relevance, accuracy, completeness) + feedback | 1 |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 2.0 Flash (free tier) |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Vector DB | FAISS (local, inner-product similarity) |
| Backend | FastAPI (async, Pydantic v2, SSE streaming) |
| Frontend | React 18 + Tailwind CSS + Vite |
| Document Processing | PyPDF + LangChain text splitters |

## Project Structure

```
ai-agent-system/
├── agents/                  # Multi-agent modules
│   ├── base.py              # Abstract base agent with timing/logging
│   ├── planner.py           # Query decomposition agent
│   ├── researcher.py        # Tool-calling research agent
│   ├── reasoner.py          # Answer synthesis agent
│   └── critic.py            # Self-evaluation agent
├── rag/
│   └── __init__.py          # FAISS engine: ingest, embed, retrieve
├── tools/
│   ├── search.py            # Web search (mock + SerpAPI)
│   └── retrieval.py         # RAG retrieval wrapper
├── models/
│   └── __init__.py          # All Pydantic schemas
├── core/
│   ├── config.py            # Settings via pydantic-settings
│   ├── llm.py               # Gemini client (sync, JSON, stream)
│   └── logging.py           # Loguru structured logging
├── api/
│   ├── app.py               # FastAPI endpoints
│   └── pipeline.py          # Orchestrator + session memory
├── frontend/                # React + Tailwind UI
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── PlanPanel.jsx
│   │   │   ├── CriticPanel.jsx
│   │   │   ├── SourcesPanel.jsx
│   │   │   ├── ScoreGauge.jsx
│   │   │   ├── AgentStatus.jsx
│   │   │   └── UploadButton.jsx
│   │   └── hooks/api.js
│   └── package.json
├── tests/
│   └── test_models.py
├── main.py                  # Entry point
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- A Google Gemini API key ([get one free](https://aistudio.google.com/apikey))

### Backend

```bash
cd ai-agent-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be at `http://localhost:5173`.

### Docker

```bash
docker build -t agent-system .
docker run -p 8000:8000 --env-file .env agent-system
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query` | Run full agent pipeline, return structured result |
| `POST` | `/query/stream` | Run pipeline + stream answer via SSE |
| `POST` | `/upload` | Upload PDF for RAG ingestion |
| `GET` | `/history` | List all chat sessions |
| `GET` | `/history/{id}` | Get messages for a session |
| `GET` | `/health` | System health + index stats |

### Example Request

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the differences between FAISS and Pinecone for vector search"}'
```

## Features

### Core
- **Multi-agent pipeline** with typed inter-agent contracts (Pydantic models)
- **RAG system**: PDF upload → chunking → embedding → FAISS retrieval → re-ranking
- **Tool usage**: Web search (mock or SerpAPI) + RAG retrieval, assigned per subtask
- **Memory**: In-memory chat sessions with context-aware responses
- **Evaluation**: Per-answer scoring on relevance, accuracy, completeness with critic feedback

### Advanced
- **Streaming responses** via Server-Sent Events
- **Multi-document reasoning** across RAG chunks and web results
- **Query rewriting** by the Planner agent for disambiguation
- **Confidence scoring** by both Reasoner (self-assessed) and Critic (external)
- **Concurrent tool execution** (RAG + web search run in parallel per subtask)

## Testing

```bash
pip install pytest
pytest tests/ -v
```

## Configuration

All configuration is via environment variables (see `.env.example`). Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Required. Your Gemini API key |
| `SEARCH_MODE` | `mock` | `mock` for development, `serpapi` for real search |
| `CHUNK_SIZE` | `512` | Text chunk size for RAG |
| `TOP_K_RESULTS` | `5` | Number of RAG results to retrieve |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model for embeddings |

## License

MIT
