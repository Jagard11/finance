import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('all_stocks.csv', 
                        encoding='cp1252',
                        on_bad_lines='skip',  # Skip problematic rows
                        dtype={
                            'symbol': str,
                            'name': str,
                            'market_cap': float,
                            'dividend_yield': float,
                            'age_years': float,
                            'timestamp': str
                        })
        return df
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None

st.set_page_config(page_title="Stock Filter", layout="wide")
st.title("Stock Filter")

df = load_data()

if df is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        min_age = st.number_input("Minimum Age (Years)", value=25.0, step=1.0)
    with col2:
        min_dividend = st.number_input("Minimum Dividend Yield (%)", value=5.0, step=0.1)
    with col3:
        min_market_cap = st.number_input("Minimum Market Cap (Billions $)", value=1.0, step=0.1)

    filtered_df = df[
        (df['age_years'] >= min_age) &
        (df['dividend_yield'] >= min_dividend) &
        (df['market_cap'] >= min_market_cap * 1_000_000_000)
    ].copy()

    st.write(f"Found {len(filtered_df)} matching stocks")

    if not filtered_df.empty:
        display_df = filtered_df.copy()
        display_df['market_cap'] = (display_df['market_cap'] / 1e9).round(2)
        st.dataframe(
            display_df[['symbol', 'name', 'market_cap', 'dividend_yield', 'age_years']],
            hide_index=True
        )
        
        if st.button("Download Results"):
            st.download_button(
                "Download CSV",
                filtered_df.to_csv(index=False),
                "filtered_stocks.csv",
                "text/csv"
            )