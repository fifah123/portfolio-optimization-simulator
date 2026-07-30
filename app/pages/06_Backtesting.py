import sys

from pathlib import Path

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

from src.backtesting.engine import (

    backtest_buy_and_hold,

    backtest_rebalanced,

    calculate_benchmark_value,

)

from src.backtesting.metrics import (

    calculate_performance_metrics,

    calculate_drawdown_series,

    calculate_rolling_metrics,

)

from app.components.backtesting import (

    create_equity_curve_chart,

    create_drawdown_chart,

    create_rolling_metrics_chart,

    create_returns_chart,

)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(

    page_title=
        "Portfolio Backtesting",

    page_icon=
        "📊",

    layout=
        "wide",

)


# ============================================================
# Header
# ============================================================

st.title(

    "📊 Portfolio Backtesting"
)


st.markdown(

    """
    Evaluate how an investment portfolio would have
    performed historically using real market data.

    The backtesting engine compares portfolio strategies
    against a benchmark and analyzes historical risk
    and performance.
    """
)


# ============================================================
# Load Settings
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


# ============================================================
# Asset Metadata
# ============================================================

asset_df = (

    get_asset_dataframe()

)


available_tickers = (

    asset_df[
        "ticker"
    ].tolist()

)


# ============================================================
# Sidebar
# ============================================================

