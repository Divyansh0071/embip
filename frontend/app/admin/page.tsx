import React from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { AppShell } from "@/components/layout/AppShell";
import { ShieldAlert, ShieldCheck, ArrowLeft, Users, Settings, Key } from "lucide-react";


export default async function AdminPortalPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?redirect=/admin");
  }

  const userRole = (user.user_metadata?.role as string) || "Analyst";

  // Enforce server-side ADMIN role check
  if (userRole !== "ADMIN") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6 text-slate-100">
        <div className="w-full max-w-md rounded-2xl border border-red-500/30 bg-slate-900/60 p-8 text-center shadow-2xl backdrop-blur">
          <div className="mx-auto inline-flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/20 text-red-400 mb-4">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-bold text-white mb-2">403 — Access Denied</h1>
          <p className="text-xs text-slate-400 mb-6 leading-relaxed">
            The Administration Portal requires the <strong className="text-white">ADMIN</strong> role. Your current role is <span className="text-amber-400 font-mono">{userRole}</span>.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center space-x-2 rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-700 transition"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Return to Dashboard</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <AppShell user={user} role="ADMIN" title="System & RBAC Administration">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Administration & Access Control Portal</h2>
              <p className="text-xs text-slate-400">Manage organization settings, workspace roles, audit logs, and access permissions</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-5 shadow-lg">
              <div className="flex items-center space-x-3 mb-3">
                <Users className="h-5 w-5 text-blue-400" />
                <h3 className="text-sm font-semibold text-white">Workspace Members & RBAC</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Manage member roles: ADMIN, MANAGER, ANALYST, VIEWER. Server-side role validation enforced via Supabase JWT.
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-5 shadow-lg">
              <div className="flex items-center space-x-3 mb-3">
                <Key className="h-5 w-5 text-amber-400" />
                <h3 className="text-sm font-semibold text-white">API Keys & Tokens</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Configure server-side Supabase credentials, service role secrets, and JWT token expiry parameters.
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-5 shadow-lg">
              <div className="flex items-center space-x-3 mb-3">
                <Settings className="h-5 w-5 text-emerald-400" />
                <h3 className="text-sm font-semibold text-white">Audit & RLS Compliance</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Audit log activity tracking & Row Level Security (RLS) policy verification across tenant organization schemas.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
