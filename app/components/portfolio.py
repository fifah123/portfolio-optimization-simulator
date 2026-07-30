import pandas as pd
import plotly.express as px


def create_allocation_chart(
    weights: pd.Series,
    title: str = "Portfolio Allocation",
):

    allocation = (
        weights
        .reset_index()
    )

    allocation.columns = [
        "Asset",
        "Weight",
    ]

    allocation = allocation[
        allocation["Weight"] > 0.0001
    ]

    fig = px.pie(
        allocation,
        names="Asset",
        values="Weight",
        title=title,
        hole=0.4,
    )

    fig.update_traces(
        texttemplate="%{label}<br>%{percent}",
        hovertemplate=(
            "%{label}<br>"
            "Weight: %{value:.2%}"
        ),
    )

    return fig


def create_weights_bar_chart(
    weights: pd.Series,
    title: str = "Asset Allocation",
):

    allocation = (
        weights
        .sort_values(
            ascending=True
        )
        .reset_index()
    )

    allocation.columns = [
        "Asset",
        "Weight",
    ]

    fig = px.bar(
        allocation,
        x="Weight",
        y="Asset",
        orientation="h",
        title=title,
        text="Weight",
    )

    fig.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside",
    )

    fig.update_xaxes(
        tickformat=".0%",
        title="Portfolio Weight",
    )

    return fig


def create_strategy_comparison(
    comparison_df: pd.DataFrame,
):

    chart_data = (
        comparison_df
        .reset_index()
        .melt(
            id_vars="Strategy",
            var_name="Metric",
            value_name="Value",
        )
    )

    fig = px.bar(
        chart_data,
        x="Strategy",
        y="Value",
        color="Metric",
        barmode="group",
        title="Portfolio Strategy Comparison",
    )

    return fig