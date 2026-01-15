import pandas as pd
import numpy as np
import os

def calculate_inflation_metrics(input_path, output_path):
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort ensure correct ordering
    df = df.sort_values(['category', 'date'])
    
    # Metrics calculation per category
    # MoM: (Price_t / Price_{t-1}) - 1
    # YoY: (Price_t / Price_{t-12}) - 1
    
    df['MoM_Inflation'] = df.groupby('category')['value'].pct_change(1) * 100
    df['YoY_Inflation'] = df.groupby('category')['value'].pct_change(12) * 100
    
    # Rolling averages (on MoM) to smooth noise
    df['Rolling_3M_MoM'] = df.groupby('category')['MoM_Inflation'].transform(lambda x: x.rolling(window=3).mean())
    df['Rolling_6M_MoM'] = df.groupby('category')['MoM_Inflation'].transform(lambda x: x.rolling(window=6).mean())
    
    # Volatility: Rolling Std Dev of MoM (6 months)
    df['Volatility_6M'] = df.groupby('category')['MoM_Inflation'].transform(lambda x: x.rolling(window=6).std())
    
    # Drop rows where calculation results are NaN (first 12 months will have NaN YoY)
    # Actually, let's keep them but maybe drop the very first one for MoM.
    # We want to keep data as much as possible for EDA, but for modeling we might drop.
    # For now, let's just save everything and handle NaNs in analysis/modeling.
    
    processed_df = df.dropna(subset=['MoM_Inflation']) # Drop first row of each group at least
    
    print("Metrics calculated.")
    print(processed_df.tail())
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    processed_df.to_csv(output_path, index=False)
    print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    INPUT_FILE = "data/raw/cpi_data.csv"
    OUTPUT_FILE = "data/processed/inflation_features.csv"
    
    if os.path.exists(INPUT_FILE):
        calculate_inflation_metrics(INPUT_FILE, OUTPUT_FILE)
    else:
        print(f"Error: {INPUT_FILE} not found. Run extract_bls.py first.")
