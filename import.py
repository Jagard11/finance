import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import csv
import os
from time import sleep
from bs4 import BeautifulSoup


def get_nasdaq_symbols():
    print("Fetching NASDAQ symbols from FTP...")
    try:
        ftp_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"
        df = pd.read_csv(ftp_url, delimiter='|')
        symbols = df[df['Symbol'].str.len() <= 5]['Symbol'].tolist()
        
        # Save symbols to CSV
        with open('available_symbols.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol'])
            for symbol in symbols:
                writer.writerow([symbol])
                
        print(f"Found {len(symbols)} NASDAQ symbols")
        return symbols
        
    except Exception as e:
        print(f"Error fetching from FTP: {str(e)}")
        backup_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'HTGC']
        
        with open('available_symbols.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Symbol'])
            for symbol in backup_symbols:
                writer.writerow([symbol])
                
        print(f"Using {len(backup_symbols)} backup symbols")
        return backup_symbols