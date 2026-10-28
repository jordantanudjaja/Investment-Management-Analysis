import pandas as pd
import streamlit as st
from src.shared.finance_utils import conditional_highlight_negative
from src.equities.valuation_models import (
    process_dcf_calculations,
    format_unlevered_fcf,
    format_wacc,
    format_pv_unlevered_fcf,
    format_enterprise_equity_value,
    format_dcf_price,
    dcf_engine
)

# Cached Function to generate the Sensitivity dataframe
@st.cache_data(ttl=3600, show_spinner=False)
def generate_sensitivity_df(wacc_range, g_range, balance_sheet_data, projected_unlevered_fcf_data, margin_of_safety, info_dict):
    matrix = []
    for wacc in wacc_range:
        row = [dcf_engine(wacc, g, balance_sheet_data, projected_unlevered_fcf_data, margin_of_safety, info_dict) for g in g_range]
        matrix.append(row)

    row_labels = [f"{wacc*100:.2f}%" for wacc in wacc_range]
    column_labels = [f"{g*100:.2f}%" for g in g_range]

    sensitivity_df = pd.DataFrame(matrix, index=row_labels, columns=column_labels)
    sensitivity_df.index.name = "Weighted Average Cost of Capital (WACC)"
    sensitivity_df.columns.name = "Perpetual Growth Rate (g)"

    # Rebuild the columns as a MultiIndex incorporating the axis name because streamlit ignores normal df.columns.name in the display
    sensitivity_df.columns = pd.MultiIndex.from_product([[sensitivity_df.columns.name], sensitivity_df.columns])

    return sensitivity_df

