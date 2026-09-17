# ARCHITECTURE.md — EMBIP Technical Architecture Specification

**Project Name:** EMBIP — Enterprise Multi-Agent Business Intelligence Platform  
**Document Version:** 1.0.0  
**Phase:** Phase 0 — Architecture  
**Date:** September 2026  

---

## 1. Executive Summary & System Overview

EMBIP (Enterprise Multi-Agent Business Intelligence Platform) is a next-generation enterprise business intelligence system designed to enable decision-makers to ask natural-language questions about complex structured business data and unstructured corporate documents. 

Unlike traditional static dashboards or simple text-to-SQL tools, EMBIP leverages a stateful **multi-agent orchestration framework (LangGraph)** powered by a **Centralized LLMService**. It decomposes complex analytical queries into distinct operational steps executed by specialized AI agents: planning, SQL generation & execution, document retrieval (RAG), statistical analytics, data visualization, safety/accuracy validation, and executive report synthesis.

---

## 2. System Architecture Diagram

```mermaid
flowchart TB
    subgraph ClientLayer ["Client Layer (Frontend)"]
        UI["Next.js 14/15 App Router<br/>TypeScript | Tailwind CSS | shadcn/ui"]
        VizEngine["Recharts Visualization Engine"]
        StreamClient["SSE / WebSocket Stream Client"]
    end

    subgraph APILayer ["API & Gateway Layer (Backend)"]
        FastAPI["FastAPI App (Python 3.11+)"]
        AuthMiddleware["JWT & Multi-Tenant Middleware"]
        IngestionPipeline["Document Ingestion & Chunking Engine"]
        CentralLLM["Centralized LLMService<br/>(OpenAI / Generic Provider Abstraction)"]
    end

    subgraph MultiAgentLayer ["Orchestration & Multi-Agent Engine (LangGraph)"]
        Graph["LangGraph StateGraph"]
        Planner["1. Planner Agent"]
        SQLAgent["2. SQL Agent"]
        DocAgent["3. Document/RAG Agent"]
        AnalyticsAgent["4. Analytics Agent"]
        VizAgent["5. Visualization Agent"]
        ValidationAgent["6. Validation Agent"]
        ReportAgent["7. Report Generator Agent"]
    end

    subgraph SecurityLayer ["Security & Validation Guardrails"]
        ASTValidator["SQL AST Safety Validator<br/>(sqlglot - SELECT-only Enforcement)"]
        RLSEnforcer["Tenant Context Enforcer"]
    end

    subgraph PlatformLayer ["Database, Storage & Vector Platform"]
        SupabaseDB[("Supabase PostgreSQL DB<br/>(NovaMart Domain + App Metadata)")]
        SupabaseRLS["Supabase Row Level Security (RLS)"]
        SupabaseAuth["Supabase Auth (JWT & Roles)"]
        SupabaseStorage["Supabase Storage (Raw Docs & Reports)"]
        Qdrant[("Qdrant Cloud Vector DB<br/>(Document Chunk Embeddings)")]
    end

    %% Client Interactions
    UI -->|HTTP / REST API| FastAPI
    UI <-->|Real-time Agent Stream| StreamClient
    StreamClient <-->|SSE Stream| FastAPI

    %% API Layer Route
    FastAPI --> AuthMiddleware
    AuthMiddleware --> Graph
    FastAPI --> IngestionPipeline

    %% Agent Graph Flow
    Graph --> Planner
    Planner --> SQLAgent
    Planner --> DocAgent
    
    SQLAgent --> ASTValidator
    ASTValidator -->|Validated Query| SupabaseDB
    
    DocAgent -->|Payload Filtered Vector Search| Qdrant

    SQLAgent --> AnalyticsAgent
    DocAgent --> AnalyticsAgent
    
    AnalyticsAgent --> VizAgent
    VizAgent --> ValidationAgent
    ValidationAgent -->|Approved Artifacts| ReportAgent
    ValidationAgent -.->|Retry on Error/Hallucination| Planner

    %% Centralized LLM Connections
    Planner --- CentralLLM
    SQLAgent --- CentralLLM
    DocAgent --- CentralLLM
    AnalyticsAgent --- CentralLLM
    VizAgent --- CentralLLM
    ValidationAgent --- CentralLLM
    ReportAgent --- CentralLLM

    %% Platform Integrations
    IngestionPipeline --> SupabaseStorage
    IngestionPipeline --> Qdrant
    AuthMiddleware --> SupabaseAuth
    SupabaseDB --- SupabaseRLS

    classDef client fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef api fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef agent fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#fff;
    classDef security fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#fff;
    classDef platform fill:#064e3b,stroke:#14b8a6,stroke-width:2px,color:#fff;

    class UI,VizEngine,StreamClient client;
    class FastAPI,AuthMiddleware,IngestionPipeline,CentralLLM api;
    class Graph,Planner,SQLAgent,DocAgent,AnalyticsAgent,VizAgent,ValidationAgent,ReportAgent agent;
    class ASTValidator,RLSEnforcer security;
    class SupabaseDB,SupabaseRLS,SupabaseAuth,SupabaseStorage,Qdrant platform;
```

