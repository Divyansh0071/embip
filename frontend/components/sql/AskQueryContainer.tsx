"use client";

import React from "react";
import { createClient } from "@/lib/supabase/client";
import { SQLQueryTester } from "@/components/sql/SQLQueryTester";

export const AskQueryContainer: React.FC = () => {
  const getAuthToken = async (): Promise<string | null> => {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  };

  return <SQLQueryTester getAuthToken={getAuthToken} />;
};
