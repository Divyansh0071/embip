"use client";

import React, { useState, useRef } from "react";
import { Upload, FileText, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

interface UploadZoneProps {
  onUploadSuccess: () => void;
  getAuthToken: () => Promise<string | null>;
}

const SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".csv", ".xlsx"];
const MAX_SIZE_MB = 25;

export const UploadZone: React.FC<UploadZoneProps> = ({ onUploadSuccess, getAuthToken }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelection = async (file: File) => {
    setErrorMessage(null);
    setSuccessMessage(null);

    // Validate size
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setErrorMessage(`File size (${(file.size / (1024 * 1024)).toFixed(2)}MB) exceeds maximum limit of ${MAX_SIZE_MB}MB.`);
      return;
    }

    // Validate extension
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!SUPPORTED_EXTENSIONS.includes(ext)) {
      setErrorMessage(`Unsupported file format '${ext}'. Allowed formats: ${SUPPORTED_EXTENSIONS.join(", ")}`);
      return;
    }

    setIsUploading(true);

    try {
      const token = await getAuthToken();
      if (!token) {
        setErrorMessage("Authentication session expired. Please log in again.");
        setIsUploading(false);
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status code ${response.status}`);
      }

      const data = await response.json();
      setSuccessMessage(`Document '${data.file_name || data.filename}' uploaded and processed successfully! (${data.chunk_count || 0} chunks created)`);
      onUploadSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to upload document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative p-8 rounded-xl border-2 border-dashed transition-all cursor-pointer text-center ${
          isDragging
            ? "border-amber-500 bg-amber-500/10"
            : "border-slate-800 bg-slate-950/60 hover:border-slate-700 hover:bg-slate-900/40"
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileSelection(e.target.files[0]);
            }
          }}
          accept=".pdf,.docx,.txt,.csv,.xlsx"
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="p-3 rounded-full bg-slate-900 border border-slate-800 text-amber-400">
            {isUploading ? (
              <Loader2 className="h-8 w-8 animate-spin" />
            ) : (
              <Upload className="h-8 w-8" />
            )}
          </div>

          <div>
            <p className="text-sm font-semibold text-white">
              {isUploading ? "Uploading & Processing Document..." : "Click or drag document to upload"}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Supports PDF, DOCX, TXT, CSV, & XLSX (Up to {MAX_SIZE_MB}MB)
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {SUPPORTED_EXTENSIONS.map((ext) => (
              <span
                key={ext}
                className="px-2.5 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-400"
              >
                {ext.toUpperCase()}
              </span>
            ))}
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center space-x-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}
    </div>
  );
};
