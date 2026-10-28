import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Function to get theoretical value of options based on the Black-Scholes-Merton Model
def black_scholes_merton(S, K, T, r, q, sigma, option_type="Call"):
    """
    S: Stock price, K: Strike price, T: Time to maturity (years),
    r: Risk-free rate, q: Continuous dividend yield, sigma: Implied Volatility
    """
    if T <= 0:
        return np.maximum(S - K, 0) if option_type == "Call" else np.maximum(K - S, 0)
    
    sigma = max(sigma, 0.0001)  # Safeguard against zero volatility
    
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "Call":
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

# Cached Function to calculate Option Greeks based on the Black-Scholes-Merton Model, which also accounts for dividends
@st.cache_data(ttl=3600, show_spinner=False)
def calculate_option_greeks(chain_df, current_price, days_to_expiration, risk_free_rate, dividend_yield, option_type="call"):   
    # Time to Expiration in years (T)
    T = max(days_to_expiration, 1) / 365.0

    # Variables
    S = current_price                               # Underlying Security Price
    K = chain_df.index.values.astype(float)         # List of Strike Prices, obtained from the index
    r = risk_free_rate                              # Risk-Free Rate
    q = dividend_yield                              # Dividend Yield
    sigma = chain_df["Implied Volatility"].values   # List of Implied Volatility values
    sigma = np.where(sigma <= 0.001, 0.001, sigma)  # Handle zero/missing IV to prevent runtime division warnings

    # Discount factors
    exp_qt = np.exp(-q * T)
    exp_rt = np.exp(-r * T)

    # Black-Scholes-Merton Model Parameters: d1 and d2
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    # --- Greeks adjusted for continuous dividend yield (q) ---

    # Gamma (identical for calls and puts)
    gamma = (exp_qt * norm.pdf(d1)) / (S * sigma * np.sqrt(T))

    # Vega (per 1% change in IV, identical for calls and puts)
    vega = (S * exp_qt * np.sqrt(T) * norm.pdf(d1)) / 100.0

    if option_type.lower() == "call":
        # Delta: discounted by e^(-qT)
        delta = exp_qt * norm.cdf(d1)

        # Theta: incorporates continuous dividend yield term
        theta = (
            -((S * exp_qt * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)))
            + q * S * exp_qt * norm.cdf(d1)
            - r * K * exp_rt * norm.cdf(d2)
        ) / 365.0

        # Rho: per 1% change in interest rate
        rho = (K * T * exp_rt * norm.cdf(d2)) / 100.0

    else:  # Puts
        delta = exp_qt * (norm.cdf(d1) - 1.0)

        theta = (
            -((S * exp_qt * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)))
            - q * S * exp_qt * norm.cdf(-d1)
            + r * K * exp_rt * norm.cdf(-d2)
        ) / 365.0

        rho = (-K * T * exp_rt * norm.cdf(-d2)) / 100.0

    # Append results rounded
    chain_df["Delta"] = np.round(delta, 4)
    chain_df["Gamma"] = np.round(gamma, 4)
    chain_df["Theta"] = np.round(theta, 4)
    chain_df["Vega"] = np.round(vega, 4)
    chain_df["Rho"] = np.round(rho, 4)

    return chain_df

