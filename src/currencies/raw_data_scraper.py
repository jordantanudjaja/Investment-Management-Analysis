from datetime import datetime
import pandas as pd
import yfinance as yf
import streamlit as st
from src.shared.finance_utils import format_large_money

# Cached Function to call the FOREX_TICKER from yfinance using the user forex ticker input and return the information dataframe and 3-year historical data 
@st.cache_data(ttl=3600, show_spinner=False)
def process_forex_ticker(forex_ticker_input):
    FOREX_TICKER = yf.Ticker(forex_ticker_input) # Getting the yfinance Ticker object
    info_dict = FOREX_TICKER.info
    raw_news = FOREX_TICKER.news
    historical_data = FOREX_TICKER.history(period="3y")
    return info_dict, raw_news, historical_data

# Cached Function to generate the forex profile table, this will only run if the info data changes or 1 hour has passed
@st.cache_data(ttl=3600, show_spinner=False)
def generate_forex_profile_table(info):
    # Creating the general_info dataframe
    general_info_df = pd.DataFrame({
        "Profile Characteristics": [
            "Currency Pair",
            "Current Exchange Rate",
            "Open",
            "Previous Close",
            "52-Week High",
            "52-Week Low",
            "50-Day Moving Average",
            "200-Day Moving Average",
            "1-Year Price Change Ratio"
        ],
        "Information": [
            info.get("shortName", "N/A"),
            f"{info.get("regularMarketPrice"):,.6g}" if info.get("regularMarketPrice", "N/A") != "N/A" else "N/A",
            f"{info.get("open"):,.6g}" if info.get("open", "N/A") != "N/A" else "N/A",
            f"{info.get("previousClose"):,.6g}" if info.get("previousClose", "N/A") != "N/A" else "N/A",
            f"{info.get("fiftyTwoWeekHigh"):,.6g}" if info.get("fiftyTwoWeekHigh", "N/A") != "N/A" else "N/A",
            f"{info.get("fiftyTwoWeekLow"):,.6g}" if info.get("fiftyTwoWeekLow", "N/A") != "N/A" else "N/A",
            f"{info.get("fiftyDayAverage"):,.6g}" if info.get("fiftyDayAverage", "N/A") != "N/A" else "N/A",
            f"{info.get("twoHundredDayAverage"):,.6g}" if info.get("twoHundredDayAverage", "N/A") != "N/A" else "N/A",
            f"{info.get("52WeekChange"):,.6g}" if info.get("52WeekChange", "N/A") != "N/A" else "N/A"
        ]
    })

    return general_info_df

# Cached Function to call the CRYPTO_TICKER from yfinance using the user crypto ticker input and return the information dataframe and 3-year historical data 
@st.cache_data(ttl=3600, show_spinner=False)
def process_crypto_ticker(crypto_ticker_input):
    CRYPTO_TICKER = yf.Ticker(crypto_ticker_input + "-USD") # Getting the yfinance Ticker object
    info_dict = CRYPTO_TICKER.info
    raw_news = CRYPTO_TICKER.news
    historical_data = CRYPTO_TICKER.history(period="3y")
    return info_dict, raw_news, historical_data

