from datetime import date
import pandas as pd
import yfinance as yf
import streamlit as st
from src.shared.finance_utils import format_large_money

# Cached Function to process the stock ticker from the yfinance object, and returns serialized objects in the form of dataframes that can be cached using cache_data instead of cache_resource
@st.cache_data(ttl=3600, show_spinner=False)
def process_stock_ticker(stock_ticker_input):
    # Initializing the yf Ticker object
    STOCK_TICKER = yf.Ticker(stock_ticker_input)

    # Extract the native attributes (These are safe to pass to cached functions)
    info_dict = STOCK_TICKER.info
    raw_news = STOCK_TICKER.news
    INCOME_STMT = STOCK_TICKER.income_stmt
    BALANCE_SHEET = STOCK_TICKER.balance_sheet
    CASHFLOW_STMT = STOCK_TICKER.cash_flow
    
    # Extract Historical Data
    statement_dates = pd.to_datetime(INCOME_STMT.columns) # Extract column headers (Pandas Timestamps or strings depending on version)
    start_date = statement_dates.min().strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")
    # Download history for the full date range in ONE API call
    historical_data = STOCK_TICKER.history(start=start_date, end=end_date) # Returns a dataframe of all Open, High, Low, Close, and Volume Data (About 5 years worth of data)
    last_2_years_historical_data = historical_data.tail(2 * 261) # 261 is the average number of working days in 1 year
    historical_closing_prices = historical_data["Close"]
    historical_closing_prices.index = historical_closing_prices.index.tz_localize(None) # Remove timezone metadata so both objects share the same naive datetime64[ns] dtype

    # Extract Future Revenue Estimates Dataframe for DCF analysis
    future_revenue_estimates = STOCK_TICKER.get_revenue_estimate()

    return info_dict, raw_news, INCOME_STMT, BALANCE_SHEET, CASHFLOW_STMT, last_2_years_historical_data, historical_closing_prices, future_revenue_estimates

# Cached Function to generate the company profile table, if the argument info does not change for 1 hour, the code does not run
@st.cache_data(ttl=3600, show_spinner=False)
def generate_profile_table(info):
    # Block of code to calculate PEGY Ratio
    forward_pe = info.get("forwardPE", "N/A")
    peg_ratio = info.get("pegRatio", "N/A")
    earnings_growth_rate = forward_pe / peg_ratio if (forward_pe != "N/A" and peg_ratio != "N/A") else "N/A"
    dividend_yield = info.get("dividendYield", 0)
    pegy_ratio = forward_pe / (earnings_growth_rate + dividend_yield) if forward_pe != "N/A" and earnings_growth_rate != "N/A" else "N/A"

    # Creating the general_info dataframe
    general_info_df = pd.DataFrame({
        "Profile Characteristics": [
            "Company Name",
            "Sector",
            "Industry",
            "Website",
            "Number of Employees",
            "Market Capitalization",
            "Beta",
            "Dividend Yield",
            "Current Price",
            "Average Analyst Price Target",
            "Number of Analyst Opinions",
            "Trailing P/E Ratio",
            "Forward P/E Ratio",
            "PEG Ratio",
            "PEGY Ratio"
        ],
        "Information": [
            info.get("shortName", "N/A"),
            info.get("sector", "N/A"),
            info.get("industry", "N/A"),
            info.get("website", "N/A"),
            f"{info.get("fullTimeEmployees"):,.0f}" if info.get("fullTimeEmployees", "N/A") != "N/A" else "N/A",
            format_large_money(info.get("marketCap", "N/A")),
            f"{info.get("beta"):,.2f}" if info.get("beta", "N/A") != "N/A" else "N/A",
            f"{dividend_yield:.2f}%" if dividend_yield != 0 else "N/A",
            f"${info.get("currentPrice"):,.2f}" if info.get("currentPrice", "N/A") != "N/A" else "N/A",
            f"${info.get("targetMeanPrice"):,.2f}" if info.get("targetMeanPrice", "N/A") != "N/A" else "N/A",
            f"{info.get("numberOfAnalystOpinions"):,.0f}" if info.get("numberOfAnalystOpinions", "N/A") != "N/A" else "N/A",
            f"{info.get("trailingPE"):,.2f}" if info.get("trailingPE", "N/A") != "N/A" else "N/A",
            f"{forward_pe:,.2f}" if forward_pe != "N/A" else "N/A",
            f"{peg_ratio:.2f}" if peg_ratio != "N/A" else "N/A",
            f"{pegy_ratio:.2f}" if pegy_ratio != "N/A" else "N/A"
        ]
    })

    return general_info_df