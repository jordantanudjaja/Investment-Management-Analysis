import logging
import pandas as pd
import yfinance as yf
import streamlit as st

# Configure the logger automatically using the file's name
logger = logging.getLogger(__name__)

# Helper to compute 20-day delta (Percentage or Absolute)
def _calc_20d_delta(hist_series:pd.Series, as_percentage:bool=True):
    """Calculates the current value and the delta against its 20-day SMA.

    Returns (latest_val, delta).
    """
    if len(hist_series) < 20:
        # Fallback if less than 20 trading days are returned
        latest_val = hist_series.iloc[-1]
        return latest_val, 0.0

    # Calculate 20-day Rolling Mean
    sma_20 = hist_series.tail(20).mean()
    latest_val = hist_series.iloc[-1]

    if as_percentage:
        # Percentage difference relative to 20-day average
        delta = (
            ((latest_val - sma_20) / sma_20) * 100.0 if sma_20 != 0 else 0.0
        )
    else:
        # Absolute basis points / numerical difference
        delta = latest_val - sma_20

    return latest_val, delta

# Cached Function to get the current metric data (price value and delta) for the required ticker
@st.cache_data(ttl=3600, show_spinner=False)
def get_asset_price_and_delta(ticker_symbol:str, as_percentage:bool=True):
    """Generic cached function to fetch price and 20-day delta for any ticker.

    Returns (current_price, delta_vs_20d_sma)
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="2y")
        hist_close = hist["Close"].dropna()

        if not hist.empty:
            value, delta = _calc_20d_delta(hist_close, as_percentage=as_percentage)
            return value, delta, hist

    except Exception as e:
        logger.warning(
            f"Failed to fetch data for ticker {ticker_symbol}: {e}"
        )

    return 0.0, 0.0, pd.DataFrame()

# Cached Function to get the treasury yield data based on the ticker, default is the Risk-Free Rate (^TNX) from the 10-year Treasury Note
@st.cache_data(ttl=3600, show_spinner=False)
def get_treasury_yield(t_bond_ticker:str="^TNX"):
    """Returns (current_yield_decimal, 20d_delta_pct_pts)."""
    try:
        tnx = yf.Ticker(t_bond_ticker)
        hist = tnx.history(period="2y")
        hist_close = hist["Close"].dropna()

        if not hist.empty:
            # Yield in percentage (e.g., 4.25)
            latest_yield, delta = _calc_20d_delta(hist_close, as_percentage=False)
            # Return yield in decimal (0.0425) and delta in percentage points (+0.15%)
            return {"Value": latest_yield / 100.0, "Delta": delta, "Historical Data": hist}

    except Exception as e:
        logger.warning(
            f"Failed to fetch live ^TNX data due to: {e}. Defaulting proxy."
        )

    return {"Value": 0.040, "Delta": 0.0, "Historical Data": pd.DataFrame()}  # Fallback: 4.0% yield, 0 delta

# Cached Function to get the Expected Market Return (SPY Earnings Yield + Growth)
@st.cache_data(ttl=3600, show_spinner=False)
def get_expected_market_return():
    """Returns (current_expected_return_decimal, 20d_delta_pct_pts)."""
    try:
        spy = yf.Ticker("SPY")
        hist = spy.history(period="2y")
        hist_close = hist["Close"].dropna()

        # Calculate implied 20-day P/E trend from historical price and current trailing EPS
        pe_ratio = spy.info.get("trailingPE", 25)
        latest_price = hist_close.iloc[-1]
        trailing_eps = latest_price / pe_ratio if pe_ratio > 0 else 1.0

        # Derive historical expected market return series: (1 / PE) + Growth
        long_term_growth = 0.050
        exp_return_series = (trailing_eps / hist_close) + long_term_growth
        latest_return, delta = _calc_20d_delta(exp_return_series * 100.0, as_percentage=False)
        
        return {"Value": latest_return / 100.0, "Delta": delta, "Historical Data": hist} # While the value is expressed in %, the Historical Data is returned as the SPY prices

    except Exception as e:
        logger.warning(
            f"Failed to fetch live S&P 500 return due to: {e}. Defaulting proxy."
        )

    return {"Value": 0.095, "Delta": 0.0, "Historical Data": pd.DataFrame()}  # Fallback: 9.5% return, 0 delta

# Cached Function to get the CBOE Volatility Index (^VIX)
@st.cache_data(ttl=3600, show_spinner=False)
def get_vix():
    """Fetches CBOE Volatility Index (^VIX) data"""
    vix_value, vix_delta, vix_history = get_asset_price_and_delta("^VIX", as_percentage=False)
    return {"Value": vix_value, "Delta": vix_delta, "Historical Data": vix_history}

# Cached Function to get the RSP / SPY ratio (The Equal-weighted S&P500 to the Cap-weighted S&P500 ratio) using the SPY historical data as an argument
@st.cache_data(ttl=3600, show_spinner=False)
def get_rsp_spy_ratio(spy_historical_data:pd.DataFrame):
    """Fetches the RSP/SPY Ratio data"""
    rsp = yf.Ticker("RSP")
    hist = rsp.history(period="2y")
    rsp_hist_close = hist["Close"].dropna()
    spy_hist_close = spy_historical_data["Close"].dropna()
    rsp_spy_ratio_hist = rsp_hist_close / spy_hist_close

    latest_return, delta = _calc_20d_delta(rsp_spy_ratio_hist, as_percentage=True)

    return {"Value": latest_return, "Delta": delta, "Historical Data": rsp_spy_ratio_hist}

# Cached Function to get energy commodities data (Brent Crude, WTI, and Natural Gas)
@st.cache_data(ttl=3600, show_spinner=False)
def get_energy_commodities_data():
    """Fetches Brent Crude, West Texas Intermediate (WTI), and Natural Gas metrics."""
    brent_crude_price, brent_crude_delta, brent_crude_history = get_asset_price_and_delta("BZ=F", as_percentage=True)
    wti_price, wti_delta, wti_history = get_asset_price_and_delta("CL=F", as_percentage=True)
    ng_price, ng_delta, ng_history = get_asset_price_and_delta("NG=F", as_percentage=True)
    return {
        "Brent Crude": {"Value": brent_crude_price, "Delta": brent_crude_delta, "Historical Data": brent_crude_history},
        "WTI": {"Value": wti_price, "Delta": wti_delta, "Historical Data": wti_history},
        "Natural Gas": {"Value": ng_price, "Delta": ng_delta, "Historical Data": ng_history}
    }

# Cached Function to get metal commoditites data (Gold, Silver, Copper, Platinum)
@st.cache_data(ttl=3600, show_spinner=False)
def get_metal_commodities_data():
    """Fetches Gold, Silver, Copper, and Platinum metrics."""
    gold_price, gold_delta, gold_history = get_asset_price_and_delta("GC=F", as_percentage=True)
    silver_price, silver_delta, silver_history = get_asset_price_and_delta("SI=F", as_percentage=True)
    copper_price, copper_delta, copper_history = get_asset_price_and_delta("HG=F", as_percentage=True)
    platinum_price, platinum_delta, platinum_history = get_asset_price_and_delta("PL=F", as_percentage=True)
    return {
        "Gold": {"Value": gold_price, "Delta": gold_delta, "Historical Data": gold_history},
        "Silver": {"Value": silver_price, "Delta": silver_delta, "Historical Data": silver_history},
        "Copper": {"Value": copper_price, "Delta": copper_delta, "Historical Data": copper_history},
        "Platinum": {"Value": platinum_price, "Delta": platinum_delta, "Historical Data": platinum_history}
    }

# Cached Function to get mainstream crypto data
@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_data():
    """Fetches Bitcoin, Ethereum, Solana, USD Tether metrics."""
    bitcoin_price, bitcoin_delta, bitcoin_history = get_asset_price_and_delta("BTC-USD", as_percentage=True)
    ethereum_price, ethereum_delta, ethereum_history = get_asset_price_and_delta("ETH-USD", as_percentage=True)
    solana_price, solana_delta, solana_history = get_asset_price_and_delta("SOL-USD", as_percentage=True)
    usdt_price,usdt_delta, usdt_history = get_asset_price_and_delta("USDT-USD", as_percentage=True)
    return {
        "Bitcoin": {"Value": bitcoin_price, "Delta": bitcoin_delta, "Historical Data": bitcoin_history},
        "Ethereum": {"Value": ethereum_price, "Delta": ethereum_delta, "Historical Data": ethereum_history},
        "Solana": {"Value": solana_price, "Delta": solana_delta, "Historical Data": solana_history},
        "USD Tether": {"Value": usdt_price, "Delta": usdt_delta, "Historical Data": usdt_history}
    }

# Cached Function to get popularly traded forex data
@st.cache_data(ttl=3600, show_spinner=False)
def get_forex_data():
    """Fetches USD/JPY, EUR/USD, and GBP/USD metrics."""
    usd_jpy_rate, usd_jpy_delta, usd_jpy_history = get_asset_price_and_delta("USDJPY=X", as_percentage=True)
    eur_usd_rate, eur_usd_delta, eur_usd_history = get_asset_price_and_delta("EURUSD=X", as_percentage=True)
    gbp_usd_rate, gbp_usd_delta, gbp_usd_history = get_asset_price_and_delta("GBPUSD=X", as_percentage=True)
    return {
        "USD/JPY": {"Value": usd_jpy_rate, "Delta": usd_jpy_delta, "Historical Data": usd_jpy_history},
        "EUR/USD": {"Value": eur_usd_rate, "Delta": eur_usd_delta, "Historical Data": eur_usd_history},
        "GBP/USD": {"Value": gbp_usd_rate, "Delta": gbp_usd_delta, "Historical Data": gbp_usd_history}
    }