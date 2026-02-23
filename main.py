import streamlit as st
import pandas as pd
import requests

# -----------------------------
# PSX API Fetch Function
# -----------------------------
def fetch_psxterminal(symbol=None):
    """Fetch PSX data from psxterminal.com API (JSON)"""
    url = "https://psxterminal.com/api/market-data"
    params = {}
    if symbol:
        params["symbol"] = symbol.upper()
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data if isinstance(data, list) else [data])
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# -----------------------------
# Fake live quote function
# -----------------------------
def fetch_live_quote(symbol):
    """Fake live quote (replace with real API if available)"""
    df, err = fetch_psxterminal(symbol)
    if df.empty:
        return {"error": err or "No data"}
    return df.iloc[-1].to_dict()

# -----------------------------
# Fake chart pattern detection
# -----------------------------
def detect_chart_patterns(file_bytes):
    """Dummy pattern detection (replace with real ML/vision later)"""
    return {"pattern_detected": "Bullish Engulfing (example)"}

# -----------------------------
# Fake support/resistance
# -----------------------------
def detect_levels(df):
    """Dummy support/resistance based on min/max"""
    if df.empty:
        return {}
    levels = {
        "support": df["close"].min(),
        "resistance": df["close"].max()
    }
    return levels

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="PSX Analysis App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX)")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "PSX API Data",
    "Live Market Data",
    "Chart Pattern Detection",
    "Support & Resistance"
])

# -----------------------------
# Tab 1: PSX API Data
# -----------------------------
with tab1:
    st.header("PSX API Data Fetch")
    symbol = st.text_input("Enter PSX symbol (leave blank to fetch all):")
    df, error = fetch_psxterminal(symbol.strip() or None)
    if error:
        st.error(error)
    else:
        st.dataframe(df)

# -----------------------------
# Tab 2: Live Market Data
# -----------------------------
with tab2:
    st.header("Live PSX Quote")
    symbol = st.text_input("Enter PSX Symbol for Live Quote", key="live_symbol")
    if symbol:
        quote = fetch_live_quote(symbol.upper())
        st.json(quote)

# -----------------------------
# Tab 3: Chart Pattern Detection
# -----------------------------
with tab3:
    st.header("Upload Chart Image")
    file = st.file_uploader("Upload a candlestick chart image", type=["jpg","png"])
    if file:
        st.image(file, use_column_width=True)
        results = detect_chart_patterns(file.read())
        st.json(results)

# -----------------------------
# Tab 4: Support & Resistance
# -----------------------------
with tab4:
    st.header("Support & Resistance (API Data)")
    symbol_sr = st.text_input("Symbol for S/R", key="sr_symbol")
    if symbol_sr:
        df_sr, _ = fetch_psxterminal(symbol_sr.strip().upper())
        if df_sr.empty:
            st.error("No data found")
        else:
            levels = detect_levels(df_sr)
            st.write(levels)
