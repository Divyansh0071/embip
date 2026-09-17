# AI & Multi-Agent Module (`ai/`)

This directory houses the AI and Multi-Agent Orchestration Engine for EMBIP.

## Directory Structure

```
ai/
├── agents/        # 7 Specialized AI Agents (Planner, SQL, RAG, Analytics, Viz, Validation, Report)
├── orchestration/ # LangGraph StateGraph workflow definition & state schema
├── llm/           # Centralized LLMService wrapper & provider adapters
├── rag/           # Document parsing, chunking, and Qdrant vector retrieval engine
├── analytics/     # Pandas, NumPy, scikit-learn statistical computation engine
├── validation/    # AST SQL safety validator & factual guardrails
├── tools/         # Agent tool definitions (SQL execution, Qdrant search, calculation)
├── prompts/       # Agent prompt templates & system instructions
└── tests/         # Unit & integration tests for AI components
```

## Module Responsibilities

* **Centralized LLMService (`ai/llm/`):** Unified access point for LLM interactions. Managed centrally to prevent credential leakage and enable telemetry.
* **LangGraph State Graph (`ai/orchestration/`):** Manages multi-agent execution graphs, state transitions, conditional edges, and error retries.
* **Security & Guardrails (`ai/validation/`):** Validates generated SQL AST before DB execution and audits final reports against raw source data.
