import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import streamlit as st

# Cached Function to get the wildly / dynamic trending database of cryptocurrencies
@st.cache_data(ttl=3600, show_spinner=False)
def get_trending_database():
    # Try to scrape the trending cryptocurrencies from yfinance first
    try:
        crypto_lookup = yf.Lookup("crypto")
        # Grab the top 100 trending cryptocurrency entries (not in terms of market cap but in terms of wild fluctuations)
        raw_crypto_df = crypto_lookup.get_cryptocurrency(count=100)

        if raw_crypto_df.empty:
            cleaned_crypto_df = pd.DataFrame()
            error_message = "Yahoo Finance returned an empty list. The endpoint might be down."
        else:  
            cleaned_crypto_df = raw_crypto_df[["shortName", "regularMarketPrice", "regularMarketPercentChange"]].reset_index()
            cleaned_crypto_df = cleaned_crypto_df.rename(
                columns={
                    "symbol": "Ticker",
                    "shortName": "Name",
                    "regularMarketPrice": "Current Price",
                    "regularMarketPercentChange": "1-Day Price Change"
                }
            )
            cleaned_crypto_df = cleaned_crypto_df.apply({
                "Ticker": lambda x: x.astype(str).str[:-4],
                "Name": lambda x: x.astype(str).str[:-4],
                "Current Price": lambda x: x.apply(lambda val: f"${val:,g}"),
                "1-Day Price Change": lambda x: x.apply(lambda val: f"{val:,g}%")
            })
            error_message = ""

    except Exception as e:
        cleaned_crypto_df = pd.DataFrame()
        error_message = f"❌ Lookup failed: {e}"

    return cleaned_crypto_df, error_message

# Cached Function to get Cryptocurrency Price Action Chart with 200-Day SMA
@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_price_action(historical_data):
    data = historical_data[["Open", "High", "Low", "Close"]].copy()

    # --- 200-Day SMA Calculation
    data["200-Day SMA"] = data["Close"].rolling(window=200).mean()

    # Setting up Subplots: Row 1 = Price (70%), Row 2 = MACD (30%)
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Exchange Rate',
                hovertemplate="<b>Open:</b> %{open:$,g}<br><b>High:</b> %{high:$,g}<br><b>Low:</b> %{low:$,g}<br><b>Close:</b> %{close:$,g}<extra></extra>"
            ),
            go.Scatter(
                x=data.index,
                y=data['200-Day SMA'],
                line=dict(color="#0831e7", width=2),
                name='200-Day SMA',
                hovertemplate="<b>200-Day SMA:</b> %{y:$,g}<extra></extra>"
            )
        ]
    )

    # Layout Configuration
    fig.update_layout(
        yaxis=dict(title="Price (OHLC)", tickformat="$~f"),
        xaxis=dict(
            title="Date",
            showticklabels=True,
            side="bottom",
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="MAX")
                ]),
                bgcolor="rgba(35, 35, 35, 0.9)",
                activecolor="#ff7f0e",
                font=dict(color="white", size=11),
                y=1.00,             
                yanchor="bottom"    
            ),
            rangeslider=dict(visible=False)
        ),  
        hovermode="x unified",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(t=20, b=0, l=0, r=0)
    )

    fig.update_xaxes(
        showspikes=True,            # Turns on the hover vertical guide lines
        spikemode="across",         # Forces the line to extend past subplot grid boundaries
        spikesnap="cursor",         # Snaps line position exactly to your pointer
        spikethickness=1.5,         # Clean visual weight match
        spikecolor="#000000",     # Black line
        spikedash="dash",           # Makes it a dashed line format
        showgrid=True,              # Shows vertical grid lines
        nticks=10                   # Increase this number to make vertical intervals smaller
    )

    return fig