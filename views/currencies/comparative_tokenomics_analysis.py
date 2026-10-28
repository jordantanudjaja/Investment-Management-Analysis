import pandas as pd
import streamlit as st
from src.currencies.raw_data_scraper import get_mainstream_crypto_db
from src.currencies.cross_currencies_analysis import (
    get_tokenomics_data,
    format_tokenomics_data,
    get_supply_comparison_chart,
    get_ratio_comparison_chart
)

# Buttons to navigate back to Cryptocurrency Profile Page or the Technical Analysis Page
with st.container(vertical_alignment="center"):
    left_col, right_col = st.columns(2)

    with left_col:
        # Button to go to the Cryptocurrency Profile Page
        if st.button("Crypto Profile",  icon="📋"):
            st.switch_page("views/currencies/cryptocurrency.py")

    with right_col:
        with st.container(horizontal=True, horizontal_alignment="right"):
            # Button to go to the Crypto Technical Analysis Page
            if st.button("Technical Analysis",  icon="📈"):
                st.switch_page("views/currencies/crypto_technical_analysis.py")

st.info(
    """
    Comparative Tokenomics Analysis involves benchmarking a target cryptographic token against other digital asset protocols and economic frameworks. 
    Instead of evaluating a token's supply and utility in a vacuum, this analysis contextually examines distribution schedules, value capture mechanisms, 
    and participant incentives across the broader Web3 ecosystem. It helps investors, developers, and researchers identify structural market leaders, 
    inflationary risks, and valuation outliers by comparing key ecosystem metrics like Fully Diluted Valuation (FDV) to Market Capitalization ratios, 
    emission curves, and staking yields. This analysis helps to determine whether a token's economic design is sustainable or dilutive over time. 
    By comparing multiple token models simultaneously, this analysis filters out short-term speculative "noise" and reveals whether a price movement is driven 
    by genuine utility and demand or temporary supply manipulation and unsustainable emissions.
    """
)

if st.session_state.crypto_ticker_input_error:
    st.error("Crypto Ticker that was inputted does not exist. Please re-enter another ticker first before viewing this page.")
else:
    crypto_ticker_input = st.session_state.crypto_ticker_input
    info_dict = st.session_state.crypto_info_dict
    crypto_name = info_dict.get("shortName", "N/A")[:-4]

    st.markdown(f"<h1 style='text-align: center;'>Ticker: {crypto_ticker_input}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>Crypto Name: {crypto_name}</h2>", unsafe_allow_html=True)

    with st.spinner("Loading Data ..."):
        # Processing the Tokenomics Data
        mainstream_cryptos = get_mainstream_crypto_db()
        raw_tokenomics_data = get_tokenomics_data(mainstream_cryptos)
        formatted_tokenomics_data = format_tokenomics_data(raw_tokenomics_data)
        full_crypto_data = pd.merge(mainstream_cryptos, formatted_tokenomics_data, left_index=True, right_index=True, how="outer")

        # Processing the comparison charts
        supply_comparison_fig = get_supply_comparison_chart(
            raw_tokenomics_data,
            crypto_ticker_input,
            info_dict
        )
        
        ratio_comparison_fig = get_ratio_comparison_chart(
            raw_tokenomics_data,
            crypto_ticker_input,
            info_dict
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Mainstream Cryptocurrencies")
        st.dataframe(full_crypto_data, height="stretch")

    with col2:
        st.subheader("Coin Supply Comparison")
        st.plotly_chart(supply_comparison_fig, width="stretch")

    st.subheader("Tokenomics Ratio Comparison")
    st.plotly_chart(ratio_comparison_fig, width="stretch")