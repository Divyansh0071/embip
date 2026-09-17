"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BarChart3,
  Sparkles,
  FileText,
  Database,
  FileSpreadsheet,
  Settings,
  ShieldCheck,
  Menu,
  X,
} from "lucide-react";

interface SidebarProps {
  role: string;
}

export function Sidebar({ role }: SidebarProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Ask EMBIP", href: "/ask", icon: Sparkles },
    { name: "Documents", href: "/documents", icon: FileText },
    { name: "Enterprise Data", href: "/data", icon: Database },
    { name: "Reports", href: "/reports", icon: FileSpreadsheet },
  ];

  const isAdmin = role.toUpperCase() === "ADMIN";

  const renderNavLinks = () => (
    <div className="space-y-1">
      <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
        BI Platform
      </div>
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={() => setMobileOpen(false)}
            className={`flex items-center space-x-3 rounded-lg px-3 py-2 text-xs font-medium transition ${
              isActive
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
            }`}
          >
            <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-white" : "text-slate-400"}`} />
            <span>{item.name}</span>
          </Link>
        );
      })}

      <div className="pt-4 px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
        System & Admin
      </div>

      <Link
        href="/settings"
        onClick={() => setMobileOpen(false)}
        className={`flex items-center space-x-3 rounded-lg px-3 py-2 text-xs font-medium transition ${
          pathname === "/settings"
            ? "bg-blue-600 text-white"
            : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
        }`}
      >
        <Settings className="h-4 w-4 shrink-0" />
        <span>Settings</span>
      </Link>

      {isAdmin && (
        <Link
          href="/admin"
          onClick={() => setMobileOpen(false)}
          className={`flex items-center space-x-3 rounded-lg px-3 py-2 text-xs font-medium transition ${
            pathname === "/admin"
              ? "bg-amber-600 text-white"
              : "text-amber-400/80 hover:bg-amber-500/10 hover:text-amber-300"
          }`}
        >
          <ShieldCheck className="h-4 w-4 shrink-0" />
          <span>Administration</span>
        </Link>
      )}
    </div>
  );

  return (
    <>
      {/* Mobile Toggle Button */}
      <div className="lg:hidden fixed top-3.5 left-4 z-50">
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-300 hover:text-white"
          aria-label="Toggle Navigation Sidebar"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex flex-col w-64 border-r border-slate-800 bg-slate-950 p-4 shrink-0 min-h-screen">
        {/* Brand */}
        <Link href="/dashboard" className="flex items-center space-x-3 px-2 mb-8">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-600 font-bold text-white shadow-md shadow-blue-500/20">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <span className="font-bold text-white tracking-wide text-sm block">EMBIP</span>
            <span className="text-[10px] text-slate-500 block">Enterprise BI Shell</span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="flex-1">{renderNavLinks()}</nav>

        {/* Footer info */}
        <div className="pt-4 border-t border-slate-900 px-2 text-[10px] text-slate-500">
          EMBIP Platform v0.1.0
        </div>
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden flex">
          <div
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative flex flex-col w-64 max-w-xs bg-slate-950 p-4 border-r border-slate-800 shadow-2xl z-50">
            <div className="flex items-center space-x-3 px-2 mb-6">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-600 font-bold text-white">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <span className="font-bold text-white text-sm">EMBIP Platform</span>
            </div>
            <nav className="flex-1">{renderNavLinks()}</nav>
          </div>
        </div>
      )}
    </>
  );
}