---

## 3. Component Responsibilities

### 3.1 Frontend (Next.js)
* **Framework:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui.
* **Responsibilities:**
  * **Ask Interface:** Rich chat-style and dashboard prompt bar supporting natural-language query input.
  * **Real-time Execution Stream:** Visualizes live agent transitions, tool execution steps, and sub-task status using Server-Sent Events (SSE).
  * **Interactive Visualizations:** Renders responsive data charts using **Recharts** based on structured JSON configurations returned by the Visualization Agent.
  * **Evidence & SQL Panel:** Provides full transparency by displaying generated SQL code, query execution metrics, and cited document context snippets.
  * **Report View & Export:** Formats multi-part business intelligence reports with executive summaries, metrics, charts, and downloadable Markdown/PDF formats.
  * **Document Management:** Multi-file drag-and-drop upload interface for PDF, DOCX, TXT, CSV, and XLSX formats with processing status indicators.
  * **Auth & Workspace Navigation:** Manages active organization and workspace switching, authenticates via Supabase Auth client SDK.

### 3.2 Backend (FastAPI)
* **Framework:** Python 3.11+, FastAPI, Pydantic v2, Async SQLAlchemy.
* **Responsibilities:**
  * **Multi-Agent Orchestration:** Hosts and executes the LangGraph workflow engine.
  * **Centralized LLMService:** Manages unified provider client instances, model routing, prompt engineering templates, token tracking, and safety guardrails.
  * **Document Ingestion Engine:** Handles file extraction, semantic chunking, embedding generation, and vector database upserts.
  * **Security Enforcement:** AST-based SQL parser validation, strict SELECT-only enforcement, query limits, execution timeouts, and tenant context propagation.
  * **API Gateway & Streaming:** Exposes RESTful endpoints and asynchronous SSE endpoints for live agent execution feedback.

### 3.3 Supabase Platform
* **Services Used:** PostgreSQL Database, Supabase Auth, Supabase Storage, Row Level Security (RLS).
* **Responsibilities:**
  * **Relational Storage:** Stores transactional business data (NovaMart domain model), user profiles, organization structures, document metadata, execution history, and generated reports.
  * **Authentication:** Handles user registration, login, JWT token issuance, session verification, and role assignments.
  * **Multi-Tenant Isolation (RLS):** Database policies enforce strict data boundary checks matching `org_id` and `workspace_id` derived from JWT tokens.
  * **Storage:** Bucket storage for original enterprise documents and exported report assets.

### 3.4 Qdrant Vector Database
* **Deployment:** Qdrant Cloud.
* **Responsibilities:**
  * **Dense & Hybrid Vector Storage:** Stores high-dimensional vector embeddings generated from document chunks.
  * **Payload Filtering:** Executes filtered vector similarity searches using mandatory payload attributes (`org_id`, `workspace_id`, `document_id`, `access_level`) to ensure tenant isolation.
  * **Semantic Retrieval:** Supplies contextually relevant document snippets to the Document/RAG Agent.

---

## 4. AI & Centralized LLMService Architecture

To eliminate credential sprawl and ensure centralized governance, EMBIP explicitly prohibits creating separate API keys, direct client instantiations, or unmanaged LLM calls across individual agents.

