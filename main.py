import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
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
# Fetch Historical Stock Data
# -----------------------------
def fetch_stock_data(symbol, period="6mo", interval="1d"):
    try:
        df = yf.download(symbol + ".PK", period=period, interval=interval)
        if df.empty:
            return pd.DataFrame(), f"No data found for {symbol}"
        df.reset_index(inplace=True)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# -----------------------------
# Compute SMA
# -----------------------------
def compute_sma(df, window=20):
    df[f"SMA_{window}"] = df['Close'].rolling(window=window).mean()
    return df

# -----------------------------
# Plot Candlestick
# -----------------------------
def plot_candlestick(df, sma_window=20):
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Candlestick"
    )])
    if f"SMA_{sma_window}" in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df[f"SMA_{sma_window}"],
            mode='lines', name=f"SMA {sma_window}"
        ))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig

# -----------------------------
# Support & Resistance
# -----------------------------
def detect_levels(df):
    if df.empty:
        return {}
    levels = {
        "support": round(df['Low'].min(), 2),
        "resistance": round(df['High'].max(), 2)
    }
    return levels

# -----------------------------
# Streamlit Page
# -----------------------------
st.set_page_config(page_title="PSX Analysis App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX)")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Market Watch Table",
    "Search Symbol",
    "Candlestick Chart",
    "Support & Resistance"
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
    symbol_search = st.text_input("Enter Symbol to search (e.g., MEBL, OGDC):")
    if symbol_search and not df_market.empty:
        df_filtered = df_market[df_market.iloc[:, 0].str.upper() == symbol_search.upper()]
        if df_filtered.empty:
            st.warning(f"No data found for {symbol_search.upper()}")
        else:
            st.dataframe(df_filtered)

# -----------------------------
# Tab 3: Candlestick Chart
# -----------------------------
with tab3:
    st.header("Candlestick Chart with SMA")
    symbol_chart = st.text_input("Enter PSX Symbol for chart:", key="chart_symbol")
    if symbol_chart:
        df_chart, error_chart = fetch_stock_data(symbol_chart.strip().upper())
        if error_chart:
            st.error(error_chart)
        else:
            df_chart = compute_sma(df_chart, window=20)
            fig = plot_candlestick(df_chart, sma_window=20)
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Tab 4: Support & Resistance
# -----------------------------
with tab4:
    st.header("Support & Resistance Levels")
    symbol_sr = st.text_input("Enter PSX Symbol for S/R:", key="sr_symbol")
    if symbol_sr:
        df_sr, error_sr = fetch_stock_data(symbol_sr.strip().upper())
        if error_sr:
            st.error(error_sr)
        else:
            levels = detect_levels(df_sr)
            st.write(levels)
