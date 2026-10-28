import streamlit as st
from src.shared.finance_utils import highlight_exact_cells, conditional_highlight_negative
from src.shared.news_parser import parse_news
from src.currencies.raw_data_scraper import process_crypto_ticker, generate_crypto_profile_table
from src.currencies.cryptocurrency_analysis import get_trending_database, get_crypto_price_action

st.markdown("<h2 style='text-align: center;'>General Information</h2>", unsafe_allow_html=True)

# Get the wildly / dynamic trending database of cryptocurrencies
crypto_database, error_message = get_trending_database()

# Keeps track of values when navigating tabs/pages
if "crypto_ticker_input" not in st.session_state:
    st.session_state.crypto_ticker_input = ""

col1, col2, col3 = st.columns(3)

with col1:
    crypto_ticker_input = st.text_input("**Enter Crypto Ticker**", placeholder="E.g: BTC", value=st.session_state.crypto_ticker_input)
    
# Check if a ticker was processed or changed
if crypto_ticker_input:
    st.session_state.crypto_ticker_input = crypto_ticker_input

    with st.spinner("Loading Data ..."):
        # Process the live yfinance object instantly and return information dictionary, news, and historical data
        info_dict, raw_news, historical_data = process_crypto_ticker(crypto_ticker_input)
        st.session_state.crypto_info_dict = info_dict

        if historical_data.empty:
            crypto_ticker_input_error = "Crypto Ticker that was inputted does not exist. Please re-enter another ticker."
        else:
            # Initialize a blank error message
            crypto_ticker_input_error = ""

            # Create the Cryptocurrency Profile Table
            general_info_df = generate_crypto_profile_table(info_dict)
            general_info_df = general_info_df.style.apply(
                highlight_exact_cells,
                axis=1,
                target_cells=[(13,1), (20,1)] # Highlighting the Current Price and Current Exchange Trading Volume
            ).apply(
                lambda row: [conditional_highlight_negative(val, 0.80) for val in row],
                axis=1,
                subset=([24], slice(None)) # Market Cap to FDV Ratio
            ).apply(
                lambda row: [conditional_highlight_negative(val, 0.01) for val in row],
                axis=1,
                subset=([25], slice(None)) # Volume to Market Cap Ratio
            )

            # Parse the Raw News Data to get a clean news dataframe
            news_df = parse_news(raw_news)
            
            # Get the Cryptocurrency Historical Data
            st.session_state.crypto_historical_data = historical_data
            crypto_price_action_fig = get_crypto_price_action(historical_data)
       
        # Session State variable of the error message to be used in the other pages of Cryptocurrencies Analysis
        st.session_state.crypto_ticker_input_error = crypto_ticker_input_error

    if crypto_ticker_input_error:
        with col1:
            st.error(crypto_ticker_input_error)
    else:
        with col1:
            # Displaying the Cryptocurrency Profile Information
            st.markdown("**Cryptocurrency Profile**")
            st.table(general_info_df, width="stretch")

        with col2:
            # Displaying the Project / Protocol Information
            st.markdown("**Project / Protocol Description**")
            st.text(info_dict.get("description", "N/A"))

            # Displaying the table of trending cryptocurrencies
            st.markdown("**Trending Cryptocurrencies (Wildly Fluctuating)**")
            if error_message == "":
                st.dataframe(crypto_database, width="stretch", height="stretch", hide_index=True)
            else:
                st.error(error_message)

        with col3:
            # Displaying the Latest News Information
            st.markdown("**Latest News**")
            if news_df.empty:
                st.warning("No News Articles on this Cryptocurrency")

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

        with st.container(vertical_alignment="center"):
            # Divide the container into 2 columns
            left_main_col, right_main_col = st.columns(2)
            with left_main_col:
                # Price Action Historical Chart
                st.subheader("Historical Price Action Chart")

            with right_main_col:
                with st.container(horizontal=True, horizontal_alignment="right", gap="xsmall"):
                    # Button to go to the Crypto Technical Analysis Page
                    if st.button("Technical Analysis",  icon="📈"):
                        st.switch_page("views/currencies/crypto_technical_analysis.py")

                    # Button to go to the Tokenomics Comparisons Page
                    if st.button("Comparative Tokenomics Analysis",  icon="📊"):
                        st.switch_page("views/currencies/comparative_tokenomics_analysis.py")

        st.plotly_chart(crypto_price_action_fig, height=600)