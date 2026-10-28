import numpy as np
import pandas as pd
import streamlit as st
from src.shared.finance_utils import conditional_highlight_negative
from src.equities.valuation_models import (
    format_dividend_data,
    format_wacc,
    format_ddm_price,
    process_ddm_calculations,
    ddm_engine
)

# Cached Function to generate the Sensitivity dataframe
@st.cache_data(ttl=3600, show_spinner=False)
def generate_sensitivity_df(wacc_range, g_range, dividend_data, margin_of_safety, info_dict):
    matrix = []
    for wacc in wacc_range:
        row = [ddm_engine(wacc, g, dividend_data, margin_of_safety, info_dict) for g in g_range]
        matrix.append(row)

    row_labels = [f"{wacc*100:.2f}%" for wacc in wacc_range]
    column_labels = [f"{g*100:.2f}%" for g in g_range]

    sensitivity_df = pd.DataFrame(matrix, index=row_labels, columns=column_labels)
    sensitivity_df.index.name = "Weighted Average Cost of Capital (WACC)"
    sensitivity_df.columns.name = "Average Dividend Growth (g)"

    # Rebuild the columns as a MultiIndex incorporating the axis name because streamlit ignores normal df.columns.name in the display
    sensitivity_df.columns = pd.MultiIndex.from_product([[sensitivity_df.columns.name], sensitivity_df.columns])
   
    return sensitivity_df

if st.session_state.stock_ticker_input == "":
    st.warning("Please enter the stock ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.info(
    """
    Dividend Discount Model (DDM) is a valuation method that estimates an investment's value based on its expected future dividends, 
    discounted back to their present value using a rate that reflects the project's or company's risk. It works best for mature companies 
    that pay reliable dividend payouts. This specific analysis uses the Gordon Growth Variation, which assumes that the company grows its 
    dividends at the exact same steady rate forever.
    
    ### Best-Suited Companies\n
    **1) Steady Earnings:** Firms with long histories of making stable profits.\n
    **2) Slow Growth:** Mature businesses that do not need to reinvest all cash to expand.\n
    **3) High Payouts:** Firms that regularly return a large share of cash to owners.\n
    **4) Common Sectors:** Utilities, big banks, and old-line consumer goods makers.\n
    
    ### Poorly Suited Companies\n
    **1) No Dividend Payouts:** Firms that pay zero cash to owners (many tech startups).\n
    **2) Low Yield and Fast Growth:** Businesses that keep all cash to build new plants or fund research like the tech giants.\n
    **3) Wild Swings:** Firms with earnings that jump up and down a lot each year.\n
    **4) High Debt:** Companies in financial trouble that might cut their cash rewards at any time.
    """
)

st.markdown(f"<h1 style='text-align: center;'>Stock Ticker: {st.session_state.stock_ticker_input}</h1>", unsafe_allow_html=True)

if st.session_state.stock_ticker_input_error:
    st.error("Stock Ticker that was inputted does not exist. Please re-enter another ticker first before viewing this page.")
