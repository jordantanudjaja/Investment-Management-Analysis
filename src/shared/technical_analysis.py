import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Cached Function to get the Bollinger Bands, Volume Bar Chart, and Relative Strength Index (RSI) charts
@st.cache_data(ttl=3600, show_spinner=False)
def get_boll_vol_rsi(historical_data, sma_period, std_devs, rsi_period, asset_class="non-forex"):
    data = historical_data[["Open", "High", "Low", "Close", "Volume"]].copy()

    # --- 1. Bollinger Bands ---
    # Bollinger Bands Calculations
    data["20-Day SMA"] = data["Close"].rolling(window=sma_period).mean() # This SMA acts as the middle band (Default period is 20-Days)
    data["20-Day Std Dev"] = data["Close"].rolling(window=sma_period).std()

    data["Upper Band"] = data["20-Day SMA"] + std_devs * data["20-Day Std Dev"]
    data["Lower Band"] = data["20-Day SMA"] - std_devs * data["20-Day Std Dev"]

    # --- 2. Volume Bar Chart ---
    # --- COLOR CODING THE VOLUME BARS ---
    # Green bar if Close >= Open, otherwise Red bar
    data["20-Day Volume SMA"] = data["Volume"].rolling(window=20).mean() 
    volume_colors = ['#2ca02c' if row['Close'] >= row['Open'] else '#d62728' for _, row in data.iterrows()]

    # --- 3. Relative Strength Index (RSI) ---
    # RSI Calculation
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Setting up Subplots: Row 1 = Candlestick (50% height), Row 2 = Volume Bar (20% height), Row 3 = RSI (30% height)
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, # Locks timelines together so zooming on one zooms both
        vertical_spacing=0.03, # Minimal spacing between rows
        row_heights=[0.50, 0.20, 0.30] # Allocates height ratios for Bollinger Bands, Volume Bar Chart, and RSI Chart
    )

    # Setting the hover_format to differentiate between forex (6 sig fig) and non-forex (2 dp) asset class
    hover_format = "$,.2f" if asset_class == "non-forex" else ",g"

    # --- BOLLINGER BANDS ---
    # Upper Band Shading (invisible line, used for shading boundary)
    fig.add_trace(
        go.Scatter(
            x=data.index, y=data['Upper Band'],
            line=dict(color='rgba(173, 216, 230, 0.2)'),
            showlegend=False,
            name='Upper Band Shading',
            hoverinfo='skip',
            hovertemplate=None
        ),
        row=1,
        col=1
    )

    # Lower Band Shading (fills the area between Upper and Lower with a translucent channel)
    fig.add_trace(
        go.Scatter(
            x=data.index, y=data['Lower Band'],
            line=dict(color='rgba(173, 216, 230, 0.2)'),
            fill='tonexty',
            fillcolor='rgba(173, 216, 230, 0.15)',
            showlegend=False,
            name='Lower Band Shading',
            hoverinfo='skip',
            hovertemplate=None
        ),
        row=1,
        col=1
    )

    # Re-adding crisp line outlines over the shaded area for the Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Upper Band'],
            line=dict(color="#1030c0", width=1),
            name='Upper Band',
            hovertemplate=f"<b>Upper Band:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['20-Day SMA'],
            line=dict(color='#ff7f0e', dash='dash'),
            name='20-Day SMA',
            hovertemplate=f"<b>20-Day SMA:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Lower Band'],
            line=dict(color="#7c11b9", width=1),
            name='Lower Band',
            hovertemplate=f"<b>Lower Band:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    
    # Candlestick Price Chart Trace
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Price",
            hovertemplate=f"<b>Open:</b> %{{open:{hover_format}}}<br><b>High:</b> %{{high:{hover_format}}}<br><b>Low:</b> %{{low:{hover_format}}}<br><b>Close:</b> %{{close:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )

    # --- VOLUME BAR CHART ---
    # Volume Bar Chart Trace
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            marker_color=volume_colors,
            name='Volume',
            hovertemplate="<b>Volume:</b> %{y:,}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # 20-Day Volume SMA Line
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['20-Day Volume SMA'],
            line=dict(color='#ff7f0e', width=1.5),
            name='20-Day Vol SMA',
            hovertemplate="<b>20-Day Vol SMA:</b> %{y:,}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # --- RELATIVE STRENGTH INDEX (RSI) ---
    # The RSI trend line
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['RSI'], 
            line=dict(color='#a6cee3', width=1.5), 
            name='RSI',
            hovertemplate="<b>RSI:</b> %{y:,.2f}<extra></extra>"
        ),
        row=3,
        col=1
    )

    # Shaded baseline bands for Oversold (under 30) and Overbought (above 70) boundary marks, as well as the middle (50) boundary
    fig.add_hline(y=70, line=dict(color="#BE0C0C", dash='dot', width=1.5), row=3, col=1)
    fig.add_hline(y=50, line=dict(color="#c9b611", dash='dot', width=1.5), row=3, col=1) # Yellow baseline midpoint
    fig.add_hline(y=30, line=dict(color="#158A0A", dash='dot', width=1.5), row=3, col=1)

    # Unifying the x-axis from all 3 subplots into one axis, denoting it by the most bottom x-axis, allowing the black hover line to pass through all charts
    fig.update_traces(xaxis="x3")

    # Layout Configurations
    tick_format = "$~f" if asset_class == "non-forex" else "~f"

    fig.update_layout(
        yaxis=dict(title="Price (OHLC)", tickformat=f"{tick_format}"),
        yaxis2=dict(title="Volume", tickformat="~s"),
        yaxis3=dict(title="RSI", range=[-5, 105]), # Slight Padding to include the grid lines for 0 and 100
        xaxis3=dict(
            title="Date",
            showticklabels=True,
            side="bottom",
            # Add sleek navigation macro timeline selection buttons
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="MAX")
                ]),
                bgcolor="rgba(30, 30, 30, 0.8)", # Match dark theme background
                activecolor="#ff7f0e", # Highlight color when selected
                font=dict(color="white"),
                y=1.00,
                yanchor="bottom" # Uses the bottom of the button box as the anchor point
            ),
            rangeslider=dict(visible=False)
        ),
        hovermode="x",
        hoversubplots="axis",
        template="plotly_dark", # Matches well with Streamlit's dark/light modes
        xaxis_rangeslider_visible=False, # Disables the noisy timeline slider at the bottom
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1)
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

    # --- HORIZONTAL DIVIDER LINES ---
    # Line 1: Between RSI (Bottom) and Volume (Middle)
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.285, y1=0.285,
        line=dict(color="#928B8B", width=1.5)
    )
    # Line 2: Between Volume (Middle) and Bollinger Bands (Top)
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.515, y1=0.515,
        line=dict(color="#928B8B", width=1.5)
    )

    return fig

