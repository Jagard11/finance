# ./table_view.py
import streamlit as st
import pandas as pd

class TableView:
    @st.cache_data
    def load_data(_self):  # Added underscore to ignore self in caching
        try:
            df = pd.read_csv('all_stocks.csv', 
                            encoding='cp1252',
                            on_bad_lines='skip',
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

    def filter_data(self, df, min_age, min_dividend, min_market_cap):
        return df[
            (df['age_years'] >= min_age) &
            (df['dividend_yield'] >= min_dividend) &
            (df['market_cap'] >= min_market_cap * 1_000_000_000)
        ].copy()

    def render(self, filtered_df):
        if not filtered_df.empty:
            display_df = filtered_df.copy()
            display_df['market_cap'] = (display_df['market_cap'] / 1e9).round(2)
            
            selected = st.dataframe(
                display_df[['symbol', 'name', 'market_cap', 'dividend_yield', 'age_years']],
                hide_index=True,
                use_container_width=True
            )
            
            symbol = st.selectbox(
                "Select a stock for charts:",
                options=display_df['symbol'].tolist(),
                key='selected_symbol'
            )
            
            if st.button("Download Results"):
                st.download_button(
                    "Download CSV",
                    filtered_df.to_csv(index=False),
                    "filtered_stocks.csv",
                    "text/csv"
                )