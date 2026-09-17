import React from "react";
import type { Metadata } from "next";
import { createClient } from "@/lib/supabase/server";
import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { ValueProp } from "@/components/landing/ValueProp";
import { Capabilities } from "@/components/landing/Capabilities";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { AgentArchitecture } from "@/components/landing/AgentArchitecture";
import { SecuritySection } from "@/components/landing/SecuritySection";
import { Pricing } from "@/components/landing/Pricing";
import { Footer } from "@/components/landing/Footer";

export const metadata: Metadata = {
  title: "EMBIP — Enterprise Multi-Agent Business Intelligence",
  description:
    "AI-powered business intelligence connecting enterprise databases, corporate documents, analytics engines, and validated decision insights.",
};

export default async function LandingPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar user={user} />
      <main className="flex-grow">
        <Hero />
        <ValueProp />
        <Capabilities />
        <HowItWorks />
        <AgentArchitecture />
        <SecuritySection />
        <Pricing />
      </main>
      <Footer />
    </div>
  );
}
