import pandas as pd
import ta

def compute_indicators(df):
    df = df.copy()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    df["ema_20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema_50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    df["macd"] = ta.trend.MACD(df["close"]).macd()
    df["macd_signal"] = ta.trend.MACD(df["close"]).macd_signal()
    df["bollinger_high"] = ta.volatility.BollingerBands(df["close"]).bollinger_hband()
    df["bollinger_low"] = ta.volatility.BollingerBands(df["close"]).bollinger_lband()
    return df
