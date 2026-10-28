import pandas as pd
import plotly.graph_objects as go
import pycountry
import streamlit as st

# Cached Function to get a full database of existing currencies
@st.cache_data(ttl=3600, show_spinner=False)
def get_currency_database():
    # 1. Comprehensive Local Fallback Dictionary
    # This covers major global currencies, multi-nation currency structures, and several unknown countries in pycountry cleanly
    local_currency_to_countries = {
        "AFN": ["Afghanistan"],
        "AOA": ["Angola"],
        "AUD": ["Australia", "Kiribati", "Nauru", "Tuvalu"],
        "AZN": ["Azerbaijan"],
        "BAM": ["Bosnia and Herzegovina"],
        "CAD": ["Canada"],
        "CHF": ["Switzerland", "Liechtenstein"],
        "CNY": ["China"],
        "EUR": ["Germany", "France", "Italy", "Spain", "Netherlands", "Belgium", "Austria", "Greece", "Portugal", "Finland", "Ireland", "Slovakia", "Croatia", "Lithuania", "Slovenia", "Latvia", "Estonia", "Cyprus", "Luxembourg", "Malta"],
        "GBP": ["United Kingdom", "Jersey", "Guernsey", "Isle of Man"],
        "INR": ["India"],
        "IDR": ["Indonesia"],
        "JPY": ["Japan"],
        "NZD": ["New Zealand", "Cook Islands", "Niue", "Pitcairn Islands"],
        "TWD": ["Taiwan"],
        "USD": ["United States", "Ecuador", "El Salvador", "Panama", "Marshall Islands", "Micronesia", "Palau", "Timor-Leste"],
        "XAF": ["Cameroon", "Central African Republic", "Chad", "Republic of the Congo", "Equatorial Guinea", "Gabon"],
        "XCD": ["Antigua and Barbuda", "Dominica", "Grenada", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Anguilla", "Montserrat"],
        "XOF": ["Benin", "Burkina Faso", "Côte d'Ivoire", "Guinea-Bissau", "Mali", "Niger", "Senegal", "Togo"],
        "ZAR": ["South Africa", "Lesotho", "Namibia", "Eswatini"]    
    }

    currency_data = []

    # 2. Iterate through all pycountry currencies
    for currency in pycountry.currencies:
        ticker = getattr(currency, 'alpha_3', None)
        name = getattr(currency, 'name', None)
        numeric_code = getattr(currency, 'numeric', None)
        
        if not ticker:
            continue

        associated_countries = []

        # Strategy A: Attempt to match by numeric code locally
        try:
            if numeric_code:
                # Padding numeric code to 3 digits if it's strings like '008'
                padded_numeric = str(numeric_code).zfill(3)
                country_match = pycountry.countries.get(numeric=padded_numeric)
                
                if country_match:
                    associated_countries.append(country_match.name)
        except Exception:
            pass # Suppress mismatch errors and move to the fallbacks

        # Strategy B: If Strategy A yielded nothing or was incorrect, apply the comprehensive fallback dictionary
        if not associated_countries or ticker in local_currency_to_countries:
            fallback_matches = local_currency_to_countries.get(ticker, [])
            if fallback_matches:
                # Merge unique findings if the numeric check found something valid
                for c in fallback_matches:
                    if c not in associated_countries:
                        associated_countries.append(c)

        # Strategy C: Final fallback label if no countries are associated
        if associated_countries:
            countries_str = ", ".join(associated_countries)
        else:
            countries_str = 'Multiple / Special / System Use'

        currency_data.append({
            'Ticker': ticker,
            'Name': name,
            'ISO Numeric Code': numeric_code,
            'Associated Countries': countries_str
        })

    # 3. Formulate and return the finished Pandas DataFrame
    return pd.DataFrame(currency_data)

# Cached Function to get the fiat currency details (Name and Associated Countries) from the ticker
@st.cache_data(ttl=3600, show_spinner=False)
def get_fiat_details(fiat_currency, currency_database):
    # Set the index to Ticker to a new temporary dataframe because dataframes are objects that passed by reference in a parameter
    # which will make unecessary changes to the global variable currency_database
    currency_database_temp = currency_database.set_index("Ticker")
    try:
        currency_name = currency_database_temp.at[fiat_currency, "Name"]
    except:
        currency_name = "Unknown Currency"

    try:
        associated_countries = currency_database_temp.at[fiat_currency, "Associated Countries"]
    except:
        associated_countries = "Unknown Country"

    fiat_details = {"Name": currency_name, "Associated Countries": associated_countries}

    return pd.DataFrame([fiat_details])

# Cached Function to get Exchange Rate Action Chart with 200-Day SMA
@st.cache_data(ttl=3600, show_spinner=False)
def get_exchange_rate_trend(historical_data):
    data = historical_data[["Open", "High", "Low", "Close"]].copy()

    # --- 200-Day SMA Calculation
    data["200-Day SMA"] = data["Close"].rolling(window=200).mean()

    # Setting up Subplots: Row 1 = Price (70%), Row 2 = MACD (30%)
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Exchange Rate',
                hovertemplate="<b>Open:</b> %{open:,.6g}<br><b>High:</b> %{high:,.6g}<br><b>Low:</b> %{low:,.6g}<br><b>Close:</b> %{close:,.6g}<extra></extra>"
            ),
            go.Scatter(
                x=data.index,
                y=data['200-Day SMA'],
                line=dict(color="#0831e7", width=2),
                name='200-Day SMA',
                hovertemplate="<b>200-Day SMA:</b> %{y:,.6g}<extra></extra>"
            )
        ]
    )

    # Layout Configuration
    fig.update_layout(
        yaxis=dict(title="Exchange Rate (OHLC)", tickformat="~f"),
        xaxis=dict(
            title="Date",
            showticklabels=True,
            side="bottom",
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="MAX")
                ]),
                bgcolor="rgba(35, 35, 35, 0.9)",
                activecolor="#ff7f0e",
                font=dict(color="white", size=11),
                y=1.00,             
                yanchor="bottom"    
            ),
            rangeslider=dict(visible=False)
        ),  
        hovermode="x unified",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(t=20, b=0, l=0, r=0)
    )

    fig.update_xaxes(
        showspikes=True,            # Turns on the hover vertical guide lines
        spikemode="across",         # Forces the line to extend past subplot grid boundaries
        spikesnap="cursor",         # Snaps line position exactly to your pointer
        spikethickness=1.5,         # Clean visual weight match
        spikecolor="#000000",     # Black line
        spikedash="dash",           # Makes it a dashed line format
        showgrid=True,              # Shows vertical grid lines
        nticks=10                   # Increase this number to make vertical intervals smaller
    )

    return fig