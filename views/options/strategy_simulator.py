import pandas as pd
import streamlit as st
from src.shared.finance_utils import format_date
from src.options.raw_data_scraper import get_strategy_option_chain_data
from src.options.quantitative_analysis import get_risk_return_profile_chart

if st.session_state.option_ticker_input == "":
    st.warning("Please enter the option ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

option_ticker_input = st.session_state.option_ticker_input
st.markdown(f"<h1 style='text-align: center;'>Option Ticker: {option_ticker_input}</h1>", unsafe_allow_html=True)

if st.session_state.option_ticker_input_error:
    st.error("Option Ticker that was inputted does not exist or is not available in Yahoo Finance. Please re-enter another ticker first before viewing this page.")
else:
    current_price = st.session_state.security_underlying_price
    dividend_yield = st.session_state.dividend_yield
    risk_free_rate = st.session_state.risk_free_rate

    st.markdown(f"<h2 style='text-align: center;'>Underlying Price: ${current_price:,.2f}, Dividend Yield: {dividend_yield * 100:,.2f}%</h2>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Options Strategy Matrix</h2>", unsafe_allow_html=True)
    # Defining a dictionary of various multi-option strategies
    strategy_buckets = {
        "Vertical Spreads": {
            "Overview": "All legs share the exact same expiration date but use different strike prices. Primarily used to trade **Delta** (market direction) with defined risk.",
            "Strategies": {
                "Bull Call Spread": {
                    "Outlook": "Moderately Bullish 📈",
                    "Type": "Net Debit",
                    "Setup": "Buy 1 lower strike Call + Sell 1 higher strike Call (same exp)."
                },
                "Bear Put Spread": {
                    "Outlook": "Moderately Bearish 📉",
                    "Type": "Net Debit",
                    "Setup": "Buy 1 higher strike Put + Sell 1 lower strike Put (same exp)."
                },
                "Bull Put Spread": {
                    "Outlook": "Moderately Bullish / Neutral 📈",
                    "Type": "Net Credit",
                    "Setup": "Sell 1 higher strike Put + Buy 1 lower strike Put (same exp)."
                },
                "Bear Call Spread": {
                    "Outlook": "Moderately Bearish / Neutral 📉",
                    "Type": "Net Credit",
                    "Setup": "Sell 1 lower strike Call + Buy 1 higher strike Call (same exp)."
                }
            }
        },
        "Volatility Combinations": {
            "Overview": "Non-directional strategies using both calls and puts at the same or adjacent strikes. Primarily used to trade **Vega** (Implied Volatility spikes or collapses).",
            "Strategies": {
                "Long Straddle": {
                    "Outlook": "High Volatility Breakout 💥",
                    "Type": "Net Debit",
                    "Setup": "Buy 1 ATM Call + Buy 1 ATM Put (same strike & exp)."
                },
                "Short Straddle": {
                    "Outlook": "Low Volatility / Flat 🛑",
                    "Type": "Net Credit",
                    "Setup": "Sell 1 ATM Call + Sell 1 ATM Put (same strike & exp)."
                },
                "Long Strangle": {
                    "Outlook": "Massive Volatility Breakout 💥",
                    "Type": "Net Debit",
                    "Setup": "Buy 1 OTM Call + Buy 1 OTM Put (different strikes, same exp)."
                },
                "Short Strangle": {
                    "Outlook": "Range-Bound / Stable 🛑",
                    "Type": "Net Credit",
                    "Setup": "Sell 1 OTM Call + Sell 1 OTM Put (different strikes, same exp)."
                }
            }
        },
        "Time & Boundary Spreads": {
            "Overview": "Strategies where legs are split across different expiration cycles (front-month vs. back-month). Designed to extract value from **Theta** (Time Decay) disparities.",
            "Strategies": {
                "Long Calendar Spread": {
                    "Outlook": "Neutral to Mildly Directional ⏳",
                    "Type": "Net Debit",
                    "Setup": "Sell 1 near-term Call/Put + Buy 1 longer-term Call/Put (same strike)."
                },
                "Short Calendar Spread": {
                    "Outlook": "Sharp Breakout / IV Collapse ⚡",
                    "Type": "Net Credit",
                    "Setup": "Buy 1 near-term Call/Put + Sell 1 longer-term Call/Put (same strike)."
                },
                "Long Diagonal Spread": {
                    "Outlook": "Directional + Multi-timeframe 🌍",
                    "Type": "Net Debit",
                    "Setup": "Sell 1 near-term Call/Put + Buy 1 longer-term Call/Put (different strikes)."
                },
                "Short Diagonal Spread": {
                    "Outlook": "Directional + IV Collapse ⚡",
                    "Type": "Net Credit",
                    "Setup": "Buy 1 near-term Call/Put + Sell 1 longer-term Call/Put (different strikes)."
                }
            }
        },
        "Butterfly & Condor Wings": {
            "Overview": "Complex 3-strike or 4-strike configurations. Used to construct highly precise target profit zones or capture cheap wider-boundary breakouts.",
            "Strategies": {
                "Iron Condor": {
                    "Outlook": "Range-Bound / Neutral 🪟",
                    "Type": "Net Credit",
                    "Setup": "Bull Put Spread + Bear Call Spread combined (4 strikes, same exp)."
                },
                "Iron Butterfly": {
                    "Outlook": "Pin Target / Highly Neutral 🎯",
                    "Type": "Net Credit",
                    "Setup": "Buy 1 OTM Put + Sell 2 ATM (1 Put/1 Call) + Buy 1 OTM Call (same exp)."
                },
                "Long Call Butterfly": {
                    "Outlook": "Pin Target / Cheap Neutral 🎯",
                    "Type": "Net Debit",
                    "Setup": "Buy 1 ITM Call + Sell 2 ATM Calls + Buy 1 OTM Call (same exp)."
                },
                "Long Iron Condor": {
                    "Outlook": "Wider Breakout 💥",
                    "Type": "Net Debit",
                    "Setup": "Buy the inner wings + Sell the outer wings (Reverse Iron Condor)."
                },
                "Short Call Butterfly": {
                    "Outlook": "Breakout away from Center ⚡",
                    "Type": "Net Credit",
                    "Setup": "Sell 1 ITM Call + Buy 2 ATM Calls + Sell 1 OTM Call (same exp)."
                },
                "Short Iron Condor": {
                    "Outlook": "Wider Breakout 💥",
                    "Type": "Net Debit",
                    "Setup": "Mirror image of an Iron Condor; betting on an explosive move."
                }
            }
        }
    }

    cols = st.columns(4)

    # Iterate through the buckets and display them into their respective column columns
    for col, (bucket_name, bucket_data) in zip(cols, strategy_buckets.items()):
        with col:
            # Display Header & Bucket Overview
            st.subheader(bucket_name)
            st.markdown(bucket_data["Overview"])
            
            # Display each strategy inside an expander
            for strategy_name, info in bucket_data["Strategies"].items():
                with st.expander(strategy_name):
                    st.markdown(f"**Outlook:** {info['Outlook']}")
                    st.markdown(f"**Cash Flow:** {info['Type']}")
                    st.markdown(f"**Setup:**\n{info['Setup']}")

    # Horizontal line dividing certain sections
    st.divider()

    strategy_parameters_df =  pd.DataFrame(
        {
            "Option Leg": ["Long Call", "Short Call", "Long Put", "Short Put"],
            "Strike Price": [0.0, 0.0, 0.0, 0.0],
            "Number of Contracts": [0, 0, 0, 0],
            "Expiration Date": ["", "", "", ""]
        }
    )
    strategy_parameters_df = strategy_parameters_df.set_index("Option Leg") # Setting the index to be Option Leg

    col1, col2 = st.columns(2)

    with col1:
        # Strategy Parameters Input Section
        st.subheader("Strategy Parameters")
        strategy_input = st.data_editor(
            strategy_parameters_df,
            num_rows="fixed",
            hide_index=False,
            width="stretch",
            key="options_strategy_editor",
            column_config={
                "Strike Price": st.column_config.NumberColumn(
                    "Strike Price",
                    min_value=0,
                    format="dollar",
                ),
                "Number of Contracts": st.column_config.NumberColumn(
                    "Number of Contracts",
                    min_value=1,
                    step=1
                ),
                "Expiration Date": st.column_config.SelectboxColumn(
                    "Expiration Date",
                    options=st.session_state.available_expiration_dates,
                    format_func=lambda x: format_date(x)
                )
            }
        )

    with col2:
        # Option Chain Data Output from the Strategy Parameters Input Section
        st.subheader("Option Chain Market Data")
        market_df, strike_errors, active_legs = get_strategy_option_chain_data(option_ticker_input, strategy_input)

        st.dataframe(
            market_df,
            width="stretch",
            column_config={
                "Latest Premium": st.column_config.NumberColumn("Latest Premium", format="dollar"),
                "Latest Bid": st.column_config.NumberColumn("Latest Bid", format="dollar"),
                "Latest Ask": st.column_config.NumberColumn("Latest Ask", format="dollar"),
                "Total Credit / Debit": st.column_config.NumberColumn("Total Credit / Debit", format="dollar"),
                "Days to Expiration": st.column_config.NumberColumn("Days to Expiration", format="localized"),
                "Implied Volatility": st.column_config.NumberColumn("Implied Volatility", format="percent")
            }
        )

    # Warning Messages for wrong / unavailable strike price inputs in the strategy parameters section
    if len(strike_errors) != 0:
        for error_message in strike_errors:
            st.warning(error_message)

    # Horizontal line dividing certain sections
    st.divider()

    if active_legs:
        # Risk-Return Profile at Expiration Section
        st.subheader("Risk-Return Profile at Expiration")

        # Find the earliest DTE across all legs (this is the absolute maximum window we can simulate)
        min_initial_dte = min([leg["initial_dte"] for leg in active_legs])
        
        # Render the interactive Day Slider widget 
        days_elapsed = st.slider(
            "📅 Simulate Time Passing (Days from Today until the nearest Expiration Date)",
            min_value=0,
            max_value=int(min_initial_dte),
            value=int(min_initial_dte), # Defaults to showing the payoff at nearest expiration
            step=1,
            help="Slide right to simulate holding the position over time until the first option expire. The curve shifts as Theta decay hits the legs."
        )
    
        risk_return_profile_fig = get_risk_return_profile_chart(active_legs, days_elapsed, risk_free_rate, dividend_yield)
        st.plotly_chart(risk_return_profile_fig, width="stretch", height=600)