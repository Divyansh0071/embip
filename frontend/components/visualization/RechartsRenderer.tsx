"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import { LineChart as ChartIcon, Sparkles } from "lucide-react";

export interface RechartsSpec {
  chartType: string;
  title: string;
  subtitle?: string | null;
  data: Array<Record<string, any>>;
  xAxis?: {
    dataKey: string;
    label?: string | null;
    type?: string;
    tickFormat?: string | null;
  } | null;
  yAxis?: {
    dataKey: string;
    label?: string | null;
    type?: string;
    tickFormat?: string | null;
  } | null;
  series: Array<{
    dataKey: string;
    name: string;
    color: string;
    type?: string | null;
  }>;
  colors: string[];
  showLegend?: boolean;
  showTooltip?: boolean;
  metadata?: Record<string, any>;
}

interface RechartsRendererProps {
  spec: RechartsSpec;
  explanation?: string | null;
}

const formatValue = (val: any, format?: string | null): string => {
  if (val === null || val === undefined) return "N/A";
  const num = typeof val === "number" ? val : parseFloat(val);
  if (isNaN(num)) return String(val);

  if (format === "currency") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 2,
    }).format(num);
  }
  if (format === "percentage") {
    return `${num.toFixed(1)}%`;
  }
  return num.toLocaleString();
};

