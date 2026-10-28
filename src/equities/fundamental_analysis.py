import numpy as np
import pandas as pd
import streamlit as st
from src.shared.finance_utils import (
    format_row,
    format_large_money,
    calculate_growth,
    format_financial_statement,
    align_financial_statements,
    conditional_highlight_negative,
    conditional_highlight_positive,
    conditional_highlight_equal,
    conditional_highlight_between
)
from src.equities.financial_statements import parse_income_stmt, parse_balance_sheet, parse_cashflow_stmt

# Function to calculate summations safely even with nan as values
def safe_add(*args):
    # Convert all inputs into a single numpy structure
    stack = np.array(args)
    
    # 1. Check where ALL inputs are nan
    all_nan = np.all(np.isnan(stack), axis=0)
    
    # 2. Replace nan with 0 and sum along the inputs axis
    total_sum = np.nansum(stack, axis=0)
    
    # 3. If all were nan, force nan. Otherwise, keep the sum.
    return np.where(all_nan, np.nan, total_sum)

# Function to calculate subtractions safely even with nan as values
def safe_subtract(*args):
    stack = np.array(args)
    all_nan = np.all(np.isnan(stack), axis=0)
    
    # Fill nan with 0 for sequential subtraction
    clean_stack = np.nan_to_num(stack)
    
    # Subtract sequentially: args[0] - args[1] - args[2]...
    total_sub = np.subtract.reduce(clean_stack, axis=0)
    
    return np.where(all_nan, np.nan, total_sub)

# Function to combine crucial data from the 3 financial statements into 1 summary
def get_statement_summary(income_stmt, balance_sheet, cashflow_stmt):
    income_stmt_summary = income_stmt.loc[[
        "Revenue",
        "COGS % of Sales",
        "Gross Profit",
        "Gross Profit Margin",
        "SG&A % of Sales",
        "R&D % of Sales",
        "Total Operating Expense % of Sales",
        "Operating Earnings (EBIT)",
        "EBIT Margin",
        "EBITDA",
        "EBITDA Margin",
        "Net Operating Profit After Tax (NOPAT)",
        "Net Income",
        "Net Income Margin"
    ]].copy()

    balance_sheet_summary = balance_sheet.loc[[
        "Total Current Assets",
        "Total Non-Current Assets",
        "Total Assets",
        "Total Current Liabilities",
        "Total Non-Current Liabilities",
        "Total Liabilities",
        "Total Shareholders' Equity"
    ]].copy()

    # Adding some custom metrics to Balance Sheet Summary
    balance_sheet_summary.loc["Total Liquid Cash"] = safe_subtract(
        balance_sheet.loc["Cash & Short Term Investments"],
        balance_sheet.loc["Current Debt"],
        balance_sheet.loc["Long-Term Debt"]
    )
    balance_sheet_summary.loc["Net PP&E % of Sales"] = balance_sheet.loc["Net Plant, Property And Equipment (PPE)"] / income_stmt.loc["Revenue"]
    balance_sheet_summary.loc["Total Debt"] = safe_add(
        balance_sheet.loc["Current Debt"],
        balance_sheet.loc["Long-Term Debt"]
    )
    balance_sheet_summary.loc["Total Capital Raised"] = safe_add(
        balance_sheet.loc["Total Capital Stock"],
        balance_sheet.loc["Additional Paid-In Capital"]
    )
    balance_sheet_summary.loc["Total Profit Retained"] = safe_add(
        balance_sheet.loc["Retained Earnings"],
        balance_sheet.loc["Treasury Stock"],
        balance_sheet.loc["Other Equity Adjustments"]
    )

    # Re-ordering the columns in balance_sheet_summary
    balance_sheet_summary = balance_sheet_summary.loc[[
        "Total Liquid Cash",
        "Total Current Assets",
        "Net PP&E % of Sales",
        "Total Non-Current Assets",
        "Total Assets",
        "Total Debt", 
        "Total Current Liabilities",
        "Total Non-Current Liabilities",
        "Total Liabilities",
        "Total Capital Raised",
        "Total Profit Retained",
        "Total Shareholders' Equity"
    ]]

    cashflow_stmt_summary = cashflow_stmt.loc[[
        "Change In Working Capital",
        "Net Operating Cash Flow",
        "Capital Expenditures on Fixed Assets (PPE)",
        "Net Capital Expenditures on Fixed Assets (PPE)",
        "Net Investing Cash Flow",
        "Total Cash Dividends Paid",
        "Net Repurchase And Issuance of Capital Stock",
        "Net Financing Cash Flow",
        "Net Change in Cash",
        "Free Cash Flow"
    ]].copy()

    # Adding some custom metrics to Cash Flow Statement Summary
    cashflow_stmt_summary.loc["Change In Working Capital % of Sales"] = cashflow_stmt.loc["Change In Working Capital"] / income_stmt.loc["Revenue"]
    cashflow_stmt_summary.loc["Net Operating Cash Flow % of Sales"] = cashflow_stmt.loc["Net Operating Cash Flow"] / income_stmt.loc["Revenue"]
    cashflow_stmt_summary.loc["CapEx on Fixed Assets (PPE) % of Sales"] = cashflow_stmt.loc["Capital Expenditures on Fixed Assets (PPE)"] / income_stmt.loc["Revenue"]
    cashflow_stmt_summary.loc["Net Investing Cash Flow % of Sales"] = cashflow_stmt.loc["Net Investing Cash Flow"] / income_stmt.loc["Revenue"]
    cashflow_stmt_summary.loc["Net Financing Cash Flow % of Sales"] = cashflow_stmt.loc["Net Financing Cash Flow"] / income_stmt.loc["Revenue"]
    cashflow_stmt_summary.loc["Free Cash Flow % of Sales"] = cashflow_stmt.loc["Free Cash Flow"] / income_stmt.loc["Revenue"]
    cashflow_stmt_summary.loc["Free Cash Flow to Firm (FCFF)"] = safe_subtract(
        safe_add(
            income_stmt.loc["Net Operating Profit After Tax (NOPAT)"],
            cashflow_stmt.loc["Depreciation, Depletion And Amortization (DD&A)"],
            cashflow_stmt.loc["Capital Expenditures on Fixed Assets (PPE)"]
        ),
        cashflow_stmt.loc["Change In Working Capital"]
    )
    cashflow_stmt_summary.loc["Free Cash Flow to Equity (FCFE)"] = safe_add(
        cashflow_stmt.loc["Net Operating Cash Flow"],
        cashflow_stmt.loc["Capital Expenditures on Fixed Assets (PPE)"],
        cashflow_stmt.loc["Net Issuance And Payments of Debt"]
    )

    # Re-ordering the columns in cashflow_stmt_summary
    cashflow_stmt_summary = cashflow_stmt_summary.loc[[
        "Change In Working Capital",
        "Change In Working Capital % of Sales",
        "Net Operating Cash Flow",
        "Net Operating Cash Flow % of Sales",
        "Capital Expenditures on Fixed Assets (PPE)",
        "CapEx on Fixed Assets (PPE) % of Sales",
        "Net Capital Expenditures on Fixed Assets (PPE)",
        "Net Investing Cash Flow",
        "Net Investing Cash Flow % of Sales",
        "Total Cash Dividends Paid",
        "Net Repurchase And Issuance of Capital Stock",
        "Net Financing Cash Flow",
        "Net Financing Cash Flow % of Sales",
        "Net Change in Cash",
        "Free Cash Flow",
        "Free Cash Flow % of Sales",
        "Free Cash Flow to Firm (FCFF)",
        "Free Cash Flow to Equity (FCFE)"
    ]]

    # Unioning the different summaries of the 3 statements to create 1 summarized statement
    financial_stmt_summary = pd.concat([
        income_stmt_summary,
        balance_sheet_summary,
        cashflow_stmt_summary
    ])

    return financial_stmt_summary

