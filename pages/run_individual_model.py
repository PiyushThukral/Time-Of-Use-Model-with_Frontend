from dash import html, dcc, Output, Input, callback, Dash
from steps_module import step_upload_data, step_select_output_folder , step_render_graph , step_select_tou_dynamicity, select_tou_bins, first_last_continuity, step_upload_model_param, step_run_model, step_view_results, view_customer_profile
import dash
import plotly.graph_objs as go
from pages.cache import inputfileDirCache , SaveDirCache , ToUDynamicityCache , RepProfileCache , model_param_Cache ,OutputFileNameCache
import sys
from sklearn.ensemble import IsolationForest
import pages
from dash import Input, Output, State, callback, no_update
from dash import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import base64
import io
import base64
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import threading
import io
import sys
import os
import pandas as pd
import duckdb
import requests
import dash
import re
from dash.exceptions import PreventUpdate
from pages import new_betrand_VM
import chardet
import csv
from pages.cache import ConsumerListCache, TouBinsCache

log_buffer = io.StringIO()
model_thread = None
model_running = False


# -------------------------
# Helpers
# -------------------------
CONSUMER_PATTERNS = ["consumer", "cons_no", "cons no", "cons", "consumer_no", "consumer_number"]
MONTH_CANDIDATES = ["month"]  # case-insensitive match
CATEGORY_CANDIDATES = ["category", "category_code", "category code", "categorycode", "category_name"]
CONNECTED_LOAD_CANDIDATES = ["connected_load", "connected load", "sanctioned_load_kw", "sanctioned load", "sanctioned_load"]

import re
import duckdb
import pandas as pd
from pages.cache import ConsumerListCache, TimeBlockRangeCache

import pandas as pd
import duckdb
import os
import re

CONSUMER_PATTERNS = ["consumer", "cons_no", "cons no"]

def cache_timeblock_range(columns):
    """
    Identify time-block/hour columns and cache the first and last numeric indices.
    Works for patterns like ImportkWhTimeBlock1...48 or Consumption_Hr_1...24
    """
    import re

    tb_cols = _timeblock_columns(columns)
    if not tb_cols:
        print("[WARN] No timeblock columns detected.")
        return

    # Extract numeric parts from column names
    nums = []
    for c in tb_cols:
        match = re.search(r'(\d+)', c)
        if match:
            nums.append(int(match.group(1)))

    if nums:
        first = min(nums)
        last = max(nums)
        TimeBlockRangeCache.set(first, last)
    else:
        print("[WARN] No numeric suffix found in timeblock columns.")


def get_consumer_data(consumer_id: str) -> pd.DataFrame:
    """Return subset of data for a given consumer number from cached file."""
    path = inputfileDirCache.get()
    if not path or not os.path.exists(path):
        raise FileNotFoundError("❌ No valid data file found in cache.")

    is_duckdb = path.endswith(".duckdb")

    try:
        # ----------------------------
        # 1️⃣ Read limited rows first
        # ----------------------------
        if is_duckdb:
            con = duckdb.connect(path, read_only=True)
            tables = con.execute("SHOW TABLES").fetchall()
            if not tables:
                raise ValueError("❌ No tables found in DuckDB file.")
            table = tables[0][0]

            # Identify consumer column dynamically
            preview = con.execute(f"SELECT * FROM {table} LIMIT 5").fetchdf()
            cons_col = next(
                (c for c in preview.columns if any(p in c.lower() for p in CONSUMER_PATTERNS)),
                None
            )
            print(f"Found these columns in duckdb file: {cons_col}")
            if not cons_col:
                raise ValueError("❌ Consumer column not found in DuckDB table.")

            # Query only matching consumer data
            # query = f"SELECT * FROM {table} WHERE lower({cons_col}) = lower(?)"

            # Ensure consumer_id is treated as string
            consumer_str = str(consumer_id).strip()
            print(f"[CHECK] Selected Consumer Number: {consumer_str}")
            dtype_info = con.execute(f"PRAGMA table_info('{table}')").fetchdf()
            print("[DEBUG] DuckDB table info:")
            print(dtype_info)
            # # Use CAST to handle both numeric and string consumer columns
            # query = f"""
            #     SELECT * FROM {table}
            #     WHERE CAST({cons_col} AS VARCHAR) = ?
            # """
            # df = con.execute(query, [consumer_str]).fetchdf()
            try:
                consumer_num = float(consumer_id)
                query = f"SELECT * FROM {table} WHERE {cons_col} = ?"
                df = con.execute(query, [consumer_num]).fetchdf()
            except ValueError:
                # Fallback to string match
                consumer_str = str(consumer_id).strip()
                query = f"SELECT * FROM {table} WHERE CAST({cons_col} AS VARCHAR) = ?"
                df = con.execute(query, [consumer_str]).fetchdf()
            print(f"[TEST] Check df.shape: {df.shape} ")
            con.close()

        else:
            # Determine file type
            if path.endswith(".csv"):
                # Use encoding fallback
                for enc in ["utf-8", "utf-16", "latin1", "windows-1252"]:
                    try:
                        df = pd.read_csv(path, encoding=enc)
                        break
                    except Exception:
                        continue
                else:
                    raise ValueError("Unable to read CSV with common encodings.")
            else:
                df = pd.read_excel(path)

            # Find consumer column
            cons_col = next(
                (c for c in df.columns if any(p in c.lower() for p in CONSUMER_PATTERNS)),
                None
            )
            if not cons_col:
                raise ValueError("❌ Consumer column not found in file.")

            # Filter
            df = df[df[cons_col].astype(str).str.lower() == str(consumer_id).lower()]

        print(f"[INFO] Filtered {len(df)} rows for consumer {consumer_id} from {os.path.basename(path)}")
        return df

    except Exception as e:
        print(f"[ERROR] Failed to read consumer data: {e}")
        return pd.DataFrame()