export const RechartsRenderer: React.FC<RechartsRendererProps> = ({ spec, explanation }) => {
  if (!spec) return null;

  const tickFormat = spec.yAxis?.tickFormat || null;

  // 1. Render Metric Card for Scalar Indicators
  if (spec.chartType === "metric_card") {
    const item = spec.data?.[0] || {};
    const val = item.value ?? spec.metadata?.value;
    const metricName = item.metric || spec.metadata?.metric_name || spec.title;

    return (
      <div className="p-6 rounded-2xl border border-rose-500/30 bg-slate-900/40 backdrop-blur space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <ChartIcon className="h-4 w-4 text-rose-400" />
            <h3 className="text-sm font-bold text-white">{spec.title}</h3>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold uppercase">
              METRIC
            </span>
          </div>
        </div>

        <div className="p-6 rounded-xl bg-rose-950/20 border border-rose-500/20 flex flex-col justify-center items-start">
          <span className="text-xs text-rose-300 font-semibold uppercase tracking-wider mb-1">
            {metricName}
          </span>
          <span className="text-3xl font-black font-mono text-white">
            {formatValue(val, tickFormat)}
          </span>
          {spec.subtitle && (
            <span className="text-xs text-slate-400 mt-2 font-mono">{spec.subtitle}</span>
          )}
        </div>

        {explanation && (
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 italic flex items-start space-x-2">
            <Sparkles className="h-4 w-4 text-rose-400 flex-shrink-0 mt-0.5" />
            <span>&quot;{explanation}&quot;</span>
          </div>
        )}
      </div>
    );
  }

  // 2. Render Charts (Bar, Horizontal Bar, Line, Area, Pie, Grouped Bar)
  const xAxisKey = spec.xAxis?.dataKey || "category";

  return (
    <div className="p-6 rounded-2xl border border-rose-500/30 bg-slate-900/40 backdrop-blur space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <ChartIcon className="h-4 w-4 text-rose-400" />
          <h3 className="text-sm font-bold text-white">{spec.title}</h3>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold uppercase">
            {spec.chartType.replace("_", " ")}
          </span>
        </div>
        {spec.subtitle && (
          <span className="text-xs font-mono text-slate-400 hidden sm:inline">{spec.subtitle}</span>
        )}
      </div>

      <div className="w-full h-72 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          {(() => {
            switch (spec.chartType) {
              case "line_chart":
                return (
                  <LineChart data={spec.data} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey={xAxisKey} stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => formatValue(v, tickFormat)} />
                    {spec.showTooltip && (
                      <Tooltip
                        contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                        formatter={(val: any) => [formatValue(val, tickFormat), ""]}
                      />
                    )}
                    {spec.showLegend && <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />}
                    {spec.series.map((s, idx) => (
                      <Line
                        key={s.dataKey || idx}
                        type="monotone"
                        dataKey={s.dataKey}
                        name={s.name}
                        stroke={s.color || spec.colors[idx % spec.colors.length]}
                        strokeWidth={2.5}
                        dot={{ r: 4 }}
                      />
                    ))}
                  </LineChart>
                );

              case "area_chart":
                return (
                  <AreaChart data={spec.data} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey={xAxisKey} stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => formatValue(v, tickFormat)} />
                    {spec.showTooltip && (
                      <Tooltip
                        contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                        formatter={(val: any) => [formatValue(val, tickFormat), ""]}
                      />
                    )}
                    {spec.showLegend && <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />}
                    {spec.series.map((s, idx) => {
                      const color = s.color || spec.colors[idx % spec.colors.length];
                      return (
                        <Area
                          key={s.dataKey || idx}
                          type="monotone"
                          dataKey={s.dataKey}
                          name={s.name}
                          stroke={color}
                          fill={color}
                          fillOpacity={0.25}
                        />
                      );
                    })}
                  </AreaChart>
                );

              case "pie_chart":
                const seriesKey = spec.series?.[0]?.dataKey || "value";
                return (
                  <PieChart margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                    <Tooltip
                      contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                      formatter={(val: any) => [formatValue(val, tickFormat), ""]}
                    />
                    {spec.showLegend && <Legend wrapperStyle={{ fontSize: "11px" }} />}
                    <Pie
                      data={spec.data}
                      dataKey={seriesKey}
                      nameKey={xAxisKey}
                      cx="50%"
                      cy="50%"
                      outerRadius={85}
                      innerRadius={40}
                      paddingAngle={4}
                    >
                      {spec.data.map((_, idx) => (
                        <Cell key={idx} fill={spec.colors[idx % spec.colors.length]} />
                      ))}
                    </Pie>
                  </PieChart>
                );

              case "horizontal_bar_chart":
                return (
                  <BarChart data={spec.data} layout="vertical" margin={{ top: 10, right: 20, left: 40, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => formatValue(v, tickFormat)} />
                    <YAxis type="category" dataKey={xAxisKey} stroke="#64748b" tick={{ fontSize: 11 }} width={120} />
                    {spec.showTooltip && (
                      <Tooltip
                        contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                        formatter={(val: any) => [formatValue(val, tickFormat), ""]}
                      />
                    )}
                    {spec.showLegend && <Legend wrapperStyle={{ fontSize: "11px" }} />}
                    {spec.series.map((s, idx) => (
                      <Bar
                        key={s.dataKey || idx}
                        dataKey={s.dataKey}
                        name={s.name}
                        fill={s.color || spec.colors[idx % spec.colors.length]}
                        radius={[0, 6, 6, 0]}
                      />
                    ))}
                  </BarChart>
                );

              case "bar_chart":
              case "grouped_bar_chart":
              default:
                return (
                  <BarChart data={spec.data} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey={xAxisKey} stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => formatValue(v, tickFormat)} />
                    {spec.showTooltip && (
                      <Tooltip
                        contentStyle={{ backgroundColor: "#020617", borderColor: "#334155", borderRadius: "12px", fontSize: "12px" }}
                        formatter={(val: any) => [formatValue(val, tickFormat), ""]}
                      />
                    )}
                    {spec.showLegend && <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />}
                    {spec.series.map((s, idx) => (
                      <Bar
                        key={s.dataKey || idx}
                        dataKey={s.dataKey}
                        name={s.name}
                        fill={s.color || spec.colors[idx % spec.colors.length]}
                        radius={[6, 6, 0, 0]}
                      />
                    ))}
                  </BarChart>
                );
            }
          })()}
        </ResponsiveContainer>
      </div>

      {explanation && (
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 italic flex items-start space-x-2">
          <Sparkles className="h-4 w-4 text-rose-400 flex-shrink-0 mt-0.5" />
          <span>&quot;{explanation}&quot;</span>
        </div>
      )}
    </div>
  );
};
