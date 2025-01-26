# ./chart_view.py
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ChartView:
    def __init__(self):
        self.cache_dir = "./chart_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_file(self, symbol):
        return os.path.join(self.cache_dir, f"{symbol}_data.pkl")

    def _is_cache_valid(self, cache_file):
        if not os.path.exists(cache_file):
            return False
        mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - mod_time < timedelta(days=1)

    def _get_stock_data(self, symbol):
        cache_file = self._get_cache_file(symbol)
        
        if self._is_cache_valid(cache_file):
            logger.info(f"Using cached data for {symbol}")
            data = pd.read_pickle(cache_file)
            return data['history'], data['dividends']
            
        logger.info(f"Fetching fresh data for {symbol}")
        stock = yf.Ticker(symbol)
        history = stock.history(period="max")
        dividends = stock.dividends
        
        data = {
            'history': history,
            'dividends': dividends
        }
        pd.to_pickle(data, cache_file)
        
        return history, dividends

    def analyze_dividend_price_impact(self, hist, dividends):
        if dividends.empty:
            return None, pd.DataFrame()
        
        impacts = []
        one_year_ago = pd.Timestamp.now(tz=dividends.index.tz) - pd.Timedelta(days=365)
        recent_divs = dividends[dividends.index > one_year_ago]
        
        for date, amount in recent_divs.items():
            try:
                start_date = date - pd.Timedelta(days=1)
                end_date = date + pd.Timedelta(days=1)
                period_prices = hist.loc[start_date:end_date]
                
                if not period_prices.empty:
                    open_price = period_prices['Open'].iloc[0]
                    close_price = period_prices['Close'].iloc[-1]
                    price_change = ((close_price - open_price) / open_price) * 100
                    
                    impacts.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Open': f'${open_price:.2f}',
                        'Close': f'${close_price:.2f}',
                        'Dividend': f'${amount:.2f}',
                        'Impact': f'{price_change:+.2f}%'
                    })
            except Exception as e:
                logger.error(f"Error analyzing dividend impact for {date}: {e}")
        
        if impacts:
            impacts_df = pd.DataFrame(impacts)
            avg_impact = np.mean([float(x['Impact'].rstrip('%')) for x in impacts])
            return avg_impact, impacts_df
        
        return None, pd.DataFrame()

    def analyze_dividend_history(self, dividends):
        if dividends.empty:
            return pd.DataFrame(), pd.DataFrame(), 0
        
        annual_div = dividends.resample('Y').sum()
        div_changes = annual_div.pct_change() * 100
        
        current_streak = 0
        prev_year = None
        
        for year in annual_div.index[::-1]:
            if prev_year is None or year.year == prev_year - 1:
                current_streak += 1
                prev_year = year.year
            else:
                break
                
        return annual_div, div_changes, current_streak

    def generate_price_chart(self, symbol):
        logger.info(f"Getting price data for {symbol}")
        
        hist, dividends = self._get_stock_data(symbol)
        if hist.empty:
            return None, hist, dividends
            
        fig = go.Figure(data=go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close']
        ))
        
        fig.update_layout(
            title=f"{symbol} Price History",
            height=600,
            yaxis=dict(fixedrange=False)
        )
        
        return fig, hist, dividends

    def generate_dividend_chart(self, symbol, hist, dividends):
        if dividends.empty:
            return None
            
        annual_div, div_changes, streak = self.analyze_dividend_history(dividends)
        
        fig = sp.make_subplots(rows=2, cols=1,
                              row_heights=[0.6, 0.4],
                              vertical_spacing=0.1)
        
        fig.add_trace(
            go.Bar(
                x=annual_div.index.year,
                y=annual_div.values,
                name="Annual Dividend"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=div_changes.index.year,
                y=div_changes.values,
                mode='lines+markers',
                name="YoY Change (%)"
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"{symbol} Dividend History (Current Streak: {streak} years)",
            height=600
        )
        
        return fig

    def render(self):
        if 'selected_symbol' not in st.session_state:
            st.write("Select a stock from the table to view charts")
            return
            
        symbol = st.session_state['selected_symbol']
        price_fig, hist, dividends = self.generate_price_chart(symbol)
        
        if price_fig:
            st.plotly_chart(price_fig, use_container_width=True)
            
            avg_impact, impacts_df = self.analyze_dividend_price_impact(hist, dividends)
            if not impacts_df.empty:
                st.write("### Dividend Price Impact Analysis (Last 12 Months)")
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    st.dataframe(impacts_df, hide_index=True)
                with col2:
                    st.metric("12-Month Average Price Impact", f"{avg_impact:+.2f}%")
            
            div_fig = self.generate_dividend_chart(symbol, hist, dividends)
            if div_fig:
                st.plotly_chart(div_fig, use_container_width=True)
                
                annual_div, div_changes, streak = self.analyze_dividend_history(dividends)
                if not annual_div.empty:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Annual Dividend Rate", 
                                f"${annual_div.iloc[-1]:.2f}")
                    with col2:
                        st.metric("5-Year Average Growth",
                                f"{div_changes.tail(5).mean():.1f}%")
                    with col3:
                        st.metric("Consecutive Payment Years", streak)