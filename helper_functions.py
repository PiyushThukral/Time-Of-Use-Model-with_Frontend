import pandas as pd
import duckdb
from config import CONSUMER_PATTERNS, STANDARD_CONSUMER_COLUMN, CATEGORY_PATTERNS
from pages.cache import ConsumerListCache


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


def read_file_generic(file_path: str) -> pd.DataFrame:
    """Read a file (DuckDB, CSV, Excel) and return as DataFrame."""
    if file_path.lower().endswith(".duckdb"):
        con = duckdb.connect(file_path, read_only=True)
        tables = con.execute("SHOW TABLES").fetchall()
        if not tables:
            raise ValueError("No tables found in DuckDB file.")
        table_name = tables[0][0]
        df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
        con.close()
        return df

    elif file_path.lower().endswith(".csv"):
        for enc in ["utf-8", "utf-16", "latin1", "windows-1252"]:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError("Could not read CSV with standard encodings.")

    elif file_path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)

    else:
        raise ValueError(f"Unsupported file format: {file_path}")
