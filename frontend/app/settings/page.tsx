import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { AppShell } from "@/components/layout/AppShell";
import { Settings, User, Building, Lock } from "lucide-react";

export default async function SettingsPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?redirect=/settings");
  }

  const role = (user.user_metadata?.role as string) || "Analyst";

  return (
    <AppShell user={user} role={role} title="Workspace & Account Settings">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2.5 rounded-xl bg-slate-500/10 text-slate-300 border border-slate-700/50">
              <Settings className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Account & Workspace Preferences</h2>
              <p className="text-xs text-slate-400">User profile, notification preferences, and workspace configuration</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
              <User className="h-5 w-5 text-indigo-400 mb-2" />
              <div className="text-xs font-semibold text-white">User Profile</div>
              <div className="text-[11px] text-slate-400 mt-1 truncate">{user.email}</div>
              <div className="mt-2 inline-flex items-center rounded-md bg-indigo-500/10 px-2 py-0.5 text-[10px] font-medium text-indigo-400 border border-indigo-500/20">
                Role: {role}
              </div>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
              <Building className="h-5 w-5 text-purple-400 mb-2" />
              <div className="text-xs font-semibold text-white">Organization</div>
              <div className="text-[11px] text-slate-400 mt-1">NovaMart Retail Solutions</div>
              <div className="text-[10px] text-slate-500 mt-0.5">Workspace ID: ws_default_01</div>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60">
              <Lock className="h-5 w-5 text-emerald-400 mb-2" />
              <div className="text-xs font-semibold text-white">Security & Tokens</div>
              <div className="text-[11px] text-slate-400 mt-1">Supabase SSR Session Active</div>
              <div className="text-[10px] text-emerald-400 mt-0.5">JWT Validated</div>
            </div>
          </div>

          <div className="p-8 rounded-xl border border-dashed border-slate-800 bg-slate-950/40 text-center">
            <p className="text-xs text-slate-500">
              Advanced workspace settings, API token generation, and notification webhooks will be configurable in future updates.
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