# Function to format the newly created financial statement summary and ensures that it is displayed nicely with units in the front-end
def format_statement_summary(financial_stmt_summary):
    percentage_rows = [
        "COGS % of Sales",
        "Gross Profit Margin",
        "SG&A % of Sales",
        "R&D % of Sales",
        "Total Operating Expense % of Sales",
        "EBIT Margin",
        "EBITDA Margin",
        "Net Income Margin",
        "Net PP&E % of Sales",
        "Change In Working Capital % of Sales",
        "Net Operating Cash Flow % of Sales",
        "CapEx on Fixed Assets (PPE) % of Sales",
        "Net Investing Cash Flow % of Sales",
        "Net Financing Cash Flow % of Sales",
        "Free Cash Flow % of Sales"
    ]

    formatted_financial_stmt_summary = financial_stmt_summary.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows
    )

    statement_structure = {
        "Income Statement Data": [ #0
            "Revenue", #1
            "COGS % of Sales", #2
            "Gross Profit", #3
            "Gross Profit Margin", #4
            "SG&A % of Sales", #5
            "R&D % of Sales", #6
            "Total Operating Expense % of Sales", #7
            "Operating Earnings (EBIT)", #8
            "EBIT Margin", #9
            "EBITDA", #10
            "EBITDA Margin", #11
            "Net Operating Profit After Tax (NOPAT)", #12
            "Net Income", #13
            "Net Income Margin" #14
        ],
        "Balance Sheet Data": [ #15
            "Total Liquid Cash", #16
            "Total Current Assets", #17
            "Net PP&E % of Sales", #18
            "Total Non-Current Assets", #19
            "Total Assets", #20
            "Total Debt", #21
            "Total Current Liabilities", #22
            "Total Non-Current Liabilities", #23
            "Total Liabilities", #24
            "Total Capital Raised", #25
            "Total Profit Retained", #26
            "Total Shareholders' Equity" #27
        ],
        "Cash Flow Statement Data": [ #28
            "Change In Working Capital", #29
            "Change In Working Capital % of Sales", #30
            "Net Operating Cash Flow", #31
            "Net Operating Cash Flow % of Sales", #32
            "Capital Expenditures on Fixed Assets (PPE)", #33
            "CapEx on Fixed Assets (PPE) % of Sales", #34
            "Net Capital Expenditures on Fixed Assets (PPE)", #35
            "Net Investing Cash Flow", #36
            "Net Investing Cash Flow % of Sales", #37
            "Total Cash Dividends Paid", #38
            "Net Repurchase And Issuance of Capital Stock", #39
            "Net Financing Cash Flow", #40
            "Net Financing Cash Flow % of Sales", #41
            "Net Change in Cash", #42
            "Free Cash Flow", #43
            "Free Cash Flow % of Sales", #44
            "Free Cash Flow to Firm (FCFF)", #45
            "Free Cash Flow to Equity (FCFE)" #46
        ]
    }

    formatted_financial_stmt_summary = format_financial_statement(
        formatted_financial_stmt_summary,
        statement_structure,
        formatted_financial_stmt_summary.columns
    )

    # Styling specific rows of the formatted dataframe
    formatted_financial_stmt_summary = formatted_financial_stmt_summary.style.apply(
        lambda row: [conditional_highlight_positive(val, 100) for val in row],
        axis=1,
        subset=([2, 5, 6, 18, 34], slice(None))
    ).apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([3, 8, 10, 12, 13, 29, 31, 36, 40, 42, 43, 45, 46], slice(None))
    )

    return formatted_financial_stmt_summary

