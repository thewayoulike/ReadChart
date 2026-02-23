import streamlit as st
import pandas as pd
from scrapers.psx_api_fetcher import fetch_psxterminal
from scrapers.live_scraper import fetch_live_quote
from analysis.indicators import compute_indicators
from analysis.patterns import detect_chart_patterns
from analysis.support_resistance import detect_levels
from ui.components import price_chart

st.set_page_config(page_title="PSX Analysis App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX)")

tab1, tab2, tab3, tab4 = st.tabs([
    "PSX API Data",
    "Live Market Data",
    "Chart Pattern Detection",
    "Support & Resistance"
])

with tab1:
    st.header("PSX API Data Fetch")
    symbol = st.text_input("Enter PSX symbol (leave blank to fetch all):")
    df, error = fetch_psxterminal(symbol.strip() or None)

    if error:
        st.error(error)
    else:
        st.dataframe(df)

with tab2:
    st.header("Live PSX Quote")
    symbol = st.text_input("Enter PSX Symbol for Live Quote", key="live_symbol")
    if symbol:
        quote = fetch_live_quote(symbol.upper())
        st.json(quote)

with tab3:
    st.header("Upload Chart Image")
    file = st.file_uploader("Upload a candlestick chart image", type=["jpg","png"])
    if file:
        st.image(file, use_column_width=True)
        results = detect_chart_patterns(file.read())
        st.json(results)

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
