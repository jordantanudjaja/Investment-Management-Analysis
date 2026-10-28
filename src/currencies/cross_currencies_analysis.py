import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import streamlit as st
from src.shared.finance_utils import format_large_money

# Function to get various charts comparing different forex pairs
@st.cache_data(ttl=3600, show_spinner=False)
def get_forex_comparison_charts(fiat_currency_ticker, fiat_currency_name, comparison_currencies, base_or_quote):
    # Ensuring that the major global economices dictionary does not include the base fiat currency if it already exist
    comparison_currencies = {key: value for key, value in comparison_currencies.items() if value != fiat_currency_ticker}

    # Building the Forex Pairs Dictionary and assigning the names and tickers to lists for the iteration of historical data
    if base_or_quote == "base":
        forex_pairs = {fiat_currency_name + f" ({fiat_currency_ticker}) / " + key + f" ({value})": fiat_currency_ticker + value + "=X" for key, value in comparison_currencies.items()}
    else:
        forex_pairs = {key + f" ({value}) / " + fiat_currency_name + f" ({fiat_currency_ticker})": value + fiat_currency_ticker + "=X" for key, value in comparison_currencies.items()}

    # Separate the names and tickers for the forex pairs
    forex_pairs_names = forex_pairs.keys()
    forex_pairs_tickers = forex_pairs.values()

    # Initialize bulk Tickers object
    tickers_obj = yf.Tickers(" ".join(forex_pairs_tickers))

    # Helper function to process a single ticker and captures tickets_obj from parent scope
    def fetch_historical_data(symbol, name):
        # tickers_obj will be defined later, tickers_obj cannot be used as an argument because this function will be iterated using ThreadPoolExecutor
        # and the tickers_obj cannot be iterated
        ticker_item = tickers_obj.tickers[symbol]
        historical_data = ticker_item.history(period="2y")[["Open", "High", "Low", "Close"]].copy()
        # --- 200-Day SMA Calculation
        historical_data["200-Day SMA"] = historical_data["Close"].rolling(window=200).mean()
        
        row = {"Forex Pair": symbol, "Forex Pair Name": name, "Historical Data": historical_data}
        return row

    # Fetch info dictionaries in parallel threads
    with ThreadPoolExecutor(max_workers=len(forex_pairs_tickers)) as executor:
        forex_list = list(executor.map(fetch_historical_data, forex_pairs_tickers, forex_pairs_names))

    # 1. Extract titles for the 3x4 grid (12 subplots)
    titles = [item["Forex Pair Name"] for item in forex_list[:12]]

    # 2. Initialize subplots figure
    fig = make_subplots(
        rows=6,
        cols=2,
        subplot_titles=titles,
        vertical_spacing=0.08,
        horizontal_spacing=0.10,
    )

    # 3. Populate each subplot
    for idx, item in enumerate(forex_list[:12]):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        df = item["Historical Data"]

        # Add Candlestick Trace
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="OHLC",
                showlegend=False,
                hovertemplate="<b>Open:</b> %{open:,.6g}<br><b>High:</b> %{high:,.6g}<br><b>Low:</b> %{low:,.6g}<br><b>Close:</b> %{close:,.6g}<extra></extra>"
            ),
            row=row,
            col=col
        )

        # Add 200-Day SMA Line
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["200-Day SMA"],
                mode="lines",
                line=dict(color="#0831e7", width=1.5),
                name="200-Day SMA",
                showlegend=False,
                hovertemplate="<b>200-Day SMA:</b> %{y:,.6g}<extra></extra>"
            ),
            row=row,
            col=col
        )

    # 4. Hide individual rangesliders to keep the 4x3 grid legible
    fig.update_xaxes(rangeslider_visible=False)

    # 5. Final layout adjustments
    fig.update_layout(
        height=1200,
        width=1400,
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig

# Cached Function to get the tokenomics data from the dataframe of mainstream cryptos that has just the general information
@st.cache_data(ttl=3600, show_spinner=False)
def get_tokenomics_data(mainstream_cryptos):
    mainstream_crypto_tickers = mainstream_cryptos.index.to_list()
    mainstream_crypto_tickers = [ticker + "-USD" for ticker in mainstream_crypto_tickers]

    # Initialize bulk Tickers object
    tickers_obj = yf.Tickers(" ".join(mainstream_crypto_tickers))

    metrics_to_collect = {
        "circulatingSupply": "Circulating Supply",
        "totalSupply": "Total Supply",
        "maxSupply": "Max Supply",
        "volume": "1-Day Rolling Trading Volume ($)",
        "regularMarketPrice": "Current Price ($)",
        "marketCap": "Market Capitalization ($)"
    }

    # Helper function to process a single ticker and captures tickets_obj & metrics_to_collect from parent scope
    def fetch_ticker_metrics(symbol):
        # tickers_obj will be defined later, tickers_obj cannot be used as an argument because this function will be iterated using ThreadPoolExecutor
        # and the tickers_obj cannot be iterated
        ticker_item = tickers_obj.tickers[symbol]
        info = ticker_item.info
        
        row = {"Ticker": symbol}
        for key, display_name in metrics_to_collect.items():
            val = info.get(key, np.nan)
                
            row[display_name] = val

        if row["Max Supply"] != 0:
            fdv = row["Current Price ($)"] * row["Max Supply"]
        else:
            fdv = row["Current Price ($)"] * row["Total Supply"]

        row["Fully Diluted Valuation (FDV) ($)"] = fdv
        row["Ticker"] = symbol[:-4] # Removing the -USD in ticker to make it cleaner
        
        return row

    # Fetch info dictionaries in parallel threads
    with ThreadPoolExecutor(max_workers=len(mainstream_crypto_tickers)) as executor:
        metrics_data = list(executor.map(fetch_ticker_metrics, mainstream_crypto_tickers))

    # Build tokenomics DataFrame
    tokenomics_df = pd.DataFrame(metrics_data).set_index("Ticker")

    return tokenomics_df

# Cached Function to format the raw tokenomics data
@st.cache_data(ttl=3600, show_spinner=False)
def format_tokenomics_data(raw_tokenomics_data):
    formatted_tokenomics_data = raw_tokenomics_data.copy()

    for col in formatted_tokenomics_data.columns:
        if col in ["Max Supply"]:
            formatted_tokenomics_data[col] = formatted_tokenomics_data[col].apply(lambda x: "Infinite" if x == 0 else f"{x:,.0f}")
        elif col in ["Circulating Supply", "Total Supply"]:
            formatted_tokenomics_data[col] = formatted_tokenomics_data[col].apply(lambda x: f"{x:,.0f}")
        elif col in ["Current Price ($)"]:
            formatted_tokenomics_data[col] = formatted_tokenomics_data[col].apply(lambda x: f"${x:,.2f}")
        elif col in ["1-Day Rolling Trading Volume ($)", "Market Capitalization ($)", "Fully Diluted Valuation (FDV) ($)"]:
            formatted_tokenomics_data[col] = formatted_tokenomics_data[col].apply(lambda x: format_large_money(x))

    return formatted_tokenomics_data

# Cached Function to get the Supply Comparison charts for Crypto
@st.cache_data(ttl=3600, show_spinner=False)
def get_supply_comparison_chart(crypto_comparison_data, crypto_ticker_input, info_dict):
    supply_data = crypto_comparison_data[["Circulating Supply", "Total Supply", "Max Supply"]].copy()

    # Adding the Crypto Ticker if not in the original mainstream Crypto dataframe
    if crypto_ticker_input not in supply_data.index:
        supply_data.loc[crypto_ticker_input] = {
            "Circulating Supply": info_dict.get("circulatingSupply"),
            "Total Supply": info_dict.get("totalSupply"),
            "Max Supply": np.nan if info_dict.get("maxSupply") == 0 else info_dict.get("maxSupply")
        }

    # Plotting the Chart
    fig = go.Figure()

    for col in supply_data.columns:
        fig.add_trace(
            go.Bar(
                x=supply_data[col],
                y=supply_data.index,
                orientation='h',
                name=col,
                hovertemplate=(f"<b>{col}: </b>" + "%{x:,.0f}<extra></extra>") # <extra></extra> removes the default secondary trace-name box
            )
        )

    # Configure layout
    fig.update_layout(
        xaxis_title="Coin Supply",
        barmode='group',
        yaxis=dict(autorange="reversed"),
        height=500,
        hovermode="y unified",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            title=dict(text="<b>Supply Category</b>", font=dict(size=12), side="top center"),
            orientation="h",        # Make the legend horizontal
            yanchor="bottom",       # Anchor the bottom of the legend
            y=1.02,                 # Position it just above the top of the plot (1.0)
            xanchor="center",       # Anchor the center of the legend
            x=0.5                   # Center it horizontally relative to the plot
        )
    )

    fig.update_xaxes(showgrid=True, gridcolor="#E7DCDC")

    return fig

