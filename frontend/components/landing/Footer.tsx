import React from "react";
import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 py-12 text-slate-400">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Col 1: Brand */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 font-bold text-white">
                <ShieldCheck className="h-4 w-4" />
              </div>
              <span className="font-bold text-white tracking-wide">EMBIP</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Enterprise Multi-Agent Business Intelligence Platform. Connecting SQL data, corporate documents, and AI agents into evidence-backed decision support.
            </p>
          </div>

          {/* Col 2: Platform */}
          <div>
            <h5 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">
              Platform
            </h5>
            <ul className="space-y-2 text-xs">
              <li><a href="#capabilities" className="hover:text-white transition">Capabilities</a></li>
              <li><a href="#how-it-works" className="hover:text-white transition">How It Works</a></li>
              <li><a href="#architecture" className="hover:text-white transition">Multi-Agent Architecture</a></li>
              <li><a href="#security" className="hover:text-white transition">Security & RLS</a></li>
              <li><a href="#pricing" className="hover:text-white transition">Pricing Tiers</a></li>
            </ul>
          </div>

          {/* Col 3: Authentication */}
          <div>
            <h5 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">
              Access & Auth
            </h5>
            <ul className="space-y-2 text-xs">
              <li><Link href="/login" className="hover:text-white transition">Sign In</Link></li>
              <li><Link href="/signup" className="hover:text-white transition">Register Organization</Link></li>
              <li><Link href="/dashboard" className="hover:text-white transition">Workspace Dashboard</Link></li>
            </ul>
          </div>

          {/* Col 4: Technology Stack */}
          <div>
            <h5 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">
              Technology Architecture
            </h5>
            <ul className="space-y-2 text-xs text-slate-500">
              <li>Next.js 14 App Router & TypeScript</li>
              <li>Python FastAPI & Async SQLAlchemy</li>
              <li>Supabase PostgreSQL & Row Level Security</li>
              <li>Qdrant Cloud Vector Database</li>
              <li>LangGraph Multi-Agent Orchestration</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-900 pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} EMBIP Platform. All rights reserved.</p>
          <p className="text-[11px]">Designed for Enterprise Multi-Agent Decision Support.</p>
        </div>
      </div>
    </footer>
  );
}
