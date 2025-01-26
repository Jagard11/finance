# ./table_view.py
import streamlit as st
import pandas as pd

class TableView:
    @st.cache_data
    def load_data(_self):
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
                                'pe_ratio': float,
                                'debt_to_equity': float,
                                'payout_ratio': float,
                                'total_cash': float,
                                'free_cash_flow': float,
                                'free_cash_flow_yield': float,
                                'timestamp': str
                            })
            return df
        except Exception as e:
            st.error(f"Data loading error: {e}")
            return None

    def filter_data(self, df, min_age, min_dividend, min_market_cap, 
                   max_pe=None, max_debt_equity=None, max_payout=None, 
                   min_cash=None, min_fcf_yield=None):
        mask = (
            (df['age_years'] >= min_age) &
            (df['dividend_yield'] >= min_dividend) &
            (df['market_cap'] >= min_market_cap * 1_000_000_000)
        )
        
        if max_pe is not None and max_pe > 0:
            mask &= (df['pe_ratio'] <= max_pe)
        if max_debt_equity is not None and max_debt_equity > 0:
            mask &= (df['debt_to_equity'] <= max_debt_equity)
        if max_payout is not None and max_payout > 0:
            mask &= (df['payout_ratio'] <= max_payout)
        if min_cash is not None and min_cash > 0:
            mask &= (df['total_cash'] >= min_cash * 1_000_000_000)
        if min_fcf_yield is not None and min_fcf_yield > 0:
            mask &= (df['free_cash_flow_yield'] >= min_fcf_yield)
            
        return df[mask].copy()

    def render(self, filtered_df):
        if not filtered_df.empty:
            display_df = filtered_df.copy()
            display_df['market_cap'] = (display_df['market_cap'] / 1e9).round(2)
            display_df['total_cash'] = (display_df['total_cash'] / 1e9).round(2)
            display_df['free_cash_flow'] = (display_df['free_cash_flow'] / 1e9).round(2)
            
            columns_to_display = [
                'symbol', 'name', 'market_cap', 'dividend_yield', 'age_years',
                'pe_ratio', 'debt_to_equity', 'payout_ratio', 'total_cash',
                'free_cash_flow', 'free_cash_flow_yield'
            ]
            
            st.dataframe(
                display_df[columns_to_display],
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("Download Results"):
                st.download_button(
                    "Download CSV",
                    filtered_df.to_csv(index=False),
                    "filtered_stocks.csv",
                    "text/csv"
                )