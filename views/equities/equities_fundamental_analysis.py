import streamlit as st
from src.shared.finance_utils import highlight_exact_cells, conditional_highlight_positive
from src.shared.news_parser import parse_news
from src.equities.raw_data_scraper import process_stock_ticker, generate_profile_table
from src.equities.financial_statements import format_income_stmt, format_balance_sheet, format_cashflow_stmt
from src.equities.fundamental_analysis import (
    process_financial_statements,
    format_statement_summary,
    format_financial_performance,
    format_financial_guardrails,
    get_insights_summary
)

st.markdown("<h2 style='text-align: center;'>General Information</h2>", unsafe_allow_html=True)

# Keeps track of values when navigating tabs/pages
if "stock_ticker_input" not in st.session_state:
    st.session_state.stock_ticker_input = ""

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(horizontal=True, vertical_alignment="bottom", wrap=True):
        stock_ticker_input = st.text_input("**Enter Stock Ticker**", placeholder="E.g: AAPL", value=st.session_state.stock_ticker_input)
        keywords_check_button_placeholder = st.empty()
    
# Check if a ticker was processed or changed
if stock_ticker_input:
    st.session_state.stock_ticker_input = stock_ticker_input

    with st.spinner("Loading Data ..."):
        try:
            # Getting the required variables from the process_stock_ticker function
            info_dict, raw_news, INCOME_STMT, BALANCE_SHEET, CASHFLOW_STMT, historical_data, price_history, future_revenue_estimates = process_stock_ticker(stock_ticker_input)
        except:
            stock_ticker_input_error = "Stock Ticker that was inputted does not exist. Please re-enter another ticker."
        else:
            # Initialize a blank error message
            stock_ticker_input_error = ""

            # Session State variables to be used in financial statements keywords file and DCF calculations
            st.session_state.stock_info_dict = info_dict
            st.session_state.income_stmt = INCOME_STMT      
            st.session_state.balance_sheet = BALANCE_SHEET 
            st.session_state.cashflow_stmt = CASHFLOW_STMT
            st.session_state.future_revenue_estimates = future_revenue_estimates

            # Session State variable to be used in technical analysis
            st.session_state.stock_historical_data = historical_data

            # Use cached functions to generate the company profile table
            general_info_df = generate_profile_table(info_dict)   
            general_info_df = general_info_df.style.apply(
                highlight_exact_cells,
                axis=1,
                target_cells=[(8,1)] # Current Price
            ).apply(
                lambda row: [conditional_highlight_positive(val, 1) for val in row],
                axis=1,
                subset=([13, 14], slice(None)) # PEG and PEGY Ratio
            )

            # Parse the Raw News Data to get a clean news dataframe
            news_df = parse_news(raw_news)

            # Get the cleaned and parsed financial statements, and financial performance data and assign them to variables
            income_stmt_data, balance_sheet_data, cashflow_stmt_data, financial_stmt_summary, financial_perf_data, financial_guardrails_df = process_financial_statements(
                INCOME_STMT, BALANCE_SHEET, CASHFLOW_STMT, price_history
            )

            # Getting the Positive and Negative Insights from the latest Financial Guardrails Data
            positive_insights, negative_insights = get_insights_summary(financial_guardrails_df)

            # Session State variables to be used in Discounted Cash Flow and Dividend Discount Model Analysis
            st.session_state.income_stmt_data = income_stmt_data["Essential Data"]
            st.session_state.balance_sheet_data = balance_sheet_data["Essential Data"]
            st.session_state.cashflow_stmt_data = cashflow_stmt_data["Essential Data"]
            st.session_state.financial_stmt_summary = financial_stmt_summary
            st.session_state.financial_perf_data = financial_perf_data

            # Session State variables for keywords to be used in error tracking
            st.session_state.income_stmt_keywords = income_stmt_data["Keywords"]
            st.session_state.balance_sheet_keywords = balance_sheet_data["Keywords"]
            st.session_state.cashflow_stmt_keywords = cashflow_stmt_data["Keywords"]

            # Formatted Financial Statements Data to be displayed in the front-end
            formatted_income_stmt_data = format_income_stmt(income_stmt_data["Essential Data"])
            formatted_balance_sheet_data = format_balance_sheet(balance_sheet_data["Essential Data"])
            formatted_cashflow_stmt_data = format_cashflow_stmt(cashflow_stmt_data["Essential Data"])
            formatted_financial_stmt_summary = format_statement_summary(financial_stmt_summary)
            formatted_financial_perf_data = format_financial_performance(financial_perf_data)
            formatted_financial_guardrails = format_financial_guardrails(financial_guardrails_df)
        finally:
            # Session State variable of the error message to be used in the other pages of Equities Analysis
            st.session_state.stock_ticker_input_error = stock_ticker_input_error

    if stock_ticker_input_error:
        with col1:
            st.error(stock_ticker_input_error)
    else:
        with col1:
            # Button to check the raw financial statements and whether the keywords are still intact from the yfinance API
            if keywords_check_button_placeholder.button("Keywords Check",  icon="☑️"):
                st.switch_page("views/equities/financial_statements_keywords.py")

            # Displaying the Company Profile Information
            st.markdown("**Company Profile**")       
            st.table(general_info_df, width='stretch')

        with col2:
            # Displaying the Business Summary Information
            st.markdown("**Business Summary**")
            st.text(info_dict.get("longBusinessSummary", "N/A"))

        with col3:
            # Displaying the Latest News Information
            st.markdown("**Latest News**")
            if news_df.empty:
                st.warning("No News Articles on this Stock")
            
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
        st.markdown("<h2 style='text-align: center;'>Latest Fiscal Year-End Insights</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🟢 Green Flags")
            if positive_insights:
                for metric, details in positive_insights.items():
                    with st.expander(f"✅ **{metric}** ({details.get('Value', 'N/A')})"):
                        m_col1, m_col2 = st.columns(2)
                        m_col1.metric("Criteria", details.get('Criteria', 'N/A'))
                        m_col2.metric("Actual Value", details.get('Value', 'N/A'))
                        st.markdown(f"**Rationale:** {details.get('Rationale', 'N/A')}")
            else:
                st.success("No Green Flag Insights")

        with col2:
            st.subheader("🚩 Red Flags")
            if negative_insights:
                for metric, details in negative_insights.items():
                    with st.expander(f"🚨 **{metric}** ({details.get('Value', 'N/A')})"):
                        m_col1, m_col2 = st.columns(2)
                        m_col1.metric("Criteria", details.get('Criteria', 'N/A'))
                        m_col2.metric("Actual Value", details.get('Value', 'N/A'))
                        st.markdown(f"**Rationale:** {details.get('Rationale', 'N/A')}")
            else:
                st.error("No Red Flag Insights")

        # Horizontal line dividing certain sections
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            # Financial Guardrails Section (Expanded using Warren Buffett's guardrails as the foundation)
            st.subheader("Financial Guardrails")
            st.dataframe(
                formatted_financial_guardrails,
                hide_index=True,
                width='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )
            
        with col2:
            # Financial Statement Summary Section
            st.subheader("Financial Statements Summary")
            st.dataframe(
                formatted_financial_stmt_summary,
                hide_index=True,
                width='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )

        with col3:
            # Financial Performance Data Section
            st.subheader("Financial Performance Data")
            st.dataframe(
                formatted_financial_perf_data,
                hide_index=True,
                width='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )    

        # Horizontal line dividing certain sections
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            # Income Statement Section
            st.subheader("Income Statement")
            st.dataframe(
                formatted_income_stmt_data,
                hide_index=True,
                width='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )

        with col2:
            # Balance Sheet Section
            st.subheader("Balance Sheet")
            st.dataframe(
                formatted_balance_sheet_data,
                hide_index=True,
                width='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )

        with col3:
            # Cash Flow Statement Section
            st.subheader("Cash Flow Statement")
            st.dataframe(
                formatted_cashflow_stmt_data,
                hide_index=True,
                width='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )