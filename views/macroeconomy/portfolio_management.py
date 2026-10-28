import pandas as pd
import streamlit as st
from src.macroeconomy.modern_portfolio_theory import fetch_portfolio_data, run_mpt_analysis, create_correlation_heatmap

st.info(
    """
    ### 📊 Modern Portfolio Theory (MPT) Overview

    Modern Portfolio Theory (MPT) is an investment framework that aims to maximize a portfolio's expected return for a given level of risk, 
    or conversely minimize risk for a given level of expected return, by carefully choosing the proportions of various assets. The theory operates 
    on **Mean-Variance Optimization**. It assumes investors are rational and risk-averse, meaning that if given two portfolios with the exact same 
    expected return, an investor will always choose the one with less volatility

    ### Core Concept
    * Diversification reduces overall risk.
    * Asset correlation matters more than individual risk.

    ### Key Components
    * **Efficient Frontier:** Optimal portfolios offering max return for risk.
    * **Risk-Return Tradeoff:** Higher returns require higher volatility.
    * **Asset Allocation:** Mixing uncorrelated assets protects capital.

    ### Real-World Limitations
    While elegant, MPT relies on strict assumptions:
    * **Historical Data Dependency:** It assumes past volatilities and asset correlations will hold true in the future.
    * **Normal Distribution:** It maps returns on a perfect Gaussian bell curve, often underestimating severe market crashes ("black swan" events).
    """
)

user_tickers = st.multiselect(
    label="Enter the list of security tickers to be used in the Portfolio Analysis:",
    options=[],
    accept_new_options=True,  # Enables custom text input
    placeholder="E.g: AAPL, MSFT, BTC-USD"
)

if len(user_tickers) >= 2:
    with st.spinner("Fetching market data and solving SLSQP quadratic optimization..."):
        prices_df = fetch_portfolio_data(user_tickers, period="2y")
        
        if not prices_df.empty and len(prices_df.columns) >= 2:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<h3 style='text-align: center;'>Efficient Frontier & Capital Allocation Line</h3>", unsafe_allow_html=True)
                fig, stats = run_mpt_analysis(prices_df, risk_free_rate=st.session_state.risk_free_rate)
                
                # Render Interactive MPT Graph
                st.plotly_chart(fig, width="stretch")

            with col2:
                st.markdown("<h3 style='text-align: center;'>Correlation Matrix</h3>", unsafe_allow_html=True)
                fig_corr = create_correlation_heatmap(prices_df)

                # Render the correlation matrix
                st.plotly_chart(fig_corr, width="stretch")
            
            # Render Optimal Weights Breakdown
            st.markdown("<h3 style='text-align: center;'>Optimal Portfolio Allocations</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Max Sharpe Ratio (Tangency)")
                ms = stats["max_sharpe"]
                with st.container(horizontal=True, wrap=True, border=True):
                    st.metric("Expected Return", f"{ms['return']:.2%}")
                    st.metric("Volatility (Risk)", f"{ms['volatility']:.2%}")
                    st.metric("Sharpe Ratio", f"{ms['sharpe']:.2f}")
                
                weights_df_ms = pd.DataFrame(
                    list(ms["weights"].items()), columns=["Ticker", "Weight"]
                )
                weights_df_ms["Weight"] = weights_df_ms["Weight"].apply(lambda x: f"{x:.2%}")
                st.dataframe(weights_df_ms, hide_index=True, width="stretch")
                
            with col2:
                st.markdown("### Minimum Variance Portfolio")
                mv = stats["min_variance"]
                with st.container(horizontal=True, wrap=True, border=True):
                    st.metric("Expected Return", f"{mv['return']:.2%}")
                    st.metric("Volatility (Risk)", f"{mv['volatility']:.2%}")
                    st.metric("Sharpe Ratio", f"{mv['sharpe']:.2f}")
                
                weights_df_mv = pd.DataFrame(
                    list(mv["weights"].items()), columns=["Ticker", "Weight"]
                )
                weights_df_mv["Weight"] = weights_df_mv["Weight"].apply(lambda x: f"{x:.2%}")
                st.dataframe(weights_df_mv, hide_index=True, width="stretch")
        else:
            st.error("Could not retrieve sufficient historical price data for the selected tickers.")
else:
    st.info("Please select at least 2 tickers to compute the Efficient Frontier.")