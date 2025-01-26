# ./main.py
import streamlit as st
from table_view import TableView
from chart_view import ChartView

st.set_page_config(page_title="Stock Filter", layout="wide")
st.title("Stock Filter")

table_view = TableView()
chart_view = ChartView()

df = table_view.load_data()

if df is not None:
    with st.expander("Basic Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            min_age = st.number_input("Minimum Age (Years)", value=25.0, step=1.0)
        with col2:
            min_dividend = st.number_input("Minimum Dividend Yield (%)", value=5.0, step=0.1)
        with col3:
            min_market_cap = st.number_input("Minimum Market Cap (Billions $)", value=1.0, step=0.1)

    with st.expander("Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        with col1:
            max_pe = st.number_input("Maximum P/E Ratio", value=0.0, step=1.0)
            max_debt_equity = st.number_input("Maximum Debt/Equity Ratio", value=0.0, step=0.1)
        with col2:
            max_payout = st.number_input("Maximum Payout Ratio (%)", value=0.0, step=1.0)
            min_cash = st.number_input("Minimum Cash (Billions $)", value=0.0, step=0.1)
        with col3:
            min_fcf_yield = st.number_input("Minimum FCF Yield (%)", value=0.0, step=0.1)

    filtered_df = table_view.filter_data(
        df, min_age, min_dividend, min_market_cap,
        max_pe, max_debt_equity, max_payout,
        min_cash, min_fcf_yield
    )

    st.write(f"Found {len(filtered_df)} matching stocks")
    
    if not filtered_df.empty:
        st.selectbox("Select Stock", options=filtered_df['symbol'].tolist(), key='selected_symbol')

        tab1, tab2 = st.tabs(["Table", "Charts"])
        
        with tab1:
            table_view.render(filtered_df)
        
        with tab2:
            chart_view.render()