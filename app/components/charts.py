import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_price_chart(
    prices: pd.DataFrame,
    title: str = "Historical Price",
):
    """
    Create an interactive price chart.
    """

    chart_data = prices.reset_index()

    chart_data = chart_data.melt(
        id_vars=chart_data.columns[0],
        var_name="Asset",
        value_name="Price",
    )

    date_column = chart_data.columns[0]

    fig = px.line(
        chart_data,
        x=date_column,
        y="Price",
        color="Asset",
        title=title,
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
    )

    return fig


def create_normalized_price_chart(
    prices: pd.DataFrame,
    title: str = "Normalized Performance",
):
    """
    Normalize asset prices to 100 at the beginning
    of the selected period.
    """

    normalized = (
        prices / prices.iloc[0]
    ) * 100

    chart_data = normalized.reset_index()

    chart_data = chart_data.melt(
        id_vars=chart_data.columns[0],
        var_name="Asset",
        value_name="Normalized Price",
    )

    date_column = chart_data.columns[0]

    fig = px.line(
        chart_data,
        x=date_column,
        y="Normalized Price",
        color="Asset",
        title=title,
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Normalized Value",
        hovermode="x unified",
    )

    return fig


def create_return_distribution(
    returns: pd.DataFrame,
    ticker: str,
):
    """
    Create return distribution histogram.
    """

    data = returns[ticker].dropna()

    fig = px.histogram(
        data,
        x=data,
        nbins=50,
        title=f"{ticker} Daily Return Distribution",
    )

    fig.update_layout(
        xaxis_title="Daily Return",
        yaxis_title="Frequency",
    )

    return fig


def create_risk_return_scatter(
    metrics_df
):

    fig = px.scatter(
        metrics_df,
        x="Volatility",
        y="Annual Return",
        text="Asset",
        hover_data=[
            "CAGR",
            "Volatility",
            "Sharpe Ratio",
            "Maximum Drawdown",
            "Sortino Ratio",
        ],
        title="Risk-Return Profile",
    )

    fig.update_traces(
        marker=dict(
            size=12
        ),
        textposition="top center",
    )

    fig.update_layout(
        xaxis_title="Annualized Volatility",
        yaxis_title="Annualized Return",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
    )

    return fig

def create_correlation_heatmap(
    correlation_matrix: pd.DataFrame,
):
    """
    Create correlation heatmap.
    """

    fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Asset Return Correlation Matrix",
    )

    fig.update_layout(
        xaxis_title="Asset",
        yaxis_title="Asset",
    )

    return fig


def create_rolling_volatility_chart(
    rolling_volatility: pd.DataFrame,
    window: int,
):
    """
    Create rolling volatility chart.
    """

    chart_data = rolling_volatility.reset_index()

    chart_data = chart_data.melt(
        id_vars=chart_data.columns[0],
        var_name="Asset",
        value_name="Volatility",
    )

    date_column = chart_data.columns[0]

    fig = px.line(
        chart_data,
        x=date_column,
        y="Volatility",
        color="Asset",
        title=f"{window}-Day Rolling Annualized Volatility",
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Annualized Volatility",
        hovermode="x unified",
    )

    fig.update_yaxes(
        tickformat=".0%"
    )

    return fig


def create_drawdown_chart(
    drawdown: pd.DataFrame,
):
    """
    Create drawdown chart.
    """

    chart_data = drawdown.reset_index()

    chart_data = chart_data.melt(
        id_vars=chart_data.columns[0],
        var_name="Asset",
        value_name="Drawdown",
    )

    date_column = chart_data.columns[0]

    fig = px.line(
        chart_data,
        x=date_column,
        y="Drawdown",
        color="Asset",
        title="Historical Drawdown",
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Drawdown",
        hovermode="x unified",
    )

    fig.update_yaxes(
        tickformat=".0%"
    )

    return fig