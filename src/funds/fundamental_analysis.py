import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Function to get and clean the top holdings data
def get_top_holdings(top_holdings):
    top_holdings = top_holdings.rename(columns={"Holding Percent": "Holding Percentage"}).reset_index()
    top_holdings["Holding Percentage"] = top_holdings["Holding Percentage"].apply(lambda x: f"{x * 100:,.2f}%")

    return top_holdings

# Function to get and clean the sector allocation data
def get_sector_allocation(sector_allocation):
    sector_allocation = {
        "Real Estate" if key == "realestate" else key.replace("_", " ").title(): value for key, value in sector_allocation.items()
    }

    return sector_allocation

# Function to get and clean the asset class allocation data
def get_asset_class_allocation(asset_class_allocation):
    asset_class_map = {
        "cashPosition": "Cash",
        "stockPosition": "Common Stocks",
        "bondPosition": "Bonds",
        "preferredPosition": "Preferred Stocks",
        "convertiblePosition": "Convertible",
        "otherPosition": "Others"
    }

    asset_class_allocation = {
        asset_class_map.get(key, key): value for key, value in asset_class_allocation.items()
    }

    return asset_class_allocation

# Function to get and clean the fund operations data
def get_fund_operations(fund_operations):
    fund_operations = pd.DataFrame(fund_operations)
    fund_operations = fund_operations.iloc[:-1].reset_index()
    for col in fund_operations.columns:
        fund_operations[col] = fund_operations[col].apply(
             lambda x: f"{x * 100:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x
        )

    return fund_operations

# Function to get and clean the bond ratings allocation data
def get_bond_rating_allocation(bond_rating_allocation):
    bond_rating_allocation = {
        key.replace("_", " ").upper(): value for key, value in bond_rating_allocation.items()
    }
    us_treasuries_share = bond_rating_allocation.pop("US GOVERNMENT", None) # Removes the US Government line item and saves its value
    bond_rating_allocation = {key: value for key, value in sorted(bond_rating_allocation.items()) if value >= 0}

    return bond_rating_allocation, us_treasuries_share

# Cached Function to process the deep dive data of an investment fund by callnig the previous functions above
@st.cache_data(ttl=3600, show_spinner=False)
def process_deep_dive_data(top_holdings, sector_allocation, asset_class_allocation, fund_operations, bond_rating_allocation):

    # Calling the various functions of each aspect of the deep dive fundamental analysis
    top_holdings = get_top_holdings(top_holdings)
    sector_allocation = get_sector_allocation(sector_allocation)
    asset_class_allocation = get_asset_class_allocation(asset_class_allocation)
    fund_operations = get_fund_operations(fund_operations)
    bond_rating_allocation, us_treasuries_share = get_bond_rating_allocation(bond_rating_allocation)
   
    deep_dive_data = {
        "Top Holdings": top_holdings,
        "Sector Allocation": sector_allocation,
        "Asset Class Allocation": asset_class_allocation,
        "Fund Operations": fund_operations,
        "Bond Rating Allocation": bond_rating_allocation
    }

    return deep_dive_data, us_treasuries_share

# Cached Function to get the pie chart for Sector Allocation
@st.cache_data(ttl=3600, show_spinner=False)
def get_sector_piechart(sector_allocation):
    # 1. Create the Pie Chart using graph_objects
    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(sector_allocation.keys()),  # Sectors
                values=list(sector_allocation.values()), # Allocation Percentage
                hole=0.0,  # Set to 0.0 for a standard solid pie chart
                textinfo="label",
                textposition="inside",
                hovertemplate="<b>%{label}</b> (%{percent})<extra></extra>"
            )
        ]
    )

    # 2. Update Layout & Styling
    fig.update_layout(
        template="plotly_white",
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            title=dict(text="<b>Sector</b>", font=dict(size=12)),
            orientation="h",   # Keeps the legend horizontal,
            xanchor="center",  # Anchors the legend from its horizontal center,
            x=0.5              # Centers it perfectly at the midpoint of the chart
        )
    )

    return fig

# Cached Function to get the pie chart for Bond Rating Allocation
@st.cache_data(ttl=3600, show_spinner=False)
def get_bond_rating_piechart(bond_rating_allocation):
    # 1. Create the Pie Chart using graph_objects
    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(bond_rating_allocation.keys()),   # Bond Ratings
                values=list(bond_rating_allocation.values()), # Allocation Percentage
                hole=0.0,  # Set to 0.0 for a standard solid pie chart
                textinfo="label",
                textposition="inside",
                hovertemplate="<b>%{label}</b> (%{percent})<extra></extra>"
            )
        ]
    )

    # 2. Update Layout & Styling
    fig.update_layout(
        template="plotly_white",
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            title=dict(text="<b>Bond Ratings</b>", font=dict(size=12)),
            orientation="h",   # Keeps the legend horizontal,
            xanchor="center",  # Anchors the legend from its horizontal center,
            x=0.5              # Centers it perfectly at the midpoint of the chart
        )
    )

    return fig

# Cached Function to get the donut chart for Asset Class Allocation
@st.cache_data(ttl=3600, show_spinner=False)
def get_asset_class_donutchart(asset_class_allocation):
    # 1. Create the Donut Chart using graph_objects
    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(asset_class_allocation.keys()),  # Asset Class
                values=list(asset_class_allocation.values()), # Allocation Percentage
                hole=0.4,  # Hole is set to > 0 for donut chart
                textinfo="label",
                textposition="inside",
                marker=dict(
                    colors=[
                        "#2b5c8f",
                        "#469b9b",
                        "#d97724",
                        "#5c6b73",
                        "#e76f51"
                    ]
                ),
                hovertemplate="<b>%{label}</b> (%{percent})<extra></extra>"
            )
        ]
    )

    # 2. Update Layout & Styling
    fig.update_layout(
        template="plotly_white",
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            title=dict(text="<b>Asset Class</b>", font=dict(size=12)),
            orientation="h",   # Keeps the legend horizontal,
            xanchor="center",  # Anchors the legend from its horizontal center,
            x=0.5              # Centers it perfectly at the midpoint of the chart
        )
    )

    return fig