from datetime import datetime
import pandas as pd
import yfinance as yf
import streamlit as st

# Cached Function to call the FUTURES_TICKER from yfinance using the user futures ticker input and return the raw news and 3-year historical data 
@st.cache_data(ttl=3600, show_spinner=False)
def process_futures_ticker(futures_ticker_input):
    FUTURES_TICKER = yf.Ticker(futures_ticker_input + "=F") # Getting the yfinance Ticker object
    info_dict = FUTURES_TICKER.info
    raw_news = FUTURES_TICKER.news
    historical_data = FUTURES_TICKER.history(period="3y")

    # Extract relevant native attributes
    current_price = historical_data["Close"].iat[-1]
    open_interest = info_dict.get("openInterest")
    raw_expiry = info_dict.get("expireDate")

    if raw_expiry:
        current_front_month_contract_expiry = datetime.fromtimestamp(raw_expiry).strftime("%d %B %Y")
    else:
        current_front_month_contract_expiry = None

    return current_price, open_interest, current_front_month_contract_expiry, raw_news, historical_data

# Cached Function to get the comomdity database from a pre-defined commodity dictionary
@st.cache_data(ttl=3600, show_spinner=False)
def get_commodity_db():
    # 1. Complete dictionary of dictionaries containing commodity futures metadata
    commodity_data = {
        # ⚡ Energy
        "CL": {
            "Name": "Crude Oil (WTI)",
            "Category": "Energy",
            "Unit Price": "barrel",
            "Description": "West Texas Intermediate (WTI) is the primary US light sweet crude benchmark, heavily driven by domestic drilling and global macroeconomic demand.",
        },
        "BZ": {
            "Name": "Brent Crude Oil",
            "Category": "Energy",
            "Unit Price": "barrel",
            "Description": "The global benchmark for waterborne sweet crude oil extracted from the North Sea, closely tracking international geopolitical events.",
        },
        "NG": {
            "Name": "Natural Gas",
            "Category": "Energy",
            "Unit Price": "MMBtu",
            "Description": "A highly seasonal and volatile heating and electricity-generation fuel benchmarked at the Henry Hub in Louisiana.",
        },
        "RB": {
            "Name": "RBOB Gasoline",
            "Category": "Energy",
            "Unit Price": "gallon",
            "Description": "Reformulated Blendstock for Oxygenate Blending; represents the refined, wholesale gasoline market prior to retail distribution.",
        },
        "HO": {
            "Name": "Heating Oil",
            "Category": "Energy",
            "Unit Price": "gallon",
            "Description": "A refined petroleum distillate used widely for residential heating and closely tied to industrial diesel fuel dynamics.",
        },
        # 🪙 Precious & Industrial Metals
        "GC": {
            "Name": "Gold",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "troy ounce",
            "Description": "The world's premier safe-haven asset, traded as a structural monetary hedge against inflation and currency debasement.",
        },
        "MGC": {
            "Name": "Micro Gold",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "troy ounce",
            "Description": "A retail-sized gold futures contract tracking the exact same COMEX benchmark asset at one-tenth the financial scale.",
        },
        "SI": {
            "Name": "Silver",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "troy ounce",
            "Description": "A dual-purpose asset serving both as a monetary store of value and an industrial metal essential for solar energy and electronics.",
        },
        "SIL": {
            "Name": "Micro Silver",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "troy ounce",
            "Description": "A micro-sized silver futures contract offering lower financial margin exposure to standard COMEX silver price movements.",
        },
        "HG": {
            "Name": "Copper",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "pound",
            "Description": "Nicknamed 'Doctor Copper' because its high industrial utility makes it an accurate early indicator of overall global economic health.",
        },
        "PL": {
            "Name": "Platinum",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "troy ounce",
            "Description": "A rare precious metal with major industrial applications, primarily used in automotive catalytic converters and luxury jewelry.",
        },
        "PA": {
            "Name": "Palladium",
            "Category": "Precious & Industrial Metals",
            "Unit Price": "troy ounce",
            "Description": "A highly specialized metal primarily consumed by the auto industry to reduce emissions from gasoline-powered internal combustion engines.",
        },
        # 🌾 Agriculture & Grains
        "ZC": {
            "Name": "Corn",
            "Category": "Agriculture & Grains",
            "Unit Price": "bushel",
            "Description": "The highest-volume global grain crop, heavily utilized for livestock feed, industrial ethanol fuel production, and consumer foods.",
        },
        "ZS": {
            "Name": "Soybeans",
            "Category": "Agriculture & Grains",
            "Unit Price": "bushel",
            "Description": "A massive global oilseed crop critical for protein-rich animal feeds and vegetable oils, highly sensitive to US-China export dynamics.",
        },
        "ZM": {
            "Name": "Soybean Meal",
            "Category": "Agriculture & Grains",
            "Unit Price": "short ton",
            "Description": "The high-protein byproduct of soybean crushing, trading as a core component of commercial livestock and poultry nutritional feeds.",
        },
        "ZL": {
            "Name": "Soybean Oil",
            "Category": "Agriculture & Grains",
            "Unit Price": "pound",
            "Description": "A vegetable oil byproduct of soybean processing used heavily in global food manufacturing and increasingly in biodiesel fuel production.",
        },
        "KE": {
            "Name": "KC HRW Wheat",
            "Category": "Agriculture & Grains",
            "Unit Price": "bushel",
            "Description": "Kansas City Hard Red Winter wheat futures, representing the high-protein grain variant primarily milled to produce bread flour.",
        },
        "ZO": {
            "Name": "Oats",
            "Category": "Agriculture & Grains",
            "Unit Price": "bushel",
            "Description": "An agricultural grain crop primarily processed into commercial livestock fodder and consumer breakfast oat products.",
        },
        "ZR": {
            "Name": "Rough Rice",
            "Category": "Agriculture & Grains",
            "Unit Price": "hundredweight (cwt)",
            "Description": "Unmilled long-grain rice futures representing a primary dietary staple for a vast portion of the global human population.",
        },
        # ☕ Soft Commodities
        "KC": {
            "Name": "Coffee",
            "Category": "Soft Commodities",
            "Unit Price": "pound",
            "Description": "Tracks the premium Arabica coffee bean variant, heavily influenced by weather trends in major growing hubs like Brazil and Vietnam.",
        },
        "CC": {
            "Name": "Cocoa",
            "Category": "Soft Commodities",
            "Unit Price": "metric ton",
            "Description": "The essential ingredient for chocolate production, with supply heavily concentrated in West African nations like Ivory Coast and Ghana.",
        },
        "SB": {
            "Name": "Sugar",
            "Category": "Soft Commodities",
            "Unit Price": "pound",
            "Description": "Global raw cane sugar futures, tightly bound to consumer food production trends and Brazilian ethanol blending mandates.",
        },
        "CT": {
            "Name": "Cotton",
            "Category": "Soft Commodities",
            "Unit Price": "pound",
            "Description": "The benchmark fiber for the global textile and apparel industry, highly sensitive to weather and industrial textile mill demand.",
        },
        "OJ": {
            "Name": "Orange Juice",
            "Category": "Soft Commodities",
            "Unit Price": "pound",
            "Description": "Frozen Concentrated Orange Juice (FCOJ) futures, historically subject to extreme volatility caused by Florida crop diseases and hurricanes.",
        },
        # 🥩 Livestock
        "LE": {
            "Name": "Live Cattle",
            "Category": "Livestock",
            "Unit Price": "pound",
            "Description": "Futures tracking market-ready cattle that have reached full weight capacity in commercial feedlots, heading toward processing.",
        },
        "GF": {
            "Name": "Feeder Cattle",
            "Category": "Livestock",
            "Unit Price": "pound",
            "Description": "Young calves weighing roughly 600-800 lbs that are purchased to enter commercial feedlots for final weight gain cycles.",
        },
        "HE": {
            "Name": "Lean Hogs",
            "Category": "Livestock",
            "Unit Price": "pound",
            "Description": "Futures tracking the wholesale swine processing market, driven by global pork demand and domestic feed corn input costs.",
        }
    }

    # 2. Convert dictionary into a Pandas DataFrame
    commodities_df = pd.DataFrame.from_dict(commodity_data, orient="index")
    commodities_df.index.name = "Ticker"

    return commodities_df