import streamlit as st
from src.shared.news_parser import parse_news
from src.futures.raw_data_scraper import process_futures_ticker, get_commodity_db
from src.futures.historical_chart import get_futures_price_action

st.markdown("<h2 style='text-align: center;'>General Information</h2>", unsafe_allow_html=True)

# Get the database of the commodities listed in yfinance
commodities_df = get_commodity_db()

# Keeps track of values when navigating tabs/pages
if "commodity_ticker_input" not in st.session_state:
    st.session_state.commodity_ticker_input = ""

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(horizontal=True, wrap=True):
        commodity_ticker_input = st.text_input("**Enter Commodity Ticker**", placeholder="E.g: GC", value=st.session_state.commodity_ticker_input)
        commodity_name_placeholder = st.empty()

with col2:
    st.markdown("**Commodity Database**")
    # Render the interactive dataframe stretched to fill the app container
    st.dataframe(commodities_df, width="stretch", height="stretch", column_config={"Description": None})

# Check if a ticker was processed or changed
if commodity_ticker_input:
    st.session_state.commodity_ticker_input = commodity_ticker_input

    with st.spinner("Loading Data ..."):
        try:
            # Process the live yfinance object instantly and return relevant data
            current_price, open_interest, current_front_month_contract_expiry, raw_news, historical_data = process_futures_ticker(commodity_ticker_input)
        except:
            commodity_ticker_input_error = "Commodity Ticker that was inputted does not exist. Please re-enter another ticker. Use the Commodity Database as a guide for what is available as a ticker."
        else:
            # Initialize a blank error message
            commodity_ticker_input_error = ""

            # Get relevant information from the commodity database
            commodity_name = commodities_df.at[commodity_ticker_input, "Name"]
            unit_price = commodities_df.at[commodity_ticker_input, "Unit Price"]
            commodity_description = commodities_df.at[commodity_ticker_input, "Description"]
            commodity_name_placeholder.metric(label="Commodity Name", value=commodity_name)

            # Relevant Session State Variables
            st.session_state.commodity_category = commodities_df.at[commodity_ticker_input, "Category"]

            # Parse the Raw News Data to get a clean news dataframe
            news_df = parse_news(raw_news)

            # Get the Current Front-Month Futures Contract Historical Data which is equivalent to the spot price of the underlying commodity
            st.session_state.commodity_historical_data = historical_data
            futures_price_action_fig = get_futures_price_action(historical_data)

        finally:
            # Session State variable of the error message to be used in the other pages of Futures Analysis
            st.session_state.commodity_ticker_input_error = commodity_ticker_input_error

    if commodity_ticker_input_error:
        with col1:
            st.error(commodity_ticker_input_error)
    else:
        with col1:
            with st.container(horizontal=True, wrap=True):
                st.metric(
                    label="Current Price per " + unit_price,
                    value=f"${current_price:,.2f}",
                    help="This is technically the price of the current front-month futures contract and not the effective spot price of the commodity. However, because the nearest-expiring futures contract must physically settle or settle in cash when the expiration date lands, arbitrage forces the front-month futures price to closely match the true physical spot price."
                )

                st.metric(
                    label="Open Interest",
                    value=f"{open_interest:,g}",
                    help="Open interest (OI) for a front-month futures contract represents the total number of active, outstanding contracts that market participants hold at the end of a trading day. It measures the cumulative volume of positions that have been opened but not yet closed out via an offsetting trade or settled via physical delivery/cash settlement."
                )

                st.metric(
                    label="Expiration Date",
                    value=current_front_month_contract_expiry,
                    help="This is the expiration date of the Current Front-Month Futures Contract. As the expiration date approaches, the price of the futures contract converges closely with the spot (current cash) price of the underlying asset. Because it is the front-month contract, it typically experiences the highest trading volume and tightest bid-ask spreads of all active months."
                )

        with col1:
            st.markdown("**Commodity Description**")
            st.text(commodity_description)

        with col3:
            # Displaying the Latest News Information
            st.markdown("**Latest News**")
            if news_df.empty:
                st.warning("No News Articles on this Commodity")

            # Iterate through sorted DataFrame rows
            for idx, row in news_df.iterrows():
                # 1. Determine sentiment badge and inline markdown color
                sentiment = row.get("Sentiment", "Neutral")
                
                if sentiment == "Positive":
                    icon = "🟢"
                    colored_sentiment_label = ":green[Positive]"
                elif sentiment == "Negative":
                    icon = "🔴"
                    colored_sentiment_label = ":red[Negative]"
                else:
                    icon = "⚪"
                    colored_sentiment_label = ":gray[Neutral]"

                # Compound score formatting if available
                compound_score = row.get("Compound Score")
                score_str = f" ({compound_score:+.2f})" if compound_score is not None else ""

                # 2. Render the date directly above the expander
                st.markdown(
                    f'<span class="date-tag" style="color: #2563eb; background-color: #eff6ff; padding: 2px 8px; font-weight: 600;">🗓️ {row["Published Date"]}</span>',
                    unsafe_allow_html=True
                )

                # 3. Build header string for the compact expander bar
                expander_title = f"{icon} **{row['Title']}** — *{row['Publisher']}*"

                # 4. Render card content inside st.expander
                with st.expander(expander_title, expanded=False):
                    col_summary, col_meta = st.columns([3.5, 1.5])

                    with col_summary:
                        st.markdown(f"**Summary:** {row['Summary']}")

                    with col_meta:
                        # Displays colored sentiment word when expanded
                        st.markdown(f"**Sentiment:** {colored_sentiment_label}{score_str}")
                        
                        st.link_button(
                            "Read Full Article ↗",
                            row["URL"],
                            width="stretch",
                            type="secondary",
                        )

        # Horizontal line dividing certain sections
        st.divider()

        st.subheader(f"Historical Price Action Chart (Price per contract ~ Price per {unit_price})")
        st.plotly_chart(futures_price_action_fig, width="stretch")