```
                  +-----------------------------------+
                  |      Centralized LLMService       |
                  |  (OpenAI / Provider Abstraction)   |
                  +-----------------------------------+
                                    |
         +--------------------------+--------------------------+
         |                          |                          |
[Config & Credentials]     [Provider Adapter]       [Telemetry & Token Tracker]
         |                          |                          |
         +--------------------------+--------------------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
    Planner Agent              SQL Agent               Document Agent
  (System Prompt A,        (System Prompt B,         (System Prompt C,
   Tools: Schema,            Tools: SQL AST,          Tools: Qdrant Search,
   Temp: 0.1)                Temp: 0.0)               Temp: 0.2)
          |                         |                         |
          +-------------------------+-------------------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
   Analytics Agent          Viz Agent            Validation / Report Agents
  (System Prompt D,        (System Prompt E,         (System Prompt F/G,
   Tools: Pandas/Py,         Tools: Recharts Spec,    Tools: Guardrail Checkers,
   Temp: 0.1)                Temp: 0.2)               Temp: 0.2)
```

### Key Principles of Centralized LLMService:
1. **Single Point of Configuration:** Global API keys, base URLs, timeouts, retry rules, and fallback models (e.g., GPT-4o, Claude 3.5 Sonnet, or local models) are configured once in `LLMService`.
2. **Provider Agnosticism:** Exposes a unified interface (`llm_service.generate()`, `llm_service.generate_structured()`) wrapping LiteLLM/LangChain/Direct SDKs, making provider switches zero-impact to agent code.
3. **Agent Context Injection:** Each agent calls `LLMService` with its specific:
   * **System Prompt:** Specialized instructions, output format rules, and role constraints.
   * **Tool Bindings:** Strictly defined JSON Schema tools authorized for that agent.
   * **Temperature & Top_P:** Tailored determinism (e.g., `0.0` for SQL generation, `0.2` for report writing).
   * **Permissions & Token Budget:** Custom max token thresholds and execution scopes.

---

## 5. LangGraph Multi-Agent Architecture

The core intelligent engine of EMBIP is built on **LangGraph**, utilizing a stateful `StateGraph` that manages data flow, decision nodes, and conditional execution paths across 7 specialized agents.

### 5.1 The 7 Specialized Agents

```
+-----------------------------------------------------------------------------------+
|                                 LANGGRAPH STATE                                   |
| user_query | org_id | workspace_id | plan | sql_results | rag_chunks | final_report |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
                                 [ 1. PLANNER AGENT ]
                                          |
                    +---------------------+---------------------+
                    |                                           |
                    v                                           v
           [ 2. SQL AGENT ]                           [ 3. DOCUMENT AGENT ]
                    |                                           |
                    v                                           |
           (AST Safety Check)                                   |
                    |                                           |
                    v                                           |
          (Execute DB Query)                                    |
                    |                                           |
                    +---------------------+---------------------+
                                          |
                                          v
                               [ 4. ANALYTICS AGENT ]
                                 (Pandas / NumPy)
                                          |
                                          v
                            [ 5. VISUALIZATION AGENT ]
                              (Recharts JSON Spec)
                                          |
                                          v
                             [ 6. VALIDATION AGENT ]
                          (Factual & Safety Audit)
                                    /           \
                             (Valid)             (Invalid / Hallucination)
                               /                   \
                              v                     v
                [ 7. REPORT GENERATOR ]     [ Loop Back to Planner ]
                              |                   (Max 2 retries)
                              v
                            (END)
```

1. **Planner Agent:**
   * **Role:** Analyzes user query, database schema summary, and document catalog. Decomposes the question into a structured execution plan JSON containing sequential or parallel sub-tasks.
2. **SQL Agent:**
   * **Role:** Constructs parametrized SQL queries against the relational database based on the schema and analytical requirements formulated by the Planner Agent.
3. **Document/RAG Agent:**
   * **Role:** Converts domain questions into semantic embeddings and executes payload-filtered searches against Qdrant Cloud to fetch contextual text and table chunks.
4. **Analytics Agent:**
   * **Role:** Receives raw SQL tabular query results and document text chunks. Executes complex mathematical, statistical, time-series, variance, or predictive computations using **Pandas**, **NumPy**, and **scikit-learn**.
5. **Visualization Agent:**
   * **Role:** Evaluates analytics outputs, selects the most informative chart type (Bar, Line, Pie, Scatter, Area), and constructs valid, responsive **Recharts-compliant JSON specifications**.
6. **Validation Agent:**
   * **Role:** Acts as the primary guardrail. Validates that:
     * Generated SQL passed AST safety checks.
     * Output numerical findings directly correlate with raw database results (prevents hallucination).
     * Responses adhere to compliance and tenant isolation constraints.
