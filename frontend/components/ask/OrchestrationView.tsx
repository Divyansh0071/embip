"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Send,
  Database,
  FileText,
  LineChart,
  PieChart,
  CheckCircle2,
  AlertCircle,
  Clock,
  Loader2,
  Table as TableIcon,
  ShieldCheck,
} from "lucide-react";
import { RechartsRenderer, RechartsSpec } from "../visualization/RechartsRenderer";

interface PlannerPlan {
  intent: string;
  requires_sql: boolean;
  requires_rag: boolean;
  requires_analytics: boolean;
  requires_visualization: boolean;
  reason: string;
}

interface AskResponse {
  request_id: string;
  question: string;
  status: string;
  plan: PlannerPlan;
  results: {
    sql?: {
      sql: string;
      explanation: string;
      tables_used: string[];
      columns: string[];
      rows: Record<string, any>[];
      row_count: number;
      execution_time_ms: number;
      status: string;
    } | null;
    rag?: {
      query: string;
      total_retrieved: number;
      results: Array<{
        chunk_id: string;
        filename: string;
        chunk_index: number;
        content: string;
        score: number;
        page_number?: number | null;
        sheet_name?: string | null;
      }>;
    } | null;
    analytics?: {
      operation: string;
      status: string;
      metric?: string | null;
      value?: number | string | null;
      groups?: Array<{ group: string; value: number | string }> | null;
      series?: Array<{ period: string; value: number | string }> | null;
      summary?: {
        rows_input: number;
        rows_used: number;
        missing_values: number;
        warnings: string[];
      };
      explanation?: string | null;
      error?: string | null;
      message?: string;
    } | null;
    visualization?: {
      status: string;
      spec?: RechartsSpec | null;
      explanation?: string | null;
      error?: string | null;
      message?: string;
    } | null;
    validation?: {
      is_valid: boolean;
      confidence_score: number;
      checks: Array<{
        check_name: string;
        passed: boolean;
        score: number;
        message: string;
        details?: Record<string, any>;
      }>;
      hallucinations_detected: string[];
      contradictions_detected: string[];
      warnings: string[];
      action: "pass" | "retry" | "flag";
    } | null;
  };
  errors: string[];
  execution_time_ms: number;
}

interface OrchestrationViewProps {
  getAuthToken: () => Promise<string | null>;
}

