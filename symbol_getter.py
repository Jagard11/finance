import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def get_symbols_multiple_sources():
    results = {
        'ftp_nasdaqtrader': set(),
        'nasdaq_screener_api': set(),
        'nasdaq_traded_list': set(),
        'nasdaq_listed_list': set(),
        'yahoo_nasdaq_tickers': set()
    }
    
    # Method 1: FTP NasdaqTrader
    try:
        df = pd.read_csv("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt", delimiter='|')
        results['ftp_nasdaqtrader'].update(df[df['Symbol'].str.len() <= 5]['Symbol'].tolist())
    except Exception as e:
        print(f"FTP error: {e}")
    
    # Method 2: NASDAQ Screener API
    try:
        url = 'https://api.nasdaq.com/api/screener/stocks'
        params = {'download': 'true', 'exchange': 'NASDAQ'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data.get('data', {}).get('rows'):
            results['nasdaq_screener_api'].update(row['symbol'] for row in data['data']['rows'])
    except Exception as e:
        print(f"Screener API error: {e}")
    
    # Method 3: NASDAQ Traded List
    try:
        url = "http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"
        df = pd.read_csv(url, delimiter='|')
        results['nasdaq_traded_list'].update(df[df['Symbol'].str.len() <= 5]['Symbol'].tolist())
    except Exception as e:
        print(f"Traded list error: {e}")
    
    # Method 4: NASDAQ Listed
    try:
        url = "http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        df = pd.read_csv(url, delimiter='|')
        results['nasdaq_listed_list'].update(df[df['Symbol'].str.len() <= 5]['Symbol'].tolist())
    except Exception as e:
        print(f"Listed error: {e}")
    
    # Method 5: Yahoo Finance
    try:
        # Use yfinance to get NASDAQ symbols
        nasdaq = yf.Ticker('^IXIC')
        components = nasdaq.components
        if components:
            results['yahoo_nasdaq_tickers'].update(components)
    except Exception as e:
        print(f"Yahoo error: {e}")

    # Save results
    all_symbols = set().union(*results.values())
    
    with open('symbol_sources.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # Headers
        writer.writerow(['Symbol'] + list(results.keys()))
        
        # Data rows
        for symbol in sorted(all_symbols):
            row = [symbol] + [1 if symbol in source else 0 for source in results.values()]
            writer.writerow(row)
            
    print(f"Results saved to symbol_sources.csv")
    print("\nSymbols found by source:")
    for source, symbols in results.items():
        print(f"{source}: {len(symbols)}")
    print(f"Total unique symbols: {len(all_symbols)}")

if __name__ == "__main__":
    get_symbols_multiple_sources()