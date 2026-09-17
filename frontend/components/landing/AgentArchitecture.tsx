import React from "react";
import { Cpu, Server, Lock, Layers } from "lucide-react";

export function AgentArchitecture() {
  const agents = [
    { name: "1. Planner Agent", role: "Query decomposition & plan generation" },
    { name: "2. SQL Agent", role: "Parametrized SELECT query generation" },
    { name: "3. Document/RAG Agent", role: "Payload-filtered Qdrant vector retrieval" },
    { name: "4. Analytics Agent", role: "Pandas/NumPy statistical computations" },
    { name: "5. Visualization Agent", role: "Recharts JSON chart configuration" },
    { name: "6. Validation Agent", role: "AST safety audit & hallucination verification" },
    { name: "7. Report Generator", role: "Markdown executive summary synthesis" },
  ];

  return (
    <section id="architecture" className="py-20 bg-slate-950">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-blue-400 mb-2">
            Multi-Agent System
          </h2>
          <h3 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            7 Specialized Agents, 1 Coordinated Platform
          </h3>
          <p className="mt-3 text-sm text-slate-400">
            Powered by a Centralized LLMService — eliminating credential fragmentation while enforcing strict context boundaries.
          </p>
        </div>

        <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
          {/* Centralized LLM Service Banner */}
          <div className="flex flex-col sm:flex-row items-center justify-between p-4 rounded-xl border border-blue-500/30 bg-blue-600/10 mb-8 gap-4">
            <div className="flex items-center space-x-3">
              <Cpu className="h-6 w-6 text-blue-400 shrink-0" />
              <div>
                <h4 className="text-sm font-semibold text-white">Centralized LLMService Wrapper</h4>
                <p className="text-xs text-slate-400">Unified credentials, token usage telemetry, and model provider abstraction (OpenAI / Claude / Azure).</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-xs font-mono text-blue-300 bg-blue-950/60 px-3 py-1.5 rounded-lg border border-blue-800">
              <Lock className="h-3.5 w-3.5" />
              <span>Single Credential Point</span>
            </div>
          </div>

          {/* Grid of 7 Agents */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {agents.map((agent, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/80 hover:border-slate-700 transition"
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Layers className="h-4 w-4 text-indigo-400" />
                  <h5 className="text-xs font-semibold text-white">{agent.name}</h5>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  {agent.role}
                </p>
              </div>
            ))}

            <div className="p-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/20 flex flex-col justify-center items-center text-center">
              <Server className="h-5 w-5 text-slate-500 mb-1" />
              <span className="text-xs font-semibold text-slate-400">LangGraph StateGraph</span>
              <span className="text-[10px] text-slate-500 mt-0.5">Stateful Graph Orchestrator</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
