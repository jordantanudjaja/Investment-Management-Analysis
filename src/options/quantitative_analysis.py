import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.options.pricing_model import black_scholes_merton

# Cached Function to get the risk-return profile chart of the simulated option strategy
@st.cache_data(ttl=3600, show_spinner=False)
def get_risk_return_profile_chart(active_legs, days_elapsed, RISK_FREE_RATE, DIVIDEND_YIELD):
    # 1. Establish domain coordinate array for the underlying asset
    strikes = [leg["strike"] for leg in active_legs]
    min_strike, max_strike = min(strikes), max(strikes)
    x_underlying = np.linspace(max(1.0, min_strike * 0.5), max_strike * 1.5, 300)
    y_profit = np.zeros_like(x_underlying)
    
    # 2. Process remaining value using the BSM model framework
    for leg in active_legs:
        K = leg["strike"]
        N = leg["contracts"]
        P = leg["premium"]
        
        # Calculate how many days of time value remain at our evaluation snapshot point
        remaining_dte = leg["initial_dte"] - days_elapsed
        T_remaining = remaining_dte / 365.0  # Annualized time matrix slice
        
        if T_remaining <= 0:
            # Front leg has expired; compute raw intrinsic terminal payoff values
            if leg["type"] == "Call":
                value_at_target = np.maximum(x_underlying - K, 0)
            else:
                value_at_target = np.maximum(K - x_underlying, 0)
        else:
            # Back leg contains active residual time value; evaluate using continuous dividend yield matrix
            value_at_target = np.array([
                black_scholes_merton(S, K, T_remaining, RISK_FREE_RATE, DIVIDEND_YIELD, leg["iv"], leg["type"]) 
                for S in x_underlying
            ])
            
        # Accumulate net strategy position Profit and Loss tracking rules
        if leg["position"] == "Long":
            y_profit += (value_at_target - P) * N * 100
        else:
            y_profit += (P - value_at_target) * N * 100

    # Separate positive and negative arrays for shading boundaries
    y_profit_positive = np.where(y_profit >= 0, y_profit, 0)
    y_profit_negative = np.where(y_profit < 0, y_profit, 0)

    fig = go.Figure()

    # Shade the Profit Zone (Green)
    fig.add_trace(go.Scatter(
        x=x_underlying, y=y_profit_positive,
        fill='tozeroy',
        fillcolor='#2ECC71', # Transparent Green
        line=dict(color='#000000'),
        hoverinfo='skip',
        showlegend=False,
        name='Profit Zone'
    ))

    # Shade the Loss Zone (Red)
    fig.add_trace(go.Scatter(
        x=x_underlying, y=y_profit_negative,
        fill='tozeroy',
        fillcolor='#E74C3C', # Transparent Red
        line=dict(color='#000000'),
        hoverinfo='skip',
        showlegend=False,
        name='Loss Zone'
    ))

    # Draw the main Solid Strategy Payoff Line
    fig.add_trace(go.Scatter(
        x=x_underlying, y=y_profit,
        mode='lines',
        line=dict(color='#2C3E50', width=3),
        hovertemplate='<b>Net Return:</b> $%{y:,.2f}<extra></extra>',
        name='Strategy Payoff'
    ))

    # Add Vertical Helper Lines at each chosen Strike Price
    for strike_val in set(strikes):
        fig.add_vline(
            x=strike_val, 
            line_dash="dash", 
            line_color="#7F8C8D",
            annotation_text=f"<b>Strike</b> ${strike_val:,.2f}",
            annotation_position="top"
        )

    # Configure Axis Layout Styling
    fig.update_layout(
        xaxis_title="Underlying Stock Price ($)",
        yaxis_title="Net Profit / Loss ($)",
        template="plotly_white",
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#F0F0F0',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2C3E50' # Darker break-even boundary line
        ),
        margin=dict(l=0, r=0, t=20, b=0), # Added top margin
    )

    fig.update_xaxes(tickprefix="$", tickformat=".2f")

    return fig

