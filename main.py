import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image
import numpy as np
import cv2
import plotly.graph_objects as go

# -----------------------------
# PSX Market Watch Scraper
# -----------------------------
def fetch_psx_market_watch():
    url = "https://dps.psx.com.pk/market-watch"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table")
        if not table:
            return pd.DataFrame(), "No table found on the page"
        headers = [th.text.strip() for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all("td")]
            if cells:
                rows.append(cells)
        df = pd.DataFrame(rows, columns=headers)
        df = normalize_market_watch_columns(df)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# -----------------------------
# Normalize Column Names
# -----------------------------
def normalize_market_watch_columns(df):
    df = df.rename(columns=lambda x: x.strip())  # remove extra spaces
    col_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'high' in col_lower:
            col_map[col] = 'High'
        elif 'low' in col_lower:
            col_map[col] = 'Low'
        elif 'open' in col_lower:
            col_map[col] = 'Open'
        elif 'close' in col_lower:
            col_map[col] = 'Close'
        elif 'symbol' in col_lower:
            col_map[col] = 'Symbol'
    df = df.rename(columns=col_map)
    return df

# -----------------------------
# Candlestick & SMA
# -----------------------------
def compute_sma(df, window=5):
    # Make sure Close exists
    if 'Close' not in df.columns:
        return df
    df['Close'] = pd.to_numeric(df['Close'].str.replace(',',''), errors='coerce')
    df['SMA'] = df['Close'].rolling(window=window).mean()
    return df

def plot_candlestick(df, symbol):
    for col in ['Open', 'High', 'Low', 'Close']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(',',''), errors='coerce')
        else:
            df[col] = 0  # fallback if column missing

    df['Date'] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))
    
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=symbol
    )])
    if 'SMA' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['SMA'],
            mode='lines',
            name='SMA'
        ))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig

# -----------------------------
# Support & Resistance
# -----------------------------
def detect_levels(df):
    for col in ['High', 'Low']:
        if col not in df.columns:
            return {"error": f"Missing {col} column"}
        df[col] = pd.to_numeric(df[col].str.replace(',',''), errors='coerce')
    levels = {
        "support": round(df['Low'].min(), 2),
        "resistance": round(df['High'].max(), 2)
    }
    return levels

# -----------------------------
# Image Analysis (trend & patterns)
# -----------------------------
def detect_patterns_from_image(image_bytes):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"error": "Cannot decode image. Make sure it is a valid PNG/JPG."}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=5, maxLineGap=3)

        if lines is None:
            return {"trend": "Unable to detect", "patterns": []}

        ys = [y1 for line in lines for x1, y1, x2, y2 in [line[0]]] + \
             [y2 for line in lines for x1, y1, x2, y2 in [line[0]]]
        trend = "Uptrend" if ys[-1] < ys[0] else "Downtrend" if ys[-1] > ys[0] else "Sideways"
        patterns = []
        if len(lines) > 50:
            patterns.append("Multiple candles detected (possible bullish/bearish)")

        return {"trend": trend, "patterns": patterns}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Streamlit Page
# -----------------------------
st.set_page_config(page_title="PSX Analysis App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX)")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Market Watch Table",
    "Search Symbol",
    "Candlestick Chart",
    "Support & Resistance",
    "Candlestick Image Analysis"
])

# -----------------------------
# Tab 1: Full Market Watch
# -----------------------------
with tab1:
    st.header("Full PSX Market Watch")
    df_market, error = fetch_psx_market_watch()
    if error:
        st.error(error)
    else:
        st.dataframe(df_market)

# -----------------------------
# Tab 2: Search Symbol
# -----------------------------
with tab2:
    st.header("Search PSX Symbol")
    symbol_search = st.text_input("Enter Symbol to search (e.g., MEBL, OGDC):", key="search")
    if symbol_search and not df_market.empty and 'Symbol' in df_market.columns:
        df_filtered = df_market[df_market['Symbol'].str.upper() == symbol_search.upper()]
        if df_filtered.empty:
            st.warning(f"No data found for {symbol_search.upper()}")
        else:
            st.dataframe(df_filtered)

# -----------------------------
# Tab 3: Candlestick Chart
# -----------------------------
with tab3:
    st.header("Candlestick Chart with SMA")
    symbol_chart = st.text_input("Enter Symbol for chart:", key="chart")
    if symbol_chart and not df_market.empty and 'Symbol' in df_market.columns:
        df_chart = df_market[df_market['Symbol'].str.upper() == symbol_chart.upper()]
        if df_chart.empty:
            st.error("No data found for symbol in Market Watch")
        else:
            df_chart = compute_sma(df_chart, window=5)
            fig = plot_candlestick(df_chart, symbol_chart.upper())
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Tab 4: Support & Resistance
# -----------------------------
with tab4:
    st.header("Support & Resistance Levels")
    symbol_sr = st.text_input("Enter Symbol for S/R:", key="sr")
    if symbol_sr and not df_market.empty and 'Symbol' in df_market.columns:
        df_sr = df_market[df_market['Symbol'].str.upper() == symbol_sr.upper()]
        if df_sr.empty:
            st.error("No data found for symbol in Market Watch")
        else:
            levels = detect_levels(df_sr)
            st.write(levels)

# -----------------------------
# Tab 5: Candlestick Image Analysis
# -----------------------------
with tab5:
    st.header("Upload Candlestick Chart Image")
    uploaded_file = st.file_uploader("Upload chart image (jpg/png)", type=["jpg","png"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chart", use_column_width=False)
        results = detect_patterns_from_image(file_bytes)
        st.subheader("Analysis Results")
        st.json(results)
