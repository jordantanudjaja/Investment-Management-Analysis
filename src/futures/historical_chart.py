import plotly.graph_objects as go
import streamlit as st

# Cached Function to get Cryptocurrency Price Action Chart with 200-Day SMA
@st.cache_data(ttl=3600, show_spinner=False)
def get_futures_price_action(historical_data):
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
                name='Price',
                hovertemplate="<b>Open:</b> %{open:$,.2f}<br><b>High:</b> %{high:$,.2f}<br><b>Low:</b> %{low:$,.2f}<br><b>Close:</b> %{close:$,.2f}<extra></extra>"
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