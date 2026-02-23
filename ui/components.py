import streamlit as st
import plotly.graph_objects as go

def price_chart(df):
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"]
        )
    ])
    fig.update_layout(height=500)
    return fig
