import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
import ssl
from time import sleep

def get_nasdaq_screener():
    try:
        url = 'https://api.nasdaq.com/api/screener/stocks'
        headers = {'User-Agent': 'Mozilla/5.0'}
        params = {'download': 'true'}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return [row['symbol'] for row in data['data']['rows']]
    except Exception as e:
        print(f"NASDAQ Screener error: {e}")
        return []

def get_nasdaq_listed():
    try:
        # Using requests instead of pd.read_csv for SSL handling
        url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
        response = requests.get(url, verify=False)
        lines = response.text.split('\n')[1:-1]  # Skip header and footer
        return [line.split('|')[0] for line in lines if line]
    except Exception as e:
        print(f"NASDAQ Listed error: {e}")
        return []

def get_nasdaq_traded():
    try:
        url = "https://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"
        response = requests.get(url, verify=False)
        lines = response.text.split('\n')[1:-1]
        return [line.split('|')[0] for line in lines if line]
    except Exception as e:
        print(f"NASDAQ Traded error: {e}")
        return []

def get_yahoo_symbols():
    try:
        tickers = yf.Tickers("AAPL MSFT").tickers
        available = []
        for symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "HTGC"]:
            try:
                info = yf.Ticker(symbol).info
                if info:
                    available.append(symbol)
                sleep(0.5)
            except:
                continue
        return available
    except Exception as e:
        print(f"Yahoo error: {e}")
        return []

def get_marketwatch_symbols():
    try:
        url = 'https://www.marketwatch.com/investing/stocks/companylist'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        symbols = []
        for row in soup.select('td.symbolcol a'):
            symbols.append(row.text.strip())
        return symbols
    except Exception as e:
        print(f"MarketWatch error: {e}")
        return []

def main():
    # Disable SSL verification warnings
    requests.packages.urllib3.disable_warnings()
    
    sources = {
        'NASDAQ_Screener': get_nasdaq_screener(),
        'NASDAQ_Listed': get_nasdaq_listed(),
        'NASDAQ_Traded': get_nasdaq_traded(),
        'Yahoo': get_yahoo_symbols(),
        'MarketWatch': get_marketwatch_symbols()
    }

    # Create DataFrame with a column for each source
    df = pd.DataFrame()
    
    # Add each source as a column
    for source_name, symbols in sources.items():
        df[source_name] = pd.Series(symbols)

    # Save to CSV
    df.to_csv('symbols.csv', index=False)
    
    # Print statistics
    print("\nSymbols found per source:")
    for source, symbols in sources.items():
        print(f"{source}: {len(symbols)}")
        
    # Verify HTGC presence
    for source, symbols in sources.items():
        if 'HTGC' in symbols:
            print(f"\nHTGC found in {source}")
            
    print(f"\nFile saved as symbols.csv")

if __name__ == "__main__":
    main()