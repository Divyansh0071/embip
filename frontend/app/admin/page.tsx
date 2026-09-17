import React from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { LogoutButton } from "@/components/auth/LogoutButton";
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
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/60 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-600 font-bold text-white">
              A
            </div>
            <span className="font-semibold text-white tracking-wide">
              EMBIP Admin Portal
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              href="/dashboard"
              className="text-xs text-slate-400 hover:text-white transition flex items-center space-x-1"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Dashboard</span>
            </Link>
            <LogoutButton />
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-7xl p-6">
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center space-x-2">
            <ShieldCheck className="h-6 w-6 text-amber-500" />
            <span>System & RBAC Administration</span>
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Manage organization settings, workspace roles, audit logs, and access permissions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-lg">
            <div className="flex items-center space-x-3 mb-3">
              <Users className="h-5 w-5 text-blue-400" />
              <h3 className="text-sm font-semibold text-white">Workspace Members & RBAC</h3>
            </div>
            <p className="text-xs text-slate-400">
              Manage member roles: ADMIN, MANAGER, ANALYST, VIEWER.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-lg">
            <div className="flex items-center space-x-3 mb-3">
              <Key className="h-5 w-5 text-amber-400" />
              <h3 className="text-sm font-semibold text-white">API Keys & Tokens</h3>
            </div>
            <p className="text-xs text-slate-400">
              Configure server-side Supabase credentials and JWT token expiry parameters.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-lg">
            <div className="flex items-center space-x-3 mb-3">
              <Settings className="h-5 w-5 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">Audit & RLS Compliance</h3>
            </div>
            <p className="text-xs text-slate-400">
              Audit log activity tracking & Row Level Security policy verification.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
