import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os

warnings.filterwarnings("ignore")

def train_and_forecast(input_file, output_file, steps=6):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    df['date'] = pd.to_datetime(df['date'])
    
    categories = df['category'].unique()
    all_forecasts = []
    
    print(f"Forecasting for {len(categories)} categories...")
    
    for cat in categories:
        print(f"Processing {cat}...")
        cat_df = df[df['category'] == cat].sort_values('date')
        cat_df = cat_df.set_index('date')
        
        # We model the 'MoM_Inflation' directly.
        
        # Drop NaNs
        ts = cat_df['MoM_Inflation'].dropna()
        
        if len(ts) < 24:
            print(f"Not enough data for {cat}, skipping.")
            continue
            
        # Simple SARIMAX
        # Order (p,d,q) x (P,D,Q,s)
        # Using a generic (1,0,1)(0,0,0,12) for simplicity.
        
        try:
            # We assume frequency is Month Start usually
            if not ts.index.freq:
                ts.index = pd.date_range(start=ts.index[0], periods=len(ts), freq='MS')

            model = SARIMAX(ts, order=(1, 0, 1), seasonal_order=(1, 0, 0, 12), trend='c', enforce_stationarity=False, enforce_invertibility=False)
            results = model.fit(disp=False)
            
            # Forecast
            forecast = results.get_forecast(steps=steps)
            forecast_mean = forecast.predicted_mean
            conf_int = forecast.conf_int()
            
            # Create forecast dataframe
            fc_df = pd.DataFrame({
                'date': forecast_mean.index,
                'category': cat,
                'forecast_value': forecast_mean.values, # This is MoM Forecast
                'lower_ci': conf_int.iloc[:, 0].values,
                'upper_ci': conf_int.iloc[:, 1].values
            })
            
            all_forecasts.append(fc_df)
            
        except Exception as e:
            print(f"Failed to model {cat}: {e}")

    if all_forecasts:
        final_df = pd.concat(all_forecasts)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        final_df.to_csv(output_file, index=False)
        print(f"Saved forecasts to {output_file}")
    else:
        print("No forecasts generated.")

if __name__ == "__main__":
    INPUT_FILE = "data/processed/inflation_features.csv"
    OUTPUT_FILE = "outputs/forecast.csv"
    
    if os.path.exists(INPUT_FILE):
        train_and_forecast(INPUT_FILE, OUTPUT_FILE)
    else:
        print(f"Error: {INPUT_FILE} not found.")
