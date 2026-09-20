"""
Pure Deterministic Calculation Functions for EMBIP Analytics Agent (Phase 11).
All calculations use Pandas / NumPy with strict error handling, missing-value tracking,
and zero arbitrary code execution.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from app.ai.analytics.exceptions import CalculationError
from app.ai.analytics.statistics import (
    calculate_cagr_val,
    calculate_percentage_change_val,
    parse_dates_series,
    safe_float,
)


def _get_numeric_series(df: pd.DataFrame, col: str) -> Tuple[pd.Series, int, List[str]]:
    """Helper to extract a numeric series, coerce errors, and count missing values."""
    warnings: List[str] = []
    if col not in df.columns:
        raise CalculationError(f"Required metric column '{col}' not found in dataset.")
    
    raw = df[col]
    numeric = pd.to_numeric(raw, errors="coerce")
    missing_cnt = int(numeric.isna().sum())
    
    if missing_cnt > 0:
        warnings.append(f"Metric column '{col}' contains {missing_cnt} null or non-numeric values which were excluded.")
        
    return numeric, missing_cnt, warnings


# ---------------------------------------------------------------------------
# 1. Descriptive Statistics
# ---------------------------------------------------------------------------

def op_count(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    warnings = []
    if metric_col and metric_col in df.columns:
        cnt = int(df[metric_col].count())
    else:
        cnt = len(df)
    return {"value": cnt, "rows_used": len(df)}, warnings


def op_sum(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'sum' requires a metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    val = safe_float(s.sum())
    return {"value": val, "rows_used": int(s.count())}, warnings


def op_mean(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'mean' requires a metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    val = safe_float(s.mean())
    return {"value": val, "rows_used": int(s.count())}, warnings


def op_median(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'median' requires a metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    val = safe_float(s.median())
    return {"value": val, "rows_used": int(s.count())}, warnings


def op_min(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'min' requires a metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    val = safe_float(s.min())
    return {"value": val, "rows_used": int(s.count())}, warnings


def op_max(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'max' requires a metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    val = safe_float(s.max())
    return {"value": val, "rows_used": int(s.count())}, warnings


def op_std(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'std' requires a metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    val = safe_float(s.std(ddof=1)) if len(s.dropna()) > 1 else 0.0
    return {"value": val, "rows_used": int(s.count())}, warnings


# ---------------------------------------------------------------------------
# 2. Business Metrics
# ---------------------------------------------------------------------------

def op_total_revenue(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    rev_col = metric_col or next((c for c in ["total_revenue", "total_amount", "revenue", "total_price", "amount"] if c in df.columns), None)
    if not rev_col:
        raise CalculationError("Could not infer revenue column. Specify metric_column.")
    s, missing, warnings = _get_numeric_series(df, rev_col)
    val = safe_float(s.sum())
    return {"value": val, "rows_used": int(s.count()), "metric_used": rev_col}, warnings


def op_average_order_value(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    rev_col = metric_col or next((c for c in ["total_revenue", "total_amount", "revenue", "total_price", "amount"] if c in df.columns), None)
    if not rev_col:
        raise CalculationError("Could not infer revenue column for AOV.")
    s, missing, warnings = _get_numeric_series(df, rev_col)
    total_rev = s.sum()
    order_cnt = len(s.dropna())
    if order_cnt == 0:
        return {"value": 0.0, "rows_used": 0}, warnings
    aov = safe_float(total_rev / order_cnt)
    return {"value": aov, "rows_used": order_cnt, "metric_used": rev_col}, warnings


def op_units_sold(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    qty_col = metric_col or next((c for c in ["quantity", "total_quantity", "units_sold", "units"] if c in df.columns), None)
    if not qty_col:
        raise CalculationError("Could not infer quantity column for units_sold.")
    s, missing, warnings = _get_numeric_series(df, qty_col)
    val = safe_float(s.sum())
    return {"value": val, "rows_used": int(s.count()), "metric_used": qty_col}, warnings


def op_gross_profit(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    warnings = []
    if "gross_profit" in df.columns:
        s, missing, w = _get_numeric_series(df, "gross_profit")
        return {"value": safe_float(s.sum()), "rows_used": int(s.count())}, w
    
    # Compute: total_price - (quantity * cost_price)
    if not {"total_price", "quantity", "cost_price"}.issubset(set(df.columns)):
        raise CalculationError("Calculating gross_profit requires 'gross_profit' column OR ('total_price', 'quantity', 'cost_price').")
    
    tp = pd.to_numeric(df["total_price"], errors="coerce").fillna(0)
    qty = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    cp = pd.to_numeric(df["cost_price"], errors="coerce").fillna(0)
    profit = tp - (qty * cp)
    val = safe_float(profit.sum())
    return {"value": val, "rows_used": len(profit)}, warnings


def op_gross_margin_percentage(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    profit_res, w1 = op_gross_profit(df)
    rev_res, w2 = op_total_revenue(df)
    warnings = w1 + w2
    
    gp = profit_res.get("value") or 0.0
    rev = rev_res.get("value") or 0.0
    
    if rev == 0:
        warnings.append("Gross margin percentage cannot be computed: total revenue is zero.")
        return {"value": None, "rows_used": len(df)}, warnings
        
    margin_pct = round((gp / rev) * 100.0, 2)
    return {"value": margin_pct, "rows_used": len(df), "gross_profit": gp, "revenue": rev}, warnings


# ---------------------------------------------------------------------------
# 3. Comparisons & Growth
# ---------------------------------------------------------------------------

def op_absolute_difference(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    params = parameters or {}
    val1 = params.get("val1")
    val2 = params.get("val2")
    
    if val1 is not None and val2 is not None:
        diff = safe_float(float(val2) - float(val1))
        return {"value": diff, "val1": val1, "val2": val2, "rows_used": len(df)}, []
        
    if not metric_col:
        raise CalculationError("absolute_difference requires val1/val2 params or metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    clean = s.dropna().tolist()
    if len(clean) < 2:
        raise CalculationError("absolute_difference requires at least 2 numerical data points.")
    diff = safe_float(clean[-1] - clean[0])
    return {"value": diff, "val1": clean[0], "val2": clean[-1], "rows_used": len(clean)}, warnings


def op_percentage_difference(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    params = parameters or {}
    val1 = params.get("val1")
    val2 = params.get("val2")
    
    if val1 is not None and val2 is not None:
        pct, warn = calculate_percentage_change_val(float(val1), float(val2))
        return {"value": pct, "val1": val1, "val2": val2, "rows_used": len(df)}, ([warn] if warn else [])
        
    if not metric_col:
        raise CalculationError("percentage_difference requires val1/val2 params or metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    clean = s.dropna().tolist()
    if len(clean) < 2:
        raise CalculationError("percentage_difference requires at least 2 numerical data points.")
    pct, warn = calculate_percentage_change_val(clean[0], clean[-1])
    if warn:
        warnings.append(warn)
    return {"value": pct, "val1": clean[0], "val2": clean[-1], "rows_used": len(clean)}, warnings


def op_growth_rate(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    return op_percentage_difference(df, metric_col=metric_col, parameters=parameters, **kwargs)


def op_cagr(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    params = parameters or {}
    beg = params.get("beginning_value")
    end = params.get("ending_value")
    years = params.get("years")
    
    if beg is not None and end is not None and years is not None:
        cagr, warn = calculate_cagr_val(float(beg), float(end), float(years))
        return {"value": cagr, "beginning_value": beg, "ending_value": end, "years": years, "rows_used": len(df)}, ([warn] if warn else [])
        
    if not metric_col:
        raise CalculationError("CAGR calculation requires parameters (beginning_value, ending_value, years) or metric_column with time series data.")
        
    s, missing, warnings = _get_numeric_series(df, metric_col)
    clean = s.dropna().tolist()
    if len(clean) < 2:
        raise CalculationError("CAGR requires at least 2 points in dataset.")
        
    calc_years = params.get("years") or (len(clean) - 1)
    cagr, warn = calculate_cagr_val(clean[0], clean[-1], float(calc_years))
    if warn:
        warnings.append(warn)
    return {"value": cagr, "beginning_value": clean[0], "ending_value": clean[-1], "years": calc_years, "rows_used": len(clean)}, warnings


# ---------------------------------------------------------------------------
# 4. Ranking
# ---------------------------------------------------------------------------

def op_top_n(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'top_n' requires metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    n = min(int((parameters or {}).get("n", 5)), 100)
    
    sorted_df = df.assign(_metric=s).sort_values(by="_metric", ascending=False).head(n).drop(columns=["_metric"])
    rows = sorted_df.to_dict(orient="records")
    return {"rows": rows, "top_n": n, "rows_used": len(rows)}, warnings


def op_bottom_n(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("Operation 'bottom_n' requires metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    n = min(int((parameters or {}).get("n", 5)), 100)
    
    sorted_df = df.assign(_metric=s).sort_values(by="_metric", ascending=True).head(n).drop(columns=["_metric"])
    rows = sorted_df.to_dict(orient="records")
    return {"rows": rows, "bottom_n": n, "rows_used": len(rows)}, warnings


def op_rank_by_metric(df: pd.DataFrame, metric_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    return op_top_n(df, metric_col=metric_col, parameters={"n": len(df)}, **kwargs)


# ---------------------------------------------------------------------------
# 5. Grouped Aggregation
# ---------------------------------------------------------------------------

def op_group_sum(df: pd.DataFrame, metric_col: Optional[str] = None, group_by: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not group_by or group_by not in df.columns:
        raise CalculationError("group_sum requires valid group_by column.")
    if not metric_col or metric_col not in df.columns:
        raise CalculationError("group_sum requires valid metric_column.")
        
    s, missing, warnings = _get_numeric_series(df, metric_col)
    grouped = df.assign(_metric=s).groupby(group_by)["_metric"].sum().reset_index()
    
    groups = []
    for _, row in grouped.iterrows():
        groups.append({
            "group": str(row[group_by]),
            "value": safe_float(row["_metric"])
        })
        
    return {"groups": groups, "rows_used": int(s.count())}, warnings


def op_group_average(df: pd.DataFrame, metric_col: Optional[str] = None, group_by: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not group_by or group_by not in df.columns:
        raise CalculationError("group_average requires valid group_by column.")
    if not metric_col or metric_col not in df.columns:
        raise CalculationError("group_average requires valid metric_column.")
        
    s, missing, warnings = _get_numeric_series(df, metric_col)
    grouped = df.assign(_metric=s).groupby(group_by)["_metric"].mean().reset_index()
    
    groups = []
    for _, row in grouped.iterrows():
        groups.append({
            "group": str(row[group_by]),
            "value": safe_float(row["_metric"])
        })
        
    return {"groups": groups, "rows_used": int(s.count())}, warnings


def op_group_count(df: pd.DataFrame, group_by: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not group_by or group_by not in df.columns:
        raise CalculationError("group_count requires valid group_by column.")
        
    counts = df.groupby(group_by).size().reset_index(name="count")
    groups = []
    for _, row in counts.iterrows():
        groups.append({
            "group": str(row[group_by]),
            "value": int(row["count"])
        })
        
    return {"groups": groups, "rows_used": len(df)}, []


# ---------------------------------------------------------------------------
# 6. Time-Series Aggregations
# ---------------------------------------------------------------------------

def _time_series_resample(df: pd.DataFrame, metric_col: str, time_col: str, freq: str) -> Tuple[List[Dict[str, Any]], int, List[str]]:
    warnings = []
    if time_col not in df.columns:
        raise CalculationError(f"Time column '{time_col}' not found.")
    if metric_col not in df.columns:
        raise CalculationError(f"Metric column '{metric_col}' not found.")
        
    dt_series, missing_dt = parse_dates_series(df[time_col])
    if missing_dt > 0:
        warnings.append(f"Time column '{time_col}' contains {missing_dt} unparseable timestamps which were excluded.")
        
    num_series, missing_num, num_warn = _get_numeric_series(df, metric_col)
    warnings.extend(num_warn)
    
    temp_df = pd.DataFrame({"dt": dt_series, "val": num_series}).dropna()
    if temp_df.empty:
        raise CalculationError("No valid datetime and numerical pairs available for time-series aggregation.")
        
    temp_df.set_index("dt", inplace=True)
    resampled = temp_df.resample(freq)["val"].sum()
    
    series_points = []
    for dt_val, val in resampled.items():
        if freq == "D":
            period_str = dt_val.strftime("%Y-%m-%d")
        elif freq == "W":
            period_str = dt_val.strftime("%Y-W%U")
        elif freq == "M" or freq == "MS":
            period_str = dt_val.strftime("%Y-%m")
        elif freq == "Q":
            period_str = f"{dt_val.year}-Q{dt_val.quarter}"
        else:
            period_str = str(dt_val)
            
        series_points.append({
            "period": period_str,
            "value": safe_float(val)
        })
        
    return series_points, len(temp_df), warnings


def op_daily_aggregation(df: pd.DataFrame, metric_col: Optional[str] = None, time_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col or not time_col:
        raise CalculationError("daily_aggregation requires metric_column and time_column.")
    series_pts, used, warnings = _time_series_resample(df, metric_col, time_col, "D")
    return {"series": series_pts, "rows_used": used}, warnings


def op_weekly_aggregation(df: pd.DataFrame, metric_col: Optional[str] = None, time_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col or not time_col:
        raise CalculationError("weekly_aggregation requires metric_column and time_column.")
    series_pts, used, warnings = _time_series_resample(df, metric_col, time_col, "W")
    return {"series": series_pts, "rows_used": used}, warnings


def op_monthly_trend(df: pd.DataFrame, metric_col: Optional[str] = None, time_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col or not time_col:
        time_col = time_col or next((c for c in ["transaction_date", "sale_date", "date", "created_at"] if c in df.columns), None)
        metric_col = metric_col or next((c for c in ["total_amount", "revenue", "total_price", "amount"] if c in df.columns), None)
    if not metric_col or not time_col:
        raise CalculationError("monthly_trend requires metric_column and time_column.")
    series_pts, used, warnings = _time_series_resample(df, metric_col, time_col, "MS")
    return {"series": series_pts, "rows_used": used}, warnings


def op_quarterly_aggregation(df: pd.DataFrame, metric_col: Optional[str] = None, time_col: Optional[str] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col or not time_col:
        raise CalculationError("quarterly_aggregation requires metric_column and time_column.")
    series_pts, used, warnings = _time_series_resample(df, metric_col, time_col, "Q")
    return {"series": series_pts, "rows_used": used}, warnings


def op_rolling_average(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("rolling_average requires metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    window = int((parameters or {}).get("window", 3))
    
    rolling_s = s.rolling(window=window, min_periods=1).mean()
    vals = [safe_float(v) for v in rolling_s]
    return {"rolling_values": vals, "window": window, "rows_used": int(s.count())}, warnings


# ---------------------------------------------------------------------------
# 7. Distribution
# ---------------------------------------------------------------------------

def op_percentile(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("percentile requires metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    p = float((parameters or {}).get("p", 90))
    if not (0 <= p <= 100):
        raise CalculationError("Percentile parameter p must be between 0 and 100.")
    val = safe_float(np.percentile(s.dropna(), p))
    return {"value": val, "percentile": p, "rows_used": int(s.count())}, warnings


def op_quantile(df: pd.DataFrame, metric_col: Optional[str] = None, parameters: Dict[str, Any] = None, **kwargs) -> Tuple[Dict[str, Any], List[str]]:
    if not metric_col:
        raise CalculationError("quantile requires metric_column.")
    s, missing, warnings = _get_numeric_series(df, metric_col)
    q_vals = (parameters or {}).get("q") or [0.25, 0.5, 0.75]
    res = {}
    clean = s.dropna()
    for q in q_vals:
        res[f"q_{q}"] = safe_float(np.quantile(clean, q))
    return {"quantiles": res, "rows_used": int(clean.count())}, warnings