7. **Report Generator Agent:**
   * **Role:** Synthesizes overall analytical narrative, executive summary, key metrics, embedded chart JSONs, raw SQL query evidence, and document citations into a structured Markdown business report.

### 5.2 LangGraph State Schema (`EMBIPState`)

```python
from typing import TypedDict, List, Dict, Any, Optional

class EMBIPState(TypedDict):
    user_query: str
    org_id: str
    workspace_id: str
    user_role: str
    
    # Operational Artifacts
    plan: Optional[Dict[str, Any]]
    generated_sql: Optional[str]
    sql_is_valid: bool
    sql_execution_result: Optional[List[Dict[str, Any]]]
    rag_chunks: Optional[List[Dict[str, Any]]]
    analytics_results: Optional[Dict[str, Any]]
    visualization_config: Optional[Dict[str, Any]]
    validation_status: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    
    # Execution Metadata & Control
    execution_steps: List[Dict[str, Any]]
    retry_count: int
    error: Optional[str]
```

---

## 6. Document RAG Architecture

```
[ Upload Document ] (PDF, DOCX, TXT, CSV, XLSX)
         |
         v
[ File Type Parser ] ---> [ Text & Table Extraction ]
                                 |
                                 v
                     [ Semantic Chunking Engine ]
                     (500-1000 tokens, 10% overlap)
                                 |
                                 v
                     [ Embedding Generator ]
                     (OpenAI text-embedding-3-small)
                                 |
                                 v
                     [ Qdrant Cloud Upsert ]
                     Payload: {
                         "org_id": "uuid",
                         "workspace_id": "uuid",
                         "document_id": "uuid",
                         "file_name": "Q2_Report.pdf",
                         "chunk_index": 4,
                         "text_content": "..."
                     }
```

### Ingestion & Retrieval Features:
* **Multi-Format Parsing:** Support for unstructured PDFs/DOCXs (`pypdf`, `python-docx`), plain text, and structured sheets (`openpyxl`, `pandas` for CSV/XLSX).
* **Tabular Preservation:** CSV and XLSX files are parsed into semantic row summaries and table headers to retain matrix contextual integrity.
* **Strict Payload Filtering:** Vector retrieval mandatory filter:
  `Qdrant.search(collection="documents", query_vector=vec, query_filter=Filter(must=[FieldCondition(key="org_id", match=MatchValue(value=org_id)), FieldCondition(key="workspace_id", match=MatchValue(value=workspace_id))]))`

---

## 7. SQL Agent Security Architecture

Security of the database is non-negotiable. The SQL Agent operates under strict programmatic and network guardrails.

```
[ SQL Agent Output ]
         |
         v
[ AST Safety Validator (sqlglot) ]
         |
  +------+--------------------------------------------------+
  | Checks:                                                 |
  | 1. Is root statement == SELECT?                         |
  | 2. Contains forbidden keywords? (INSERT, DROP, etc.)   |
  | 3. Contains multiple statements separated by ';' ?      |
  | 4. Is dynamic code execution present? (EXEC, CALL)      |
  +------+--------------------------------------------------+
         |
   (Pass / Reject)
     /         \
 (PASS)       (REJECT) ---> Raise SecurityException & Loop Back to SQL Agent
   |
   v
[ Automatic Query Limits & Timeout Injection ]
  - Append 'LIMIT 1000' if omitted
  - SET LOCAL statement_timeout = '5000ms'
   |
   v
[ Read-Only PostgreSQL User Connection ]
  - Privilege: SELECT ONLY on NovaMart tables
  - Connection Scope: Parametrized execution via Async SQLAlchemy
```

### Forbidden Operations (Strictly Prohibited):
`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`, `COPY`, `VACUUM`, `REINDEX`, `EXEC`, `EXECUTE`, `CALL`, semicolon chaining (`;`).

---

## 8. Multi-Tenancy & Authentication Architecture

EMBIP implements a strict hierarchical multi-tenant structure:

$$\text{User} \longrightarrow \text{Organization} \longrightarrow \text{Workspace} \longrightarrow \begin{cases} \text{Business Data} \\ \text{Documents} \\ \text{Queries} \\ \text{Reports} \end{cases}$$

