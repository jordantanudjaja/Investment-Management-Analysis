# Investment-Management-Analysis

![GitHub stars](https://img.shields.io/github/stars/jordantanudjaja/Investment-Management-Analysis?style=for-the-badge&logo=github) ![GitHub forks](https://img.shields.io/github/forks/jordantanudjaja/Investment-Management-Analysis?style=for-the-badge&logo=github) ![GitHub issues](https://img.shields.io/github/issues/jordantanudjaja/Investment-Management-Analysis?style=for-the-badge&logo=github) ![Last commit](https://img.shields.io/github/last-commit/jordantanudjaja/Investment-Management-Analysis?style=for-the-badge&logo=github)

## 📑 Table of Contents

- [Description](#description)
- [Project Structure](#project-structure)
- [Features](#features)
- [Python Tech Stack](#python-tech-stack)

## 📝 Description

A streamlit project that scrapes the yfinance API and serves as an all-in-one terminal for retail investors and analysts, enabling data ingestion, advanced financial modeling, algorithmic technical analysis, and multi-asset portfolio optimization across stocks, funds (ETFs/Mutual Funds), currencies (Forex), cryptocurrency, options, and futures.

## 📁 Project Structure

```
.
├── main.py
├── src
│   ├── __init__.py
│   ├── currencies
│   │   ├── cross_currencies_analysis.py
│   │   ├── cryptocurrency_analysis.py
│   │   ├── fiat_currency_analysis.py
│   │   └── raw_data_scraper.py
│   ├── equities
│   │   ├── competitor_analysis.py
│   │   ├── financial_statements.py
│   │   ├── fundamental_analysis.py
│   │   ├── raw_data_scraper.py
│   │   └── valuation_models.py
│   ├── funds
│   │   ├── cross_fund_analysis.py
│   │   ├── fundamental_analysis.py
│   │   └── raw_data_scraper.py
│   ├── futures
│   │   ├── comparative_market_analysis.py
│   │   ├── historical_chart.py
│   │   └── raw_data_scraper.py
│   ├── macroeconomy
│   │   ├── global_market_analysis.py
│   │   └── modern_portfolio_theory.py
│   ├── options
│   │   ├── pricing_model.py
│   │   ├── quantitative_analysis.py
│   │   └── raw_data_scraper.py
│   └── shared
│       ├── finance_utils.py
│       ├── macroeconomic_metrics.py
│       ├── news_parser.py
│       └── technical_analysis.py
└── views
    ├── currencies
    │   ├── comparative_tokenomics_analysis.py
    │   ├── crypto_technical_analysis.py
    │   ├── cryptocurrency.py
    │   ├── foreign_exchange.py
    │   ├── forex_technical_analysis.py
    │   └── relative_currency_strength_analysis.py
    ├── equities
    │   ├── discounted_cash_flow.py
    │   ├── dividend_discount_model.py
    │   ├── equities_competitor_analysis.py
    │   ├── equities_fundamental_analysis.py
    │   ├── equities_technical_analysis.py
    │   └── financial_statements_keywords.py
    ├── funds
    │   ├── funds_fundamental_analysis.py
    │   ├── funds_technical_analysis.py
    │   └── peer_analysis.py
    ├── futures
    │   ├── commodities_cma.py
    │   ├── commodities_technical_analysis.py
    │   └── commodity_futures.py
    ├── macroeconomy
    │   ├── financial_markets.py
    │   └── portfolio_management.py
    └── options
        ├── option_greeks.py
        ├── option_profile.py
        └── strategy_simulator.py
```

## 🛠️ Features

- <b>Macroeconomic Overview:</b> A section that displays the relevant analytics of the global financial markets and runs the Modern Portfolio Theory analysis
- <b>Equities Analysis:</b> A section dedicated to equity analytics
- <b>Investment Funds Analysis:</b> A section dedicated to fund analytics
- <b>Currencies Analysis:</b> A section dedicated to both forex currency and cryptocurrency analytics
- <b>Options Analysis:</b> A section dedicated to options analytics
- <b>Futures Analysis:</b> A section dedicated to futures analytics

## 💻 Python Tech Stack

- <b>UI/Framework:</b> Streamlit
- <b>API:</b> Yfinance
- <b>Data Pipelines:</b> Pandas, NumPy, SciPy
- <b>Visualization:</b> Plotly
- <b>Natural Language Processing:</b> Nltk