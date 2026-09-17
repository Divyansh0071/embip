import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { AppShell } from "@/components/layout/AppShell";
import { BarChart3, Database } from "lucide-react";

export default async function AnalyticsPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?redirect=/analytics");
  }

  const role = (user.user_metadata?.role as string) || "Analyst";

  return (
    <AppShell user={user} role={role} title="Advanced Analytics Engine">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
          <div className="flex items-center space-x-3 mb-3">
            <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <BarChart3 className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Statistical Analytics Module</h2>
              <p className="text-xs text-slate-400">Pandas, NumPy, & scikit-learn Computational Engine</p>
            </div>
          </div>

          <div className="my-8 p-12 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 text-center">
            <Database className="h-10 w-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-200">Analytics Workspace Shell Prepared</h3>
            <p className="mt-1 text-xs text-slate-500 max-w-md mx-auto">
              Statistical transformations, time-series variance analysis, and numerical forecasting algorithms will connect in Phase 11.
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
