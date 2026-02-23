import streamlit as st
import pandas as pd
from scrapers.psx_csv_fetcher import fetch_psx_data
from scrapers.live_scraper import fetch_live_quote
from analysis.indicators import compute_indicators
from analysis.patterns import detect_chart_patterns
from analysis.support_resistance import detect_levels
from ui.components import price_chart

st.set_page_config(page_title="PSX Analysis App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX)")

tab1, tab2, tab3, tab4 = st.tabs([
    "Daily Price Sheet",
    "Live Market Data",
    "Chart Pattern Detection",
    "Support & Resistance"
])

# ------------------------------
# Daily Price Sheet (AUTO FETCH)
# ------------------------------
with tab1:
    st.header("Daily Price Sheet (PSX)")
    symbols_input = st.text_input("Enter symbols separated by comma (default top 5):", 
                                  value="MEBL,OGDC,UBL,ENGRO,HBL")
    symbols = [s.strip().upper() for s in symbols_input.split(",")]

    st.info("Fetching PSX data...")
    dps = fetch_psx_data(symbols)
    if dps.empty:
        st.error("Failed to fetch PSX data. Check symbols or network.")
    else:
        st.dataframe(dps)

# ------------------------------
# Live Market Data
# ------------------------------
with tab2:
    st.header("Live PSX Quote")
    symbol = st.text_input("Enter PSX Symbol (e.g., MEBL, OGDC, ENGRO)", key="live_symbol")
    if symbol:
        quote = fetch_live_quote(symbol.upper())
        st.json(quote)

# ------------------------------
# Pattern Detection
# ------------------------------
with tab3:
    st.header("Upload Chart Image")
    file = st.file_uploader("Upload a candlestick chart image", type=["jpg","png"])
    if file:
        st.image(file, caption="Uploaded Chart", use_column_width=True)
        results = detect_chart_patterns(file.read())
        st.subheader("Detected Patterns")
        st.json(results)

# ------------------------------
# Support & Resistance
# ------------------------------
with tab4:
    st.header("Support/Resistance Levels (Auto PSX Data)")
    symbol = st.text_input("Symbol for S/R Detection", key="sr_symbol")
    if symbol:
        df = dps[dps["symbol"] == symbol.upper()]
        if df.empty:
            st.error("Symbol not found in fetched data")
        else:
            df = df.sort_values("close", ascending=False).head(100)
            levels = detect_levels(df)
            st.write(levels)
