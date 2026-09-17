import React from "react";
import { User } from "@supabase/supabase-js";
import { UserMenu } from "@/components/layout/UserMenu";
import { Building2 } from "lucide-react";

interface HeaderProps {
  user: User;
  role: string;
  title: string;
  workspaceName?: string;
}

export function Header({
  user,
  role,
  title,
  workspaceName = "Default Workspace",
}: HeaderProps) {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 px-6 py-3.5 backdrop-blur-md sticky top-0 z-30">
      <div className="flex items-center justify-between">
        {/* Title & Breadcrumb */}
        <div className="pl-10 lg:pl-0">
          <h1 className="text-base font-bold text-white tracking-tight">{title}</h1>
        </div>

        {/* Right Info: Workspace Context + User Menu */}
        <div className="flex items-center space-x-4">
          <div className="hidden sm:flex items-center space-x-2 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300">
            <Building2 className="h-3.5 w-3.5 text-blue-400" />
            <span className="font-medium text-slate-200">NovaMart Retail</span>
            <span className="text-slate-500">/</span>
            <span className="text-slate-400">{workspaceName}</span>
          </div>

          <UserMenu user={user} role={role} />
        </div>
      </div>
    </header>
  );
}
