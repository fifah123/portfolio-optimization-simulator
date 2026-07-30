import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_efficient_frontier_chart(
    random_portfolios: pd.DataFrame,
    efficient_frontier: pd.DataFrame,
    optimal_portfolios: pd.DataFrame,
):
    """
    Create Efficient Frontier visualization.
    """

    fig = go.Figure()


    # ========================================================
    # Random Portfolios
    # ========================================================

    fig.add_trace(

        go.Scatter(

            x=
                random_portfolios[
                    "Volatility"
                ],

            y=
                random_portfolios[
                    "Return"
                ],

            mode="markers",

            marker={
                "size": 5,

                "color":
                    random_portfolios[
                        "Sharpe Ratio"
                    ],

                "colorscale":
                    "Viridis",

                "showscale":
                    True,

                "colorbar": {
                    "title":
                        "Sharpe Ratio"
                },

                "opacity":
                    0.5,
            },

            name=
                "Random Portfolios",

            hovertemplate=
                (
                    "Volatility: %{x:.2%}"
                    "<br>"
                    "Return: %{y:.2%}"
                    "<extra></extra>"
                ),
        )
    )


    # ========================================================
    # Efficient Frontier
    # ========================================================

    if not efficient_frontier.empty:

        fig.add_trace(

            go.Scatter(

                x=
                    efficient_frontier[
                        "Volatility"
                    ],

                y=
                    efficient_frontier[
                        "Return"
                    ],

                mode="lines",

                line={
                    "width":
                        4,
                },

                name=
                    "Efficient Frontier",
            )
        )


    # ========================================================
    # Optimal Portfolios
    # ========================================================

    for _, row in (
        optimal_portfolios.iterrows()
    ):

        fig.add_trace(

            go.Scatter(

                x=[
                    row[
                        "Volatility"
                    ]
                ],

                y=[
                    row[
                        "Return"
                    ]
                ],

                mode="markers+text",

                marker={
                    "size":
                        14,
                },

                text=[
                    row[
                        "Strategy"
                    ]
                ],

                textposition=
                    "top center",

                name=
                    row[
                        "Strategy"
                    ],

                hovertemplate=
                    (
                        "Strategy: "
                        + str(
                            row[
                                "Strategy"
                            ]
                        )
                        + "<br>"
                        "Return: %{y:.2%}"
                        "<br>"
                        "Volatility: %{x:.2%}"
                        "<extra></extra>"
                    ),
            )
        )


    # ========================================================
    # Layout
    # ========================================================

    fig.update_layout(

        title=
            "Efficient Frontier",

        xaxis_title=
            "Annualized Volatility (Risk)",

        yaxis_title=
            "Expected Annual Return",

        xaxis={
            "tickformat":
                ".0%"
        },

        yaxis={
            "tickformat":
                ".0%"
        },

        hovermode=
            "closest",

        height=
            650,
    )


    return fig