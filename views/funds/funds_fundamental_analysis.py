import streamlit as st
from src.shared.finance_utils import highlight_exact_cells, conditional_highlight_negative
from src.shared.news_parser import parse_news
from src.funds.raw_data_scraper import process_fund_ticker, generate_profile_table
from src.funds.fundamental_analysis import (
    process_deep_dive_data,
    get_sector_piechart,
    get_bond_rating_piechart,
    get_asset_class_donutchart
)

st.markdown("<h2 style='text-align: center;'>General Information</h2>", unsafe_allow_html=True)

# Keeps track of values when navigating tabs/pages
if "fund_ticker_input" not in st.session_state:
    st.session_state.fund_ticker_input = ""

col1, col2, col3 = st.columns(3)

with col1:
    fund_ticker_input = st.text_input("**Enter Funds Ticker**", placeholder="E.g: SPY", value=st.session_state.fund_ticker_input)
    
# Check if a ticker was processed or changed
if fund_ticker_input:
    st.session_state.fund_ticker_input = fund_ticker_input

    with st.spinner("Loading Data ..."):
        try:
            # Getting the required variables from the process_fund_ticker function
            info_dict, raw_news, fund_overview, top_holdings, sector_allocation, asset_class_allocation, fund_operations, bond_rating_allocation, historical_data = process_fund_ticker(fund_ticker_input)
        except:
            fund_ticker_input_error = "Fund Ticker that was inputted does not exist. Please re-enter another ticker."
        else:
            # Initialize a blank error message
            fund_ticker_input_error = ""

            # Session State variable to be used in technical analysis
            st.session_state.fund_historical_data = historical_data

            # Use cached functions to generate the company profile table
            general_info_df = generate_profile_table(info_dict, fund_overview)

            # Parse the Raw News Data to get a clean news dataframe
            news_df = parse_news(raw_news)

            # Session State variables to be used in peer analysis
            st.session_state.fund_type = general_info_df.at[1, "Information"]
            st.session_state.fund_category = general_info_df.at[2, "Information"]
            st.session_state.net_expense_ratio = general_info_df.at[10, "Information"]

            # Styling the General Info DataFrame after obtaining the necessary session state variables
            general_info_df = general_info_df.style.apply(
                highlight_exact_cells,
                axis=1,
                target_cells=[(11,1)] # Current Price
            ).apply(
                lambda row: [conditional_highlight_negative(val, 0) for val in row],
                axis=1,
                subset=([14, 15, 16, 17], slice(None)) # Return % Line Items
            )

            # Process the Deep Dive fundamental analysis data of the Fund and returns cleaned data, % share of US Treasuries and Allocation Pie Charts
            deep_dive_data, us_treasuries_share = process_deep_dive_data(top_holdings, sector_allocation, asset_class_allocation, fund_operations, bond_rating_allocation)
            sector_allocation_fig = get_sector_piechart(deep_dive_data["Sector Allocation"])
            asset_class_allocation_fig = get_asset_class_donutchart(deep_dive_data["Asset Class Allocation"])
            bond_rating_allocation_fig = get_bond_rating_piechart(deep_dive_data["Bond Rating Allocation"])

            # Session State variable for Category Average Expense Ratio
            st.session_state.category_average_expense_ratio = deep_dive_data["Fund Operations"].at[0, "Category Average"]
        finally:
            # Session State variable of the error message to be used in the other pages of Investment Funds Analysis
            st.session_state.fund_ticker_input_error = fund_ticker_input_error

    if fund_ticker_input_error:
        with col1:
            st.error(fund_ticker_input_error)
    else:
        with col1:
            # Displaying the Fund Profile Information
            st.markdown("**Fund Profile**")       
            st.table(general_info_df, width='stretch')

        with col2:
            # Displaying the Fund Summary Information
            st.markdown("**Investment Policy**")
            st.text(info_dict.get("longBusinessSummary", "N/A"))

            # Displaying the Top Holdings Information
            st.markdown("**Top Holdings**")
            st.table(deep_dive_data["Top Holdings"], width="stretch")

            # Displaying the Fund Operations Information
            st.markdown("**Operation Insights**")
            st.table(deep_dive_data["Fund Operations"], width="stretch")

        with col3:
            # Displaying the Latest News Information
            st.markdown("**Latest News**")
            if news_df.empty:
                st.warning("No News Articles on this Investment Fund")

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
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sector / Bond Rating Allocation")
            # Creating the nav bar for chart selection between sector and bond rating allocation
            with st.container(horizontal_alignment="center"):
                chart_choice = st.pills(
                    label="Select View:",
                    options=["Sector Allocation", "Bond Rating Allocation"],
                    default="Sector Allocation",
                    label_visibility="collapsed" # Hide the label for a cleaner nav bar look,
                )

            if chart_choice == "Sector Allocation":
                st.plotly_chart(sector_allocation_fig, width="stretch")
            else:
                st.markdown(
                    f"**Percentage of Risk-Free US Treasury Securities (Bills, Notes, Bonds):** {us_treasuries_share * 100:,.2f}%",
                    text_alignment="center"
                )
                st.plotly_chart(bond_rating_allocation_fig, width="stretch")

        with col2:
            st.subheader("Asset Class Allocation")
            st.plotly_chart(asset_class_allocation_fig, width="stretch")