# Legal Compass — AI-Powered Indian Law Assistant ⚖️

**Developer:** Kunal Kushwaha | B.Tech AI/ML, PSIT Kanpur  
**GitHub:** [github.com/KunalKushwaha1806/Legal-Compass](https://github.com/KunalKushwaha1806/Legal-Compass)

---

## 🏛️ Project Overview

**Legal Compass** is an AI-powered legal assistant chatbot designed to simplify Indian legal concepts for non-expert citizens. It provides authoritative, context-aware answers across:

- ⚖️ **Constitution of India:** Complete coverage of **Articles 1 to 395** (Fundamental Rights, DPSPs, Fundamental Duties, Union/State Executives, Parliament, Supreme Court, High Courts, Emergency Provisions, Amendments, Special Provisions).
- 🔴 **Indian Penal Code (IPC):** **Sections 1 to 511** (Murder, Culpable Homicide, Rape, Theft, Cheating, Forgery, Extortion, Criminal Intimidation, Dowry Cruelty, etc.).
- 🔵 **Code of Criminal Procedure (CrPC):** **Sections 1 to 484** (FIR, Arrest, Custody, Default Bail, Anticipatory Bail, Charge Sheet, Section 144, Section 125 Maintenance, Inherent High Court Powers).
- 📜 **New Criminal Laws (2023):** Full integration for **Bharatiya Nyaya Sanhita (BNS)**, **Bharatiya Nagarik Suraksha Sanhita (BNSS)**, and **Bharatiya Sakshya Adhiniyam (BSA)**.

Built completely from scratch without third-party bot builders. Features a **decoupled microservices architecture** pairing a Node.js/Express backend with dual database support (Neon.tech PostgreSQL + automatic local SQLite fallback), a modern React (Vite) glassmorphic frontend, and a Python NLP/RAG engine.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────────┐
                                  │    React (Vite) Frontend      │
                                  │   Port 5173 / Vercel Deploy   │
                                  └───────────────┬───────────────┘
                                                  │ JWT Auth & API Requests
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    Node.js Express Backend    │
                                  │   Port 3001 / Railway Deploy  │
                                  └───────┬───────────────┬───────┘
                                          │               │
                      PostgreSQL / SQLite │               │  RAG / NLP Proxy
                     ┌────────────────────┘               └────────────────────┐
                     ▼                                                         ▼
    ┌──────────────────────────────────┐                      ┌──────────────────────────────────┐
    │  Users & Persistent Chat Logs    │                      │      Python AI Engine Layer      │
    │  (Neon PostgreSQL / SQLite DB)   │                      │  (FastAPI / Colab GPU / Local)   │
    └──────────────────────────────────┘                      └──────────────────────────────────┘
                                                                               │
                                                                               ▼
                                                              ┌──────────────────────────────────┐
                                                              │ Full 395 Articles + IPC/CrPC KB  │
                                                              │ + Fine-Tuned Flan-T5 + FAISS DB  │
                                                              └──────────────────────────────────┘
```

---

## ✨ Key Features & Technical Highlights

1. **Comprehensive Legal Mapping:** Covers all 395 Articles of the Constitution of India, 511 IPC Sections, 484 CrPC Sections, and BNS 2023.
2. **Zero False-Positive Engine:** Employs strict regex word boundary matching (`\bARTICLE 5\b`) ensuring `Article 5` matches citizenship, NOT `51A` or `503`.
3. **Dual Database Persistence:** Seamlessly uses **Neon.tech Cloud PostgreSQL** in production with an automatic fallback to local **SQLite (`legal_compass_node.db`)** for zero-config offline dev.
4. **Dual Engine Intelligence:** Automatically proxies questions to a fine-tuned `google/flan-t5-base` FastAPI model on GPU (via Colab + ngrok) when configured, or executes the local Python NLP engine offline.
5. **Modern Glassmorphic Frontend:** Built with React 18 & Vite, featuring live AI status indicators, Markdown rendering via `marked.js`, cited legal sources, response timings, paginated history sidebar, and quick-start prompt chips.
6. **Automated Test Suite (`test_suite.py`):** Includes a 40-query test suite covering upper/lower boundary conditions, out-of-bound checks (`Article 0`, `Article 396`), alpha suffixes (`21A`, `498A`), short forms (`art 21`), and natural language queries (**100% pass rate**).

---

## 📁 Repository Structure

```
Legal-Compass/
├── nlp_engine.py             ← Main Python NLP Engine & TF-IDF retriever
├── legal_full_corpus.py      ← Comprehensive statutory map (Articles 1-395, IPC 1-511, CrPC 1-484, BNS 2023)
├── test_suite.py             ← Automated 40-query boundary & edge-case test suite
├── app.py                    ← Standalone Python Flask server
├── data/
│   ├── raw/legal_corpus.json
│   ├── processed/train.json, val.json, test.json, all_qa_pairs.csv
│   └── vector_store/legal.index, corpus.pkl
├── model/
│   ├── saved_model/          ← Fine-tuned Flan-T5 model weights & tokenizer
│   └── finetune.py
├── backend_node/             ← Express.js Backend
│   ├── server.js             ← Express app entry point
│   ├── db/index.js           ← Dual DB connector (PostgreSQL + SQLite fallback)
│   ├── middleware/auth.js    ← JWT authentication middleware
│   ├── models/schema.sql     ← Database table schemas
│   └── routes/
│       ├── auth.js           ← Register, login, & user profile endpoints
│       └── chat.js           ← Chat proxy & local NLP engine fallback
└── frontend/                 ← React (Vite) Frontend
    ├── src/
    │   ├── context/AuthContext.jsx ← JWT session context
    │   ├── services/api.js        ← Axios client with auth interceptors
    │   ├── components/            ← Navbar, Sidebar, ChatBubble
    │   └── pages/                 ← Chat, Login, Register
    ├── index.html
    └── vite.config.js
```

---

## ⚡ Quick Start & Local Execution

### 1. Start the Node.js Express Backend
```bash
cd backend_node

# Copy environment template
copy .env.example .env

# Start dev server (uses local SQLite automatically if no PG URL is set)
cmd /c npm run dev
# Running at http://localhost:3001
```

### 2. Start the React Frontend
```bash
cd frontend

# Install dependencies & start Vite dev server
cmd /c npm run dev
# Running at http://localhost:5173
```

---

## 🧪 Running the Test Suite

Run the automated boundary and edge-case test suite to verify all statutory mappings and input variations:

```bash
python test_suite.py
```

**Test Results:** `40/40 PASSED (100.0%)`

---

## 🌐 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | Public | Register new user with bcrypt password hashing |
| `POST` | `/api/auth/login` | Public | Authenticate user & return 7-day JWT token |
| `GET` | `/api/auth/me` | Bearer JWT | Retrieve current authenticated user profile |
| `POST` | `/api/chat` | Bearer JWT | Process legal question (FastAPI proxy / Local NLP engine) & save history |
| `GET` | `/api/chat/history` | Bearer JWT | Retrieve paginated chat history for logged-in user |
| `DELETE` | `/api/chat/:id` | Bearer JWT | Delete specific chat entry |
| `GET` | `/health` | Public | Service health & Python API connectivity status |

---

## 🚀 Production Deployment (Phase 6)

- **Frontend:** Deploy `frontend/` to **Vercel** or **Netlify** (`npm run build`).
- **Node Backend:** Deploy `backend_node/` to **Railway** or **Render** (set `DATABASE_URL`, `JWT_SECRET`, `PYTHON_API_URL`).
- **Python RAG Server:** Run on **Hugging Face Spaces (GPU)** or **Google Colab** + `ngrok`.

---

> ⚠️ **Disclaimer:** Legal Compass is designed for informational and educational purposes only. It does not constitute formal legal advice. For serious legal matters, consult a registered advocate or contact **NALSA** (National Legal Services Authority) at `nalsa.gov.in` for free legal aid under Article 39A of the Indian Constitution.