st.sidebar.header(

    "Backtest Configuration"

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
# Dates
# ============================================================

st.sidebar.subheader(

    "Backtest Period"

)


start_date = (

    st.sidebar.date_input(

        "Start Date",

        value=
            pd.Timestamp(
                "2021-01-01"
            ).date(),

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
# Portfolio Strategy
# ============================================================

st.sidebar.subheader(

    "Portfolio Strategy"

)


strategy = (

    st.sidebar.selectbox(

        "Optimization Strategy",

        [

            "Equal Weight",

            "Minimum Variance",

            "Maximum Sharpe",

        ],

    )

)


# ============================================================
# Backtest Method
# ============================================================

backtest_method = (

    st.sidebar.selectbox(

        "Backtest Method",

        [

            "Buy & Hold",

            "Periodic Rebalancing",

        ],

    )

)


# ============================================================
# Rebalancing Frequency
# ============================================================

if (

    backtest_method

    ==

    "Periodic Rebalancing"

):

    rebalance_frequency = (

        st.sidebar.selectbox(

            "Rebalancing Frequency",

            [

                "D",

                "W",

                "M",

                "Q",

                "Y",

            ],

            format_func=lambda x: {

                "D":
                    "Daily",

                "W":
                    "Weekly",

                "M":
                    "Monthly",

                "Q":
                    "Quarterly",

                "Y":
                    "Yearly",

            }[
                x
            ],

        )

    )

else:

    rebalance_frequency = "M"


# ============================================================
# Initial Investment
# ============================================================

initial_value = (

    st.sidebar.number_input(

        "Initial Investment",

        min_value=
            100.0,

        value=
            100000.0,

        step=
            10000.0,

    )

)


# ============================================================
# Benchmark
# ============================================================

benchmark = (

    st.sidebar.selectbox(

        "Benchmark",

        [

            "SPY",

            "QQQ",

            "DIA",

        ],

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


# ============================================================
# Download Data
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

    return clean_price_data(

        prices

    )


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


    benchmark_prices = (

        load_market_data(

            (
                benchmark,
            ),

            start_date,

            end_date,

        )

    )


except Exception as error:

    st.error(

        f"Unable to load market data: "
        f"{error}"

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


expected_returns = (

    calculate_annualized_returns(

        daily_returns,

        trading_days=
            TRADING_DAYS,

    )

)


covariance_matrix = (

    daily_returns.cov()

    * TRADING_DAYS

)


# ============================================================
# Optimize Portfolio
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


if strategy == "Equal Weight":

    weights, optimization_metrics = (

        optimize_equal_weight(

            optimizer

        )

    )


elif strategy == "Minimum Variance":

    weights, optimization_metrics = (

        optimize_minimum_variance(

            optimizer

        )

    )


else:

    weights, optimization_metrics = (

        optimize_maximum_sharpe(

            optimizer

        )

    )


# ============================================================
# Portfolio Allocation
# ============================================================

st.subheader(

    "Portfolio Allocation"

)


allocation_df = (

    weights

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
# Backtest
# ============================================================

st.divider()


st.subheader(

    "Historical Backtest"

)


if (

    backtest_method

    ==

    "Buy & Hold"

):

    results = (

        backtest_buy_and_hold(

            prices=

                prices,

            weights=

                weights,

            initial_value=

                initial_value,

        )

    )


else:

    results = (

        backtest_rebalanced(

            prices=

                prices,

            weights=

                weights,

            initial_value=

                initial_value,

            rebalance_frequency=

                rebalance_frequency,

        )

    )


# ============================================================
# Benchmark
# ============================================================

benchmark_values = (

    calculate_benchmark_value(

        benchmark_prices[

            benchmark

        ],

        initial_value=

            initial_value,

    )

)


# Align benchmark
benchmark_values = (

    benchmark_values

    .reindex(

        results.index

    )

    .ffill()

)


# ============================================================
# Metrics
# ============================================================

portfolio_values = (

    results[

        "Portfolio_Value"

    ]

)


portfolio_returns = (

    results[

        "Portfolio_Return"

    ]

)


metrics = (

    calculate_performance_metrics(

        portfolio_values=

            portfolio_values,

        portfolio_returns=

            portfolio_returns,

        risk_free_rate=

            RISK_FREE_RATE,

        trading_days=

            TRADING_DAYS,

    )

)


# ============================================================
# Performance Metrics
# ============================================================

st.subheader(

    "Performance Summary"

)


col1, col2, col3, col4 = (

    st.columns(4)

)


col1.metric(

    "Final Value",

    f"${metrics['Final Value']:,.0f}",

)


col2.metric(

    "Total Return",

    f"{metrics['Total Return']:.2%}",

)


col3.metric(

    "CAGR",

    f"{metrics['CAGR']:.2%}",

)


col4.metric(

    "Sharpe Ratio",

    f"{metrics['Sharpe Ratio']:.2f}",

)


col5, col6, col7, col8 = (

    st.columns(4)

)


col5.metric(

    "Annualized Volatility",

    f"{metrics['Annualized Volatility']:.2%}",

)


col6.metric(

    "Maximum Drawdown",

    f"{metrics['Maximum Drawdown']:.2%}",

)


col7.metric(

    "Calmar Ratio",

    f"{metrics['Calmar Ratio']:.2f}",

)


col8.metric(

    "Positive Days",

    f"{metrics['Positive Days']:.2%}",

)


# ============================================================
# Equity Curve
# ============================================================

st.divider()


st.subheader(

    "Portfolio Growth"

)


equity_chart = (

    create_equity_curve_chart(

        portfolio_values=

            portfolio_values,

        benchmark_values=

            benchmark_values,

    )

)


st.plotly_chart(

    equity_chart,

    width="stretch",

)


# ============================================================
# Cumulative Return
# ============================================================

st.subheader(

    "Cumulative Return"

)


returns_chart = (

    create_returns_chart(

        portfolio_returns

    )

)


st.plotly_chart(

    returns_chart,

    width="stretch",

)


# ============================================================
# Drawdown
# ============================================================

st.subheader(

    "Drawdown Analysis"

)


drawdown = (

    calculate_drawdown_series(

        portfolio_values

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
# Rolling Metrics
# ============================================================

st.subheader(

    "Rolling Risk Analysis"

)


rolling_metrics = (

    calculate_rolling_metrics(

        portfolio_returns,

        window=

            TRADING_DAYS,

        trading_days=

            TRADING_DAYS,

    )

)


rolling_chart = (

    create_rolling_metrics_chart(

        rolling_metrics

    )

)


st.plotly_chart(

    rolling_chart,

    width="stretch",

)


# ============================================================
# Detailed Metrics
# ============================================================

st.divider()


st.subheader(

    "Detailed Performance Metrics"

)


metrics_df = (

    pd.DataFrame(

        {

            "Metric":

                list(
                    metrics.keys()
                ),

            "Value":

                list(
                    metrics.values()
                ),

        }

    )

)


st.dataframe(

    metrics_df,

    width="stretch",

    hide_index=
        True,

)


# ============================================================
# Portfolio Weights
# ============================================================

with st.expander(

    "View Portfolio Weights"

):

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
# Methodology
# ============================================================

st.divider()


with st.expander(

    "📚 Backtesting Methodology"

):

    st.markdown(

        """
        ### Buy & Hold

        The portfolio is constructed at the beginning
        of the backtest and is not rebalanced.

        This approach reflects an investor who purchases
        assets and holds them throughout the entire
        investment period.

        ---

        ### Periodic Rebalancing

        The portfolio is periodically rebalanced back
        to its target allocation.

        Available frequencies:

        - Daily
        - Weekly
        - Monthly
        - Quarterly
        - Yearly

        Rebalancing allows the portfolio to maintain
        the desired asset allocation.

        ---

        ### CAGR

        Compound Annual Growth Rate measures the
        annualized growth of the portfolio.

        $$
        CAGR =
        \\left(
        \\frac{V_{end}}
        {V_{start}}
        \\right)^{1/T}
        - 1
        $$

        ---

        ### Sharpe Ratio

        Measures risk-adjusted return.

        $$
        Sharpe =
        \\frac{R_p - R_f}
        {\\sigma_p}
        $$

        ---

        ### Maximum Drawdown

        Measures the largest decline from a historical
        peak to a subsequent trough.

        $$
        Drawdown_t =
        \\frac{V_t}
        {Peak_t}
        - 1
        $$

        ---

        ### Important Limitations

        Backtesting results do not guarantee future
        investment performance.

        The current implementation does not include:

        - Transaction costs
        - Taxes
        - Bid-ask spread
        - Slippage
        - Market impact
        - Delisted securities
        - Survivorship bias adjustments

        These factors should be considered in a more
        advanced version of the backtesting framework.
        """

    )


# ============================================================
# Disclaimer
# ============================================================

st.divider()


st.caption(

    """
    Disclaimer: This application is for educational and
    research purposes only. Historical backtesting results
    are hypothetical and should not be considered financial
    advice or a guarantee of future investment performance.
    """

)