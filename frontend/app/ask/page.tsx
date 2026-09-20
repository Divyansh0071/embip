import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { AppShell } from "@/components/layout/AppShell";
import { AskOrchestrationContainer } from "@/components/ask/AskOrchestrationContainer";
import { AskQueryContainer } from "@/components/sql/AskQueryContainer";

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
      <div className="max-w-7xl mx-auto space-y-8">
        <AskOrchestrationContainer />
        <div className="border-t border-slate-800/80 pt-6">
          <h4 className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-4">
            Phase 9 SQL Direct Testing Interface
          </h4>
          <AskQueryContainer />
        </div>
      </div>
    </AppShell>
  );
}
