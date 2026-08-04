# Legal Compass — System Architecture & Technical Documentation 🏛️

**Developer:** Kunal Kushwaha | B.Tech AI/ML, PSIT Kanpur  
**Repository:** [github.com/KunalKushwaha1806/Legal-Compass](https://github.com/KunalKushwaha1806/Legal-Compass)  
**Version:** 2.0 (Full Statutory Corpus & Dual-Engine Fallback Edition)

---

## 📑 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [End-to-End Execution Sequence](#3-end-to-end-execution-sequence)
4. [Component Deep-Dive](#4-component-deep-dive)
   - [4.1 Frontend Layer (React + Vite)](#41-frontend-layer-react--vite)
   - [4.2 Backend Gateway (Node.js + Express)](#42-backend-gateway-nodejs--express)
   - [4.3 Database Abstraction Layer (PostgreSQL + SQLite)](#43-database-abstraction-layer-postgresql--sqlite)
   - [4.4 Dual AI & NLP Inference Engine](#44-dual-ai--nlp-inference-engine)
5. [Statutory Routing & Precision Matching](#5-statutory-routing--precision-matching)
6. [Data Schemas & ER Model](#6-data-schemas--er-model)
7. [Fault Tolerance & Offline Mechanics](#7-fault-tolerance--offline-mechanics)
8. [Automated Verification & Test Suite](#8-automated-verification--test-suite)

---

## 1. Executive Summary

**Legal Compass** is a production-grade, decoupled AI legal assistant built from scratch without third-party chatbot frameworks (e.g., Botpress). It is specifically engineered to answer complex legal questions regarding the **Constitution of India (Articles 1–395)**, **Indian Penal Code (IPC 1–511)**, **Code of Criminal Procedure (CrPC 1–484)**, and **Bharatiya Nyaya Sanhita (BNS 2023)**.

The system uses a **microservices-based multi-tier architecture** with built-in redundancy at both the database level (Neon PostgreSQL with SQLite fallback) and the AI engine level (Google Colab GPU FastAPI with local Python NLP fallback).

---

## 2. System Architecture Overview

```
                                  ┌───────────────────────────────┐
                                  │   React 18 (Vite) Frontend    │
                                  │   Glassmorphic UI / Port 5173 │
                                  └───────────────┬───────────────┘
                                                  │
                                                  │ HTTPS / REST API + JWT Bearer
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │   Node.js + Express Server    │
                                  │    API Gateway / Port 3001    │
                                  └───────┬───────────────┬───────┘
                                          │               │
                     PostgreSQL / SQLite  │               │ HTTP Proxy / Subprocess
                    ┌─────────────────────┘               └────────────────────┐
                    ▼                                                          ▼
   ┌──────────────────────────────────┐                       ┌──────────────────────────────────┐
   │    Dual-Mode Database Layer      │                       │     Dual AI Inference Layer      │
   │  - Neon.tech PostgreSQL (Cloud)  │                       │  Mode A: FastAPI (Colab GPU)     │
   │  - SQLite (Local Fallback DB)    │                       │  Mode B: Local Python NLP Engine │
   └──────────────────────────────────┘                       └──────────────────────────────────┘
                                                                               │
                                                                               ▼
                                                              ┌──────────────────────────────────┐
                                                              │ Full 395 Articles + IPC/CrPC KB  │
                                                              │  FAISS Vector Index + Flan-T5    │
                                                              └──────────────────────────────────┘
```

---

## 3. End-to-End Execution Sequence

The diagram below traces the exact flow of data when a user types a legal question (e.g., *"What is Article 21?"* or *"What is the punishment for murder under IPC 302?"*):

```
User (Browser)          React Frontend            Node.js Backend           Python NLP Engine           Database
     │                        │                          │                          │                      │
     │── 1. Types Query ─────>│                          │                          │                      │
     │                        │── 2. POST /api/chat ────>│                          │                      │
     │                        │   (with JWT Token)       │                          │                      │
     │                        │                          │── 3. Verify JWT Token ──>│                      │
     │                        │                          │                          │                      │
     │                        │                          │── 4. Dispatch Query ────>│                      │
     │                        │                          │    (Try Colab / Local)   │                      │
     │                        │                          │                          │── 5. Statutory Match │
     │                        │                          │                          │   (Regex Boundaries) │
     │                        │                          │                          │                      │
     │                        │                          │                          │── 6. TF-IDF Fallback │
     │                        │                          │                          │   (If NL Question)   │
     │                        │                          │                          │                      │
     │                        │                          │<── 7. Answer Payload ────│                      │
     │                        │                          │    (JSON + Sources)      │                      │
     │                        │                          │                                                 │
     │                        │                          │── 8. Persist History ───────────────────────────>│
     │                        │                          │                                                 │
     │<── 9. Render Markdown ─│<── 10. HTTP 200 OK ───────│                                                 │
     │    Bubble + Sources    │    Payload               │                                                 │
```

---

## 4. Component Deep-Dive

### 4.1 Frontend Layer (React + Vite)
- **Framework:** React 18 initialized via Vite.
- **Styling:** Custom CSS with Glassmorphism, CSS variable design tokens, custom scrollbars, dark themes, responsive layout.
- **State Management:** `AuthContext.jsx` provides global user authentication state, persistent JWT session storage in `localStorage`, and login/logout handlers.
- **HTTP Client:** Axios instance in `services/api.js` configured with request interceptors to append `Authorization: Bearer <token>` headers automatically.
- **Markdown & UI Rendering:** `marked.js` parses raw legal markdown into rich HTML; custom CSS highlights legal sources, warnings, and citations.

### 4.2 Backend Gateway (Node.js + Express)
- **Framework:** Express.js running on Port 3001.
- **Authentication:** `jsonwebtoken` generates signed 7-day tokens; `bcryptjs` hashes passwords with 10 salt rounds.
- **Routes:**
  - `POST /api/auth/register`: Creates new user account.
  - `POST /api/auth/login`: Validates credentials & returns JWT.
  - `GET /api/auth/me`: Retrieves logged-in profile.
  - `POST /api/chat`: Dual-engine chat gateway & history logger.
  - `GET /api/chat/history`: Retrieves user history.
  - `DELETE /api/chat/:id`: Deletes chat history entry.

### 4.3 Database Abstraction Layer (PostgreSQL + SQLite)
`backend_node/db/index.js` implements a **fail-safe database abstraction**:
1. Checks for environment variable `DATABASE_URL` (Neon.tech PostgreSQL).
2. If `DATABASE_URL` is set, connects via `pg.Pool`.
3. If PostgreSQL fails or `DATABASE_URL` is missing, **automatically initializes local SQLite database (`legal_compass_node.db`)** using `better-sqlite3`.
4. Exposes unified query helper `query(text, params)` so all controller logic remains 100% database-agnostic.

### 4.4 Dual AI & NLP Inference Engine
- **Mode A (GPU Server - RAG Pipeline):**
  - Fine-tuned `google/flan-t5-base` trained on Indian Legal Q&A data.
  - FAISS Vector DB indexed with `sentence-transformers/all-MiniLM-L6-v2` embeddings.
  - Runs on Google Colab GPU via FastAPI exposed through `ngrok`.
- **Mode B (Local Precision NLP Engine - `nlp_engine.py` + `legal_full_corpus.py`):**
  - High-speed Python module executing locally.
  - Regex-isolated Statutory Router for Articles 1–395, IPC 1–511, CrPC 1–484, and BNS 2023.
  - Scikit-learn TF-IDF Vectorizer + Cosine Similarity fallback for unstructured natural language questions.

---

## 5. Statutory Routing & Precision Matching

To eliminate false-positive substring matching (e.g., `Article 5` matching `Article 51A` or `Section 503`), `legal_full_corpus.py` executes a **4-step strict priority routing pipeline**:

```python
def lookup_specific_provision(query: str) -> Optional[Dict[str, Any]]:
    # STEP 1: New Criminal Laws Check (BNS, BNSS, BSA 2023)
    # Check BNSS before BNS to prevent substring collision

    # STEP 2: CrPC Section Check (Sections 1 to 484)
    # Validates section ranges; returns custom out-of-bounds if > 484

    # STEP 3: IPC Section Check (Sections 1 to 511)
    # Ignores 4-digit years (1860, 1973, 2023); returns out-of-bounds if > 511

    # STEP 4: Constitution Article Check (Articles 1 to 395)
    # Maps all 395 Articles across Parts I to XXII; returns out-of-bounds if > 395
```

---

## 6. Data Schemas & ER Model

```
 ┌──────────────────────────────────┐        1 : N        ┌──────────────────────────────────┐
 │              users               │────────────────────>│           chat_history           │
 ├──────────────────────────────────┤                     ├──────────────────────────────────┤
 │ id             UUID / INTEGER PK │                     │ id             UUID / INTEGER PK │
 │ name           VARCHAR(100)      │                     │ user_id        FK -> users(id)   │
 │ email          VARCHAR(255) UNI  │                     │ question       TEXT              │
 │ password_hash  VARCHAR(255)      │                     │ answer         TEXT              │
 │ created_at     TIMESTAMP         │                     │ category       VARCHAR(50)       │
 └──────────────────────────────────┘                     │ confidence     FLOAT             │
                                                          │ sources        TEXT / JSON       │
                                                          │ created_at     TIMESTAMP         │
                                                          └──────────────────────────────────┘
```

---

## 7. Fault Tolerance & Offline Mechanics

| Component Failure | Secondary Fallback Mechanism | Impact on User |
|-------------------|------------------------------|----------------|
| **Neon PostgreSQL Cloud DB down** | Automatic fallback to local SQLite (`legal_compass_node.db`) | Zero downtime; local storage enabled |
| **Colab GPU / ngrok offline** | Node backend routes to `queryLocalEngine` (`nlp_engine.py`) | Immediate responses; offline retrieval active |
| **No Internet Connection** | Entire stack (React + Node + SQLite + Python Engine) runs on `localhost` | Full offline functionality |

---

## 8. Automated Verification & Test Suite

The system includes a 40-query test suite (`test_suite.py`) verifying all boundary conditions:

```bash
python test_suite.py
```

### Verified Test Categories:
1. **Constitutional Boundaries:** `Article 1` (lower bound), `Article 395` (upper bound), `Article 0` & `Article 396` (out-of-bounds guards), `Article 21A`, `Article 300A` (alpha suffixes).
2. **IPC Boundaries:** `IPC 1` (lower bound), `IPC 511` (upper bound), `IPC 512` (out-of-bounds guard), `Section 498A`, `Section 120B`.
3. **CrPC Boundaries:** `CrPC 1`, `CrPC 484`, `CrPC 41`, `CrPC 144`, `CrPC 438`, `CrPC 482`.
4. **Formatting & Short Forms:** `ARTICLE 21` (uppercase), `  article   21  ` (spaces), `art 21`, `sec 302`, `ipc 302`, `crpc 438`, `what is art. 21???` (punctuation).
5. **New Laws & Situational Queries:** `BNS 2023`, `BNSS 2023`, `BSA 2023`, *"How do I file an FIR?"*, *"What is anticipatory bail?"*.

**Final Status:** `40/40 PASSED (100.0%)`

---

## 9. Environment Variables & Configuration Matrix

Legal Compass requires zero mandatory environment configuration to run locally because of its automatic fallbacks. However, for production deployment, the following environment variables control server behavior:

| Variable | Scope | Required? | Default Fallback | Purpose / Description |
|----------|-------|-----------|------------------|───────────────────────|
| `PORT` | Backend (`.env`) | Optional | `3001` | Express server listener port |
| `NODE_ENV` | Backend (`.env`) | Optional | `development` | Runtime environment mode |
| `DATABASE_URL` | Backend (`.env`) | Optional | Local SQLite (`legal_compass_node.db`) | Neon.tech PostgreSQL connection string |
| `JWT_SECRET` | Backend (`.env`) | Recommended | Development secret key | HMAC SHA-256 signing secret for JWT tokens |
| `PYTHON_API_URL` | Backend (`.env`) | Optional | Local Python NLP Engine (`nlp_engine.py`) | ngrok URL for Google Colab GPU FastAPI server |
| `FRONTEND_URL` | Backend (`.env`) | Optional | `http://localhost:5173` | Allowed CORS origin header for browser requests |
| `VITE_API_BASE_URL` | Frontend | Optional | `http://localhost:3001/api` | Base API endpoint URL for Axios client |

> 🔒 **Security Best Practice:** Never commit `.env` files with actual production secrets to GitHub. Always use `.env.example` as a template in open-source repositories.

