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
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# -----------------------------
# Candlestick & SMA from Market Watch
# -----------------------------
def compute_sma(df, window=5):
    df['Close'] = pd.to_numeric(df['Close'].str.replace(',',''), errors='coerce')
    df['SMA'] = df['Close'].rolling(window=window).mean()
    return df

def plot_candlestick(df, symbol):
    df['Open'] = pd.to_numeric(df['Open'].str.replace(',',''), errors='coerce')
    df['High'] = pd.to_numeric(df['High'].str.replace(',',''), errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'].str.replace(',',''), errors='coerce')
    df['Close'] = pd.to_numeric(df['Close'].str.replace(',',''), errors='coerce')
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
    df['High'] = pd.to_numeric(df['High'].str.replace(',',''), errors='coerce')
    df['Low'] = pd.to_numeric(df['Low'].str.replace(',',''), errors='coerce')
    levels = {
        "support": round(df['Low'].min(), 2),
        "resistance": round(df['High'].max(), 2)
    }
    return levels

# -----------------------------
# Candlestick Image Analysis (Fixed for Streamlit Cloud)
# -----------------------------
def detect_patterns_from_image(uploaded_file):
    try:
        # Load with PIL and convert to numpy
        image = Image.open(uploaded_file).convert("RGB")
        img = np.array(image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=5, maxLineGap=3)

        if lines is None:
            return {"trend": "Unable to detect", "support": None, "resistance": None, "patterns": []}

        ys = [y1 for line in lines for x1, y1, x2, y2 in [line[0]]] + \
             [y2 for line in lines for x1, y1, x2, y2 in [line[0]]]
        support = int(np.percentile(ys, 90))
        resistance = int(np.percentile(ys, 10))
        trend = "Uptrend" if ys[-1] < ys[0] else "Downtrend" if ys[-1] > ys[0] else "Sideways"
        patterns = []
        if len(lines) > 50:
            patterns.append("Multiple candles detected (possible bullish/bearish)")

        return {"trend": trend, "support": support, "resistance": resistance, "patterns": patterns}

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
    if symbol_search and not df_market.empty:
        df_filtered = df_market[df_market.iloc[:,0].str.upper() == symbol_search.upper()]
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
    if symbol_chart and not df_market.empty:
        df_chart = df_market[df_market.iloc[:,0].str.upper() == symbol_chart.upper()]
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
    if symbol_sr and not df_market.empty:
        df_sr = df_market[df_market.iloc[:,0].str.upper() == symbol_sr.upper()]
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
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chart", use_column_width=True)
        results = detect_patterns_from_image(uploaded_file)  # <- fixed
        st.subheader("Analysis Results")
        st.json(results)
