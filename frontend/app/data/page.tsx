import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { AppShell } from "@/components/layout/AppShell";
import { Database, Plus, Server } from "lucide-react";

export default async function DataPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?redirect=/data");
  }

  const role = (user.user_metadata?.role as string) || "Analyst";

  return (
    <AppShell user={user} role={role} title="Enterprise Data Sources">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Database className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Data Connections & Schema Registry</h2>
                <p className="text-xs text-slate-400">PostgreSQL, SQL Server, Snowflake, & CSV Data Ingestion</p>
              </div>
            </div>
            <button disabled className="inline-flex items-center space-x-2 rounded-xl bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-500 cursor-not-allowed">
              <Plus className="h-4 w-4" />
              <span>Connect Database</span>
            </button>
          </div>

          <div className="p-12 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 text-center">
            <Server className="h-10 w-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-200">Data Management Shell Prepared</h3>
            <p className="mt-1 text-xs text-slate-500 max-w-md mx-auto">
              SQL connectors, schema introspectors, and text-to-SQL agent validation engines will connect in Phase 7.
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
