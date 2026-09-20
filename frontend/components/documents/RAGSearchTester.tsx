"use client";

import React, { useState } from "react";
import { Search, Sparkles, FileText, Layers, AlertCircle, Loader2 } from "lucide-react";

interface Citation {
  chunk_id: string;
  document_id: string;
  filename: string;
  file_type: string;
  chunk_index: number;
  content: string;
  score: number;
  page_number?: number | null;
  sheet_name?: string | null;
}

interface RAGSearchTesterProps {
  getAuthToken: () => Promise<string | null>;
}

export const RAGSearchTester: React.FC<RAGSearchTesterProps> = ({ getAuthToken }) => {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<Citation[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setErrorMessage(null);
    setResults([]);

    try {
      const token = await getAuthToken();
      if (!token) {
        setErrorMessage("Authentication session expired. Please log in.");
        setIsSearching(false);
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/rag/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: query.trim(),
          top_k: topK,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Retrieval failed with HTTP ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to execute semantic search.");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur space-y-4">
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
        <Sparkles className="h-5 w-5 text-amber-400" />
        <h3 className="text-sm font-bold text-white">Semantic RAG Retrieval Tester</h3>
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
          Qdrant Vector DB
        </span>
      </div>

      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question or enter keywords to retrieve document chunks..."
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors"
          />
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="py-2 px-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-amber-500"
          >
            <option value={3}>Top 3</option>
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
          </select>

          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors disabled:opacity-50"
          >
            {isSearching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            <span>Retrieve</span>
          </button>
        </div>
      </form>

      {errorMessage && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="text-xs text-slate-400 font-mono">
            Retrieved {results.length} matching document chunks:
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
            {results.map((item, idx) => (
              <div
                key={item.chunk_id || idx}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/80 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between text-slate-400 text-[11px] border-b border-slate-800/80 pb-2">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-3.5 w-3.5 text-amber-400" />
                    <span className="font-semibold text-slate-200">{item.filename}</span>
                    <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      Chunk {item.chunk_index}
                    </span>
                    {item.page_number && (
                      <span className="text-[10px] text-slate-500">Page {item.page_number}</span>
                    )}
                    {item.sheet_name && (
                      <span className="text-[10px] text-slate-500">Sheet: {item.sheet_name}</span>
                    )}
                  </div>
                  <div className="font-mono font-bold text-amber-400">
                    {(item.score * 100).toFixed(1)}% match
                  </div>
                </div>

                <p className="text-slate-300 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">
                  {item.content}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
