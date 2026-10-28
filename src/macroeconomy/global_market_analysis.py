import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Cached Function to get the OHLC Chart for specified assets
@st.cache_data(ttl=3600, show_spinner=False)
def get_OHLC_historical_chart(hist_data:pd.DataFrame, title:str, yaxis_title:str="Price (OHLC)", units_category:str="Price") -> go.Figure:
    """Calculates 20-Day and 200-Day SMAs on historical OHLC data and generates an interactive
       Plotly Candlestick chart with SMA line overlays.

    Parameters:
        hist_data (pd.DataFrame): Historical data DataFrame containing
        'Open', 'High', 'Low', 'Close' columns indexed by Date.
        title (str): The main title for the chart.
        yaxis_title (str): Label for the Y-axis (defaults to 'Price ($)').

    Returns:
        go.Figure: Interactive Plotly figure object ready for st.plotly_chart().
    """
    df = hist_data.copy()

    # Calculate 20-Day and 200-Day Simple Moving Averages
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()

    fig = go.Figure()

    # Setting the hover_format and tick_format to differentiate between various unit categories of the underlying asset
    if units_category == "Price":
        hover_format = ",.2f"
        prefix = "$"
        suffix = ""
    elif units_category == "Yield":
        hover_format = ",.2f"
        prefix = ""
        suffix = "%"
    elif units_category == "Forex": # standard currency
        hover_format = ",g"
        prefix = "¥" if "JPY" in title else "$"
        suffix = ""
    else:
        hover_format = ",.2f"
        prefix = ""
        suffix = ""

    # 1. Add OHLC Candlestick Trace
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color="#10b981",  # Green
            decreasing_line_color="#ef4444",  # Red
            hovertemplate=(
                f"<b>Open:</b> {prefix}%{{open:{hover_format}}}{suffix}<br>"
                f"<b>High:</b> {prefix}%{{high:{hover_format}}}{suffix}<br>"
                f"<b>Low:</b> {prefix}%{{low:{hover_format}}}{suffix}<br>"
                f"<b>Close:</b> {prefix}%{{close:{hover_format}}}{suffix}<extra></extra>"
            )
        )
    )

    # 2. Add 20-Day SMA Overlay Line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA_20"],
            mode="lines",
            name="20-Day SMA",
            line=dict(color="#2563eb", width=1.5),  # Blue
            hovertemplate=f"<b>20-Day SMA:</b> {prefix}%{{y:{hover_format}}}{suffix}<extra></extra>"
        )
    )

    # 3. Add 200-Day SMA Overlay Line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA_200"],
            mode="lines",
            name="200-Day SMA",
            line=dict(color="#f59e0b", width=2.0),  # Orange/Amber
            hovertemplate=f"<b>200-Day SMA:</b> {prefix}%{{y:{hover_format}}}{suffix}<extra></extra>"
        )
    )

    # Global Layout Styling
    fig.update_layout(
        title=dict(text=title, x=0.0, font=dict(size=18)),
        yaxis=dict(
            title=yaxis_title,
            tickformat="~f",
            tickprefix=prefix,
            ticksuffix=suffix,
            showtickprefix="all",
            showticksuffix="all"
        ),
        xaxis_title="Date",
        template="plotly_white",
        hovermode="x unified",
        height=650,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        xaxis_rangeslider_visible=False # Disables the noisy timeline slider at the bottom
    )

    # Explicit Grid Lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#e5e7eb")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#e5e7eb")

    return fig

# Cached Function to get the Ratio Chart for specified assets
@st.cache_data(ttl=3600, show_spinner=False)
def get_ratio_line_chart(hist_data:pd.Series, title:str="RSP/SPY Ratio"):
    df = hist_data.copy().to_frame()

    fig = go.Figure()

    # Add the main ratio Line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            name=title,
            line=dict(color="#000000", width=1.5),  # Black
            hovertemplate=f"<b>{title}:</b> %{{y:,.4f}}<extra></extra>"
        )
    )
 
    # Global Layout Styling
    fig.update_layout(
        title=dict(text=title, x=0.0, font=dict(size=18)),
        yaxis=dict(title="Ratio", tickformat="~f"),
        xaxis_title="Date",
        template="plotly_white",
        hovermode="x unified",
        height=650,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        xaxis_rangeslider_visible=False # Disables the noisy timeline slider at the bottom
    )

    # Explicit Grid Lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#e5e7eb")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#e5e7eb")

    return fig