def extract_and_cache_consumers(file_path):
    """Identify consumer column and cache unique values."""
    consumers = []
    try:
        # ----------- DuckDB -----------
        if file_path.lower().endswith(".duckdb"):
            con = duckdb.connect(file_path, read_only=True)
            tables = con.execute("SHOW TABLES").fetchall()
            if not tables:
                print("[WARN] No tables found in DuckDB.")
                return

            table_name = tables[0][0]
            df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
            con.close()

        # ----------- CSV -----------
        elif file_path.lower().endswith(".csv"):
            for enc in ["utf-8", "utf-16", "latin1", "windows-1252"]:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print("[ERROR] Could not read CSV with standard encodings.")
                return

        # ----------- Excel -----------
        elif file_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)

        else:
            print("[WARN] Unsupported file format.")
            return

        # ----------- Identify consumer column -----------
        df.columns = [str(c).strip() for c in df.columns]
        matched_cols = [c for c in df.columns if any(p in c.lower() for p in CONSUMER_PATTERNS)]

        if not matched_cols:
            print("[WARN] No consumer column found.")
            return

        cons_col = matched_cols[0]
        consumers = sorted(df[cons_col].unique().tolist())

        # ----------- Cache -----------
        ConsumerListCache.set(consumers)
        print(f"[CACHE] Cached {len(consumers)} consumer IDs from column '{cons_col}'.")

    except Exception as e:
        print(f"[ERROR] Failed to extract consumers: {e}")


def _file_kind(path: str) -> str:
    p = path.lower()
    if p.endswith(".duckdb"):
        return "duckdb"
    if p.endswith(".csv"):
        return "csv"
    if p.endswith(".xlsx") or p.endswith(".xls"):
        return "excel"
    return "unknown"


def _detect_encoding_and_delimiter(csv_path: str):
    with open(csv_path, "rb") as f:
        enc_detect = chardet.detect(f.read(50000))
    enc = enc_detect.get("encoding") or "utf-8"

    with open(csv_path, "r", encoding=enc, errors="ignore") as f:
        sample = f.read(4096)
        sniffer = csv.Sniffer()
        try:
            delim = sniffer.sniff(sample).delimiter
        except Exception:
            delim = ","
    return enc, delim


def _read_preview_df(path: str, limit_rows: int = 500) -> pd.DataFrame:
    kind = _file_kind(path)
    if kind == "duckdb":
        con = duckdb.connect(path, read_only=True)
        try:
            tables = con.execute("SHOW TABLES").fetchall()
            if not tables:
                return pd.DataFrame()
            table = tables[0][0]
            df = con.execute(f"SELECT * FROM {table} LIMIT {limit_rows}").fetchdf()
            return df
        finally:
            con.close()

    if kind == "csv":
        enc, delim = _detect_encoding_and_delimiter(path)
        df = pd.read_csv(path, nrows=limit_rows, encoding=enc, sep=delim, on_bad_lines="skip")
        return df

    if kind == "excel":
        return pd.read_excel(path, nrows=limit_rows)

    return pd.DataFrame()


def _find_first_matching_column(columns, candidates, contains_mode=True):
    """
    Return the first column name matching patterns.
    If contains_mode=True: match if any candidate substring is in col.lower().
    If contains_mode=False: exact (case-insensitive) match to any candidate.
    """
    cols_lower = {c.lower(): c for c in columns}
    # exact first
    if not contains_mode:
        for cand in candidates:
            if cand.lower() in cols_lower:
                return cols_lower[cand.lower()]
    # contains
    for c in columns:
        cl = c.lower()
        if any(pat in cl for pat in candidates):
            return c
    return None


def _timeblock_columns(columns):
    # Matches ImportkWhTimeBlock\d+ or Consumption_Hr_\d+ or ConsumptionHr\d+
    patt = re.compile(r"(ImportkWhTimeBlock\d+|Consumption_?Hr_\d+|ConsumptionHr\d+)", re.IGNORECASE)
    cols = [c for c in columns if patt.fullmatch(c)]
    if not cols:
        # Be more permissive: startswith patterns
        cols = [
            c for c in columns
            if c.lower().startswith("importkwhtimeblock")
            or c.lower().startswith("consumption_hr_")
            or c.lower().startswith("consumptionhr")
        ]
    return cols


def _read_distinct_months_for_consumer(path, cons_col, consumer_value, month_col):
    kind = _file_kind(path)
    if kind == "duckdb":
        con = duckdb.connect(path, read_only=True)
        try:
            table = con.execute("SHOW TABLES").fetchall()[0][0]
            q = f"""
                SELECT DISTINCT "{month_col}"
                FROM "{table}"
                WHERE CAST("{cons_col}" AS VARCHAR) = ?
                AND "{month_col}" IS NOT NULL
            """
            df = con.execute(q, [str(consumer_value)]).fetchdf()
        finally:
            con.close()
        months = sorted(df[month_col].astype(str).tolist()) if month_col in df.columns else []
        return months

    if kind == "csv":
        enc, delim = _detect_encoding_and_delimiter(path)
        # stream in small chunks; only two columns to reduce memory
        months_set = set()
        usecols = [cons_col, month_col]
        for chunk in pd.read_csv(path, encoding=enc, sep=delim, usecols=usecols, chunksize=100000, on_bad_lines="skip"):
            mask = chunk[cons_col].astype(str) == str(consumer_value)
            sub = chunk.loc[mask, month_col].dropna().astype(str).unique().tolist()
            months_set.update(sub)
        return sorted(months_set)

    if kind == "excel":
        df = pd.read_excel(path, usecols=[cons_col, month_col])
        df = df[df[cons_col].astype(str) == str(consumer_value)]
        return sorted(df[month_col].dropna().astype(str).unique().tolist())

    return []


