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
    col1, col2, col3 = st.columns(3)
    with col1:
        min_age = st.number_input("Minimum Age (Years)", value=25.0, step=1.0)
    with col2:
        min_dividend = st.number_input("Minimum Dividend Yield (%)", value=5.0, step=0.1)
    with col3:
        min_market_cap = st.number_input("Minimum Market Cap (Billions $)", value=1.0, step=0.1)

    filtered_df = table_view.filter_data(df, min_age, min_dividend, min_market_cap)
    st.write(f"Found {len(filtered_df)} matching stocks")

    tab1, tab2 = st.tabs(["Table", "Charts"])
    
    with tab1:
        table_view.render(filtered_df)
    
    with tab2:
        chart_view.render()