# Cached Function to get the Market Cap to FDV Ratio and Volume to Market Cap Ratio Comparison Chart for Crypto
@st.cache_data(ttl=3600, show_spinner=False)
def get_ratio_comparison_chart(crypto_comparison_data, crypto_ticker_input, info_dict):
    ratio_data = crypto_comparison_data[
        [
            "Total Supply",
            "Max Supply",
            "1-Day Rolling Trading Volume ($)",
            "Current Price ($)",
            "Market Capitalization ($)",
            "Fully Diluted Valuation (FDV) ($)"
        ]
    ].copy()

    # Adding the Crypto Ticker if not in the original mainstream Crypto dataframe
    if crypto_ticker_input not in ratio_data.index:
        ratio_data.loc[crypto_ticker_input] = {
            "Total Supply": info_dict.get("totalSupply"),
            "Max Supply": np.nan if info_dict.get("maxSupply") == 0 else info_dict.get("maxSupply"),
            "Current Price ($)": info_dict.get("regularMarketPrice"),
            "1-Day Rolling Trading Volume ($)": info_dict.get("volume"),
            "Market Capitalization ($)": info_dict.get("marketCap")
        }

        if ratio_data.at[crypto_ticker_input, "Max Supply"] != np.nan: 
            ratio_data.at[crypto_ticker_input, "Fully Diluted Valuation (FDV) ($)"] = ratio_data.at[crypto_ticker_input, "Current Price ($)"] * ratio_data.at[crypto_ticker_input, "Max Supply"]
        else:
             ratio_data.at[crypto_ticker_input, "Fully Diluted Valuation (FDV) ($)"] = ratio_data.at[crypto_ticker_input, "Current Price ($)"] * ratio_data.at[crypto_ticker_input, "Total Supply"]

    # Calculate the Ratios
    ratio_data["Market Cap to FDV Ratio"] = ratio_data["Market Capitalization ($)"] / ratio_data["Fully Diluted Valuation (FDV) ($)"]
    ratio_data["Volume to Market Cap Ratio"] = ratio_data["1-Day Rolling Trading Volume ($)"] / ratio_data["Market Capitalization ($)"]

    # Plotting the Chart
    fig = make_subplots(
        rows=1, 
        cols=2, 
        subplot_titles=("Market Cap to FDV Ratio", "Volume to Market Cap Ratio"),
        horizontal_spacing=0.10 # Gap size between the two charts (10%)
    )

    colors = {
        "Market Cap to FDV Ratio": "#F5F120",    
        "Volume to Market Cap Ratio": "#F7B451" 
    }

    fig.add_trace(
        go.Bar(
            x=ratio_data["Market Cap to FDV Ratio"],
            y=ratio_data.index,
            orientation='h',
            name="Market Cap to FDV Ratio",
            marker_color=colors["Market Cap to FDV Ratio"],
            hovertemplate=(f"<b>{"Market Cap to FDV Ratio"}: </b>" + "%{x:.2f}<extra></extra>") # <extra></extra> removes the default secondary trace-name box
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=ratio_data["Volume to Market Cap Ratio"],
            y=ratio_data.index,
            orientation='h',
            name="Volume to Market Cap Ratio",
            marker_color=colors["Volume to Market Cap Ratio"],
            hovertemplate=f"<b>{"Volume to Market Cap Ratio"}: </b>" + "%{x:.3f}<extra></extra>" # <extra></extra> removes the default secondary trace-name box
        ),
        row=1,
        col=2
    )

    # Line for Market Cap to FDV Ratio (x = 0.80)
    fig.add_vline(
        x=0.80, 
        line_width=2, 
        line_dash="dash", 
        line_color="#48CC0B", # Using red/coral for the benchmark boundary
        row=1,
        col=1
    )

    # Line for Volume to Market Cap Ratio (x = 0.01)
    fig.add_vline(
        x=0.01, 
        line_width=2, 
        line_dash="dash", 
        line_color="#48CC0B", 
        row=1,
        col=2
    )

    # Configure layout
    fig.update_layout(
        height=500,
        showlegend=False,       # Subplot titles usually replace the need for a global legend
        yaxis=dict(autorange="reversed"),  # Reverses first Y-axis
        yaxis2=dict(autorange="reversed"), # Reverses second Y-axis
        hovermode="y unified",
        template="plotly_white",
        margin=dict(l=0, r=0, t=50, b=0), # Added top margin for subplot titles
    )

    fig.update_xaxes(showgrid=True, gridcolor="#E7DCDC")

    return fig