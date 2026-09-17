export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-slate-950 text-slate-100">
      <div className="max-w-2xl w-full p-8 rounded-xl border border-slate-800 bg-slate-900/50 shadow-2xl backdrop-blur">
        <div className="flex items-center space-x-3 mb-6">
          <div className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Phase 1 — Project Foundation
          </span>
        </div>

        <h1 className="text-3xl font-bold tracking-tight text-white mb-3">
          EMBIP Platform Engine
        </h1>
        <p className="text-slate-400 text-sm mb-6 leading-relaxed">
          Enterprise Multi-Agent Business Intelligence Platform. The application container,
          monorepo layout, Next.js App Router, and FastAPI backend foundation are running.
        </p>

        <div className="grid grid-cols-2 gap-4 border-t border-slate-800 pt-6 text-left">
          <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-800">
            <p className="text-xs font-medium text-slate-400 uppercase">Frontend App</p>
            <p className="text-sm font-semibold text-emerald-400 mt-1">Next.js 14 (App Router)</p>
          </div>
          <div className="p-4 rounded-lg bg-slate-800/40 border border-slate-800">
            <p className="text-xs font-medium text-slate-400 uppercase">Backend Server</p>
            <p className="text-sm font-semibold text-emerald-400 mt-1">FastAPI (Python 3.11+)</p>
          </div>
        </div>

        <div className="mt-6 text-xs text-slate-500 text-center">
          EMBIP System Status: Foundation Ready & Verified
        </div>
      </div>
    </main>
  );
}
