"use client";

import React, { useState } from "react";
import { Database, Play, Code2, Table, Clock, AlertCircle, Loader2, Sparkles, CheckCircle2 } from "lucide-react";

interface SQLQueryResponse {
  question: string;
  sql: string;
  explanation: string;
  tables_used: string[];
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  execution_time_ms: number;
  status: string;
}

interface SQLQueryTesterProps {
  getAuthToken: () => Promise<string | null>;
}

export const SQLQueryTester: React.FC<SQLQueryTesterProps> = ({ getAuthToken }) => {
  const [question, setQuestion] = useState("");
  const [maxRows, setMaxRows] = useState(50);
  const [queryResponse, setQueryResponse] = useState<SQLQueryResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsExecuting(true);
    setErrorMessage(null);
    setQueryResponse(null);

    try {
      const token = await getAuthToken();
      if (!token) {
        setErrorMessage("Authentication session expired. Please log in.");
        setIsExecuting(false);
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/sql/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question: question.trim(),
          max_rows: maxRows,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Query execution failed with HTTP ${response.status}`);
      }

      const data: SQLQueryResponse = await response.json();
      setQueryResponse(data);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute natural language SQL query.");
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Natural Language SQL Agent
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                AST Read-Only
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Translates business questions into safe PostgreSQL queries and fetches live database results.
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleExecute} className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Sparkles className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a business question e.g. 'What was total revenue by store last year?'..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={maxRows}
              onChange={(e) => setMaxRows(Number(e.target.value))}
              className="py-2.5 px-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
            >
              <option value={10}>Max 10 rows</option>
              <option value={50}>Max 50 rows</option>
              <option value={100}>Max 100 rows</option>
              <option value={500}>Max 500 rows</option>
            </select>

            <button
              type="submit"
              disabled={isExecuting || !question.trim()}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-colors disabled:opacity-50"
            >
              {isExecuting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4 fill-slate-950" />
              )}
              <span>Execute SQL</span>
            </button>
          </div>
        </div>
      </form>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-start space-x-3">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold">Query Execution Failed</p>
            <p className="text-rose-300/80 font-mono text-[11px] leading-relaxed">{errorMessage}</p>
          </div>
        </div>
      )}

      {queryResponse && (
        <div className="space-y-5 pt-2">
          {/* Metrics bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-mono">Row Count</span>
              <span className="text-sm font-bold text-cyan-400">{queryResponse.row_count} rows</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-mono">Execution Time</span>
              <span className="text-sm font-bold text-emerald-400">{queryResponse.execution_time_ms} ms</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 col-span-2">
              <span className="text-[10px] text-slate-400 block font-mono">Tables Referenced</span>
              <div className="flex flex-wrap gap-1 mt-0.5">
                {queryResponse.tables_used.map((t, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Explanation */}
          <div className="p-3.5 rounded-xl bg-cyan-500/5 border border-cyan-500/20 text-xs text-slate-300 flex items-start space-x-3">
            <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-cyan-300">Agent Explanation: </span>
              <span>{queryResponse.explanation}</span>
            </div>
          </div>

          {/* SQL Code Box */}
          <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-slate-900/60 text-xs text-slate-400">
              <div className="flex items-center space-x-2">
                <Code2 className="h-3.5 w-3.5 text-cyan-400" />
                <span className="font-mono text-[11px] font-semibold text-slate-300">Generated PostgreSQL Query</span>
              </div>
            </div>
            <pre className="p-4 text-xs font-mono text-cyan-300 leading-relaxed overflow-x-auto">
              {queryResponse.sql}
            </pre>
          </div>

          {/* Results Table */}
          {queryResponse.rows.length > 0 ? (
            <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden space-y-2">
              <div className="flex items-center space-x-2 px-4 py-2.5 border-b border-slate-800 bg-slate-900/60 text-xs text-slate-300">
                <Table className="h-3.5 w-3.5 text-emerald-400" />
                <span className="font-semibold">Query Result Dataset</span>
              </div>

              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 sticky top-0">
                    <tr>
                      {queryResponse.columns.map((col, idx) => (
                        <th key={idx} className="px-4 py-2.5 font-semibold whitespace-nowrap">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {queryResponse.rows.map((row, rowIdx) => (
                      <tr key={rowIdx} className="hover:bg-slate-900/40 transition-colors">
                        {queryResponse.columns.map((col, colIdx) => (
                          <td key={colIdx} className="px-4 py-2.5 whitespace-nowrap text-[11px]">
                            {row[col] !== null ? String(row[col]) : <span className="text-slate-600 italic">null</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-6 rounded-xl border border-slate-800 bg-slate-950 text-center text-slate-500 text-xs font-mono">
              No matching database records returned for this query.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
