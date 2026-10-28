import streamlit as st
from src.futures.raw_data_scraper import get_commodity_db
from src.futures.comparative_market_analysis import get_commodity_comparison_charts

if st.session_state.commodity_ticker_input == "":
    st.warning("Please enter the commodity ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.info(
    """
    A Comparative Market Analysis (CMA) is a structured evaluation method used to establish the fair value of an asset by systematically comparing 
    it against similar benchmarks—known as "comparables" or "comps" within the same category or geographic region. While highly famous in real estate
    for estimating property values, the foundational logic of a CMA applies broadly to business operations, product pricing, and commodity markets to 
    identify key opportunities and anomalies.
    """
)

commodity_category = st.session_state.commodity_category
st.markdown(f"<h1 style='text-align: center;'>Category: {commodity_category}</h1>", unsafe_allow_html=True)

if st.session_state.commodity_ticker_input_error:
    st.error("Commodity Ticker that was inputted does not exist. Please re-enter another ticker first before viewing this page.")
else:
    # Slicing the Commodity Database to only choose the tickers of the same category as the chosen commodity ticker
    commodity_df = get_commodity_db()
    category_df = commodity_df.loc[commodity_df["Category"] == commodity_category]

    # Plotting the comparison charts
    commodity_comparison_fig = get_commodity_comparison_charts(category_df)
    st.plotly_chart(commodity_comparison_fig, width="stretch")