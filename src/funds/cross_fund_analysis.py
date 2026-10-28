import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
from yfinance import ETFQuery, FundQuery
import streamlit as st
from src.shared.finance_utils import format_large_money

# Function to get the top 10 Investment Funds for its Category
def get_top_10_funds(category_funds_df):
    # Since category_funds_df is passed by reference, the following code below will also filter the category_funds_df used in the peer_analysis page
    category_funds_df = category_funds_df.loc[category_funds_df["currency"] == "USD"]

    top_10_funds = category_funds_df[[
        "symbol",
        "longName",
        "netExpenseRatio",
        "regularMarketPrice",
        "fiftyTwoWeekHigh",
        "fiftyTwoWeekLow",
        "netAssets",
        "dividendYield",
        "trailingPE",
        "priceToBook"
    ]].head(10)

    top_10_funds = top_10_funds.rename(
        columns={
            "symbol": "Ticker",
            "longName": "Fund Name",
            "regularMarketPrice": "Current Price",
            "netExpenseRatio": "Net Expense Ratio",
            "fiftyTwoWeekHigh": "52-Week High",
            "fiftyTwoWeekLow": "52-Week Low",
            "netAssets": "Net Assets",
            "dividendYield": "Dividend Yield",
            "trailingPE": "Trailing P/E Ratio",
            "priceToBook": "P/B Ratio"
        }
    ).set_index("Ticker")

    # Formatting specific columns
    for col in top_10_funds.columns:
        if col in ["Current Price", "52-Week High", "52-Week Low"]:
            top_10_funds[col] = top_10_funds[col].apply(lambda x: f"${x:,.2f}")
        elif col == "Net Assets":
            top_10_funds[col] = top_10_funds[col].apply(format_large_money)
        elif col == "Dividend Yield":
            top_10_funds[col] = top_10_funds[col].apply(lambda x: f"{x:,.2f}%")
        elif col == "Net Expense Ratio":
            top_10_funds[col] = top_10_funds[col].apply(lambda x: f"{x:,.3g}%")            

    return top_10_funds

# Cached Function to query the comparison funds and return the top 10 funds of this category
@st.cache_data(ttl=3600, show_spinner=False)
def generate_comparison_funds(fund_type, fund_category):
    try:
        if fund_type == "Mutual Fund":
            # Execute the query
            q = FundQuery('eq', ["categoryname", fund_category])
        else:
            q = ETFQuery('eq', ["categoryname", fund_category])

        response = yf.screen(q, sortField='fundnetassets', sortAsc=False)
    except Exception as e:
        st.error(f"Querying failed. Endpoint could be down or the keywords may have changed for category. Error Occured: {e} ")
        quotes_list = [] # Create an empty list
    else:
        # Extract the nested list of quotes
        quotes_list = response.get('quotes', [])
    finally:
        # Convert directly to a pandas DataFrame
        category_funds_df = pd.DataFrame(quotes_list)

        # Checking if the query returns an empty dataframe
        if category_funds_df.empty:
            top_10_funds = pd.DataFrame() # Initializing an empty dataframe
        else:
            # Getting the Top 10 Funds for the category
            top_10_funds = get_top_10_funds(category_funds_df)
    
    return top_10_funds

# Cached Function to get the Net Expense Ratio Comparison Chart
@st.cache_data(ttl=3600, show_spinner=False)
def get_net_expense_ratio_chart(top_10_funds, fund_ticker_input, net_expense_ratio, category_average_expense_ratio):
    net_expense_ratio_series = top_10_funds["Net Expense Ratio"]

    # Making sure to include the fund ticker if it is not in the top 10 list of funds for the category
    if fund_ticker_input not in net_expense_ratio_series:
        net_expense_ratio_series[fund_ticker_input] = net_expense_ratio

    # Sorting and changing the string to float values
    numeric_values = net_expense_ratio_series.str.replace("%", "").astype(float)
    numeric_values = numeric_values.sort_values(ascending=True)
    avg_expense_numeric = float(category_average_expense_ratio.replace("%", ""))

    # Realign the original string series to match the sorted order
    sorted_strings = net_expense_ratio_series.loc[numeric_values.index]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=numeric_values,               # Numeric float values for bar lengths
            y=numeric_values.index,         # Tickers from the Series index
            orientation="h",                # Horizontal bar chart
            text=sorted_strings,            # Original string with % for labels
            textposition="auto",
            hovertemplate="<b>Ticker:</b> %{y}<br>" + "<b>Net Expense Ratio:</b> %{text}<extra></extra>"
        )
    )

    fig.add_vline(
        x=avg_expense_numeric,        # Where to place the line on the X-axis
        line_width=2,
        line_dash="dash",             # Makes it a dashed line
        line_color="crimson",         # Stands out against blue bars
        annotation_text=f"<b> Category Average:</b> {category_average_expense_ratio}", # Uses your original string in the label
        annotation_position="bottom right",
        annotation_font=dict(color="crimson", size=12)
    )

    fig.update_layout(
        xaxis_title="Net Expense Ratio (%)",
        template="plotly_white",
        margin=dict(t=10, b=0, l=40, r=0) # Adjust 't' (top) down to 10 if no ttitle
    )

    return fig

