"use client";

import React from "react";
import { createClient } from "@/lib/supabase/client";
import { OrchestrationView } from "@/components/ask/OrchestrationView";

export const AskOrchestrationContainer: React.FC = () => {
  const getAuthToken = async (): Promise<string | null> => {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  };

  return <OrchestrationView getAuthToken={getAuthToken} />;
};
