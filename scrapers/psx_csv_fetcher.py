import datetime
import pandas as pd
from psx_feed import stocks

def fetch_psx_data(symbols=None, start_date=None, end_date=None):
    """
    Fetch PSX data automatically and return as DataFrame
    symbols: list of PSX symbols (default top 5)
    start_date: datetime.date object (default: 2025-01-01)
    end_date: datetime.date object (default: today)
    """
    if symbols is None:
        symbols = ["MEBL", "OGDC", "UBL", "ENGRO", "HBL"]

    if start_date is None:
        start_date = datetime.date(2025, 1, 1)
    if end_date is None:
        end_date = datetime.date.today()

    all_data = []
    for s in symbols:
        try:
            df = stocks(s, start=start_date, end=end_date)
            df["symbol"] = s
            all_data.append(df)
        except Exception as e:
            print(f"Failed to fetch {s}: {e}")

    if all_data:
        df_all = pd.concat(all_data)
        df_all.reset_index(inplace=True)
        df_all.rename(columns={"index": "date"}, inplace=True)
        return df_all
    else:
        return pd.DataFrame()