# Function to create a custom financial performance statement based on calculations of metrics from the 3 financial statements
def get_financial_performance(price_history, income_stmt, balance_sheet, cashflow_stmt):
    # Map the closing prices back to the exact dates in income_stmt
    closing_prices = {}
    for dt in income_stmt.columns:
        # Format date string for indexing
        date_str = pd.to_datetime(dt).strftime("%Y-%m-%d")
        
        # Check if the date exists in price history (e.g., if it landed on a market open day)
        if date_str in price_history.index.strftime("%Y-%m-%d"):
            closing_prices[dt] = price_history.loc[date_str]
        else:
            # Fallback: get the nearest prior trading day's price if the date was a weekend/holiday
            idx = price_history.index.get_indexer([pd.to_datetime(dt)], method="pad")[0]
            closing_prices[dt] = price_history.iloc[idx]

    # Add the closing prices as a new row to a new Financial Performance Dataframe
    financial_perf_data = income_stmt.loc[[
        "Basic EPS",
        "Basic EPS Growth",
        "Basic Average Shares",
        "Revenue Growth",
        "Gross Profit Growth",
        "EBIT Growth",
        "EBITDA Growth",
        "Net Income Growth"
    ]].copy()
    financial_perf_data.loc["Closing Stock Price ($)"] = pd.Series(closing_prices)

    # Adding custom data from all financial statements, some calculated using different information from each statement
    # Per Share Data
    financial_perf_data.loc["Sales Per Share (SPS)"] = income_stmt.loc["Revenue"] / income_stmt.loc["Basic Average Shares"]
    financial_perf_data.loc["Book Value Per Share (BVPS)"] = safe_subtract(
        balance_sheet.loc["Total Shareholders' Equity"],
        balance_sheet.loc["Preferred Stock"]
    ) / income_stmt.loc["Basic Average Shares"]
    financial_perf_data.loc["Free Cash Flow Per Share (FCFPS)"] = cashflow_stmt.loc["Free Cash Flow"] / income_stmt.loc["Basic Average Shares"]

    # Valuation Metrics
    financial_perf_data.loc["P/E Ratio"] = np.where(
        income_stmt.loc["Basic EPS"] > 0,
        financial_perf_data.loc["Closing Stock Price ($)"] / income_stmt.loc["Basic EPS"],
        np.nan
    )
    financial_perf_data.loc["P/S Ratio"] = financial_perf_data.loc["Closing Stock Price ($)"] / financial_perf_data.loc["Sales Per Share (SPS)"]
    financial_perf_data.loc["P/B Ratio"] = np.where(
        financial_perf_data.loc["Book Value Per Share (BVPS)"] > 0,
        financial_perf_data.loc["Closing Stock Price ($)"] / financial_perf_data.loc["Book Value Per Share (BVPS)"],
        np.nan
    )
    financial_perf_data.loc["P/FCF Ratio"] = np.where(
        financial_perf_data.loc["Free Cash Flow Per Share (FCFPS)"] > 0,
        financial_perf_data.loc["Closing Stock Price ($)"] / financial_perf_data.loc["Free Cash Flow Per Share (FCFPS)"],
        np.nan
    )

    # Growth Metrics from Balance Sheet and Cash Flow Statement
    financial_perf_data.loc["Total Assets Growth"] = balance_sheet.loc["Total Assets Growth"]
    financial_perf_data.loc["Total Shareholders' Equity Growth"] = balance_sheet.loc["Total Shareholders' Equity Growth"]
    financial_perf_data.loc["Net Operating Cash Flow Growth"] = cashflow_stmt.loc["Net Operating Cash Flow Growth"]
    financial_perf_data.loc["Net Investing Cash Flow Growth"] = cashflow_stmt.loc["Net Investing Cash Flow Growth"]
    financial_perf_data.loc["Net Financing Cash Flow Growth"] = cashflow_stmt.loc["Net Financing Cash Flow Growth"]
    financial_perf_data.loc["Free Cash Flow Growth"] = cashflow_stmt.loc["Free Cash Flow Growth"]
    financial_perf_data.loc["FCFPS Growth"] = calculate_growth("Free Cash Flow Per Share (FCFPS)", financial_perf_data)

    # Financial Strength Metrics
    financial_perf_data.loc["Total Liabilities % of Total Assets"] = balance_sheet.loc["Total Liabilities % of Total Assets"]
    financial_perf_data.loc["Net Debt"] = safe_subtract(
        safe_add(
            balance_sheet.loc["Current Debt"],
            balance_sheet.loc["Long-Term Debt"]
        ),
        balance_sheet.loc["Cash & Short Term Investments"]
    )
    financial_perf_data.loc["Net Debt to EBITDA Ratio"] = financial_perf_data.loc["Net Debt"] / income_stmt.loc["EBITDA"]
    financial_perf_data.loc["Quick Ratio"] = safe_add(
        balance_sheet.loc["Cash & Short Term Investments"],
        balance_sheet.loc[ "Accounts Receivable"]
    ) / balance_sheet.loc["Total Current Liabilities"]
    financial_perf_data.loc["Current Ratio"] = balance_sheet.loc["Total Current Assets"] / balance_sheet.loc["Total Current Liabilities"]
    financial_perf_data.loc["Long-Term Debt to Equity Ratio"] = balance_sheet.loc["Long-Term Debt"] / balance_sheet.loc["Total Shareholders' Equity"]
    financial_perf_data.loc["Debt to Equity Ratio"] = safe_add(
        balance_sheet.loc["Current Debt"],
        balance_sheet.loc["Long-Term Debt"]
    ) / balance_sheet.loc["Total Shareholders' Equity"]

    # Management Effectiveness Metrics
    financial_perf_data.loc["Return on Assets (ROA)"] = income_stmt.loc["Net Income"] / balance_sheet.loc["Total Assets"]
    financial_perf_data.loc["Return on Invested Capital (ROIC)"] = income_stmt.loc["Net Operating Profit After Tax (NOPAT)"] / safe_subtract(safe_add(balance_sheet.loc["Current Debt"], balance_sheet.loc["Long-Term Debt"], balance_sheet.loc["Total Shareholders' Equity"]), balance_sheet.loc["Cash & Short Term Investments"])
    financial_perf_data.loc["Return on Equity (ROE)"] = income_stmt.loc["Net Income"] / balance_sheet.loc["Total Shareholders' Equity"]

    # Efficiency Metrics
    financial_perf_data.loc["Asset Turnover Ratio"] = income_stmt.loc["Revenue"] / balance_sheet.loc["Total Assets"]
    financial_perf_data.loc["Inventory Turnover Ratio"] = income_stmt.loc["Cost Of Goods Sold (COGS)"] / balance_sheet.loc["Inventory"]

    # Dividend Metrics
    financial_perf_data.loc["Annual Dividends Per Share"] = abs(cashflow_stmt.loc["Total Cash Dividends Paid"]) / income_stmt.loc["Basic Average Shares"]
    financial_perf_data.loc["Dividend Yield"] = financial_perf_data.loc["Annual Dividends Per Share"] / financial_perf_data.loc["Closing Stock Price ($)"]
    financial_perf_data.loc["Dividend Growth"] = calculate_growth("Annual Dividends Per Share", financial_perf_data)
    financial_perf_data.loc["Dividend Payout"] = abs(cashflow_stmt.loc["Total Cash Dividends Paid"]) / income_stmt.loc["Net Income"]
    financial_perf_data.loc["Dividends And Net Repurchase And Issuance of Capital Stock % of FCF"] = abs(
        safe_add(
            cashflow_stmt.loc["Total Cash Dividends Paid"],
            cashflow_stmt.loc["Net Repurchase And Issuance of Capital Stock"]
        )
    ) / cashflow_stmt.loc["Free Cash Flow"]

    # Re-ordering the columns in the financial_perf_data
    financial_perf_data = financial_perf_data.loc[[
        "Closing Stock Price ($)",
        "Basic EPS",
        "Sales Per Share (SPS)",
        "Book Value Per Share (BVPS)",
        "Free Cash Flow Per Share (FCFPS)",
        "P/E Ratio",
        "P/S Ratio",
        "P/B Ratio",
        "P/FCF Ratio",
        "Revenue Growth",
        "Gross Profit Growth",
        "EBIT Growth",
        "EBITDA Growth",
        "Net Income Growth",
        "Net Operating Cash Flow Growth",
        "Net Investing Cash Flow Growth",
        "Net Financing Cash Flow Growth",
        "Free Cash Flow Growth",
        "Basic EPS Growth",
        "FCFPS Growth",
        "Total Liabilities % of Total Assets",
        "Net Debt",
        "Net Debt to EBITDA Ratio",
        "Quick Ratio",
        "Current Ratio",
        "Long-Term Debt to Equity Ratio",
        "Debt to Equity Ratio",
        "Return on Assets (ROA)",
        "Return on Invested Capital (ROIC)",
        "Return on Equity (ROE)",
        "Asset Turnover Ratio",
        "Inventory Turnover Ratio",
        "Annual Dividends Per Share",
        "Dividend Yield",
        "Dividend Growth",
        "Dividend Payout",
        "Dividends And Net Repurchase And Issuance of Capital Stock % of FCF"
    ]]

    return financial_perf_data

