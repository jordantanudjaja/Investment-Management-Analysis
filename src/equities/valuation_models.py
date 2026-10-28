import numpy as np
import pandas as pd
import streamlit as st
from src.shared.finance_utils import (
    format_date_columns,
    format_row,
    format_financial_statement,
    highlight_exact_cells,
    conditional_highlight_negative,
    conditional_highlight_positive
)
from src.shared.macroeconomic_metrics import get_expected_market_return, get_treasury_yield
from src.equities.fundamental_analysis import safe_add, safe_subtract

# Function to create Unlevered Free Cash Flow (FCFF) dataframes (Historical and Projected) for DCF calculations
def get_unlevered_fcf(income_stmt_data, cashflow_stmt_data, financial_stmt_summary, future_yearly_sales_growth, timeframe_years):
    # Building the Current Unlevered Free Cash Flow Data using Income Statement, Cash Flow Statement, and the Financial Summary Statement from the statement_summary function
    historical_unlevered_fcf_data = pd.concat([
        income_stmt_data.loc[[
            "Revenue",
            "Revenue Growth",
            "Depreciation And Amortization (D&A)",
            "D&A % of Sales",
            "Operating Earnings (EBIT)",
            "EBIT Margin",
            "Effective Tax Rate",
            "Net Operating Profit After Tax (NOPAT)"
        ]],
        cashflow_stmt_data.loc[[
            "Capital Expenditures on Fixed Assets (PPE)",
            "Change In Working Capital"
        ]],
        financial_stmt_summary.loc[[
            "CapEx on Fixed Assets (PPE) % of Sales",
            "Change In Working Capital % of Sales",
            "Free Cash Flow to Firm (FCFF)" # FCFF is equivalent to Unlevered FCF
        ]]
    ])

    # Getting Revenue Growth Estimates for Y0 and Y1 (next 2 years of data)
    revenue_growth_0y = future_yearly_sales_growth[0]
    revenue_growth_1y = future_yearly_sales_growth[1]

    # Projected Margin Calculations for 5-10 Years into the future
    DA_margin_projection = np.mean(historical_unlevered_fcf_data.loc["D&A % of Sales"])
    EBIT_margin_projection = np.mean(historical_unlevered_fcf_data.loc["EBIT Margin"])
    tax_rate_projection = np.mean(historical_unlevered_fcf_data.loc["Effective Tax Rate"])
    CapEx_margin_projection = np.mean(historical_unlevered_fcf_data.loc["CapEx on Fixed Assets (PPE) % of Sales"])
    Change_In_Working_Capital_margin_projection = np.mean(historical_unlevered_fcf_data.loc["Change In Working Capital % of Sales"])
    # Projection for Revenue Growth from Y+2 onwards
    revenue_growth_projection = min(revenue_growth_0y, revenue_growth_1y)

    start_date = historical_unlevered_fcf_data.columns[-1]
    start_revenue = historical_unlevered_fcf_data.at["Revenue", start_date]

    # Building the dataframe for projected unlevered free cash flow data
    data = {}
    for i in range(timeframe_years):
        column_name = start_date + pd.DateOffset(years=i+1)
        if i == 0:
            revenue = start_revenue * (1 + revenue_growth_0y)
            revenue_growth = revenue_growth_0y
        elif i == 1:
            revenue = start_revenue * (1 + revenue_growth_1y)
            revenue_growth = revenue_growth_1y
        else:
            revenue = start_revenue * (1 + revenue_growth_projection)
            revenue_growth = revenue_growth_projection

        # Updating start_revenue to the latest new value in the latest year
        start_revenue = revenue

        depreciation_and_amortization = revenue * DA_margin_projection
        depreciation_and_amortization_margin = DA_margin_projection
        ebit = revenue * EBIT_margin_projection
        ebit_margin = EBIT_margin_projection
        effective_tax_rate = tax_rate_projection
        nopat = ebit * (1 - effective_tax_rate)
        capex = revenue * CapEx_margin_projection
        capex_margin = CapEx_margin_projection
        change_in_working_capital = revenue * Change_In_Working_Capital_margin_projection
        change_in_working_capital_margin = Change_In_Working_Capital_margin_projection
        unlevered_fcf = nopat + depreciation_and_amortization + capex - change_in_working_capital # capex is negative value, so + capex means subtracting capex expenditure

        data[column_name] = {
            "Revenue": revenue,
            "Revenue Growth": revenue_growth,
            "Depreciation And Amortization (D&A)": depreciation_and_amortization,
            "D&A % of Sales": depreciation_and_amortization_margin,
            "Operating Earnings (EBIT)": ebit,
            "EBIT Margin": ebit_margin,
            "Effective Tax Rate": effective_tax_rate,
            "Net Operating Profit After Tax (NOPAT)": nopat,
            "Capital Expenditures on Fixed Assets (PPE)": capex,
            "CapEx on Fixed Assets (PPE) % of Sales": capex_margin,
            "Change In Working Capital": change_in_working_capital,
            "Change In Working Capital % of Sales": change_in_working_capital_margin,
            "Free Cash Flow to Firm (FCFF)": unlevered_fcf
        }

    projected_unlevered_fcf_data = pd.DataFrame(data)

    return historical_unlevered_fcf_data, projected_unlevered_fcf_data