if st.session_state.stock_ticker_input == "":
    st.warning("Please enter the stock ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.info(
    """
    Discounted Cash Flow (DCF) is a valuation method that estimates an investment's value based on its expected future cash flows, 
    discounted back to their present value using a rate that reflects the project's or company's risk. It works best for mature companies 
    with stable, predictable cash flows.
    
    ### Best-Suited Companies
    **1) Stable Growth:** Firms with consistent, predictable revenue patterns.\n
    **2) Mature Industries:** Established utilities, consumer staples, or telecom companies.\n
    **3) Visible Capital Expenditures:** Businesses where future reinvestment needs are clear and steady.\n
    **4) Positive Free Cash Flow:** Companies that already generate reliable cash rather than burning it for growth.\n
    
    ### Poorly Suited Companies
    **1) High Growth / Startups:** Companies with negative or highly volatile current cash flows.\n
    **2) Cyclical Sectors:** Commodity or mining firms with cash flows that swing wildly with market prices.\n
    **3) Financial Institutions:** Banks and insurance companies where working capital and debt definitions differ significantly.
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

    # Storing Session State variables into local variables
    info_dict = st.session_state.stock_info_dict
    future_revenue_estimates = st.session_state.future_revenue_estimates
    y0_expected_sales_growth = future_revenue_estimates.at["0y", "growth"]
    y1_expected_sales_growth = future_revenue_estimates.at["+1y", "growth"]

    st.markdown(f"<h2 style='text-align: center;'>Expected Sales Growth (Y0): {y0_expected_sales_growth * 100:,.2f}%<br> Expected Sales Growth (Y1): {y1_expected_sales_growth * 100:,.2f}%</h2>", unsafe_allow_html=True)

    # Create 2 columns side-by-side
    col1, col2 = st.columns(2)

    with st.spinner("Loading Data ..."):
        with col1:
            # Creating the DCF Inputs Table
            st.subheader("DCF Inputs")
            dcf_input = st.data_editor(
                pd.DataFrame(
                    {
                        "Perpetual Growth Rate" : [0.025],
                        "Margin of Safety": [0.3],
                        "Projected FCF Timeframe": ["5 Years"]
                    }

                ),
                num_rows="fixed",
                hide_index=True,
                column_config={
                    "Perpetual Growth Rate": st.column_config.NumberColumn(
                        "Perpetual Growth Rate (g)",
                        format="percent",  # Displays as percentage (e.g., 5.25%)
                    ),
                    "Margin of Safety": st.column_config.NumberColumn(
                        "Margin of Safety",
                        format="percent",
                    ),
                    "Projected FCF Timeframe": st.column_config.SelectboxColumn(
                        "Projected FCF Timeframe",
                        options=["5 Years", "10 Years"],
                        required=True
                    )
                }
            )

        # Converting DCF Inputs into numerical formats to be used in calculations
        number_of_years = 5 if dcf_input.at[0, "Projected FCF Timeframe"] == "5 Years" else 10 # Assigning the number_of_years projected timeframe variable based on the DCF Input
        g = dcf_input.at[0, "Perpetual Growth Rate"]  # Assigning Perpetual Growth Rate to the variable g
        mos = dcf_input.at[0, "Margin of Safety"]           # Assigning Margin of Safety to the variable mos
        future_yearly_sales_growth = (y0_expected_sales_growth, y1_expected_sales_growth) # Assigning a Tuple to Future Estimated Revenue Growth Rates

        # Running the DCF Valuation process
        wacc_data, wacc, historical_unlevered_fcf_data, projected_unlevered_fcf_data, pv_unlevered_fcf_data, enterprise_equity_value_data, dcf_price_data = process_dcf_calculations(
            info_dict,
            income_stmt_data,
            balance_sheet_data,
            cashflow_stmt_data,
            financial_stmt_summary,
            future_yearly_sales_growth,
            number_of_years,
            g,
            mos
        )

        # Formatted Data for display
        formatted_wacc_data = format_wacc(wacc_data)
        formatted_historical_unlevered_fcf_data, formatted_projected_unlevered_fcf_data = format_unlevered_fcf(historical_unlevered_fcf_data, projected_unlevered_fcf_data)
        formatted_pv_unlevered_fcf_data = format_pv_unlevered_fcf(pv_unlevered_fcf_data)
        formatted_enterprise_equity_value_data = format_enterprise_equity_value(enterprise_equity_value_data)
        formatted_dcf_price_data = format_dcf_price(dcf_price_data)

        # Important Variables to note
        implied_share_price = dcf_price_data.at["Implied Share Price", dcf_price_data.columns[0]]
        target_buy_price = dcf_price_data.at["Target Buy Price", dcf_price_data.columns[0]]
        current_price = dcf_price_data.at["Current Price", dcf_price_data.columns[0]]
        percent_diff = abs((current_price - target_buy_price) / target_buy_price) * 100

        # Sensitivity Analysis block of code 
        wacc_range = [wacc - 2*0.02, wacc - 0.02, wacc, wacc + 0.02, wacc + 2*0.02]
        g_range = [g - 2*0.005, g - 0.005, g, g + 0.005, g + 2*0.005]
        sensitivity_df = generate_sensitivity_df(wacc_range, g_range, balance_sheet_data, projected_unlevered_fcf_data, mos, info_dict)
        formatted_sensitivity_df = sensitivity_df.style.map(conditional_highlight_negative, subset=sensitivity_df.columns, value2=current_price) # Applying conditional formatting to the dataframe

        with col2:
            # DCF Output Section
            st.subheader("DCF Output")
            if implied_share_price < 0:
                st.error("DCF analysis is not applicable.")
            elif current_price <= target_buy_price:
                st.success(f"Valuation: UNDERVALUED by {percent_diff:.2f}%")
            else:
                st.warning(f"Valuation: OVERVALUED by {percent_diff:.2f}%")

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
            # Implied Share and Target Buy Price Calculations Section
            st.subheader("Implied Share and Target Buy Price Calculations")
            st.dataframe(
                formatted_dcf_price_data,
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

        # Horizontal Line dividing certain sections
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            # Historical Unlevered Free Cash Flow Data Section
            st.subheader("Historical Unlevered Free Cash Flow Data")
            st.dataframe(
                formatted_historical_unlevered_fcf_data,
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

            # Present Value of Unlevered Free Cash Flow Data Section
            st.subheader("Present Value of Unlevered Free Cash Flow Data")
            st.dataframe(
                formatted_pv_unlevered_fcf_data,
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

        with col2:
            # Projected Unlevered Free Cash Flow Data Section
            st.subheader("Projected Unlevered Free Cash Flow Data")
            st.dataframe(
                formatted_projected_unlevered_fcf_data,
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

            # Enterprise and Equity Value Calculations
            st.subheader("Enterprise and Equity Value Calculations")
            st.dataframe(
                formatted_enterprise_equity_value_data,
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