import streamlit as st
import pandas as pd
import sys
import os

# -----------------------------
# Add local folders to sys.path
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, "scrapers"))
sys.path.append(os.path.join(BASE_DIR, "analysis"))
sys.path.append(os.path.join(BASE_DIR, "ui"))

# Now imports should work even if Streamlit Cloud can't find modules
from psx_api_fetcher import fetch_psxterminal
from live_scraper import fetch_live_quote
from indicators import compute_indicators
from patterns import detect_chart_patterns
from support_resistance import detect_levels
from components import price_chart

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