# Function to format the newly created financial performance data and ensures that it is displayed nicely with units in the front-end
def format_financial_performance(financial_perf_data):
    pershare_rows = [
        "Closing Stock Price ($)",
        "Basic EPS",
        "Sales Per Share (SPS)",
        "Book Value Per Share (BVPS)",
        "Free Cash Flow Per Share (FCFPS)",
        "Annual Dividends Per Share"
    ]

    ratio_rows = [
        "P/E Ratio",
        "P/S Ratio",
        "P/B Ratio",
        "P/FCF Ratio",
        "Net Debt to EBITDA Ratio",
        "Quick Ratio",
        "Current Ratio",
        "Long-Term Debt to Equity Ratio",
        "Debt to Equity Ratio",
        "Asset Turnover Ratio",
        "Inventory Turnover Ratio"
    ]

    percentage_rows = [
        "Revenue Growth",
        "Gross Profit Growth",
        "EBIT Growth",
        "EBITDA Growth",
        "Net Income Growth",
        "Net Operating Cash Flow Growth",
        "Net Investing Cash Flow Growth",
        "Net Financing Cash Flow Growth",
        "Free Cash Flow Growth",
        "Basic EPS Growth",
        "FCFPS Growth",
        "Total Liabilities % of Total Assets",
        "Return on Assets (ROA)",
        "Return on Invested Capital (ROIC)",
        "Return on Equity (ROE)",
        "Dividend Yield",
        "Dividend Growth",
        "Dividend Payout",
        "Dividends And Net Repurchase And Issuance of Capital Stock % of FCF"
    ]

    formatted_financial_perf_data = financial_perf_data.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows,
        pershare_rows=pershare_rows,
        ratio_rows=ratio_rows
    )

    statement_structure = {
        "Per Share Metrics": [ #0
            "Closing Stock Price ($)", #1
            "Basic EPS", #2
            "Sales Per Share (SPS)", #3
            "Book Value Per Share (BVPS)", #4
            "Free Cash Flow Per Share (FCFPS)" #5
        ],
        "Valuation Metrics": [ #6
            "P/E Ratio", #7
            "P/S Ratio", #8
            "P/B Ratio", #9
            "P/FCF Ratio" #10
        ],
        "Growth Metrics": [ #11
            "Revenue Growth", #12
            "Gross Profit Growth", #13
            "EBIT Growth", #14
            "EBITDA Growth", #15
            "Net Income Growth", #16
            "Net Operating Cash Flow Growth", #17
            "Net Investing Cash Flow Growth", #18
            "Net Financing Cash Flow Growth", #19
            "Free Cash Flow Growth", #20
            "Basic EPS Growth", #21
            "FCFPS Growth" #22
        ],
        "Financial Strength Metrics": [ #23
            "Total Liabilities % of Total Assets", #24
            "Net Debt", #25
            "Net Debt to EBITDA Ratio", #26
            "Quick Ratio", #27
            "Current Ratio", #28
            "Long-Term Debt to Equity Ratio", #29
            "Debt to Equity Ratio" #30
        ],
        "Management Effectiveness Metrics": [ #31
            "Return on Assets (ROA)", #32
            "Return on Invested Capital (ROIC)", #33
            "Return on Equity (ROE)" #34
        ],
        "Efficiency Metrics": [ #35
            "Asset Turnover Ratio", #36
            "Inventory Turnover Ratio" #37
        ],
        "Dividend Metrics": [ #38
            "Annual Dividends Per Share", #39
            "Dividend Yield", #40
            "Dividend Growth", #41
            "Dividend Payout", #42
            "Dividends And Net Repurchase And Issuance of Capital Stock % of FCF" #43
        ]
    }

    formatted_financial_perf_data = format_financial_statement(
        formatted_financial_perf_data,
        statement_structure,
        formatted_financial_perf_data.columns
    )

    # Styling specific rows of the formatted dataframe
    formatted_financial_perf_data = formatted_financial_perf_data.style.apply(
        lambda row: [conditional_highlight_positive(val, 100) for val in row],
        axis=1,
        subset=([24, 43], slice(None)) # Total Liabilities to Total Assets Ratio (%) and Dividends and Net Repurchase And Issuance of Capital Stock % of FCF
    ).apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 41], slice(None)) # All the Per Share (except SPS) and Growth Metrics
    ).apply(
        lambda row: [conditional_highlight_positive(val, 70) for val in row],
        axis=1,
        subset=([42], slice(None)) # Dividend Payout
    ).apply(
        lambda row: [conditional_highlight_positive(val, 3) for val in row],
        axis=1,
        subset=([26], slice(None)) # Net Debt to EBITDA Ratio
    ).apply(
        lambda row: [conditional_highlight_positive(val, 2) for val in row],
        axis=1,
        subset=([30], slice(None)) # Debt to Equity Ratio
    ).apply(
        lambda row: [conditional_highlight_positive(val, 1.5) for val in row],
        axis=1,
        subset=([29], slice(None)) # Long-Term Debt to Equity Ratio
    ).apply(
        lambda row: [conditional_highlight_positive(val, 0) for val in row],
        axis=1,
        subset=([25], slice(None)) # Net Debt
    ).apply(
        lambda row: [conditional_highlight_negative(val, 20) for val in row],
        axis=1,
        subset=([34], slice(None)) # Return on Equity (ROE)
    ).apply(
        lambda row: [conditional_highlight_negative(val, 10) for val in row],
        axis=1,
        subset=([32, 33], slice(None)) # Return on Assets (ROA) and Return on Invested Capital (ROIC)
    ).apply(
        lambda row: [conditional_highlight_negative(val, 5) for val in row],
        axis=1,
        subset=([37], slice(None)) # Inventory Turnover Ratio
    ).apply(
        lambda row: [conditional_highlight_negative(val, 1) for val in row],
        axis=1,
        subset=([27, 28, 36], slice(None)) # Quick Ratio, Current Ratio and Asset Turnover Ratio
    )

    return formatted_financial_perf_data

