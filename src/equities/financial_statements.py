import numpy as np
from src.shared.finance_utils import (
    calculate_growth,
    format_row,
    format_financial_statement,
    conditional_highlight_negative,
    conditional_highlight_positive
)

# Function to parse the Income Statement Data from yfinance and returns a dictionary of dataframes containing essential data and the keywords for web-scraping error checking
def parse_income_stmt(INCOME_STMT):
    # Important Key Words listed in yfinance Income Statement method that are required
    keywords = [
        "Total Revenue", "Cost Of Revenue", "Gross Profit", "Reconciled Depreciation", "Selling General And Administration", "Research And Development",
        "Operating Expense", "Operating Income", "EBITDA", "Other Non Operating Income Expenses", "Interest Income Non Operating", "Interest Expense Non Operating",
        "Earnings From Equity Interest", "Pretax Income", "Tax Provision", "Tax Rate For Calcs", "Net Income", "Net Income From Continuing And Discontinued Operation",
        "Preferred Stock Dividends", "Net Income Common Stockholders", "Basic EPS", "Basic Average Shares", "Diluted EPS", "Diluted Average Shares"
    ]

    # --- REVENUE DATA ---
    if "Total Revenue" in INCOME_STMT.index:
        INCOME_STMT.loc["Revenue"] = INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["Revenue Growth"] = calculate_growth("Total Revenue", INCOME_STMT)
    else:
        INCOME_STMT.loc["Revenue"] = np.nan
        INCOME_STMT.loc["Revenue Growth"] = np.nan

    # --- COST OF REVENUE DATA ---
    if "Cost Of Revenue" in INCOME_STMT.index:
        INCOME_STMT.loc["Cost Of Goods Sold (COGS)"] = INCOME_STMT.loc["Cost Of Revenue"]
        INCOME_STMT.loc["COGS % of Sales"] = INCOME_STMT.loc["Cost Of Revenue"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["COGS Growth"] = calculate_growth("Cost Of Revenue", INCOME_STMT)
    else:
        INCOME_STMT.loc["Cost Of Goods Sold (COGS)"] = np.nan
        INCOME_STMT.loc["COGS % of Sales"] = np.nan
        INCOME_STMT.loc["COGS Growth"] = np.nan

    # --- GROSS PROFIT DATA ---
    if "Gross Profit" in INCOME_STMT.index:
        INCOME_STMT.loc["Gross Profit"] = INCOME_STMT.loc["Gross Profit"]
        INCOME_STMT.loc["Gross Profit Margin"] = INCOME_STMT.loc["Gross Profit"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["Gross Profit Growth"] = calculate_growth("Gross Profit", INCOME_STMT)
    else:
        INCOME_STMT.loc["Gross Profit"] = np.nan
        INCOME_STMT.loc["Gross Profit Margin"] = np.nan
        INCOME_STMT.loc["Gross Profit Growth"] = np.nan

    # --- OPERATING EXPENSE DATA ---
    # Depreciation And Amortization
    if "Reconciled Depreciation" in INCOME_STMT.index:
        INCOME_STMT.loc["Depreciation And Amortization (D&A)"] = INCOME_STMT.loc["Reconciled Depreciation"]
        INCOME_STMT.loc["D&A % of Sales"] = INCOME_STMT.loc["Reconciled Depreciation"] / INCOME_STMT.loc["Total Revenue"]
    else:
        INCOME_STMT.loc["Depreciation And Amortization (D&A)"] = np.nan
        INCOME_STMT.loc["D&A % of Sales"] = np.nan
    # Selling General And Administration
    if "Selling General And Administration" in INCOME_STMT.index:
        INCOME_STMT.loc["Selling General And Administration (SG&A)"] = INCOME_STMT.loc["Selling General And Administration"]
        INCOME_STMT.loc["SG&A % of Sales"] = INCOME_STMT.loc["Selling General And Administration"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["SG&A Growth"] = calculate_growth("Selling General And Administration", INCOME_STMT)
    else:
        INCOME_STMT.loc["Selling General And Administration (SG&A)"] = np.nan
        INCOME_STMT.loc["SG&A % of Sales"] = np.nan
        INCOME_STMT.loc["SG&A Growth"] = np.nan
    # Research And Development
    if "Research And Development" in INCOME_STMT.index:
        INCOME_STMT.loc["Research And Development (R&D)"] = INCOME_STMT.loc["Research And Development"]
        INCOME_STMT.loc["R&D % of Sales"] = INCOME_STMT.loc["Research And Development"] / INCOME_STMT.loc["Total Revenue"]
    else:
        INCOME_STMT.loc["Research And Development (R&D)"] = np.nan
        INCOME_STMT.loc["R&D % of Sales"] = np.nan
    # Total Operating Expense
    if "Operating Expense" in INCOME_STMT.index:
        INCOME_STMT.loc["Total Operating Expense"] = INCOME_STMT.loc["Operating Expense"]
        INCOME_STMT.loc["Total Operating Expense % of Sales"] = INCOME_STMT.loc["Operating Expense"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["Total Operating Expense Growth"] = calculate_growth("Operating Expense", INCOME_STMT)
    else:
        INCOME_STMT.loc["Total Operating Expense"] = np.nan
        INCOME_STMT.loc["Total Operating Expense % of Sales"] = np.nan
        INCOME_STMT.loc["Total Operating Expense Growth"] = np.nan

    # --- OPERATING EARNINGS (EBIT) AND EBITDA DATA ---
    # EBIT
    if "Operating Income" in INCOME_STMT.index:
        INCOME_STMT.loc["Operating Earnings (EBIT)"] = INCOME_STMT.loc["Operating Income"]
        INCOME_STMT.loc["EBIT Margin"] = INCOME_STMT.loc["Operating Income"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["EBIT Growth"] = calculate_growth("Operating Income", INCOME_STMT)
    else:
        INCOME_STMT.loc["Operating Earnings (EBIT)"] = np.nan
        INCOME_STMT.loc["EBIT Margin"] = np.nan
        INCOME_STMT.loc["EBIT Growth"] = np.nan
    # EBITDA
    if "EBITDA" in INCOME_STMT.index:
        INCOME_STMT.loc["EBITDA"] = INCOME_STMT.loc["EBITDA"]
        INCOME_STMT.loc["EBITDA Margin"] = INCOME_STMT.loc["EBITDA"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["EBITDA Growth"] = calculate_growth("EBITDA", INCOME_STMT)
    else:
        INCOME_STMT.loc["EBITDA"] = np.nan
        INCOME_STMT.loc["EBITDA Margin"] = np.nan
        INCOME_STMT.loc["EBITDA Growth"] = np.nan

    # --- OTHER INCOME AND EXPENSES DATA ---
    # Non-Operating Income/Expense
    INCOME_STMT.loc["Non-Operating Income/Expense"] = INCOME_STMT.loc["Other Non Operating Income Expenses"] if "Other Non Operating Income Expenses" in INCOME_STMT.index else np.nan
    # Non-Operating Interest Income
    INCOME_STMT.loc["Non-Operating Interest Income"] = INCOME_STMT.loc["Interest Income Non Operating"] if "Interest Income Non Operating" in INCOME_STMT.index else np.nan
    # Non-Operating Interest Expense
    INCOME_STMT.loc["Non-Operating Interest Expense"] = INCOME_STMT.loc["Interest Expense Non Operating"] if "Interest Expense Non Operating" in INCOME_STMT.index else np.nan
    # Earnings From Equity Interest (Pre-Tax)
    INCOME_STMT.loc["Earnings From Equity Interest (Pre-Tax)"] = INCOME_STMT.loc["Earnings From Equity Interest"] if "Earnings From Equity Interest" in INCOME_STMT.index else np.nan

    # --- PRE-TAX INCOME (EBT) DATA ---
    if "Pretax Income" in INCOME_STMT.index:
        INCOME_STMT.loc["Pre-Tax Income (EBT)"] = INCOME_STMT.loc["Pretax Income"]
        INCOME_STMT.loc["EBT Margin"] = INCOME_STMT.loc["Pretax Income"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["EBT Growth"] = calculate_growth("Pretax Income", INCOME_STMT)
    else:
        INCOME_STMT.loc["Pre-Tax Income (EBT)"] = np.nan
        INCOME_STMT.loc["EBT Margin"] = np.nan
        INCOME_STMT.loc["EBT Growth"] = np.nan

    # --- TAX DATA ---
    # Income Tax
    INCOME_STMT.loc["Income Tax"] = INCOME_STMT.loc["Tax Provision"] if "Tax Provision" in INCOME_STMT.index else np.nan
    # Effective Tax Rate
    INCOME_STMT.loc["Effective Tax Rate"] = INCOME_STMT.loc["Tax Rate For Calcs"] if "Tax Rate For Calcs" in INCOME_STMT.index else np.nan

    # --- NET INCOME DATA ---
    # Net Operating Profit After Tax (NOPAT)
    if "Operating Income" in INCOME_STMT.index and "Tax Rate For Calcs" in INCOME_STMT.index:
        INCOME_STMT.loc["Net Operating Profit After Tax (NOPAT)"] = INCOME_STMT.loc["Operating Income"] * (1 - INCOME_STMT.loc["Tax Rate For Calcs"])
    else:
        INCOME_STMT.loc["Net Operating Profit After Tax (NOPAT)"] = np.nan
    # Net Income
    if "Net Income" in INCOME_STMT.index:
        INCOME_STMT.loc["Net Income"] = INCOME_STMT.loc["Net Income"]
        INCOME_STMT.loc["Net Income Margin"] = INCOME_STMT.loc["Net Income"] / INCOME_STMT.loc["Total Revenue"]
        INCOME_STMT.loc["Net Income Growth"] = calculate_growth("Net Income", INCOME_STMT)
    else:
        INCOME_STMT.loc["Net Income"] = np.nan
        INCOME_STMT.loc["Net Income Margin"] = np.nan
        INCOME_STMT.loc["Net Income Growth"] = np.nan
    # Net Income After Extraordinaries & Discontinued Operations
    INCOME_STMT.loc["Net Income after Extraordinaries & Discontinued Operations"] = INCOME_STMT.loc["Net Income From Continuing And Discontinued Operation"] if "Net Income From Continuing And Discontinued Operation" in INCOME_STMT.index else np.nan
    # Preferred Dividends
    INCOME_STMT.loc["Preferred Dividends"] = INCOME_STMT.loc["Preferred Stock Dividends"] if "Preferred Stock Dividends" in INCOME_STMT.index else np.nan
    # Net Income Available to Common Shareholders
    INCOME_STMT.loc["Net Income Available to Common Shareholders"] = INCOME_STMT.loc["Net Income Common Stockholders"] if "Net Income Common Stockholders" in INCOME_STMT.index else np.nan

    # --- EARNINGS PER SHARE DATA ---
    # Basic EPS
    if "Basic EPS" in INCOME_STMT.index and "Basic Average Shares" in INCOME_STMT.index:
        INCOME_STMT.loc["Basic EPS"] = INCOME_STMT.loc["Basic EPS"]
        INCOME_STMT.loc["Basic EPS Growth"] = calculate_growth("Basic EPS", INCOME_STMT)
        INCOME_STMT.loc["Basic Average Shares"] = INCOME_STMT.loc["Basic Average Shares"]
    else:
        INCOME_STMT.loc["Basic EPS"] = np.nan
        INCOME_STMT.loc["Basic EPS Growth"] = np.nan
        INCOME_STMT.loc["Basic Average Shares"] = np.nan
    # Diluted EPS
    if "Diluted EPS" in INCOME_STMT.index and "Diluted Average Shares" in INCOME_STMT.index:
        INCOME_STMT.loc["Diluted EPS"] = INCOME_STMT.loc["Diluted EPS"]
        INCOME_STMT.loc["Diluted EPS Growth"] = calculate_growth("Diluted EPS", INCOME_STMT)
        INCOME_STMT.loc["Diluted Average Shares"] = INCOME_STMT.loc["Diluted Average Shares"]
    else:
        INCOME_STMT.loc["Diluted EPS"] = np.nan
        INCOME_STMT.loc["Diluted EPS Growth"] = np.nan
        INCOME_STMT.loc["Diluted Average Shares"] = np.nan

    income_stmt_essentials = INCOME_STMT.loc[[
        "Revenue",
        "Revenue Growth",
        "Cost Of Goods Sold (COGS)",
        "COGS % of Sales",
        "COGS Growth",
        "Gross Profit",
        "Gross Profit Margin",
        "Gross Profit Growth",
        "Depreciation And Amortization (D&A)",
        "D&A % of Sales",
        "Selling General And Administration (SG&A)",
        "SG&A % of Sales",
        "SG&A Growth",
        "Research And Development (R&D)",
        "R&D % of Sales",
        "Total Operating Expense",
        "Total Operating Expense % of Sales",
        "Total Operating Expense Growth",
        "Operating Earnings (EBIT)",
        "EBIT Margin",
        "EBIT Growth",
        "EBITDA",
        "EBITDA Margin",
        "EBITDA Growth",
        "Non-Operating Income/Expense",
        "Non-Operating Interest Income",
        "Non-Operating Interest Expense",
        "Earnings From Equity Interest (Pre-Tax)",
        "Pre-Tax Income (EBT)",
        "EBT Margin",
        "EBT Growth",
        "Income Tax",
        "Effective Tax Rate",
        "Net Operating Profit After Tax (NOPAT)",
        "Net Income",
        "Net Income Margin",
        "Net Income Growth",
        "Net Income after Extraordinaries & Discontinued Operations",
        "Preferred Dividends",
        "Net Income Available to Common Shareholders",
        "Basic EPS",
        "Basic EPS Growth",
        "Basic Average Shares",
        "Diluted EPS",
        "Diluted EPS Growth",
        "Diluted Average Shares"
    ]].copy()

    return {"Essential Data": income_stmt_essentials, "Keywords": keywords}

# Function to format the income statement data that was parsed and ensures that it is displayed nicely with units in the front-end
def format_income_stmt(income_stmt_essentials):
    quantity_rows = ["Basic Average Shares", "Diluted Average Shares"]
    pershare_rows = ["Basic EPS", "Diluted EPS"]
    percentage_rows = [
        "Revenue Growth",
        "COGS % of Sales",
        "COGS Growth",
        "Gross Profit Margin",
        "Gross Profit Growth",
        "D&A % of Sales",
        "SG&A % of Sales",
        "SG&A Growth",
        "R&D % of Sales",
        "Total Operating Expense % of Sales",
        "Total Operating Expense Growth",
        "EBIT Margin",
        "EBIT Growth",
        "EBITDA Margin",
        "EBITDA Growth",
        "EBT Margin",
        "EBT Growth",
        "Effective Tax Rate",
        "Net Income Margin",
        "Net Income Growth",
        "Basic EPS Growth",
        "Diluted EPS Growth"
    ]

    formatted_income_stmt_essentials = income_stmt_essentials.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows,
        quantity_rows=quantity_rows,
        pershare_rows=pershare_rows
    )

    statement_structure = {
        "Revenue Data": [ #0
            "Revenue", #1
            "Revenue Growth" #2
        ],
        "Cost of Revenue Data": [ #3
            "Cost Of Goods Sold (COGS)", #4
            "COGS % of Sales", #5
            "COGS Growth" #6
        ],
        "Gross Profit Data": [ #7
            "Gross Profit", #8
            "Gross Profit Margin", #9
            "Gross Profit Growth" #10
        ],
        "Operating Expenses Data": [ #11
            "Depreciation And Amortization (D&A)", #12
            "D&A % of Sales", #13
            "Selling General And Administration (SG&A)", #14
            "SG&A % of Sales", #15
            "SG&A Growth", #16
            "Research And Development (R&D)", #17
            "R&D % of Sales", #18
            "Total Operating Expense", #19
            "Total Operating Expense % of Sales", #20
            "Total Operating Expense Growth" #21
        ],
        "Operating Earnings (EBIT) and EBITDA Data": [ #22
            "Operating Earnings (EBIT)", #23
            "EBIT Margin", #24
            "EBIT Growth", #25
            "EBITDA", #26
            "EBITDA Margin", #27
            "EBITDA Growth" #28
        ],
        "Other Income and Expenses Data": [ #29
            "Non-Operating Income/Expense", #30
            "Non-Operating Interest Income", #31
            "Non-Operating Interest Expense", #32
            "Earnings From Equity Interest (Pre-Tax)" #33
        ],
        "Pre-Tax Income (EBT) Data": [ #34
            "Pre-Tax Income (EBT)", #35
            "EBT Margin", #36
            "EBT Growth" #37
        ],
        "Tax Data": [ #38
            "Income Tax", #39
            "Effective Tax Rate" #40
        ],
        "Net Income Data": [ #41
            "Net Operating Profit After Tax (NOPAT)", #42
            "Net Income", #43
            "Net Income Margin", #44
            "Net Income Growth", #45
            "Net Income after Extraordinaries & Discontinued Operations", #46
            "Preferred Dividends", #47
            "Net Income Available to Common Shareholders" #48
        ],
        "Earnings Per Share Data": [ #49
            "Basic EPS", #50
            "Basic EPS Growth", #51
            "Basic Average Shares", #52
            "Diluted EPS", #53
            "Diluted EPS Growth", #54
            "Diluted Average Shares" #55
        ]
    }

    formatted_income_stmt_essentials = format_financial_statement(
        formatted_income_stmt_essentials,
        statement_structure,
        formatted_income_stmt_essentials.columns
    )

    # Styling specific rows of the formatted dataframe
    formatted_income_stmt_essentials = formatted_income_stmt_essentials.style.apply(
        lambda row: [conditional_highlight_positive(val, 100) for val in row],
        axis=1,
        subset=([5, 15, 20], slice(None))
    ).apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([2, 8, 10, 23, 25, 26, 28, 35, 37, 42, 43, 45, 46, 48, 50, 51, 53, 54], slice(None))
    )

    return formatted_income_stmt_essentials

# Function to parse the Balance Sheet Data from yfinance and returns a dictionary of dataframes containing essential data and the keywords for web-scraping error checking
def parse_balance_sheet(BALANCE_SHEET):
    # Important Key Words listed in yfinance Balance Sheet method that are required
    keywords = [
        "Cash And Cash Equivalents", "Other Short Term Investments", "Cash Cash Equivalents And Short Term Investments", "Total Assets", "Accounts Receivable",
        "Other Receivables", "Receivables", "Inventory", "Other Current Assets", "Current Assets", "Net PPE", "Investments And Advances", "Non Current Deferred Assets",
        "Other Non Current Assets", "Total Non Current Assets", "Total Assets", "Current Debt", "Total Liabilities Net Minority Interest", "Accounts Payable",
        "Income Tax Payable", "Payables", "Other Current Liabilities", "Current Liabilities", "Long Term Debt", "Other Non Current Liabilities",
        "Total Non Current Liabilities Net Minority Interest", "Preferred Stock", "Common Stock", "Capital Stock", "Additional Paid In Capital", "Retained Earnings",
        "Treasury Stock", "Other Equity Adjustments", "Minority Interest", "Total Equity Gross Minority Interest"
    ]

    # ---- ASSETS DATA ----
    # --- CURRENT ASSETS ---
    # Cash and Cash Equivalents
    BALANCE_SHEET.loc["Cash And Cash Equivalents"] = BALANCE_SHEET.loc["Cash And Cash Equivalents"] if "Cash And Cash Equivalents" in BALANCE_SHEET.index else np.nan
    # Short Term Investments
    BALANCE_SHEET.loc["Short Term Investments"] = BALANCE_SHEET.loc["Other Short Term Investments"] if "Other Short Term Investments" in BALANCE_SHEET.index else np.nan
    # Cash & Short Term Investments
    if "Cash Cash Equivalents And Short Term Investments" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Cash & Short Term Investments"] = BALANCE_SHEET.loc["Cash Cash Equivalents And Short Term Investments"]
        BALANCE_SHEET.loc["Cash & Short Term Investments Growth"] = calculate_growth("Cash Cash Equivalents And Short Term Investments", BALANCE_SHEET)
        BALANCE_SHEET.loc["Cash & Short Term Investments % of Total Assets"] = BALANCE_SHEET.loc["Cash Cash Equivalents And Short Term Investments"] / BALANCE_SHEET.loc["Total Assets"] if "Total Assets" in BALANCE_SHEET.index else np.nan
    else:
        BALANCE_SHEET.loc["Cash & Short Term Investments"] = np.nan
        BALANCE_SHEET.loc["Cash & Short Term Investments Growth"] = np.nan
        BALANCE_SHEET.loc["Cash & Short Term Investments % of Total Assets"] = np.nan
    # Accounts Receivable
    if "Accounts Receivable" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Accounts Receivable"] = BALANCE_SHEET.loc["Accounts Receivable"]
        BALANCE_SHEET.loc["Accounts Receivable Growth"] = calculate_growth("Accounts Receivable", BALANCE_SHEET)
    else:
        BALANCE_SHEET.loc["Accounts Receivable"] = np.nan
        BALANCE_SHEET.loc["Accounts Receivable Growth"] = np.nan
    # Other Receivables
    BALANCE_SHEET.loc["Other Receivables"] = BALANCE_SHEET.loc["Other Receivables"] if "Other Receivables" in BALANCE_SHEET.index else np.nan
    # Total Receivables
    BALANCE_SHEET.loc["Total Receivables"] = BALANCE_SHEET.loc["Receivables"] if "Receivables" in BALANCE_SHEET.index else np.nan
    # Inventory
    BALANCE_SHEET.loc["Inventory"] = BALANCE_SHEET.loc["Inventory"] if "Inventory" in BALANCE_SHEET.index else np.nan
    # Other Current Assets
    BALANCE_SHEET.loc["Other Current Assets"] = BALANCE_SHEET.loc["Other Current Assets"] if "Other Current Assets" in BALANCE_SHEET.index else np.nan
    # Total Current Assets
    BALANCE_SHEET.loc["Total Current Assets"] = BALANCE_SHEET.loc["Current Assets"] if "Current Assets" in BALANCE_SHEET.index else np.nan

    # --- NON-CURRENT ASSETS ---
    # Net Plant, Property And Equipment (PPE)
    BALANCE_SHEET.loc["Net Plant, Property And Equipment (PPE)"] = BALANCE_SHEET.loc["Net PPE"] if "Net PPE" in BALANCE_SHEET.index else np.nan
    # Total Investments And Advances
    BALANCE_SHEET.loc["Investments And Advances"] = BALANCE_SHEET.loc["Investments And Advances"] if "Investments And Advances" in BALANCE_SHEET.index else np.nan
    # Non-Current Deferred Assets
    BALANCE_SHEET.loc["Non-Current Deferred Assets"] = BALANCE_SHEET.loc["Non Current Deferred Assets"] if "Non Current Deferred Assets" in BALANCE_SHEET.index else np.nan
    # Other Non-Current Assets
    BALANCE_SHEET.loc["Other Non-Current Assets"] = BALANCE_SHEET.loc["Other Non Current Assets"] if "Other Non Current Assets" in BALANCE_SHEET.index else np.nan
    # Total Non-Current Assets
    BALANCE_SHEET.loc["Total Non-Current Assets"] = BALANCE_SHEET.loc["Total Non Current Assets"] if "Total Non Current Assets" in BALANCE_SHEET.index else np.nan

    # --- TOTAL ASSETS ---
    # Total Assets
    if "Total Assets" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Total Assets"] = BALANCE_SHEET.loc["Total Assets"]
        BALANCE_SHEET.loc["Total Assets Growth"] = calculate_growth("Total Assets", BALANCE_SHEET)
    else:
        BALANCE_SHEET.loc["Total Assets"] = np.nan
        BALANCE_SHEET.loc["Total Assets Growth"] = np.nan

    # ---- LIABILITIES DATA ----
    # --- CURRENT LIABILITIES ---
    # Current Debt
    if "Current Debt" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Current Debt"] = BALANCE_SHEET.loc["Current Debt"]
        BALANCE_SHEET.loc["Current Debt Growth"] = calculate_growth("Current Debt", BALANCE_SHEET)
        BALANCE_SHEET.loc["Current Debt % of Total Liabilities"] = BALANCE_SHEET.loc["Current Debt"] / BALANCE_SHEET.loc["Total Liabilities Net Minority Interest"] if "Total Liabilities Net Minority Interest" in BALANCE_SHEET.index else np.nan
    else:
        BALANCE_SHEET.loc["Current Debt"] = np.nan
        BALANCE_SHEET.loc["Current Debt Growth"] = np.nan
        BALANCE_SHEET.loc["Current Debt % of Total Liabilities"] = np.nan
    # Accounts Payable
    if "Accounts Payable" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Accounts Payable"] = BALANCE_SHEET.loc["Accounts Payable"]
        BALANCE_SHEET.loc["Accounts Payable Growth"] = calculate_growth("Accounts Payable", BALANCE_SHEET)
    else:
        BALANCE_SHEET.loc["Accounts Payable"] = np.nan
        BALANCE_SHEET.loc["Accounts Payable Growth"] = np.nan
    # Income Tax Payable
    BALANCE_SHEET.loc["Income Tax Payable"] = BALANCE_SHEET.loc["Income Tax Payable"] if "Income Tax Payable" in BALANCE_SHEET.index else np.nan
    # Total Payables
    BALANCE_SHEET.loc["Total Payables"] = BALANCE_SHEET.loc["Payables"] if "Payables" in BALANCE_SHEET.index else np.nan
    # Other Current Liabilities
    BALANCE_SHEET.loc["Other Current Liabilities"] = BALANCE_SHEET.loc["Other Current Liabilities"] if "Other Current Liabilities" in BALANCE_SHEET.index else np.nan
    # Total Current Liabilities
    BALANCE_SHEET.loc["Total Current Liabilities"] = BALANCE_SHEET.loc["Current Liabilities"] if "Current Liabilities" in BALANCE_SHEET.index else np.nan

    # --- NON-CURRENT LIABILITIES ---
    # Long-Term Debt
    BALANCE_SHEET.loc["Long-Term Debt"] = BALANCE_SHEET.loc["Long Term Debt"] if "Long Term Debt" in BALANCE_SHEET.index else np.nan
    # Other Non-Current Liabilities
    BALANCE_SHEET.loc["Other Non-Current Liabilities"] = BALANCE_SHEET.loc["Other Non Current Liabilities"] if "Other Non Current Liabilities" in BALANCE_SHEET.index else np.nan
    # Total Non-Current Liabilities
    BALANCE_SHEET.loc["Total Non-Current Liabilities"] = BALANCE_SHEET.loc["Total Non Current Liabilities Net Minority Interest"] if "Total Non Current Liabilities Net Minority Interest" in BALANCE_SHEET.index else np.nan

    # --- TOTAL LIABILITIES ---
    # Total Liabilities
    if "Total Liabilities Net Minority Interest" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Total Liabilities"] = BALANCE_SHEET.loc["Total Liabilities Net Minority Interest"]
        BALANCE_SHEET.loc["Total Liabilities % of Total Assets"] = BALANCE_SHEET.loc["Total Liabilities Net Minority Interest"] / BALANCE_SHEET.loc["Total Assets"] if "Total Assets" in BALANCE_SHEET.index else np.nan
    else:
        BALANCE_SHEET.loc["Total Liabilities"] = np.nan
        BALANCE_SHEET.loc["Total Liabilities % of Total Assets"] = np.nan

    # ---- SHAREHOLDERS' EQUITY ----
    # --- CAPITAL RAISED DATA ---
    # Preferred Stock
    BALANCE_SHEET.loc["Preferred Stock"] = BALANCE_SHEET.loc["Preferred Stock"] if "Preferred Stock" in BALANCE_SHEET.index else np.nan
    # Common Stock
    BALANCE_SHEET.loc["Common Stock"] = BALANCE_SHEET.loc["Common Stock"] if "Common Stock" in BALANCE_SHEET.index else np.nan
    # Total Capital Raised
    BALANCE_SHEET.loc["Total Capital Stock"] = BALANCE_SHEET.loc["Capital Stock"] if "Capital Stock" in BALANCE_SHEET.index else np.nan
    # Additional Paid In Capital
    BALANCE_SHEET.loc["Additional Paid-In Capital"] = BALANCE_SHEET.loc["Additional Paid In Capital"] if "Additional Paid In Capital" in BALANCE_SHEET.index else np.nan

    # --- PROFIT RETAINED DATA ---
    # Retained Earnings
    if "Retained Earnings" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Retained Earnings"] = BALANCE_SHEET.loc["Retained Earnings"]
        BALANCE_SHEET.loc["Retained Earnings Growth"] = calculate_growth("Retained Earnings", BALANCE_SHEET)
    else:
        BALANCE_SHEET.loc["Retained Earnings"] = np.nan
        BALANCE_SHEET.loc["Retained Earnings Growth"] = np.nan
    # Treasury Stock
    BALANCE_SHEET.loc["Treasury Stock"] = BALANCE_SHEET.loc["Treasury Stock"] if "Treasury Stock" in BALANCE_SHEET.index else np.nan
    # Other Equity Adjustments
    BALANCE_SHEET.loc["Other Equity Adjustments"] = BALANCE_SHEET.loc["Other Equity Adjustments"] if "Other Equity Adjustments" in BALANCE_SHEET.index else np.nan

    # --- TOTAL SHAREHOLDERS' EQUITY ---
    # Minority Interest
    BALANCE_SHEET.loc["Minority Interest"] = BALANCE_SHEET.loc["Minority Interest"] if "Minority Interest" in BALANCE_SHEET.index else np.nan
    # Total Shareholders' Equity
    if "Total Equity Gross Minority Interest" in BALANCE_SHEET.index:
        BALANCE_SHEET.loc["Total Shareholders' Equity"] = BALANCE_SHEET.loc["Total Equity Gross Minority Interest"]
        BALANCE_SHEET.loc["Total Shareholders' Equity Growth"] = calculate_growth("Total Equity Gross Minority Interest", BALANCE_SHEET)
        BALANCE_SHEET.loc["Total Shareholders' Equity % of Total Assets"] = BALANCE_SHEET.loc["Total Equity Gross Minority Interest"] / BALANCE_SHEET.loc["Total Assets"] if "Total Assets" in BALANCE_SHEET.index else np.nan
    else:
        BALANCE_SHEET.loc["Total Shareholders' Equity"] = np.nan
        BALANCE_SHEET.loc["Total Shareholders' Equity Growth"] = np.nan
        BALANCE_SHEET.loc["Total Shareholders' Equity % of Total Assets"] = np.nan

    balance_sheet_essentials = BALANCE_SHEET.loc[[
        "Cash And Cash Equivalents",
        "Short Term Investments",
        "Cash & Short Term Investments",
        "Cash & Short Term Investments Growth",
        "Cash & Short Term Investments % of Total Assets",
        "Accounts Receivable",
        "Accounts Receivable Growth",
        "Other Receivables",
        "Total Receivables",
        "Inventory",
        "Other Current Assets",
        "Total Current Assets",
        "Net Plant, Property And Equipment (PPE)",
        "Investments And Advances",
        "Non-Current Deferred Assets",
        "Other Non-Current Assets",
        "Total Non-Current Assets",
        "Total Assets",
        "Total Assets Growth",
        "Current Debt",
        "Current Debt Growth",
        "Current Debt % of Total Liabilities",
        "Accounts Payable",
        "Accounts Payable Growth",
        "Income Tax Payable",
        "Total Payables",
        "Other Current Liabilities",
        "Total Current Liabilities",
        "Long-Term Debt",
        "Other Non-Current Liabilities",
        "Total Non-Current Liabilities",
        "Total Liabilities",
        "Total Liabilities % of Total Assets",
        "Preferred Stock",
        "Common Stock",
        "Total Capital Stock",
        "Additional Paid-In Capital",
        "Retained Earnings",
        "Retained Earnings Growth",
        "Treasury Stock",
        "Other Equity Adjustments",
        "Minority Interest",
        "Total Shareholders' Equity",
        "Total Shareholders' Equity Growth",
        "Total Shareholders' Equity % of Total Assets"
    ]].copy()

    return {"Essential Data": balance_sheet_essentials, "Keywords": keywords}

# Function to format the balance sheet data that was parsed and ensures that it is displayed nicely with units in the front-end
def format_balance_sheet(balance_sheet_essentials):
    percentage_rows = [
        "Cash & Short Term Investments Growth",
        "Cash & Short Term Investments % of Total Assets",
        "Accounts Receivable Growth",
        "Total Assets Growth",
        "Current Debt Growth",
        "Current Debt % of Total Liabilities",
        "Accounts Payable Growth",
        "Total Liabilities % of Total Assets",
        "Retained Earnings Growth",
        "Total Shareholders' Equity Growth",
        "Total Shareholders' Equity % of Total Assets"
    ]

    formatted_balance_sheet_essentials = balance_sheet_essentials.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows
    )

    statement_structure = {
        "Current Assets": [ #0
            "Cash And Cash Equivalents", #1
            "Short Term Investments", #2
            "Cash & Short Term Investments", #3
            "Cash & Short Term Investments Growth", #4
            "Cash & Short Term Investments % of Total Assets", #5
            "Accounts Receivable", #6
            "Accounts Receivable Growth", #7
            "Other Receivables", #8
            "Total Receivables", #9
            "Inventory", #10
            "Other Current Assets", #11
            "Total Current Assets" #12
        ],
        "Non-Current Assets": [ #13
            "Net Plant, Property And Equipment (PPE)", #14
            "Investments And Advances", #15
            "Non-Current Deferred Assets", #16
            "Other Non-Current Assets", #17
            "Total Non-Current Assets" #18
        ],
        "Total Assets": [ #19
            "Total Assets", #20
            "Total Assets Growth" #21
        ],
        "Current Liabilities": [ #22
            "Current Debt", #23
            "Current Debt Growth", #24
            "Current Debt % of Total Liabilities", #25
            "Accounts Payable", #26
            "Accounts Payable Growth", #27
            "Income Tax Payable", #28
            "Total Payables", #29
            "Other Current Liabilities", #30
            "Total Current Liabilities" #31
        ],
        "Non-Current Liabilities": [ #32
            "Long-Term Debt", #33
            "Other Non-Current Liabilities", #34
            "Total Non-Current Liabilities" #35
        ],
        "Total Liabilities": [ #36
            "Total Liabilities", #37
            "Total Liabilities % of Total Assets" #38
        ],
        "Capital Raised": [ #39
            "Preferred Stock", #40
            "Common Stock", #41
            "Total Capital Stock", #42
            "Additional Paid-In Capital" #43
        ],
        "Profit Retained": [ #44
            "Retained Earnings", #45
            "Retained Earnings Growth", #46
            "Treasury Stock", #47
            "Other Equity Adjustments" #48
        ],
        "Shareholders' Equity": [ #49
            "Minority Interest", #50
            "Total Shareholders' Equity", #51
            "Total Shareholders' Equity Growth", #52
            "Total Shareholders' Equity % of Total Assets" #53
        ]
    }

    formatted_balance_sheet_essentials = format_financial_statement(
        formatted_balance_sheet_essentials,
        statement_structure,
        formatted_balance_sheet_essentials.columns
    )

    # Styling specific rows of the formatted dataframe
    formatted_balance_sheet_essentials = formatted_balance_sheet_essentials.style.apply(
        lambda row: [conditional_highlight_positive(val, 0) for val in row],
        axis=1,
        subset=([24, 27], slice(None))
    ).apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([4, 7, 21, 45, 46], slice(None))
    )

    return formatted_balance_sheet_essentials

# Function to parse the Cash Flow Statement Data from yfinance and returns a dictionary of dataframes containing essential data and the keywords for web-scraping error checking
def parse_cashflow_stmt(CASHFLOW_STMT):
    # Important Key Words listed in yfinance Cash Flow Statement method that are required
    keywords = [
        "Net Income From Continuing Operations", "Depreciation Amortization Depletion", "Deferred Tax", "Stock Based Compensation", "Other Non Cash Items", "Change In Working Capital",
        "Operating Cash Flow", "Purchase Of PPE", "Net PPE Purchase And Sale", "Net Intangibles Purchase And Sale", "Capital Expenditure", "Net Business Purchase And Sale",
        "Net Investment Purchase And Sale", "Net Other Investing Changes", "Investing Cash Flow", "Cash Dividends Paid", "Net Common Stock Issuance", "Net Issuance Payments Of Debt",
        "Net Other Financing Charges", "Financing Cash Flow", "Changes In Cash", "Free Cash Flow"
    ]
    
    # --- OPERATING ACTIVITIES DATA ---
    # Net Income From Continuing Operations
    if "Net Income From Continuing Operations" in CASHFLOW_STMT.index:
        CASHFLOW_STMT.loc["Net Income From Continuing Operations"] = CASHFLOW_STMT.loc["Net Income From Continuing Operations"]
        CASHFLOW_STMT.loc["Net Income Growth"] = calculate_growth("Net Income From Continuing Operations", CASHFLOW_STMT)
    else:
        CASHFLOW_STMT.loc["Net Income From Continuing Operations"] = np.nan
        CASHFLOW_STMT.loc["Net Income Growth"] = np.nan
    # Depreciation, Depletion And Amortization
    CASHFLOW_STMT.loc["Depreciation, Depletion And Amortization (DD&A)"] = CASHFLOW_STMT.loc["Depreciation Amortization Depletion"] if "Depreciation Amortization Depletion" in CASHFLOW_STMT.index else np.nan
    # Deferred Taxes
    CASHFLOW_STMT.loc["Deferred Taxes"] = CASHFLOW_STMT.loc["Deferred Tax"] if "Deferred Tax" in CASHFLOW_STMT.index else np.nan
    # Stock Based Compensation
    CASHFLOW_STMT.loc["Stock Based Compensation"] = CASHFLOW_STMT.loc["Stock Based Compensation"] if "Stock Based Compensation" in CASHFLOW_STMT.index else np.nan
    # Other Non-Cash Items
    CASHFLOW_STMT.loc["Other Non-Cash Items"] = CASHFLOW_STMT.loc["Other Non Cash Items"] if "Other Non Cash Items" in CASHFLOW_STMT.index else np.nan
    # Change In Working Capital
    CASHFLOW_STMT.loc["Change In Working Capital"] = CASHFLOW_STMT.loc["Change In Working Capital"] if "Change In Working Capital" in CASHFLOW_STMT.index else np.nan
    # Net Operating Cash Flow
    if "Operating Cash Flow" in CASHFLOW_STMT.index:
        CASHFLOW_STMT.loc["Net Operating Cash Flow"] = CASHFLOW_STMT.loc["Operating Cash Flow"]
        CASHFLOW_STMT.loc["Net Operating Cash Flow Growth"] = calculate_growth("Operating Cash Flow", CASHFLOW_STMT)
    else:
        CASHFLOW_STMT.loc["Net Operating Cash Flow"] = np.nan
        CASHFLOW_STMT.loc["Net Operating Cash Flow Growth"] = np.nan

    # --- INVESTING ACTIVITIES DATA ---
    # Capital Expenditure on Fixed Assets (PPE)
    CASHFLOW_STMT.loc["Capital Expenditures on Fixed Assets (PPE)"] = CASHFLOW_STMT.loc["Purchase Of PPE"] if "Purchase Of PPE" in CASHFLOW_STMT.index else np.nan
    # Net Capital Expenditures on Fixed Assets (PPE)
    if "Net PPE Purchase And Sale" in CASHFLOW_STMT.index:
        CASHFLOW_STMT.loc["Net Capital Expenditures on Fixed Assets (PPE)"] = CASHFLOW_STMT.loc["Net PPE Purchase And Sale"]
        CASHFLOW_STMT.loc["Net Capital Expenditures on PPE Growth"] = calculate_growth("Net PPE Purchase And Sale", CASHFLOW_STMT)
    else:
        CASHFLOW_STMT.loc["Net Capital Expenditures on Fixed Assets (PPE)"] = np.nan
        CASHFLOW_STMT.loc["Net Capital Expenditures on PPE Growth"] = np.nan
    # Net Capital Expenditures on Intangible Assets
    CASHFLOW_STMT.loc["Net Capital Expenditures on Intangible Assets"] = CASHFLOW_STMT.loc["Net Intangibles Purchase And Sale"] if "Net Intangibles Purchase And Sale" in CASHFLOW_STMT.index else np.nan
    # Total Capital Expenditures
    CASHFLOW_STMT.loc["Total Capital Expenditures"] = CASHFLOW_STMT.loc["Capital Expenditure"] if "Capital Expenditure" in CASHFLOW_STMT.index else np.nan
    # Net Purchase And Sale of Businesses
    CASHFLOW_STMT.loc["Net Purchase And Sale of Businesses"] = CASHFLOW_STMT.loc["Net Business Purchase And Sale"] if "Net Business Purchase And Sale" in CASHFLOW_STMT.index else np.nan
    # Net Purchase And Sale of Investments
    CASHFLOW_STMT.loc["Net Purchase And Sale of Investments"] = CASHFLOW_STMT.loc["Net Investment Purchase And Sale"] if "Net Investment Purchase And Sale" in CASHFLOW_STMT.index else np.nan
    # Net Other Investing Changes
    CASHFLOW_STMT.loc["Net Other Investing Changes"] = CASHFLOW_STMT.loc["Net Other Investing Changes"] if "Net Other Investing Changes" in CASHFLOW_STMT.index else np.nan
    # Net Investing Cash Flow
    if "Investing Cash Flow" in CASHFLOW_STMT.index:
        CASHFLOW_STMT.loc["Net Investing Cash Flow"] = CASHFLOW_STMT.loc["Investing Cash Flow"]
        CASHFLOW_STMT.loc["Net Investing Cash Flow Growth"] = calculate_growth("Investing Cash Flow", CASHFLOW_STMT)
    else:
        CASHFLOW_STMT.loc["Net Investing Cash Flow"] = np.nan
        CASHFLOW_STMT.loc["Net Investing Cash Flow Growth"] = np.nan

    # --- FINANCING ACTIVITIES DATA ---
    # Total Cash Dividends Paid
    CASHFLOW_STMT.loc["Total Cash Dividends Paid"] = CASHFLOW_STMT.loc["Cash Dividends Paid"] if "Cash Dividends Paid" in CASHFLOW_STMT.index else np.nan
    # Net Repurchase And Issuance of Capital Stock
    CASHFLOW_STMT.loc["Net Repurchase And Issuance of Capital Stock"] = CASHFLOW_STMT.loc["Net Common Stock Issuance"] if "Net Common Stock Issuance" in CASHFLOW_STMT.index else np.nan
    # Net Issuance And Reduction of Debt
    CASHFLOW_STMT.loc["Net Issuance And Payments of Debt"] = CASHFLOW_STMT.loc["Net Issuance Payments Of Debt"] if "Net Issuance Payments Of Debt" in CASHFLOW_STMT.index else np.nan
    # Net Other Financing Charges
    CASHFLOW_STMT.loc["Net Other Financing Charges"] = CASHFLOW_STMT.loc["Net Other Financing Charges"] if "Net Other Financing Charges" in CASHFLOW_STMT.index else np.nan
    # Net Financing Cash Flow
    if "Financing Cash Flow" in CASHFLOW_STMT.index:
        CASHFLOW_STMT.loc["Net Financing Cash Flow"] = CASHFLOW_STMT.loc["Financing Cash Flow"]
        CASHFLOW_STMT.loc["Net Financing Cash Flow Growth"] = calculate_growth("Financing Cash Flow", CASHFLOW_STMT)
    else:
        CASHFLOW_STMT.loc["Net Financing Cash Flow"] = np.nan
        CASHFLOW_STMT.loc["Net Financing Cash Flow Growth"] = np.nan

    # --- NET CHANGE IN CASH DATA ---
    # Net Change in Cash
    CASHFLOW_STMT.loc["Net Change in Cash"] = CASHFLOW_STMT.loc["Changes In Cash"] if "Changes In Cash" in CASHFLOW_STMT.index else np.nan

    # --- FREE CASH FLOW DATA ---
    # Free Cash Flow
    if "Free Cash Flow" in CASHFLOW_STMT.index:
        CASHFLOW_STMT.loc["Free Cash Flow"] = CASHFLOW_STMT.loc["Free Cash Flow"]
        CASHFLOW_STMT.loc["Free Cash Flow Growth"] = calculate_growth("Free Cash Flow", CASHFLOW_STMT)
    else:
        CASHFLOW_STMT.loc["Free Cash Flow"] = np.nan
        CASHFLOW_STMT.loc["Free Cash Flow Growth"] = np.nan

    cashflow_stmt_essentials = CASHFLOW_STMT.loc[[
        "Net Income From Continuing Operations",
        "Net Income Growth",
        "Depreciation, Depletion And Amortization (DD&A)",
        "Deferred Taxes",
        "Stock Based Compensation",
        "Other Non-Cash Items",
        "Change In Working Capital",
        "Net Operating Cash Flow",
        "Net Operating Cash Flow Growth",
        "Capital Expenditures on Fixed Assets (PPE)",
        "Net Capital Expenditures on Fixed Assets (PPE)",
        "Net Capital Expenditures on PPE Growth",
        "Net Capital Expenditures on Intangible Assets",
        "Total Capital Expenditures",
        "Net Purchase And Sale of Businesses",
        "Net Purchase And Sale of Investments",
        "Net Other Investing Changes",
        "Net Investing Cash Flow",
        "Net Investing Cash Flow Growth",
        "Total Cash Dividends Paid",
        "Net Repurchase And Issuance of Capital Stock",
        "Net Issuance And Payments of Debt",
        "Net Other Financing Charges",
        "Net Financing Cash Flow",
        "Net Financing Cash Flow Growth",
        "Net Change in Cash",
        "Free Cash Flow",
        "Free Cash Flow Growth"
    ]].copy()

    return {"Essential Data": cashflow_stmt_essentials, "Keywords": keywords}

# Function to format the cash flow statement data that was parsed and ensures that it is displayed nicely with units in the front-end
def format_cashflow_stmt(cashflow_stmt_essentials):
    percentage_rows = [
        "Net Income Growth",
        "Net Operating Cash Flow Growth",
        "Net Capital Expenditures on PPE Growth",
        "Net Investing Cash Flow Growth",
        "Net Financing Cash Flow Growth",
        "Free Cash Flow Growth"
    ]

    formatted_cashflow_stmt_essentials = cashflow_stmt_essentials.apply(
        format_row,
        axis=1,
        percentage_rows=percentage_rows
    )

    statement_structure = {
        "Operating Activities": [ #0
            "Net Income From Continuing Operations", #1
            "Net Income Growth", #2
            "Depreciation, Depletion And Amortization (DD&A)", #3
            "Deferred Taxes", #4
            "Stock Based Compensation", #5
            "Other Non-Cash Items", #6
            "Change In Working Capital", #7
            "Net Operating Cash Flow", #8
            "Net Operating Cash Flow Growth" #9
        ],
        "Investing Activities": [ #10
            "Capital Expenditures on Fixed Assets (PPE)", #11
            "Net Capital Expenditures on Fixed Assets (PPE)", #12
            "Net Capital Expenditures on PPE Growth", #13
            "Net Capital Expenditures on Intangible Assets", #14
            "Total Capital Expenditures", #15
            "Net Purchase And Sale of Businesses", #16
            "Net Purchase And Sale of Investments", #17
            "Net Other Investing Changes", #18
            "Net Investing Cash Flow", #19
            "Net Investing Cash Flow Growth" #20
        ],
        "Financing Activities": [ #21
            "Total Cash Dividends Paid", #22
            "Net Repurchase And Issuance of Capital Stock", #23
            "Net Issuance And Payments of Debt", #24
            "Net Other Financing Charges", #25
            "Net Financing Cash Flow", #26
            "Net Financing Cash Flow Growth" #27
        ],
        "Free Cash Flow Data": [ #28
            "Net Change in Cash", #29
            "Free Cash Flow", #30
            "Free Cash Flow Growth" #31
        ]
    }

    formatted_cashflow_stmt_essentials = format_financial_statement(
        formatted_cashflow_stmt_essentials,
        statement_structure,
        formatted_cashflow_stmt_essentials.columns
    )

    # Styling specific rows of the formatted dataframe
    formatted_cashflow_stmt_essentials = formatted_cashflow_stmt_essentials.style.apply(
        lambda row: [conditional_highlight_negative(val, 0) for val in row],
        axis=1,
        subset=([1, 2, 7, 8, 9, 19, 20, 26, 27, 29, 30, 31], slice(None))
    )

    return formatted_cashflow_stmt_essentials