# Cached Function to get the Return Comparison Chart
@st.cache_data(ttl=3600, show_spinner=False)
def get_return_comparison_chart(top_10_funds, fund_ticker_input):
    top_10_tickers = top_10_funds.index.to_list()

    # Adding the current stock ticker if it is not in the list of top 10 funds
    if fund_ticker_input not in top_10_tickers:
        top_10_tickers.append(fund_ticker_input)

    # Initialize bulk Tickers object
    tickers_obj = yf.Tickers(" ".join(top_10_tickers))

    metrics_to_collect = {
        "ytdReturn": "YTD Return",
        "trailingThreeMonthReturns": "3-Month Return",
        "threeYearAverageReturn": "3-Year CAGR Return",
        "fiveYearAverageReturn": "5-Year CAGR Return"
    }

    # Helper function to process a single ticker and captures tickets_obj & metrics_to_collect from parent scope
    def fetch_ticker_metrics(symbol):
        # tickers_obj will be defined later, tickers_obj cannot be used as an argument because this function will be iterated using ThreadPoolExecutor
        # and the tickers_obj cannot be iterated
        ticker_item = tickers_obj.tickers[symbol]
        info = ticker_item.info
        
        row = {"Ticker": symbol}
        for key, display_name in metrics_to_collect.items():
            if key in ["ytdReturn", "trailingThreeMonthReturns"]:
                val = info.get(key, np.nan) # Display as it is because the number displayed is already in % format
            else:
                val = info.get(key, np.nan) * 100 # Must multiply by 100 for 3-year and 5-year CAGR return because they are displayed as the raw decimal
            row[display_name] = val
        return row

    # Fetch info dictionaries in parallel threads
    with ThreadPoolExecutor(max_workers=len(top_10_tickers)) as executor:
        metrics_data = list(executor.map(fetch_ticker_metrics, top_10_tickers))

    # Build comparison DataFrame
    comparison_df = pd.DataFrame(metrics_data).set_index("Ticker")

    # Plotting the Chart
    fig = make_subplots(
        rows=1, 
        cols=2, 
        subplot_titles=("YTD and 3-Month Return", "3-Year and 5-Year CAGR Return"),
        horizontal_spacing=0.10 # Gap size between the two charts (10%)
    )

    for column in comparison_df.columns:
        row_coordinate = 1
        col_coordinate = 1 if column in ["YTD Return", "3-Month Return"] else 2

        fig.add_trace(
            go.Bar(
                x=comparison_df[column],
                y=comparison_df.index,
                orientation='h',
                name=column,
                # Customizing the hover box appearance:
                hovertemplate=(f"<b>{column}: </b>" + "%{x:.2f}%<extra></extra>") # <extra></extra> removes the default secondary trace-name box
            ),
            row=row_coordinate,
            col=col_coordinate
        )

    # Configure layout
    fig.update_layout(
        barmode='group',
        yaxis=dict(autorange="reversed"),  # Reverses first Y-axis
        yaxis2=dict(autorange="reversed"), # Reverses second Y-axis
        height=500,
        showlegend=False,       # Subplot titles usually replace the need for a global legend
        hovermode="y unified",
        margin=dict(l=0, r=0, t=50, b=0), # Added top margin for subplot titles
    )

    fig.update_xaxes(title_text="Return (%)", showgrid=True, gridcolor="#E7DCDC")

    return fig