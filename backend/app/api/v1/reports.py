"""
FastAPI Router for Executive Reports (Phase 14).
Provides endpoints to generate executive business reports and export as PDF/Markdown/JSON.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import Response

from app.ai.report.models import ReportData, ReportExportRequest
from app.ai.report.service import report_service
from app.core.security import get_current_user
from app.models.tenancy import User

router = APIRouter(prefix="/reports", tags=["reports"])



@router.post("/generate", response_model=ReportData)
async def generate_report_endpoint(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
):
    """
    Generates an executive business report from question or orchestration result payload.
    """
    question = payload.get("question", "")
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is required to generate a report.",
        )

    try:
        report = await report_service.generate_report(
            question=question,
            sql_result=payload.get("sql_result"),
            rag_result=payload.get("rag_result"),
            analytics_result=payload.get("analytics_result"),
            visualization_result=payload.get("visualization_result"),
            validation_result=payload.get("validation_result"),
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


@router.post("/export")
async def export_report_endpoint(
    payload: ReportExportRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Exports ReportData to PDF, Markdown, or JSON.
    """
    try:
        exported = report_service.export_report(payload)
        
        if payload.format == "pdf":
            return Response(
                content=exported,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="report_{payload.report_data.report_id}.pdf"'
                },
            )
        elif payload.format == "markdown":
            return Response(
                content=exported,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="report_{payload.report_data.report_id}.md"'
                },
            )
        else:
            return exported
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report export failed: {str(e)}",
        )
