"use client";

import React, { useState } from "react";
import {
  FileText,
  Download,
  CheckCircle2,
  AlertCircle,
  FileDown,
  Sparkles,
  BookOpen,
  HelpCircle,
  Clock,
  Loader2,
} from "lucide-react";
import { RechartsRenderer, RechartsSpec } from "../visualization/RechartsRenderer";

export interface ReportSectionData {
  section_id: string;
  title: string;
  content: string;
  section_type: "executive_summary" | "key_metrics" | "visualizations" | "sources" | "methodology";
}

export interface ReportCitationData {
  source_filename: string;
  chunk_id: string;
  excerpt: string;
  score: number;
  page_number?: number | null;
  sheet_name?: string | null;
}

export interface ReportDataProps {
  report_id: string;
  title: string;
  subtitle?: string | null;
  generated_at: string;
  executive_summary: string;
  sections: ReportSectionData[];

  metrics: Record<string, any>;
  visualization_spec?: RechartsSpec | null;
  citations: ReportCitationData[];
  methodology: string;
  confidence_score: number;
  is_validated: boolean;
}

interface ReportViewProps {
  report: ReportDataProps;
  getAuthToken: () => Promise<string | null>;
}

export const ReportView: React.FC<ReportViewProps> = ({ report, getAuthToken }) => {
  const [isExporting, setIsExporting] = useState<"pdf" | "markdown" | null>(null);

  const handleExport = async (format: "pdf" | "markdown") => {
    setIsExporting(format);
    try {
      const token = await getAuthToken();
      if (!token) return;

      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/reports/export`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          format,
          report_data: report,
        }),
      });

      if (!response.ok) {
        throw new Error(`Export failed with HTTP ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${report.report_id}.${format === "pdf" ? "pdf" : "md"}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Report export failed", err);
    } finally {
      setIsExporting(null);
    }
  };

  return (
    <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-indigo-400" />
            <h2 className="text-xl font-bold text-white">{report.title}</h2>
          </div>
          {report.subtitle && <p className="text-xs text-slate-400">{report.subtitle}</p>}
          <div className="flex items-center space-x-3 text-xs text-slate-400 font-mono pt-1">
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5 text-slate-500" />
              {new Date(report.generated_at).toLocaleString()}
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
              {(report.confidence_score * 100).toFixed(0)}% Confidence Verified
            </span>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={() => handleExport("pdf")}
            disabled={isExporting !== null}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white transition-colors disabled:opacity-50"
          >
            {isExporting === "pdf" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Download className="h-3.5 w-3.5" />
            )}
            <span>Export PDF</span>
          </button>

          <button
            onClick={() => handleExport("markdown")}
            disabled={isExporting !== null}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-colors disabled:opacity-50"
          >
            {isExporting === "markdown" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <FileDown className="h-3.5 w-3.5 text-slate-400" />
            )}
            <span>Markdown</span>
          </button>
        </div>
      </div>

      {/* Executive Summary Card */}
      <div className="p-5 rounded-xl bg-indigo-950/20 border border-indigo-500/20 space-y-2">
        <div className="flex items-center space-x-2 text-indigo-300 font-semibold text-xs uppercase tracking-wider">
          <Sparkles className="h-4 w-4" />
          <span>1. Executive Summary</span>
        </div>
        <p className="text-sm text-slate-200 leading-relaxed font-sans">
          {report.executive_summary}
        </p>
      </div>

      {/* Key Metrics Grid */}
      {Object.keys(report.metrics).length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            2. Key Business Metrics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(report.metrics).map(([k, v], idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-[11px] text-slate-400 font-medium capitalize block truncate">
                  {k.replace(/_/g, " ")}
                </span>
                <span className="text-lg font-bold font-mono text-white">
                  {typeof v === "number" ? v.toLocaleString() : String(v)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Embedded Chart */}
      {report.visualization_spec && (
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            3. Visual Analytics
          </h3>
          <RechartsRenderer spec={report.visualization_spec} />
        </div>
      )}

      {/* Citations & Source Evidence */}
      {report.citations && report.citations.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="flex items-center space-x-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
            <BookOpen className="h-4 w-4" />
            <span>Document Evidence & Citations</span>
          </div>
          <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
            {report.citations.map((cite, idx) => (
              <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1 text-xs">
                <div className="flex items-center justify-between text-slate-400 text-[11px]">
                  <span className="font-semibold text-slate-200">{cite.source_filename}</span>
                  <span className="font-mono text-amber-400">{(cite.score * 100).toFixed(0)}% match</span>
                </div>
                <p className="text-slate-300 italic font-mono text-[11px]">
                  &quot;{cite.excerpt}&quot;
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Methodology Note */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1 text-xs text-slate-400">
        <span className="font-semibold text-slate-300 block">Methodology & Scope:</span>
        <p className="leading-relaxed">{report.methodology}</p>
      </div>
    </div>
  );
};
