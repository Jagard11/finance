import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

def create_stock_charts(input_file='potential_picks.csv', output_dir='stock_charts'):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read potential picks
    stocks_df = pd.read_csv(input_file)
    
    # Set date range (25 years from today)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*25)
    
    for _, stock in stocks_df.iterrows():
        symbol = stock['Symbol']
        try:
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            div_hist = ticker.dividends
            
            if len(hist) == 0:
                print(f"No data available for {symbol}")
                continue
            
            # Create subplot figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(36, 8), height_ratios=[2, 1])
            fig.suptitle(f'{symbol} - {stock["Name"]}', fontsize=16)
            
            # Price history plot
            ax1.plot(hist.index, hist['Close'], 'b-')
            ax1.set_title('Price History')
            ax1.set_ylabel('Price ($)')
            ax1.grid(True)
            
            # Dividend history plot
            if len(div_hist) > 0:
                yearly_div = div_hist.groupby(div_hist.index.year).sum()
                ax2.bar(yearly_div.index, yearly_div.values, color='g')
                ax2.set_title('Annual Dividend History')
                ax2.set_ylabel('Dividend ($)')
                ax2.grid(True)
            else:
                ax2.text(0.5, 0.5, 'No dividend history available', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax2.transAxes)
            
            # Adjust layout and save
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{symbol}_analysis.png'))
            plt.close()
            
            print(f"Generated charts for {symbol}")
            
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue

if __name__ == "__main__":
    create_stock_charts()