# Function to format the newly created unlevered free cash flow dataframes (historical and projected)
def format_unlevered_fcf(historical_unlevered_fcf_data, projected_unlevered_fcf_data):
    # Formatting both the Historical and Projected Unlevered FCF Data
    percentage_rows = [
        "Revenue Growth",
        "D&A % of Sales",
        "EBIT Margin",
        "Effective Tax Rate",
        "CapEx on Fixed Assets (PPE) % of Sales",
        "Change In Working Capital % of Sales"
    ]

    formatted_historical_unlevered_fcf_data = historical_unlevered_fcf_data.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows
    )

    formatted_projected_unlevered_fcf_data = projected_unlevered_fcf_data.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows
    )

    statement_structure = {
        "Income Statement Data": [ #0
            "Revenue", #1
            "Revenue Growth", #2
            "Depreciation And Amortization (D&A)", #3
            "D&A % of Sales", #4
            "Operating Earnings (EBIT)", #5
            "EBIT Margin", #6
            "Effective Tax Rate", #7
            "Net Operating Profit After Tax (NOPAT)" #8
        ],
        "Cash Flow Statement Data": [ #9
            "Capital Expenditures on Fixed Assets (PPE)", #10
            "CapEx on Fixed Assets (PPE) % of Sales", #11
            "Change In Working Capital", #12
            "Change In Working Capital % of Sales", #13
            "Free Cash Flow to Firm (FCFF)" #14
        ]
    }

    formatted_historical_unlevered_fcf_data = format_financial_statement(
        formatted_historical_unlevered_fcf_data,
        statement_structure,
        formatted_historical_unlevered_fcf_data.columns
    )

    formatted_projected_unlevered_fcf_data = format_financial_statement(
        formatted_projected_unlevered_fcf_data,
        statement_structure,
        formatted_projected_unlevered_fcf_data.columns
    )

    # Styling the EBIT, NOPAT, and FCFF rows
    formatted_historical_unlevered_fcf_data = formatted_historical_unlevered_fcf_data.style.apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([2, 5, 8, 12, 14], slice(None)) # Revenue Growth, EBIT, NOPAT, Change in Working Capital and FCFF
    )

    formatted_projected_unlevered_fcf_data = formatted_projected_unlevered_fcf_data.style.apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([2, 5, 8, 12, 14], slice(None)) # Revenue Growth, EBIT, NOPAT, Change in Working Capital and FCFF
    )

    return formatted_historical_unlevered_fcf_data, formatted_projected_unlevered_fcf_data

