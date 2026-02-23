import requests
import pandas as pd

def fetch_dps():
    url = "https://dps.psx.com.pk/companies"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/112.0.0.0 Safari/537.36"
    }

    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()  # Raise exception if HTTP error

    # Pass the HTML content to pandas.read_html
    tables = pd.read_html(r.text)
    df = tables[0]

    # Clean column names
    df.columns = [c.replace(" ", "_").lower() for c in df.columns]
    df = df.dropna(subset=["symbol"])

    return df
