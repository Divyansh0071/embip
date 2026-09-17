import React from "react";
import { User } from "@supabase/supabase-js";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

interface AppShellProps {
  user: User;
  role: string;
  title: string;
  children: React.ReactNode;
}

export function AppShell({ user, role, title, children }: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      <Sidebar role={role} />
      <div className="flex flex-1 flex-col min-w-0">
        <Header user={user} role={role} title={title} />
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
