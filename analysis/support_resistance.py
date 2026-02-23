import numpy as np

def detect_levels(df, max_levels=10):
    df = df.copy()
    prices = df["close"].values
    levels = []

    for i in range(2, len(prices)-2):
        if prices[i] == max(prices[i-2:i+3]):
            levels.append(("resistance", prices[i]))
        if prices[i] == min(prices[i-2:i+3]):
            levels.append(("support", prices[i]))

    unique = []
    for lvl_type, price in levels:
        if not any(abs(price - u[1]) < price * 0.005 for u in unique):
            unique.append((lvl_type, price))
            if len(unique) >= max_levels:
                break

    return unique
