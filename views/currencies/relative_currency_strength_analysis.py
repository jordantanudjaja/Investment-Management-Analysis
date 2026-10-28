import streamlit as st
from src.currencies.cross_currencies_analysis import get_forex_comparison_charts

# Buttons to navigate back to Forex Profile Page or the Technical Analysis Page
with st.container(vertical_alignment="center"):
    left_col, right_col = st.columns(2)

    with left_col:
        # Button to go to the Forex Profile Page
        if st.button("Forex Profile",  icon="📋"):
            st.switch_page("views/currencies/foreign_exchange.py")

    with right_col:
        with st.container(horizontal=True, horizontal_alignment="right"):
            # Button to go to the Forex Technical Analysis Page
            if st.button("Technical Analysis",  icon="📈"):
                st.switch_page("views/currencies/forex_technical_analysis.py")

st.info(
    """
    Relative Currency Strength Analysis involves benchmarking a target currency pair against other global currency combinations. Instead of looking at an exchange rate in a vacuum, 
    this analysis contextually evaluates price momentum, capital flows, and volatility across the foreign exchange market. It helps traders and institutional investors 
    identify market leaders, trend reversals, and historical outliers by comparing key market metrics like interest rate differentials, moving averages, and 
    relative strength indices (RSI). This analysis can help to determine whether a currency is strengthening or weakening against one another. By comparing multiple 
    currency pairs simultaneously, this analysis filters out market "noise." It reveals whether a move is driven by genuine strength in one currency or widespread weakness in another.
    """
)

if st.session_state.forex_ticker_input_error:
    st.error("Forex Ticker that was inputted does not exist. Please re-enter another ticker pair first before viewing this page.")
else:
    # Defining the Major Global Currencies
    major_global_currencies = {
        "US Dollar": "USD",
        "Euro": "EUR",
        "Pound Sterling": "GBP",
        "Yuan Renminbi": "CNY",
        "Japanese Yen": "JPY",
        "Russian Ruble": "RUB",
        "Singapore Dollar": "SGD",
        "New Taiwan Dollar": "TWD",
        "Hong Kong Dollar": "HKD",
        "South Korean Won": "KRW",
        "Indian Rupee": "INR",
        "Indonesian Rupiah": "IDR"
    }

    # 1. Custom Top Navigation Bar
    with st.container(horizontal_alignment="center"):
        current_tab = st.segmented_control(
            label="Relative Currency Strength Analysis",
            options=["Base Fiat Currency", "Quote Fiat Currency"],
            default="Base Fiat Currency",
            label_visibility="collapsed"
        )

    # 2. Handle Navigation Logic
    if current_tab == "Base Fiat Currency":
        base_fiat_ticker_input = st.session_state.base_fiat_ticker_input
        base_fiat_currency_name = st.session_state.base_fiat_currency_name
        st.markdown(f"<h1 style='text-align: center;'>Base Fiat Currency: {base_fiat_ticker_input}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>Currency Name: {base_fiat_currency_name}</h2>", unsafe_allow_html=True)

        with st.spinner("Loading Data ..."):
            # Processing the Comparison Charts
            comparison_currencies_fig = get_forex_comparison_charts(
                base_fiat_ticker_input,
                base_fiat_currency_name,
                major_global_currencies,
                base_or_quote="base"
            )

        st.subheader("Cross-Currencies Charts")
        st.plotly_chart(comparison_currencies_fig, width="stretch")

    else:
        quote_fiat_ticker_input = st.session_state.quote_fiat_ticker_input
        quote_fiat_currency_name = st.session_state.quote_fiat_currency_name
        st.markdown(f"<h1 style='text-align: center;'>Quote Fiat Currency: {quote_fiat_ticker_input}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>Currency Name: {quote_fiat_currency_name}</h2>", unsafe_allow_html=True)

        with st.spinner("Loading Data ..."):
            # Processing the Comparison Charts
            comparison_currencies_fig = get_forex_comparison_charts(
                quote_fiat_ticker_input,
                quote_fiat_currency_name,
                major_global_currencies,
                base_or_quote="quote"
            )

        st.subheader("Cross-Currencies Charts")
        st.plotly_chart(comparison_currencies_fig, width="stretch")