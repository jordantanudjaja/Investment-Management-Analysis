import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import streamlit as st

# Function to get various charts comparing commodities of the same category
@st.cache_data(ttl=3600, show_spinner=False)
def get_commodity_comparison_charts(commodity_df):
    commodity_tickers = [ticker + "=F" for ticker in commodity_df.index.to_list()]
    commodity_names = commodity_df["Name"].to_list()
    commodity_unit_prices = commodity_df["Unit Price"].to_list()

    # Initialize bulk Tickers object
    tickers_obj = yf.Tickers(" ".join(commodity_tickers))

    # Helper function to process a single ticker and captures tickets_obj from parent scope
    def fetch_historical_data(symbol, name, unit_price):
        # tickers_obj will be defined later, tickers_obj cannot be used as an argument because this function will be iterated using ThreadPoolExecutor
        # and the tickers_obj cannot be iterated
        ticker_item = tickers_obj.tickers[symbol]
        historical_data = ticker_item.history(period="2y")[["Open", "High", "Low", "Close"]].copy()
        # --- 200-Day SMA Calculation
        historical_data["200-Day SMA"] = historical_data["Close"].rolling(window=200).mean()
        
        row = {"Commodity Ticker": symbol, "Commodity Name": name, "Unit Price": unit_price, "Historical Data": historical_data}
        return row

    # Fetch info dictionaries in parallel threads
    with ThreadPoolExecutor(max_workers=len(commodity_tickers)) as executor:
        commodity_list = list(executor.map(fetch_historical_data, commodity_tickers, commodity_names, commodity_unit_prices))

    # 1. Extract titles for the 3x4 grid (12 subplots)
    titles = [item["Commodity Name"] + f" (Price per {item["Unit Price"]})" for item in commodity_list[:12]]

    # 2. Initialize subplots figure
    fig = make_subplots(
        rows=4,
        cols=2,
        subplot_titles=titles,
        vertical_spacing=0.08,
        horizontal_spacing=0.10,
    )

    # 3. Populate each subplot
    for idx, item in enumerate(commodity_list[:10]):
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
                hovertemplate="<b>Open:</b> $%{open:,.2f}<br><b>High:</b> $%{high:,.2f}<br><b>Low:</b> $%{low:,.2f}<br><b>Close:</b> $%{close:,.2f}<extra></extra>"
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
                hovertemplate="<b>200-Day SMA:</b> $%{y:,.2f}<extra></extra>"
            ),
            row=row,
            col=col
        )

        # --- Dynamic Y-Axis Customization ---
        fig.update_yaxes(  
            tickprefix="$",
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