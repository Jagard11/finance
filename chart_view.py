# ./chart_view.py
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ChartView:
    def ensure_chart_dir(self, symbol):
        path = f"./charts/{symbol}"
        os.makedirs(path, exist_ok=True)
        return path

    def generate_price_chart(self, symbol):
        logger.info(f"Fetching price data for {symbol}")
        path = self.ensure_chart_dir(symbol)
        
        stock = yf.Ticker(symbol)
        hist = stock.history(period="max")  # Changed from 5y to max
        
        if hist.empty:
            return None
            
        fig = go.Figure(data=go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close']
        ))
        
        fig.update_layout(
            title=f"{symbol} Price History",
            height=400
        )
        fig.write_image(f"{path}/price_chart.png")
        hist.to_csv(f"{path}/price_data.csv")
        
        return fig

    def generate_dividend_chart(self, symbol):
        logger.info(f"Fetching dividend data for {symbol}")
        path = self.ensure_chart_dir(symbol)
        
        stock = yf.Ticker(symbol)
        dividends = stock.dividends
        
        if dividends.empty:
            return None
            
        fig = go.Figure(data=go.Scatter(
            x=dividends.index,
            y=dividends.values,
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title=f"{symbol} Dividend History",
            height=400
        )
        fig.write_image(f"{path}/dividend_chart.png")
        dividends.to_csv(f"{path}/dividend_data.csv")
        
        return fig

    def render(self):
        if 'selected_symbol' not in st.session_state:
            st.write("### Select a stock ticker for price chart")
            st.write("### Select a stock ticker for dividend chart")
        else:
            symbol = st.session_state['selected_symbol']
            price_fig = self.generate_price_chart(symbol)
            if price_fig:
                st.plotly_chart(price_fig, use_container_width=True)
            
            div_fig = self.generate_dividend_chart(symbol)
            if div_fig:
                st.plotly_chart(div_fig, use_container_width=True)