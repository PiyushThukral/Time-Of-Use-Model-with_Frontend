
import pandas as pd
import duckdb
from config import CONSUMER_PATTERNS, CATEGORY_PATTERNS, CONNECTED_LOAD_PATTERNS, METER_NUMBER_PATTERNS


def identify_consumer_column(df: pd.DataFrame):
    """Return the first matching consumer column based on pattern list."""
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in CONSUMER_PATTERNS):
            return col
    return None


def identify_category_column(df: pd.DataFrame):
    """Return the first matching category column based on pattern list."""
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in CATEGORY_PATTERNS):
            return col
    return None


def identify_connected_load_column(df: pd.DataFrame):
    """Return the first matching connected load column based on pattern list."""
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in CONNECTED_LOAD_PATTERNS):
            return col
    return None


def identify_meter_number_column(df: pd.DataFrame):
    """Return the first matching meter number column based on pattern list."""
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in METER_NUMBER_PATTERNS):
            return col
    return None

