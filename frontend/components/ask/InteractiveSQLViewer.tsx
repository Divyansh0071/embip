"use client";

import React, { useState } from "react";
import { Database, Copy, Check, ChevronDown, ChevronUp, Code2, Table as TableIcon } from "lucide-react";

interface InteractiveSQLViewerProps {
  sql: string;
  tablesUsed?: string[];
  columns?: string[];
  rowCount?: number;
  executionTimeMs?: number;
}

export const InteractiveSQLViewer: React.FC<InteractiveSQLViewerProps> = ({
  sql,
  tablesUsed = [],
  columns = [],
  rowCount = 0,
  executionTimeMs = 0,
}) => {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-6 rounded-2xl border border-cyan-500/30 bg-slate-900/40 backdrop-blur space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Database className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white">Database Read-Only SQL Query</h3>
          <span className="text-xs font-mono text-cyan-400">({rowCount} rows)</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopy}
            className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[11px] font-mono text-slate-300 transition-colors"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3 text-slate-400" />}
            <span>{copied ? "Copied" : "Copy SQL"}</span>
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 transition-colors"
          >
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="space-y-3">
          {/* SQL Query Box */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-cyan-300 leading-relaxed overflow-x-auto">
            <pre className="whitespace-pre-wrap break-words">{sql}</pre>
          </div>

          {/* Schema & Tables Inspector */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 font-mono">
            {tablesUsed.length > 0 && (
              <div className="flex items-center space-x-1">
                <TableIcon className="h-3.5 w-3.5 text-slate-500" />
                <span>Tables:</span>
                {tablesUsed.map((t, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">
                    {t}
                  </span>
                ))}
              </div>
            )}

            {columns.length > 0 && (
              <div className="flex items-center space-x-1">
                <Code2 className="h-3.5 w-3.5 text-slate-500" />
                <span>Columns:</span>
                <span className="text-slate-300">{columns.join(", ")}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