def _read_profiles_subset(path, cons_col, month_col, consumer_value, month_value, meta_cols=None):
    """Return (df_subset, hr_cols, meta_dict)"""
    meta_cols = meta_cols or []
    kind = _file_kind(path)

    if kind == "duckdb":
        con = duckdb.connect(path, read_only=True)
        try:
            table = con.execute("SHOW TABLES").fetchall()[0][0]
            # Read one row first to detect HR columns reliably
            df_head = con.execute(f'SELECT * FROM "{table}" LIMIT 1').fetchdf()
            hr_cols = _timeblock_columns(df_head.columns)
            needed_cols = list({*hr_cols, cons_col, month_col, *meta_cols})
            q_cols = ", ".join([f'"{c}"' for c in needed_cols])
            q = f"""
                SELECT {q_cols}
                FROM "{table}"
                WHERE CAST("{cons_col}" AS VARCHAR)=? AND CAST("{month_col}" AS VARCHAR)=?
            """
            df = con.execute(q, [str(consumer_value), str(month_value)]).fetchdf()
            return df, hr_cols
        finally:
            con.close()

    if kind == "csv":
        enc, delim = _detect_encoding_and_delimiter(path)
        # Get header to figure out hr_cols and meta columns present
        header = pd.read_csv(path, nrows=0, encoding=enc, sep=delim)
        hr_cols = _timeblock_columns(header.columns)
        present_meta = [c for c in meta_cols if c in header.columns]
        usecols = list({*hr_cols, cons_col, month_col, *present_meta})

        frames = []
        for chunk in pd.read_csv(path, encoding=enc, sep=delim, usecols=usecols, chunksize=100000, on_bad_lines="skip"):
            mask = (chunk[cons_col].astype(str) == str(consumer_value)) & (chunk[month_col].astype(str) == str(month_value))
            sub = chunk.loc[mask]
            if not sub.empty:
                frames.append(sub)
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=usecols)
        return df, hr_cols

    if kind == "excel":
        # Load once; if big, consider openpyxl read-only, but this is simpler
        df_full = pd.read_excel(path)
        hr_cols = _timeblock_columns(df_full.columns)
        present_meta = [c for c in meta_cols if c in df_full.columns]
        needed = list({*hr_cols, cons_col, month_col, *present_meta})
        df = df_full.loc[
            (df_full[cons_col].astype(str) == str(consumer_value)) &
            (df_full[month_col].astype(str) == str(month_value)),
            needed
        ].copy()
        return df, hr_cols

    return pd.DataFrame(), []


def load_cached_df():
    """
    Unified data loader:
    1. If inputfileDirCache points to a valid file (.duckdb, .csv, .xlsx) → load from file.
    2. If not found or fails → fallback to API fetch.
    """

    fp = inputfileDirCache.get()
    df = None

    # ------------------------------------------------------------
    # 1️⃣ Try loading from local file (DuckDB / Excel / CSV)
    # ------------------------------------------------------------
    if fp and os.path.exists(fp):
        print(f"📂 Loading data from local file: {fp}")
        ext = os.path.splitext(fp)[1].lower()

        try:
            if ext == ".duckdb":
                con = duckdb.connect(fp)
                tables = con.execute("SHOW TABLES").fetchdf()["name"].tolist()
                if not tables:
                    raise ValueError("No tables found in DuckDB file.")
                table_name = tables[0]
                df = con.execute(f"SELECT * FROM {table_name}").fetchdf()
                con.close()

            elif ext in [".xls", ".xlsx"]:
                df = pd.read_excel(fp)

            elif ext == ".csv":
                df = pd.read_csv(fp)

        except Exception as e:
            print(f"⚠️ File read failed: {e}. Falling back to API...")

    # ------------------------------------------------------------
    # 2️⃣ If no local data → fallback to API
    # ------------------------------------------------------------
    # if df is None:
    #     try:
    #         api_url = "http://localhost:8000/api/data/latest"   # change when backend URL ready
    #         print(f"🌐 Fetching data from API: {api_url}")
    #         resp = requests.get(api_url, timeout=15)
    #         resp.raise_for_status()
    #         df = pd.read_json(resp.text)
    #     except Exception as e:
    #         print(f"❌ Failed to fetch from API: {e}")
    #         raise dash.exceptions.PreventUpdate

    # ------------------------------------------------------------
    # 3️⃣ Post-processing
    # ------------------------------------------------------------
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Date_str"] = df["Date"].dt.strftime("%Y-%m-%d")
    
    print("✅ Loaded DF shape:", df.shape)
    print("✅ Columns:", df.columns.tolist())
    print("✅ Dataframe Insights:")
    print(df.info())

    return df


# Layout
layout = html.Div(
    style={"display": "flex", "height": "100vh", "fontFamily": "Inter, sans-serif"},
    children=[
        dcc.Store(id="store-uploaded-file", storage_type="session"),

        # Left Panel – Step-by-step guide placeholder
        html.Div(
            style={
                "flex": "1",
                "padding": "20px",
                "backgroundColor": "#F9FAFB",
                "borderRight": "1px solid #E5E7EB",
                "overflowY": "auto"
            },
            children=[
                #html.H3("Steps Panel", style={"marginBottom": "20px"}),
                #html.P("This panel will later contain steps such as upload, settings, visualization, etc.")
                step_upload_data(),
                step_select_output_folder(),
                #step_render_graph(),
                #step_select_tou_dynamicity(),
                #step_select_representative_profile(),
                select_tou_bins(),
                first_last_continuity(),
                step_upload_model_param(),
                step_run_model(),
                step_view_results(),
                dcc.Store(id="store-uploaded-file"),
                dcc.Store(id="output-file-name-store"),
                # dcc.Store(id="store-uploaded-file"),        # file from CSV/Excel upload
                dcc.Store(id="duckdb-path-store"),          # file from DuckDB selection
                # dcc.Store(id="selected-hours-store"),       # ToU bins
                # dcc.Store(id="continuity-setting"),         # Continuity ON/OFF
                # dcc.Store(id="n-historical-days-store"),    # historical days input
                dcc.Store(id="selected-hours-store", storage_type="session"),
                dcc.Store(id = "continuity-setting", storage_type="session"),
                dcc.Store(id = "store-final-indiv-data", data =  {"data" : ""}, storage_type="session")
                #dcc.Store(id = "output-file-name-input", storage_type="session"),
            ]
        ),

        # Right Panel – Divided into 3 sections: logo, graph area, logs
        html.Div(
            style={"flex": "3", "display": "flex", "flexDirection": "column", "padding": "20px"},
            children=[


                # Middle: Interactive visualization area
                html.Div(
                    id="visualization-area",
                    style={
                        "flex": "1",
                        "backgroundColor": "#FFFFFF",
                        "border": "1px solid #E5E7EB",
                        "borderRadius": "10px",
                        "padding": "20px",
                        "marginBottom": "10px",
                        "overflowY": "auto"
                    },
                    children=[
                        #dcc.Graph(id='input-data-graph', style={'height': '400px'}),
                        #html.P("Interactive charts or outputs will appear here.")
                        view_customer_profile(),
                        dcc.Store(id="vis-consumer-col-store"),
                        dcc.Store(id="vis-month-col-store"),
                        dcc.Store(id="vis-meta-cols-store"),

                    ]
                ),

                # Bottom: Logs area
                html.Div(
                    id="logs-area",
                    style={
                        "height": "150px",
                        "backgroundColor": "#F3F4F6",
                        "border": "1px solid #D1D5DB",
                        "borderRadius": "10px",
                        "padding": "10px",
                        "fontSize": "13px",
                        "overflowY": "scroll",
                        "whiteSpace": "pre-line"
                    },
                    children=[
                        html.P("Logs will appear here...")
                    ]
                )
            ]
        )
    ]
)