# Cached Function to get Price Action with 200-Day SMA, On-Balance Volume (OBV), Accumulation/Distribution (A/D), and Money Flow Index (MFI) Charts
@st.cache_data(ttl=3600, show_spinner=False)
def get_ma_obv_ad_mfi(historical_data, asset_class="non-forex"):
    data = historical_data[["Open", "High", "Low", "Close", "Volume"]].copy()

    # --- 1. 200-Day SMA Calculation ---
    data["200-Day SMA"] = data["Close"].rolling(window=200).mean()

     # --- 2. On-Balance Volume Calculation ---
    data['OBV'] = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()

    # --- 3. Accumulation/Distribution Calculations ---
    # Calculating Close Location Value
    clv = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low'])
    clv = clv.fillna(0) # Handle division by zero if High == Low

    data['AD'] = (clv * data['Volume']).cumsum()

    # --- 4. Money Flow Index (14-Day Period) ---
    # Calculating Typical Price and Raw Money Flow
    tp = (data['High'] + data['Low'] + data['Close']) / 3
    rmf = tp * data['Volume']
    
    tp_diff = tp.diff()
    pos_mf = np.where(tp_diff > 0, rmf, 0)
    neg_mf = np.where(tp_diff < 0, rmf, 0)
    
    # Rolling sums for 14 periods
    pos_mf_14 = pd.Series(pos_mf, index=data.index).rolling(window=14).sum()
    neg_mf_14 = pd.Series(neg_mf, index=data.index).rolling(window=14).sum()
    
    m_ratio = pos_mf_14 / neg_mf_14
    data['MFI'] = 100 - (100 / (1 + m_ratio))
    data['MFI'] = data['MFI'].fillna(50) # Default mid-value for initial NaN rows

    # Setting up Subplots: 4 Rows mapped from top down [0.60, 0.20, 0.20]
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True,           
        vertical_spacing=0.04,
        row_heights=[0.40, 0.20, 0.20, 0.20]       
    )

    # Setting the hover_format to differentiate between forex (6 sig fig) and non-forex (2 dp) asset class
    hover_format = "$,.2f" if asset_class == "non-forex" else ",g"

    # --- ROW 1: Candlesticks & 200-Day SMA ---
    # Main Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            hovertemplate=f"<b>Open:</b> %{{open:{hover_format}}}<br><b>High:</b> %{{high:{hover_format}}}<br><b>Low:</b> %{{low:{hover_format}}}<br><b>Close:</b> %{{close:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    
    # 200-Day SMA Line
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['200-Day SMA'],
            line=dict(color="#0831e7", width=2),
            name='200-Day SMA',
            hovertemplate=f"<b>200-Day SMA:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )

    # --- ROW 2: OBV Panel ---
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['OBV'],
            line=dict(color="#f1821a", width=2),
            name='OBV',
            hovertemplate="<b>OBV:</b> %{y:,.0f}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # --- ROW 3: A/D Panel ---
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['AD'],
            line=dict(color="#34c707", width=2),
            name='A/D',
            hovertemplate="<b>A/D:</b> %{y:,.0f}<extra></extra>"
        ),
        row=3,
        col=1
    )

    # --- ROW 4: MFI Panel ---
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MFI'],
            line=dict(color="#7312f1", width=2),
            name='MFI',
            hovertemplate="<b>MFI:</b> %{y:,.2f}<extra></extra>"
        ),
        row=4,
        col=1
    )

    fig.add_hline(y=70, line=dict(color="#BE0C0C", dash='dot', width=1.5), row=4, col=1)
    fig.add_hline(y=50, line=dict(color="#c9b611", dash='dot', width=1.5), row=4, col=1) # Yellow baseline midpoint
    fig.add_hline(y=30, line=dict(color="#158A0A", dash='dot', width=1.5), row=4, col=1)

    # Unifying the x-axis from all 4 subplots into one axis, denoting it by the most bottom x-axis
    fig.update_traces(xaxis="x4")

    # Layout Configuration
    tick_format = "$~f" if asset_class == "non-forex" else "~f"

    fig.update_layout(
        yaxis=dict(title="Price (OHLC)", tickformat=f"{tick_format}"),
        yaxis2=dict(title="OBV", tickformat="~s"),               
        yaxis3=dict(title="A/D", tickformat="~s"),
        yaxis4=dict(title="MFI", range=[-5, 105], zeroline=False),
        # Configure layout configurations strictly on 'xaxis3' since it's the bottom row anchor
        xaxis4=dict(
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
                bgcolor="rgba(35, 35, 35, 0.9)", activecolor="#ff7f0e", font=dict(color="white", size=11),
                y=1.00, yanchor="bottom"    
            ),
            rangeslider=dict(visible=False) # Completely removes noisy background slider track
        ), 
        hovermode="x",
        hoversubplots="axis",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1)
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

    # --- Crisp Grid Divider Lines (Calculated for Heights [0.40, 0.20, 0.20, 0.20]) ---
    # Gap 1: Separates MFI and A/D
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.215, y1=0.215,
        line=dict(color="#928B8B", width=1.5)
    )
    # Gap 2: Separates A/D and OBV
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.430, y1=0.430,
        line=dict(color="#928B8B", width=1.5)
    )
    # Gap 3: Separates OBV and Price Action Candlesticks
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.645, y1=0.645,
        line=dict(color="#928B8B", width=1.5)
    )
    return fig

