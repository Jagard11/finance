import yfinance as yf
import datetime
import json

def get_stock_details(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Calculate company age from first trade date
        first_trade = datetime.datetime.fromtimestamp(info.get('firstTradeDateEpochUtc', 0))
        age_years = (datetime.datetime.now() - first_trade).days / 365.25
        
        data = {
            'symbol': symbol,
            'market_cap': info.get('marketCap'),
            'age_years': age_years,
            'dividend_yield': info.get('dividendYield', 0) * 100,  # Convert to percentage
            'company_name': info.get('longName'),
            'first_trade_date': first_trade.strftime('%Y-%m-%d')
        }
        
        # Save data to file
        with open(f'{symbol}_details.json', 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Data saved to {symbol}_details.json")
        return data

    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

if __name__ == "__main__":
    data = get_stock_details('HTGC')
    if data:
        print(f"\nResults for {data['symbol']}:")
        print(f"Market Cap: ${data['market_cap']:,}")
        print(f"Age: {data['age_years']:.1f} years")
        print(f"Dividend Yield: {data['dividend_yield']:.2f}%")
        print(f"First Trade Date: {data['first_trade_date']}")