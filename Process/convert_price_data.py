import pandas as pd
import os
from datetime import datetime

def convert_price_data(symbol):
    # Read the original CSV file
    input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', 'History_DataPriceVNZ.csv')
    df = pd.read_csv(input_file)
    
    # Rename columns
    df = df.rename(columns={
        'Ngày': 'Date',
        'Lần cuối': 'Close',
        'Mở': 'Open',
        'Cao': 'High',
        'Thấp': 'Low',
        'KL': 'Volume'
    })
    
    # Convert date format
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
    
    # Clean price columns by removing commas and converting to float
    price_columns = ['Close', 'Open', 'High', 'Low']
    for col in price_columns:
        df[col] = df[col].str.replace(',', '').str.replace('"', '').str.replace('.00', '').astype(float)
    
    # Convert volume to numeric, removing 'K' and multiplying by 1000
    df['Volume'] = df['Volume'].str.replace('K', '').astype(float) * 1000
    
    # Sort by date
    df = df.sort_values('Date')
    
    # Save to new file
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data', f'{symbol}_prices.csv')
    df.to_csv(output_file, index=False)
    print(f"Converted price data saved to {output_file}")

if __name__ == "__main__":
    convert_price_data('VNZ') 