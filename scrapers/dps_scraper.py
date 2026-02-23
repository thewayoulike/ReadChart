import requests
import pandas as pd

def fetch_dps():
    url = "https://dps.psx.com.pk/companies"
    tables = pd.read_html(url)
    df = tables[0]

    df.columns = [c.replace(" ", "_").lower() for c in df.columns]
    df = df.dropna(subset=["symbol"])

    return df