```
+-----------------------------------------------------------------------+
|                            USER IDENTITY                              |
|                       (Supabase Auth JWT Token)                       |
+-----------------------------------------------------------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
         v                                                   v
[ Database Layer Isolation ]                        [ Vector Layer Isolation ]
  Supabase Row Level Security (RLS)                   Qdrant Payload Filtering
  
  CREATE POLICY tenant_isolation                      Filter(must=[
  ON workspace_table                                      FieldCondition("org_id", org),
  FOR ALL USING (                                         FieldCondition("workspace_id", ws)
    org_id = auth.jwt() -> 'org_id'                   ])
    AND workspace_id = auth.jwt() -> 'workspace_id'
  );
```

### Role-Based Access Control (RBAC):
* **Owner:** Full access to Organization, Workspaces, User Invitations, Billing, and Data.
* **Admin:** Workspace configuration, Document Ingestion, Data source management, Querying.
* **Analyst:** Executing queries, generating reports, viewing document evidence, exporting.
* **Viewer:** Read-only access to saved reports and dashboards.

---

## 9. Database Schema Proposal (NovaMart Retail Solutions)

The relational schema is divided into **System & Multi-Tenancy Core**, **NovaMart Business Domain**, and **Query/Report Audit Tables**.

```
+---------------------------------------------------------------------------------------------------+
|                                     NOVAMART RETAIL DOMAIN SCHEMA                                 |
+---------------------------------------------------------------------------------------------------+
|  ORGANIZATIONS (id, name, created_at)                                                             |
|   └── WORKSPACES (id, org_id, name, created_at)                                                    |
|        ├── USERS & WORKSPACE_MEMBERS (id, user_id, workspace_id, role)                            |
|        ├── CATEGORIES (id, workspace_id, name, description)                                       |
|        │    └── PRODUCTS (id, workspace_id, category_id, sku, name, unit_cost, unit_price)        |
|        ├── WAREHOUSES (id, workspace_id, warehouse_code, name, city, state, capacity_sqft)         |
|        │    └── INVENTORY (id, workspace_id, warehouse_id, product_id, quantity_on_hand)          |
|        ├── STORES (id, workspace_id, store_code, name, city, state, square_feet, opened_date)     |
|        │    ├── EMPLOYEES (id, workspace_id, store_id, first_name, last_name, role, salary)     |
|        │    ├── OPERATING_EXPENSES (id, workspace_id, store_id, expense_date, category, amount)   |
|        │    └── SALES_TRANSACTIONS (id, workspace_id, store_id, customer_id, employee_id, total)  |
|        │         └── SALES_ITEMS (id, workspace_id, transaction_id, product_id, qty, unit_price)|
|        ├── CUSTOMERS (id, workspace_id, customer_code, first_name, last_name, email, city, state) |
|        ├── DOCUMENTS & CHUNKS (id, workspace_id, storage_path, status, metadata)                 |
|        ├── QUERIES & EXECUTIONS (id, workspace_id, user_id, natural_query, sql, execution_ms)     |
|        └── REPORTS (id, workspace_id, query_id, title, content_markdown, viz_config_json)         |
+---------------------------------------------------------------------------------------------------+
```

### Summary Scale of NovaMart Demo Target (Phase 3):
* 10 Stores, 5 Warehouses, 50 Products, 200 Employees, 20,000+ Customers, 100,000+ Sales Transactions across 3 years of historical data.

---

## 10. API Architecture & Endpoint Design

FastAPI REST and Streaming endpoints:

```
AUTHENTICATION & WORKSPACE:
  POST   /api/v1/auth/session          -> Validate JWT & load tenant context
  GET    /api/v1/workspaces            -> List user accessible workspaces
  POST   /api/v1/workspaces            -> Create workspace (Admin/Owner)

DOCUMENT INGESTION & RAG:
  POST   /api/v1/documents/upload      -> Upload PDF/DOCX/CSV file & trigger chunking
  GET    /api/v1/documents             -> List workspace ingested documents
  DELETE /api/v1/documents/{id}        -> Remove document metadata & Qdrant vectors

NATURAL LANGUAGE QUERY & MULTI-AGENT EXECUTION:
  POST   /api/v1/query/ask             -> Submit query ("Why did profit decrease in Q2?")
  GET    /api/v1/query/{query_id}/stream -> Real-time SSE stream of agent execution graph
  GET    /api/v1/query/history         -> List query log history for workspace

REPORTS & EXPORT:
  GET    /api/v1/reports/{report_id}   -> Fetch synthesized Markdown report & viz JSON
  POST   /api/v1/reports/{report_id}/export -> Export report to PDF / Markdown package

SYSTEM HEALTH:
  GET    /api/v1/health                -> Check health of DB, Qdrant, and LLM connection
```

