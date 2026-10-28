from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from src.shared.finance_utils import format_date

# Cached Function to process the option ticker from the yfinance object, and returns relevant information for the Options Page
@st.cache_data(ttl=3600, show_spinner=False)
def process_option_ticker(option_ticker_input):
    # Initializing the yf Ticker object
    OPTION_TICKER = yf.Ticker(option_ticker_input)

    # Extract the native attributes
    security_name = OPTION_TICKER.info.get("shortName", "N/A")
    current_price = OPTION_TICKER.info.get("currentPrice")
    dividend_yield = OPTION_TICKER.info.get("dividendYield", 0)
    available_expiration_dates = OPTION_TICKER.options
    
    return security_name, current_price, dividend_yield, available_expiration_dates

# Cached Function to get the calls and puts dataframes from the option_ticker_input and selected expiration date in string format
@st.cache_data(ttl=3600, show_spinner=False)
def get_option_chain(option_ticker_input, expiration_date_str):
    # Initializing the yf Ticker object again and getting the option chain
    OPTION_TICKER = yf.Ticker(option_ticker_input)
    option_chain = OPTION_TICKER.option_chain(expiration_date_str)

    # Splitting the option chain into 2 halves to get the calls and puts data
    raw_calls_df = option_chain.calls
    raw_puts_df = option_chain.puts

    # Data Cleaning the raw dataframes and inserting them into a new list
    parsed_option_chain_dfs = []
    for chain_df in [raw_calls_df, raw_puts_df]:
        parsed_chain_df = chain_df[[
            "strike",
            "lastPrice",
            "bid",
            "ask",
            "volume",
            "openInterest",
            "impliedVolatility",
            "inTheMoney"
        ]].copy()

        parsed_chain_df = parsed_chain_df.rename(
            columns={
                "strike": "Strike Price",
                "lastPrice": "Latest Premium",
                "bid": "Latest Bid",
                "ask": "Latest Ask",
                "volume": "Volume",
                "openInterest": "Open Interest",
                "impliedVolatility": "Implied Volatility",
                "inTheMoney": "Moneyness"
            }
        )

        parsed_chain_df = parsed_chain_df.set_index("Strike Price")
        parsed_chain_df["Moneyness"] = np.where(
            parsed_chain_df["Moneyness"] == True, 
            "In The Money (ITM)", 
            "Out Of The Money (OTM)"
        )

        parsed_option_chain_dfs.append(parsed_chain_df)

    return parsed_option_chain_dfs[0], parsed_option_chain_dfs[1] # Index 0 is the call option chain, and index 1 is the put option chain

# Function to format the call and put option chain to be displayed in a readable format
def format_option_chain(chain_df):
    formatted_chain_df = chain_df.copy()

    # Formatting the Index
    formatted_chain_df.index = formatted_chain_df.index.map(lambda x: f"${x:,.2f}")

    # Formatting the Columns
    formatted_chain_df = formatted_chain_df.style.format(
        {
            "Latest Premium": "${:,.2f}",
            "Latest Bid": "${:,.2f}",
            "Latest Ask": "${:,.2f}",
            "Volume": "{:,.0f}",
            "Open Interest": "{:,.0f}",
            "Implied Volatility": lambda x: f"{x * 100:,g}%",
            "Delta": "{:,.4f}",
            "Gamma": "{:,.4f}",
            "Theta": "{:,.4f}",
            "Vega": "{:,.4f}",
            "Rho": "{:,.4f}"
        }
    )

    return formatted_chain_df

# Cached Function to get Option Chain Market Data from the Strategy Parameters
@st.cache_data(ttl=3600, show_spinner=False)
def get_strategy_option_chain_data(option_ticker_input, strategy_input):
    market_rows = []
    strike_errors = []
    active_legs = []  # To track legs that have valid data for the payoff calculation

    # Iterate through the rows currently sitting in the edited dataframe
    for option_leg, row in strategy_input.iterrows():
        strike = row["Strike Price"]
        expiry = row["Expiration Date"]
        num_contract = row["Number of Contracts"]
        
        market_data = {
            "Option Leg": option_leg,
            "Latest Premium": 0.0,
            "Latest Bid": 0.0,
            "Latest Ask": 0.0,
            "Total Credit / Debit": 0.0,
            "Days to Expiration": 0,
            "Implied Volatility": 0.0
        }
        
        # Only try fetching if the user has input a meaningful strike price, expiration date, and number of contracts is more than 0
        if strike > 0 and expiry and num_contract > 0:
            try:
                ticker_obj = yf.Ticker(option_ticker_input)
                chain = ticker_obj.option_chain(expiry)
                
                # Route intent based on option leg type
                if "Call" in option_leg:
                    chain_df = chain.calls
                else:
                    chain_df = chain.puts
                    
                # Filter the yfinance chain to find the exact strike price
                specific_contract = chain_df[chain_df["strike"] == float(strike)]
                
                if not specific_contract.empty:
                    # Getting and calculating option premiums and total credit / debit
                    market_data["Latest Premium"] = specific_contract.iloc[0]["lastPrice"]
                    market_data["Latest Bid"] = specific_contract.iloc[0]["bid"]
                    market_data["Latest Ask"] = specific_contract.iloc[0]["ask"]
                    multiplier = -1 if "Long" in option_leg else 1
                    market_data["Total Credit / Debit"] = multiplier * market_data["Latest Premium"] * num_contract * 100

                    # Getting and calculating the days to expiry and implied volatility
                    expiration_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                    market_data["Days to Expiration"] = (expiration_date - datetime.today().date()).days
                    market_data["Implied Volatility"] = specific_contract.iloc[0]["impliedVolatility"]
                
                    # Save processed data for the graph generation step
                    active_legs.append({
                        "leg_name": option_leg,
                        "type": "Call" if "Call" in option_leg else "Put",
                        "position": "Long" if "Long" in option_leg else "Short",
                        "strike": float(strike),
                        "contracts": float(num_contract),
                        "premium": float(market_data["Latest Premium"]),
                        "initial_dte": float(market_data["Days to Expiration"]),
                        "iv": float(market_data["Implied Volatility"]) 
                    })
                
                else:
                    # 💡 IF THE STRIKE DOES NOT EXIST: Throw an exception to reach our custom block
                    raise ValueError(f"Strike {strike} is not active for this expiration.")
                    
            except Exception:
                # 💡 THE EXCEPTION BLOCK: Grab and list the actually available strike choices
                try:
                    # Retrieve all unique available strikes for this specific option type
                    available_strikes = sorted(chain_df["strike"].unique().tolist())
                    # Format them cleanly as strings (e.g. 150.0, 155.0, 160.0)
                    strikes_string = ", ".join([f"\\${s:,.2f}" for s in available_strikes])
                    
                    # Display a clear warning notification right underneath the table
                    warning_message = f"⚠️ **{option_leg}**: Strike Price **\\${strike:,.2f}** is unavailable for the expiration date **{format_date(expiry)}**.  \n" + f"**Available Strike Prices:** {strikes_string}"      
                    strike_errors.append(warning_message)
                
                except Exception:
                    # Fallback safeguard if the yfinance connection fails entirely
                    st.error(f"Could not load option chain data for {expiry}. Please check your connection.")
                
        market_rows.append(market_data)

    # Convert the secondary dictionary collection into a matching String-Indexed DataFrame
    market_df = pd.DataFrame(market_rows).set_index("Option Leg")

    return market_df, strike_errors, active_legs