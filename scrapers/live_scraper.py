import requests
from bs4 import BeautifulSoup

def fetch_live_quote(symbol: str):
    """
    Fetch live PSX quote for a given symbol.
    Returns dictionary: last_price, change, volume.
    """
    url = f"https://www.psx.com.pk/market-summary/company/{symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/112.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch data: {e}"}

    soup = BeautifulSoup(r.text, "lxml")

    def extract(label):
        tag = soup.find("td", string=lambda x: x and label in x)
        if tag:
            return tag.find_next("td").text.strip()
        return None

    return {
        "symbol": symbol.upper(),
        "last_price": extract("Current Price"),
        "change": extract("Change"),
        "volume": extract("Total Volume"),
    }
