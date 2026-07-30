import pandas as pd

import plotly.graph_objects as go


def create_simulation_paths_chart(
    simulation_paths: pd.DataFrame,
    initial_value: float,
    max_paths: int = 100,
):
    """
    Plot individual Monte Carlo simulation paths.
    """

    fig = go.Figure()

    selected_columns = (

        simulation_paths.columns[
            :max_paths
        ]
    )

    for column in selected_columns:

        fig.add_trace(

            go.Scatter(

                x=
                    simulation_paths.index,

                y=
                    simulation_paths[
                        column
                    ],

                mode=
                    "lines",

                line={
                    "width":
                        0.7,
                },

                opacity=
                    0.15,

                showlegend=
                    False,
            )
        )

    fig.add_hline(

        y=
            initial_value,

        line_dash=
            "dash",

        annotation_text=
            "Initial Investment",
    )

    fig.update_layout(

        title=
            "Portfolio Simulation Paths",

        xaxis_title=
            "Date",

        yaxis_title=
            "Portfolio Value",

        height=
            600,
    )

    return fig


def create_percentile_chart(
    percentile_bands: pd.DataFrame,
):
    """
    Plot percentile bands for simulated
    portfolio outcomes.
    """

    fig = go.Figure()

    # 5th - 95th percentile range
    fig.add_trace(

        go.Scatter(

            x=
                percentile_bands.index,

            y=
                percentile_bands[
                    "95th Percentile"
                ],

            mode=
                "lines",

            line={
                "width":
                    0,
            },

            showlegend=
                False,
        )
    )

    fig.add_trace(

        go.Scatter(

            x=
                percentile_bands.index,

            y=
                percentile_bands[
                    "5th Percentile"
                ],

            mode=
                "lines",

            fill=
                "tonexty",

            name=
                "5th–95th Percentile",

            line={
                "width":
                    0,
            },
        )
    )

    # Median
    fig.add_trace(

        go.Scatter(

            x=
                percentile_bands.index,

            y=
                percentile_bands[
                    "Median"
                ],

            mode=
                "lines",

            name=
                "Median",

            line={
                "width":
                    3,
            },
        )
    )

    # 25th - 75th percentile
    fig.add_trace(

        go.Scatter(

            x=
                percentile_bands.index,

            y=
                percentile_bands[
                    "75th Percentile"
                ],

            mode=
                "lines",

            line={
                "width":
                    0,
            },

            showlegend=
                False,
        )
    )

    fig.add_trace(

        go.Scatter(

            x=
                percentile_bands.index,

            y=
                percentile_bands[
                    "25th Percentile"
                ],

            mode=
                "lines",

            fill=
                "tonexty",

            name=
                "25th–75th Percentile",

            line={
                "width":
                    0,
            },
        )
    )

    fig.update_layout(

        title=
            "Simulated Portfolio Outcome Range",

        xaxis_title=
            "Date",

        yaxis_title=
            "Portfolio Value",

        height=
            600,
    )

    return fig


def create_final_value_distribution(

    simulation_paths:
        pd.DataFrame,

):

    final_values = (

        simulation_paths

        .iloc[-1]

    )

    fig = go.Figure()

    fig.add_trace(

        go.Histogram(

            x=
                final_values,

            nbinsx=
                50,

            name=
                "Final Portfolio Value",
        )
    )

    fig.update_layout(

        title=
            "Distribution of Final Portfolio Values",

        xaxis_title=
            "Final Portfolio Value",

        yaxis_title=
            "Number of Simulations",

        height=
            500,
    )

    return fig