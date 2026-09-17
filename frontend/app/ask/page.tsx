import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { AppShell } from "@/components/layout/AppShell";
import { MessageSquare, Sparkles, Send } from "lucide-react";

export default async function AskPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login?redirect=/ask");
  }

  const role = (user.user_metadata?.role as string) || "Analyst";

  return (
    <AppShell user={user} role={role} title="Ask EMBIP — Natural Language Intelligence">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
          <div className="flex items-center space-x-3 mb-3">
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <MessageSquare className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Natural Language Ask Interface</h2>
              <p className="text-xs text-slate-400">Multi-agent Planner & Orchestrated Context Query Engine</p>
            </div>
          </div>

          {/* Search bar simulation */}
          <div className="relative my-6">
            <div className="flex items-center rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 shadow-inner">
              <Sparkles className="h-5 w-5 text-indigo-400 mr-3 shrink-0" />
              <input
                type="text"
                disabled
                placeholder="Ask any business question... (e.g. 'What were top 5 revenue categories in Q3?')"
                className="w-full bg-transparent text-sm text-slate-300 placeholder-slate-500 focus:outline-none cursor-not-allowed"
              />
              <button disabled className="ml-2 rounded-lg bg-slate-800 p-2 text-slate-500 cursor-not-allowed">
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="p-12 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 text-center">
            <Sparkles className="h-10 w-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-200">Natural Language Engine Shell Prepared</h3>
            <p className="mt-1 text-xs text-slate-500 max-w-md mx-auto">
              Natural language queries, intent classification, and Planner agent task delegation will be connected in Phase 6.
            </p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
