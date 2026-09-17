import React from "react";
import { Bot, Code2, FileSearch, Calculator, PieChart, ShieldCheck, FileSpreadsheet } from "lucide-react";

export function Capabilities() {
  const capabilities = [
    {
      icon: Bot,
      color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
      title: "1. Multi-Agent Orchestration",
      description: "Designed to coordinate specialized AI agents through a stateful LangGraph execution engine for multi-step reasoning.",
    },
    {
      icon: Code2,
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
      title: "2. Natural Language to SQL",
      description: "Converts plain language questions into parametrized SELECT queries validated by an AST safety parser before database execution.",
    },
    {
      icon: FileSearch,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
      title: "3. Document Intelligence & RAG",
      description: "Connects corporate PDFs, DOCXs, and sheets to Qdrant Cloud vector search with strict payload-filtered tenant isolation.",
    },
    {
      icon: Calculator,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
      title: "4. Statistical & Trend Analytics",
      description: "Offloads numerical variance, growth rate, and margin calculations to Pandas, NumPy, and scikit-learn analytics modules.",
    },
    {
      icon: PieChart,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
      title: "5. Dynamic Data Visualization",
      description: "Automatically selects optimal chart types (Bar, Line, Pie, Scatter, Area) and generates Recharts JSON configurations.",
    },
    {
      icon: ShieldCheck,
      color: "text-red-400 bg-red-500/10 border-red-500/20",
      title: "6. Validation & Fact Checking",
      description: "Audits AI outputs against raw query results to prevent hallucinations and enforce strict compliance rules.",
    },
    {
      icon: FileSpreadsheet,
      color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
      title: "7. Automated Business Reports",
      description: "Synthesizes multi-part executive reports complete with executive summaries, metrics, charts, and cited document links.",
    },
  ];

  return (
    <section id="capabilities" className="py-20 bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            Platform Capabilities
          </h2>
          <h3 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Architected for Enterprise Intelligence
          </h3>
          <p className="mt-3 text-sm text-slate-400">
            EMBIP integrates 7 specialized functional modules designed to deliver autonomous, verified decision support.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {capabilities.map((item, index) => {
            const IconComponent = item.icon;
            return (
              <div
                key={index}
                className="p-6 rounded-xl border border-slate-800/80 bg-slate-900/40 hover:bg-slate-900/80 transition duration-200 shadow-md space-y-3"
              >
                <div className={`inline-flex p-2.5 rounded-lg border ${item.color}`}>
                  <IconComponent className="h-5 w-5" />
                </div>
                <h4 className="text-base font-semibold text-white">{item.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {item.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
