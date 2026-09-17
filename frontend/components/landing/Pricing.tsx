import React from "react";
import Link from "next/link";
import { Check, ArrowRight } from "lucide-react";

export function Pricing() {
  const plans = [
    {
      name: "Starter",
      tagline: "For small teams starting with AI analytics",
      price: "$49",
      period: "/month",
      features: [
        "Up to 5 Workspace Users",
        "Core Multi-Agent NL-to-SQL Querying",
        "Basic Visualizations (Recharts)",
        "SELECT-Only Security Guardrails",
        "Community Support",
      ],
      cta: "Start Free Trial",
      highlight: false,
    },
    {
      name: "Business",
      tagline: "For growing teams needing RAG & reports",
      price: "$199",
      period: "/month",
      features: [
        "Up to 25 Workspace Users",
        "Full Multi-Agent Orchestration (7 Agents)",
        "Document RAG (PDF, DOCX, CSV, XLSX)",
        "Pandas/NumPy Statistical Analytics",
        "Automated Markdown Report Generation",
        "Priority Email Support",
      ],
      cta: "Get Started with Business",
      highlight: true,
    },
    {
      name: "Enterprise",
      tagline: "For large enterprises requiring custom controls",
      price: "Custom",
      period: "",
      features: [
        "Unlimited Organization Users",
        "Custom Roles & Workspace RBAC",
        "Dedicated Supabase RLS Schemas",
        "Qdrant Cloud Custom Vector Indexing",
        "SAML/SSO Authentication Connectors",
        "Dedicated Account Manager & SLA",
      ],
      cta: "Contact Enterprise Sales",
      highlight: false,
    },
  ];

  return (
    <section id="pricing" className="py-20 bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            Illustrative Tier Architecture
          </h2>
          <h3 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Flexible Plans for Teams of Any Scale
          </h3>
          <p className="mt-3 text-sm text-slate-400">
            Planned commercial pricing tiers tailored for enterprise BI governance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`relative flex flex-col justify-between p-8 rounded-2xl border transition duration-200 shadow-xl ${
                plan.highlight
                  ? "border-blue-500 bg-slate-900/90 shadow-blue-500/10 ring-1 ring-blue-500"
                  : "border-slate-800 bg-slate-900/40 hover:border-slate-700"
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white shadow-md">
                  Most Popular
                </div>
              )}

              <div>
                <h4 className="text-lg font-bold text-white">{plan.name}</h4>
                <p className="mt-1 text-xs text-slate-400">{plan.tagline}</p>

                <div className="mt-6 flex items-baseline space-x-1">
                  <span className="text-4xl font-extrabold tracking-tight text-white">
                    {plan.price}
                  </span>
                  <span className="text-xs text-slate-400">{plan.period}</span>
                </div>

                <ul className="mt-6 space-y-3 border-t border-slate-800/80 pt-6">
                  {plan.features.map((feature, fIdx) => (
                    <li key={fIdx} className="flex items-start space-x-3 text-xs text-slate-300">
                      <Check className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-8 pt-4">
                <Link
                  href="/signup"
                  className={`w-full inline-flex items-center justify-center space-x-2 rounded-lg px-4 py-2.5 text-xs font-semibold transition ${
                    plan.highlight
                      ? "bg-blue-600 text-white hover:bg-blue-500 shadow-md shadow-blue-600/20"
                      : "border border-slate-700 bg-slate-800 text-white hover:bg-slate-700"
                  }`}
                >
                  <span>{plan.cta}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>

        <p className="mt-8 text-center text-[11px] text-slate-500">
          * Note: Tier specifications reflect planned commercial platform packaging. All core capabilities are accessible in Phase 4 workspace previews.
        </p>
      </div>
    </section>
  );
}