# Function to generate the cryptocurrency profile table, this will only run if the info data changes or 1 hour has passed
@st.cache_data(ttl=3600, show_spinner=False)
def generate_crypto_profile_table(info):
    # Converting epoch launch date timestamp of the token / blockchain into a readable date
    epoch_startDate = info.get("startDate", "N/A")
    readable_startDate = datetime.fromtimestamp(epoch_startDate)

    # Converting 0-coded Max Supply into infinity
    max_supply = "Infinite" if info.get("maxSupply") == 0 else info.get("maxSupply", "N/A")

    # Calculating the Fully Diluted Valuation (FDV) because the value returned from info object is sometimes less than the Market Cap
    current_price = info.get("regularMarketPrice", 'N/A')
    total_supply = info.get("totalSupply", "N/A")
    if isinstance(max_supply, (int, float)):
        fdv = current_price * max_supply if current_price != "N/A" else "N/A"
    else:
        fdv = current_price * total_supply if (current_price != "N/A" and total_supply != "N/A") else "N/A"

    # Calculating the Market Cap to FDV ratio and Volume to Market Cap Ratio
    market_cap = info.get("marketCap", "N/A")
    rolling_vol_1day = info.get("volume", "N/A") # This is the Exchange Trading Volume, it is not the On-Chain Transaction Volume used in calculation of NVT Ratio and Signal
    market_cap_to_fdv_ratio = market_cap / fdv if (market_cap != "N/A" and fdv != "N/A") else "N/A"
    volume_to_market_cap_ratio = rolling_vol_1day / market_cap if (rolling_vol_1day != "N/A" and market_cap != "N/A") else "N/A"

    # Creating the general_info dataframe
    general_info_df = pd.DataFrame({
        "Profile Characteristics": [
            "Cryptocurrency Name",
            "Token / Blockchain Launch Date",
            "Website",
            "CoinMarketCap Link",
            "Whitepaper Link",
            "Block Number",
            "Block Reward",
            "Block Reward Reduction",
            "Market Capitalization",
            "Fully Diluted Valuation (FDV)",
            "Circulating Supply",
            "Total Supply",
            "Max Supply",
            "Current Price",
            "Open",
            "Previous Close",
            "52-Week High",
            "52-Week Low",
            "50-Day Moving Average",
            "200-Day Moving Average",
            "Current Exchange Trading Volume ($)",
            "1-Day Rolling Exchange Trading Volume ($)",
            "10-Day Moving Average Exchange Trading Volume ($)",
            "90-Day Moving Average Exchange Trading Volume ($)",
            "Market Cap to FDV Ratio",
            "Volume to Market Cap Ratio"
        ],
        "Information": [
            info.get("shortName", "N/A")[:-4],
            readable_startDate.strftime("%d %B %Y"),
            info.get("website", "N/A"),
            info.get("coinMarketCapLink", "N/A"),
            info.get("whitepaper", "N/A"),
            f"{info.get("blockNumber"):,.0f}" if info.get("blockNumber", "N/A") != "N/A" else "N/A",
            f"{str(info.get("blockReward")) + " " + info.get("symbol")[:-4]}" if info.get("blockReward", "N/A") != "N/A" else "N/A",
            info.get("blockRewardReduction", "N/A"),
            format_large_money(market_cap),
            format_large_money(fdv),
            f"{info.get("circulatingSupply"):,.0f}" if info.get("circulatingSupply", "N/A") != "N/A" else "N/A",
            f"{total_supply:,.0f}" if total_supply != "N/A" else "N/A",
            f"{max_supply:,.0f}" if (max_supply != "Infinite" and max_supply != "N/A") else max_supply,
            f"${current_price:,.2f}" if current_price != "N/A" else "N/A",
            f"${info.get("open"):,.2f}" if info.get("open", "N/A") != "N/A" else "N/A",
            f"${info.get("previousClose"):,.2f}" if info.get("previousClose", "N/A") != "N/A" else "N/A",
            f"${info.get("fiftyTwoWeekHigh"):,.2f}" if info.get("fiftyTwoWeekHigh", "N/A") != "N/A" else "N/A",
            f"${info.get("fiftyTwoWeekLow"):,.2f}" if info.get("fiftyTwoWeekLow", "N/A") != "N/A" else "N/A",
            f"${info.get("fiftyDayAverage"):,.2f}" if info.get("fiftyDayAverage", "N/A") != "N/A" else "N/A",
            f"${info.get("twoHundredDayAverage"):,.2f}" if info.get("twoHundredDayAverage", "N/A") != "N/A" else "N/A",
            format_large_money(info.get("regularMarketVolume")),
            format_large_money(rolling_vol_1day),
            format_large_money(info.get("averageVolume10days")),
            format_large_money(info.get("averageVolume")),
            f"{market_cap_to_fdv_ratio:,.2f}" if market_cap_to_fdv_ratio != "N/A" else "N/A",
            f"{volume_to_market_cap_ratio:,.3f}" if volume_to_market_cap_ratio != "N/A" else "N/A"
        ]
    })

    return general_info_df

# Cached Function to get the mainstream cryptocurrency database from a pre-defined crypto dictionary
@st.cache_data(ttl=3600, show_spinner=False)
def get_mainstream_crypto_db():
    # Dictionary of Mainstream Cryptocurrencies
    crypto_comparisons = {
        "BTC": {
            "Name": "Bitcoin",
            "Category": "Payment / Transactional",
            "Blockchain Network": "Bitcoin Ecosystem"
        },
        "ETH": {
            "Name": "Ethereum",
            "Category": "Utility Token",
            "Blockchain Network": "Ethereum Ecosystem"
        },
        "SOL": {
            "Name": "Solana",
            "Category": "Proof of Stake",
            "Blockchain Network": "Solana Ecosystem"
        },
        "BNB": {
            "Name": "Binance Coin",
            "Category": "Utility Token",
            "Blockchain Network": "BNB Chain Ecosystem"
        },
        "LTC": {
            "Name": "Litecoin",
            "Category": "Payment / Transactional",
            "Blockchain Network": "Litecoin Ecosystem"
        },
        "USDT": {
            "Name": "Tether",
            "Category": "Stablecoin",
            "Blockchain Network": "Multiple Ecosystems"
        },
        "USDC": {
            "Name": "USD Coin",
            "Category": "Stablecoin",
            "Blockchain Network": "Multiple Ecosystems"
        },
        "XRP": {
            "Name": "Ripple",
            "Category": "Decentralized Finance",
            "Blockchain Network": "XRP Ledger"
        },
        "AAVE": {
            "Name": "Aave",
            "Category": "Decentralized Finance",
            "Blockchain Network": "Multiple Ecosystems"
        },
        "LINK": {
            "Name": "Chainlink",
            "Category": "Utility Token",
            "Blockchain Network": "Ethereum Ecosystem"
        },
        "DOGE": {
            "Name": "Dogecoin",
            "Category": "Payment / Transactional",
            "Blockchain Network": "Dogecoin Ecosystem"
        },
        "ADA": {
            "Name": "Cardano",
            "Category": "Proof of Stake",
            "Blockchain Network": "Cardano Ecosystem"
        },
        "ALGO": {
            "Name": "Algorand",
            "Category": "Utility Token",
            "Blockchain Network": "Algorand Ecosystem"
        }
    }

    mainstream_cryptos = pd.DataFrame.from_dict(crypto_comparisons, orient="index")
    return mainstream_cryptos