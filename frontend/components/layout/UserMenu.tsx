"use client";

import React, { useState } from "react";
import Link from "next/link";
import { User } from "@supabase/supabase-js";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { User as UserIcon, Settings, ChevronDown } from "lucide-react";

interface UserMenuProps {
  user: User;
  role: string;
}

export function UserMenu({ user, role }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-200 transition hover:bg-slate-800"
      >
        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600/30 text-blue-400 font-semibold text-[10px]">
          {user.email ? user.email.charAt(0).toUpperCase() : "U"}
        </div>
        <span className="max-w-[120px] truncate font-medium">{user.email}</span>
        <span className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[9px] uppercase text-blue-400 border border-slate-700">
          {role}
        </span>
        <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl border border-slate-800 bg-slate-900 p-2 shadow-2xl backdrop-blur-md z-50">
          <div className="px-3 py-2 border-b border-slate-800/80 mb-1">
            <p className="text-[11px] font-medium text-white truncate">{user.email}</p>
            <p className="text-[10px] text-slate-400">Role: <span className="text-blue-400 font-mono">{role}</span></p>
          </div>

          <Link
            href="/settings"
            onClick={() => setIsOpen(false)}
            className="flex items-center space-x-2 rounded-lg px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white transition"
          >
            <Settings className="h-3.5 w-3.5 text-slate-400" />
            <span>Workspace Settings</span>
          </Link>

          <div className="pt-1 border-t border-slate-800/80 mt-1">
            <LogoutButton />
          </div>
        </div>
      )}
    </div>
  );
}
