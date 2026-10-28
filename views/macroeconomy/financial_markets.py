import streamlit as st
from src.shared.macroeconomic_metrics import (
    get_expected_market_return,
    get_treasury_yield,
    get_vix,
    get_rsp_spy_ratio,
    get_energy_commodities_data,
    get_metal_commodities_data,
    get_forex_data,
    get_crypto_data
)
from src.macroeconomy.global_market_analysis import (
    get_OHLC_historical_chart,
    get_ratio_line_chart,
    get_comparison_tbonds_chart,
    get_yield_curve
)

st.markdown("<h2 style='text-align: center;'>Market Overview</h2>", unsafe_allow_html=True)

with st.spinner("Loading Data ..."):
    expected_market_return = get_expected_market_return()
    risk_free_rate = get_treasury_yield("^TNX") # Using the 10-year Treasury Note as the reference
    three_month_tbill = get_treasury_yield("^IRX")
    five_year_tnote = get_treasury_yield("^FVX")
    thirty_year_tbond = get_treasury_yield("^TYX")
    vix = get_vix()
    rsp_spy_ratio = get_rsp_spy_ratio(expected_market_return["Historical Data"])

    energy_commodities = get_energy_commodities_data()
    brent_crude_price = energy_commodities["Brent Crude"]
    wti_price = energy_commodities["WTI"]
    ng_price = energy_commodities["Natural Gas"]

    metal_commodities = get_metal_commodities_data()
    gold_price = metal_commodities["Gold"]
    silver_price = metal_commodities["Silver"]
    copper_price = metal_commodities["Copper"]
    platinum_price = metal_commodities["Platinum"]

    forex = get_forex_data()
    eur_usd_rate = forex["EUR/USD"]
    usd_jpy_rate = forex["USD/JPY"]
    gbp_usd_rate = forex["GBP/USD"]

    crypto = get_crypto_data()
    bitcoin_price = crypto["Bitcoin"]
    ethereum_price = crypto["Ethereum"]
    solana_price = crypto["Solana"]
    usd_tether_price = crypto["USD Tether"]

    st.session_state.risk_free_rate = risk_free_rate["Value"]
    
# Capital Market Assumptions Section
st.markdown("<h3 style='text-align: center;'>Capital Market Assumptions</h3>", unsafe_allow_html=True)
with st.container(horizontal=True, wrap=True, border=True):
    st.metric(
        "Expected Stock Market Return",
        value=f"{expected_market_return["Value"] * 100:,.2f}%",
        delta=f"{expected_market_return["Delta"]:+.2f}% vs 20D Avg",
        help="Expected market return is the anticipated long-term average percentage profit or loss of an entire stock market index (like the S&P 500) based on historical performance and economic forecasts."
    )
    st.metric(
        "Risk-Free Rate",
        value=f"{risk_free_rate["Value"] * 100:,.2f}%",
        delta=f"{risk_free_rate["Delta"]:+.2f}% vs 20D Avg",
        help="The risk-free rate is the theoretical rate of return an investor expects from an investment with zero risk of financial loss. The 10-year Treasury Bill is used as a benchmark to calculate this rate."
    )
    st.metric(
        "RSP/SPY Ratio",
        value=f"{rsp_spy_ratio["Value"]:,.2f}",
        delta=f"{rsp_spy_ratio["Delta"]:+.2f}% vs 20D Avg",
        help="The RSP/SPY Ratio compares the Invesco S&P 500 Equal Weight ETF (RSP) to the cap-weighted SPDR S&P 500 ETF Trust (SPY). It acts as a breadth gauge to see if market rallies are supported by healthy participation across all 500 stocks or just the mega-caps. A falling ratio means market gains are narrow, heavily driven by a handful of mega-cap tech stocks."
    )
    st.metric(
        "CBOE Volatility Index (VIX)",
        value=f"{vix["Value"]:,.2f}",
        delta=f"{vix["Delta"]:+.2f}pts vs 20D Avg",
        delta_color="inverse",  # Renders red when VIX rises above average, green when below
        help="VIX, also known as the 'Fear Gauge', represents a percentage figure that measures the stock market's expectation of near-term volatility. Below 15 indicates market calm and stability. 15 to 25 reflects standard, healthy market movement. Above 25 signals severe market stress, panic, or large upcoming market swings."
    )

