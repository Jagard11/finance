import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import csv
import os
from time import sleep
from bs4 import BeautifulSoup

def get_nasdaq_symbols():
    print("Fetching NASDAQ symbols...")
    symbols = set()
    
    # Try FTP first
    try:
        ftp_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt"
        df = pd.read_csv(ftp_url, delimiter='|')
        symbols.update(df[df['Symbol'].str.len() <= 5]['Symbol'].tolist())
    except Exception as e:
        print(f"FTP fetch failed: {e}")
    
    # Try screener API as backup
    try:
        url = 'https://api.nasdaq.com/api/screener/stocks'
        params = {'download': 'true', 'exchange': 'NASDAQ'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if data.get('data', {}).get('rows'):
            symbols.update(row['symbol'] for row in data['data']['rows'])
    except Exception as e:
        print(f"API fetch failed: {e}")
    
    symbols = sorted(list(symbols))
    
    if not symbols:
        print("Using backup symbols")
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'HTGC']
    
    with open('available_symbols.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Symbol'])
        for symbol in symbols:
            writer.writerow([symbol])
    
    print(f"Found {len(symbols)} symbols")
    return symbols

def get_stock_info(symbol, current, total):
    print(f"\n[{current}/{total}] Attempting to fetch {symbol}...")
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        first_trade_date = datetime.fromtimestamp(info.get('firstTradeDateEpochUtc', 0))
        company_age = (datetime.now() - first_trade_date).days / 365
        dividend_yield = info.get('dividendYield', 0) * 100
        
        data = {
            # Basic Info
            'Symbol': symbol,
            'Name': info.get('longName', symbol),
            'Exchange': info.get('exchange', 'Unknown'),
            'Country': info.get('country', 'Unknown'),
            'Age': company_age,
            'Dividend_Yield': dividend_yield,
            'Fetch_Time': datetime.now().isoformat(),
            
            # Location & Contact
            'Address': info.get('address1', ''),
            'City': info.get('city', ''),
            'State': info.get('state', ''),
            'Zip': info.get('zip', ''),
            'Phone': info.get('phone', ''),
            'Website': info.get('website', ''),
            
            # Industry Info
            'Industry': info.get('industry', ''),
            'Sector': info.get('sector', ''),
            'Business_Summary': info.get('longBusinessSummary', ''),
            'Full_Time_Employees': info.get('fullTimeEmployees', 0),
            
            # Financial Metrics
            'Market_Cap': info.get('marketCap', 0),
            'Enterprise_Value': info.get('enterpriseValue', 0),
            'PE_Ratio': info.get('trailingPE', 0),
            'Forward_PE': info.get('forwardPE', 0),
            'Price_To_Book': info.get('priceToBook', 0),
            'Price_To_Sales': info.get('priceToSalesTrailing12Months', 0),
            'Profit_Margins': info.get('profitMargins', 0),
            'Current_Price': info.get('currentPrice', 0),
            'Target_Mean_Price': info.get('targetMeanPrice', 0),
            'Recommendation': info.get('recommendationKey', ''),
            'Num_Analysts': info.get('numberOfAnalystOpinions', 0),
            
            # Balance Sheet Items
            'Total_Cash': info.get('totalCash', 0),
            'Total_Debt': info.get('totalDebt', 0),
            'Quick_Ratio': info.get('quickRatio', 0),
            'Current_Ratio': info.get('currentRatio', 0),
            'Total_Revenue': info.get('totalRevenue', 0),
            'Debt_To_Equity': info.get('debtToEquity', 0),
            
            # Performance Metrics
            'ROA': info.get('returnOnAssets', 0),
            'ROE': info.get('returnOnEquity', 0),
            'Revenue_Growth': info.get('revenueGrowth', 0),
            'Gross_Margins': info.get('grossMargins', 0),
            'Operating_Margins': info.get('operatingMargins', 0),
            'Beta': info.get('beta', 0)
        }
        
        matches_criteria = (
            data['Country'] == 'United States' and 
            company_age >= 25 and 
            dividend_yield >= 8.0
        )
        
        if matches_criteria:
            print("*** MATCHES CRITERIA ***")
            
        return data, matches_criteria
        
    except Exception as e:
        print(f"Failed: {symbol} - Error: {str(e)}")
        return None, False

def main():
    print("=== NASDAQ High Dividend Stock Scanner ===")
    print("Criteria:\n- US Companies\n- Age > 25 years\n- Dividend Yield ≥ 8%\n")
    
    symbols = get_nasdaq_symbols()
    total_symbols = len(symbols)
    matches_found = 0
    
    # Define all fields
    fieldnames = [
        'Symbol', 'Name', 'Exchange', 'Country', 'Age', 'Dividend_Yield', 'Fetch_Time',
        'Address', 'City', 'State', 'Zip', 'Phone', 'Website',
        'Industry', 'Sector', 'Business_Summary', 'Full_Time_Employees',
        'Market_Cap', 'Enterprise_Value', 'PE_Ratio', 'Forward_PE', 'Price_To_Book',
        'Price_To_Sales', 'Profit_Margins', 'Current_Price', 'Target_Mean_Price',
        'Recommendation', 'Num_Analysts', 'Total_Cash', 'Total_Debt', 'Quick_Ratio',
        'Current_Ratio', 'Total_Revenue', 'Debt_To_Equity', 'ROA', 'ROE',
        'Revenue_Growth', 'Gross_Margins', 'Operating_Margins', 'Beta'
    ]
    
    # Create/clear the files
    for filename in ['all_stocks.csv', 'matching_stocks.csv']:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    
    for i, symbol in enumerate(symbols, 1):
        info, matches_criteria = get_stock_info(symbol, i, total_symbols)
        
        if info:
            # Save to all stocks file
            with open('all_stocks.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(info)
            
            # If matches criteria, save to matching stocks file
            if matches_criteria:
                matches_found += 1
                with open('matching_stocks.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(info)
        
        sleep(1)  # Rate limiting
    
    print(f"\nProcessing complete!")
    print(f"Total stocks processed: {total_symbols}")
    print(f"Matches found: {matches_found}")
    print(f"Results saved to all_stocks.csv and matching_stocks.csv")

if __name__ == "__main__":
    main()