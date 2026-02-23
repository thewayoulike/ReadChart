import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# -----------------------------
# Helper Functions
# -----------------------------
def fetch_stock_data(symbol, period="6mo", interval="1d"):
    """
    Fetch PSX stock data from Yahoo Finance (.PK suffix)
    """
    try:
        df = yf.download(symbol + ".PK", period=period, interval=interval)
        if df.empty:
            return pd.DataFrame(), f"No data found for {symbol}"
        df.reset_index(inplace=True)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def compute_sma(df, window=20):
    """Compute Simple Moving Average"""
    df[f"SMA_{window}"] = df['Close'].rolling(window=window).mean()
    return df

def detect_levels(df):
    """Basic support/resistance using min/max"""
    if df.empty:
        return {}
    levels = {
        "support": round(df['Low'].min(), 2),
        "resistance": round(df['High'].max(), 2)
    }
    return levels

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
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="PSX Analysis App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX)")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "PSX Stock Data",
    "Live Quote",
    "Candlestick Chart",
    "Support & Resistance"
])

# -----------------------------
# Tab 1: PSX Stock Data Table
# -----------------------------
with tab1:
    st.header("Fetch PSX Stock Data")
    symbol = st.text_input("Enter PSX symbol (e.g., MEBL, OGDC):", key="tab1_symbol")
    if symbol:
        df, error = fetch_stock_data(symbol.strip().upper())
        if error:
            st.error(error)
        else:
            df = compute_sma(df, window=20)
            st.dataframe(df)

# -----------------------------
# Tab 2: Live Quote
# -----------------------------
with tab2:
    st.header("Live PSX Quote")
    symbol_live = st.text_input("Enter PSX symbol for Live Quote:", key="tab2_symbol")
    if symbol_live:
        df_live, error_live = fetch_stock_data(symbol_live.strip().upper(), period="5d", interval="1d")
        if error_live:
            st.error(error_live)
        else:
            latest = df_live.iloc[-1]
            st.write({
                "Date": latest["Date"],
                "Open": latest["Open"],
                "High": latest["High"],
                "Low": latest["Low"],
                "Close": latest["Close"],
                "Volume": latest["Volume"]
            })

# -----------------------------
# Tab 3: Candlestick Chart
# -----------------------------
with tab3:
    st.header("Candlestick Chart with SMA")
    symbol_chart = st.text_input("Enter PSX symbol for chart:", key="tab3_symbol")
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
    symbol_sr = st.text_input("Enter PSX symbol for S/R:", key="tab4_symbol")
    if symbol_sr:
        df_sr, error_sr = fetch_stock_data(symbol_sr.strip().upper())
        if error_sr:
            st.error(error_sr)
        else:
            levels = detect_levels(df_sr)
            st.write(levels)