# Cached Function to get 200-Day Moving Averages with Moving Average Convergence Divergence (MACD) Charts
@st.cache_data(ttl=3600, show_spinner=False)
def get_ma_macd(historical_data, asset_class="non-forex"):
    data = historical_data[["Open", "High", "Low", "Close"]].copy()
    
    # 200-Day EMA Calculation
    data["200-Day EMA"] = data["Close"].ewm(span=200, adjust=False).mean()

    # --- MACD Calculation ---
    # Standard MACD parameters: Fast = 12-Day EMA, Slow = 26-Day EMA, Signal = 9-Day EMA of MACD Line
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD Histogram'] = data['MACD'] - data['Signal Line']

    # Color-code the MACD histogram bars (Green for growing momentum, Red for falling)
    hist_colors = ['#2ca02c' if val >= 0 else '#d62728' for val in data['MACD Histogram']]

    # Setting up Subplots: Row 1 = Price (70%), Row 2 = MACD (30%)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True,           
        vertical_spacing=0.03,       
        row_heights=[0.70, 0.30]  
    )

    # Setting the hover_format to differentiate between forex (6 sig fig) and non-forex (2 dp) asset class
    hover_format = "$,.2f" if asset_class == "non-forex" else ",g"

    # --- ROW 1: Candlesticks & 200 Moving Averages ---
    # Main Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            hovertemplate=f"<b>Open:</b> %{{open:{hover_format}}}<br><b>High:</b> %{{high:{hover_format}}}<br><b>Low:</b> %{{low:{hover_format}}}<br><b>Close:</b> %{{close:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    
    # 200-Day EMA Line
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['200-Day EMA'],
            line=dict(color="#8012e7", width=2),
            name='200-Day EMA',
            hovertemplate=f"<b>200-Day EMA:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )

    # --- ROW 2: MACD Panel ---
    # MACD Line (Fast)
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MACD'], 
            line=dict(color='#1f77b4', width=1.5), 
            name='MACD',
            hovertemplate="<b>MACD:</b> %{y:.3f}<extra></extra>"
        ),
        row=2,
        col=1
    )
    
    # Signal Line (Slow)
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Signal Line'], 
            line=dict(color='#ff7f0e', width=1.5), 
            name='Signal Line',
            hovertemplate="<b>Signal:</b> %{y:.3f}<extra></extra>"
        ),
        row=2,
        col=1
    )
    
    # MACD Histogram Bars
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['MACD Histogram'],
            marker_color=hist_colors,
            name='Histogram',
            hovertemplate="<b>Histogram:</b> %{y:.3f}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # Unifying the x-axis from all 2 subplots into one axis, denoting it by the most bottom x-axis
    fig.update_traces(xaxis="x2")

    # Layout Configuration
    tick_format = "$~f" if asset_class == "non-forex" else "~f"

    fig.update_layout(
        yaxis=dict(title="Price (OHLC)", tickformat=f"{tick_format}"),
        yaxis2=dict(title="MACD", zeroline=True, zerolinecolor="rgba(255, 255, 255, 0.2)"), 
        xaxis2=dict(
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
        hovermode="x",
        hoversubplots="axis",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1)
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

    # --- PERFECT HORIZONTAL GRID GAP DIVIDER LINE ---
    # Based on Row Heights [0.70, 0.30] and Vertical Spacing 0.03:
    # 0.30 * (1 - 0.03) = 0.291 -> Midpoint of the structural gap is ~0.305
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.305, y1=0.305,
        line=dict(color="#928B8B", width=1.5)
    )

    return fig