# Function to calculate Weighted Average Cost of Capital (WACC) for DCF calculations
def get_wacc(info, income_stmt_data, balance_sheet_data, financial_stmt_summary):
    # Creating the series object using the latest year of data
    wacc_data = pd.concat([
        income_stmt_data.loc[[
            "Non-Operating Interest Expense",
            "Effective Tax Rate",
            "Preferred Dividends"
        ], income_stmt_data.columns[-1]],
        balance_sheet_data.loc[[
            "Current Debt",
            "Long-Term Debt",
            "Preferred Stock"
        ], balance_sheet_data.columns[-1]],
        financial_stmt_summary.loc[[
            "Total Debt"
        ], financial_stmt_summary.columns[-1]]
    ])

    # Renaming the Series Labels and Name (which eventually will become the Column name when converted into a dataframe)
    wacc_data = wacc_data.rename({
        "Non-Operating Interest Expense": "Latest Interest Expense",
        "Effective Tax Rate": "Latest Effective Tax Rate",
        "Preferred Dividends": "Latest Preferred Dividends",
        "Current Debt": "Latest Current Debt",
        "Long-Term Debt": "Latest Long-Term Debt",
        "Preferred Stock": "Latest Preferred Stock",
        "Total Debt": "Latest Total Debt"
    }).rename("Value")

    wacc_data.loc["Beta"] = info.get("beta", np.nan)
    wacc_data.loc["Market Capitalization"] = info.get("marketCap", np.nan)
    wacc_data.loc["Risk-Free Rate"] = get_treasury_yield()["Value"] # Using the 10-year Treasury Note Yield as the reference
    wacc_data.loc["Expected Return of the Market"] = get_expected_market_return()["Value"]

    wacc_data.loc["Cost of Debt"] = wacc_data.loc["Latest Interest Expense"] / wacc_data.loc["Latest Total Debt"] if wacc_data.loc["Latest Total Debt"] > 0 else 0
    wacc_data.loc["Cost of Common Equity"] = safe_add(
        wacc_data.loc["Risk-Free Rate"],
        wacc_data.loc["Beta"] * safe_subtract(
            wacc_data.loc["Expected Return of the Market"],
            wacc_data.loc["Risk-Free Rate"]
        )
    )
    # Cost of Preferred Stock is currently calculated using the book value (Preferred Stock from Balance Sheet) but it's better to use
    # the current market price of the Preferred Stock, but that is hard to get from the yfinance API
    wacc_data.loc["Cost of Preferred Stock"] = wacc_data.loc["Latest Preferred Dividends"] / wacc_data.loc["Latest Preferred Stock"] if wacc_data.loc["Latest Preferred Stock"] > 0 else 0 

    wacc_data.loc["Weight of Debt"] = wacc_data.loc["Latest Total Debt"] / safe_add(wacc_data.loc["Latest Total Debt"], wacc_data.loc["Market Capitalization"], wacc_data.loc["Latest Preferred Stock"])
    wacc_data.loc["Weight of Common Equity"] = wacc_data.loc["Market Capitalization"] / safe_add(wacc_data.loc["Latest Total Debt"], wacc_data.loc["Market Capitalization"], wacc_data.loc["Latest Preferred Stock"])
    wacc_data.loc["Weight of Preferred Stock"] = wacc_data.loc["Latest Preferred Stock"] / safe_add(wacc_data.loc["Latest Total Debt"], wacc_data.loc["Market Capitalization"], wacc_data.loc["Latest Preferred Stock"])

    wacc_data.loc["Weighted Average Cost of Capital (WACC)"] = safe_add(
        wacc_data.loc["Weight of Debt"] * wacc_data.loc["Cost of Debt"] * (1 - wacc_data.loc["Latest Effective Tax Rate"]),
        wacc_data.loc["Weight of Common Equity"] * wacc_data.loc["Cost of Common Equity"],
        wacc_data.loc["Weight of Preferred Stock"] * wacc_data.loc["Cost of Preferred Stock"]
    )

    # Converting the Series wacc_data to a DataFrame object instead so function format_row can be applied
    wacc_data = wacc_data.to_frame()
    wacc = wacc_data.at["Weighted Average Cost of Capital (WACC)", wacc_data.columns[0]]

    return wacc_data, wacc