# Function to create a financial guardrail of metrics from the financial statements to determine the health of a company
def get_financial_guardrails(income_stmt_data, balance_sheet_data, cashflow_stmt_data, financial_perf_data):
    # Building the financial_guardrails dataframe using specific line items from the 3 financial statements and the financial performance dataframe
    financial_guardrails_df = pd.concat([
        income_stmt_data.loc[[
            "Gross Profit Margin",
            "Effective Tax Rate",
            "Net Income Margin",
            "Basic EPS",
            "Basic EPS Growth"
        ]],
        balance_sheet_data.loc[[
            "Preferred Stock",
            "Retained Earnings",
            "Retained Earnings Growth",
            "Treasury Stock"
        ]],
        cashflow_stmt_data.loc[[
            "Net Operating Cash Flow",
            "Net Operating Cash Flow Growth"
        ]],
        financial_perf_data.loc[[
            "Net Debt",
            "Debt to Equity Ratio",
            "Return on Equity (ROE)",
            "Dividend Payout"
        ]]
    ])

    financial_guardrails_df.loc["SG&A % of Gross Profit"] = income_stmt_data.loc["Selling General And Administration (SG&A)"] / income_stmt_data.loc["Gross Profit"]
    financial_guardrails_df.loc["R&D % of Gross Profit"] = income_stmt_data.loc["Research And Development (R&D)"] / income_stmt_data.loc["Gross Profit"]
    financial_guardrails_df.loc["Interest Expense % of EBIT"] = income_stmt_data.loc["Non-Operating Interest Expense"] / income_stmt_data.loc["Operating Earnings (EBIT)"]
    financial_guardrails_df.loc["CapEx % of Net Income"] = abs(cashflow_stmt_data.loc["Capital Expenditures on Fixed Assets (PPE)"]) / income_stmt_data.loc["Net Income"]

    return financial_guardrails_df

# Function to format the newly created financial guardrails data and ensures that it is displayed nicely with units in the front-end
def format_financial_guardrails(financial_guardrails_df):
    percentage_rows = [
        "Gross Profit Margin",
        "SG&A % of Gross Profit",
        "R&D % of Gross Profit",
        "Interest Expense % of EBIT",
        "Effective Tax Rate",
        "Net Income Margin",
        "Basic EPS Growth",
        "Retained Earnings Growth",
        "Return on Equity (ROE)",
        "Net Operating Cash Flow Growth",
        "CapEx % of Net Income",
        "Dividend Payout"
    ]

    quantity_rows = ["Preferred Stock", "Treasury Stock"]
    pershare_rows = ["Basic EPS"]
    ratio_rows = ["Debt to Equity Ratio"]

    formatted_financial_guardrails_df = financial_guardrails_df.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows,
        quantity_rows=quantity_rows,
        pershare_rows=pershare_rows,
        ratio_rows=ratio_rows
    )

    statement_structure = {
        "Income Statement": [ #0
            "Gross Profit Margin", #1
            "SG&A % of Gross Profit", #2
            "R&D % of Gross Profit", #3
            "Interest Expense % of EBIT", #4
            "Effective Tax Rate", #5
            "Net Income Margin", #6
            "Basic EPS", #7
            "Basic EPS Growth", #8
        ],
        "Balance Sheet": [ #9
            "Net Debt", #10
            "Debt to Equity Ratio", #11
            "Preferred Stock", #12
            "Retained Earnings", #13
            "Retained Earnings Growth", #14
            "Treasury Stock", #15
            "Return on Equity (ROE)" #16
        ],
        "Cash Flow Statement": [ #17
            "Net Operating Cash Flow", #18
            "Net Operating Cash Flow Growth", #19
            "CapEx % of Net Income", #20
            "Dividend Payout" #21
        ]
    }

    formatted_financial_guardrails_df = format_financial_statement(
        formatted_financial_guardrails_df,
        statement_structure,
        formatted_financial_guardrails_df.columns
    )

    formatted_financial_guardrails_df["Criteria"] = formatted_financial_guardrails_df.index.map({
        0: None, # Income Statement
        1: "> 40%", # Gross Profit Margin
        2: "≤ 30%", # SG&A % of Gross Profit
        3: "≤ 30%", # R&D % of Gross Profit
        4: "≤ 15%", # Interest Expense % of EBIT
        5: "20 ± 5%", # Effective Tax Rate
        6: "> 20%", # Net Income Margin
        7: "> 0", # Basic EPS
        8: "> 0%", # Basic EPS Growth
        9: None, # Balance Sheet
        10: "≤ 0", # Net Debt
        11: "≤ 0.80", # Debt to Equity Ratio
        12: "= 0", # Preferred Stock
        13: "> 0", # Retained Earnings
        14: "> 0%", # Retained Earnings Growth
        15: "> 0", # Treasury Stock
        16: "> 15%", # Return on Equity (ROE)
        17: None, # Cash Flow Statement
        18: "> 0", # Net Operating Cash Flow
        19: "> 0%", # Net Operating Cash Flow Growth
        20: "≤ 25%", # CapEx % of Net Income
        21: "≤ 70%" # Dividend Payout
    })

    # Move the Criteria column to the second column, and append the rest
    formatted_financial_guardrails_df = formatted_financial_guardrails_df[
        [formatted_financial_guardrails_df.columns[0], formatted_financial_guardrails_df.columns[-1]] 
        + list(formatted_financial_guardrails_df.columns[1:-1])
    ]

    formatted_financial_guardrails_df = formatted_financial_guardrails_df.style.apply(
        lambda row: [conditional_highlight_negative(val, 40) for val in row],
        axis=1,
        subset=([1], slice(None)) # Gross Profit Margin
    ).apply(
        lambda row: [conditional_highlight_positive(val, 30) for val in row],
        axis=1,
        subset=([2, 3], slice(None)) # SG&A and R&D % of Gross Profit
    ).apply(
        lambda row: [conditional_highlight_positive(val, 15) for val in row],
        axis=1,
        subset=([4], slice(None)) # Interest Expense % of EBIT
    ).apply(
        lambda row: [conditional_highlight_between(val, 15, 25) for val in row],
        axis=1,
        subset=([5], slice(None)) # Effective Tax Rate
    ).apply(
        lambda row: [conditional_highlight_negative(val, 20) for val in row],
        axis=1,
        subset=([6], slice(None)) # Net Income Margin
    ).apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([7, 8, 13, 14, 15, 18, 19], slice(None)) # Basic EPS, Basic EPS Growth, Retained Earnings, Retained Earnings Growth, Treasury Stock, Net Operating Cash Flow, and Net Operating Cash Flow Growth
    ).apply(
        lambda row: [conditional_highlight_positive(val, 0) for val in row],
        axis=1,
        subset=([10], slice(None)) # Net Debt
    ).apply(
        lambda row: [conditional_highlight_positive(val, 0.8) for val in row],
        axis=1,
        subset=([11], slice(None)) # Debt to Equity Ratio
    ).apply(
        lambda row: [conditional_highlight_equal(val, 0) for val in row],
        axis=1,
        subset=([12], slice(None)) # Preferred Stock
    ).apply(
        lambda row: [conditional_highlight_negative(val, 15) for val in row],
        axis=1,
        subset=([16], slice(None)) # Return on Equity (ROE)
    ).apply(
        lambda row: [conditional_highlight_positive(val, 25) for val in row],
        axis=1,
        subset=([20], slice(None)) # CapEx % of Net Income
    ).apply(
        lambda row: [conditional_highlight_positive(val, 70) for val in row],
        axis=1,
        subset=([21], slice(None)) # Dividend Payout
    )

    return formatted_financial_guardrails_df

