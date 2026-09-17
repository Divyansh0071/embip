"use client";

import React, { useState } from "react";
import { FileText, Trash2, Eye, FileCheck, AlertTriangle, Layers } from "lucide-react";

export interface DocumentItem {
  id: string;
  file_name: string;
  original_filename?: string | null;
  file_type: string;
  file_size: number;
  status: "uploaded" | "processing" | "processed" | "failed" | string;
  processing_error?: string | null;
  created_at: string;
  chunk_count?: number;
}

interface DocumentListProps {
  documents: DocumentItem[];
  userRole: string;
  onDeleteDocument: (docId: string) => Promise<void>;
  onRefresh: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  userRole,
  onDeleteDocument,
}) => {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);

  const canDelete = ["MANAGER", "ADMIN"].includes(userRole.toUpperCase());

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getStatusBadge = (statusStr: string) => {
    switch (statusStr.toLowerCase()) {
      case "processed":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
            Processed
          </span>
        );
      case "processing":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mr-1.5 animate-ping" />
            Processing
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
            Uploaded
          </span>
        );
    }
  };

  const getTypeBadgeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "docx":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "xlsx":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "csv":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
      default:
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to delete this document and all its chunks?")) {
      setDeletingId(id);
      try {
        await onDeleteDocument(id);
      } finally {
        setDeletingId(null);
      }
    }
  };

  if (documents.length === 0) {
    return (
      <div className="p-12 rounded-xl border border-dashed border-slate-800 bg-slate-950/60 text-center">
        <FileCheck className="h-10 w-10 text-slate-600 mx-auto mb-3" />
        <h3 className="text-sm font-semibold text-slate-200">No Documents Uploaded</h3>
        <p className="mt-1 text-xs text-slate-500 max-w-md mx-auto">
          Upload enterprise PDFs, DOCX files, spreadsheets, or text files to build your workspace knowledge base.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/40 backdrop-blur">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/80 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th className="py-3.5 px-4">Document</th>
              <th className="py-3.5 px-4">Format</th>
              <th className="py-3.5 px-4">Size</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4">Chunks</th>
              <th className="py-3.5 px-4">Upload Date</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs font-normal text-slate-300">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-3 px-4 font-medium text-white flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-slate-800/80 text-amber-400 border border-slate-700">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div className="truncate max-w-xs">
                    <span className="block truncate font-medium text-slate-200">{doc.file_name}</span>
                    {doc.original_filename && doc.original_filename !== doc.file_name && (
                      <span className="block truncate text-[10px] text-slate-500">{doc.original_filename}</span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${getTypeBadgeColor(doc.file_type)}`}>
                    {doc.file_type.toUpperCase()}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400">{formatBytes(doc.file_size)}</td>
                <td className="py-3 px-4">{getStatusBadge(doc.status)}</td>
                <td className="py-3 px-4">
                  <span className="inline-flex items-center space-x-1 font-mono text-slate-400">
                    <Layers className="h-3.5 w-3.5 text-slate-500" />
                    <span>{doc.chunk_count ?? 0}</span>
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400">
                  {new Date(doc.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => setSelectedDoc(doc)}
                      title="View Details"
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                    >
                      <Eye className="h-3.5 w-3.5" />
                    </button>

                    {canDelete && (
                      <button
                        onClick={() => handleDelete(doc.id)}
                        disabled={deletingId === doc.id}
                        title="Delete Document"
                        className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors disabled:opacity-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Details Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-5 text-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">{selectedDoc.file_name}</h3>
                  <p className="text-xs text-slate-400">ID: {selectedDoc.id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800"
              >
                Close
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Format & Size</span>
                <span className="font-mono text-slate-300">{selectedDoc.file_type.toUpperCase()} • {formatBytes(selectedDoc.file_size)}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-slate-500 block text-[10px] font-semibold uppercase">Status & Chunks</span>
                <span className="font-mono text-slate-300">{selectedDoc.status.toUpperCase()} • {selectedDoc.chunk_count || 0} Chunks</span>
              </div>
            </div>

            {selectedDoc.processing_error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-start space-x-2">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold block">Processing Error</span>
                  <span className="text-[11px] opacity-90">{selectedDoc.processing_error}</span>
                </div>
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