# Function to format the newly created WACC Calculation Dataframe
def format_wacc(wacc_data):
    percentage_rows = [
        "Latest Effective Tax Rate",
        "Risk-Free Rate",
        "Expected Return of the Market",
        "Cost of Debt",
        "Cost of Common Equity",
        "Cost of Preferred Stock",
        "Weight of Debt",
        "Weight of Common Equity",
        "Weight of Preferred Stock",
        "Weighted Average Cost of Capital (WACC)"
    ]

    ratio_rows = ["Beta"]

    formatted_wacc_data = wacc_data.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows,
        ratio_rows=ratio_rows
    )

    statement_structure = {
        "Debt Portion": [
            "Latest Interest Expense",
            "Latest Current Debt",
            "Latest Long-Term Debt",
            "Latest Total Debt",
            "Latest Effective Tax Rate",
            "Cost of Debt",
            "Weight of Debt"
        ],
        "Common Equity Portion": [
            "Beta",
            "Market Capitalization",
            "Risk-Free Rate",
            "Expected Return of the Market",
            "Cost of Common Equity",
            "Weight of Common Equity"
        ],
        "Preferred Stock Portion": [
            "Latest Preferred Dividends",
            "Latest Preferred Stock",
            "Cost of Preferred Stock",
            "Weight of Preferred Stock"
        ],
        "WACC Calculation": [
            "Weighted Average Cost of Capital (WACC)"
        ]
    }

    formatted_wacc_data = format_financial_statement(
        formatted_wacc_data,
        statement_structure,
        formatted_wacc_data.columns
    )

    # Highlighting the Beta, Risk-Free Rate, and Expected Return of the Market Cells
    formatted_wacc_data = formatted_wacc_data.style.apply(
        highlight_exact_cells,
        axis=1,
        target_cells=[
            (9,1),  # Beta
            (11,1), # Risk-Free Rate
            (12,1)  # Expected Return of the Market
        ],
        background_color="#40E0D0"
    )

    return formatted_wacc_data

# Function to create the Present Value of Future Unlevered Free Cash Flow dataframe
def get_pv_unlevered_fcf(projected_unlevered_fcf_data, wacc, perpetual_growth_rate):
    # Creating the dataframe by joining the historical and projected Unlevered FCF dataframes horizontally
    pv_unlevered_fcf_data = projected_unlevered_fcf_data.loc[["Free Cash Flow to Firm (FCFF)"]].rename(index={"Free Cash Flow to Firm (FCFF)": "Unlevered Free Cash Flow"})
    # Using the mid-year convention to approximate cash flows spread evently throughout the year
    pv_unlevered_fcf_data.loc["Discount Factor"] = [1 / (1 + wacc)**(i + 0.5) for i in range(len(pv_unlevered_fcf_data.columns))]
    pv_unlevered_fcf_data.loc["Present Value (PV)"] = pv_unlevered_fcf_data.loc["Discount Factor"] * pv_unlevered_fcf_data.loc["Unlevered Free Cash Flow"]

    # Formatting the date columns to be easier to read
    pv_unlevered_fcf_data = format_date_columns(pv_unlevered_fcf_data)

    latest_fcf_projection = pv_unlevered_fcf_data.at["Unlevered Free Cash Flow", pv_unlevered_fcf_data.columns[-1]]
    latest_discount_factor = pv_unlevered_fcf_data.at["Discount Factor", pv_unlevered_fcf_data.columns[-1]]
    terminal_value_fcf = latest_fcf_projection * (1 + perpetual_growth_rate) / (wacc - perpetual_growth_rate)

    # Adding the Terminal Value as a new column to the dataframe
    pv_unlevered_fcf_data["Terminal Value"] = {
        "Unlevered Free Cash Flow": terminal_value_fcf,
        "Discount Factor": latest_discount_factor,
        "Present Value (PV)": latest_discount_factor * terminal_value_fcf
    }

    return pv_unlevered_fcf_data