# Cached Function to process the financial statements and returns serialized objects like dataframes and not the styled dataframes so that the cache_data decorator can be used instead of using cache_resource
@st.cache_data(ttl=3600, show_spinner=False)
def process_financial_statements(income_stmt, balance_sheet, cashflow_stmt, price_history):
    # Adjusting the dimensions of the financial statement dataframes to ensure they are all homogeneous and have the same number of columns
    income_stmt, balance_sheet, cashflow_stmt = align_financial_statements(
        income_stmt, balance_sheet, cashflow_stmt
    )

    # Parsing the data to clean and get relevant information
    income_stmt_data = parse_income_stmt(income_stmt)
    balance_sheet_data = parse_balance_sheet(balance_sheet)
    cashflow_stmt_data = parse_cashflow_stmt(cashflow_stmt)

    # Calculating Financial Summaries
    financial_stmt_summary = get_statement_summary(
        income_stmt_data["Essential Data"],
        balance_sheet_data["Essential Data"],
        cashflow_stmt_data["Essential Data"]
    )

    # Calculating Financial Performance Data
    financial_perf_data = get_financial_performance(
        price_history,
        income_stmt_data["Essential Data"],
        balance_sheet_data["Essential Data"],
        cashflow_stmt_data["Essential Data"]
    )

    # Getting the financial guardrails of metrics from the 3 financial statements and the financial performance data
    financial_guardrails_df = get_financial_guardrails(
        income_stmt_data["Essential Data"],
        balance_sheet_data["Essential Data"],
        cashflow_stmt_data["Essential Data"],
        financial_perf_data
    )

    return income_stmt_data, balance_sheet_data, cashflow_stmt_data, financial_stmt_summary, financial_perf_data, financial_guardrails_df

