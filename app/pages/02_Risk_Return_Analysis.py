import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# Project Root
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


# ============================================================
# Imports
# ============================================================

from src.data.loader import (
    get_asset_dataframe,
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
    calculate_downside_deviation,
    calculate_sortino_ratio,
    calculate_rolling_volatility,
    calculate_drawdown_series,
)

from src.analytics.correlation import (
    calculate_correlation_matrix,
)

from app.components.charts import (
    create_risk_return_scatter,
    create_correlation_heatmap,
    create_rolling_volatility_chart,
    create_drawdown_chart,
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Risk & Return Analysis",
    page_icon="⚖️",
    layout="wide",
)


# ============================================================
# Load Settings
# ============================================================

settings = load_settings_config()

TRADING_DAYS = settings[
    "data"
]["trading_days_per_year"]

RISK_FREE_RATE = settings[
    "analytics"
]["risk_free_rate"]

DEFAULT_START_DATE = pd.to_datetime(
    settings[
        "data"
    ]["default_start_date"]
).date()


# ============================================================
# Header
# ============================================================

st.title(
    "⚖️ Risk & Return Analysis"
)

st.markdown(
    """
    Analyze the relationship between investment return and risk
    across selected assets.

    This analysis helps identify assets that may be attractive
    individually and understand how diversification can reduce
    portfolio-level risk.
    """
)


# ============================================================
# Asset Metadata
# ============================================================

asset_df = get_asset_dataframe()


# ============================================================
# Sidebar
# ============================================================

st.sidebar.header(
    "Analysis Configuration"
)


# ============================================================
# Asset Class
# ============================================================

asset_classes = sorted(
    asset_df[
        "asset_class"
    ].unique()
)

selected_asset_classes = st.sidebar.multiselect(
    "Asset Class",
    options=asset_classes,
    default=asset_classes,
)


filtered_assets = asset_df[
    asset_df[
        "asset_class"
    ].isin(
        selected_asset_classes
    )
]


# ============================================================
# Sector
# ============================================================

sectors = sorted(
    filtered_assets[
        "sector"
    ].unique()
)

selected_sectors = st.sidebar.multiselect(
    "Sector",
    options=sectors,
    default=sectors,
)


filtered_assets = filtered_assets[
    filtered_assets[
        "sector"
    ].isin(
        selected_sectors
    )
]


available_tickers = filtered_assets[
    "ticker"
].tolist()


# ============================================================
# Ticker Selection
# ============================================================

selected_tickers = st.sidebar.multiselect(
    "Select Assets",
    options=available_tickers,
    default=available_tickers[:5],
)


# ============================================================
# Date Range
# ============================================================

st.sidebar.subheader(
    "Date Range"
)


start_date = st.sidebar.date_input(
    "Start Date",
    value=DEFAULT_START_DATE,
)


end_date = st.sidebar.date_input(
    "End Date",
    value=pd.Timestamp.today().date(),
)


# ============================================================
# Risk-Free Rate
# ============================================================

risk_free_rate = st.sidebar.number_input(
    "Risk-Free Rate",
    min_value=0.0,
    max_value=1.0,
    value=float(RISK_FREE_RATE),
    step=0.005,
    format="%.3f",
)


# ============================================================
# Rolling Window
# ============================================================

rolling_window = st.sidebar.slider(
    "Rolling Window (Days)",
    min_value=20,
    max_value=252,
    value=30,
    step=10,
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


if len(selected_tickers) < 2:

    st.info(
        "Select at least two assets to perform "
        "correlation and diversification analysis."
    )


# ============================================================
# Data Loading
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
# Calculate Returns
# ============================================================

daily_returns = calculate_daily_returns(
    prices
)


# ============================================================
# Calculate Risk and Return
# ============================================================

annualized_returns = (
    calculate_annualized_returns(
        daily_returns,
        trading_days=TRADING_DAYS,
    )
)


cagr = calculate_cagr(
    prices
)


volatility = (
    calculate_annualized_volatility(
        daily_returns,
        trading_days=TRADING_DAYS,
    )
)


sharpe_ratio = (
    calculate_sharpe_ratio(
        annualized_returns,
        volatility,
        risk_free_rate,
    )
)


max_drawdown = (
    calculate_max_drawdown(
        prices
    )
)


downside_deviation = (
    calculate_downside_deviation(
        daily_returns,
        target_return=0.0,
        trading_days=TRADING_DAYS,
    )
)


sortino_ratio = (
    calculate_sortino_ratio(
        annualized_returns,
        downside_deviation,
        risk_free_rate,
    )
)


# ============================================================
# Metrics DataFrame
# ============================================================

metrics_df = pd.DataFrame(
    {
        "Annual Return": annualized_returns,
        "CAGR": cagr,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Maximum Drawdown": max_drawdown,
        "Downside Deviation": downside_deviation,
        "Sortino Ratio": sortino_ratio,
    }
)


metrics_df.index.name = "Asset"


# ============================================================
# Page Tabs
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Risk-Return",
        "🔗 Correlation",
        "📉 Rolling Risk",
        "📉 Drawdown",
        "📋 Metrics",
    ]
)


