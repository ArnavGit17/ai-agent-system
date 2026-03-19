# 🚀 Autonomous Multi-Agent AI System

> A production-grade AI system that simulates how modern AI applications think — using multiple specialized agents for planning, research, reasoning, and self-evaluation.

---

## 🧠 Overview

This project implements a **multi-agent architecture** where different AI agents collaborate to solve complex queries:

* 🧠 **Planner** → Breaks down the problem into steps
* 🔎 **Researcher** → Retrieves relevant information (RAG)
* 🤖 **Reasoner** → Generates structured answers
* 📊 **Critic** → Evaluates and scores the output

---

## 🏗️ Architecture

```
User Query
   ↓
Planner → Researcher → Reasoner → Critic
   ↓
Final Answer + Evaluation
```

---

## ⚙️ Features

* ✅ Multi-agent orchestration pipeline
* ✅ Retrieval-Augmented Generation (RAG)
* ✅ FAISS vector database for semantic search
* ✅ HuggingFace embeddings (MiniLM)
* ✅ LLM integration (Google Gemini API)
* ✅ FastAPI backend with OpenAPI docs
* ✅ React frontend (Vite)
* ✅ Modular & extensible design

---

## 🛠️ Tech Stack

**Backend**

* Python (FastAPI)
* FAISS (Vector DB)
* Sentence Transformers
* Pydantic

**AI / ML**

* Gemini API (LLM)
* Embeddings (MiniLM)

**Frontend**

* React + Vite

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-agent-system.git
cd ai-agent-system
```

---

### 2. Setup Backend

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

### 3. Setup Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

### 4. Run Backend

```bash
python main.py
```

Open:
👉 http://localhost:8000/docs

---

### 5. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:
👉 http://localhost:5173

---

## 🧪 Example Queries

Try these in `/docs` or UI:

* “Explain RAG vs fine-tuning with examples”
* “Compare FAISS and Pinecone in production systems”
* “Design a scalable AI system architecture”

---

## 📊 What Makes This Project Stand Out

* 🔥 Real-world **multi-agent system design**
* 🔥 Combines **LLMs + RAG + evaluation loop**
* 🔥 Demonstrates **end-to-end AI system engineering**
* 🔥 Clean modular architecture (easy to extend)

---

## 🔐 Environment Variables

Refer to `.env.example`:

```env
GEMINI_API_KEY=your_api_key_here
SERPAPI_KEY=optional_key
```

---

## ⚠️ Notes

* Requires API key for full functionality
* Works in mock mode without external APIs
* Designed for learning + production extension

---

## 🚀 Future Improvements

* [ ] Memory module (long-term context)
* [ ] Better retrieval (reranking models)
* [ ] Real-time web search integration
* [ ] Deployment (Docker + Cloud)
* [ ] Agent communication optimization

---

## 💼 Resume Value

This project demonstrates:

* System design for AI applications
* Multi-agent orchestration
* LLM + RAG integration
* Backend + frontend development

---

## 🤝 Contributing

Feel free to fork and improve the system.

---

## ⭐ Show your support

If you like this project, give it a ⭐ on GitHub!

