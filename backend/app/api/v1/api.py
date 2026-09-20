from fastapi import APIRouter
from app.api.v1.endpoints import ask, auth, documents, llm, rag, sql

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(llm.router)
api_router.include_router(documents.router)
api_router.include_router(rag.router)
api_router.include_router(sql.router, prefix="/sql", tags=["SQL Agent"])
api_router.include_router(ask.router, prefix="/ask", tags=["Orchestration Agent"])
