import streamlit as st


def display_asset_metrics(
    ticker: str,
    metrics: dict,
):
    """
    Display key metrics for a selected asset.
    """

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Annual Return",
            f"{metrics['Annual Return']:.2%}",
        )

    with col2:
        st.metric(
            "CAGR",
            f"{metrics['CAGR']:.2%}",
        )

    with col3:
        st.metric(
            "Volatility",
            f"{metrics['Volatility']:.2%}",
        )

    with col4:
        st.metric(
            "Sharpe Ratio",
            f"{metrics['Sharpe Ratio']:.2f}",
        )

    st.metric(
        "Maximum Drawdown",
        f"{metrics['Maximum Drawdown']:.2%}",
    )