# Function to get the Gamma Exposure (GEX) chart
def get_GEX_chart(calls_df, puts_df, underlying_price):
    # 1. Calculate Dollar GEX per contract (in Millions $)
    # Formula: Gamma * Open Interest * 100 shares * (S^2) * 0.01 / 1,000,000
    multiplier = 100 * (underlying_price**2) * 0.01 / 1e6

    calls_df["GEX"] = calls_df["Gamma"] * calls_df["Open Interest"] * multiplier
    puts_df["GEX"] = -1 * puts_df["Gamma"] * puts_df["Open Interest"] * multiplier  # Negative for Puts

    # 2. Combine into a unified GEX DataFrame by Strike Price
    gex_df = pd.DataFrame(
        {
            "Call GEX": calls_df["GEX"],
            "Put GEX": puts_df["GEX"],
        }
    ).fillna(0)

    gex_df["Total GEX"] = gex_df["Call GEX"] + gex_df["Put GEX"]
    # Sort by strike price ascending so y-axis renders cleanly from bottom to top
    gex_df = gex_df.sort_index()

    # 3. Identify Key GEX Wall Strikes
    # Call Wall = Maximum Positive Call GEX Strike
    call_wall_strike = float(gex_df["Call GEX"].idxmax())
    call_wall_val = gex_df.loc[call_wall_strike, "Call GEX"]
    call_wall_info = {"Strike Price": call_wall_strike, "GEX Value": call_wall_val}

    # Put Wall = Maximum Absolute Negative Put GEX Strike
    put_wall_strike = float(gex_df["Put GEX"].idxmin())
    put_wall_val = gex_df.loc[put_wall_strike, "Put GEX"]
    put_wall_info = {"Strike Price": put_wall_strike, "GEX Value": put_wall_val}
    
    # Build Horizontal Plotly Bar Chart
    fig = go.Figure()

    # Call GEX (Green Horizontal Bars)
    fig.add_trace(
        go.Bar(
            y=gex_df.index,  # Strike on Y-axis
            x=gex_df["Call GEX"],  # GEX value on X-axis
            orientation="h",  # Horizontal orientation
            name="Call GEX (+)",
            marker_color="#10b981",
            hovertemplate="<b>Call GEX:</b> $%{x:,.2f}M<extra></extra>",
        )
    )

    # Put GEX (Red Horizontal Bars)
    fig.add_trace(
        go.Bar(
            y=gex_df.index,
            x=gex_df["Put GEX"],
            orientation="h",
            name="Put GEX (-)",
            marker_color="#ef4444",
            hovertemplate="<b>Put GEX:</b> $%{x:,.2f}M<extra></extra>",
        )
    )

    # Total Net GEX Line/Points
    fig.add_trace(
        go.Scatter(
            y=gex_df.index,
            x=gex_df["Total GEX"],
            mode="lines+markers",
            name="Net GEX",
            line=dict(color="#3b82f6", width=2),
            hovertemplate="<b>Net GEX:</b> $%{x:,.2f}M<extra></extra>",
        )
    )

    # Horizontal Reference Line for Spot Price
    fig.add_hline(
        y=underlying_price,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=2,
        annotation_text=f"<b>Spot: ${underlying_price:.2f}</b>",
        annotation_position="top left",
    )

    # Call Wall Line (Green Solid Line)
    fig.add_hline(
        y=call_wall_strike,
        line_dash="solid",
        line_color="#059669",
        line_width=2.5,
        annotation_text=f"<b>Call Wall: ${call_wall_strike:.2f}</b>",
        annotation_position="top right",
        annotation_font_color="#059669",
    )

    # Put Wall Line (Red Solid Line)
    fig.add_hline(
        y=put_wall_strike,
        line_dash="solid",
        line_color="#dc2626",
        line_width=2.5,
        annotation_text=f"<b>Put Wall: ${put_wall_strike:.2f}</b>",
        annotation_position="bottom right",
        annotation_font_color="#dc2626",
    )

    # Update Layout & Axis Formatting
    fig.update_layout(
        title="Gamma Exposure (GEX) Chart",
        yaxis_title="Strike Price ($)",
        xaxis_title="Gamma Exposure ($ Millions per 1% Move)",
        barmode="relative",  # Stacks Call GEX (positive) to the right and Put GEX (negative) to the left
        hovermode="y unified",  # Unified hover inspector along the strike prices
        template="plotly_white",
        height=800,  # Increased height for better readability across multiple strikes
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=80, b=0), # Added top margin
    )

    # Format y-axis ticks as currency
    fig.update_yaxes(tickprefix="$", tickformat=".2f")

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",
        showline=False,  # Don't Show left axis border line
        linecolor="#cbd5e1",
    )

    return fig, call_wall_info, put_wall_info

