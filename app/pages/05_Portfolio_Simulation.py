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

from src.simulation.monte_carlo import (
    simulate_gbm_portfolio,
)

from src.simulation.historical import (
    simulate_historical_bootstrap,
)

from src.simulation.scenario import (
    simulate_scenario,
)

from src.simulation.metrics import (
    calculate_simulation_metrics,
    calculate_percentile_bands,
)

from app.components.simulation import (
    create_simulation_paths_chart,
    create_percentile_chart,
    create_final_value_distribution,
)


# ============================================================
# Currency Formatting
# ============================================================

def format_idr(value):
    """
    Format numeric value as Indonesian Rupiah.

    Examples:
        100000000  -> Rp100.000.000
        125000000  -> Rp125.000.000
        -5000000   -> -Rp5.000.000
    """

    value = float(value)

    if value < 0:
        return (
            f"-Rp{abs(value):,.0f}"
            .replace(",", ".")
        )

    return (
        f"Rp{value:,.0f}"
        .replace(",", ".")
    )


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Portfolio Simulation",
    page_icon="🔮",
    layout="wide",
)


# ============================================================
# Header
# ============================================================

st.title(
    "🔮 Portfolio Simulation"
)

st.markdown(
    """
    Simulate potential future portfolio outcomes using
    historical market data and probabilistic models.

    This page answers the question:

    > **"If I invest this amount with this portfolio allocation,
    > what could my portfolio value look like in the future?"**
    """
)


# ============================================================
# Settings
# ============================================================

settings = load_settings_config()

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

asset_df = get_asset_dataframe()


# ============================================================
# Sidebar
# ============================================================

st.sidebar.header(
    "Simulation Configuration"
)


# ============================================================
# Asset Selection
# ============================================================