# Function to format the newly created Present Value Unlevered FCF Dataframe
def format_pv_unlevered_fcf(pv_unlevered_fcf_data):
    ratio_rows = ["Discount Factor"]

    formatted_pv_unlevered_fcf_data = pv_unlevered_fcf_data.apply(
        format_row,
        axis=1,
        ratio_rows=ratio_rows
    ).reset_index()

    return formatted_pv_unlevered_fcf_data

# Function to create the Enterprise and Equity Value dataframe for DCF calculations
def get_enterprise_equity_value(pv_unlevered_fcf_data, balance_sheet_data):
    enterprise_value = pv_unlevered_fcf_data.loc["Present Value (PV)"].sum()
    latest_cash_and_cash_equivalents = balance_sheet_data.at["Cash And Cash Equivalents", balance_sheet_data.columns[-1]]
    latest_total_debt = safe_add(
        balance_sheet_data.at["Current Debt", balance_sheet_data.columns[-1]],
        balance_sheet_data.at["Long-Term Debt", balance_sheet_data.columns[-1]]
    )
    latest_preferred_stock = balance_sheet_data.at["Preferred Stock", balance_sheet_data.columns[-1]]
    latest_minority_interest = balance_sheet_data.at["Minority Interest", balance_sheet_data.columns[-1]]
    equity_value = safe_subtract(
        safe_add(
            enterprise_value,
            latest_cash_and_cash_equivalents
        ),
        latest_total_debt,
        latest_preferred_stock,
        latest_minority_interest
    )

    # Creating the dataframe
    enterprise_equity_value_data = pd.DataFrame({
        "Value": {
            "Enterprise Value": enterprise_value,
            "Latest Cash And Cash Equivalents": latest_cash_and_cash_equivalents,
            "Latest Total Debt": latest_total_debt,
            "Latest Preferred Stock": latest_preferred_stock,
            "Latest Minority Interest": latest_minority_interest,
            "Equity Value": equity_value
        }
    })

    return enterprise_equity_value_data

# Function to format the newly created Enterprise Equity Value Dataframe
def format_enterprise_equity_value(enterprise_equity_value_data):
    formatted_enterprise_equity_value_data = enterprise_equity_value_data.apply(
            format_row,
            axis=1
        ).reset_index()
    
    return formatted_enterprise_equity_value_data

# Function to create the Implied Share Price and Target Buy Price dataframe for DCF calculations
def get_dcf_price(margin_of_safety, shares_outstanding, equity_value, current_price):
    implied_share_price = equity_value / shares_outstanding if shares_outstanding > 0 else "N/A"
    target_buy_price =  (1 - margin_of_safety) * implied_share_price

    # Creating the dataframe
    dcf_price_data = pd.DataFrame({
        "Value": {
            "Current Number of Outstanding Shares": shares_outstanding,
            "Implied Share Price": implied_share_price,
            "Target Buy Price": target_buy_price,
            "Current Price": current_price
        }
    })

    return dcf_price_data

# Function to format the newly created DCF Implied Share Price and Target Buy Price dataframe
def format_dcf_price(dcf_price_data):
    pershare_rows = ["Implied Share Price", "Target Buy Price", "Current Price"]
    quantity_rows = ["Current Number of Outstanding Shares"]

    formatted_dcf_price_data = dcf_price_data.apply(
        format_row,
        axis=1,
        pershare_rows=pershare_rows,
        quantity_rows=quantity_rows
    ).reset_index()

    # Highlighting the Target Buy Price Cell, which is in coordinates (2,1)
    formatted_dcf_price_data = formatted_dcf_price_data.style.apply(
        highlight_exact_cells,
        axis=1,
        target_cells=[(2,1)]
    )
    
    return formatted_dcf_price_data

