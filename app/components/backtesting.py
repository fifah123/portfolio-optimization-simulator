import pandas as pd

import plotly.graph_objects as go


def create_equity_curve_chart(
    portfolio_values: pd.Series,
    benchmark_values: pd.Series | None = None,
):
    """
    Create portfolio equity curve.
    """

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=
                portfolio_values.index,

            y=
                portfolio_values.values,

            mode=
                "lines",

            name=
                "Portfolio",

        )
    )

    if benchmark_values is not None:

        fig.add_trace(

            go.Scatter(

                x=
                    benchmark_values.index,

                y=
                    benchmark_values.values,

                mode=
                    "lines",

                name=
                    "Benchmark",

            )
        )

    fig.update_layout(

        title=
            "Portfolio Growth vs Benchmark",

        xaxis_title=
            "Date",

        yaxis_title=
            "Portfolio Value",

        hovermode=
            "x unified",

        height=
            600,
    )

    return fig


def create_drawdown_chart(
    drawdown: pd.Series,
):
    """
    Create drawdown chart.
    """

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=
                drawdown.index,

            y=
                drawdown.values,

            mode=
                "lines",

            fill=
                "tozeroy",

            name=
                "Drawdown",

        )
    )

    fig.update_layout(

        title=
            "Portfolio Drawdown",

        xaxis_title=
            "Date",

        yaxis_title=
            "Drawdown",

        yaxis_tickformat=
            ".0%",

        height=
            500,
    )

    return fig


def create_rolling_metrics_chart(
    rolling_metrics: pd.DataFrame,
):
    """
    Create rolling volatility and Sharpe charts.
    """

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=
                rolling_metrics.index,

            y=
                rolling_metrics[
                    "Rolling_Volatility"
                ],

            mode=
                "lines",

            name=
                "Rolling Volatility",

        )
    )

    fig.add_trace(

        go.Scatter(

            x=
                rolling_metrics.index,

            y=
                rolling_metrics[
                    "Rolling_Sharpe"
                ],

            mode=
                "lines",

            name=
                "Rolling Sharpe",

            yaxis=
                "y2",

        )
    )

    fig.update_layout(

        title=
            "Rolling Risk Metrics",

        xaxis_title=
            "Date",

        yaxis={

            "title":
                "Volatility",

        },

        yaxis2={

            "title":
                "Sharpe Ratio",

            "overlaying":
                "y",

            "side":
                "right",

        },

        height=
            500,
    )

    return fig


def create_returns_chart(
    portfolio_returns: pd.Series,
):
    """
    Create cumulative return chart.
    """

    cumulative_returns = (

        1
        + portfolio_returns

    ).cumprod() - 1

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=
                cumulative_returns.index,

            y=
                cumulative_returns.values,

            mode=
                "lines",

            name=
                "Cumulative Return",

        )
    )

    fig.update_layout(

        title=
            "Cumulative Portfolio Return",

        xaxis_title=
            "Date",

        yaxis_title=
            "Cumulative Return",

        yaxis_tickformat=
            ".0%",

        height=
            500,
    )

    return fig