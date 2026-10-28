from datetime import datetime
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import streamlit as st

# Cached Function to load once into memory and shared across pages (No TTL needed, stays cached indefinitely in memory while the app runs)
@st.cache_resource(show_spinner=False)
def load_vader_analyzer():
    """Downloads lexicon once and caches the VADER analyzer instance in memory."""
    nltk.download("vader_lexicon", quiet=True)
    return SentimentIntensityAnalyzer()

# Function to calculate sentiment score from a text
def get_vader_sentiment(text):
    """Calculates compound sentiment score and assigns a label."""
    # Retrieve the cached instance (Instant lookup, no re-download or re-instantiation)
    sia = load_vader_analyzer()
    scores = sia.polarity_scores(text)
    compound = scores["compound"]
    
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
        
    return label, compound

# Cached Function to parse the raw news data and returns an organized news dataframe
@st.cache_data(ttl=3600, show_spinner=False)
def parse_news(raw_news):
    parsed_news = []

    # Slice the top 5 news items
    for item in raw_news[:5]:
        # Extract nested 'content' dict if it exists; otherwise fallback to root dict
        content = item.get("content", item)

        # 1. Title & Sentiment Analysis
        title = content.get("title", "N/A")
        sentiment_label, compound_score = get_vader_sentiment(title) if title != "N/A" else ("N/A", 0.0)

        # 2. Summary / Short Description
        summary = content.get("summary") or content.get("description", "N/A")

        # 3. URL / Link
        # Check canonicalUrl -> clickThroughUrl -> fallback link
        url_data = content.get("canonicalUrl") or content.get("clickThroughUrl")
        url = (
            url_data.get("url")
            if isinstance(url_data, dict)
            else url_data or content.get("link", "N/A")
        )

        # 4. Published Date Formatting
        # Handles ISO string ('pubDate') or UNIX epoch ('providerPublishTime')
        pub_date_raw = content.get("pubDate") or content.get("providerPublishTime")

        # Store explicit datetime object for sorting
        dt_obj = None
        if isinstance(pub_date_raw, (int, float)):
            dt_obj = datetime.fromtimestamp(pub_date_raw)
        elif isinstance(pub_date_raw, str):
            try:
                dt_obj = datetime.fromisoformat(pub_date_raw.replace("Z", "+00:00"))
            except ValueError:
                dt_obj = None

        # Format human-readable string
        pub_date_str = dt_obj.strftime("%d %B %Y") if dt_obj else "N/A"

        # 5. Relevant Info (Publisher / Provider)
        provider_data = content.get("provider")
        publisher = (
            provider_data.get("displayName")
            if isinstance(provider_data, dict)
            else content.get("publisher", "N/A")
        )

        parsed_news.append(
            {
                "Title": title,
                "Sentiment": sentiment_label,
                "Compound Score": round(compound_score, 3),
                "Publisher": publisher,
                "Published Date": pub_date_str,
                "dt_obj": dt_obj,  # Temporary column used strictly for sorting
                "Summary": summary,
                "URL": url
            }
        )

    # Format into a clean Pandas DataFrame for display
    news_df = pd.DataFrame(parsed_news)

    # Sort DataFrame: Latest to Oldest
    if "dt_obj" in news_df.columns:
        news_df = news_df.sort_values(by="dt_obj", ascending=False).drop(columns=["dt_obj"])

    # Reset index so Streamlit iteration starts cleanly from 0
    news_df = news_df.reset_index(drop=True)

    return news_df