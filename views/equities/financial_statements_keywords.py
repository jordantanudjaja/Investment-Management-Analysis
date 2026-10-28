import streamlit as st

# Function to compare the required keywords from each financial statements and the actual wording in each financial statement index
def check_subset_set(list_keywords, list_statement_index):
    """
    This function is important because it acts as a check on updates to the yfinance API and whether the update changed the
    wording of any of the line items in each financial statement.
    """
    set_keywords = set(list_keywords)
    set_statement_index = set(list_statement_index)

    # Check if set_keywords is a subset of set_statement_index
    is_subset = set_keywords.issubset(set_statement_index)
    missing_elements = list(set_keywords - set_statement_index) # If it is a subset, this will automatically be an empty list

    return is_subset, missing_elements

st.info(
    """
    This page shows the required keywords from the 3 financial statements that are important to the fundamental analysis of the stock.
    yfinance API sometimes has an update and makes changes to the wordings on the index of the financial statements, which may not be
    captured by the parsing functions.
    
    However, even if not all required keywords are present, it does not mean that the parsing was
    unsuccessful. Sometimes, there really is no value in that keyword for that stock (e.g: Preferred Stock, Minority Interest, Cash
    Dividends Paid etc).

    It is important to note that as long as the main required keywords such as Revenue, Net Income, Current Assets, Current Liabilities,
    Operating Cash Flow, Free Cash Flow etc are present, then the parsing is considered successful.
    """
)

if st.button("Back to Financial Statements Analysis",  icon="⬅️"):
    st.switch_page("views/equities/equities_fundamental_analysis.py")

# Create 3 columns side-by-side
col1, col2, col3 = st.columns(3)

with col1:
    if "income_stmt" not in st.session_state:
        st.session_state.income_stmt = ""
    else:
        st.subheader("Income Statement")

        income_stmt_index = sorted(st.session_state.income_stmt.index.to_list())
        income_stmt_keywords = sorted(st.session_state.income_stmt_keywords)

        # Comparing the keywords with the financial statement index
        income_stmt_subset_status, income_stmt_missing_elements = check_subset_set(income_stmt_keywords, income_stmt_index)

        if income_stmt_subset_status == True:
            st.success("All required keywords are present")
        else:
            st.error("Not all required keywords are present")
            st.markdown("<h5>Missing Keywords</h5>", unsafe_allow_html=True)
            st.table(income_stmt_missing_elements)

with col2:
    if "balance_sheet" not in st.session_state:
        st.session_state.balance_sheet = ""
    else:
        st.subheader("Balance Sheet")

        balance_sheet_index = sorted(st.session_state.balance_sheet.index.to_list())
        balance_sheet_keywords = sorted(st.session_state.balance_sheet_keywords)

        # Comparing the keywords with the financial statement index
        balance_sheet_subset_status, balance_sheet_missing_elements = check_subset_set(balance_sheet_keywords, balance_sheet_index)

        if balance_sheet_subset_status == True:
            st.success("All required keywords are present")
        else:
            st.error("Not all required keywords are present")
            st.markdown("<h5>Missing Keywords</h5>", unsafe_allow_html=True)
            st.table(balance_sheet_missing_elements)

with col3:
    if "cashflow_stmt" not in st.session_state:
        st.session_state.cashflow_stmt = ""
    else:
        st.subheader("Cash Flow Statement")
    
        cashflow_stmt_index = sorted(st.session_state.cashflow_stmt.index.to_list())
        cashflow_stmt_keywords = sorted(st.session_state.cashflow_stmt_keywords)

        # Comparing the keywords with the financial statement index
        cashflow_stmt_subset_status, cashflow_stmt_missing_elements = check_subset_set(cashflow_stmt_keywords, cashflow_stmt_index)

        if cashflow_stmt_subset_status == True:
            st.success("All required keywords are present")
        else:
            st.error("Not all required keywords are present")
            st.markdown("<h5>Missing Keywords</h5>", unsafe_allow_html=True)
            st.table(cashflow_stmt_missing_elements)

# Horizontal line dividing certain sections
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<h5>Keywords Required</h5>", unsafe_allow_html=True)
        st.table(income_stmt_keywords)
    with col_b:
        st.markdown("<h5>Statement Index</h5>", unsafe_allow_html=True)
        st.table(income_stmt_index)

with col2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<h5>Keywords Required</h5>", unsafe_allow_html=True)
        st.table(balance_sheet_keywords)
    with col_b:
        st.markdown("<h5>Statement Index</h5>", unsafe_allow_html=True)
        st.table(balance_sheet_index)

with col3:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<h5>Keywords Required</h5>", unsafe_allow_html=True)
        st.table(cashflow_stmt_keywords)
    with col_b:
        st.markdown("<h5>Statement Index</h5>", unsafe_allow_html=True)
        st.table(cashflow_stmt_index) 