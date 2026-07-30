import numpy as np
import pandas as pd


def calculate_simulation_metrics(
    simulation_paths: pd.DataFrame,
    initial_value: float,
) -> dict:
    """
    Calculate summary statistics from
    simulation results.
    """

    final_values = (

        simulation_paths

        .iloc[-1]

        .dropna()
    )

    metrics = {

        "Initial Investment":
            initial_value,

        "Mean Final Value":
            final_values.mean(),

        "Median Final Value":
            final_values.median(),

        "Best Case":
            final_values.max(),

        "Worst Case":
            final_values.min(),

        "5th Percentile":
            final_values.quantile(
                0.05
            ),

        "25th Percentile":
            final_values.quantile(
                0.25
            ),

        "75th Percentile":
            final_values.quantile(
                0.75
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

        "Probability of Profit":
            (
                final_values
                > initial_value
            ).mean(),
    }

    return metrics


def calculate_percentile_bands(
    simulation_paths: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate percentile bands across
    all simulation paths.
    """

    return pd.DataFrame(

        {

            "5th Percentile":
                simulation_paths.quantile(
                    0.05,
                    axis=1,
                ),

            "25th Percentile":
                simulation_paths.quantile(
                    0.25,
                    axis=1,
                ),

            "Median":
                simulation_paths.quantile(
                    0.50,
                    axis=1,
                ),

            "75th Percentile":
                simulation_paths.quantile(
                    0.75,
                    axis=1,
                ),

            "95th Percentile":
                simulation_paths.quantile(
                    0.95,
                    axis=1,
                ),

        },

        index=
            simulation_paths.index,
    )