export const OrchestrationView: React.FC<OrchestrationViewProps> = ({ getAuthToken }) => {
  const [question, setQuestion] = useState("");
  const [askResponse, setAskResponse] = useState<AskResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsExecuting(true);
    setErrorMessage(null);
    setAskResponse(null);

    try {
      const token = await getAuthToken();
      if (!token) {
        setErrorMessage("Authentication session expired. Please log in.");
        setIsExecuting(false);
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: question.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Orchestration failed with HTTP ${response.status}`);
      }

      const data: AskResponse = await response.json();
      setAskResponse(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute multi-agent orchestration.");
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-6">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              LangGraph Multi-Agent Orchestrator
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Phase 10 Engine
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Planner Agent automatically routes questions across database SQL, document RAG, and analytical capabilities.
            </p>
          </div>
        </div>

        <form onSubmit={handleAsk} className="relative">
          <div className="flex items-center rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 shadow-inner focus-within:border-indigo-500 transition-colors">
            <Sparkles className="h-5 w-5 text-indigo-400 mr-3 shrink-0" />
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask any question (e.g. 'What was revenue last quarter and what does our return policy say?')..."
              className="w-full bg-transparent text-sm text-slate-200 placeholder-slate-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={isExecuting || !question.trim()}
              className="ml-3 inline-flex items-center space-x-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-2 text-xs font-bold text-white transition-colors disabled:opacity-50"
            >
              {isExecuting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span>Ask Intelligence</span>
            </button>
          </div>
        </form>

        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-start space-x-3">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Orchestration Error</p>
              <p className="text-rose-300/80 font-mono text-[11px] leading-relaxed">{errorMessage}</p>
            </div>
          </div>
        )}
      </div>

      {askResponse && (
        <div className="space-y-6">
          {/* Planner Card */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Planner Execution Strategy</h3>
              </div>
              <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
                <Clock className="h-3.5 w-3.5 text-indigo-400" />
                <span>{askResponse.execution_time_ms} ms</span>
              </div>
            </div>

            {/* Capability Badges */}
            <div className="flex flex-wrap gap-2">
              <span className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 border ${
                askResponse.plan.requires_sql
                  ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30 font-bold"
                  : "bg-slate-950 text-slate-600 border-slate-800"
              }`}>
                <Database className="h-3.5 w-3.5" />
                SQL Agent {askResponse.plan.requires_sql ? "✓ Active" : "Off"}
              </span>

              <span className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 border ${
                askResponse.plan.requires_rag
                  ? "bg-amber-500/10 text-amber-400 border-amber-500/30 font-bold"
                  : "bg-slate-950 text-slate-600 border-slate-800"
              }`}>
                <FileText className="h-3.5 w-3.5" />
                RAG Search {askResponse.plan.requires_rag ? "✓ Active" : "Off"}
              </span>

              <span className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 border ${
                askResponse.plan.requires_analytics
                  ? "bg-purple-500/10 text-purple-400 border-purple-500/30"
                  : "bg-slate-950 text-slate-600 border-slate-800"
              }`}>
                <LineChart className="h-3.5 w-3.5" />
                Analytics Engine {askResponse.plan.requires_analytics ? "✓ Active" : "Off"}
              </span>

              <span className={`px-2.5 py-1 rounded-lg text-xs font-mono flex items-center gap-1.5 border ${
                askResponse.plan.requires_visualization
                  ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                  : "bg-slate-950 text-slate-600 border-slate-800"
              }`}>
                <PieChart className="h-3.5 w-3.5" />
                Visualization Engine {askResponse.plan.requires_visualization ? "✓ Active" : "Off"}
              </span>
            </div>

            <p className="text-xs text-slate-300 font-mono bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <span className="text-indigo-400 font-semibold">Planner Reasoning: </span>
              {askResponse.plan.reason}
            </p>
          </div>

          {/* Phase 13 Validation & Safety Audit Card */}
          {askResponse.results.validation && (
            <div className="p-6 rounded-2xl border border-emerald-500/30 bg-slate-900/40 backdrop-blur space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Validation & Guardrail Safety Audit</h3>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold border ${
                    askResponse.results.validation.action === "pass"
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                      : askResponse.results.validation.action === "flag"
                      ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                      : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                  }`}>
                    {(askResponse.results.validation.confidence_score * 100).toFixed(0)}% Confidence ({askResponse.results.validation.action.toUpperCase()})
                  </span>
                </div>
              </div>

              {/* Validation Check Status Matrix */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
                {askResponse.results.validation.checks.map((chk, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-slate-400 uppercase truncate">{chk.check_name.replace(/_/g, " ")}</span>
                      {chk.passed ? (
                        <span className="text-emerald-400 text-[10px] font-bold">✓ PASS</span>
                      ) : (
                        <span className="text-rose-400 text-[10px] font-bold">⚠ WARN</span>
                      )}
                    </div>
                    <div className="text-slate-300 text-[11px] truncate">{chk.message}</div>
                  </div>
                ))}
              </div>

              {/* Hallucination Alerts */}
              {askResponse.results.validation.hallucinations_detected.length > 0 && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5 text-rose-400">
                    <AlertCircle className="h-4 w-4" /> Detected Hallucination Warnings:
                  </p>
                  <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                    {askResponse.results.validation.hallucinations_detected.map((h, idx) => (
                      <li key={idx}>{h}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Contradiction Alerts */}
              {askResponse.results.validation.contradictions_detected.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5 text-amber-400">
                    <AlertCircle className="h-4 w-4" /> SQL vs Document Contradictions:
                  </p>
                  <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                    {askResponse.results.validation.contradictions_detected.map((c, idx) => (
                      <li key={idx}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* SQL Output Results */}
          {askResponse.results.sql && askResponse.results.sql.rows && (
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Database SQL Results</h3>
                  <span className="text-xs font-mono text-cyan-400">({askResponse.results.sql?.row_count ?? 0} rows)</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300">
                {askResponse.results.sql?.sql}
              </div>

              <div className="overflow-x-auto max-h-80 rounded-xl border border-slate-800">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 sticky top-0">
                    <tr>
                      {askResponse.results.sql?.columns?.map((col, idx) => (
                        <th key={idx} className="px-4 py-2.5 font-semibold">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300 bg-slate-950/40">
                    {askResponse.results.sql?.rows?.map((row, rowIdx) => (
                      <tr key={rowIdx} className="hover:bg-slate-900/40 transition-colors">
                        {askResponse.results.sql?.columns?.map((col, colIdx) => (
                          <td key={colIdx} className="px-4 py-2 whitespace-nowrap text-[11px]">
                            {row[col] !== null ? String(row[col]) : <span className="text-slate-600 italic">null</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* RAG Output Results */}
          {askResponse.results.rag && askResponse.results.rag.results && (
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-amber-400" />
                  <h3 className="text-sm font-bold text-white">Document RAG Retrieval Citations</h3>
                  <span className="text-xs font-mono text-amber-400">({askResponse.results.rag.results.length} chunks)</span>
                </div>
              </div>

              <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
                {askResponse.results.rag.results.map((chunk, idx) => (
                  <div key={chunk.chunk_id || idx} className="p-4 rounded-xl border border-slate-800 bg-slate-950/80 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-slate-400 text-[11px] border-b border-slate-800/80 pb-2">
                      <div className="flex items-center space-x-2">
                        <FileText className="h-3.5 w-3.5 text-amber-400" />
                        <span className="font-semibold text-slate-200">{chunk.filename}</span>
                        <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                          Chunk {chunk.chunk_index}
                        </span>
                      </div>
                      <span className="font-mono font-bold text-amber-400">
                        {(chunk.score * 100).toFixed(1)}% match
                      </span>
                    </div>
                    <p className="text-slate-300 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">
                      {chunk.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analytics Agent Execution Results */}
          {askResponse.results.analytics && askResponse.results.analytics.status !== "not_implemented" && (
            <div className="p-6 rounded-2xl border border-purple-500/30 bg-slate-900/40 backdrop-blur space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <LineChart className="h-4 w-4 text-purple-400" />
                  <h3 className="text-sm font-bold text-white">Analytics Agent Output</h3>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-semibold uppercase">
                    {askResponse.results.analytics.operation}
                  </span>
                </div>
                {askResponse.results.analytics.summary && (
                  <span className="text-xs font-mono text-slate-400">
                    Used {askResponse.results.analytics.summary.rows_used} / {askResponse.results.analytics.summary.rows_input} rows
                  </span>
                )}
              </div>

              {/* Scalar Metric Value display */}
              {askResponse.results.analytics.value !== undefined && askResponse.results.analytics.value !== null && (
                <div className="p-4 rounded-xl bg-purple-950/30 border border-purple-500/20 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-purple-300 font-medium uppercase tracking-wider block">
                      {askResponse.results.analytics.metric || askResponse.results.analytics.operation}
                    </span>
                    <span className="text-2xl font-black font-mono text-white">
                      {typeof askResponse.results.analytics.value === "number"
                        ? askResponse.results.analytics.value.toLocaleString()
                        : String(askResponse.results.analytics.value)}
                    </span>
                  </div>
                </div>
              )}

              {/* Grouped Aggregations display */}
              {askResponse.results.analytics.groups && askResponse.results.analytics.groups.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-400">Grouped Aggregations</span>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {askResponse.results.analytics.groups.map((g, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex flex-col justify-between">
                        <span className="text-[11px] text-slate-400 font-medium truncate">{g.group}</span>
                        <span className="text-sm font-bold font-mono text-purple-300">
                          {typeof g.value === "number" ? g.value.toLocaleString() : String(g.value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Time-Series display */}
              {askResponse.results.analytics.series && askResponse.results.analytics.series.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-400">Time-Series Trend</span>
                  <div className="max-h-48 overflow-y-auto space-y-1 pr-1 font-mono text-xs">
                    {askResponse.results.analytics.series.map((pt, idx) => (
                      <div key={idx} className="p-2 rounded bg-slate-950 border border-slate-800 flex justify-between items-center text-[11px]">
                        <span className="text-slate-400">{pt.period}</span>
                        <span className="text-purple-300 font-bold">
                          {typeof pt.value === "number" ? pt.value.toLocaleString() : String(pt.value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Natural Language Explanation */}
              {askResponse.results.analytics.explanation && (
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 italic">
                  &quot;{askResponse.results.analytics.explanation}&quot;
                </div>
              )}

              {/* Warnings */}
              {askResponse.results.analytics.summary?.warnings && askResponse.results.analytics.summary.warnings.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 space-y-1">
                  {askResponse.results.analytics.summary.warnings.map((w, idx) => (
                    <div key={idx} className="flex items-center space-x-1.5">
                      <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Visualization Agent Recharts Output */}
          {askResponse.results.visualization?.spec && (
            <RechartsRenderer
              spec={askResponse.results.visualization.spec}
              explanation={askResponse.results.visualization.explanation}
            />
          )}
        </div>
      )}
    </div>
  );
};