# Cached Function to calculate the DCF valuation
@st.cache_data(ttl=3600, show_spinner=False)
def process_dcf_calculations(info_dict, income_stmt_data, balance_sheet_data, cashflow_stmt_data, financial_stmt_summary, future_yearly_sales_growth, timeframe_years, perpetual_growth_rate, margin_of_safety):
    # 1. Get the Weighted Average Cost of Capital (WACC)
    wacc_data, wacc = get_wacc(
        info_dict,
        income_stmt_data,
        balance_sheet_data,
        financial_stmt_summary
    )

    # 2. Get the Historical and Projected Unlevered Free Cash Flow Data
    historical_unlevered_fcf_data, projected_unlevered_fcf_data = get_unlevered_fcf(
        income_stmt_data,
        cashflow_stmt_data,
        financial_stmt_summary,
        future_yearly_sales_growth,
        timeframe_years
    )

    # 3. Get Present Value of the Unlevered Free Cash Flow Data by discounting the Projected Cash Flows with the WACC
    pv_unlevered_fcf_data = get_pv_unlevered_fcf(
        projected_unlevered_fcf_data,
        wacc,
        perpetual_growth_rate
    )

    # 4. Get the Enterprise and Equity Value Data
    enterprise_equity_value_data = get_enterprise_equity_value(
        pv_unlevered_fcf_data,
        balance_sheet_data
    )

    # Get the DCF price data, which includes Implied Share Price, and the Target Buy Price after accounting for Margin of Safety
    dcf_price_data = get_dcf_price(
        margin_of_safety,
        info_dict.get("sharesOutstanding", "N/A"),
        enterprise_equity_value_data.at["Equity Value", enterprise_equity_value_data.columns[0]],
        info_dict.get("currentPrice", "N/A")
    )

    return wacc_data, wacc, historical_unlevered_fcf_data, projected_unlevered_fcf_data, pv_unlevered_fcf_data, enterprise_equity_value_data, dcf_price_data

# Cached Function that calculates the DCF engine for Sensitivity Analysis based on the inputs
@st.cache_data(ttl=3600, show_spinner=False)
def dcf_engine(wacc, g, balance_sheet_data, projected_unlevered_fcf_data, margin_of_safety, info_dict):
    if wacc < g:
        return np.nan # Avoid mathematical errors

    pv_unlevered_fcf_data = get_pv_unlevered_fcf(
        projected_unlevered_fcf_data,
        wacc,
        g
    )

    enterprise_equity_value_data = get_enterprise_equity_value(
        pv_unlevered_fcf_data,
        balance_sheet_data
    )

    dcf_price_data = get_dcf_price(
        margin_of_safety,
        info_dict.get("sharesOutstanding", "N/A"),
        enterprise_equity_value_data.at["Equity Value", enterprise_equity_value_data.columns[0]],
        info_dict.get("currentPrice", "N/A")
    )

    target_buy_price = dcf_price_data.at["Target Buy Price", dcf_price_data.columns[0]]

    return f"${target_buy_price:.2f}"

# Function to create annual dividends dataframe for Dividend Discount Model
def get_dividend_data(income_stmt_data, cashflow_stmt_data, financial_perf_data): 
    dividend_data = pd.concat([
        cashflow_stmt_data.loc[[
            "Total Cash Dividends Paid"
        ]],
        income_stmt_data.loc[[
            "Net Income",
            "Net Income Growth"
        ]],
        financial_perf_data.loc[[
            "Annual Dividends Per Share",
            "Dividend Growth",
            "Dividend Payout"
        ]]
    ])

    # Formatting the date columns to be easier to read
    dividend_data = format_date_columns(dividend_data)
    average_dividend_growth = np.mean(dividend_data.loc["Dividend Growth"])

    return dividend_data, average_dividend_growth

# Function to format the newly created annual dividends dataframe
def format_dividend_data(dividend_data):
    percentage_rows = ["Net Income Growth", "Dividend Payout", "Dividend Growth"]
    pershare_rows = ["Annual Dividends Per Share"]

    formatted_dividend_data = dividend_data.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows,
        pershare_rows=pershare_rows
    ).reset_index()

    # Styling the Net Income and Dividend Payout rows (If Dividend Payout < 70%, it is a positive sign)
    formatted_dividend_data = formatted_dividend_data.style.apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([1], slice(None)) # Net Income is in index value 1
    ).apply(
        lambda row: [conditional_highlight_positive(val, 70) for val in row],
        axis=1,
        subset=([5], slice(None)) # Dividend Payout is in index value 5
    )

    return formatted_dividend_data
    
