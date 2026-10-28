import numpy as np
import streamlit as st
from src.equities.competitor_analysis import get_top_10_companies, get_mkt_weight_chart, get_sector_industry_comparisons

if st.session_state.stock_ticker_input == "":
    st.warning("Please enter the stock ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.info(
    """
    Competitor analysis involves benchmarking a target company against its peers. Instead of looking at a stock in a vacuum, this analysis contextually evaluates performance. 
    It helps investors identify market leaders, overvalued or undervalued stocks, and industry outliers by comparing key financial metrics like P/E ratios, profit margins, 
    and revenue growth.
    
    ### Sectors vs. Industries
    
    While often used interchangeably, sectors and industries represent different levels of classification:
    
    - **Sector:** A large segment of the economy containing companies that share similar macro-economic characteristics (e.g., Technology, Healthcare, Financials). There are 
    typically 11 major sectors. 
        - Sector-level comparison looks at the broad economic pillars of the market. Because sectors contain vastly different business models, you are 
    not looking for identical twins; instead, you are analyzing how different business drivers perform under identical economic conditions.
    - **Industry:** A much more specific grouping of companies engaged in similar business activities within a sector. For example, within the Technology sector, 
    industries include Software, Semiconductors, and IT Services. 
        - Industry-level comparison is a hyper-focused head-to-head battle. Companies within the same industry compete 
    for the same market share, utilize similar supply chains, and target the exact same customer demographics.
    """
)

stock_ticker_input = st.session_state.stock_ticker_input
st.markdown(f"<h1 style='text-align: center;'>Stock Ticker: {stock_ticker_input}</h1>", unsafe_allow_html=True)

if st.session_state.stock_ticker_input_error:
    st.error("Stock Ticker that was inputted does not exist. Please re-enter another ticker first before viewing this page.")
else:
    # 1. Custom Top Navigation Bar
    with st.container(horizontal_alignment="center"):
        current_tab = st.segmented_control(
            label="Competitor Analysis",
            options=["Sector Analysis", "Industry Analysis"],
            default="Sector Analysis",
            label_visibility="collapsed" # Keeps it clean like a real nav bar
        )

    # 2. Handle Navigation Logic
    if current_tab == "Sector Analysis":
        sector_string = st.session_state.stock_info_dict.get("sector", "N/A")
        st.markdown(f"<h2 style='text-align: center;'>Sector: {sector_string}</h2>", unsafe_allow_html=True)

        with st.spinner("Loading Data ..."):
            # Getting the Top 10 Companies and Comparison Charts in the Sector by Market Weight   
            top_10_companies = get_top_10_companies("Sector", sector_string)
            comparison_charts_fig = get_sector_industry_comparisons("Sector", sector_string, stock_ticker_input)

            # Checking if there is any company information for this sector
            if top_10_companies.empty:
                competitor_analysis_error = "Currently, there is no list of company information for this sector, so competitor analysis cannot be executed."
            else:
                competitor_analysis_error = ""

    else:
        industry_string = st.session_state.stock_info_dict.get("industry", "N/A")
        st.markdown(f"<h2 style='text-align: center;'>Industry: {industry_string}</h2>", unsafe_allow_html=True)

        with st.spinner("Loading Data ..."):
            # Getting the Top 10 Companies and Comparison Charts in the Industry by Market Weight
            top_10_companies = get_top_10_companies("Industry", industry_string)
            comparison_charts_fig = get_sector_industry_comparisons("Industry", industry_string, stock_ticker_input)

            # Checking if there is any company information for this industry
            if top_10_companies.empty:
                competitor_analysis_error = "Currently, there is no list of company information for this industry, so competitor analysis cannot be executed."
            else:
                competitor_analysis_error = ""

    if competitor_analysis_error:
        st.error(competitor_analysis_error)
    else:
        mkt_weight_fig = get_mkt_weight_chart(top_10_companies)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Top {len(top_10_companies)} Companies by Market Weight in the US") # Using len() because some sectors have less than 10 top 10 companies
            st.write(f"**Total Market Weight:** {np.sum(top_10_companies["Market Weight"]):.3f}")
            st.dataframe(top_10_companies)
        with col2:
            st.subheader("Market Weight Distribution")
            st.plotly_chart(mkt_weight_fig, width="stretch", height=400)

        st.subheader("Comparison Charts")
        st.plotly_chart(comparison_charts_fig, width="stretch")