col1, col2 = st.columns(2)

with col1:
    # Energy Commodities Section
    st.subheader("Energy Commodities")
    with st.container(horizontal=True, wrap=True, border=True):
        st.metric(
            "Brent Crude Price per barrel",
            value=f"${brent_crude_price["Value"]:,.2f}",
            delta=f"{brent_crude_price["Delta"]:+.2f}% vs 20D Avg",
            help="Brent Crude is a light, sweet blend originating mainly from the North Sea, serving as the leading global benchmark for pricing international oil. Brent Crude is waterborne and easily shipped worldwide, reflecting broader global events."
        )
        st.metric(
            "WTI Price per barrel",
            value=f"${wti_price["Value"]:,.2f}",
            delta=f"{wti_price["Delta"]:+.2f}% vs 20D Avg",
            help="West Texas Intermediate (WTI) is a light, sweet crude oil extracted in the United States and used as the primary benchmark for North American oil pricing. WTI is landlocked in Oklahoma and relies on pipelines, making it sensitive to domestic U.S. storage data."
        )
        st.metric(
            "Natural Gas Price per MMBtu",
            value=f"${ng_price["Value"]:,.2f}",
            delta=f"{ng_price["Delta"]:+.2f}% vs 20D Avg",
            help="Natural Gas is a clean-burning fossil fuel benchmarked at the Henry Hub in Louisiana, serving as the leading pricing standard for the North American energy market. Unlike globally traded waterborne oil, natural gas relies heavily on pipeline infrastructure and regional storage, making its price highly sensitive to local weather patterns, industrial demand, and domestic supply changes. The price is quoted in USD per Million British Thermal Units."
        )
        
    # Metal Commodities Section
    st.subheader("Metal Commodities")
    with st.container(horizontal=True, wrap=True, border=True):
        st.metric(
            "Gold Price per troy ounce",
            value=f"${gold_price["Value"]:,.2f}",
            delta=f"{gold_price["Delta"]:+.2f}% vs 20D Avg",
            help="Gold is a premier global safe-haven asset and store of value, primarily driven by investment demand, central bank reserves, and jewelry manufacturing."
        )
        st.metric(
            "Platinum Price per troy ounce",
            value=f"${platinum_price["Value"]:,.2f}",
            delta=f"{platinum_price["Delta"]:+.2f}% vs 20D Avg",
            help="Platinum is a rare precious metal with major industrial applications, primarily utilized in automotive catalytic converters, hydrogen fuel cells, and high-end jewelry."
        )
        st.metric(
            "Silver Price per troy ounce",
            value=f"${silver_price["Value"]:,.2f}",
            delta=f"{silver_price["Delta"]:+.2f}% vs 20D Avg",
            help="Silver is a dual-purpose precious and industrial metal, heavily influenced by both investor sentiment and industrial demand in electronics, solar panels, and photography."
        )
        st.metric(
            "Copper Price per pound",
            value=f"${copper_price["Value"]:,.2f}",
            delta=f"{copper_price["Delta"]:+.2f}% vs 20D Avg",
            help="Copper is a leading industrial base metal and key economic health indicator ('Doctor Copper'), critical for global infrastructure, electrical wiring, and clean energy technologies."
        )

