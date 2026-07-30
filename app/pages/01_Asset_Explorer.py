import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# Add project root to Python path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


# ============================================================
# Import project modules
# ============================================================

from src.data.loader import (
    get_asset_dataframe,
    get_asset_metadata,
    load_settings_config,
)

from src.data.downloader import (
    download_price_data,
)

from src.data.preprocessing import (
    clean_price_data,
)

from src.analytics.returns import (
    calculate_daily_returns,
    calculate_annualized_returns,
    calculate_cagr,
)

from src.analytics.risk import (
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
)

from app.components.charts import (
    create_price_chart,
    create_normalized_price_chart,
    create_return_distribution,
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Asset Explorer",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# Load Configuration
# ============================================================

settings = load_settings_config()

TRADING_DAYS = settings["data"]["trading_days_per_year"]

RISK_FREE_RATE = settings["analytics"]["risk_free_rate"]

DEFAULT_START_DATE = pd.to_datetime(
    settings["data"]["default_start_date"]
).date()


# ============================================================
# Header
# ============================================================

st.title("📈 Asset Explorer")

st.markdown(
    """
    Explore historical price movements, returns, volatility,
    and risk-adjusted performance of selected financial assets.
    
    This page provides the foundation for the portfolio optimization
    process by analyzing individual assets before constructing a portfolio.
    """
)


# ============================================================
# Asset Metadata
# ============================================================

asset_df = get_asset_dataframe()


# ============================================================
# Sidebar Filters
# ============================================================

st.sidebar.header("Asset Selection")

asset_classes = sorted(
    asset_df["asset_class"].unique()
)

selected_asset_classes = st.sidebar.multiselect(
    "Asset Class",
    options=asset_classes,
    default=asset_classes,
)


filtered_assets = asset_df[
    asset_df["asset_class"].isin(
        selected_asset_classes
    )
]


sectors = sorted(
    filtered_assets["sector"].unique()
)

selected_sectors = st.sidebar.multiselect(
    "Sector",
    options=sectors,
    default=sectors,
)


filtered_assets = filtered_assets[
    filtered_assets["sector"].isin(
        selected_sectors
    )
]


available_tickers = filtered_assets[
    "ticker"
].tolist()


selected_tickers = st.sidebar.multiselect(
    "Select Assets",
    options=available_tickers,
    default=available_tickers[:3],
)


# ============================================================
# Date Selection
# ============================================================

st.sidebar.subheader("Date Range")

start_date = st.sidebar.date_input(
    "Start Date",
    value=DEFAULT_START_DATE,
)

end_date = st.sidebar.date_input(
    "End Date",
    value=pd.Timestamp.today().date(),
)


# ============================================================
# Validation
# ============================================================

if not selected_tickers:

    st.warning(
        "Please select at least one asset."
    )

    st.stop()


if start_date >= end_date:

    st.error(
        "Start date must be earlier than end date."
    )

    st.stop()


# ============================================================
# Download Button
# ============================================================

download_button = st.sidebar.button(
    "🔄 Load Market Data",
    type="primary",
)


# ============================================================
# Data Loading Function
# ============================================================

@st.cache_data(
    show_spinner="Downloading market data..."
)
def load_market_data(
    tickers,
    start_date,
    end_date,
):

    prices = download_price_data(
        tickers=list(tickers),
        start_date=str(start_date),
        end_date=str(end_date),
    )

    prices = clean_price_data(
        prices
    )

    return prices


# ============================================================
# Load Data
# ============================================================

try:

    prices = load_market_data(
        tuple(selected_tickers),
        start_date,
        end_date,
    )

except Exception as error:

    st.error(
        f"Unable to load market data: {error}"
    )

    st.stop()


# ============================================================
# Calculate Analytics
# ============================================================

daily_returns = calculate_daily_returns(
    prices
)

annualized_returns = calculate_annualized_returns(
    daily_returns,
    trading_days=TRADING_DAYS,
)

cagr = calculate_cagr(
    prices
)

volatility = calculate_annualized_volatility(
    daily_returns,
    trading_days=TRADING_DAYS,
)

sharpe_ratio = calculate_sharpe_ratio(
    annualized_returns,
    volatility,
    risk_free_rate=RISK_FREE_RATE,
)

max_drawdown = calculate_max_drawdown(
    prices
)


# ============================================================
# Create Metrics DataFrame
# ============================================================

metrics_df = pd.DataFrame(
    {
        "Asset": selected_tickers,
        "Annual Return": annualized_returns,
        "CAGR": cagr,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Maximum Drawdown": max_drawdown,
    }
).set_index("Asset")


# ============================================================
# Overview
# ============================================================

st.subheader("📊 Asset Overview")

st.dataframe(
    metrics_df.style.format(
        {
            "Annual Return": "{:.2%}",
            "CAGR": "{:.2%}",
            "Volatility": "{:.2%}",
            "Sharpe Ratio": "{:.2f}",
            "Maximum Drawdown": "{:.2%}",
        }
    ),
    width="stretch",
)


# ============================================================
# Price Chart
# ============================================================

st.subheader("📈 Historical Price")

price_chart = create_price_chart(
    prices
)

st.plotly_chart(
    price_chart,
    width="stretch",
)


# ============================================================
# Normalized Performance
# ============================================================

st.subheader(
    "📊 Normalized Performance"
)

st.caption(
    "All assets are normalized to 100 at the beginning "
    "of the selected period."
)

normalized_chart = create_normalized_price_chart(
    prices
)

st.plotly_chart(
    normalized_chart,
    width="stretch",
)


# ============================================================
# Individual Asset Analysis
# ============================================================

st.subheader(
    "🔎 Individual Asset Analysis"
)

selected_asset = st.selectbox(
    "Select an asset",
    options=selected_tickers,
)


asset_metrics = metrics_df.loc[
    selected_asset
]


# ============================================================
# Metrics
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Annual Return",
        f"{asset_metrics['Annual Return']:.2%}",
    )


with col2:

    st.metric(
        "CAGR",
        f"{asset_metrics['CAGR']:.2%}",
    )


with col3:

    st.metric(
        "Volatility",
        f"{asset_metrics['Volatility']:.2%}",
    )


with col4:

    st.metric(
        "Sharpe Ratio",
        f"{asset_metrics['Sharpe Ratio']:.2f}",
    )


with col5:

    st.metric(
        "Max Drawdown",
        f"{asset_metrics['Maximum Drawdown']:.2%}",
    )


# ============================================================
# Return Distribution
# ============================================================

st.subheader(
    f"📉 {selected_asset} Return Distribution"
)

return_distribution = create_return_distribution(
    daily_returns,
    selected_asset,
)

st.plotly_chart(
    return_distribution,
    width="stretch",
)


# ============================================================
# Asset Information
# ============================================================

st.subheader(
    "ℹ️ Asset Information"
)

asset_metadata = get_asset_metadata()

metadata = asset_metadata[
    selected_asset
]

info_col1, info_col2, info_col3 = st.columns(3)


with info_col1:

    st.write(
        "**Asset Name**"
    )

    st.write(
        metadata["name"]
    )


with info_col2:

    st.write(
        "**Asset Class**"
    )

    st.write(
        metadata["asset_class"]
    )


with info_col3:

    st.write(
        "**Sector**"
    )

    st.write(
        metadata["sector"]
    )


# ============================================================
# Disclaimer
# ============================================================

st.divider()

st.caption(
    """
    Disclaimer: This application is for educational and research
    purposes only. Historical performance does not guarantee future
    results and should not be considered financial advice.
    """
)