# ============================================================
# TAB 1: Risk Return
# ============================================================

with tab1:

    st.subheader(
        "Risk-Return Profile"
    )

    st.markdown(
        """
        The chart compares annualized return against annualized
        volatility.

        Assets in the **upper-left area** generally have a more
        attractive historical risk-return profile because they
        achieved higher returns with lower volatility.
        """
    )

    risk_return_chart = (
        create_risk_return_scatter(
            metrics_df.reset_index()
        )
    )

    st.plotly_chart(
        risk_return_chart,
        width="stretch"
    )


    st.subheader(
        "Risk-Adjusted Performance"
    )


    col1, col2, col3 = st.columns(3)


    best_sharpe = (
        metrics_df[
            "Sharpe Ratio"
        ].idxmax()
    )

    best_return = (
        metrics_df[
            "Annual Return"
        ].idxmax()
    )

    lowest_risk = (
        metrics_df[
            "Volatility"
        ].idxmin()
    )


    with col1:

        st.metric(
            "Highest Sharpe Ratio",
            best_sharpe,
            f"{metrics_df.loc[best_sharpe, 'Sharpe Ratio']:.2f}",
        )


    with col2:

        st.metric(
            "Highest Annual Return",
            best_return,
            f"{metrics_df.loc[best_return, 'Annual Return']:.2%}",
        )


    with col3:

        st.metric(
            "Lowest Volatility",
            lowest_risk,
            f"{metrics_df.loc[lowest_risk, 'Volatility']:.2%}",
        )


# ============================================================
# TAB 2: Correlation
# ============================================================

with tab2:

    st.subheader(
        "Asset Return Correlation"
    )

    st.markdown(
        """
        Correlation measures how asset returns move relative
        to each other.

        - **+1**: Move in the same direction
        - **0**: Little linear relationship
        - **-1**: Move in opposite directions

        Lower correlations may provide greater diversification
        benefits when assets are combined into a portfolio.
        """
    )


    if len(selected_tickers) >= 2:

        correlation_matrix = (
            calculate_correlation_matrix(
                daily_returns
            )
        )


        correlation_chart = (
            create_correlation_heatmap(
                correlation_matrix
            )
        )


        st.plotly_chart(
            correlation_chart,
            width="stretch",
        )


        st.subheader(
            "Correlation Matrix"
        )


        st.dataframe(
            correlation_matrix.style.format(
                "{:.2f}"
            ),
            width="stretch",
        )


    else:

        st.warning(
            "Select at least two assets to view "
            "the correlation matrix."
        )


# ============================================================
# TAB 3: Rolling Risk
# ============================================================

with tab3:

    st.subheader(
        "Rolling Volatility"
    )

    st.markdown(
        f"""
        Rolling volatility shows how the risk of each asset
        changes over time using a **{rolling_window}-day window**.
        """
    )


    rolling_volatility = (
        calculate_rolling_volatility(
            daily_returns,
            window=rolling_window,
            trading_days=TRADING_DAYS,
        )
    )


    rolling_chart = (
        create_rolling_volatility_chart(
            rolling_volatility,
            rolling_window,
        )
    )


    st.plotly_chart(
        rolling_chart,
        width="stretch",
    )


# ============================================================
# TAB 4: Drawdown
# ============================================================

with tab4:

    st.subheader(
        "Historical Drawdown"
    )

    st.markdown(
        """
        Drawdown measures the decline from an asset's previous
        peak price.

        This helps identify historical periods of significant
        losses and the potential severity of downside risk.
        """
    )


    drawdown = (
        calculate_drawdown_series(
            prices
        )
    )


    drawdown_chart = (
        create_drawdown_chart(
            drawdown
        )
    )


    st.plotly_chart(
        drawdown_chart,
        width="stretch",
    )


# ============================================================
# TAB 5: Metrics
# ============================================================

with tab5:

    st.subheader(
        "Detailed Risk & Return Metrics"
    )


    st.dataframe(
        metrics_df.style.format(
            {
                "Annual Return": "{:.2%}",
                "CAGR": "{:.2%}",
                "Volatility": "{:.2%}",
                "Sharpe Ratio": "{:.2f}",
                "Maximum Drawdown": "{:.2%}",
                "Downside Deviation": "{:.2%}",
                "Sortino Ratio": "{:.2f}",
            }
        ),
        width="stretch",
    )


# ============================================================
# Interpretation
# ============================================================

st.divider()

st.subheader(
    "💡 Analysis Summary"
)


st.markdown(
    f"""
    Based on the selected historical period:

    - **Highest historical return:** {best_return}
    - **Lowest historical volatility:** {lowest_risk}
    - **Highest Sharpe Ratio:** {best_sharpe}

    The next step is to combine these individual assets into
    a portfolio. An asset with the highest return is not
    necessarily the best portfolio component. The correlation
    between assets and their contribution to total portfolio
    risk must also be considered.
    """
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