---

## 11. Complete Natural-Language-Query Data Flow

### Example Query: *"Why did our profit decrease in Q2?"*

```
[ USER ]  ---> Inputs query in Next.js UI
   |
   v
[ NEXT.JS ]  ---> Sends POST /api/v1/query/ask (JWT Bearer Token attached)
   |
   v
[ FASTAPI GATEWAY ]
   ├── Validates JWT token via Supabase Auth
   ├── Extracts org_id, workspace_id, user_role
   └── Initializes LangGraph StateGraph with EMBIPState
   |
   v
[ 1. PLANNER AGENT ]
   ├── Calls LLMService with Database Schema Summary & Document Catalog
   └── Formulates Plan:
       Step 1: Execute SQL comparing Q1 vs Q2 Revenue, Expenses, and Profit Margin.
       Step 2: Query Qdrant vector store for Q2 Management & Operational Reports.
       Step 3: Run Analytics Agent to calculate variance & cost drivers.
       Step 4: Generate Visualization JSON for Q1 vs Q2 comparison.
       Step 5: Audit result with Validation Agent.
       Step 6: Synthesize Executive Report.
   |
   v
[ 2. SQL AGENT ]  --- (Parallel Step A) ---
   ├── Generates Parametrized SQL query on sales_items & operating_expenses
   ├── AST Validator checks query -> SELECT-only approved!
   └── Executes query on Supabase DB -> Returns Tabular Results (e.g. Expense spike in Freight + Logistics)
   |
   v
[ 3. DOCUMENT/RAG AGENT ]  --- (Parallel Step B) ---
   ├── Embeds query & searches Qdrant with payload filter workspace_id
   └── Retrieves chunk: "In Q2, regional warehouse shipping surcharges increased by 28% due to supplier fuel index adjustments..."
   |
   v
[ 4. ANALYTICS AGENT ]
   ├── Takes SQL tabular numbers + Document context
   └── Computes variance percentages in Pandas: Revenue -0.8%, Operating Expenses +14.2%, Net Profit -18.5%
   |
   v
[ 5. VISUALIZATION AGENT ]
   └── Generates Recharts Config JSON: Bar/Line combo showing Revenue vs Expense vs Profit Margin by month
   |
   v
[ 6. VALIDATION AGENT ]
   ├── Verifies numbers in summary match SQL execution data exactly
   └── Confirms AST safety & absence of hallucinated facts -> APPROVED!
   |
   v
[ 7. REPORT GENERATOR AGENT ]
   └── Compiles Markdown executive report with inline charts, SQL query snippet, document citation links
   |
   v
[ FASTAPI SSE STREAM ]  ---> Pushes live updates to Next.js UI
   |
   v
[ NEXT.JS UI ]  ---> Renders interactive report, Recharts graphics, and evidence panel!
```

---

## 12. Deployment Architecture

```
+-----------------------+     +-------------------------------+
|     Vercel Platform   |     |    Docker-Compatible Host     |
|                       |     |   (AWS ECS / GCP Cloud Run)   |
|   Next.js 14/15 App   |     |                               |
|  TypeScript Frontend  |     |  FastAPI Multi-Agent Server   |
+-----------+-----------+     +---------------+---------------+
            |                                 |
            +----------------+----------------+
                             |
         +-------------------+-------------------+
         |                                       |
         v                                       v
+-----------------------+              +-----------------------+
| Supabase Cloud Platform|              |     Qdrant Cloud      |
|                       |              |                       |
|  - PostgreSQL DB      |              | - Vector Cluster      |
|  - Supabase Auth      |              | - Document Payload    |
|  - Supabase Storage   |              |   Filtered Index      |
|  - Row Level Security |              |                       |
+-----------------------+              +-----------------------+
```

---

## 13. Environment Variable Plan

