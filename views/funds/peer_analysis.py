import streamlit as st
from src.funds.cross_fund_analysis import generate_comparison_funds, get_net_expense_ratio_chart, get_return_comparison_chart

if st.session_state.fund_ticker_input == "":
    st.warning("Please enter the investment fund ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.info(
    """
    Peer analysis for investment funds involves benchmarking a target fund against similar portfolios rather than evaluating 
    its performance in isolation. This analysis helps investors identify top-performing managers, understand if a fund's high 
    returns are due to skill or just a rising market trend, and spot overvalued or under-performing funds. Investors do this 
    by comparing key metrics like expense ratios, Sharpe ratios (risk-adjusted returns), turnover rates, and historical yields.

    In this section, peer analysis focuses on categorical comparisons that has unique characteristics of investment style, market 
    capitalizatoin, sector focus etc. Category-level comparison is a head-to-head battle between fund managers. Funds within the 
    exact same category (like Large Growth) are fighting for the same investor capital, benchmarked against the same index (like 
    the Russell 1000 Growth), and navigating identical market environments with the same types of underlying holdings.
    """
)

fund_ticker_input = st.session_state.fund_ticker_input
st.markdown(f"<h1 style='text-align: center;'>Investment Fund Ticker: {fund_ticker_input}</h1>", unsafe_allow_html=True)

if st.session_state.fund_ticker_input_error:
    st.error("Fund Ticker that was inputted does not exist. Please re-enter another ticker first before viewing this page.")
else:
    # Storing Session State variables into local variables
    fund_type = st.session_state.fund_type
    fund_category = st.session_state.fund_category
    net_expense_ratio = st.session_state.net_expense_ratio
    category_average_expense_ratio = st.session_state.category_average_expense_ratio

    st.markdown(f"<h2 style='text-align: center;'>Category: {fund_category}</h2>", unsafe_allow_html=True)

    with st.spinner("Loading Data ..."):
        # Getting the Top 10 Funds and Comparison Charts
        top_10_funds = generate_comparison_funds(fund_type, fund_category)

        # Checking if there is any investment fund information for this category
        if top_10_funds.empty:
            peer_analysis_error = "Currently, there is no list of investment funds for this category, so peer analysis cannot be executed."
        else:
            peer_analysis_error = ""
            net_expense_ratio_fig = get_net_expense_ratio_chart(
                    top_10_funds,
                    fund_ticker_input,
                    net_expense_ratio,
                    category_average_expense_ratio
                )
            return_comparison_fig = get_return_comparison_chart(top_10_funds, fund_ticker_input)

    col1, col2 = st.columns(2)

    if peer_analysis_error:
        st.error(peer_analysis_error)
    else:
        with col1:
            st.subheader(f"Top {len(top_10_funds)} {"ETFs" if st.session_state.fund_type == "ETF" else "Mutual Funds"}")
            st.dataframe(top_10_funds, width="stretch", height="stretch", row_height=50)

        with col2:
            st.subheader("Net Expense Ratio Comparison")
            st.plotly_chart(net_expense_ratio_fig, width="stretch")

        st.subheader("Fund Performance Comparison")
        st.plotly_chart(return_comparison_fig, width="stretch")