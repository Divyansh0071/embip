import React from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { LayoutDashboard, Shield, User, FolderKanban, Terminal } from "lucide-react";

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?redirect=/dashboard");
  }

  const userRole = (user.user_metadata?.role as string) || "Analyst";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/60 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 font-bold text-white">
              E
            </div>
            <span className="font-semibold text-white tracking-wide">
              EMBIP Platform
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <User className="h-3.5 w-3.5 text-blue-400" />
              <span>{user.email}</span>
              <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] uppercase text-blue-400">
                {userRole}
              </span>
            </div>
            <LogoutButton />
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-7xl p-6">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center space-x-2">
              <LayoutDashboard className="h-6 w-6 text-blue-500" />
              <span>Enterprise BI Dashboard</span>
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Authenticated Session Verified — Phase 3 Auth Foundation Running
            </p>
          </div>

          {userRole === "ADMIN" && (
            <Link
              href="/admin"
              className="inline-flex items-center space-x-2 rounded-lg bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 text-xs font-semibold text-amber-400 transition hover:bg-amber-500/20"
            >
              <Shield className="h-4 w-4" />
              <span>Admin Portal</span>
            </Link>
          )}
        </div>

        {/* Status Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-lg">
            <div className="flex items-center space-x-3 mb-3">
              <User className="h-5 w-5 text-blue-400" />
              <h3 className="text-sm font-semibold text-white">Identity Profile</h3>
            </div>
            <div className="space-y-1.5 text-xs text-slate-400">
              <p><strong className="text-slate-300">User ID:</strong> {user.id}</p>
              <p><strong className="text-slate-300">Email:</strong> {user.email}</p>
              <p><strong className="text-slate-300">Auth Status:</strong> Verified</p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-lg">
            <div className="flex items-center space-x-3 mb-3">
              <FolderKanban className="h-5 w-5 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">Workspace Context</h3>
            </div>
            <div className="space-y-1.5 text-xs text-slate-400">
              <p><strong className="text-slate-300">Org:</strong> NovaMart Enterprise</p>
              <p><strong className="text-slate-300">Workspace:</strong> Default Workspace</p>
              <p><strong className="text-slate-300">Role:</strong> {userRole}</p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 shadow-lg">
            <div className="flex items-center space-x-3 mb-3">
              <Terminal className="h-5 w-5 text-purple-400" />
              <h3 className="text-sm font-semibold text-white">FastAPI Auth API</h3>
            </div>
            <div className="space-y-1.5 text-xs text-slate-400">
              <p><strong className="text-slate-300">Endpoint:</strong> /api/v1/auth/me</p>
              <p><strong className="text-slate-300">Header:</strong> Authorization: Bearer</p>
              <p><strong className="text-slate-300">JWT Check:</strong> Active</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