# Cached Function to get Donchian Channels, Average Directional Index (ADI) and Choppiness Index (CHOP) Charts
@st.cache_data(ttl=3600, show_spinner=False)
def get_donchian_adi_chop(historical_data, donchian_period, adx_period, chop_period, asset_class="non-forex"):
    data = historical_data[["Open", "High", "Low", "Close"]].copy()

    # --- 1. Donchian Channel Calculations ---
    data['Upper Band'] = data['High'].rolling(window=donchian_period).max()
    data['Lower Band'] = data['Low'].rolling(window=donchian_period).min()
    data['Middle Band'] = (data['Upper Band'] + data['Lower Band']) / 2
    data["50-Day EMA"] = data["Close"].ewm(span=50, adjust=False).mean()

    # --- 2. ADX (Average Directional Index) Calculations ---
    data['TR'] = np.maximum(
        data['High'] - data['Low'],
        np.maximum(
            abs(data['High'] - data['Close'].shift(1)),
            abs(data['Low'] - data['Close'].shift(1))
        )
    )
    
    data['+DM'] = np.where(
        (data['High'] - data['High'].shift(1)) > (data['Low'].shift(1) - data['Low']),
        np.maximum(data['High'] - data['High'].shift(1), 0),
        0
    )
    data['-DM'] = np.where(
        (data['Low'].shift(1) - data['Low']) > (data['High'] - data['High'].shift(1)),
        np.maximum(data['Low'].shift(1) - data['Low'], 0),
        0
    )
    
    # Smooth via rolling sums
    tr_smooth = data['TR'].rolling(window=adx_period).sum()
    dm_plus_smooth = data['+DM'].rolling(window=adx_period).sum()
    dm_minus_smooth = data['-DM'].rolling(window=adx_period).sum()
    
    data['+DI'] = 100 * (dm_plus_smooth / tr_smooth)
    data['-DI'] = 100 * (dm_minus_smooth / tr_smooth)
    data['DX'] = 100 * (abs(data['+DI'] - data['-DI']) / (data['+DI'] + data['-DI']))
    data['ADX'] = data['DX'].rolling(window=adx_period).mean()

    # --- 3. Choppiness Index Calculation ---
    true_high = np.maximum(data['High'], data['Close'].shift(1))
    true_low = np.minimum(data['Low'], data['Close'].shift(1))
    
    tr_sum = data['TR'].rolling(window=chop_period).sum()
    max_hi = true_high.rolling(window=chop_period).max()
    min_lo = true_low.rolling(window=chop_period).min()
    
    data['Choppiness'] = 100 * (np.log10(tr_sum / (max_hi - min_lo)) / np.log10(chop_period))

    # Setting up Subplots: 4 Rows mapped from top down [0.60, 0.20, 0.20]
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True,           
        vertical_spacing=0.03,
        row_heights=[0.60, 0.20, 0.20]       
    )

    # Setting the hover_format to differentiate between forex (6 sig fig) and non-forex (2 dp) asset class
    hover_format = "$,.2f" if asset_class == "non-forex" else ",g"

    # --- ROW 1: Donchian Channels & Candlesticks ---
    # Translucent channel fill boundaries (hidden from hover)
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Upper Band'],
            line=dict(color='rgba(0, 255, 255, 0.0)'),
            showlegend=False,
            name='Upper Bound',
            hoverinfo='skip',
            hovertemplate=None
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Lower Band'],
            line=dict(color='rgba(0, 255, 255, 0.0)'),
            fill='tonexty',
            fillcolor='rgba(0, 255, 255, 0.06)',
            showlegend=False,
            name='Lower Bound',
            hoverinfo='skip',
            hovertemplate=None
        ),
        row=1,
        col=1
    )

    # Sharp boundary outlines
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Upper Band'],
            line=dict(color="#1030c0", width=1.5),
            name='Upper Band',
            hovertemplate=f"<b>Upper Band:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Middle Band'],
            line=dict(color='#ff7f0e', dash='dash', width=1.2),
            name='Middle Band',
            hovertemplate=f"<b>Middle Band:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Lower Band'],
            line=dict(color='#7c11b9', width=1.5),
            name='Lower Band',
            hovertemplate=f"<b>Lower Band:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    
    # Core Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            hovertemplate=f"<b>Open:</b> %{{open:{hover_format}}}<br><b>High:</b> %{{high:{hover_format}}}<br><b>Low:</b> %{{low:{hover_format}}}<br><b>Close:</b> %{{close:{hover_format}}}<extra></extra>"       
        ),
        row=1,
        col=1
    )

    # 50-Day EMA Line
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['50-Day EMA'],
            line=dict(color="#e7d104", width=2),
            name='50-Day EMA',
            hovertemplate=f"<b>50-Day EMA:</b> %{{y:{hover_format}}}<extra></extra>"
        ),
        row=1,
        col=1
    )
    
    # --- ROW 2: ADX Trend Strength Panel ---
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['ADX'],
            line=dict(color='#29b6f6', width=2),
            name='ADX',
            hovertemplate="<b>ADX:</b> %{y:,.2f}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # Use go.Scatter instead of add.hline here because it prevents the layout geometry engine from clashing and shifting to 1970
    fig.add_trace(
        go.Scatter(
            x=[data.index[0], data.index[-1]], # Stretches from the very start date to the end date
            y=[25, 25],                         # Flat threshold line at 25
            mode="lines",
            line=dict(color="#0BA525", dash='dot', width=1.2),
            showlegend=False,
            hoverinfo='skip',                   # Stops it from cluttering your hover tooltip box
            hovertemplate=None
        ),
        row=2,
        col=1
    )

    # --- ROW 3: Choppiness Index Panel ---
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Choppiness'],
            line=dict(color='#ab47bc', width=2),
            name='Choppiness Index',
            hovertemplate="<b>CHOP:</b> %{y:,.2f}<extra></extra>"
        ),
        row=3,
        col=1
    )
    fig.add_hline(y=61.8, line=dict(color="#BE0C0C", dash='dot', width=1.5), row=3, col=1)  # High consolidation limit
    fig.add_hline(y=38.2, line=dict(color="#158A0A", dash='dot', width=1.5), row=3, col=1)  # Strong trend limit

    # Unifying the x-axis from all 3 subplots into one axis, denoting it by the most bottom x-axis
    fig.update_traces(xaxis="x3")

    # Layout Configuration
    tick_format = "$~f" if asset_class == "non-forex" else "~f"

    fig.update_layout(
        yaxis=dict(title="Price (OHLC)", tickformat=f"{tick_format}"),
        yaxis2=dict(title="ADX", range=[-5, 105], zeroline=False),               
        yaxis3=dict(title="CHOP", range=[-5, 105], zeroline=False),
        # Configure layout configurations strictly on 'xaxis3' since it's the bottom row anchor
        xaxis3=dict(
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
                bgcolor="rgba(35, 35, 35, 0.9)", activecolor="#ff7f0e", font=dict(color="white", size=11),
                y=1.00, yanchor="bottom"    
            ),
            rangeslider=dict(visible=False) # Completely removes noisy background slider track
        ), 
        hovermode="x",
        hoversubplots="axis",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1)
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

    # --- Crisp Grid Divider Lines (Calculated for Heights [0.60, 0.20, 0.20]) ---
    # Gap 1: Separates Choppiness (Row 3) and ADX (Row 2)
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.215, y1=0.215,
        line=dict(color="#928B8B", width=1.5)
    )
    # Gap 2: Separates ADX (Row 2) and Price Candlesticks (Row 1)
    fig.add_shape(
        type="line", xref="paper", yref="paper",
        x0=0, x1=1, y0=0.430, y1=0.430,
        line=dict(color="#928B8B", width=1.5)
    )

    return fig