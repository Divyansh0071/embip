import React from "react";
import Link from "next/link";
import { ArrowRight, Bot, ShieldCheck, Database, FileText, BarChart3 } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-slate-950 pt-16 pb-20 md:pt-24 md:pb-28">
      {/* Background Subtle Gradient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-blue-600/10 blur-[120px] pointer-events-none rounded-full" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-3.5 py-1 text-xs font-semibold text-blue-400">
            <Bot className="h-3.5 w-3.5 text-blue-400 animate-pulse" />
            <span>Multi-Agent AI Architecture Specification</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl md:text-6xl leading-tight">
            Enterprise Intelligence, <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
              Orchestrated by AI Agents.
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-base text-slate-300 sm:text-lg leading-relaxed max-w-2xl mx-auto">
            EMBIP bridges structured relational data, corporate documents, statistical algorithms, and specialized AI agents into a single, evidence-backed decision intelligence platform.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4">
            <Link
              href="/signup"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:bg-blue-500"
            >
              <span>Get Started</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="#capabilities"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 rounded-lg border border-slate-800 bg-slate-900/80 px-6 py-3 text-sm font-medium text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              <span>Explore Platform</span>
            </a>
          </div>

          {/* Highlights Footer */}
          <div className="pt-10 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-2xl mx-auto border-t border-slate-800/80 text-left">
            <div className="flex items-center space-x-2.5">
              <Database className="h-4 w-4 text-blue-400 shrink-0" />
              <span className="text-xs text-slate-300 font-medium">SELECT-Only SQL Safety</span>
            </div>
            <div className="flex items-center space-x-2.5">
              <FileText className="h-4 w-4 text-emerald-400 shrink-0" />
              <span className="text-xs text-slate-300 font-medium">Document RAG (Qdrant)</span>
            </div>
            <div className="flex items-center space-x-2.5">
              <BarChart3 className="h-4 w-4 text-purple-400 shrink-0" />
              <span className="text-xs text-slate-300 font-medium">Pandas / NumPy Engine</span>
            </div>
            <div className="flex items-center space-x-2.5">
              <ShieldCheck className="h-4 w-4 text-indigo-400 shrink-0" />
              <span className="text-xs text-slate-300 font-medium">Supabase RLS Isolation</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
