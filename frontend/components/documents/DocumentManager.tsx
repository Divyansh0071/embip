"use client";

import React, { useState, useEffect, useCallback } from "react";
import { createClient } from "@/lib/supabase/client";
import { UploadZone } from "./UploadZone";
import { DocumentList, DocumentItem } from "./DocumentList";
import { RAGSearchTester } from "./RAGSearchTester";
import { FileText, RefreshCw, Layers } from "lucide-react";

interface DocumentManagerProps {
  userRole: string;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({ userRole }) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const supabase = createClient();

  const getAuthToken = useCallback(async (): Promise<string | null> => {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  }, [supabase]);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const token = await getAuthToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/documents`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch documents (HTTP ${response.status})`);
      }

      const data = await response.json();
      setDocuments(data);
    } catch (err: any) {
      setError(err.message || "Could not load documents.");
    } finally {
      setIsLoading(false);
    }
  }, [getAuthToken]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleDeleteDocument = async (docId: string) => {
    const token = await getAuthToken();
    if (!token) return;

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/api/v1/documents/${docId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      alert(err.detail || "Failed to delete document.");
      return;
    }

    fetchDocuments();
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Document Knowledge Base</h2>
              <p className="text-xs text-slate-400">PDF, DOCX, TXT, CSV, & XLSX Unstructured Ingestion Pipeline</p>
            </div>
          </div>

          <button
            onClick={fetchDocuments}
            disabled={isLoading}
            className="inline-flex items-center space-x-2 rounded-xl bg-slate-800 hover:bg-slate-700 px-4 py-2 text-xs font-semibold text-slate-300 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Upload Zone */}
        <UploadZone onUploadSuccess={fetchDocuments} getAuthToken={getAuthToken} />
      </div>

      {/* Semantic RAG Retrieval Tester */}
      <RAGSearchTester getAuthToken={getAuthToken} />

      {/* Documents Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center space-x-2">
            <Layers className="h-4 w-4 text-amber-400" />
            <h3 className="text-sm font-bold text-white">Workspace Documents</h3>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-800 text-slate-400">
              {documents.length}
            </span>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="p-12 text-center text-slate-500 text-xs font-mono">Loading workspace documents...</div>
        ) : (
          <DocumentList
            documents={documents}
            userRole={userRole}
            onDeleteDocument={handleDeleteDocument}
            onRefresh={fetchDocuments}
          />
        )}
      </div>
    </div>
  );
};
