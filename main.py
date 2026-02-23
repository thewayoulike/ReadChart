import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# -----------------------------
# PSX Market Watch Scraper
# -----------------------------
def fetch_psx_market_watch():
    """
    Scrape PSX Market Watch page and return a DataFrame
    """
    url = "https://dps.psx.com.pk/market-watch"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find the table on the page
        table = soup.find("table")
        if not table:
            return pd.DataFrame(), "No table found on the page"
        
        # Extract headers
        headers = [th.text.strip() for th in table.find_all("th")]
        
        # Extract rows
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
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="PSX Market Watch App", layout="wide")
st.title("📈 Pakistan Stock Market Analysis (PSX) - Market Watch")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2 = st.tabs(["Market Watch Table", "Search Symbol"])

# -----------------------------
# Tab 1: Full Market Watch
# -----------------------------
with tab1:
    st.header("Full PSX Market Watch")
    df, error = fetch_psx_market_watch()
    if error:
        st.error(error)
    else:
        st.dataframe(df)

# -----------------------------
# Tab 2: Search for Symbol
# -----------------------------
with tab2:
    st.header("Search PSX Symbol")
    symbol_search = st.text_input("Enter Symbol to search (e.g., MEBL, OGDC):")
    if symbol_search and not df.empty:
        df_filtered = df[df.iloc[:, 0].str.upper() == symbol_search.upper()]
        if df_filtered.empty:
            st.warning(f"No data found for {symbol_search.upper()}")
        else:
            st.dataframe(df_filtered)
