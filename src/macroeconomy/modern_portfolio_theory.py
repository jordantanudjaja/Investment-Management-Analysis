import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import minimize
import streamlit as st
import yfinance as yf

# Cached Data to getch the historical data from the inputted tickers
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_portfolio_data(tickers:list[str], period:str="2y") -> pd.DataFrame:
    """Fetches daily closing prices for user-selected tickers and calculates log returns."""
    data = yf.download(tickers, period=period, progress=False)["Close"]
    
    # If single ticker returns as Series, convert to DataFrame
    if isinstance(data, pd.Series):
        data = data.to_frame()
        
    # Drop columns with all NaN values
    data = data.dropna(axis=1, how="all")
    return data

# Function to run the Modern Portfolio Theory Engine (Don't cache this because hashing a large matrix dataframe cause unecessary overhead, the MPT engine calculation is not even that long)
def run_mpt_analysis(prices_df:pd.DataFrame, risk_free_rate:float, num_simulations:int=3000) -> tuple[go.Figure, dict]:
    """Computes Modern Portfolio Theory metrics, solves the Efficient Frontier, and generates an interactive Plotly visualization."""
    tickers = prices_df.columns.tolist()
    num_assets = len(tickers)

    if num_assets < 2:
        raise ValueError("Modern Portfolio Theory requires at least 2 valid assets.")

    # 1. Calculate Annualized Expected Returns & Covariance Matrix
    daily_returns = prices_df.pct_change().dropna()
    mean_daily_returns = daily_returns.mean()
    cov_daily = daily_returns.cov()

    trading_days = 252
    annual_returns = mean_daily_returns * trading_days
    annual_cov = cov_daily * trading_days

    # Portfolio Performance Math
    def portfolio_performance(weights: np.ndarray):
        ret = np.dot(weights, annual_returns)
        vol = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))
        sharpe = (ret - risk_free_rate) / vol if vol > 0 else 0
        return ret, vol, sharpe

    # Negative Sharpe function for Scipy Minimizer
    def neg_sharpe_ratio(weights: np.ndarray):
        return -portfolio_performance(weights)[2]

    # Portfolio Variance function for Minimum Variance Minimizer
    def portfolio_volatility(weights: np.ndarray):
        return portfolio_performance(weights)[1]

    # Constraints & Bounds (Long-only portfolio: 0 <= w_i <= 1, sum(w) = 1)
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_guess = num_assets * [1.0 / num_assets]

    # 2. Optimize Max Sharpe Ratio (Tangency Portfolio)
    max_sharpe_opt = minimize(
        neg_sharpe_ratio, init_guess, method="SLSQP", bounds=bounds, constraints=constraints
    )
    max_sharpe_weights = max_sharpe_opt.x
    max_ret, max_vol, max_sharpe = portfolio_performance(max_sharpe_weights)

    # 3. Optimize Minimum Variance Portfolio
    min_var_opt = minimize(
        portfolio_volatility, init_guess, method="SLSQP", bounds=bounds, constraints=constraints
    )
    min_var_weights = min_var_opt.x
    min_ret, min_vol, min_sharpe = portfolio_performance(min_var_weights)

    # 4. Compute Efficient Frontier Curve
    target_returns = np.linspace(min_ret, annual_returns.max() * 1.1, 50)
    efficient_vols = []

    for target in target_returns:
        req_constraint = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w, t=target: portfolio_performance(w)[0] - t},
        ]
        res = minimize(
            portfolio_volatility, init_guess, method="SLSQP", bounds=bounds, constraints=req_constraint
        )
        if res.success:
            efficient_vols.append(res.fun)
        else:
            efficient_vols.append(np.nan)

    # Filter valid frontier points
    frontier_df = pd.DataFrame({"Volatility": efficient_vols, "Return": target_returns}).dropna()

    # 5. Monte Carlo Simulation for Scatter Cloud
    np.random.seed(42)
    sim_weights = np.random.dirichlet(np.ones(num_assets), size=num_simulations)
    sim_returns = np.dot(sim_weights, annual_returns)
    sim_vols = np.sqrt(np.einsum("ij,jk,ik->i", sim_weights, annual_cov, sim_weights))
    sim_sharpes = (sim_returns - risk_free_rate) / sim_vols

    # 6. Capital Allocation Line (CAL)
    cal_x = np.linspace(0, max_vol * 1.5, 100)
    cal_y = risk_free_rate + max_sharpe * cal_x

    # ==============================================================================
    # 7. Build Plotly Figure
    # ==============================================================================
    fig = go.Figure()

    # Monte Carlo Scatter
    fig.add_trace(
        go.Scatter(
            x=sim_vols,
            y=sim_returns,
            mode="markers",
            name="Random Portfolios",
            marker=dict(
                size=5,
                color=sim_sharpes,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Sharpe Ratio", x=1.02),
            ),
            hovertemplate="<b>Volatility:</b> %{x:.2%}<br><b>Return:</b> %{y:.2%}<extra></extra>"
        )
    )

    # Efficient Frontier Line
    fig.add_trace(
        go.Scatter(
            x=frontier_df["Volatility"],
            y=frontier_df["Return"],
            mode="lines",
            name="Efficient Frontier",
            line=dict(color="#2563eb", width=3.5),
            hovertemplate="<b>Frontier Volatility:</b> %{x:.2%}<br><b>Frontier Return:</b> %{y:.2%}<extra></extra>"
        )
    )

    # Capital Allocation Line (CAL)
    fig.add_trace(
        go.Scatter(
            x=cal_x,
            y=cal_y,
            mode="lines",
            name="Capital Allocation Line (CAL)",
            line=dict(color="#8b5cf6", width=2, dash="dash"),
            hovertemplate="<b>CAL Volatility:</b> %{x:.2%}<br><b>CAL Return:</b> %{y:.2%}<extra></extra>"
        )
    )

    # Risk-Free Rate Marker (CAL Origin) ---
    fig.add_trace(
        go.Scatter(
            x=[0],
            y=[risk_free_rate],
            mode="markers+text",
            name=f"Risk-Free Rate ({risk_free_rate:.2%})",
            text=[f"Rf ({risk_free_rate:.2%})"],
            textposition="top right",
            marker=dict(
                size=11,
                color="#8b5cf6",
                symbol="circle",
                line=dict(color="black", width=1.5),
            ),
            hovertemplate=f"<b>Risk-Free Rate:</b> {risk_free_rate:.2%}<br><b>Volatility:</b> 0.00%<extra></extra>"
        )
    )

    # Individual Asset Markers
    asset_vols = np.sqrt(np.diag(annual_cov))
    fig.add_trace(
        go.Scatter(
            x=asset_vols,
            y=annual_returns,
            mode="markers+text",
            name="Individual Assets",
            text=tickers,
            textposition="top center",
            marker=dict(size=10, color="#000000", symbol="diamond"),
            hovertemplate="<b>Asset:</b> %{text}<br><b>Volatility:</b> %{x:.2%}<br><b>Return:</b> %{y:.2%}<extra></extra>"
        )
    )

    # Max Sharpe Portfolio (Tangency Point)
    fig.add_trace(
        go.Scatter(
            x=[max_vol],
            y=[max_ret],
            mode="markers",
            name="Max Sharpe (Tangency)",
            marker=dict(size=14, color="#10b981", symbol="star", line=dict(color="black", width=1)),
            hovertemplate=f"<b>Max Sharpe Ratio:</b> {max_sharpe:.2f}<br><b>Volatility:</b> %{{x:.2%}}<br><b>Return:</b> %{{y:.2%}}<extra></extra>"
        )
    )

    # Min Variance Portfolio
    fig.add_trace(
        go.Scatter(
            x=[min_vol],
            y=[min_ret],
            mode="markers",
            name="Min Variance Portfolio",
            marker=dict(size=12, color="#ef4444", symbol="cross", line=dict(color="black", width=1)),
            hovertemplate=f"<b>Min Volatility:</b> {min_vol:.2%}<br><b>Return:</b> %{{y:.2%}}<extra></extra>",
        )
    )

    # Chart Layout Formatting
    fig.update_layout(
        template="plotly_white",
        height=800,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # --- Explicit X and Y Gridline Configurations ---
    fig.update_xaxes(
        title="Annualized Volatility (Risk)",
        tickformat=".1%",
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor="#9ca3af",
        rangemode="nonnegative"
    )

    fig.update_yaxes(
        title="Annualized Expected Return",
        tickformat=".1%",
        showgrid=True,
        gridwidth=1,
        gridcolor="#e5e7eb",
        zeroline=True,
        zerolinewidth=1.5,
        zerolinecolor="#9ca3af",
        rangemode="nonnegative"
    )

    # Structured Output Metrics
    optimal_stats = {
        "max_sharpe": {
            "return": max_ret,
            "volatility": max_vol,
            "sharpe": max_sharpe,
            "weights": dict(zip(tickers, np.round(max_sharpe_weights, 4))),
        },
        "min_variance": {
            "return": min_ret,
            "volatility": min_vol,
            "sharpe": min_sharpe,
            "weights": dict(zip(tickers, np.round(min_var_weights, 4))),
        },
    }

    return fig, optimal_stats

# Function to create the correlation heatmap (Don't cache this because hashing a large matrix dataframe cause unecessary overhead, the correlation calculation is not even that long)
def create_correlation_heatmap(prices_df: pd.DataFrame) -> go.Figure:
    """Computes the Pearson correlation matrix from asset prices and returns an interactive Plotly Heatmap figure."""
    # 1. Calculate daily percentage returns and Pearson correlation
    daily_returns = prices_df.pct_change().dropna()
    corr_matrix = daily_returns.corr(method="pearson")

    tickers = corr_matrix.columns.tolist()
    correlation_values = corr_matrix.values

    # Generate text formatting annotations for each cell
    text_annotations = [
        [f"{val:.2f}" for val in row] for row in correlation_values
    ]

    # 2. Build Plotly Heatmap using graph_objects
    fig = go.Figure(
        data=go.Heatmap(
            z=correlation_values,
            x=tickers,
            y=tickers,
            zmin=-1.0,
            zmax=1.0,
            colorscale="RdBu",
            reversescale=True,  # Blue = -1 (inverse), Red = +1 (synchronized)
            text=text_annotations,
            texttemplate="%{text}",
            hoverinfo="skip",  # Completely disables hover tooltips
            colorbar=dict(title="Correlation")
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=800,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(
            side="top"
        ),  # Moves the horizontal ticker labels to the top
        yaxis=dict(
            autorange="reversed"
        )   # Keeps row 0 at the top like standard matrices
    )

    return fig