import streamlit as st
from src.shared.finance_utils import highlight_exact_cells
from src.shared.news_parser import parse_news
from src.currencies.raw_data_scraper import process_forex_ticker, generate_forex_profile_table
from src.currencies.fiat_currency_analysis import get_currency_database, get_fiat_details, get_exchange_rate_trend

st.markdown("<h2 style='text-align: center;'>General Information</h2>", unsafe_allow_html=True)

# Initialize the currency database
currency_database = get_currency_database()

# Keeps track of values when navigating tabs/pages
if "base_fiat_ticker_input" not in st.session_state:
    st.session_state.base_fiat_ticker_input = ""
if "quote_fiat_ticker_input" not in st.session_state:
    st.session_state.quote_fiat_ticker_input = ""

col1, col2, col3 = st.columns(3)

with col1:
    col_a, col_b = st.columns(2)

    with col_a:
        base_fiat_ticker_input = st.text_input("**Enter Base Fiat Currency Ticker**", placeholder="E.g: USD", value=st.session_state.base_fiat_ticker_input)
        if base_fiat_ticker_input:
            st.session_state.base_fiat_ticker_input = base_fiat_ticker_input
            base_fiat_details = get_fiat_details(base_fiat_ticker_input, currency_database)
            st.session_state.base_fiat_currency_name = base_fiat_details.at[0, "Name"]
            st.table(base_fiat_details, width="stretch")

    with col_b:
        quote_fiat_ticker_input = st.text_input("**Enter Quote Fiat Currency Ticker**", placeholder="E.g: IDR", value=st.session_state.quote_fiat_ticker_input)
        if quote_fiat_ticker_input:
            st.session_state.quote_fiat_ticker_input = quote_fiat_ticker_input
            quote_fiat_details = get_fiat_details(quote_fiat_ticker_input, currency_database)
            st.session_state.quote_fiat_currency_name = quote_fiat_details.at[0, "Name"]
            st.table(quote_fiat_details, width="stretch")

with col2:
    # Global Currency Database
    st.markdown("**Global Currency Database**")
    st.dataframe(
        currency_database,
        width="stretch",
        height="stretch",
        hide_index=True,
        row_height=80
    )

if base_fiat_ticker_input and quote_fiat_ticker_input:
    forex_ticker_input = base_fiat_ticker_input + quote_fiat_ticker_input + "=X"
    st.session_state.forex_currency_pair = base_fiat_ticker_input + "-" + quote_fiat_ticker_input

    with st.spinner("Loading Data ..."):
        # Process the live yfinance object instantly and return information dictionary, news, and historical data
        info_dict, raw_news, historical_data = process_forex_ticker(forex_ticker_input)

        if historical_data.empty:
            forex_ticker_input_error = "Forex Ticker that was inputted does not exist. Please re-enter another ticker."
        else:
            # Initialize a blank error message
            forex_ticker_input_error = ""

            # Create the Forex Profile Table
            general_info_df = generate_forex_profile_table(info_dict)
            current_exchange_rate = general_info_df.at[1, "Information"].replace(",", "") # Getting the Current Exchange Rate before applying styling
            general_info_df = general_info_df.style.apply(
                highlight_exact_cells,
                axis=1,
                target_cells=[(1,1)] # Highlighting the Current Exchange Rate Cell
            )

            # Parse the Raw News Data to get a clean news dataframe
            news_df = parse_news(raw_news)
            
            # Get the Exchange Rate Historical Data
            st.session_state.forex_historical_data = historical_data
            exchange_rate_trend_fig = get_exchange_rate_trend(historical_data)

        # Session State variable of the error message to be used in the other pages of Investment Funds Analysis
        st.session_state.forex_ticker_input_error = forex_ticker_input_error

    if forex_ticker_input_error:
        with col1:
            st.error(forex_ticker_input_error)
    else:
        with col1:
            # Currency Converter
            st.markdown("**Currency Converter**")

            col_a, col_b = st.columns(2)

            with col_a:
                # Captures user input as a string
                base_input = st.text_input(f"**Amount of {base_fiat_ticker_input}**", value="1.00")

            with col_b:
                try:
                    # Convert string input to float for calculation
                    base_amount = float(base_input) if base_input else 0.0
                    quote_amount = base_amount * float(current_exchange_rate)

                    # Render the dynamic f-string output next to it
                    quote_output = st.text_input(f"**Equivalent Amount of {quote_fiat_ticker_input}**", value=f"{quote_amount:,}", disabled=True)
                    
                except ValueError:
                    st.write("⚠️ Please enter a valid number.")

            st.markdown("**Foreign Exchange (Forex) Profile**")
            st.table(general_info_df, width="stretch")

        with col3:
            # Displaying the Latest News Information
            st.markdown("**Latest News**")
            if news_df.empty:
                st.warning("No News Articles on this Forex Pair")

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
                # Exchange Rate Historical Chart
                st.subheader("Exchange Rate History")

            with right_main_col:
                with st.container(horizontal=True, horizontal_alignment="right", gap="xsmall"):
                    # Button to go to the Forex Technical Analysis Page
                    if st.button("Technical Analysis",  icon="📈"):
                        st.switch_page("views/currencies/forex_technical_analysis.py")

                    # Button to go to the Relative Currency Strength Analysis Page
                    if st.button("Relative Currency Strength Analysis",  icon="📉"):
                        st.switch_page("views/currencies/relative_currency_strength_analysis.py")

        # Display the Exchange Rate Historical Data Chart underneath the container
        st.plotly_chart(exchange_rate_trend_fig, height=600)