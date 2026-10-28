import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600, show_spinner=False)
def process_fund_ticker(fund_ticker_input):
    # Initializing the yf Ticker object
    FUND_TICKER = yf.Ticker(fund_ticker_input)

    # Extract the native attributes relevant to fund profiling and deep-dive analysis
    info_dict = FUND_TICKER.info
    raw_news = FUND_TICKER.news
    fund_data = FUND_TICKER.funds_data
    fund_overview = fund_data.fund_overview
    top_holdings = fund_data.top_holdings
    sector_allocation = fund_data.sector_weightings
    asset_class_allocation = fund_data.asset_classes
    fund_operations = fund_data.fund_operations
    bond_rating_allocation = fund_data.bond_ratings

    # Extract 2-year Historical Data for technical analysis
    historical_data = FUND_TICKER.history(period="2y")

    return info_dict, raw_news, fund_overview, top_holdings, sector_allocation, asset_class_allocation, fund_operations, bond_rating_allocation, historical_data
   
# Cached Function to generate the fund profile table, fund_overview is a backup dictionary argument specifically for getting category and family values
@st.cache_data(ttl=3600, show_spinner=False)
def generate_profile_table(info, fund_overview):
    # Block of code to calculate Net Asset Value if key is not present
    net_assets = info.get("netAssets", "N/A")
    shares_outstanding = info.get("sharesOutstanding", "N/A")
    nav = net_assets / shares_outstanding if net_assets != "N/A" and shares_outstanding != "N/A" else 0

    # Creating the general_info dataframe
    general_info_df = pd.DataFrame({
        "Profile Characteristics": [
            "Fund Name",
            "Fund Type",
            "Category",
            "Fund Family",
            "Region",
            "Beta",
            "Fund Yield",
            "Dividend Yield",
            "Net Assets",
            "Net Asset Value (NAV)",
            "Net Expense Ratio",
            "Current Price",
            "Trailing P/E Ratio",
            "P/B Ratio",
            "YTD Return",
            "3-Month Return",
            "3-Year Compound Annual Growth Rate (CAGR) Return",
            "5-Year Compound Annual Growth Rate (CAGR) Return"
        ],
        "Information": [
            info.get("longName", "N/A"),
            info.get("quoteType", "N/A") if info.get("quoteType", "N/A") != "MUTUALFUND" else "MUTUAL FUND",
            info.get("category", "N/A") if info.get("category", "N/A") != "N/A" else fund_overview.get("categoryName", "N/A"),
            info.get("fundFamily", "N/A") if info.get("fundFamily", "N/A") != "N/A" else fund_overview.get("family", "N/A"),
            info.get("region", "N/A"),
            f"{info.get("beta3Year"):,.2f}" if info.get("beta3Year", "N/A") != "N/A" else "N/A",
            f"{info.get("yield") * 100:,.2f}%" if info.get("yield", "N/A") != "N/A" else "N/A",
            f"{info.get("dividendYield", 0):.2f}%" if info.get("dividendYield", 0) != 0 else "N/A",
            f"${net_assets:,.0f}" if net_assets != "N/A" else "N/A",
            f"${info.get("navPrice"):,.2f}" if info.get("navPrice", "N/A") != "N/A" else f"${nav:.2f}",
            f"{info.get("netExpenseRatio"):,.3f}%" if info.get("netExpenseRatio", "N/A") != "N/A" else "N/A",
            f"${info.get("regularMarketPrice"):,.2f}" if info.get("regularMarketPrice", "N/A") != "N/A" else "N/A",
            f"{info.get("trailingPE", "N/A"):,.2f}" if info.get("trailingPE", "N/A") != "N/A" else "N/A",
            f"{info.get("priceToBook", "N/A"):,.2f}" if info.get("priceToBook", "N/A") != "N/A" else "N/A",
            f"{info.get("ytdReturn"):,.2f}%" if info.get("ytdReturn", "N/A") != "N/A" else "N/A",
            f"{info.get("trailingThreeMonthReturns"):,.2f}%" if info.get("trailingThreeMonthReturns", "N/A") != "N/A" else "N/A",
            f"{info.get("threeYearAverageReturn") * 100:,.2f}%" if info.get("threeYearAverageReturn", "N/A") != "N/A" else "N/A",
            f"{info.get("fiveYearAverageReturn") * 100:,.2f}%" if info.get("fiveYearAverageReturn", "N/A") != "N/A" else "N/A"
        ]
    })

    return general_info_df