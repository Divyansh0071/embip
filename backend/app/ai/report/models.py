"""
Pydantic Schemas for EMBIP Report Generator Agent (Phase 14).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    """Represents an individual section in an executive report."""
    section_id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section narrative content in Markdown format")
    section_type: Literal["executive_summary", "key_metrics", "visualizations", "sources", "methodology"] = Field(
        ..., description="Type of section"
    )


class ReportCitation(BaseModel):
    """Source document chunk citation embedded in a report."""
    source_filename: str = Field(..., description="Name of source document file")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    excerpt: str = Field(..., description="Exact quoted passage from source document")
    score: float = Field(..., description="Semantic match score (0.0 to 1.0)")
    page_number: Optional[int] = Field(default=None, description="Page number if applicable")
    sheet_name: Optional[str] = Field(default=None, description="Sheet name if applicable")


class ReportData(BaseModel):
    """Complete executive business report data structure."""
    report_id: str = Field(..., description="Unique report identifier")
    title: str = Field(..., description="Executive report title")
    subtitle: Optional[str] = Field(default=None, description="Report subtitle / summary line")
    generated_at: str = Field(..., description="ISO timestamp of report generation")
    executive_summary: str = Field(..., description="High-level executive narrative summary")
    sections: List[ReportSection] = Field(default_factory=list, description="Ordered report sections")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Ground-truth metrics from SQL/Analytics")
    visualization_spec: Optional[Dict[str, Any]] = Field(default=None, description="Recharts spec for report chart")
    citations: List[ReportCitation] = Field(default_factory=list, description="Evidence and source document citations")
    methodology: str = Field(..., description="Description of data sources, SQL parameters, and analysis boundaries")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall factual confidence score from Phase 13")
    is_validated: bool = Field(default=True, description="Whether report passed factual guardrail audit")


class ReportExportRequest(BaseModel):
    """Request payload for exporting a report."""
    format: Literal["pdf", "markdown", "json"] = Field(..., description="Export format")
    report_data: ReportData = Field(..., description="Report data structure to export")
