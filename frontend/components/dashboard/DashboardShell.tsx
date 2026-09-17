import React from "react";
import Link from "next/link";
import {
  DollarSign,
  ShoppingCart,
  TrendingUp,
  Store as StoreIcon,
  Sparkles,
  FileSpreadsheet,
  ArrowUpRight,
  Database,
} from "lucide-react";

export function DashboardShell() {
  const kpis = [
    {
      title: "Total Revenue",
      value: "$0.00",
      change: "Phase 3/4 Shell",
      icon: DollarSign,
      color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    },
    {
      title: "Sales Transactions",
      value: "0",
      change: "Target: 100,000+",
      icon: ShoppingCart,
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      title: "Net Profit Margin",
      value: "0.0%",
      change: "Analytics Engine",
      icon: TrendingUp,
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
    {
      title: "Active Stores",
      value: "10 Planned",
      change: "NovaMart Domain",
      icon: StoreIcon,
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Overview Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            NovaMart Retail Solutions Workspace
          </h2>
          <p className="mt-1 text-xs text-slate-400">
            Phase 4 Product Shell Running — Enterprise BI & Multi-Agent Interface Prepared
          </p>
        </div>

        <Link
          href="/ask"
          className="inline-flex items-center space-x-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-500 shadow-md shadow-blue-600/20 transition"
        >
          <Sparkles className="h-4 w-4" />
          <span>Ask AI Agent</span>
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 shadow-lg space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{kpi.title}</span>
                <div className={`p-2 rounded-lg border ${kpi.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
              </div>

              <div>
                <div className="text-2xl font-extrabold text-white tracking-tight">
                  {kpi.value}
                </div>
                <div className="mt-1 text-[11px] text-slate-500 flex items-center space-x-1">
                  <Database className="h-3 w-3 text-slate-500" />
                  <span>{kpi.change}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Analytical Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Analytics Chart Placeholder */}
        <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-800 bg-slate-900/40 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-white">Revenue & Profit Overview</h3>
              <span className="text-[10px] font-mono text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                Recharts Chart Placeholder
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Interactive visualization engine ready for Phase 5 data ingestion.
            </p>
          </div>

          <div className="my-12 flex flex-col items-center justify-center p-8 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 text-center">
            <Database className="h-8 w-8 text-slate-600 mb-2" />
            <span className="text-xs font-semibold text-slate-300">Data Visualization Ready</span>
            <span className="text-[11px] text-slate-500 mt-1">
              Connect NovaMart Retail sales data to generate dynamic Recharts graphics
            </span>
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs text-slate-500">
            <span>Source: NovaMart Database Schema</span>
            <Link href="/analytics" className="text-blue-400 hover:underline inline-flex items-center space-x-1">
              <span>View Analytics</span>
              <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>

        {/* Recent AI Queries & Reports Side Column */}
        <div className="space-y-6">
          {/* Recent AI Queries Placeholder */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 shadow-lg space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                <Sparkles className="h-4 w-4 text-blue-400" />
                <span>Recent Natural Language Queries</span>
              </h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-lg border border-slate-800/80 bg-slate-950/80 text-xs text-slate-300">
                &quot;Why did our net profit margin decrease in Q2?&quot;
                <span className="block text-[10px] text-slate-500 mt-1">Multi-Agent Planner Flow</span>
              </div>
              <div className="p-3 rounded-lg border border-slate-800/80 bg-slate-950/80 text-xs text-slate-300">
                &quot;Top 5 performing stores by total sales revenue&quot;
                <span className="block text-[10px] text-slate-500 mt-1">SQL Agent Execution</span>
              </div>
            </div>
          </div>

          {/* Recent Reports Placeholder */}
          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/40 shadow-lg space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
                <span>Executive Reports</span>
              </h3>
            </div>
            <div className="p-4 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 text-center text-xs text-slate-400">
              Generated Markdown reports will appear here in Phase 15.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