# Cached Function to get the comparison chart for different treasury yields
@st.cache_data(ttl=3600, show_spinner=False)
def get_comparison_tbonds_chart(three_month_tbill, five_year_tnote, ten_year_tnote, thirty_year_tbond):
    df_3_month = three_month_tbill.copy()
    df_5_year = five_year_tnote.copy()
    df_10_year = ten_year_tnote.copy()
    df_30_year = thirty_year_tbond.copy()

    fig = go.Figure()

    # Add the 3-month Treasury Bill Line
    fig.add_trace(
        go.Scatter(
            x=df_3_month.index,
            y=df_3_month["Close"],
            mode="lines",
            name="3-Month Treasury Bill",
            line=dict(color="#199E0D", width=1.5),  # Green
            hovertemplate="<b>3-Month Treasury Bill:</b> %{y:,.2f}%<extra></extra>"
        )
    )

    # Add the 5-year Treasury Note Line
    fig.add_trace(
        go.Scatter(
            x=df_5_year.index,
            y=df_5_year["Close"],
            mode="lines",
            name="5-Year Treasury Note",
            line=dict(color="#1B0D9E", width=1.5),  # Blue
            hovertemplate="<b>5-Year Treasury Note:</b> %{y:,.2f}%<extra></extra>"
        )
    )

    # Add the 10-year Treasury Note Line
    fig.add_trace(
        go.Scatter(
            x=df_10_year.index,
            y=df_10_year["Close"],
            mode="lines",
            name="10-year Treasury Note",
            line=dict(color="#000000", width=1.5),  # Black
            hovertemplate="<b>10-year Treasury Note:</b> %{y:,.2f}%<extra></extra>"
        )
    )

    # Add the 30-year Treasury Bond Line
    fig.add_trace(
        go.Scatter(
            x=df_30_year.index,
            y=df_30_year["Close"],
            mode="lines",
            name="30-year Treasury Bond",
            line=dict(color="#B60B0B", width=1.5),  # Red
            hovertemplate="<b>30-year Treasury Bond:</b> %{y:,.2f}%<extra></extra>"
        )
    )

    # Global Layout Styling
    fig.update_layout(
        title=dict(text="U.S. Treasury Bond Yields", x=0.0, font=dict(size=18)),
        yaxis=dict(title="Yield", tickformat="~f", ticksuffix="%"),
        xaxis_title="Date",
        template="plotly_white",
        hovermode="x unified",
        height=650,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        xaxis_rangeslider_visible=False # Disables the noisy timeline slider at the bottom
    )

    # Explicit Grid Lines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#e5e7eb")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#e5e7eb")

    return fig

# Cached Function to get the yield curve
@st.cache_data(ttl=3600, show_spinner=False)
def get_yield_curve(yield_3m, yield_5y, yield_10y, yield_30y):
    """Plots a 4-point U.S. Treasury yield curve using Plotly.

    Parameters:
        yield_3m -- 3-Month Bill yield (e.g., 4.02)
        yield_5y -- 5-Year Note yield (e.g., 5.07)
        yield_10y -- 10-Year Note yield (e.g., 5.34)
        yield_30y -- 30-Year Bond yield (e.g., 5.70)

    Returns:
        go.Figure: Interactive Plotly figure object ready for st.plotly_chart().
    """
    # Define chronological categories for the X-axis
    maturities = ["3-Month", "5-Year", "10-Year", "30-Year"]
    yields = [yield_3m, yield_5y, yield_10y, yield_30y]

    # Create the figure
    fig = go.Figure()

    # Add the yield curve line
    fig.add_trace(
        go.Scatter(
            x=maturities,
            y=yields,
            mode="lines+markers",
            name="Yield Curve",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=10, symbol="circle"),
            hovertemplate="<b>Maturity:</b> %{x}<br><b>Yield:</b> %{y:.2f}%<extra></extra>"
        )
    )

    # Customize layout for a clean, financial style
    fig.update_layout(
        title=dict(text="U.S. Treasury Yield Curve", x=0.0, font=dict(size=18)),
        xaxis_title="Maturity",
        yaxis_title="Yield (%)",
        template="plotly_white",
        hovermode="x unified",
        yaxis=dict(
            ticksuffix="%",
            gridcolor="#e5e5e5",
            zerolinecolor="#cccccc",
        ),
        xaxis=dict(
            gridcolor="#e5e5e5",
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig
