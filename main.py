import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import logging
import csv
import os
from time import sleep

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class StockScreener:
    def __init__(self):
        self.output_file = 'all_stocks.csv'
        self.fieldnames = ['symbol', 'name', 'market_cap', 'dividend_yield', 'age_years', 'exchange', 'timestamp']
        self.processed_symbols = set()
        self._initialize_file()
        self._load_processed_symbols()

    def _initialize_file(self):
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def _load_processed_symbols(self):
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                reader = csv.DictReader(f)
                self.processed_symbols = {row['symbol'] for row in reader}
            logger.info(f"Loaded {len(self.processed_symbols)} processed symbols")

    def get_symbols(self):
        url = 'https://api.nasdaq.com/api/screener/stocks'
        headers = {'User-Agent': 'Mozilla/5.0'}
        params = {'download': 'true'}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            all_symbols = [(row['symbol'], row.get('exchange', '')) for row in data['data']['rows']]
            return [(s, e) for s, e in all_symbols if s not in self.processed_symbols]
        except Exception as e:
            logger.error(f"Symbol fetch error: {e}")
            return []

    def process_stock(self, symbol_data):
        symbol, exchange = symbol_data
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', ''),
                'market_cap': info.get('marketCap', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'age_years': 0,
                'exchange': exchange,
                'timestamp': datetime.now().isoformat()
            }
            
            if 'firstTradeDateEpochUtc' in info:
                first_trade = pd.to_datetime(info['firstTradeDateEpochUtc'], unit='s')
                stock_data['age_years'] = (datetime.now() - first_trade).days / 365.25

            with open(self.output_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(stock_data)
                f.flush()
                os.fsync(f.fileno())
            
            self.processed_symbols.add(symbol)
            logger.info(f"Saved {symbol} ({exchange})")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return False

    def run(self):
        remaining_symbols = self.get_symbols()
        logger.info(f"Processing {len(remaining_symbols)} remaining symbols")
        
        try:
            for i, symbol_data in enumerate(remaining_symbols, 1):
                logger.info(f"Processing {i}/{len(remaining_symbols)}: {symbol_data[0]}")
                self.process_stock(symbol_data)
                sleep(1)
        except KeyboardInterrupt:
            logger.info("Program interrupted. Progress saved.")

if __name__ == "__main__":
    StockScreener().run()