"use client";

import React, { useState } from "react";
import {
  FileText,
  PieChart,
  Database,
  Table as TableIcon,
  ShieldCheck,
  LineChart,
  FileDown,
} from "lucide-react";
import { RechartsRenderer, RechartsSpec } from "../visualization/RechartsRenderer";
import { ReportView, ReportDataProps } from "../reports/ReportView";
import { InteractiveSQLViewer } from "./InteractiveSQLViewer";

interface MultiTabIntelligenceViewProps {
  askResponse: {
    request_id: string;
    question: string;
    status: string;
    plan: any;
    results: {
      sql?: any;
      rag?: any;
      analytics?: any;
      visualization?: any;
      validation?: any;
      report?: ReportDataProps | null;
    };
    errors: string[];
    execution_time_ms: number;
  };
  getAuthToken: () => Promise<string | null>;
}

export const MultiTabIntelligenceView: React.FC<MultiTabIntelligenceViewProps> = ({
  askResponse,
  getAuthToken,
}) => {
  const [activeTab, setActiveTab] = useState<"report" | "chart" | "sql" | "table" | "audit">("report");

  const results = askResponse.results;
  const hasReport = !!results.report;
  const hasChart = !!results.visualization?.spec;
  const hasSQL = !!results.sql?.sql;
  const hasTable = !!(results.sql?.rows && results.sql.rows.length > 0);
  const hasAudit = !!results.validation;

  return (
    <div className="space-y-6">
      {/* Navigation Tab Bar */}
      <div className="flex items-center space-x-1 p-1.5 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs overflow-x-auto">
        {hasReport && (
          <button
            onClick={() => setActiveTab("report")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold transition-colors ${
              activeTab === "report"
                ? "bg-indigo-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <FileDown className="h-4 w-4" />
            <span>Executive Report</span>
          </button>
        )}

        {hasChart && (
          <button
            onClick={() => setActiveTab("chart")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold transition-colors ${
              activeTab === "chart"
                ? "bg-rose-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <PieChart className="h-4 w-4" />
            <span>Visual Analytics</span>
          </button>
        )}

        {hasSQL && (
          <button
            onClick={() => setActiveTab("sql")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold transition-colors ${
              activeTab === "sql"
                ? "bg-cyan-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <Database className="h-4 w-4" />
            <span>SQL Explorer</span>
          </button>
        )}

        {hasTable && (
          <button
            onClick={() => setActiveTab("table")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold transition-colors ${
              activeTab === "table"
                ? "bg-purple-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <TableIcon className="h-4 w-4" />
            <span>Data Grid ({results.sql.rows.length})</span>
          </button>
        )}

        {hasAudit && (
          <button
            onClick={() => setActiveTab("audit")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-bold transition-colors ${
              activeTab === "audit"
                ? "bg-emerald-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <ShieldCheck className="h-4 w-4" />
            <span>Guardrail Audit</span>
          </button>
        )}
      </div>

      {/* Tab Content Panels */}
      <div>
        {activeTab === "report" && hasReport && (
          <ReportView report={results.report!} getAuthToken={getAuthToken} />
        )}

        {activeTab === "chart" && hasChart && (
          <RechartsRenderer
            spec={results.visualization.spec}
            explanation={results.visualization.explanation}
          />
        )}

        {activeTab === "sql" && hasSQL && (
          <InteractiveSQLViewer
            sql={results.sql.sql}
            tablesUsed={results.sql.tables_used}
            columns={results.sql.columns}
            rowCount={results.sql.row_count}
            executionTimeMs={results.sql.execution_time_ms}
          />
        )}

        {activeTab === "table" && hasTable && (
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TableIcon className="h-4 w-4 text-purple-400" />
              Tabular Dataset Preview
            </h3>
            <div className="overflow-x-auto max-h-96 rounded-xl border border-slate-800">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 sticky top-0">
                  <tr>
                    {results.sql.columns?.map((col: string, idx: number) => (
                      <th key={idx} className="px-4 py-2.5 font-semibold">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300 bg-slate-950/40">
                  {results.sql.rows?.map((row: any, rowIdx: number) => (
                    <tr key={rowIdx} className="hover:bg-slate-900/40 transition-colors">
                      {results.sql.columns?.map((col: string, colIdx: number) => (
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

        {activeTab === "audit" && hasAudit && (
          <div className="p-6 rounded-2xl border border-emerald-500/30 bg-slate-900/40 backdrop-blur space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Validation Audit Matrix</h3>
              </div>
              <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {(results.validation.confidence_score * 100).toFixed(0)}% Confidence Verified
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
              {results.validation.checks?.map((chk: any, idx: number) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-slate-400 uppercase truncate">{chk.check_name.replace(/_/g, " ")}</span>
                    <span className={chk.passed ? "text-emerald-400 text-[10px] font-bold" : "text-rose-400 text-[10px] font-bold"}>
                      {chk.passed ? "✓ PASS" : "⚠ WARN"}
                    </span>
                  </div>
                  <div className="text-slate-300 text-[11px] truncate">{chk.message}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
