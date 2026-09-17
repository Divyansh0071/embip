import React from "react";
import { CheckCircle2, ShieldCheck, Zap } from "lucide-react";

export function ValueProp() {
  return (
    <section className="bg-slate-900/40 border-y border-slate-800/80 py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-950/60 shadow-lg space-y-3">
            <div className="inline-flex p-2.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Zap className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Natural Language Analysis</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ask complex business questions in plain English. The platform decomposes inquiries into structured data queries and document context retrieval.
            </p>
          </div>

          <div className="p-6 rounded-xl border border-slate-800 bg-slate-950/60 shadow-lg space-y-3">
            <div className="inline-flex p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Evidence-Backed Insights</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every executive summary is backed by inspectable SQL query results, cited document chunks, and interactive Recharts visualizations.
            </p>
          </div>

          <div className="p-6 rounded-xl border border-slate-800 bg-slate-950/60 shadow-lg space-y-3">
            <div className="inline-flex p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Enterprise Security & Isolation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Strict AST-based SELECT-only SQL validation, Supabase Row Level Security (RLS), and Qdrant payload filters guarantee multi-tenant data boundaries.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