# Cached Function to create the insights summary from the latest data of the financial guardrails
@st.cache_data(ttl=3600, show_spinner=False)
def get_insights_summary(financial_guardrails_df):
    latest_data = financial_guardrails_df.iloc[:, 0].fillna(0)

    # Initializing empty dictionaries
    positive_insights = {}
    negative_insights = {}

    # Gross Profit Margin
    if latest_data["Gross Profit Margin"] > 0.40:
        positive_insights["Gross Profit Margin"] = {
            "Criteria": "> 40%",
            "Value": f"{latest_data["Gross Profit Margin"] * 100:,.2f}%",
            "Rationale": "Indicates a strong, sustainable competitive advantage (moat) and pricing power. Companies with high gross margins can absorb supply chain shocks or inflationary pressures without destroying bottom-line profitability."
        }
    else:
        negative_insights["Gross Profit Margin"] = {
            "Criteria": "≤ 40%",
            "Value": f"{latest_data["Gross Profit Margin"] * 100:,.2f}%",
            "Rationale": "Signifies a commodity-type business lacking a competitive moat or pricing power. Low gross margins mean the company is highly vulnerable to raw material cost spikes, supplier pressure, or industry price wars, leaving very little room to cover operating overhead."
        }

    # SG&A % of Gross Profit
    if latest_data["SG&A % of Gross Profit"] <= 0.30:
        positive_insights["SG&A % of Gross Profit"] = {
            "Criteria": "≤ 30%",
            "Value": f"{latest_data["SG&A % of Gross Profit"] * 100:,.2f}%",
            "Rationale": "Measures operational efficiency and the cost structural drag on core earnings power. Low operational overhead relative to gross output highlights scalable business models that do not require aggressive marketing or administrative scaling to grow revenue."
        }
    else:
        negative_insights["SG&A % of Gross Profit"] = {
            "Criteria": "> 30%",
            "Value": f"{latest_data["SG&A % of Gross Profit"] * 100:,.2f}%",
            "Rationale": "Highlights severe operational inefficiency or an asset-heavy cost structure. When overhead consumes a vast portion of gross output, it reveals a business model that is difficult to scale, often requiring aggressive marketing, high salaries, or heavy administrative burdens just to survive."
        }

    # R&D % of Gross Profit
    if latest_data["R&D % of Gross Profit"] <= 0.30:
        positive_insights["R&D % of Gross Profit"] = {
            "Criteria": "≤ 30%",
            "Value": f"{latest_data["R&D % of Gross Profit"] * 100:,.2f}%",
            "Rationale": "Identifies technological or structural stability. High R&D requirements suggest a company is on a technological treadmill, needing to constantly reinvest to maintain its position, which exposes investors to high obsolescence risk."
        }
    else:
        negative_insights["R&D % of Gross Profit"] = {
            "Criteria": "> 30%",
            "Value": f"{latest_data["R&D % of Gross Profit"] * 100:,.2f}%",
            "Rationale": "Warns that the company is on an expensive, high-risk technological treadmill. Massive structural R&D commitments mean the product suite faces rapid obsolescence risk, forcing continuous reinvestment just to protect existing market share rather than creating incremental value."
        }
    
    # Interest Expense % of EBIT
    if latest_data["Interest Expense % of EBIT"] <= 0.15:
        positive_insights["Interest Expense % of EBIT"] = {
            "Criteria": "≤ 15%",
            "Value": f"{latest_data["Interest Expense % of EBIT"] * 100:,.2f}%",
            "Rationale": "Serves as an earnings-based solvency guardrail. Ensuring operating income easily covers debt service obligations protects the firm from debt default risks during cyclical downturns or periods of escalating interest rates."
        }
    else:
        negative_insights["Interest Expense % of EBIT"] = {
            "Criteria": "> 15%",
            "Value": f"{latest_data["Interest Expense % of EBIT"] * 100:,.2f}%",
            "Rationale": "Signals heavy financial stress and dangerous vulnerability to credit cycles. When debt service consumes a large portion of core operating income, a minor macroeconomic slowdown or an increase in interest rates can easily push the entity into insolvency or cause debt covenant violations."
        }
    
    # Effective Tax Rate
    if latest_data["Effective Tax Rate"] >= 0.15 and latest_data["Effective Tax Rate"] <= 0.25:
        positive_insights["Effective Tax Rate"] = {
            "Criteria": "= 20 ± 5%",
            "Value": f"{latest_data["Effective Tax Rate"] * 100:,.2f}%",
            "Rationale": "Validates earnings quality and structural sustainability. An effective rate within this band aligns with standard corporate regimes, indicating that net income is not being artificially inflated by one-off tax credits or fragile, aggressive offshore tax structures."
        }
    else:
        negative_insights["Effective Tax Rate"] = {
            "Criteria": "≠ 20 ± 5%",
            "Value": f"{latest_data["Effective Tax Rate"] * 100:,.2f}%",
            "Rationale": "Rates below 15% expose low earnings quality, warning that profits are artificially propped up by temporary tax loopholes, foreign tax havens, or vulnerable subsidies. Rates above 25% reveal structural tax inefficiency or exposure to punitive legislative jurisdictions that permanently erode net shareholder yields."
        }

    # Net Income Margin
    if latest_data["Net Income Margin"] > 0.20:
        positive_insights["Net Income Margin"] = {
            "Criteria" : "> 20%",
            "Value": f"{latest_data["Net Income Margin"] * 100:,.2f}%",
            "Rationale": "Reflects exceptional bottom-line efficiency and high conversion of revenue to shareholder wealth. Broad margins provide a significant safety buffer against macroeconomic contraction."
        }
    else:
        negative_insights["Net Income Margin"] = {
            "Criteria": "≤ 20%",
            "Value": f"{latest_data["Net Income Margin"] * 100:,.2f}%",
            "Rationale": "Exposes tight bottom-line margins with zero safety margin. A low conversion rate of revenue to actual profits means that any minor disruption—such as rising logistics costs, a sudden regulatory levy, or modest inflation—can completely wipe out absolute corporate earnings."
        }
        
    # Basic EPS
    if latest_data["Basic EPS"] > 0:
        positive_insights["Basic EPS"] = {
            "Criteria": "> 0",
            "Value": f"${latest_data["Basic EPS"]:,.2f}",
            "Rationale": "Establishes a baseline constraint for fundamental profitability. Eliminates pre-revenue, speculative, or structurally loss-making entities from the investment universe."
        }
    else:
        negative_insights["Basic EPS"] = {
            "Criteria": "≤ 0",
            "Value": f"${latest_data["Basic EPS"]:,.2f}",
            "Rationale": "Identifies a cash-burning, speculative, or fundamentally unprofitable enterprise. Investing in companies with negative earnings requires relying on speculative multi-year growth narratives rather than current fundamental value."
        }

    # Basic EPS Growth
    if latest_data["Basic EPS Growth"] > 0:
        positive_insights["Basic EPS Growth"] = {
            "Criteria": "> 0%",
            "Value": f"{latest_data["Basic EPS Growth"] * 100:,.2f}%",
            "Rationale": "Mandates positive fundamental momentum. Confirms the business is actively scaling or optimizing its capital structure to generate compounding per-share value."
        }
    else:
        negative_insights["Basic EPS Growth"] = {
            "Criteria": "≤ 0%",
            "Value": f"{latest_data["Basic EPS Growth"] * 100:,.2f}%",
            "Rationale": "Captures fundamental contraction or severe per-share capital dilution. It signals that competitive dynamics are degrading the business, margins are compressing, or aggressive share printing is destroying existing shareholder value."
        }
        
    # Net Debt
    if latest_data["Net Debt"] <= 0:
        positive_insights["Net Debt"] = {
            "Criteria": "≤ 0",
            "Value": format_large_money(latest_data["Net Debt"]),
            "Rationale": "Denotes a 'Net Cash' position where total cash and liquid equivalents exceed gross debt obligations. This completely eliminates bankruptcy risk and maximizes financial flexibility for organic expansion or opportunistic M&A."
        }
    else:
        negative_insights["Net Debt"] = {
            "Criteria": "> 0",
            "Value": format_large_money(latest_data["Net Debt"]),
            "Rationale": "Confirms that corporate debt outweighs total available liquidity. This dependency forces the firm to allocate future operating cash flows directly to lenders, raising financing risk and decreasing capital agility."
        }
    
    # Debt to Equity Ratio
    if latest_data["Debt to Equity Ratio"] <= 0.80:
        positive_insights["Debt to Equity Ratio"] = {
            "Criteria": "≤ 0.80",
            "Value": f"{latest_data["Debt to Equity Ratio"]:,.3f}",
            "Rationale": "Restricts structural leverage to institutional safety levels. Prevents the capitalization structure from becoming overly dependent on debt capital, mitigating systemic solvency risks."
        }
    else:
        negative_insights["Debt to Equity Ratio"] = {
            "Criteria": "> 0.80",
            "Value": f"{latest_data["Debt to Equity Ratio"]:,.3f}",
            "Rationale": "Indicates an aggressively leveraged, fragile capital structure. A balance sheet heavily skewed toward debt forces permanent interest burdens and places the company at the mercy of credit market disruptions, heavily multiplying bankruptcy risks during cyclical stress."
        }

    # Preferred Stock
    if latest_data["Preferred Stock"] == 0:
        positive_insights["Preferred Stock"] = {
            "Criteria": "= 0",
            "Value": format_large_money(latest_data["Preferred Stock"]),
            "Rationale": "Eliminates senior equity claims. Preferred stock acts as pseudo-debt with senior dividend rights, which complicates capital allocation and dilutes the residual upside belonging strictly to common equity holders."
        }
    else:
        negative_insights["Preferred Stock"] = {
            "Criteria": "> 0",
            "Value": format_large_money(latest_data["Preferred Stock"]),
            "Rationale": "Introduces senior hurdle layers within equity financing. Preferred equity creates structural subordination for common shareholders, demanding fixed dividend payouts that function like interest obligations, capturing upside that would otherwise accumulate to common book value."
        }

    # Retained Earnings
    if latest_data["Retained Earnings"] > 0:
        positive_insights["Retained Earnings"] = {
            "Criteria": "> 0",
            "Value": format_large_money(latest_data["Retained Earnings"]),
            "Rationale": "Demonstrates long-term cumulative profitability. A positive retained earnings balance confirms the enterprise has a historical track record of generating net profits rather than accumulating deficit capital."
        }
    else:
        negative_insights["Retained Earnings"] = {
            "Criteria": "≤ 0",
            "Value": format_large_money(latest_data["Retained Earnings"]),
            "Rationale": "Unveils a cumulative history of destruction of equity capital. A negative or deficit balance in retained earnings signals that the firm has historically failed to build a self-sustaining operational engine and has consistently bled investor capital."
        }

    # Retained Earnings Growth
    if latest_data["Retained Earnings Growth"] > 0:
        positive_insights["Retained Earnings Growth"] = {
            "Criteria": "> 0%",
            "Value": f"{latest_data["Retained Earnings Growth"] * 100:,.2f}%",
            "Rationale": "Verifies that the corporation is consistently reinvesting internal profits to expand its book value rather than burning capital or over-relying on dilutive share issuances."
        }
    else:
        negative_insights["Retained Earnings Growth"] = {
            "Criteria": "≤ 0%",
            "Value": f"{latest_data["Retained Earnings Growth"] * 100:,.2f}%",
            "Rationale": "Proves that the underlying enterprise is actively consuming its accounting book value. This destruction occurs through structural net losses or irresponsible over-distribution of dividends exceeding actual corporate profit generation."
        }

    # Treasury Stock
    if latest_data["Treasury Stock"] > 0:
        positive_insights["Treasury Stock"] = {
            "Criteria": "> 0",
            "Value": format_large_money(latest_data["Treasury Stock"]),
            "Rationale": "Indicates a historical commitment to share buybacks. The presence of treasury stock reduces outstanding share count, boosts EPS artificially over time, and signals management's confidence that their own stock is an attractive investment."
        }
    else:
        negative_insights["Treasury Stock"] = {
            "Criteria": "≤ 0",
            "Value": format_large_money(latest_data["Treasury Stock"]),
            "Rationale": "Reveals a complete lack of tactical share buyback history. This missing signal typically implies that management is prioritizing cash absorption or dilution via equity issuance, completely failing to exploit periods when their own equity might be underpriced in the open market."
        }

    # Return on Equity (ROE)
    if latest_data["Return on Equity (ROE)"] > 0.15:
        positive_insights["Return on Equity (ROE)"] = {
            "Criteria": "> 15%",
            "Value": f"{latest_data["Return on Equity (ROE)"] * 100:,.2f}%",
            "Rationale": "Measures capital allocation efficiency. High ROE confirms that management generates excellent returns on the net assets entrusted to them by shareholders, reflecting either high asset turnover, high profit margins, or optimized financial leverage."
        }
    else:
        negative_insights["Return on Equity (ROE)"] = {
            "Criteria": "≤ 15%",
            "Value": f"{latest_data["Return on Equity (ROE)"] * 100:,.2f}%",
            "Rationale": "Denotes subpar capital efficiency. A low ROE implies management is failing to optimize equity resources to achieve an acceptable premium over risk-free benchmark alternatives, warning of weak asset optimization or poor product pricing."
        }

    # Net Operating Cash Flow
    if latest_data["Net Operating Cash Flow"] > 0:
        positive_insights["Net Operating Cash Flow"] = {
            "Criteria": "> 0",
            "Value": format_large_money(latest_data["Net Operating Cash Flow"]),
            "Rationale": "Ensures the enterprise produces actual cash from its day-to-day operations. Prevents look-alike profitability driven entirely by non-cash accounting adjustments on the income statement."
        }
    else:
        negative_insights["Net Operating Cash Flow"] = {
            "Criteria": "≤ 0",
            "Value": format_large_money(latest_data["Net Operating Cash Flow"]),
            "Rationale": "Serves as the ultimate warning sign for structural corporate insolvency. It unmasks companies that rely on artificial accounting accruals on the income statement while their day-to-day operations are a net drain on physical liquidity."
        }

    # Net Operating Cash Flow Growth
    if latest_data["Net Operating Cash Flow Growth"] > 0:
        positive_insights["Net Operating Cash Flow Growth"] = {
            "Criteria": "> 0%",
            "Value": f"{latest_data["Net Operating Cash Flow Growth"] * 100:,.2f}%",
            "Rationale": "Confirms structural liquidity scaling. Assures that cash production is expanding alongside top-line and bottom-line accounting metrics, indicating healthy working capital management."
        }
    else:
        negative_insights["Net Operating Cash Flow Growth"] = {
            "Criteria": "≤ 0%",
            "Value": f"{latest_data["Net Operating Cash Flow Growth"] * 100:,.2f}%",
            "Rationale": "Identifies operational or cash cycle degradation. It warns that inventory buildup, poor accounts receivable collections, or general structural decline are stalling the company's liquidity growth engine."
        }
    
    # CapEx % of Net Income
    if latest_data["CapEx % of Net Income"] <= 0.25:
        positive_insights["CapEx % of Net Income"] = {
            "Criteria": "≤ 25%",
            "Value": f"{latest_data["CapEx % of Net Income"] * 100:,.2f}%",
            "Rationale": "Identifies asset-light, highly cash-generative business models. Low capital expenditure requirements mean a vast majority of earnings remain untouched as free cash flow, available for distribution, debt paydown, or strategic maneuvers."
        }
    else:
        negative_insights["CapEx % of Net Income"] = {
            "Criteria": "> 25%",
            "Value": f"{latest_data["CapEx % of Net Income"] * 100:,.2f}%",
            "Rationale": "Exposes an asset-heavy business model bound to high maintenance expenditures. Such firms must spend a vast share of accounting profits merely replacing broken or outdated plant equipment and real estate, transforming them into capital-intensive operations that struggle to distribute free cash flow to investors."
        }

    # Dividend Payout
    if latest_data["Dividend Payout"] <= 0.70:
        positive_insights["Dividend Payout"] = {
            "Criteria": "≤ 70%",
            "Value": f"{latest_data["Dividend Payout"] * 100:,.2f}%",
            "Rationale": "Evaluates dividend safety and corporate reinvestment balance. A payout ratio below this ceiling ensures the dividend is highly insulated from macro shocks while leaving sufficient internal funds to fuel future corporate growth."
        }
    else:
        negative_insights["Dividend Payout"] = {
            "Criteria": "> 70%",
            "Value": f"{latest_data["Dividend Payout"] * 100:,.2f}%",
            "Rationale": "Signals an unsustainable dividend policy at extreme risk of a dividend cut. Such a massive payout ceiling leaves virtually no protection against sudden revenue drops and entirely starves the enterprise of the vital internal capital required for growth."
        }
    
    return positive_insights, negative_insights