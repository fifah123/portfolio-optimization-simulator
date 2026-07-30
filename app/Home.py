import streamlit as st


st.set_page_config(
    page_title="Portfolio Optimization Simulator",
    page_icon="📊",
    layout="wide",
)


st.title(
    "📊 Portfolio Optimization & Diversification Simulator"
)


st.markdown(
    """
    ## Welcome

    This application explores quantitative portfolio construction
    and investment diversification using historical financial data.

    The project combines:

    - 📈 Historical market data analysis
    - 📊 Return and risk analysis
    - 🔗 Correlation and diversification
    - ⚙️ Portfolio optimization
    - 📐 Efficient Frontier
    - 🎲 Monte Carlo simulation
    - 🔄 Historical backtesting
    """
)


st.divider()


st.subheader(
    "🚀 Project Workflow"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Step 1",
        "Asset Explorer",
    )

    st.write(
        "Explore historical asset prices, "
        "returns, and risk metrics."
    )


with col2:

    st.metric(
        "Step 2",
        "Risk Analysis",
    )

    st.write(
        "Analyze risk, return, and correlation."
    )


with col3:

    st.metric(
        "Step 3",
        "Optimization",
    )

    st.write(
        "Find optimal portfolio allocation."
    )


with col4:

    st.metric(
        "Step 4",
        "Simulation",
    )

    st.write(
        "Simulate and backtest portfolio performance."
    )


st.divider()


st.info(
    """
    👈 Use the sidebar to navigate through the application.

    Start with **Asset Explorer** to understand the historical
    characteristics of individual assets before constructing
    an optimized portfolio.
    """
)


st.caption(
    """
    Educational and research project. Not financial advice.
    """
)