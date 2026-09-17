import React from "react";
import { ShieldCheck, Lock, Key, FileCheck, Eye, Activity } from "lucide-react";

export function SecuritySection() {
  const pillars = [
    {
      icon: Lock,
      title: "Supabase RLS Multi-Tenancy",
      description: "Row Level Security policies enforce strict organization and workspace data boundaries at the database level.",
    },
    {
      icon: ShieldCheck,
      title: "AST SELECT-Only SQL Parser",
      description: "sqlglot parser auditing rejects mutating operations (INSERT, UPDATE, DELETE, DROP, TRUNCATE) before DB execution.",
    },
    {
      icon: Key,
      title: "Role-Based Access Control (RBAC)",
      description: "Fine-grained permissions across ADMIN, MANAGER, ANALYST, and VIEWER roles enforced on backend endpoints.",
    },
    {
      icon: FileCheck,
      title: "Payload-Filtered Vector Store",
      description: "Qdrant vector search requires mandatory tenant payload filtering for document chunk retrieval.",
    },
    {
      icon: Eye,
      title: "Full Auditability & Evidence",
      description: "Every answer includes inspectable SQL queries, raw data rows, and document citations.",
    },
    {
      icon: Activity,
      title: "Query Timeouts & Hard Limits",
      description: "Automatic limit injection (LIMIT 1000) and strict session statement timeouts prevent database overload.",
    },
  ];

  return (
    <section id="security" className="py-20 bg-slate-900/40 border-t border-slate-800/80">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            Enterprise Governance
          </h2>
          <h3 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Built-In Security & Guardrails
          </h3>
          <p className="mt-3 text-sm text-slate-400">
            Enterprise decision support designed around non-negotiable security principles.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pillars.map((pillar, idx) => {
            const Icon = pillar.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-xl border border-slate-800 bg-slate-950/80 shadow-md space-y-3"
              >
                <div className="inline-flex p-2.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  <Icon className="h-5 w-5" />
                </div>
                <h4 className="text-base font-semibold text-white">{pillar.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {pillar.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
