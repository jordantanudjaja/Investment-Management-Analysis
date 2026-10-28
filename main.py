import streamlit as st

# Streamlit Page Settings
st.set_page_config(layout="wide")

if "active_section" not in st.session_state:
    st.session_state.active_section = "Macroeconomic Overview"

# Create Sidebar Clickable Section Labels
st.sidebar.title("Navigation")

# Section 1 Button
if st.sidebar.button(
    "🌍 Macroeconomic Overview", 
    width="stretch", 
    type="primary" if st.session_state.active_section == "Macroeconomic Overview" else "secondary"
):
    st.session_state.active_section = "Macroeconomic Overview"
    st.rerun()

# Section 2 Button
if st.sidebar.button(
    "📊 Equities Analysis", 
    width="stretch", 
    type="primary" if st.session_state.active_section == "Equities Analysis" else "secondary"
):
    st.session_state.active_section = "Equities Analysis"
    st.rerun()

# Section 3 Button
if st.sidebar.button(
    "🏦 Investment Funds Analysis", 
    width="stretch", 
    type="primary" if st.session_state.active_section == "Investment Funds Analysis" else "secondary"
):
    st.session_state.active_section = "Investment Funds Analysis"
    st.rerun()

# Section 4 Button
if st.sidebar.button(
    "🪙 Currencies Analysis", 
    width="stretch", 
    type="primary" if st.session_state.active_section == "Currencies Analysis" else "secondary"
):
    st.session_state.active_section = "Currencies Analysis"
    st.rerun()

# Section 5 Button
if st.sidebar.button(
    "📝 Options Analysis", 
    width="stretch", 
    type="primary" if st.session_state.active_section == "Options Analysis" else "secondary"
):
    st.session_state.active_section = "Options Analysis"
    st.rerun()

# Section 6 Button
if st.sidebar.button(
    "📈 Futures Analysis", 
    width="stretch", 
    type="primary" if st.session_state.active_section == "Futures Analysis" else "secondary"
):
    st.session_state.active_section = "Futures Analysis"
    st.rerun()

# Page Rendering depending on the active_section
if st.session_state.active_section == "Macroeconomic Overview":
    pages = [
        st.Page("views/macroeconomy/financial_markets.py", title="Financial Markets"),
        st.Page("views/macroeconomy/portfolio_management.py", title="Portfolio Management")
    ]
elif st.session_state.active_section == "Equities Analysis":
    pages = [
        st.Page("views/equities/equities_fundamental_analysis.py", title="Fundamental Analysis"),
        st.Page("views/equities/financial_statements_keywords.py", title="Financial Statements Keywords", visibility="hidden"),
        st.Page("views/equities/discounted_cash_flow.py", title="Discounted Cash Flow"),
        st.Page("views/equities/dividend_discount_model.py", title="Dividend Discount Model"),
        st.Page("views/equities/equities_technical_analysis.py", title="Technical Analysis"),
        st.Page("views/equities/equities_competitor_analysis.py", title="Competitor Analysis")
    ]
elif st.session_state.active_section == "Investment Funds Analysis":
    pages = [
        st.Page("views/funds/funds_fundamental_analysis.py", title="Fundamental Analysis"),
        st.Page("views/funds/funds_technical_analysis.py", title="Technical Analysis"),
        st.Page("views/funds/peer_analysis.py", title="Peer Analysis")
    ]
elif st.session_state.active_section == "Currencies Analysis":
    pages = [
        st.Page("views/currencies/foreign_exchange.py", title="Foreign Exchange"),
        st.Page("views/currencies/cryptocurrency.py", title="Cryptocurrency"),
        st.Page("views/currencies/forex_technical_analysis.py", title="Technical Analysis", visibility="hidden"),
        st.Page("views/currencies/crypto_technical_analysis.py", title="Technical Analysis", visibility="hidden"),
        st.Page("views/currencies/relative_currency_strength_analysis.py", title="Relative Currency Strength Analysis", visibility="hidden"),
        st.Page("views/currencies/comparative_tokenomics_analysis.py", title="Comparative Tokenomics Analysis", visibility="hidden")
    ]
elif st.session_state.active_section == "Options Analysis":
    pages = [
        st.Page("views/options/option_profile.py", title="Option Profile"),
        st.Page("views/options/option_greeks.py", title="Option Greeks"),
        st.Page("views/options/strategy_simulator.py", title="Strategy Simulator")
    ]
elif st.session_state.active_section == "Futures Analysis":
    pages = [
        st.Page("views/futures/commodity_futures.py", title="Commodity Futures"),
        st.Page("views/futures/commodities_technical_analysis.py", title="Technical Analysis"),
        st.Page("views/futures/commodities_cma.py", title="Comparative Market Analysis")
    ]

nav = st.navigation(pages, position="top")

nav.run()