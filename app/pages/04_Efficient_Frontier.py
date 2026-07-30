import sys

from pathlib import Path

import numpy as np

import pandas as pd

import streamlit as st


# ============================================================
# Project Root
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


if str(
    PROJECT_ROOT
) not in sys.path:

    sys.path.append(
        str(
            PROJECT_ROOT
        )
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

from src.optimization.efficient_frontier import (
    generate_random_portfolios,
    calculate_efficient_frontier,
)

from app.components.efficient_frontier import (
    create_efficient_frontier_chart,
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(

    page_title=
        "Efficient Frontier",

    page_icon=
        "📈",

    layout=
        "wide",
)


# ============================================================
# Header
# ============================================================

st.title(
    "📈 Efficient Frontier"
)


st.markdown(
    """
    Explore the relationship between portfolio risk and
    expected return.

    The Efficient Frontier identifies portfolios that offer
    the highest expected return for a given level of risk,
    or equivalently, the lowest risk for a given expected
    return.
    """
)


# ============================================================
# Configuration
# ============================================================

settings = (
    load_settings_config()
)


TRADING_DAYS = (
    settings[
        "data"
    ][
        "trading_days_per_year"
    ]
)


RISK_FREE_RATE = (
    settings[
        "analytics"
    ][
        "risk_free_rate"
    ]
)


DEFAULT_START_DATE = (
    pd.to_datetime(
        settings[
            "data"
        ][
            "default_start_date"
        ]
    ).date()
)


# ============================================================
# Asset Metadata
# ============================================================

asset_df = (
    get_asset_dataframe()
)


# ============================================================
# Sidebar
# ============================================================

st.sidebar.header(
    "Frontier Configuration"
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

        options=
            asset_classes,

        default=
            asset_classes,
    )
)


filtered_assets = (
    asset_df[
        asset_df[
            "asset_class"
        ].isin(
            selected_asset_classes
        )
    ]
)


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

        options=
            sectors,

        default=
            sectors,
    )
)


filtered_assets = (

    filtered_assets[
        filtered_assets[
            "sector"
        ].isin(
            selected_sectors
        )
    ]
)


# ============================================================
# Assets
# ============================================================

available_tickers = (

    filtered_assets[
        "ticker"
    ].tolist()
)


selected_tickers = (

    st.sidebar.multiselect(

        "Select Assets",

        options=
            available_tickers,

        default=
            available_tickers[
                :5
            ],
    )
)


# ============================================================
# Date Range
# ============================================================

st.sidebar.subheader(
    "Historical Data"
)


start_date = (
    st.sidebar.date_input(

        "Start Date",

        value=
            DEFAULT_START_DATE,
    )
)


end_date = (
    st.sidebar.date_input(

        "End Date",

        value=
            pd.Timestamp
            .today()
            .date(),
    )
)


# ============================================================
# Portfolio Settings
# ============================================================

st.sidebar.subheader(
    "Portfolio Settings"
)


n_portfolios = (
    st.sidebar.slider(

        "Random Portfolios",

        min_value=
            1000,

        max_value=
            50000,

        value=
            10000,

        step=
            1000,
    )
)


min_weight = (
    st.sidebar.slider(

        "Minimum Asset Weight",

        min_value=
            0.0,

        max_value=
            0.5,

        value=
            0.0,

        step=
            0.01,
    )
)


max_weight = (
    st.sidebar.slider(

        "Maximum Asset Weight",

        min_value=
            0.1,

        max_value=
            1.0,

        value=
            1.0,

        step=
            0.05,
    )
)