with col2:
    # Forex Currencies Section
    st.subheader("Forex Currencies")
    with st.container(horizontal=True, wrap=True, border=True):
        st.metric(
            "EUR/USD exchange rate",
            value=f"${eur_usd_rate["Value"]:,.4f}",
            delta=f"{eur_usd_rate["Delta"]:+.2f}% vs 20D Avg",
            help="EUR/USD represents about 21%-24% of all daily forex volume, and acts as a broad gauge of economic health for the US and EU."
        )
        st.metric(
            "USD/JPY exchange rate",
            value=f"¥{usd_jpy_rate["Value"]:,.4f}",
            delta=f"{usd_jpy_rate["Delta"]:+.2f}% vs 20D Avg",
            help="USD/JPY accounts for roughly 13%-14% of global volume, and is closely tied to interest rate gaps and Asian market sentiment. price of Gold is universally denominated in USD per troy ounce. 1 troy ounce = 31.10 grams."
        )
        st.metric(
            "GBP/USD exchange rate",
            value=f"${gbp_usd_rate["Value"]:,.4f}",
            delta=f"{gbp_usd_rate["Delta"]:+.2f}% vs 20D Avg",
            help="GBP/USD is known as 'Cable', capturing roughly 8%-9% of volume, and is noted for high volatility and swift reactions to UK data."
        )

    # Cryptocurrencies Section
    st.subheader("Cryptocurrencies")
    with st.container(horizontal=True, wrap=True, border=True):
        st.metric(
            "Bitcoin Price",
            value=f"${bitcoin_price["Value"]:,.2f}",
            delta=f"{bitcoin_price["Delta"]:+.2f}% vs 20D Avg",
            help="Bitcoin is viewed as 'digital gold' and a macro inflation hedge, commanding over 50% of the digital asset market."
        )
        st.metric(
            "Ethereum Price",
            value=f"${ethereum_price["Value"]:,.2f}",
            delta=f"{ethereum_price["Delta"]:+.2f}% vs 20D Avg",
            help="Ethereum is the leading platform for smart contracts, decentralized finance (DeFi), and token creation."
        )
        st.metric(
            "Solana Price",
            value=f"${solana_price["Value"]:,.2f}",
            delta=f"{solana_price["Delta"]:+.2f}% vs 20D Avg",
            help="Solana is utilized for high-speed transactions, dApps, and institutional settlement layers."
        )
        st.metric(
            "USD Tether Price",
            value=f"${usd_tether_price["Value"]:,.2f}",
            delta=f"{usd_tether_price["Delta"]:+.2f}% vs 20D Avg",
            help="USD Tether is used by traders for volatility hedging, or park funds between trades, and aims to maintain a 1:1 ratio with USD."
        )

# Horizontal line dividing certain sections
st.divider()

st.markdown("<h2 style='text-align: center;'>Historical Charts</h2>", unsafe_allow_html=True)
# Custom Top Navigation Bar
with st.container(horizontal_alignment="center"):
    current_tab = st.segmented_control(
        label="Market Segments",
        options=["Capital Markets", "Energy Commodities", "Metal Commodities", "Forex Currencies", "Cryptocurrencies"],
        default="Capital Markets",
        label_visibility="collapsed" # Keeps it clean like a real nav bar
    )

