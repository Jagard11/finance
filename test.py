import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_and_plot_history(symbol):
    # Fetch data
    stock = yf.Ticker(symbol)
    hist = stock.history(period="25y")
    
    # Create plot
    plt.figure(figsize=(30,7))
    plt.plot(hist.index, hist['Close'])
    plt.title(f'{symbol} Stock Price History')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    
    # Save plot
    plt.savefig(f'{symbol}_history.png')
    
    # Save raw data
    hist.to_csv(f'{symbol}_history.csv')
    
    print(f"Saved history data and plot for {symbol}")

if __name__ == "__main__":
    fetch_and_plot_history('HTGC')