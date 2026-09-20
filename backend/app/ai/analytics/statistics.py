"""
Mathematical, statistical, and time-series helper utilities for EMBIP Analytics (Phase 11).
Pure Python, Pandas, and NumPy functions with zero side effects.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from app.ai.analytics.exceptions import CalculationError


def safe_float(val: Any) -> Optional[float]:
    """Safely converts a value to float, returning None if NaN, Inf, or invalid."""
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return None
        return round(f, 4)
    except (ValueError, TypeError):
        return None


def calculate_cagr_val(beginning_value: float, ending_value: float, years: float) -> Tuple[Optional[float], Optional[str]]:
    """
    Computes Compound Annual Growth Rate (CAGR).
    CAGR = (Ending Value / Beginning Value) ^ (1 / Years) - 1
    
    Validation:
    - beginning_value > 0
    - ending_value >= 0
    - years > 0
    """
    if years <= 0:
        return None, "CAGR calculation error: time period (years) must be greater than zero."
    if beginning_value <= 0:
        return None, "CAGR calculation error: beginning value must be greater than zero."
    if ending_value < 0:
        return None, "CAGR calculation error: ending value cannot be negative."

    try:
        cagr = ((ending_value / beginning_value) ** (1.0 / years) - 1.0) * 100.0
        return round(cagr, 2), None
    except Exception as e:
        return None, f"CAGR calculation exception: {str(e)}"


def calculate_percentage_change_val(beginning: float, ending: float) -> Tuple[Optional[float], Optional[str]]:
    """
    Computes percentage change: ((ending - beginning) / abs(beginning)) * 100
    If beginning == 0: returns None with a warning instead of Infinity.
    """
    if beginning == 0:
        return None, "Percentage change calculation warning: beginning value is zero (undefined percentage change)."
    
    pct = ((ending - beginning) / abs(beginning)) * 100.0
    return round(pct, 2), None


def parse_dates_series(series: pd.Series) -> Tuple[pd.Series, int]:
    """
    Parses a Pandas Series into datetime objects.
    Returns (datetime_series, missing_date_count).
    """
    parsed = pd.to_datetime(series, errors="coerce")
    missing_count = int(parsed.isna().sum())
    return parsed, missing_count
