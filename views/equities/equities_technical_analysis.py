import streamlit as st
from src.shared.technical_analysis import get_boll_vol_rsi, get_ma_obv_ad_mfi, get_ma_macd, get_donchian_adi_chop

if st.session_state.stock_ticker_input == "":
    st.warning("Please enter the stock ticker input on the first page before proceeding.")
    st.stop()  # Halts execution of the rest of this page

st.markdown(f"<h1 style='text-align: center;'>Stock Ticker: {st.session_state.stock_ticker_input}</h1>", unsafe_allow_html=True)

if st.session_state.stock_ticker_input_error:
    st.error("Stock Ticker that was inputted does not exist. Please re-enter another ticker first before viewing this page.")
else:
    with st.spinner("Loading Data ..."):
        historical_data = st.session_state.stock_historical_data

        col1, col2 = st.columns(2)
        with col1:
            st.info(
                """
                **1. Bollinger Bands**
                
                **Primary Function:** Measures market volatility and identifies potential "extreme" price levels.
                
                **How it works:** It consists of three lines superimposed over the main price chart. The middle line is a standard 
                moving average (usually the past 20 candles). The upper and lower bands automatically expand when the 
                market is volatile and contract (squeeze) when the market is quiet.
                
                **What it tells you:** Because price stays inside these bands roughly 95% of the time, touching the outer 
                bands acts like a rubber band being stretched. Reaching the upper band means the price is relatively 
                high (potentially overbought), and reaching the lower band means it is relatively low (potentially oversold).
                
                **2. Volume Bars**
                
                **Primary Function:** Measures market commitment and the strength behind a price movement.
                
                **How it works:** Displayed as a series of vertical bars on the second panel. The height of the bar 
                represents how many shares, contracts, or coins were traded during that specific candle. The color usually matches 
                the price candle (green for buying volume, red for selling volume).
                
                **What it tells you:** Volume is the "fuel" of the market.
                - **High Volume:** Large institutional players (banks, hedge funds) are participating. A price breakout on huge 
                volume is highly reliable.
                - **Low Volume:** There is a lack of interest. If price is rising but volume is falling, the move is fragile and likely 
                to fail because there aren't enough buyers to sustain it.
                
                **3. Relative Strength Index (RSI)**
                
                **Primary Function:** Measures price momentum and speed to evaluate internal market strength.
                
                **How it works:** Plotted on a third panel beneath the volume chart, the RSI is a single line that oscillates strictly 
                between 0 and 100 based on the ratio of recent upward changes to downward changes.
                
                **What it tells you:** It detects when a trend is getting exhausted.
                - **Above 70:** The market has moved up too fast and is overbought, warning you that a pullback or reversal might 
                be around the corner.
                - **Below 30:** The market has dropped aggressively and is oversold, hinting that a bounce-back might happen soon.
                - **Crosses above/below 50:** Tells you whether the buyers (above 50) or sellers (below 50) are currently 
                controlling the overall momentum.
                """        
            )

        with col2:
            st.subheader("Bollinger Bands, Volume Bars, & Relative Strength Index (RSI) Charts")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                sma_period = st.slider("Bollinger Bands Period", min_value=5, max_value=50, value=20)
            with col_b:
                num_std = st.slider("Standard Deviations", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
            with col_c:
                rsi_period = st.slider("RSI Period", min_value=5, max_value=30, value=14)

            boll_vol_rsi_fig = get_boll_vol_rsi(historical_data, sma_period, num_std, rsi_period)
            st.plotly_chart(boll_vol_rsi_fig, width="stretch", height=700)

        col1, col2 = st.columns(2)
        with col1:
            st.info(
                """
                **1. Price Action with 200-Day Simple Moving Average (SMA)**
                
                **Primary Function:** Identifies the long-term market trend and establishes major support or resistance levels.
                
                **How it works:** Price Action focuses entirely on candlestick patterns, market structure (higher highs/lower lows), and horizontal support and 
                resistance lines without lagging indicators. Plotted directly on the price chart, the 200-Day SMA calculates the average closing price of an asset 
                over the past 200 trading days, creating a smooth line that filters out short-term market noise.
                
                **What it tells you:** When the price is trading above the 200-Day SMA, the asset is considered to be in a long-term bull market. When the price 
                trades below it, the asset is in a long-term bear market.
                - **The Baseline Filter:** Traders use this line as a directional filter; they generally only look for buy setups when price is above the line and 
                sell setups when price is below it.
                - **Dynamic Support/Resistance:** During structural trends, institutional buyers often step in when the price pulls back to the 200-Day SMA, causing 
                it to act as a floor (support) in an uptrend or a ceiling (resistance) in a downtrend.
                
                **2. On-Balance Volume (OBV)**
                
                **Primary Function:** Uses volume flow to predict potential price changes based on institutional buying and selling pressure.
                
                **How it works:** Plotted in a separate panel below the price chart, OBV is a cumulative running total of volume. It adds the day's volume if the price 
                closes higher than the previous day, and subtracts the day's volume if the price closes lower.
                
                **What it tells you:** Volume precedes price. When OBV is rising, 
                it shows that volume is heavier on up-days, signaling that smart money is accumulating the asset.  
                - **Trend Confirmation:** If the price is making higher highs and OBV is also making higher highs, it confirms that the upward trend is healthy and backed 
                by strong volume.
                - **Divergence Warning:** If the price is rising but OBV is falling or flattening, it reveals a bearish divergence. This means the price rally is hollow, 
                lacks institutional support, and is prone to a sudden reversal.
                
                **3. Accumulation/Distribution (A/D) Line**
                
                **Primary Function:** Gauges the supply and demand of an asset by looking at where the price closes relative to its daily high and low range.
                
                **How it works:** Plotted in a separate panel below the price chart, the A/D Line multiplies the volume of a period by a multiplier based on the closing price. 
                If the price closes near the high of the day, volume is heavily added; if it closes near the low, volume is heavily subtracted.
                
                **What it tells you:** It reveals whether a trend is sustainable based on intra-period price resilience. It shows if buying power is truly sustaining the asset 
                through the closing bell.
                - **Buying vs. Selling Pressure:** A rising A/D line indicates strong accumulation, showing that buyers are dominant and pushing prices toward the top of their 
                daily range. A falling line indicates distribution and selling pressure.
                - **Breakout Validation:** If an asset breaks out of a consolidation pattern and the A/D line moves sharply upward alongside it, it confirms that the breakout 
                is authentic and heavily bought into by the market.
                
                **4. Money Flow Index (MFI)**
                
                **Primary Function:** Measures the momentum of money flowing into and out of an asset to identify overbought and oversold conditions.
                
                **How it works:** Plotted in a separate panel below the price chart, MFI is often called the "Volume-Weighted RSI." It incorporates both price action and volume 
                data into a mathematical formula that oscillates strictly between 0 and 100.
                
                **What it tells you:** It identifies when a market move has gone too far, too fast, and is running out of liquidity to sustain itself.
                **- Extreme Boundaries:** Traditional overbought levels occur above 80, signaling a potential pullback. Oversold levels occur below 20, signaling a potential bounce 
                or buying opportunity.
                **- MFI Divergence:** Just like RSI, if the stock price hits a new high but the MFI peaks at a lower high, money flow is quietly drying up, serving as a leading 
                indicator of an upcoming downside reversal.
                """
            )

        with col2:
            st.subheader("Price Action with 200-Day Simple Moving Average (SMA), On-Balance Volume (OBV), Accumulation/Distribution (A/D) & Money Flow Index (MFI) Charts")
            ma_obv_ad_mfi_fig= get_ma_obv_ad_mfi(historical_data)
            st.plotly_chart(ma_obv_ad_mfi_fig, width="stretch", height=1000)

        col1, col2 = st.columns(2)
        with col1:
            st.info(
                """
                **1. Price Action with 200-Day Exponential Moving Average (EMA)**
                        
                **Primary Function:** Identifies the structural market trend while giving greater weight to recent price changes 
                for faster trend tracking.

                **How it works:** Price Action focuses entirely on candlestick patterns, market structure (higher highs/lower lows), 
                and horizontal support and resistance lines without lagging indicators. Superimposed on this is the 200-Day Exponential
                Moving Average (EMA). Plotted directly on the price chart, the 200-Day EMA tracks the long-term trend but uses a mathematical 
                calculation that heavily weights the most recent data points, rather than treating all 200 days equally like a Simple 
                Moving Average (SMA).

                **What it tells you:** The 200-Day EMA is considered the ultimate indicator of the long-term trend. If the price is 
                above these lines, the market is in a structural bull market; if below, it is a bear market.
                - **Fast-Response Filter:** Because it adapts to recent price movements quicker, it helps traders spot 
                long-term trend reversals or macro shifts earlier, though it can occasionally result in more false signals (whipsaws) 
                during choppy markets.
                - **Institutional Reaction Zone:** Major institutions monitor this level closely. When a healthy asset pulls back and 
                consolidates right at the 200-Day EMA, it often indicates heavy institutional accumulation and serves as a highly reliable, 
                reactive entry point.

                **2. Moving Average Convergence Divergence (MACD)**

                **Primary Function:** Measures trend momentum shifts, direction, and potential reversal turning points.

                **How it works:** Plotted in a separate panel below the price chart, the MACD consists of three components: the MACD Line 
                (the difference between two fast moving averages (12-Day EMA and 26-Day EMA)), the Signal Line (a 9-Day moving average of 
                the MACD line itself), and the Histogram (the vertical bars measuring the distance between the two lines).

                **What it tells you:** When the MACD line crosses above the Signal Line, it creates a bullish momentum signal (Buy). 
                When it crosses below, it creates a bearish signal (Sell).
                - **The Zero Line Filter:** If the lines are above the center "Zero Line," the overall momentum is bullish. If they are below 
                the Zero Line, momentum is bearish.
                - **Momentum Strength (Histogram):** When the histogram bars are growing taller, momentum is accelerating. When they begin to 
                shrink or change color, it warns you that the current price push is losing its steam before the actual price reverses.
                """
            )

        with col2:
            st.subheader("Price Action with 200-Day Exponential Moving Averages (EMA) & Moving Average Convergence Divergence (MACD) Charts")
            ma_macd_fig= get_ma_macd(historical_data)
            st.plotly_chart(ma_macd_fig, width="stretch", height=700)

        col1, col2 = st.columns(2)
        with col1:
            st.info(
                """
                **1. Donchian Channels**
                
                **Primary Function:** Tracks market breakouts and visualizes the exact price range over a set period.
                
                **How it works:** It consists of three lines overlaying the price action. The upper band plots the highest price 
                achieved over a chosen timeframe (usually 20 periods), while the lower band plots the lowest price. The middle line 
                is simply the average of the two outer bands. Unlike Bollinger Bands, which change shape based on volatility, 
                Donchian Bands only move when price creates a new high or a new low.
                
                **What it tells you:** It serves as a visual boundary for breakouts. If price touches or pushes through the upper band, 
                a bullish breakout is occurring. If it hits the lower band, a bearish breakdown is underway. The middle line often acts 
                as dynamic support or resistance during an established trend. A 50-Day EMA is also plotted in the chart and it serves 2 purposes:
                - **Filtering False Breakouts:** If the price punches through the Upper Donchian Channel (a buy signal), but the price is still below 
                the 50-Day EMA, the line warns you that the broader trend is still bearish. You can avoid a false breakout by only taking long trades 
                when the price breaks the upper channel and is safely above the 50-Day EMA.
                - **Trailing Stop Loss:** Once you enter a breakout trade based on the Donchian Channel, you can use the 50-Day EMA line as your trailing stop. 
                As long as the candles close above the 50-Day EMA, you stay in the trade. The moment a candle closes on the opposite side of the line, you 
                exit with your profits.
                
                **2. Average Directional Index (ADX)**
                
                **Primary Function:** Measures the overall strength of a trend, completely independent of its direction.
                
                **How it works:** Displayed in the second panel as a single line fluctuating between 0 and 100. It is often accompanied 
                by two directional indicator lines (+DI and -DI) to show who is winning, but the core ADX line itself cares only about speed 
                and consistency of price movement.
                
                **What it tells you:** It acts as a filter to tell you whether you should use a trend-following strategy or a range-bound strategy.
                - **Below 20 to 25:** The market is weak, drifting sideways, or locked in a tight consolidation range.
                - **Above 25:** A strong trend has officially begun (either up or down).
                - **Above 40 or 50:** The trend is historically powerful or reaching an unsustainable climax.
                
                **3. Choppiness Index (CHOP)**
                
                **Primary Function:** Quantifies market "noisiness" to determine if the market is trending smoothly or chopping sideways.
                
                **How it works:** A specialized indicator that uses modern chaos theory to evaluate market structure. It moves strictly 
                between 0 and 100 on a panel below the price chart.
                
                **What it tells you:** It does not predict price direction; instead, it defines the market's current state of behavior using 
                two key mathematical thresholds:
                - **Above 61.8:** The market is extremely "choppy." It is moving sideways in an unpredictable, messy pattern. This signals that 
                energy is storing up and a major explosive breakout is near.
                - **Below 38.2:** The market is "smooth." It is in a highly efficient, one-directional trend. This tells you to ride the momentum 
                and avoid trying to fade or reverse the trend.
                """
            )

        with col2:
            st.subheader("Donchian Channels, Average Directional Index (ADX), & Choppiness Index (CHOP) Charts")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                donchian_period = st.slider("Donchian Period", min_value=5, max_value=50, value=20)
            with col_b:
                adx_period = st.slider("ADX Period", min_value=5, max_value=30, value=14)
            with col_c:
                chop_period = st.slider("CHOP Period", min_value=5, max_value=30, value=14)

            donchian_adi_chop_fig = get_donchian_adi_chop(historical_data, donchian_period, adx_period, chop_period)
            st.plotly_chart(donchian_adi_chop_fig, width="stretch", height=700)