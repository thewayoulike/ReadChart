import requests
import pandas as pd

def fetch_psxterminal(symbol: str = None):
    """
    Fetch PSX data from psxterminal.com API.
    If symbol is None, returns market data for all symbols.
    """
    base = "https://psxterminal.com/api/market-data"
    params = {}

    if symbol:
        params["symbol"] = symbol.upper()

    try:
        r = requests.get(base, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return pd.DataFrame(), f"Error: {e}"

    # If symbol specified, wrap in list
    items = data if isinstance(data, list) else [data]
    df = pd.DataFrame(items)

    return df, None
