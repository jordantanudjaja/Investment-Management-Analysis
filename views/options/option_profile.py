from datetime import datetime
import streamlit as st
from src.options.raw_data_scraper import process_option_ticker, get_option_chain, format_option_chain
from src.options.pricing_model import calculate_option_greeks
from src.options.quantitative_analysis import get_GEX_chart, get_iv_skew_chart
from src.shared.finance_utils import format_date
from src.shared.macroeconomic_metrics import get_treasury_yield

# Define the callback function to save changes to the persistent key
def update_value():
    st.session_state.expiration_date_str = st.session_state.temp_selectbox_key

st.markdown("<h2 style='text-align: center;'>General Information</h2>", unsafe_allow_html=True)

# Keeps track of values when navigating tabs/pages
if "option_ticker_input" not in st.session_state:
    st.session_state.option_ticker_input = ""

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(horizontal=True, wrap=True):
        option_ticker_input = st.text_input("**Enter Stock or ETF Ticker**", placeholder="E.g: AAPL", value=st.session_state.option_ticker_input)
        security_name_placeholder = st.empty()
        #security_name_placeholder.metric("**Security Name**", value="")

# Check if a ticker was processed or changed
if option_ticker_input:
    st.session_state.option_ticker_input = option_ticker_input

    with st.spinner("Loading Data ..."):
        # Getting the required variables from the process_option_ticker function
        security_name, current_price, dividend_yield, available_expiration_dates = process_option_ticker(option_ticker_input)
        risk_free_rate = get_treasury_yield()["Value"]
        
        if not isinstance(current_price, float):
            option_ticker_input_error = "Option Ticker that was inputted does not exist or is not yet available in Yahoo Finance. Please re-enter another ticker."
        else:
            # Initialize a blank error message
            option_ticker_input_error = ""

            # Session state variables to be used in the Strategy Simulator Page
            st.session_state.security_underlying_price = current_price
            st.session_state.dividend_yield = dividend_yield / 100
            st.session_state.available_expiration_dates = available_expiration_dates
            st.session_state.risk_free_rate = risk_free_rate
       
        # Session State variable of the error message to be used in the other pages of Options Analysis
        st.session_state.option_ticker_input_error = option_ticker_input_error

    if option_ticker_input_error:
        with col1:
            st.error(option_ticker_input_error)
    else:
        security_name_placeholder.metric("**Security Name**", value=security_name) # Initalizing the previous placeholder
        
        if "expiration_date_str" not in st.session_state:
            st.session_state.expiration_date_str = available_expiration_dates[0]

        # Find the matching index of the current expiration date option to keep the UI in sync
        current_index = available_expiration_dates.index(st.session_state.expiration_date_str)

        with col2:
            with st.container(horizontal=True, wrap=True):
                expiration_date_str = st.selectbox(
                    "**Choose Expiration Date**",
                    options=available_expiration_dates,
                    index=current_index,
                    key="temp_selectbox_key",
                    on_change=update_value,
                    format_func=lambda x: format_date(x) # Only displaying it as DD-mmm-YYYY but the variable is still stored as YYYY-MM-DD
                )
                days_to_expiration_placeholder = st.empty()
                days_to_expiration_placeholder.metric("**Days to Expiration**", value="")

                # Session State variable to be used in the Option Greeks Page
                st.session_state.expiration_date_str = expiration_date_str

        # Getting the Days to Expiration and Risk-Free Rate data
        if expiration_date_str:
            with st.spinner("Loading Data ..."):
                expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
                days_to_expiration = (expiration_date - datetime.today().date()).days

                days_to_expiration_placeholder.metric("**Days to Expiration**", value=days_to_expiration) # Initalizing the previous placeholder

                # Get the parsed option chain from the ticker and expiration date
                calls_df, puts_df = get_option_chain(option_ticker_input, expiration_date_str)

                # Calculate the option greeks and append that data into the option chain
                calls_df = calculate_option_greeks(calls_df, current_price, days_to_expiration, risk_free_rate, dividend_yield / 100, option_type="call")
                puts_df = calculate_option_greeks(puts_df, current_price, days_to_expiration, risk_free_rate, dividend_yield / 100, option_type="put")

                # Session State variables to be used in the Options Greek Page
                st.session_state.calls_df = calls_df
                st.session_state.puts_df = puts_df

                # Format the option chain to be displayed in a readable format
                formatted_calls_df = format_option_chain(calls_df)
                formatted_puts_df = format_option_chain(puts_df)

                # Get the Gamma Exposure, and IV Skew Charts
                gex_fig, call_wall_info, put_wall_info = get_GEX_chart(calls_df, puts_df, current_price)
                iv_skew_fig = get_iv_skew_chart(calls_df, puts_df, current_price, call_wall_info["Strike Price"], put_wall_info["Strike Price"])

            with col3:
                with st.container(horizontal=True, wrap=True):
                    st.metric("**Current Price**", value=f"${current_price:,.2f}")
                    st.metric("**Dividend Yield**", value=f"{dividend_yield:.2f}%")
                    st.metric("**Current Risk-Free Rate**", value=f"{risk_free_rate * 100:,.2f}%")

            # Horizontal line dividing certain sections
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Call Option Chain")
                st.dataframe(formatted_calls_df)
            
            with col2:
                st.subheader("Put Option Chain")
                st.dataframe(formatted_puts_df)

            # Horizontal line dividing certain sections
            st.divider()
            st.markdown("<h2 style='text-align: center;'>Quantitative Analysis</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                # Gamma Exposure (GEX) Section
                st.info("""
                    **Gamma Exposure (GEX)** measures the dollar value of stock that options market makers must buy or sell for every 1% move in the underlying asset to remain delta-hedged.

                    ### 📊 Market Regimes
                    * **Positive GEX (+GEX):** Dealers trade *against* the trend. Acts as a market shock absorber, dampening volatility and pinning prices.
                    * **Negative GEX (-GEX):** Dealers trade *with* the trend. Accelerates price direction, introducing extreme volatility and sharp swings.

                    ### 📌 Key Levels
                    * **Gamma Flip:** The exact price level where net dealer gamma crosses zero, shifting the market from a low-volatility to a high-volatility regime.
                    * **Call / Put Walls:** Major open interest strikes acting as strong psychological overhead resistance or underlying support.
                    """
                )
                st.plotly_chart(gex_fig, width="stretch")

            with col2:
                # Implied Volatility Skew Section
                st.info("""
                    An **Implied Volatility (IV) Skew Chart** visualizes how implied volatility varies across different strike prices for the same expiration date, mapping market sentiment and tail-risk pricing.

                    ### 📊 Skew Patterns
                    * **Volatility Smirk / Skew:** IV is higher for out-of-the-money (OTM) puts than OTM calls. Common in equity markets, reflecting elevated fear of sudden downside crashes.
                    
                    ### 📌 Key Trading Metrics
                    * **Put-Call Skew (Risk Reversal):** The numerical difference in IV between an OTM put and an equivalent OTM call, used to measure downside fear versus upside greed.
                    * **Steepness:** A steeper skew slope signals that institutional traders are aggressively bidding up protective options, pricing in a higher probability of extreme tail-risk events.
                    """
                )
                st.plotly_chart(iv_skew_fig, width="stretch")