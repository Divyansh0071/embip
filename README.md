# EMBIP — Enterprise Multi-Agent Business Intelligence Platform

[![Phase](https://img.shields.io/badge/Phase-1%20Project%20Foundation-blue.svg)](file:///c:/Users/Divyansh%20Singh/Desktop/Buisness%20Enterprise/PROJECT_STATUS.md)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

EMBIP (Enterprise Multi-Agent Business Intelligence Platform) is an AI-powered enterprise business intelligence system that empowers decision-makers to ask natural-language analytical questions about structured business datasets and unstructured corporate documents.

---

## 1. Project Purpose & Core Capabilities

Traditional BI tools rely on static dashboards, pre-built reports, or brittle SQL generators. EMBIP introduces a stateful **multi-agent orchestration framework (LangGraph)** powered by a **Centralized LLMService** to perform multi-step business analysis:

1. **Natural-Language Understanding:** Parses complex analytical inquiries (e.g., *"Why did our profit decrease in Q2?"*).
2. **Autonomous Execution Planning:** Decomposes queries into operational analytical sub-tasks.
3. **SELECT-Only Structured SQL Queries:** Queries relational databases safely with AST-based security validation.
4. **Document Search (RAG):** Contextually searches corporate documents (PDF, DOCX, CSV, XLSX) stored in Qdrant Cloud.
5. **Numerical & Statistical Computations:** Offload complex mathematical transformations to Pandas, NumPy, and scikit-learn.
6. **Dynamic Data Visualizations:** Automatically selects and configures Recharts graphs.
7. **Validation & Guardrails:** Audits findings against raw data to ensure zero hallucinations and strict multi-tenant isolation.
8. **Executive Report Synthesis:** Compiles multi-part markdown business reports complete with charts and SQL query evidence.

---

## 2. Current Development Phase

* **Current Phase:** **Phase 1 — Project Foundation**
* **Status:** Complete monorepo skeleton setup, frontend foundation, backend foundation, directory structure, environment configurations, and health check endpoints.
* **Important Note:** Functional modules (database models, demo dataset generation, authentication integration, agent graph nodes, vector ingestion) will be implemented incrementally in subsequent phases.

---

## 3. Technology Stack

### Frontend
* **Core:** Next.js (App Router), React 18+, TypeScript
* **Styling:** Tailwind CSS, shadcn/ui components, Lucide Icons
* **Visualizations:** Recharts
* **State & Data Fetching:** React Hooks, Server-Sent Events (SSE)

### Backend
* **Core:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2
* **Database Access:** Async SQLAlchemy, asyncpg
* **Testing:** pytest, httpx

### AI & Multi-Agent Architecture
* **Orchestration:** LangGraph (StateGraph multi-agent flow)
* **LLM Layer:** Centralized `LLMService` (OpenAI / Provider Abstraction)
* **Analytics Engine:** Pandas, NumPy, scikit-learn
* **SQL Safety:** `sqlglot` AST Parser (SELECT-only validator)

### Platform & Infrastructure
* **Relational DB / Auth / Storage:** Supabase Cloud (PostgreSQL, Supabase Auth, Supabase Storage, Row Level Security)
* **Vector DB:** Qdrant Cloud (Payload-filtered document embeddings)

---

## 4. Repository Structure

```
Business Enterprise/
│
├── frontend/             # Next.js App Router UI application
│   ├── app/              # App router pages & API routes
│   ├── components/       # UI components & shadcn design system
│   ├── lib/              # Frontend utilities & API clients
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript interface definitions
│   └── package.json      # Node.js dependencies
│
├── backend/              # Python FastAPI Application
│   ├── app/              # FastAPI application package
│   │   ├── main.py       # Application entry point & health check
│   │   ├── api/          # REST & SSE API routers
│   │   ├── core/         # Settings, security & logging
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic data schemas
│   │   ├── services/     # Business logic & services
│   │   └── repositories/ # Database repository layer
│   ├── tests/            # Pytest suite
│   └── requirements.txt  # Python package dependencies
│
├── ai/                   # AI & Multi-Agent Engine (LangGraph & LLM)
│   ├── agents/           # 7 Specialized AI Agents
│   ├── orchestration/    # LangGraph StateGraph definition
│   ├── llm/              # Centralized LLMService wrapper
│   ├── rag/              # Ingestion & vector search handlers
│   ├── analytics/        # Pandas/NumPy analytics handlers
│   ├── validation/       # Guardrail & SQL AST checkers
│   ├── tools/            # Agent tool definitions
│   └── prompts/          # System prompt templates
│
├── database/             # Database Schemas & Migrations (Phase 2+)
│   ├── migrations/       # SQL migration scripts
│   ├── seeds/            # Database seed data scripts
│   └── scripts/          # Maintenance scripts
│
├── data/                 # Demo Dataset Generation (NovaMart Retail - Phase 3+)
│   ├── generators/       # Synthetic data generation scripts
│   ├── raw/              # Raw data files
│   └── processed/        # Processed seed datasets
│
├── documents/            # Document Ingestion Storage (Phase 7+)
│   ├── sample/           # Sample corporate PDFs, DOCX, CSV files
│   ├── uploads/          # Temporary upload directory
│   └── processed/        # Chunked text data
│
├── evaluation/           # AI Benchmark & Evaluation Suite (Phase 16)
│   ├── datasets/         # Test query & ground truth evaluation sets
│   ├── tests/            # Automated accuracy test scripts
│   └── reports/          # Benchmarking output reports
│
├── infrastructure/       # Containerization & Deployment Setup (Phase 19)
│   ├── docker/           # Dockerfiles & docker-compose configurations
│   ├── deployment/       # Cloud deployment scripts
│   └── cicd/             # CI/CD pipeline definitions
│
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules
├── ARCHITECTURE.md       # Comprehensive Architecture Specification
├── PROJECT_STATUS.md     # Phase progress tracking & ADR log
└── README.md             # Project documentation (this file)
```

---

## 5. Local Development Setup

### Prerequisites
* **Node.js:** v18.0.0 or higher (v22+ recommended)
* **npm:** v9.0.0 or higher
* **Python:** v3.11.0 or higher

### Environment Configuration
Copy `.env.example` to `.env` in the project root:
```bash
cp .env.example .env
```

---

## 6. Running the Application

### Starting the Backend (FastAPI)
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Backend health check endpoint: [http://localhost:8000/health](http://localhost:8000/health)

### Starting the Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Frontend development server: [http://localhost:3000](http://localhost:3000)

---

## 7. Development Philosophy & Rules

* **Incremental Delivery:** Features are implemented phase-by-phase. No premature feature additions without verification.
* **Separation of Concerns:** 
  * Next.js handles UI, presentation, and client interaction.
  * FastAPI handles API routing, authentication middleware, and backend processing.
  * AI module handles LLM Service, LangGraph orchestration, agents, and RAG.
  * Supabase handles PostgreSQL data, Auth JWTs, Storage, and Row Level Security.
  * Qdrant handles vector embeddings.
* **Strict SQL Security:** The SQL Agent is SELECT-only with AST validation (`sqlglot`) rejecting all mutating statements (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.).

---

## 8. Current Limitations (Phase 1)

* Business API endpoints, database schemas, authentication, agent execution graphs, and vector ingestion are intentionally unbuilt during Phase 1.
* The system currently exposes the foundation workspace layout and a FastAPI health check (`GET /health`).
