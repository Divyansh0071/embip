"""
Planner Agent for Multi-Agent Task Classification & Intent Decomposition (Phase 10).
Analyzes natural language business questions using LLMService and produces structured execution plans.
"""

import json
import logging
from typing import Optional

from app.ai.llm import llm_service
from app.ai.llm.models import LLMMessage, LLMRequest
from app.ai.orchestration.exceptions import PlannerError
from app.ai.orchestration.models import PlannerPlan

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are the master Planner Agent for EMBIP (Enterprise Multi-Agent Business Intelligence Platform).
Your job is to analyze the user's business question and decide which platform capabilities are required to answer it.

AVAILABLE CAPABILITIES:
1. "requires_sql" (SQL Agent): Set to true if the question asks for numeric metrics, totals, sales, store data, employee counts, expenses, customer metrics, inventory, or structured database records.
2. "requires_rag" (RAG Search Agent): Set to true if the question asks about company policies, uploaded documents, contract terms, text reports, FAQs, or unstructured text files.
3. "requires_analytics" (Analytics Agent): Set to true if the question explicitly asks for complex statistical transformations, regression, growth projections, or advanced mathematical calculations.
4. "requires_visualization" (Visualization Agent): Set to true if the question explicitly asks for a chart, graph, plot, or visual representation (e.g. "show a bar chart of...").

RULES:
- If a question needs BOTH relational data and document context (e.g., "What was total sales in Q3 and what does our return policy say?"), set BOTH requires_sql=true AND requires_rag=true.
- Do NOT output chain-of-thought or reasoning text inside JSON. Keep "reason" concise (1-2 sentences max).
- Return raw JSON matching this EXACT structure:
{
  "intent": "sql_query|rag_search|combined|analytics|visualization|general",
  "requires_sql": boolean,
  "requires_rag": boolean,
  "requires_analytics": boolean,
  "requires_visualization": boolean,
  "reason": "Concise justification for selected tools."
}
- Do NOT wrap JSON in markdown code blocks. Return raw JSON string only.
"""


class PlannerAgent:
    """
    Agent responsible for analyzing natural language questions and selecting required capability nodes.
    """

    def _parse_planner_json(self, raw_text: str) -> PlannerPlan:
        """Parses raw text response from LLM into PlannerPlan model."""
        text_content = raw_text.strip()
        if text_content.startswith("```"):
            lines = text_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text_content = "\n".join(lines).strip()

        try:
            data = json.loads(text_content)
            return PlannerPlan(
                intent=data.get("intent", "general"),
                requires_sql=bool(data.get("requires_sql", False)),
                requires_rag=bool(data.get("requires_rag", False)),
                requires_analytics=bool(data.get("requires_analytics", False)),
                requires_visualization=bool(data.get("requires_visualization", False)),
                reason=data.get("reason", "Analyzed query intent to determine appropriate platform tool capabilities."),
            )
        except json.JSONDecodeError as e:
            raise PlannerError(f"Planner Agent received non-JSON output from LLM: {str(e)}")
        except Exception as e:
            raise PlannerError(f"Failed to parse Planner Agent output: {str(e)}")

    async def plan(
        self,
        question: str,
        provider_name: Optional[str] = None,
    ) -> PlannerPlan:
        """
        Classifies user question into structured execution plan.
        """
        messages = [
            LLMMessage(role="system", content=PLANNER_SYSTEM_PROMPT),
            LLMMessage(role="user", content=f'Analyze business question: "{question}"'),
        ]

        llm_req = LLMRequest(
            messages=messages,
            temperature=0.0,
            max_tokens=500,
        )

        try:
            llm_resp = await llm_service.generate(llm_req, provider_name=provider_name)
            plan = self._parse_planner_json(llm_resp.content)
            logger.info(
                f"Planner Agent Plan | intent='{plan.intent}' "
                f"sql={plan.requires_sql} rag={plan.requires_rag} "
                f"analytics={plan.requires_analytics} viz={plan.requires_visualization}"
            )
            return plan
        except Exception as e:
            logger.error(f"Planner Agent Failed | error='{str(e)}'")
            if isinstance(e, PlannerError):
                raise e
            raise PlannerError(f"Planner Agent classification failed: {str(e)}")


# Singleton Instance
planner_agent = PlannerAgent()