```env
# ==============================================================================
# FRONTEND ENVIRONMENT VARIABLES (.env.local)
# ==============================================================================
NEXT_PUBLIC_APP_NAME="EMBIP — Enterprise Multi-Agent BI Platform"
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"
NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-supabase-anon-key"

# ==============================================================================
# BACKEND ENVIRONMENT VARIABLES (.env)
# ==============================================================================
# Core App
PROJECT_NAME="EMBIP Backend Engine"
ENVIRONMENT="development"
LOG_LEVEL="INFO"
SECRET_KEY="your-super-secret-jwt-signing-key"

# Supabase Platform
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"
DATABASE_URL="postgresql+asyncpg://postgres.ref:password@aws-0-region.pooler.supabase.com:6543/postgres"
DATABASE_READONLY_URL="postgresql+asyncpg://readonly_user:password@aws-0-region.pooler.supabase.com:6543/postgres"

# Qdrant Vector DB
QDRANT_URL="https://your-cluster.qdrant.tech:6333"
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_COLLECTION_NAME="embip_document_chunks"

# Centralized LLM Service
LLM_PROVIDER="openai" # openai, azure, anthropic
OPENAI_API_KEY="sk-proj-your-openai-api-key"
OPENAI_MODEL_PRIMARY="gpt-4o"
OPENAI_MODEL_FAST="gpt-4o-mini"
EMBEDDING_MODEL="text-embedding-3-small"

# Security & Limits
MAX_SQL_QUERY_LIMIT=1000
SQL_QUERY_TIMEOUT_SECONDS=5
RATE_LIMIT_PER_MINUTE=60
```

---

## 14. Technical Risks & Mitigations

| Risk Factor | Impact | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **SQL Injection & Data Corruption** | Malicious or hallucinated query alters/deletes database records. | **CRITICAL** | 1. AST Parser validation (`sqlglot`) rejecting non-SELECT statements.<br/>2. Read-only PostgreSQL connection role.<br/>3. Parametrized execution via SQLAlchemy. |
| **Cross-Tenant Data Leakage** | User accesses another organization's financial data or documents. | **CRITICAL** | 1. Supabase Row Level Security (RLS) on relational database.<br/>2. Mandatory Qdrant payload filtering on `org_id` and `workspace_id`.<br/>3. FastAPI JWT authentication context injection. |
| **LLM Hallucination in Financial Reports** | Agent outputs inaccurate calculations or fabricates metrics. | **HIGH** | 1. Validation Agent cross-checking text with raw query output.<br/>2. Pandas/NumPy execution offload for all mathematical ops.<br/>3. Mandatory evidence citations. |
| **Multi-Agent Latency & Timeout** | 7-agent sequential loop causes web response timeouts. | **HIGH** | 1. Parallel execution of SQL and RAG agents in LangGraph.<br/>2. Real-time streaming via Server-Sent Events (SSE).<br/>3. Max retry limit (2) on graph validation node. |

---

## 15. Dependencies Plan

### Backend (Python 3.11+)
`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `asyncpg`, `langgraph`, `langchain-core`, `langchain-openai`, `qdrant-client`, `pandas`, `numpy`, `scikit-learn`, `sqlglot`, `pypdf`, `python-docx`, `openpyxl`, `python-jose`, `passlib`, `httpx`, `pytest`, `ruff`, `mypy`.

### Frontend (Node.js 18+)
`next`, `react`, `react-dom`, `typescript`, `tailwindcss`, `@shadcn/ui`, `recharts`, `lucide-react`, `@supabase/supabase-js`, `zod`, `axios`, `clsx`, `tailwind-merge`.

---

## 16. MVP vs Future Features

| Feature | Phase 0 - Phase 16 (MVP Scope) | Post-MVP / Future Expansion |
| :--- | :--- | :--- |
| **Multi-Agent Graph** | 7 core agents in LangGraph stateful graph | Custom user-defined sub-agents & custom workflow nodes |
| **SQL Security** | SELECT-only AST validation + read-only DB role | Dynamic view generation & sandboxed read-only replicas |
| **RAG Ingestion** | PDF, DOCX, TXT, CSV, XLSX parsing & Qdrant vector store | Real-time Notion, Slack, Google Drive & Confluence connectors |
| **Visualizations** | Recharts (Bar, Line, Pie, Scatter, Area) | Interactive 3D graphics & custom D3.js dashboard widgets |
| **Multi-Tenancy** | Org -> Workspace -> RLS & Payload filtering | Enterprise SSO (SAML/Okta) & dedicated schema per tenant |
| **LLM Support** | Centralized LLMService (OpenAI / generic abstraction) | Local Ollama/vLLM enterprise self-hosted fallback |

---

**Architecture Status:** COMPLETE  
**Implementation Code Started:** NO  
**Ready for Phase 1:** YES
