import streamlit as st
import pandas as pd
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
# Daily Price Sheet (UPLOAD)
# ------------------------------
with tab1:
    st.header("Daily Price Sheet (PSX)")
    file = st.file_uploader("Upload DPS CSV or Excel", type=["csv","xlsx"])
    if file:
        if file.name.endswith(".csv"):
            dps = pd.read_csv(file)
        else:
            dps = pd.read_excel(file)
        st.dataframe(dps)

# ------------------------------
# Live Market Data
# ------------------------------
with tab2:
    st.header("Live PSX Quote")
    symbol = st.text_input("Enter PSX Symbol (e.g., MEBL, OGDC, ENGRO)")
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
    st.header("Support/Resistance Levels (from uploaded DPS)")
    file = st.file_uploader("Upload DPS CSV/Excel for S/R detection", key="sr_file")
    if file:
        if file.name.endswith(".csv"):
            dps = pd.read_csv(file)
        else:
            dps = pd.read_excel(file)

        symbol = st.text_input("Symbol for S/R Detection", key="sr_symbol")
        if symbol:
            df = dps[dps["symbol"] == symbol.upper()]
            if df.empty:
                st.error("Symbol not found in uploaded DPS")
            else:
                df = df.sort_values("close", ascending=False).head(100)
                levels = detect_levels(df)
                st.write(levels)
