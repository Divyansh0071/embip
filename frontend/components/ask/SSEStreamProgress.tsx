"use client";

import React from "react";
import {
  Sparkles,
  Database,
  FileText,
  LineChart,
  PieChart,
  ShieldCheck,
  FileDown,
  CheckCircle2,
  Loader2,
  Clock,
} from "lucide-react";

export interface StreamNodeState {
  node: string;
  label: string;
  icon: React.ElementType;
  status: "idle" | "running" | "completed" | "error";
  duration_ms?: number;
}

interface SSEStreamProgressProps {
  activeNode: string | null;
  completedNodes: string[];
  isStreaming: boolean;
  elapsedMs: number;
}

export const SSEStreamProgress: React.FC<SSEStreamProgressProps> = ({
  activeNode,
  completedNodes,
  isStreaming,
  elapsedMs,
}) => {
  const nodes: Array<{ id: string; label: string; icon: React.ElementType }> = [
    { id: "planner", label: "Planner Intent", icon: Sparkles },
    { id: "sql_node", label: "SQL Database Query", icon: Database },
    { id: "rag_node", label: "RAG Vector Search", icon: FileText },
    { id: "analytics_node", label: "Analytics Engine", icon: LineChart },
    { id: "visualization_node", label: "Chart Spec Engine", icon: PieChart },
    { id: "validation_node", label: "Guardrail Audit", icon: ShieldCheck },
    { id: "report_node", label: "Executive Report", icon: FileDown },
  ];

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-4 w-4 text-indigo-400" />
          <h3 className="text-sm font-bold text-white">Live Multi-Agent Event Stream</h3>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
          <Clock className="h-3.5 w-3.5 text-indigo-400" />
          <span>{elapsedMs} ms</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
        {nodes.map((n) => {
          const Icon = n.icon;
          const isDone = completedNodes.includes(n.id);
          const isActive = activeNode === n.id;

          let badgeStyle = "bg-slate-950 text-slate-500 border-slate-800/80";
          if (isDone) {
            badgeStyle = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
          } else if (isActive) {
            badgeStyle = "bg-indigo-500/10 text-indigo-400 border-indigo-500/40 animate-pulse";
          }

          return (
            <div
              key={n.id}
              className={`p-3 rounded-xl border flex flex-col items-center text-center space-y-1.5 transition-all ${badgeStyle}`}
            >
              <div className="flex items-center justify-center space-x-1">
                {isActive ? (
                  <Loader2 className="h-4 w-4 animate-spin text-indigo-400 shrink-0" />
                ) : isDone ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                ) : (
                  <Icon className="h-4 w-4 text-slate-500 shrink-0" />
                )}
              </div>
              <span className="text-[11px] font-mono font-medium leading-tight">
                {n.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
