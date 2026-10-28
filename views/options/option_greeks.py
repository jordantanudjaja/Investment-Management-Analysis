import streamlit as st
from src.options.pricing_model import get_option_greek_charts
from src.shared.finance_utils import format_date

if st.session_state.option_ticker_input == "":
    st.warning("Please enter the option ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.markdown(f"<h1 style='text-align: center;'>Option Ticker: {st.session_state.option_ticker_input}</h1>", unsafe_allow_html=True)

if st.session_state.option_ticker_input_error:
    st.error("Option Ticker that was inputted does not exist or is not available in Yahoo Finance. Please re-enter another ticker first before viewing this page.")
else:
    st.markdown(f"<h2 style='text-align: center;'>Expiration Date: {format_date(st.session_state.expiration_date_str)}</h2>", unsafe_allow_html=True)

    calls_df = st.session_state.calls_df
    puts_df = st.session_state.puts_df 
    delta_theta_rho_fig, gamma_vega_fig = get_option_greek_charts(calls_df, puts_df)

    st.info(
        """
        Option Greeks are calculated backwards using the Black-Scholes-Merton (BSM) Model. The Black-Scholes-Merton model is a mathematical formula used to calculate the theoretical 
        fair price of European-style options, after accounting for dividends. It uses six key inputs: the current stock price, the strike price, the time to expiration, the risk-free interest rate, 
        the dividend yield, and the implied volatility (IV) of the underlying asset.

        European-Style Options are options that can only be exercised at the expiry date. American-Style Options can be exercised anytime, which results in a more complex calculation of the 
        model compared to the Black-Scholes-Merton Model.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(delta_theta_rho_fig, width="stretch")

    with col2:
        st.plotly_chart(gamma_vega_fig, width="stretch")