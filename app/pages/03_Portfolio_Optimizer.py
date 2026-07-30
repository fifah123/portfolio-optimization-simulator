import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# Project Root
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.append(
        str(PROJECT_ROOT)
    )


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
)

from src.optimization.base import (
    PortfolioOptimizer,
)

from src.optimization.equal_weight import (
    optimize_equal_weight,
)

from src.optimization.minimum_variance import (
    optimize_minimum_variance,
)

from src.optimization.maximum_sharpe import (
    optimize_maximum_sharpe,
)

from src.optimization.target_return import (
    optimize_target_return,
)

from app.components.portfolio import (
    create_allocation_chart,
    create_weights_bar_chart,
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Portfolio Optimizer",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# Header
# ============================================================

st.title(
    "📊 Portfolio Optimizer"
)

st.markdown(
    """
    Optimize asset allocation based on historical return,
    risk, and diversification.

    Select your investment objective and the optimizer will
    calculate the allocation proportion for each asset.
    """
)


# ============================================================
# Configuration
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
# Asset Metadata
# ============================================================

asset_df = get_asset_dataframe()


# ============================================================
# Sidebar
# ============================================================

st.sidebar.header(
    "Portfolio Configuration"
)


# ============================================================
# Asset Class
# ============================================================

asset_classes = sorted(
    asset_df[
        "asset_class"
    ].unique()
)

selected_asset_classes = (
    st.sidebar.multiselect(
        "Asset Class",
        options=asset_classes,
        default=asset_classes,
    )
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

selected_sectors = (
    st.sidebar.multiselect(
        "Sector",
        options=sectors,
        default=sectors,
    )
)


filtered_assets = filtered_assets[
    filtered_assets[
        "sector"
    ].isin(
        selected_sectors
    )
]


# ============================================================
# Tickers
# ============================================================

available_tickers = (
    filtered_assets[
        "ticker"
    ].tolist()
)


selected_tickers = (
    st.sidebar.multiselect(
        "Select Assets",
        options=available_tickers,
        default=available_tickers[:5],
    )
)


# ============================================================
# Date
# ============================================================

st.sidebar.subheader(
    "Historical Data"
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
# Optimization Strategy
# ============================================================

st.sidebar.subheader(
    "Optimization Strategy"
)


strategy = st.sidebar.selectbox(
    "Select Strategy",
    [
        "Equal Weight",
        "Minimum Variance",
        "Maximum Sharpe",
        "Target Return",
    ],
)


# ============================================================
# Risk-Free Rate
# ============================================================

risk_free_rate = (
    st.sidebar.number_input(
        "Risk-Free Rate",
        min_value=0.0,
        max_value=1.0,
        value=float(
            RISK_FREE_RATE
        ),
        step=0.005,
        format="%.3f",
    )
)


# ============================================================
# Weight Constraints
# ============================================================

st.sidebar.subheader(
    "Allocation Constraints"
)


min_weight = (
    st.sidebar.slider(
        "Minimum Weight",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
    )
)


max_weight = (
    st.sidebar.slider(
        "Maximum Weight",
        min_value=0.01,
        max_value=1.0,
        value=1.0,
        step=0.01,
    )
)


# ============================================================
# Target Return
# ============================================================

target_return = None


if strategy == "Target Return":

    target_return = (
        st.sidebar.number_input(
            "Target Annual Return",
            min_value=-1.0,
            max_value=2.0,
            value=0.10,
            step=0.01,
            format="%.2f",
        )
    )


# ============================================================
# Validation
# ============================================================

if len(
    selected_tickers
) < 2:

    st.warning(
        "Please select at least two assets."
    )

    st.stop()


if min_weight > max_weight:

    st.error(
        "Minimum weight cannot be greater "
        "than maximum weight."
    )

    st.stop()


if (
    len(selected_tickers)
    * min_weight
    > 1
):

    st.error(
        "Minimum allocation constraints are "
        "too high. The total minimum allocation "
        "must be <= 100%."
    )

    st.stop()


# ============================================================
# Load Data
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
        tickers=list(
            tickers
        ),
        start_date=str(
            start_date
        ),
        end_date=str(
            end_date
        ),
    )

    prices = clean_price_data(
        prices
    )

    return prices


try:

    prices = load_market_data(
        tuple(
            selected_tickers
        ),
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

daily_returns = (
    calculate_daily_returns(
        prices
    )
)


# ============================================================
# Expected Returns
# ============================================================

expected_returns = (
    calculate_annualized_returns(
        daily_returns,
        trading_days=TRADING_DAYS,
    )
)


# ============================================================
# Covariance Matrix
# ============================================================

covariance_matrix = (
    daily_returns.cov()
    * TRADING_DAYS
)


# ============================================================
# Create Optimizer
# ============================================================

optimizer = PortfolioOptimizer(
    expected_returns=expected_returns,
    covariance_matrix=covariance_matrix,
    risk_free_rate=risk_free_rate,
)


# ============================================================
# Run Optimization
# ============================================================

try:

    if strategy == "Equal Weight":

        weights, metrics = (
            optimize_equal_weight(
                optimizer
            )
        )


    elif strategy == "Minimum Variance":

        weights, metrics = (
            optimize_minimum_variance(
                optimizer,
                min_weight=min_weight,
                max_weight=max_weight,
            )
        )


    elif strategy == "Maximum Sharpe":

        weights, metrics = (
            optimize_maximum_sharpe(
                optimizer,
                min_weight=min_weight,
                max_weight=max_weight,
            )
        )


    elif strategy == "Target Return":

        weights, metrics = (
            optimize_target_return(
                optimizer,
                target_return=target_return,
                min_weight=min_weight,
                max_weight=max_weight,
            )
        )


except Exception as error:

    st.error(
        f"Portfolio optimization failed: {error}"
    )

    st.stop()


# ============================================================
# Portfolio Metrics
# ============================================================

st.subheader(
    f"Optimization Result: {strategy}"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Expected Annual Return",
        f"{metrics['Expected Return']:.2%}",
    )


with col2:

    st.metric(
        "Annualized Volatility",
        f"{metrics['Volatility']:.2%}",
    )


with col3:

    st.metric(
        "Sharpe Ratio",
        f"{metrics['Sharpe Ratio']:.2f}",
    )


# ============================================================
# Allocation Visualization
# ============================================================

st.divider()


col1, col2 = st.columns(
    [1, 1]
)


with col1:

    st.plotly_chart(
        create_allocation_chart(
            weights,
            title=(
                f"{strategy} "
                "Portfolio Allocation"
            ),
        ),
        width="stretch",
    )


with col2:

    st.plotly_chart(
        create_weights_bar_chart(
            weights,
            title=(
                "Asset Allocation Weights"
            ),
        ),
        width="stretch",
    )


# ============================================================
# Allocation Table
# ============================================================

st.subheader(
    "Recommended Asset Allocation"
)


allocation_df = pd.DataFrame(
    {
        "Asset": weights.index,
        "Weight": weights.values,
        "Expected Return": [
            expected_returns[
                asset
            ]
            for asset in weights.index
        ],
    }
)


allocation_df[
    "Contribution to Return"
] = (
    allocation_df[
        "Weight"
    ]
    * allocation_df[
        "Expected Return"
    ]
)


allocation_df = (
    allocation_df
    .sort_values(
        "Weight",
        ascending=False,
    )
)


st.dataframe(
    allocation_df.style.format(
        {
            "Weight": "{:.2%}",
            "Expected Return": "{:.2%}",
            "Contribution to Return": "{:.2%}",
        }
    ),
    width="stretch",
)


# ============================================================
# Portfolio Explanation
# ============================================================

st.divider()

st.subheader(
    "💡 Portfolio Interpretation"
)


if strategy == "Equal Weight":

    st.markdown(
        """
        The Equal Weight strategy allocates the same proportion
        of capital to every selected asset.

        This provides a simple baseline that can be compared
        against more sophisticated optimization strategies.
        """
    )


elif strategy == "Minimum Variance":

    st.markdown(
        """
        The Minimum Variance portfolio attempts to minimize
        portfolio volatility.

        This strategy may allocate more capital to assets that
        have lower volatility or provide strong diversification
        benefits through low correlations with other assets.
        """
    )


elif strategy == "Maximum Sharpe":

    st.markdown(
        """
        The Maximum Sharpe portfolio attempts to maximize
        risk-adjusted return.

        It considers both expected returns and portfolio
        volatility when determining asset allocation.
        """
    )


elif strategy == "Target Return":

    st.markdown(
        f"""
        The Target Return strategy attempts to achieve an
        annual return of **{target_return:.2%}** while minimizing
        portfolio risk.

        This approach is particularly useful when an investor
        has a specific investment objective and wants to find
        the allocation with the lowest possible volatility
        that satisfies that objective.
        """
    )


# ============================================================
# Formula Explanation
# ============================================================

with st.expander(
    "📐 View Optimization Methodology"
):

    st.markdown(
        """
        ### Portfolio Return

        The expected portfolio return is:

        $$
        E(R_p) = \\sum_{i=1}^{n} w_i E(R_i)
        $$

        where:

        - $w_i$ = portfolio weight of asset $i$
        - $E(R_i)$ = expected return of asset $i$

        ### Portfolio Variance

        Portfolio variance is:

        $$
        \\sigma_p^2 =
        w^T \\Sigma w
        $$

        where:

        - $w$ = vector of portfolio weights
        - $\\Sigma$ = covariance matrix

        ### Portfolio Volatility

        $$
        \\sigma_p =
        \\sqrt{w^T \\Sigma w}
        $$

        ### Sharpe Ratio

        $$
        Sharpe =
        \\frac{E(R_p) - R_f}
        {\\sigma_p}
        $$

        ### Target Return Optimization

        The optimization problem is:

        $$
        \\min_w
        \\quad
        w^T \\Sigma w
        $$

        subject to:

        $$
        \\sum_i w_i = 1
        $$

        and:

        $$
        E(R_p) \\geq R_{target}
        $$

        with allocation constraints:

        $$
        w_{min}
        \\leq
        w_i
        \\leq
        w_{max}
        $$
        """
    )


# ============================================================
# Disclaimer
# ============================================================

st.divider()

st.caption(
    """
    Disclaimer: This application is for educational and
    research purposes only. Historical returns and optimization
    results do not guarantee future performance and should not
    be considered financial advice.
    """
)