if current_tab == "Capital Markets":
    col1, col2, col3 = st.columns(3)

    with col1:
        # SPY Price Action
        spy_fig = get_OHLC_historical_chart(
            expected_market_return["Historical Data"],
            title="SPY Price Action",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(spy_fig, width="stretch")

        # RSP/SPY Ratio
        rsp_spy_fig = get_ratio_line_chart(
            rsp_spy_ratio["Historical Data"],
            title="RSP/SPY Ratio"
        )
        st.plotly_chart(rsp_spy_fig, width="stretch")
        
    with col2:
        # 10-Year Treasury Yield
        ten_year_tnote_fig = get_OHLC_historical_chart(
            risk_free_rate["Historical Data"],
            title="10-Year Treasury Note Yield",
            yaxis_title="Yield (OHLC)",
            units_category="Yield"
        )
        st.plotly_chart(ten_year_tnote_fig, width="stretch")

        # Treasury Bonds Comparisons
        t_bonds_fig = get_comparison_tbonds_chart(
            three_month_tbill["Historical Data"],
            five_year_tnote["Historical Data"],
            risk_free_rate["Historical Data"],
            thirty_year_tbond["Historical Data"]
        )
        st.plotly_chart(t_bonds_fig, width="stretch")

    with col3:
        # VIX
        vix_fig = get_OHLC_historical_chart(
            vix["Historical Data"],
            title="CBOE Volatility Index (VIX)",
            yaxis_title="VIX (OHLC)",
            units_category="Unitless"
        )
        st.plotly_chart(vix_fig, width="stretch")

        # Yield Curve
        yield_curve_fig = get_yield_curve(
            three_month_tbill["Value"] * 100,
            five_year_tnote["Value"] * 100,
            risk_free_rate["Value"] * 100,
            thirty_year_tbond["Value"] * 100
        )
        st.plotly_chart(yield_curve_fig, width="stretch", height="stretch")

elif current_tab == "Energy Commodities":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Brent Crude Price Action
        brent_crude_fig = get_OHLC_historical_chart(
            brent_crude_price["Historical Data"],
            title="Brent Crude price per barrel",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(brent_crude_fig, width="stretch")

    with col2:
        # WTI Price Action
        wti_fig = get_OHLC_historical_chart(
            wti_price["Historical Data"],
            title="WTI price per barrel",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(wti_fig, width="stretch")

    with col3:
        # Natural Gas Price Action
        ng_fig = get_OHLC_historical_chart(
            ng_price["Historical Data"],
            title="Natural Gas price per MMBtu",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(ng_fig, width="stretch")

elif current_tab == "Metal Commodities":
    col1, col2 = st.columns(2)
    
    with col1:
        # Gold Price Action
        gold_fig = get_OHLC_historical_chart(
            gold_price["Historical Data"],
            title="Gold price per troy ounce",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(gold_fig, width="stretch")

        # Silver Price Action
        silver_fig = get_OHLC_historical_chart(
            silver_price["Historical Data"],
            title="Silver price per troy ounce",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(silver_fig, width="stretch")

    with col2:
        # Platinum Price Action
        platinum_fig = get_OHLC_historical_chart(
            platinum_price["Historical Data"],
            title="Platinum price per troy ounce",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(platinum_fig, width="stretch")

        # Copper Price Action
        copper_fig = get_OHLC_historical_chart(
            copper_price["Historical Data"],
            title="Copper price per pound",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(copper_fig, width="stretch")

elif current_tab == "Forex Currencies":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # EUR/USD Exchange Rate
        eur_usd_fig = get_OHLC_historical_chart(
            eur_usd_rate["Historical Data"],
            title="EUR/USD Exchange Rate",
            yaxis_title="Exchange Rate (OHLC)",
            units_category="Forex"
        )
        st.plotly_chart(eur_usd_fig, width="stretch")

    with col2:
        # USD/JPY Exchange Rate
        usd_jpy_fig = get_OHLC_historical_chart(
            usd_jpy_rate["Historical Data"],
            title="USD/JPY Exchange Rate",
            yaxis_title="Exchange Rate (OHLC)",
            units_category="Forex"
        )
        st.plotly_chart(usd_jpy_fig, width="stretch")

    with col3:
        # GBP/USD Exchange Rate
        gbp_usd_fig = get_OHLC_historical_chart(
            gbp_usd_rate["Historical Data"],
            title="GBP/USD Exchange Rate",
            yaxis_title="Exchange Rate (OHLC)",
            units_category="Forex"
        )
        st.plotly_chart(gbp_usd_fig, width="stretch")

else:
    col1, col2 = st.columns(2)
    
    with col1:
        # Bitcoin Price Action
        bitcoin_fig = get_OHLC_historical_chart(
            bitcoin_price["Historical Data"],
            title="Bitcoin Price Action",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(bitcoin_fig, width="stretch")

        # Ethereum Price Action
        ethereum_fig = get_OHLC_historical_chart(
            ethereum_price["Historical Data"],
            title="Ethereum Price Action",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(ethereum_fig, width="stretch")

    with col2:
        # Solana Price Action
        solana_fig = get_OHLC_historical_chart(
            solana_price["Historical Data"],
            title="Solana Price Action",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(solana_fig, width="stretch")

        # USD Tether Price Action
        usd_tether_fig = get_OHLC_historical_chart(
            usd_tether_price["Historical Data"],
            title="USD Tether Price Action",
            yaxis_title="Price (OHLC)"
        )
        st.plotly_chart(usd_tether_fig, width="stretch")