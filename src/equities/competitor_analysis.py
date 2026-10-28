import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import streamlit as st

# Function to get the top 10 companies from the Sector or Industry
@st.cache_data(ttl=3600, show_spinner=False)
def get_top_10_companies(sector_or_industry, string_value):
    # Cleaning up the string value of sector or industry to be used later in either the Sector or Industry class
    string_value = re.sub(
        r'[\s\-]+',
        '-', 
        string_value.lower()
    ).strip('-')

    if string_value == "N/A":
        return None
    else:
        if sector_or_industry == "Sector":
            obj = yf.Sector(string_value)
        else:
            obj = yf.Industry(string_value)

        # Top 10 companies of Sector or Industry by Market Weight in the US (Default) unless the region parameter is specified
        try:
            top_10_companies = obj.top_companies.head(10)
        except:
            top_10_companies = pd.DataFrame() # Sometimes there is no information of companies for a certain sector or industry
        else:
            top_10_companies.columns = top_10_companies.columns.str.title()
            top_10_companies.index.name = "Ticker"

    return top_10_companies

# Cached Function to get a pie chart showing the distribution of Market Weight by the top 10 companies
@st.cache_data(ttl=3600, show_spinner=False)
def get_mkt_weight_chart(top_10_companies_df):
    # 1. Create the Pie/Donut Chart using graph_objects
    fig = go.Figure(
        data=[
            go.Pie(
                labels=top_10_companies_df.index.tolist(),  # Ticker symbols from DataFrame index
                values=top_10_companies_df["Market Weight"],
                hole=0.0,  # Set to 0.0 for a standard solid pie chart
                textinfo="label+percent",
                textposition="inside",
                marker=dict(
                    colors=[
                        "#2b5c8f",
                        "#469b9b",
                        "#d97724",
                        "#5c6b73",
                        "#e76f51",
                        "#2a9d8f",
                        "#e9c46a",
                        "#f4a261",
                    ],
                    line=dict(color="#ffffff", width=2),  # White borders between slices
                ),
                hovertemplate="<b>%{label}</b><br>Market Weight: %{value:.2f}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    # 2. Update Layout & Styling
    fig.update_layout(
        template="plotly_white",
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(
            title=dict(text="<b>Tickers</b>", font=dict(size=12)),
            orientation="v",
            y=0.5,
            x=1.02,
        ),
    )

    return fig

# Cached Function to return charts for sector and industry analysis
@st.cache_data(ttl=3600, show_spinner=False)
def get_sector_industry_comparisons(sector_or_industry, string_value, ticker_input):
    if string_value == "N/A":
        return None
    else:
        top_10_companies = get_top_10_companies(sector_or_industry, string_value)
        top_10_tickers = top_10_companies.index.to_list()
        # Adding the current stock ticker if it is not in the list of top 10 companies
        if ticker_input not in top_10_tickers:
            top_10_tickers.append(ticker_input)

        # Initialize bulk Tickers object
        tickers_obj = yf.Tickers(" ".join(top_10_tickers))

        metrics_to_collect = {
            "volume": "Volume",
            "averageVolume": "Average Volume",
            "currentPrice": "Current Price",
            "bookValue": "BVPS",
            "dividendYield": "Dividend Yield",
            "beta": "Beta",
            "grossMargins": "Gross Margins",
            "operatingMargins": "Operating (EBIT) Margins",
            "profitMargins": "Net Income Margins",
            "forwardPE": "Forward P/E Ratio",
            "priceToSalesTrailing12Months": "P/S Ratio",
            "priceToBook": "P/B Ratio",
            "pegRatio": "PEG Ratio",
            "quickRatio": "Quick Ratio",
            "currentRatio": "Current Ratio",
            "debtToEquity": "Debt to Equity Ratio",
            "returnOnAssets": "Return on Assets",
            "returnOnEquity": "Return on Equity",
        }

        # Helper function to process a single ticker and captures tickets_obj & metrics_to_collect from parent scope
        def fetch_ticker_metrics(symbol):
            # tickers_obj will be defined later, tickers_obj cannot be used as an argument because this function will be iterated using ThreadPoolExecutor
            # and the tickers_obj cannot be iterated
            ticker_item = tickers_obj.tickers[symbol]
            info = ticker_item.info
            
            row = {"Ticker": symbol}
            for key, display_name in metrics_to_collect.items():
                val = info.get(key, np.nan)
                
                if key in ["grossMargins", "operatingMargins", "profitMargins", "returnOnAssets", "returnOnEquity"] and val is not None:
                    val = round(val * 100, 2)
                elif key in ["currentPrice", "bookValue", "forwardPE", "priceToSalesTrailing12Months", "priceToBook"] and val is not None:
                    val = round(val, 2)
                elif key in ["debtToEquity"] and val is not None:
                    val = round(val / 100, 2)
                    
                row[display_name] = val
            return row

        # Fetch info dictionaries in parallel threads
        with ThreadPoolExecutor(max_workers=len(top_10_tickers)) as executor:
            metrics_data = list(executor.map(fetch_ticker_metrics, top_10_tickers))

        # Build comparison DataFrame
        comparison_df = pd.DataFrame(metrics_data).set_index("Ticker")

        chart_config = [
            (["Volume", "Average Volume"], "Trading Volume"),
            (["Current Price", "BVPS"], "Price vs. BVPS"),
            (["Dividend Yield"], "Dividend Yield"),
            (["Beta"], "Beta (Volatility)"),
            (
                [
                    "Gross Margins",
                    "Operating (EBIT) Margins",
                    "Net Income Margins",
                ],
                "Profitability Margins",
            ),
            (["Forward P/E Ratio", "P/S Ratio", "P/B Ratio"], "Valuation Ratios"),
            (["PEG Ratio"], "PEG Ratio"),
            (
                ["Quick Ratio", "Current Ratio", "Debt to Equity Ratio"],
                "Liquidity & Solvency",
            ),
            (["Return on Assets", "Return on Equity"], "Management Effectiveness"),
        ]

        percentage_metrics = ["Dividend Yield", "Gross Margins", "Operating (EBIT) Margins", "Net Income Margins", "Return on Assets", "Return on Equity"]
        price_metrics = ["Current Price", "BVPS"]

        # Initialize a 3x3 Plotly Subplot Figure
        fig = make_subplots(
            rows=3,
            cols=3,
            subplot_titles=[title for _, title in chart_config],
            vertical_spacing=0.14,
            horizontal_spacing=0.10,
        )

        # Color palette for metrics within grouped bar charts
        # Define a clean, professional multi-metric palette (3 distinct, high-contrast colors)
        MULTI_BAR_COLORS = [
            "#2b5c8f",
            "#469b9b",
            "#d97724",
        ]  # Navy Blue, Teal, Warm Amber

        # Define a neutral color for single-metric charts
        SINGLE_BAR_COLOR = "#5c6b73"  # Muted Slate Gray

        # Populate subplots dynamically
        tickers = comparison_df.index.tolist()

        for idx, (cols, title) in enumerate(chart_config):
            row = (idx // 3) + 1
            col = (idx % 3) + 1

            valid_cols = [c for c in cols if c in comparison_df.columns]
            is_multi_metric = len(valid_cols) > 1

            # Tracks text/color pairs for the inline legend banner above this specific chart
            legend_items = []

            for color_idx, metric in enumerate(valid_cols):
                color = MULTI_BAR_COLORS[color_idx % len(MULTI_BAR_COLORS)] if is_multi_metric == True else SINGLE_BAR_COLOR

                # Determine hover format string
                hover_fmt = ":,.0f" if "Volume" in metric else ":,.2f"

                # Determine the prefix and suffix for hover display
                if metric in percentage_metrics:
                    prefix = ""
                    suffix = "%"
                elif metric in price_metrics:
                    prefix = "$"
                    suffix = ""
                else:
                    prefix = ""
                    suffix = ""

                # Add Horizontal Bar trace (showlegend disabled to avoid global legend clutter)
                fig.add_trace(
                    go.Bar(
                        y=tickers,
                        x=comparison_df[metric],
                        orientation="h",
                        name=metric,
                        marker_color=color,
                        showlegend=False,  # Turn off standard global legend
                        hovertemplate=f"<b>{metric}</b>: {prefix}%{{x{hover_fmt}}}{suffix}<extra></extra>",
                    ),
                    row=row,
                    col=col,
                )

                # Store HTML colored text for inline legend
                legend_items.append(
                    f"<span style='color:{color};'><b>■</b> {metric}</span>"
                )

        # Update Grid Aesthetics & Layout
        fig.update_layout(
            height=1000,
            barmode="group",
            template="plotly_white",
            margin=dict(l=20, r=20, t=50, b=40),
            hovermode="y unified"
        )

        # Format axes across all subplots
        fig.update_xaxes(showgrid=True, gridcolor="#E7DCDC")
        fig.update_yaxes(showgrid=False, autorange="reversed")
        
        return fig