# Function to get the Implied Volatility Skew Chart
def get_iv_skew_chart(calls_df, puts_df, underlying_price, call_wall_strike, put_wall_strike):
    """Processes call and put option chains to build a clean Implied Volatility

    Skew/Smile chart using OTM options and blended IV curves.
    """
    # 1. Ensure strike is accessible
    call_strikes = calls_df.index
    put_strikes = puts_df.index

    # 2. Extract IV and convert to percentage format (* 100)
    call_iv = calls_df["Implied Volatility"] * 100
    put_iv = puts_df["Implied Volatility"] * 100

    # 3. Filter out zero/invalid IV data points (noisy/illiquid strikes)
    call_mask = call_iv > 1.0
    put_mask = put_iv > 1.0

    call_strikes_clean = call_strikes[call_mask]
    call_iv_clean = call_iv[call_mask]

    put_strikes_clean = put_strikes[put_mask]
    put_iv_clean = put_iv[put_mask]

    # 4. Construct Blended OTM IV Curve
    # Use Put IV for strikes below spot, Call IV for strikes above spot
    # Blended IV for a Strike Price (K) is Put IV if K <= S else Call IV if K > S where S is the current underlying price
    otm_puts = put_iv[put_strikes <= underlying_price]
    otm_calls = call_iv[call_strikes > underlying_price]

    blended_strikes = np.concatenate(
        [otm_puts.index.values, otm_calls.index.values]
    )
    blended_iv = np.concatenate([otm_puts.values, otm_calls.values])

    blended_df = (
        pd.DataFrame({"strike": blended_strikes, "iv": blended_iv})
        .dropna()
        .sort_values("strike")
    )
    blended_df = blended_df[blended_df["iv"] > 1.0]

    # Build Plotly Chart
    fig = go.Figure()

    # Raw Call IV Curve (Dashed Green)
    fig.add_trace(
        go.Scatter(
            x=call_strikes_clean,
            y=call_iv_clean,
            mode="lines",
            name="Call IV",
            line=dict(color="#10b981", width=1.5, dash="dash"),
            hovertemplate="<b>Call IV:</b> %{y:.2f}%<extra></extra>",
        )
    )

    # Raw Put IV Curve (Dashed Red)
    fig.add_trace(
        go.Scatter(
            x=put_strikes_clean,
            y=put_iv_clean,
            mode="lines",
            name="Put IV",
            line=dict(color="#ef4444", width=1.5, dash="dash"),
            hovertemplate="<b>Put IV:</b> %{y:.2f}%<extra></extra>",
        )
    )

    # Blended OTM IV Curve (Solid Blue Line with Markers)
    fig.add_trace(
        go.Scatter(
            x=blended_df["strike"],
            y=blended_df["iv"],
            mode="lines+markers",
            name="Blended OTM IV (Skew)",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=6, color="#1d4ed8"),
            hovertemplate="<b>Blended IV:</b> %{y:.2f}%<extra></extra>",
        )
    )

    # Add Current Spot Price Reference Line
    fig.add_vline(
        x=underlying_price,
        line_dash="dash",
        line_color="#f59e0b",
        line_width=2,
        annotation_text=f"<b>Spot: ${underlying_price:.2f}</b>",
        annotation_position="top",
    )

    if call_wall_strike:
        fig.add_vline(
            x=call_wall_strike,
            line_dash="dot",
            line_color="#059669",
            line_width=2,
            annotation_text=f"<b>Call Wall: ${call_wall_strike:.2f}</b>",
            annotation_position="top right",
            annotation_font_color="#059669",
        )

    if put_wall_strike:
        fig.add_vline(
            x=put_wall_strike,
            line_dash="dot",
            line_color="#dc2626",
            line_width=2,
            annotation_text=f"<b>Put Wall: ${put_wall_strike:.2f}</b>",
            annotation_position="top left",
            annotation_font_color="#dc2626",
        )

    # Update Layout Formatting
    fig.update_layout(
        title="Implied Volatility (IV) Skew Chart",
        xaxis_title="Strike Price ($)",
        yaxis_title="Implied Volatility (%)",
        hovermode="x unified",
        template="plotly_white",
        height=800,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=80, b=0) # Added top margin
    )

    # Format X-axis Strike Prices as Currency
    fig.update_xaxes(tickprefix="$", tickformat=".2f")
    fig.update_yaxes(ticksuffix="%")

    return fig