available_tickers = (
    asset_df[
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
# Historical Data
# ============================================================

st.sidebar.subheader(
    "Historical Data"
)

start_date = (
    st.sidebar.date_input(
        "Start Date",
        value=pd.Timestamp(
            "2021-01-01"
        ).date(),
    )
)

end_date = (
    st.sidebar.date_input(
        "End Date",
        value=pd.Timestamp.today().date(),
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
        "Select Portfolio",
        [
            "Equal Weight",
            "Minimum Variance",
            "Maximum Sharpe",
        ],
    )
)


# ============================================================
# Simulation Settings
# ============================================================

st.sidebar.subheader(
    "Simulation Settings"
)


initial_value = (
    st.sidebar.number_input(
        "Initial Investment (IDR)",
        min_value=1_000_000.0,
        value=100_000_000.0,
        step=5_000_000.0,
        format="%.0f",
    )
)


years = (
    st.sidebar.slider(
        "Investment Horizon (Years)",
        min_value=1,
        max_value=30,
        value=5,
    )
)


simulations = (
    st.sidebar.slider(
        "Number of Simulations",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100,
    )
)


# ============================================================
# Simulation Method
# ============================================================

simulation_method = (
    st.sidebar.selectbox(
        "Simulation Method",
        [
            "Monte Carlo GBM",
            "Historical Bootstrap",
        ],
    )
)


# ============================================================
# Validation
# ============================================================

if len(selected_tickers) < 2:

    st.warning(
        "Please select at least two assets."
    )

    st.stop()


if start_date >= end_date:

    st.error(
        "Start date must be earlier than end date."
    )

    st.stop()


# ============================================================
# Load Data
# ============================================================

@st.cache_data(
    show_spinner="Downloading historical data..."
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

    return clean_price_data(
        prices
    )


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

daily_returns = (
    calculate_daily_returns(
        prices
    )
)

expected_returns = (
    calculate_annualized_returns(
        daily_returns,
        trading_days=TRADING_DAYS,
    )
)

covariance_matrix = (
    daily_returns.cov()
    * TRADING_DAYS
)


# ============================================================
# Portfolio Optimizer
# ============================================================

optimizer = (
    PortfolioOptimizer(
        expected_returns=expected_returns,
        covariance_matrix=covariance_matrix,
        risk_free_rate=RISK_FREE_RATE,
    )
)


# ============================================================
# Select Portfolio
# ============================================================

if strategy == "Equal Weight":

    weights, metrics = (
        optimize_equal_weight(
            optimizer
        )
    )

elif strategy == "Minimum Variance":

    weights, metrics = (
        optimize_minimum_variance(
            optimizer
        )
    )

else:

    weights, metrics = (
        optimize_maximum_sharpe(
            optimizer
        )
    )


# ============================================================
# Portfolio Returns
# ============================================================

portfolio_daily_returns = (
    daily_returns @ weights
)

portfolio_return = (
    metrics[
        "Expected Return"
    ]
)

portfolio_volatility = (
    metrics[
        "Volatility"
    ]
)


# ============================================================
# Portfolio Summary
# ============================================================

st.subheader(
    "Selected Portfolio"
)

col1, col2, col3, col4 = (
    st.columns(4)
)


col1.metric(
    "Initial Investment",
    format_idr(
        initial_value
    ),
)


col2.metric(
    "Expected Annual Return",
    f"{portfolio_return:.2%}",
)


col3.metric(
    "Annual Volatility",
    f"{portfolio_volatility:.2%}",
)


col4.metric(
    "Sharpe Ratio",
    f"{metrics['Sharpe Ratio']:.2f}",
)


# ============================================================
# Portfolio Allocation
# ============================================================

with st.expander(
    "View Portfolio Allocation",
    expanded=False,
):

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
            ascending=False,
        )
    )

    # Calculate IDR allocation
    allocation_df[
        "Investment (IDR)"
    ] = (
        allocation_df[
            "Weight"
        ]
        * initial_value
    )

    st.dataframe(

        allocation_df.style.format(

            {
                "Weight":
                    "{:.2%}",

                "Investment (IDR)":
                    format_idr,
            }
        ),

        width="stretch",
        hide_index=True,
    )


# ============================================================
# Run Simulation
# ============================================================

st.divider()

st.subheader(
    "Simulation Results"
)


if simulation_method == "Monte Carlo GBM":

    with st.spinner(
        "Running Monte Carlo simulation..."
    ):

        simulation_paths = (
            simulate_gbm_portfolio(
                initial_value=initial_value,
                portfolio_return=portfolio_return,
                portfolio_volatility=portfolio_volatility,
                years=years,
                simulations=simulations,
                trading_days=TRADING_DAYS,
            )
        )


else:

    with st.spinner(
        "Running historical bootstrap simulation..."
    ):

        simulation_paths = (
            simulate_historical_bootstrap(
                initial_value=initial_value,
                portfolio_returns=portfolio_daily_returns,
                years=years,
                simulations=simulations,
                trading_days=TRADING_DAYS,
            )
        )


# ============================================================
# Calculate Metrics
# ============================================================

simulation_metrics = (
    calculate_simulation_metrics(
        simulation_paths,
        initial_value,
    )
)


percentile_bands = (
    calculate_percentile_bands(
        simulation_paths
    )
)


# ============================================================
# Outcome Metrics
# ============================================================

st.subheader(
    "Potential Outcomes"
)


col1, col2, col3, col4 = (
    st.columns(4)
)


col1.metric(
    "Median Final Value",
    format_idr(
        simulation_metrics[
            "Median Final Value"
        ]
    ),
)


col2.metric(
    "Mean Final Value",
    format_idr(
        simulation_metrics[
            "Mean Final Value"
        ]
    ),
)


col3.metric(
    "5th Percentile",
    format_idr(
        simulation_metrics[
            "5th Percentile"
        ]
    ),
)


col4.metric(
    "95th Percentile",
    format_idr(
        simulation_metrics[
            "95th Percentile"
        ]
    ),
)


# ============================================================
# Simulation Charts
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "Simulation Paths",
        "Outcome Range",
        "Final Value Distribution",
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    fig_paths = (
        create_simulation_paths_chart(
            simulation_paths,
            initial_value,
            max_paths=min(
                100,
                simulations,
            ),
        )
    )

    st.plotly_chart(
        fig_paths,
        width="stretch",
    )


# ============================================================
# TAB 2
# ============================================================

with tab2:

    fig_percentile = (
        create_percentile_chart(
            percentile_bands
        )
    )

    st.plotly_chart(
        fig_percentile,
        width="stretch",
    )


# ============================================================
# TAB 3
# ============================================================

with tab3:

    fig_distribution = (
        create_final_value_distribution(
            simulation_paths
        )
    )

    st.plotly_chart(
        fig_distribution,
        width="stretch",
    )


# ============================================================
# Risk Metrics
# ============================================================

st.subheader(
    "Simulation Risk Analysis"
)

risk_col1, risk_col2 = (
    st.columns(2)
)


risk_col1.metric(
    "Probability of Profit",
    f"{simulation_metrics['Probability of Profit']:.2%}",
)


risk_col2.metric(
    "Probability of Loss",
    f"{simulation_metrics['Probability of Loss']:.2%}",
)


# ============================================================
# Scenario Analysis
# ============================================================

st.divider()

st.subheader(
    "Scenario Analysis"
)

st.markdown(
    """
    Compare the potential outcome of your portfolio
    under different market assumptions.
    """
)


scenario_results = []


for scenario_name in [
    "Bear",
    "Base",
    "Bull",
]:

    scenario_paths = (
        simulate_scenario(
            initial_value=initial_value,
            portfolio_return=portfolio_return,
            portfolio_volatility=portfolio_volatility,
            scenario=scenario_name,
            years=years,
            simulations=simulations,
            trading_days=TRADING_DAYS,
        )
    )

    final_values = (
        scenario_paths
        .iloc[-1]
    )

    scenario_results.append(
        {
            "Scenario":
                scenario_name,

            "Mean Final Value":
                final_values.mean(),

            "Median Final Value":
                final_values.median(),

            "5th Percentile":
                final_values.quantile(
                    0.05
                ),

            "95th Percentile":
                final_values.quantile(
                    0.95
                ),

            "Probability of Loss":
                (
                    final_values
                    < initial_value
                ).mean(),
        }
    )


scenario_df = pd.DataFrame(
    scenario_results
)


st.dataframe(

    scenario_df.style.format(

        {
            "Mean Final Value":
                format_idr,

            "Median Final Value":
                format_idr,

            "5th Percentile":
                format_idr,

            "95th Percentile":
                format_idr,

            "Probability of Loss":
                "{:.2%}",
        }
    ),

    width="stretch",

    hide_index=True,
)


# ============================================================
# Methodology
# ============================================================

st.divider()


with st.expander(
    "📚 Methodology & Assumptions"
):

    st.markdown(
        """
        ### Monte Carlo GBM

        The Monte Carlo simulation uses Geometric Brownian
        Motion to model future portfolio values.

        The process is:

        $$
        S_{t+1}
        =
        S_t
        \\times
        e^{
        (\\mu - \\frac{1}{2}\\sigma^2)dt
        +
        \\sigma\\sqrt{dt}Z
        }
        $$

        Where:

        - $S_t$ = Portfolio value at time $t$
        - $\\mu$ = Expected annual return
        - $\\sigma$ = Annualized volatility
        - $dt$ = Time step
        - $Z$ = Random standard normal variable

        ---

        ### Historical Bootstrap

        Historical Bootstrap randomly samples daily returns
        from the observed historical return distribution.

        This method preserves some characteristics of the
        historical return distribution, including non-normal
        observations.

        ---

        ### Scenario Analysis

        The scenario model applies adjustments to the expected
        return and volatility.

        - **Bear:** Lower return and higher volatility
        - **Base:** Historical estimates
        - **Bull:** Higher return and lower volatility

        These scenarios are simplified assumptions and should
        not be interpreted as forecasts.

        ---

        ### Important Limitations

        Simulation results are highly dependent on:

        1. Historical data period
        2. Expected return assumptions
        3. Volatility estimates
        4. Correlation between assets
        5. Number of simulations
        6. Simulation horizon

        Historical performance does not guarantee future
        investment returns.
        """
    )


# ============================================================
# Disclaimer
# ============================================================

st.divider()

st.caption(
    """
    Disclaimer: This application is for educational and
    research purposes only. Simulation results are hypothetical
    and should not be considered financial advice or a
    guarantee of future investment performance.
    """
)