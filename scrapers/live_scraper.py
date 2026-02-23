import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_live_quote(symbol: str):
    url = f"https://www.psx.com.pk/market-summary/company/{symbol}"

    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "lxml")

    def extract(label):
        tag = soup.find("td", string=lambda x: x and label in x)
        if tag:
            return tag.find_next("td").text.strip()
        return None

    return {
        "symbol": symbol,
        "last_price": extract("Current Price"),
        "change": extract("Change"),
        "volume": extract("Total Volume"),
    }
