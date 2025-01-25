# ./listGetter/listGetter.py 
 
import requests
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_symbols():
    url = 'https://api.nasdaq.com/api/screener/stocks'
    headers = {'User-Agent': 'Mozilla/5.0'}
    params = {'download': 'true'}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [{'symbol': row['symbol'], 'timestamp': datetime.now().isoformat()} 
                for row in data['data']['rows']]
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return []

def main():
    symbols = get_all_symbols()
    logger.info(f"Found {len(symbols)} symbols")
    
    df = pd.DataFrame(symbols)
    df.to_csv('symbols.csv', index=False)
    logger.info("Symbols written to symbols.csv")

if __name__ == "__main__":
    main()