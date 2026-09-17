import React from "react";
import { MessageSquare, GitBranch, Database, BarChart3, ShieldCheck, FileCheck } from "lucide-react";

export function HowItWorks() {
  const steps = [
    {
      icon: MessageSquare,
      title: "1. User Question",
      description: "User submits natural language question ('Why did Q2 net profit decline?').",
    },
    {
      icon: GitBranch,
      title: "2. Planner Decomposition",
      description: "Planner Agent formulates structured execution plan across database & docs.",
    },
    {
      icon: Database,
      title: "3. SQL & RAG Execution",
      description: "SQL Agent queries relational DB; Document Agent retrieves Qdrant vector chunks.",
    },
    {
      icon: BarChart3,
      title: "4. Analytics & Viz",
      description: "Analytics Agent computes variance; Visualization Agent formats Recharts JSON.",
    },
    {
      icon: ShieldCheck,
      title: "5. Validation Audit",
      description: "Validation Agent checks SQL safety, verifies metrics, and detects hallucinations.",
    },
    {
      icon: FileCheck,
      title: "6. Business Insight",
      description: "Report Generator delivers executive markdown report with live SSE streaming.",
    },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-slate-900/30 border-t border-slate-800/80">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            Execution Flow
          </h2>
          <h3 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            How EMBIP Answers Business Inquiries
          </h3>
          <p className="mt-3 text-sm text-slate-400">
            A transparent, deterministic workflow transforming raw questions into verified executive answers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className="relative p-6 rounded-xl border border-slate-800 bg-slate-950/80 shadow-md space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/10 text-blue-400 border border-blue-500/20">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-500">
                    STEP 0{idx + 1}
                  </span>
                </div>
                <h4 className="text-base font-semibold text-white">{step.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