frontier_points = (
    st.sidebar.slider(

        "Efficient Frontier Points",

        min_value=
            10,

        max_value=
            100,

        value=
            50,

        step=
            10,
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
        "Minimum weight cannot exceed "
        "maximum weight."
    )

    st.stop()


if (
    len(
        selected_tickers
    )
    * min_weight
    > 1
):

    st.error(
        "Minimum allocation constraints are "
        "too restrictive."
    )

    st.stop()


# ============================================================
# Load Market Data
# ============================================================

@st.cache_data(

    show_spinner=
        "Downloading market data..."
)
def load_market_data(

    tickers,

    start_date,

    end_date,
):

    prices = (
        download_price_data(

            tickers=
                list(
                    tickers
                ),

            start_date=
                str(
                    start_date
                ),

            end_date=
                str(
                    end_date
                ),
        )
    )


    prices = (
        clean_price_data(
            prices
        )
    )


    return prices


try:

    prices = (
        load_market_data(

            tuple(
                selected_tickers
            ),

            start_date,

            end_date,
        )
    )


except Exception as error:

    st.error(

        f"Unable to load "
        f"market data: {error}"
    )

    st.stop()


# ============================================================
# Returns
# ============================================================

daily_returns = (

    calculate_daily_returns(

        prices
    )
)


# ============================================================
# Expected Return
# ============================================================

expected_returns = (

    calculate_annualized_returns(

        daily_returns,

        trading_days=
            TRADING_DAYS,
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

optimizer = (

    PortfolioOptimizer(

        expected_returns=
            expected_returns,

        covariance_matrix=
            covariance_matrix,

        risk_free_rate=
            RISK_FREE_RATE,
    )
)


# ============================================================
# Generate Random Portfolios
# ============================================================

with st.spinner(

    "Generating random portfolios..."
):

    random_portfolios = (

        generate_random_portfolios(

            optimizer,

            n_portfolios=
                n_portfolios,

            min_weight=
                min_weight,

            max_weight=
                max_weight,
        )
    )


if random_portfolios.empty:

    st.error(

        "No valid random portfolios were "
        "generated. Try relaxing the allocation "
        "constraints."
    )

    st.stop()


# ============================================================
# Calculate Frontier
# ============================================================

min_return = (

    random_portfolios[
        "Return"
    ].min()
)


max_return = (

    random_portfolios[
        "Return"
    ].max()
)


target_returns = np.linspace(

    min_return,

    max_return,

    frontier_points,
)


with st.spinner(

    "Calculating efficient frontier..."
):

    efficient_frontier = (

        calculate_efficient_frontier(

            optimizer,

            target_returns,

            min_weight=
                min_weight,

            max_weight=
                max_weight,
        )
    )


# ============================================================
# Calculate Optimal Portfolios
# ============================================================

equal_weights, equal_metrics = (

    optimize_equal_weight(

        optimizer
    )
)


min_var_weights, min_var_metrics = (

    optimize_minimum_variance(

        optimizer,

        min_weight=
            min_weight,

        max_weight=
            max_weight,
    )
)


max_sharpe_weights, max_sharpe_metrics = (

    optimize_maximum_sharpe(

        optimizer,

        min_weight=
            min_weight,

        max_weight=
            max_weight,
    )
)


# ============================================================
# Optimal Portfolio DataFrame
# ============================================================

optimal_portfolios = pd.DataFrame(

    [

        {

            "Strategy":
                "Equal Weight",

            "Return":
                equal_metrics[
                    "Expected Return"
                ],

            "Volatility":
                equal_metrics[
                    "Volatility"
                ],

            "Sharpe Ratio":
                equal_metrics[
                    "Sharpe Ratio"
                ],
        },

        {

            "Strategy":
                "Minimum Variance",

            "Return":
                min_var_metrics[
                    "Expected Return"
                ],

            "Volatility":
                min_var_metrics[
                    "Volatility"
                ],

            "Sharpe Ratio":
                min_var_metrics[
                    "Sharpe Ratio"
                ],
        },

        {

            "Strategy":
                "Maximum Sharpe",

            "Return":
                max_sharpe_metrics[
                    "Expected Return"
                ],

            "Volatility":
                max_sharpe_metrics[
                    "Volatility"
                ],

            "Sharpe Ratio":
                max_sharpe_metrics[
                    "Sharpe Ratio"
                ],
        },
    ]
)


# ============================================================
# Efficient Frontier Chart
# ============================================================

st.subheader(
    "Risk-Return Opportunity Set"
)


fig = (

    create_efficient_frontier_chart(

        random_portfolios,

        efficient_frontier,

        optimal_portfolios,
    )
)


st.plotly_chart(

    fig,

    width="stretch",
)


# ============================================================
# Portfolio Comparison
# ============================================================

st.subheader(
    "Portfolio Strategy Comparison"
)


comparison_df = (

    optimal_portfolios.copy()
)


comparison_df[
    "Return"
] = (

    comparison_df[
        "Return"
    ].map(
        lambda x:
        f"{x:.2%}"
    )
)


comparison_df[
    "Volatility"
] = (

    comparison_df[
        "Volatility"
    ].map(
        lambda x:
        f"{x:.2%}"
    )
)


comparison_df[
    "Sharpe Ratio"
] = (

    comparison_df[
        "Sharpe Ratio"
    ].map(
        lambda x:
        f"{x:.2f}"
    )
)


st.dataframe(

    comparison_df,

    width="stretch",

    hide_index=
        True,
)


# ============================================================
# Tabs
# ============================================================

tab1, tab2, tab3 = st.tabs(

    [

        "📊 Portfolio Allocations",

        "📈 Frontier Data",

        "📐 Methodology",

    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    strategy = st.selectbox(

        "Select Portfolio",

        [

            "Equal Weight",

            "Minimum Variance",

            "Maximum Sharpe",

        ],

    )


    if strategy == "Equal Weight":

        selected_weights = (
            equal_weights
        )


    elif strategy == "Minimum Variance":

        selected_weights = (
            min_var_weights
        )


    else:

        selected_weights = (
            max_sharpe_weights
        )


    allocation_df = (

        selected_weights

        .reset_index()
    )


    allocation_df.columns = [

        "Asset",

        "Weight",

    ]


    allocation_df = (

        allocation_df

        .sort_values(

            "Weight",

            ascending=
                False,
        )
    )


    st.dataframe(

        allocation_df.style.format(

            {

                "Weight":
                    "{:.2%}"

            }
        ),

        width="stretch",

        hide_index=
            True,
    )


# ============================================================
# TAB 2
# ============================================================

with tab2:

    st.dataframe(

        efficient_frontier.style.format(

            {

                "Return":
                    "{:.2%}",

                "Volatility":
                    "{:.2%}",

                "Sharpe Ratio":
                    "{:.2f}",

            }
        ),

        width="stretch",

        hide_index=
            True,
    )


# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.markdown(

        """
        ## Efficient Frontier

        The Efficient Frontier represents portfolios that
        provide the highest expected return for each level
        of portfolio risk.

        ### Portfolio Return

        $$
        E(R_p) =
        \\sum_{i=1}^{n}
        w_i E(R_i)
        $$

        ### Portfolio Variance

        $$
        \\sigma_p^2 =
        w^T \\Sigma w
        $$

        ### Portfolio Volatility

        $$
        \\sigma_p =
        \\sqrt{
        w^T \\Sigma w
        }
        $$

        The frontier is calculated by minimizing portfolio
        variance for different target return levels.

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
        E(R_p) =
        R_{target}
        $$

        with:

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
# Summary
# ============================================================

st.divider()


st.subheader(
    "💡 Key Insights"
)


max_sharpe_return = (

    max_sharpe_metrics[
        "Expected Return"
    ]
)


max_sharpe_volatility = (

    max_sharpe_metrics[
        "Volatility"
    ]
)


min_var_volatility = (

    min_var_metrics[
        "Volatility"
    ]
)


st.markdown(

    f"""
    Based on the selected historical period:

    - The **Minimum Variance Portfolio** has an estimated
      annualized volatility of
      **{min_var_volatility:.2%}**.

    - The **Maximum Sharpe Portfolio** has an estimated
      annual return of
      **{max_sharpe_return:.2%}**.

    - The efficient frontier represents the theoretical set
      of portfolios that provide the best expected return
      for each level of risk.

    - Portfolios below the frontier are considered
      **inefficient**, because another portfolio may provide
      a higher return for the same level of risk.
    """
)


# ============================================================
# Disclaimer
# ============================================================

st.divider()


st.caption(

    """
    Disclaimer: This application is for educational and
    research purposes only. Efficient frontier calculations
    are based on historical data and assumptions about
    expected returns and covariance. They do not guarantee
    future performance and should not be considered financial
    advice.
    """
)