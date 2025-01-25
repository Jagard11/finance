import pandas as pd

def filter_stocks(input_file='all_stocks.csv', output_file='potential_picks.csv'):
    # Read the CSV
    df = pd.read_csv(input_file)
    
    # Apply filters
    filtered_df = df[
        (df['Dividend_Yield'] > 5) &
        (df['Age'] >= 25) &
        (df['Market_Cap'] > 1_000_000_000)
    ]
    
    # Sort by dividend yield
    filtered_df = filtered_df.sort_values('Dividend_Yield', ascending=False)
    
    # Select relevant columns
    columns = [
        'Symbol', 'Name', 'Exchange', 'Dividend_Yield', 'Age', 
        'Market_Cap', 'Industry', 'Sector', 'Current_Price',
        'ROE', 'ROA', 'Debt_To_Equity', 'Current_Ratio'
    ]
    
    # Save to CSV
    filtered_df[columns].to_csv(output_file, index=False)
    
    print(f"Found {len(filtered_df)} matching stocks")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    filter_stocks()