else:
    # Re-ordering the date columns to go from oldest year to most recent year and storing them in local data variables
    income_stmt_data = st.session_state.income_stmt_data.iloc[:, ::-1]
    balance_sheet_data = st.session_state.balance_sheet_data.iloc[:, ::-1]
    cashflow_stmt_data = st.session_state.cashflow_stmt_data.iloc[:, ::-1]
    financial_stmt_summary = st.session_state.financial_stmt_summary.iloc[:, ::-1]
    financial_perf_data = st.session_state.financial_perf_data.iloc[:, ::-1]

    # Storing Session State variable into local variable
    info_dict = st.session_state.stock_info_dict

    # Create 2 columns side-by-side
    col1, col2 = st.columns(2)

    with st.spinner("Loading Data ..."):
        with col1:
            # Creating the DDM Input Table
            st.subheader("DDM Input")
            ddm_input = st.data_editor(
                pd.DataFrame(
                    {"Margin of Safety": [0.3]}
                ),
                num_rows="fixed",
                hide_index=True,
                column_config={
                    "Margin of Safety": st.column_config.NumberColumn(
                        "Margin of Safety",
                        format="percent", # Displays as percentage (e.g., 5.25%)
                    )
                }
            )

        # Assigning Margin of Safety to the variable mos
        mos = ddm_input.at[0, "Margin of Safety"]

        # Running the DDM Valuation process
        wacc_data, wacc, dividend_data, g, ddm_price_data = process_ddm_calculations(
            info_dict,
            income_stmt_data,
            balance_sheet_data,
            cashflow_stmt_data,
            financial_stmt_summary,
            financial_perf_data,
            mos
        )

        # Formatted Data for display
        formatted_dividend_data = format_dividend_data(dividend_data)
        formatted_wacc_data = format_wacc(wacc_data)
        formatted_ddm_price_data = format_ddm_price(ddm_price_data)

        # Important Variables to note
        implied_share_price = ddm_price_data.at["Implied Share Price", ddm_price_data.columns[0]]
        target_buy_price = ddm_price_data.at["Target Buy Price", ddm_price_data.columns[0]]
        current_price = ddm_price_data.at["Current Price", ddm_price_data.columns[0]]
        percent_diff = abs((current_price - target_buy_price) / target_buy_price) * 100

        # Sensitivity Analysis block of code 
        wacc_range = [wacc - 2*0.02, wacc - 0.02, wacc, wacc + 0.02, wacc + 2*0.02]
        g_range = [g - 2*0.005, g - 0.005, g, g + 0.005, g + 2*0.005]
        sensitivity_df = generate_sensitivity_df(wacc_range, g_range, dividend_data, mos, info_dict)
        formatted_sensitivity_df = sensitivity_df.style.map(conditional_highlight_negative, subset=sensitivity_df.columns, value2=current_price) # Applying conditional formatting to the dataframe

        with col2:
            # DDM Output Section
            st.subheader("DDM Output")
            if current_price <= target_buy_price:
                st.success(f"Valuation: UNDERVALUED by {percent_diff:.2f}%")
            elif current_price > target_buy_price:
                st.warning(f"Valuation: OVERVALUED by {percent_diff:.2f}%")
            else:
                if wacc < g:
                    st.error("DDM analysis is not applicable. The required rate of return (using WACC) is less than the average dividend growth rate (g), resulting in a negative implied share price value.")
                else:
                    st.error("DDM analysis is not applicable.")

        # Horizontal Line dividing certain sections
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            # Weighted Average Cost of Capital Calculations Section
            st.subheader("Weighted Average Cost of Capital Calculations")
            st.write(f"**Weighted Average Cost of Capital (WACC):** {wacc*100:.2f}%")
            st.dataframe(
                formatted_wacc_data,
                hide_index=True,
                width='stretch',
                height='stretch',
                column_config={
                    # Key change: Use TextColumn with markdown formatting enabled
                    "Metric": st.column_config.MarkdownColumn(
                        label="", 
                        width="medium"
                    )
                }
            )

        with col2:
            try:
                # Implied Share and Target Buy Price Calculations Section
                st.subheader("Implied Share and Target Buy Price Calculations")
                st.dataframe(
                    formatted_ddm_price_data,
                    hide_index=True,
                    width='stretch',
                    column_config={
                        # Key change: Use TextColumn with markdown formatting enabled
                        "index": st.column_config.MarkdownColumn(
                            label="", 
                            width="medium"
                        )
                    }
                )

                # Sensitivity Analysis Section
                st.subheader("Sensitivity Analysis (Target Buy Price)")
                st.dataframe(formatted_sensitivity_df, width="stretch")

            except:
                st.error("No calculations because the DDM returns an error")

        # Horizontal Line dividing certain sections
        st.divider()

        # Dividend Calculations Section
        st.subheader("Dividend Calculations")
        st.write(f"**Average Dividend Growth**: {g * 100:.2f}%" if g is not np.nan else "No Dividends")
        st.dataframe(
            formatted_dividend_data,
            hide_index=True,
            width='stretch',
            column_config={
                # Key change: Use TextColumn with markdown formatting enabled
                "index": st.column_config.MarkdownColumn(
                    label="", 
                    width="medium"
                )
            }
        )