dialog_lock = threading.Lock()

def open_output_folder_dialog(result_queue):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        folder_path = filedialog.askdirectory(parent=root)

        result_queue.put(folder_path)
    except Exception as e:
        result_queue.put(f"Error: {str(e)}")
    finally:
        try:
            root.destroy()
        except:
            pass


def select_output_directory():
    if not dialog_lock.acquire(blocking=False):
        return None

    result_queue = queue.Queue()

    try:
        dialog_thread = threading.Thread(
            target=open_output_folder_dialog, args=(result_queue,), daemon=True
        )
        dialog_thread.start()

        try:
            result = result_queue.get(timeout=300)
            if isinstance(result, str) and result.startswith("Error:"):
                return None
            return result
        except queue.Empty:
            return None
        finally:
            dialog_thread.join(timeout=1.0)
    finally:
        dialog_lock.release()





def get_scenario_df():
    
    fp = inputfileDirCache.get()  # this must return the full path to the uploaded file

    if os.path.exists(fp):
        df = pd.read_excel(
            fp,
            parse_dates=["Date"]
        )
        df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
        return df

    return None


def register_callbacks(app):

    #############################
    ####### STEP 1 ############## READ INPUT FILE
    #############################



    @app.callback(
        Output("data-input-area", "children"),
        Input("data-source-type", "value"),
    )
    def toggle_data_input(source_type):
        """Dynamically display the correct UI based on data source selection."""
        common_style = {
            "width": "100%",
            "height": "70px",
            "lineHeight": "70px",
            "borderWidth": "2px",
            "borderStyle": "dashed",
            "borderRadius": "12px",
            "textAlign": "center",
            "backgroundColor": "#f9f9f9",
            "color": "#555",
            "fontSize": "14px",
            "fontWeight": "500",
            "cursor": "pointer",
            "marginBottom": "10px",
        }

        # if source_type == "file":
        #     return html.Div([
        #         dcc.Upload(
        #             id="upload-data",
        #             children=html.Div("📂 Drag & drop or click to upload CSV/Excel file"),
        #             style=common_style,
        #             multiple=False
        #         ),
        #         html.Div(id="file-upload-status", style={
        #             "fontSize": "13px",
        #             "color": "#134A94",
        #             "marginTop": "8px"
        #         }),
        #     ])
        if source_type == "file":
            return html.Div([
                html.Div(
                    "📄 Click to select CSV/Excel file",
                    id="select-file-path-btn",
                    n_clicks=0,
                    style=common_style
                ),
                html.Div(id="file-upload-status", style={
                    "fontSize": "13px",
                    "color": "#134A94",
                    "marginTop": "8px"
                }),
            ])
            
        elif source_type == "duckdb":
            return html.Div([
                html.Div(
                    "🦆 Click to select DuckDB file",
                    id="select-duckdb-path-btn",
                    n_clicks=0,
                    style=common_style
                ),
                html.Div(id="duckdb-path-status", style={
                    "fontSize": "13px",
                    "color": "#134A94",
                    "marginTop": "8px"
                }),
            ])

        return html.Div("Please select a data source type above.")


    @app.callback(
        Output("file-upload-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("select-file-path-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def select_local_csv_excel(n_clicks):
        """Let the user pick a CSV/Excel file from disk and cache its path."""
        if not n_clicks:
            raise PreventUpdate

        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askopenfilename(
                title="Select CSV/Excel file",
                filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")],
            )
            root.destroy()

            if not file_path:
                msg = "❌ No file selected or dialog cancelled."
                return html.Div(msg, style={"color": "red"}), html.Div(msg)

            # cache the path for later readers
            inputfileDirCache.set(file_path)
            extract_and_cache_consumers(file_path)
            print(f"[CACHE] File selected: {file_path}")
            print(f"[VERIFY CSV/EXCEL] Cache now holds: {inputfileDirCache.get()}")
            # ✅ Try reading a small preview to verify and inspect columns
            try:
                # import pandas as pd

                if file_path.lower().endswith(".csv"):
                    df_preview = pd.read_csv(file_path)
                    print(f"[INFO] CSV file loaded successfully. Columns: {list(df_preview.columns)}")
                elif file_path.lower().endswith((".xlsx", ".xls")):
                    df_preview = pd.read_excel(file_path)
                    print(f"[INFO] Excel file loaded successfully. Columns: {list(df_preview.columns)}")
                else:
                    print("[WARN] Unsupported file format for preview.")

            except Exception as e:
                print(f"[ERROR] Failed to read preview: {e}")

            msg = f"✅ Selected file: {file_path}"
            return html.Div(msg, style={"color": "#134A94"}), html.Div(f"✅ File path saved: {file_path}")

        except Exception as e:
            err = f"❌ Error selecting file: {e}"
            return html.Div(err, style={"color": "red"}), html.Div(err)


    @app.callback(
        Output("duckdb-path-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("select-duckdb-path-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def select_duckdb_file(n_clicks):
        """Open DuckDB file picker safely from a background thread."""
        result_queue = queue.Queue()

        def open_dialog(q):
            import tkinter as tk
            from tkinter import filedialog
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                duck_path = filedialog.askopenfilename(
                    title="Select DuckDB File",
                    filetypes=[("DuckDB files", "*.duckdb")],
                )
                q.put(duck_path if duck_path else None)
            except Exception as e:
                q.put(f"Error: {e}")
            finally:
                try:
                    root.destroy()
                except:
                    pass

        t = threading.Thread(target=open_dialog, args=(result_queue,), daemon=True)
        t.start()
        t.join(timeout=60)  # wait for user to finish selecting

        duck_path = result_queue.get() if not result_queue.empty() else None
        if not duck_path or isinstance(duck_path, str) and duck_path.startswith("Error:"):
            msg = "❌ No file selected or dialog cancelled."
            return html.Div(msg, style={"color": "red"}), html.Div(msg)

        # ✅ Cache path
        inputfileDirCache.set(duck_path)
        print(f"[VERIFY DUCKDB TEST] Cache now holds: {inputfileDirCache.get()}")
        # ✅ Extract and cache consumers
        extract_and_cache_consumers(duck_path)
        print(f"[CACHE] DuckDB file set: {duck_path}")
        # ✅ Quick read check — verify file, table, and columns
        try:
            # import duckdb

            con = duckdb.connect(duck_path, read_only=True)
            tables = con.execute("SHOW TABLES").fetchall()

            if not tables:
                print("[WARN] No tables found in the DuckDB file.")
            else:
                table_name = tables[0][0]
                df_preview = con.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
                print(f"[INFO] DuckDB file read OK. Using table: '{table_name}'")
                print(f"[INFO] Columns: {list(df_preview.columns.to_list()[10])}")
                print(f"[INFO] Unique Consumers: {df_preview['CONS_NO'].unique()}")
                unique_consumers = df_preview['CONS_NO'].unique()
                del df_preview


            con.close()

        except Exception as e:
            print(f"[ERROR] Failed to read DuckDB file: {e}")


        msg = f"✅ Selected DuckDB file: {duck_path}"
        return html.Div(msg, style={"color": "#134A94"}), html.Div(f"✅ File path saved: {duck_path}")
    #############################
    ####### STEP 2 ############## SELECT OUTPUT DIRECTORY
    #############################    

    @app.callback(
        Output("selected-folder-path", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Output("output-folder-store", "data"),
        Input("select-output-folder-btn", "n_clicks"),
        #State("output-folder-input", "abs_path_folder"),
        prevent_initial_call=True
    )
    def on_select_folder(n_clicks):
        folder_path = select_output_directory()

        if not folder_path:
            return "❌ No folder selected or dialog cancelled.", html.Div("❌ No folder selected or dialog cancelled."), None

        try:
            os.makedirs(folder_path, exist_ok=True)
            abs_path = os.path.abspath(folder_path)
            SaveDirCache.set(abs_path)

            msg = f"✅ Output folder set to: {abs_path}"

            # abs_path_folder = {
            #     "output_path": abs_path,
            # }
            
            return msg, html.Div(msg), {"output_folder": abs_path}
        
        except Exception as e:
            err_msg = f"❌ Error setting folder: {str(e)}"
            return abs_path, err_msg, html.Div(err_msg), None
    
    #############################
    ####### STEP 2 ############## ENTER OUTPUT FILE NAME
    #############################   


    @app.callback(
        Output("output-file-name-store", "data"),
        Output("output-file-name-log", "children"),
        Input("confirm-output-filename-btn", "n_clicks"),
        State("output-file-name-input", "value"),
        prevent_initial_call=True
    )
    def store_output_file_name(n_clicks, file_name):
        if file_name:
            cleaned_name = file_name.strip()
            print("file_name_testing_ok")
            if not cleaned_name or cleaned_name.lower() in ['output', 'con', 'nul']:  # Windows reserved words
                return no_update, "⚠️ Please enter a valid output file name."
            print("file_cache_testing_ok")
            OutputFileNameCache.set(cleaned_name)
            return cleaned_name, f"✅ Output file name saved as: {cleaned_name}.xlsx"

        OutputFileNameCache.set(None)
        return "", "⚠️ Please enter a valid output file name."

    #############################
    ####### STEP 3 ############## VISUALIZE PLOTS
    #############################



    @app.callback(
        Output("consumer-dropdown", "options",allow_duplicate=True),
        Output("consumer-dropdown", "disabled"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("file-upload-status", "children"),   # CSV/Excel
        Input("duckdb-path-status", "children"),   # DuckDB
        State("file-upload-status","value"),
        State("duckdb-path-status", "value"),
        prevent_initial_call=True,
    )
    def populate_consumer_dropdown(uploaded_csv, uploaded_duckdb, uploaded_csv_path, uploaded_duckb_path):
        
        """Populate consumers only after path exists in cache."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        
        print("[DEBUG] populate_consumer_dropdown triggered!")
        path = inputfileDirCache.get()
        print(f"[DEBUG] Cached path in callback: {path}")
        if not path or not os.path.exists(path):
            raise dash.exceptions.PreventUpdate

        if path is not None:
            # Extract consumer list once from file
            print("[TEST] inside test of uploaded csv and duckdb")
            extract_and_cache_consumers(path)
            consumers = ConsumerListCache.get()

            if not consumers:
                return [], True

            opts = [{"label": c, "value": c} for c in consumers]
            print(f"[INFO] Populated {len(opts)} initial consumers")
            msg = f"✅ Populated {len(opts)} consumers for View in drop-down: {len(opts)}"
        return opts, False, html.Div(msg)

    @app.callback(
        Output("consumer-dropdown", "options", allow_duplicate=True),
        Input("consumer-dropdown", "search_value"),
        prevent_initial_call=True,
    )
    def lazy_filter_consumers(search_text):
        consumers = ConsumerListCache.get()
        if not consumers:
            raise dash.exceptions.PreventUpdate

        if not search_text:
            subset = consumers
        else:
            subset = [c for c in consumers if search_text.lower() in str(c).lower()]

        opts = [{"label": c, "value": c} for c in subset]
        print(f"[INFO] Filtered {len(opts)} consumers for '{search_text}'")
        return opts


    # ------------------------------------------------------
    # 2) Populate Month dropdown after a Consumer is selected
    # ------------------------------------------------------
    @app.callback(
        Output("month-dropdown", "options", allow_duplicate=True),
        Output("month-dropdown", "disabled", allow_duplicate=True),
        Input("consumer-dropdown", "value"),
        State("vis-consumer-col-store", "data"),
        State("vis-month-col-store", "data"),
        prevent_initial_call=True,
    )
    def load_month_dropdown(selected_consumer, cons_col, month_col):
        if not selected_consumer or not cons_col:
            raise PreventUpdate

        path = inputfileDirCache.get()
        if not path or not os.path.exists(path):
            raise PreventUpdate

        if not month_col:
            # If there's no month column, disable and return empty options
            return [], True

        try:
            months = _read_distinct_months_for_consumer(path, cons_col, selected_consumer, month_col)
            options = [{"label": str(m), "value": str(m)} for m in months]
            return options, False if options else True
        except Exception as e:
            print(f"[ERROR] Month load failed: {e}")
            return [], True

    # import dash
    # from dash import Input, Output
    # import plotly.graph_objects as go
    # import pandas as pd
    # import re

    # Assuming get_consumer_data() and _timeblock_columns() are already defined and imported
    # and inputfileDirCache is available globally

    @app.callback(
        Output("profile-graph", "figure", allow_duplicate=True),
        Output("profile-info", "children", allow_duplicate=True),
        Input("consumer-dropdown", "value"),
        # Input("month-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_graph(selected_consumer): #, selected_month):
        """
        Plot the consumer profile for the selected consumer and month.
        Works for CSV/Excel/DuckDB files using inputfileDirCache.get().
        """
        if not selected_consumer:
            raise dash.exceptions.PreventUpdate

        # ----------------------------------------------------------------
        # 1️⃣ Read consumer-specific data (already filtered by consumer_id)
        # ----------------------------------------------------------------
        df = get_consumer_data(selected_consumer)
        if df.empty:
            fig = go.Figure().update_layout(
                title=f"⚠️ No data found for Consumer: {selected_consumer}",
                template="plotly_white"
            )
            return fig, f"⚠️ No data found for {selected_consumer}"

        # # ----------------------------------------------------------------
        # # 2️⃣ Filter by Month (if available)
        # # ----------------------------------------------------------------
        # month_col = next((c for c in df.columns if c.lower() in ["month", "mon"]), None)
        # if selected_month and month_col:
        #     df = df[df[month_col] == selected_month]
        #     print(f"[INFO] Filtered {len(df)} rows for month {selected_month}")

        # ----------------------------------------------------------------
        # 3️⃣ Extract relevant timeblock / hourly columns
        # ----------------------------------------------------------------
        hr_cols = _timeblock_columns(df.columns)
        cache_timeblock_range(df.columns)
        tb_range = TimeBlockRangeCache.get()
        print(f"[TEST] The hour_cols are {hr_cols}")
        print(f"[TEST CACHE COMMAND] First block: {tb_range['first']}, Last block: {tb_range['last']}")
        if not hr_cols:
            fig = go.Figure().update_layout(
                title="⚠️ No time-block columns found (expected ImportkWhTimeBlock or Consumption_Hr_)",
                template="plotly_white"
            )
            return fig, "⚠️ No valid time-block data available."

        # Sort columns numerically (important for consistent x-axis)
        hr_cols = sorted(hr_cols, key=lambda x: int(re.findall(r"\d+", x)[0]))

        # ----------------------------------------------------------------
        # 4️⃣ Identify metadata columns for info display
        # ----------------------------------------------------------------
        meta_cols = [c for c in df.columns if any(k in c.lower() for k in ["category", "connected", "load"])]
        meta_info = {}
        for c in meta_cols:
            val = df[c].iloc[0] if c in df.columns and not df[c].empty else None
            meta_info[c] = val

        # ----------------------------------------------------------------
        # 5️⃣ Create the Plotly Figure
        # ----------------------------------------------------------------
        fig = go.Figure()
        for idx, row in df.iterrows():
            if 'Date' in df.columns:
                # Handle datetime or string type date values
                date_label = (
                    row['Date'].strftime("%Y-%m-%d") 
                    if pd.api.types.is_datetime64_any_dtype(df['Date']) 
                    else str(row['Date'])
                )
                trace_name = f"{date_label}"
            else:
                trace_name = f"Day {idx + 1}"
            fig.add_trace(go.Scatter(
                x=list(range(1, len(hr_cols) + 1)),
                y=row[hr_cols].values,
                mode="lines",
                # name=f"Day {idx + 1}" if 'day' not in df.columns else f"Day {df.loc[idx, 'day']}",
                name = trace_name,
                opacity=0.4,
                line=dict(width=1),
                hoverinfo="x+y+name"
            ))

        fig.update_layout(
            title=f"Consumer {selected_consumer} Load Profile",
            # xaxis=dict(title="Time Block", tickmode="linear", dtick=1),
            xaxis=dict(
                tickmode="linear",
                tick0=1,
                dtick=1,
                range=[1, len(hr_cols)],
                title="Time Block",
                tickangle=90   # ✅ rotate labels vertically
            ),
            yaxis=dict(title="Load (kW)"),
            template="plotly_white",
            margin=dict(t=50, l=50, r=30, b=50),
            height=450
        )

        # ----------------------------------------------------------------
        # 6️⃣ Create info summary
        # ----------------------------------------------------------------
        info_text = f"""
        📊 **Consumer No:** {selected_consumer}  
        🏷️ **Category:** {meta_info.get('category', 'N/A')}  
        ⚡ **Connected Load:** {meta_info.get('connected_load', 'N/A')}
        """
        # 📅 **Month:** {selected_month if selected_month else 'All'} 

        return fig, info_text




    #############################
    ####### STEP 4 ############## SELECT TOU DYNAMICITY
    #############################

    @app.callback(
        Output("tou-selection-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("tou-dynamicity-radio", "value"),
        prevent_initial_call=True
    )
    def store_tou_dynamicity(selection):
        ToUDynamicityCache.set(selection)
        msg = f"✅ ToU dynamicity set to: {selection}"
        return msg, html.Div(msg)
    
    #############################
    ####### STEP 4 ############## SELECT HOUR BINS
    #############################


    @app.callback(
        Output("selected-hours-store", "data"),
        Output("tou-bins-feedback", "children"),
        Input("confirm-tou-bins", "n_clicks"),
        State("tou-bins-input", "value"),
        prevent_initial_call=True
    )
    def confirm_tou_bins(n_clicks, input_text):
        """Validate and store ToU bin selections."""
        if not input_text:
            return dash.no_update, "⚠️ Please enter at least one time block."

        # Parse numbers (split by comma or pipe)
        parts = re.split(r"[,\|]", input_text)
        try:
            hours = sorted(set(int(p.strip()) for p in parts if p.strip().isdigit()))
        except ValueError:
            return dash.no_update, "❌ Invalid entry: please enter integers only."

        tb_range = TimeBlockRangeCache.get()
        # Retrieve valid time range from cache
        start_hr = tb_range['first']
        end_hr = tb_range['last']

        # Validate range
        invalid = [h for h in hours if h < start_hr or h > end_hr]
        if invalid:
            return dash.no_update, f"❌ Invalid hour(s): {invalid}. Must be within [{start_hr}, {end_hr}]."

        if len(hours) < 2:
            return dash.no_update, "⚠️ You need at least two breakpoints to form bands."

        TouBinsCache.set(hours)
        print(f" [CACHE TEST] Tou Bins Set by user : {TouBinsCache.get()}")
        msg = f"✅ ToU bands updated successfully: {hours}"
        print(f"[INFO] Updated ToU hours: {hours}")
        return hours, msg



    @app.callback(
        Output("profile-graph", "figure", allow_duplicate=True),
        Output("logs-area", "children", allow_duplicate=True),
        Input("selected-hours-store", "data"),
        State("profile-graph", "figure"),
        State("keep-continuous-bins", "value"),  # Checkbox/Radio from user
        prevent_initial_call=True
    )
    def update_tou_bands(selected_hours, current_fig, keep_continuity):
        """Draw ToU bands and vertical markers — default continuity ON."""
        # import numpy as np

        if not current_fig:
            raise dash.exceptions.PreventUpdate

        fig = go.Figure(current_fig)
        fig.update_layout(shapes=[])  # Clear existing bands

        if not selected_hours:
            return fig, "⚠️ No ToU hours selected."

        # --- Sort and deduplicate selected hours ---
        selected_hours = sorted(set(map(int, selected_hours)))
        logs = [f"Selected ToU breakpoints: {selected_hours}"]

        # --- Assume full range of timeblocks (e.g., 1 to N) ---
        # You can later replace this with actual hour range cache
        total_blocks = int(max(selected_hours))
        start_hour = 1
        end_hour = total_blocks

        # --- Build bands ---
        bands = []

        # Add initial band (1 to first)
        if selected_hours[0] > start_hour:
            bands.append((start_hour, selected_hours[0]))

        # Add inner consecutive bands
        bands.extend([(selected_hours[i], selected_hours[i + 1]) for i in range(len(selected_hours) - 1)])

        # Add final band (last to end_hour)
        if selected_hours[-1] < end_hour:
            bands.append((selected_hours[-1], end_hour))

        # --- Colors ---
        colors = [
            "rgba(255, 99, 71, 0.25)",   # Tomato
            "rgba(54, 162, 235, 0.25)",  # Blue
            "rgba(255, 206, 86, 0.25)",  # Yellow
            "rgba(75, 192, 192, 0.25)",  # Teal
            "rgba(153, 102, 255, 0.25)", # Purple
            "rgba(255, 159, 64, 0.25)"   # Orange
        ]

        # --- Continuity setting ---
        continuity_on = True
        if keep_continuity and isinstance(keep_continuity, list):
            if any(str(v).lower() in ["no", "false", "0"] for v in keep_continuity):
                continuity_on = False

        # --- Apply continuity coloring ---
        for i, (start_hr, end_hr) in enumerate(bands):
            # continuity rule: (1, first) and (last, end) same color
            if continuity_on and (
                (start_hr == start_hour and end_hr == selected_hours[0]) or
                (start_hr == selected_hours[-1] and end_hr == end_hour)
            ):
                color = colors[0]
            else:
                color = colors[i % len(colors)]

            fig.add_shape(
                type="rect",
                x0=start_hr , #- 0.5,
                x1=end_hr, # + 0.5,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                fillcolor=color,
                opacity=0.3,
                layer="below",
                line_width=0,
            )

            logs.append(f"🟩 Band {i+1}: {start_hr}–{end_hr}, Color: {color}")

        # --- Add vertical lines at selected hours ---
        for hr in selected_hours:
            fig.add_vline(
                x=hr,
                line=dict(color="red", dash="dash", width=1),
                opacity=0.9,
                annotation_text=f"{hr}",
                annotation_position="top",
            )

        # --- Layout settings ---
        fig.update_layout(
            title="Consumer Load Profile with ToU Bands",
            xaxis=dict(title="Time Block", tickangle=90),
            yaxis=dict(title="Load (kW)"),
        )

        logs.append("✅ Vertical red lines added at selected breakpoints.")
        if continuity_on:
            logs.append("🔁 Continuity ON: (1,first) and (last,end) bands share same color.")
        else:
            logs.append("⚠️ Continuity OFF: all bands distinct.")

        return fig, "\n".join(logs)




    #############################
    ####### STEP 5 ############## CONTINUITY OF FIRST LAST BLOCK SETTINGS
    #############################


    @app.callback(
        Output('continuity-setting', 'data'),
        Input('keep-continuous-bins', 'value')
    )
    def update_continuity_setting(value):
        print(f"Continuity Setting is {value}")
        return {'setting': value}

    #############################
    ####### STEP 6 ############## UPLOAD MODEL PARAMETER FILE
    #############################

    @app.callback(
        Output("store-param-file", "data"),
        Output("model-param-upload-status", "children"),
        Output("logs-area", "children", allow_duplicate=True),
        Input("upload-model-params", "contents"),
        State("upload-model-params", "filename"),
        #State("logs-area", "children"),
        prevent_initial_call=True,
    )
    def handle_param_upload(contents, filename):
        if not contents:
            raise PreventUpdate

        try:
            # Decode content
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Save locally
            os.makedirs("temp_data", exist_ok=True)
            file_path = os.path.join("temp_data", filename)

            with open(file_path, "wb") as f:
                f.write(decoded)

            # Cache path for later use
            model_param_Cache.set(file_path)

            print(f"Model param file is {filename} and save dir is {model_param_Cache.get()}")

            # Store file data in memory (for later inspection or plotting)
            param_data = {
                "filename": filename,
                "path": file_path
            }

            return (
                param_data,
                html.Div(f"✅ Uploaded file: {filename}"),
                html.Div(f"✅ File {filename} saved to {file_path}")
            )

        except Exception as e:
            return (
                no_update,
                html.Div("❌ Upload failed."),
                html.Div(f"❌ Error: {str(e)}")
            )
    

    #############################
    ####### STEP 6 ############## 
    #############################




    #############################
    ####### STEP 7 ############## RUN MODEL
    #############################

    from datetime import datetime



    @app.callback(
        Output("logs-area", "children", allow_duplicate=True),
        Input("run-tou-button", "n_clicks"),
        State("store-param-file", "data"),             # Model parameter file info
        State("selected-hours-store", "data"),         # ToU bins
        State("continuity-setting", "data"),           # Continuity
        State("output-folder-store", "data"),          # Output folder
        State("output-file-name-store", "data"),       # File name + total blocks + n_days
        prevent_initial_call=True
    )
    def run_tou_model(n_clicks, model_param, tou_bins, cont_setting,
                    output_folder_store, file_settings):

        print("\n🟢 Running TOU model callback...")

        if not n_clicks:
            raise dash.exceptions.PreventUpdate


        # --- Collect inputs ---
        output_path = SaveDirCache.get() # if isinstance(output_folder_store, dict) else output_folder_store
        customer_data_path = inputfileDirCache.get()   # path from cache
        model_param_path = model_param.get("path")
        output_file_name = OutputFileNameCache.get()
        
        n_historical_days = 30  

        tb_range = TimeBlockRangeCache.get()
        # Retrieve valid time range from cache
        total_time_blocks_modelled = tb_range['last']

        print("📦 Preparing model inputs...")
        print(f"[TESTING RUN TOU] Customer File Path     : {customer_data_path}")
        print(f"[TESTING RUN TOU] Model Param File Path  : {model_param_path}")
        print(f"[TESTING RUN TOU] Output Folder          : {output_path}")
        print(f"[TESTING RUN TOU] ToU Bins               : {tou_bins}")
        print(f"[TESTING RUN TOU] Continuity Setting     : {cont_setting}")
        print(f"[TESTING RUN TOU] Output File Name       : {output_file_name}")
        print(f"[TESTING RUN TOU] Timestamped Name       : {output_file_name_dt}")
        print(f"[TESTING RUN TOU] Total Time Blocks      : {total_time_blocks_modelled}")
        print(f"[TESTING RUN TOU] Historical Days        : {n_historical_days}")

        # --- Validate inputs ---
        if not (customer_data_path):
            return html.Div("⚠️ No customer data file selected.")
        if not model_param_path:
            return html.Div("⚠️ No model parameter file provided.")
        if not tou_bins:
            return html.Div("⚠️ Please select ToU Time Bands.")
        if not cont_setting:
            return html.Div("⚠️ Continuity setting missing.")
        if not output_folder_store:
            return html.Div("⚠️ Output folder not selected.")
        if not output_file_name:
            return html.Div("⚠️ Output file not selected.")
        if not file_settings:
            return html.Div("⚠️ Model settings missing (check output name or total blocks).")
        
        
        # --- Continuity setting ---
        cont_set = cont_setting.get("setting") if isinstance(cont_setting, dict) else cont_setting

        # --- Timestamped output name ---
        now = datetime.now()
        datetime_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        output_file_name_dt = f"{output_file_name}_{datetime_string}"

        # --- Prepare log buffer ---
        buffer = io.StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = buffer



        try:
            # --- Call your model run function ---
            pages.new_betrand_VM.run(
                customer_data_file=customer_data_path,
                model_input_file=model_param_path,
                output_folder=output_path,
                output_file_name_str=output_file_name_dt,
                tou_bins=sorted(tou_bins),
                total_time_blocks_modelled=total_time_blocks_modelled,
                cont_setting=cont_set,
                output_file_name_by_user=output_file_name,
                n_historical_days=n_historical_days
            )

            print(f"✅ Model run complete. Output saved as: {output_file_name_dt}.xlsx")

        except Exception as e:
            print(f"❌ Error while running TOU model: {e}")

        finally:
            sys.stdout = sys_stdout_backup

        logs = buffer.getvalue()
        buffer.close()

        return html.Pre(logs, style={"whiteSpace": "pre-wrap", "fontSize": "13px"})




    #############################
    ####### STEP 10 #############
    #############################



    @app.callback(
        Output("trigger-new-tab", "children"),
        Input("view-optariff-results", "n_clicks"),
        Input("compare-optariff-results", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_new_tab(n1, n2):
        triggered_id = ctx.triggered_id
        if triggered_id == "view-optariff-results":
            return html.Script('window.open("/load-graphs", "_blank");')
        elif triggered_id == "compare-optariff-results":
            return html.Script('window.open("/compare-results", "_blank");')
        return dash.no_update