# Cached Function to get the Option Greeks Charts
@st.cache_data(ttl=3600, show_spinner=False)
def get_option_greek_charts(calls_df, puts_df):
    # Ensure strike is available as a column/index array
    call_strikes = calls_df.index
    put_strikes = puts_df.index

    # Standardized color scheme
    COLOR_CALL = "#10b981"  # Emerald Green
    COLOR_PUT = "#ef4444"   # Crimson Red

    # ==============================================================================
    # CHART 1: Directional & Time Greeks (Delta, Theta, Rho) — 3x1 Subplot
    # ==============================================================================
    fig1 = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02
    )

    # 1. Delta
    fig1.add_trace(
        go.Scatter(
            x=call_strikes,
            y=calls_df["Delta"],
            mode="lines+markers",
            name="Call Delta",
            line=dict(color=COLOR_CALL, width=2),
            hovertemplate="<span style='color:green;'><b>Call Delta:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig1.add_trace(
        go.Scatter(
            x=put_strikes,
            y=puts_df["Delta"],
            mode="lines+markers",
            name="Put Delta",
            line=dict(color=COLOR_PUT, width=2),
            hovertemplate="<span style='color:red;'><b>Put Delta:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=1, col=1
    )

    # 2. Theta
    fig1.add_trace(
        go.Scatter(
            x=call_strikes,
            y=calls_df["Theta"],
            mode="lines+markers",
            name="Call Theta",
            line=dict(color=COLOR_CALL, width=2),
            hovertemplate="<span style='color:green;'><b>Call Theta:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=2,
        col=1
    )
    fig1.add_trace(
        go.Scatter(
            x=put_strikes,
            y=puts_df["Theta"],
            mode="lines+markers",
            name="Put Theta",
            line=dict(color=COLOR_PUT, width=2),
            hovertemplate="<span style='color:red;'><b>Put Theta:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # 3. Rho
    fig1.add_trace(
        go.Scatter(
            x=call_strikes,
            y=calls_df["Rho"],
            mode="lines+markers",
            name="Call Rho",
            line=dict(color=COLOR_CALL, width=2),
            hovertemplate="<span style='color:green;'><b>Call Rho:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=3,
        col=1
    )
    fig1.add_trace(
        go.Scatter(
            x=put_strikes,
            y=puts_df["Rho"],
            mode="lines+markers",
            name="Put Rho",
            line=dict(color=COLOR_PUT, width=2),
            hovertemplate="<span style='color:red;'><b>Put Rho:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=3,
        col=1
    )
    
    # Unifying the x-axis from all 3 subplots into one axis, denoting it by the most bottom x-axis, allowing the black hover line to pass through all charts
    fig1.update_traces(xaxis="x3")

    # Update layout for Chart 1
    fig1.update_layout(
        title_text="Greeks Profile: Delta, Theta, & Rho",
        height=800,
        showlegend=False,
        hovermode="x",
        hoversubplots="axis",
        template="plotly_white"
    )

    fig1.update_xaxes(title_text="Strike Price ($)", row=3, col=1)
    fig1.update_xaxes(tickprefix="$", tickformat=".2f")
    fig1.update_yaxes(title_text="Delta", row=1, col=1)
    fig1.update_yaxes(title_text="Theta ($/day)", row=2, col=1)
    fig1.update_yaxes(title_text="Rho ($/1%)", row=3, col=1)

    fig1.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",  # Light gray (Tailwind gray-200)
        zeroline=False,  # Don't Highlight the 0 GEX vertical axis line
        zerolinewidth=2,
        zerolinecolor="#9ca3af",
    )

    fig1.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",
        showline=False,  # Don't Show left axis border line
        linecolor="#cbd5e1",
    )

    fig1.update_xaxes(
        showspikes=True,            # Turns on the hover vertical guide lines
        spikemode="across",         # Forces the line to extend past subplot grid boundaries
        spikesnap="cursor",         # Snaps line position exactly to your pointer
        spikethickness=1.5,         # Clean visual weight match
        spikecolor="#000000",     # Black line
        spikedash="dash",           # Makes it a dashed line format
        showgrid=True               # Shows vertical grid lines
    )

    # ==============================================================================
    # CHART 2: Volatility & Curvature Greeks (Gamma, Vega) — 2x1 Subplot
    # ==============================================================================
    fig2 = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02
    )

    # 1. Gamma
    fig2.add_trace(
        go.Scatter(
            x=call_strikes,
            y=calls_df["Gamma"],
            mode="lines+markers",
            name="Call Gamma",
            line=dict(color=COLOR_CALL, width=2),
            hovertemplate="<span style='color:green;'><b>Call Gamma:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=1,
        col=1
    )
    fig2.add_trace(
        go.Scatter(
            x=put_strikes,
            y=puts_df["Gamma"],
            mode="lines+markers",
            name="Put Gamma",
            line=dict(color=COLOR_PUT, width=2),
            hovertemplate="<span style='color:red;'><b>Put Gamma:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=1,
        col=1
    )

    # 2. Vega
    fig2.add_trace(
        go.Scatter(
            x=call_strikes,
            y=calls_df["Vega"],
            mode="lines+markers",
            name="Call Vega",
            line=dict(color=COLOR_CALL, width=2),
            hovertemplate="<span style='color:green;'><b>Call Vega:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=2,
        col=1
    )
    fig2.add_trace(
        go.Scatter(
            x=put_strikes,
            y=puts_df["Vega"],
            mode="lines+markers",
            name="Put Vega",
            line=dict(color=COLOR_PUT, width=2),
            hovertemplate="<span style='color:red;'><b>Put Vega:</b></span> %{y:.4f}<extra></extra>"
        ),
        row=2,
        col=1
    )

    # Unifying the x-axis from all 2 subplots into one axis, denoting it by the most bottom x-axis, allowing the black hover line to pass through all charts
    fig2.update_traces(xaxis="x2")

    # Update layout for Chart 2
    fig2.update_layout(
        title_text="Greeks Profile: Gamma & Vega",
        height=800,
        showlegend=False,
        hovermode="x",
        hoversubplots="axis",
        template="plotly_white"
    )

    fig2.update_xaxes(title_text="Strike Price ($)", row=2, col=1)
    fig2.update_xaxes(tickprefix="$", tickformat=".2f")
    fig2.update_yaxes(title_text="Gamma", row=1, col=1)
    fig2.update_yaxes(title_text="Vega ($/1% IV)", row=2, col=1)

    fig2.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",  # Light gray (Tailwind gray-200)
        zeroline=False,  # Don't Highlight the 0 GEX vertical axis line
        zerolinewidth=2,
        zerolinecolor="#9ca3af",
    )

    fig2.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",
        showline=False,  # Don't Show left axis border line
        linecolor="#cbd5e1",
    )

    fig2.update_xaxes(
        showspikes=True,            # Turns on the hover vertical guide lines
        spikemode="across",         # Forces the line to extend past subplot grid boundaries
        spikesnap="cursor",         # Snaps line position exactly to your pointer
        spikethickness=1.5,         # Clean visual weight match
        spikecolor="#000000",     # Black line
        spikedash="dash",           # Makes it a dashed line format
        showgrid=True               # Shows vertical grid lines
    )

    return fig1, fig2