# Function to create the Implied Share Price and Target Buy Price dataframe for DDM calculations
def get_ddm_price(margin_of_safety, latest_annual_dividend_pershare, average_dividend_growth, wacc, current_price):
    """
    The DDM model here uses the Gordon Growth Variation which assumes that the company grows its dividends
    at the exact same steady rate forever.
    """
    try:
        next_year_dividend_pershare = latest_annual_dividend_pershare * (1 + average_dividend_growth)
        implied_share_price = next_year_dividend_pershare / (wacc - average_dividend_growth) if (wacc - average_dividend_growth) > 0 else np.nan
        target_buy_price =  (1 - margin_of_safety) * implied_share_price
    except:
        ddm_price_data = {}
    else:
        # Creating the dataframe
        ddm_price_data = pd.DataFrame({
            "Value": {
                "Y1 Expected Annual Dividends Per Share": next_year_dividend_pershare,
                "Implied Share Price": implied_share_price,
                "Target Buy Price": target_buy_price,
                "Current Price": current_price
            }
        })
    
    return ddm_price_data

# Function to format the newly created DDM Implied Share Price and Target Buy Price dataframe
def format_ddm_price(ddm_price_data):
    pershare_rows = ["Y1 Expected Annual Dividends Per Share", "Implied Share Price", "Target Buy Price", "Current Price"]

    formatted_ddm_price_data = ddm_price_data.apply(
        format_row,
        axis=1,
        pershare_rows=pershare_rows
    ).reset_index()

    # Highlighting the Target Buy Price Cell, which is in coordinates (2,1)
    formatted_ddm_price_data = formatted_ddm_price_data.style.apply(
        highlight_exact_cells,
        axis=1,
        target_cells=[(2,1)]
    )

    return formatted_ddm_price_data

# Cached Function to calculate the DDM valuation
@st.cache_data(ttl=3600, show_spinner=False)
def process_ddm_calculations(info_dict, income_stmt_data, balance_sheet_data, cashflow_stmt_data, financial_stmt_summary, financial_perf_data, margin_of_safety):
    # 1. Get the Weighted Average Cost of Capital (WACC)
    wacc_data, wacc = get_wacc(
        info_dict,
        income_stmt_data,
        balance_sheet_data,
        financial_stmt_summary
    )

    # 2. Get the historical dividend data and the average dividend growth rate (g)
    dividend_data, g = get_dividend_data(
        income_stmt_data,
        cashflow_stmt_data,
        financial_perf_data
    )

    # 3. Get the DDM Price data, which includes Implied Share Price, and the Target Buy Price after accounting for Margin of Safety
    ddm_price_data = get_ddm_price(
        margin_of_safety,
        dividend_data.at["Annual Dividends Per Share", dividend_data.columns[-1]],
        g,
        wacc,
        info_dict.get("currentPrice", "N/A")
    )

    return wacc_data, wacc, dividend_data, g, ddm_price_data

# Cached Function that calculates the DDM engine for Sensitivity Analysis based on the inputs
@st.cache_data(ttl=3600, show_spinner=False)
def ddm_engine(wacc, g, dividend_data, margin_of_safety, info_dict):
    if wacc < g:
        return np.nan # Avoid mathematical errors

    ddm_price_data = get_ddm_price(
        margin_of_safety,
        dividend_data.at["Annual Dividends Per Share", dividend_data.columns[-1]],
        g,
        wacc,
        info_dict.get("currentPrice", "N/A")
    )

    target_buy_price = ddm_price_data.at["Target Buy Price", ddm_price_data.columns[0]]

    return f"${target_buy_price:.2f}"