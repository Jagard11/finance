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
    def ensure_chart_dir(self, symbol):
        path = f"./charts/{symbol}"
        os.makedirs(path, exist_ok=True)
        return path

    def analyze_dividend_price_impact(self, hist, dividends):
        if dividends.empty:
            return pd.DataFrame()
        
        impacts = []
        for date, amount in dividends.items():
            try:
                # Get prices around dividend date
                start_date = date - timedelta(days=5)
                end_date = date + timedelta(days=5)
                period_prices = hist.loc[start_date:end_date]['Close']
                
                # Calculate price change
                pre_div_price = period_prices[:date].iloc[-1]
                post_div_price = period_prices[date:].iloc[0]
                price_change = ((post_div_price - pre_div_price) / pre_div_price) * 100
                
                impacts.append({
                    'date': date,
                    'dividend': amount,
                    'pre_price': pre_div_price,
                    'post_price': post_div_price,
                    'price_change': price_change
                })
            except Exception as e:
                logger.error(f"Error analyzing dividend impact for {date}: {e}")
                
        return pd.DataFrame(impacts)

    def analyze_dividend_history(self, dividends):
        if dividends.empty:
            return pd.DataFrame()
        
        annual_div = dividends.resample('Y').sum()
        div_changes = annual_div.pct_change() * 100
        
        # Calculate streak of consecutive dividend payments
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
        logger.info(f"Fetching price data for {symbol}")
        path = self.ensure_chart_dir(symbol)
        
        stock = yf.Ticker(symbol)
        hist = stock.history(period="max")
        dividends = stock.dividends
        
        if hist.empty:
            return None
            
        # Create subplot with price and dividend impact
        fig = sp.make_subplots(rows=2, cols=1, 
                              row_heights=[0.7, 0.3],
                              vertical_spacing=0.1)
                              
        # Price candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name="Price"
            ),
            row=1, col=1
        )
        
        # Add dividend markers
        if not dividends.empty:
            impacts_df = self.analyze_dividend_price_impact(hist, dividends)
            if not impacts_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=impacts_df['date'],
                        y=impacts_df['pre_price'],
                        mode='markers',
                        marker=dict(
                            symbol='triangle-down',
                            size=10,
                            color='orange'
                        ),
                        name="Dividend Dates"
                    ),
                    row=1, col=1
                )
                
                # Price impact chart
                fig.add_trace(
                    go.Bar(
                        x=impacts_df['date'],
                        y=impacts_df['price_change'],
                        name="Price Impact (%)"
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            title=f"{symbol} Price History and Dividend Impact",
            height=800,
            yaxis=dict(fixedrange=False),
            yaxis2=dict(fixedrange=False)
        )
        
        # Enable zooming for both y-axes
        fig.update_yaxes(fixedrange=False)
        
        return fig, hist, dividends

    def generate_dividend_chart(self, symbol, hist, dividends):
        if dividends.empty:
            return None
            
        annual_div, div_changes, streak = self.analyze_dividend_history(dividends)
        
        fig = sp.make_subplots(rows=2, cols=1,
                              row_heights=[0.6, 0.4],
                              vertical_spacing=0.1)
        
        # Annual dividend amounts
        fig.add_trace(
            go.Bar(
                x=annual_div.index.year,
                y=annual_div.values,
                name="Annual Dividend"
            ),
            row=1, col=1
        )
        
        # Year-over-year changes
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
        
        div_fig = self.generate_dividend_chart(symbol, hist, dividends)
        if div_fig:
            st.plotly_chart(div_fig, use_container_width=True)
            
            # Display dividend statistics
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