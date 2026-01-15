import requests
import pandas as pd
import json
import os
from datetime import datetime
import time

# Constants
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
START_YEAR = "2015"  # Adjusted to last 10 years per plan
END_YEAR = datetime.now().strftime("%Y")

# Series IDs for key CPI categories
SERIES_IDS = {
    "Headline CPI": "CUUR0000SA0",
    "Food": "CUUR0000SAF1",
    "Energy": "CUUR0000SA0E",
    "Gasoline": "CUUR0000SETB01",
    "Shelter": "CUUR0000SAH1",
    "Apparel": "CUUR0000SAA",
    "New Vehicles": "CUUR0000SETA01",
    "Used Cars and Trucks": "CUUR0000SETA02"
}

def fetch_bls_data(series_ids, start_year, end_year, api_key=None):
    headers = {'Content-type': 'application/json'}
    
    s_year = int(start_year)
    e_year = int(end_year)
    
    # Split into 10-year chunks to respect API limits if needed, 
    # though V1 is strict on other limits too.
    segments = []
    for y in range(s_year, e_year + 1, 10):
        sy = y
        ey = min(y + 9, e_year)
        segments.append((str(sy), str(ey)))
        
    all_data = []

    for sy, ey in segments:
        print(f"Fetching data for {sy}-{ey}...")
        payload = {
            "seriesid": list(series_ids.values()),
            "startyear": sy,
            "endyear": ey
        }
        if api_key:
            payload["registrationkey"] = api_key
            
        data = json.dumps(payload)
        
        try:
            p = requests.post(BLS_API_URL, data=data, headers=headers)
            json_data = p.json()
            
            if json_data['status'] == 'REQUEST_NOT_PROCESSED':
                 print(f"Error: {json_data.get('message')}")
                 # simple retry or skip
                 continue

            if 'Results' not in json_data:
                print(f"No results found. Response: {json_data}")
                continue

            for series in json_data['Results']['series']:
                series_id = series['seriesID']
                # Reverse mapping to get name
                name_matches = [k for k, v in series_ids.items() if v == series_id]
                series_name = name_matches[0] if name_matches else series_id
                
                rows = []
                for item in series['data']:
                    year = item['year']
                    period = item['period']
                    value = item['value']
                    # Construct date
                    # period is M01, M02...
                    if 'M' in period: 
                        month = int(period[1:])
                        date = f"{year}-{month:02d}-01"
                        
                        try:
                            float_val = float(value)
                            rows.append({
                                "date": date,
                                "series_id": series_id,
                                "category": series_name,
                                "value": float_val
                            })
                        except ValueError:
                            # Skip values that are not floats (e.g. '-')
                            pass
                all_data.extend(rows)
            
            # Be nice to the API
            time.sleep(1) 
                
        except Exception as e:
            print(f"Failed to fetch data: {e}")

    df = pd.DataFrame(all_data)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['category', 'date']).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    # Ensure raw directory exists
    os.makedirs("data/raw", exist_ok=True)
    
    print("Starting BLS data extraction...")
    df = fetch_bls_data(SERIES_IDS, START_YEAR, END_YEAR)
    
    if not df.empty:
        output_path = "data/raw/cpi_data.csv"
        df.to_csv(output_path, index=False)
        print(f"Successfully saved {len(df)} rows to {output_path}")
        print(df.head())
    else:
        print("No data collected.")
