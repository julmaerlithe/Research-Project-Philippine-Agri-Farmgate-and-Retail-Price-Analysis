from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
import os
import calendar

app = FastAPI(title="Agri-Price Intelligence API")

# 1. CORS Configuration (Allows frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "Standardized_Farmgate_Retail_Final_Data.csv"

def load_processed_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Standardized data file missing.")
    df = pd.read_csv(DATA_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# --- API ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "online", "file_found": os.path.exists(DATA_PATH)}

@app.get("/data/all")
def get_raw_data():
    """Returns the full standardized dataset."""
    df = load_processed_data()
    return df.to_dict(orient="records")

@app.get("/analysis/margin/{commodity}")
def get_marketing_margin(commodity: str):
    """Calculates marketing margins and efficiency ratios."""
    df = load_processed_data()
    subset = df[df['Commodity'].str.lower() == commodity.lower()].copy()
    
    if subset.empty:
        raise HTTPException(status_code=404, detail="Commodity not found")

    # Marketing Margin = Retail - Farmgate
    # Farmer's Share = (Farmgate / Retail) * 100
    subset['Farmers_Share'] = (subset['Farmgate (average)'] / subset['Retail (average)']) * 100
    
    return {
        "commodity": commodity,
        "average_margin": round(subset['Margin'].mean(), 3),
        "average_farmers_share_percentage": round(subset['Farmers_Share'].mean(), 2),
        "max_margin_recorded": subset['Margin'].max(),
        "min_margin_recorded": subset['Margin'].min(),
        "trend": subset[['Date', 'Margin', 'Farmers_Share']].to_dict(orient="records")
    }

@app.get("/analysis/causality/{commodity}")
def run_causality_test(commodity: str, max_lag: int = 3):
    try:
        df = load_processed_data()
        subset = df[df['Commodity'].str.lower() == commodity.lower()].sort_values('Date')
        
        if len(subset) < (max_lag + 10):
            return {"status": "Error", "detail": "Not enough data points."}

        ts_data = subset[['Retail (average)', 'Farmgate (average)']].copy()
        ts_data = ts_data.interpolate(method='linear').ffill().bfill()
        ts_diff = ts_data.diff().dropna()

        if (ts_diff.std() == 0).any():
            return {"status": "Skipped", "detail": "Price data is constant."}

        # Run test - using .values for compatibility
        test_result = grangercausalitytests(ts_diff.values, maxlag=max_lag, verbose=False)
        
        p_values = {}
        for lag in range(1, max_lag + 1):
            # FIX: The key is 'ssr_ftest', not 'ssr_f_test'
            # We use .get() to prevent the 500 error if the key is missing
            test_stats = test_result[lag][0]
            p_val = test_stats.get('ssr_ftest', [None, None])[1] 
            
            if p_val is not None:
                p_values[f"lag_{lag}"] = round(float(p_val), 4)
        
        significant = any(p < 0.05 for p in p_values.values())
        
        return {
            "commodity": commodity,
            "status": "Success",
            "p_values": p_values,
            "is_statistically_significant": significant
        }

    except Exception as e:
        # This will return the actual error message if something else goes wrong
        return {"status": "Error", "detail": str(e)}
      
@app.get("/analysis/trends")
def get_time_series_aggregation(commodity: str = None, freq: str = "ME", seasonal: bool = False):
    """
    freq: "ME" (Monthly), "QE" (Quarterly), "YE" (Yearly)
    seasonal: If True, returns Jan-Dec average across all years.
    """
    df = load_processed_data()
    
    # Filter by commodity first if provided
    if commodity:
        df = df[df['Commodity'].str.lower() == commodity.lower()].copy()

    if seasonal:
        # --- SEASONAL LOGIC (Jan-Dec Average) ---
        # We group by the month number (1-12)
        summary = df.groupby(['Commodity', df['Date'].dt.month]).agg({
            'Farmgate (average)': 'mean',
            'Retail (average)': 'mean',
            'Margin': 'mean'
        }).reset_index()
        
        # Rename the 'Date' column (which is now 1-12) to Month Names
        summary['Date'] = summary['Date'].apply(lambda x: calendar.month_name[x])
        
    else:
        # --- TIME-SERIES LOGIC (2021-2025 Timeline) ---
        df.set_index('Date', inplace=True)
        summary = df.groupby(['Commodity', pd.Grouper(freq=freq)]).agg({
            'Farmgate (average)': 'mean',
            'Retail (average)': 'mean',
            'Margin': 'mean'
        }).reset_index()
        
        # Keep the Year-Month format for the timeline
        summary['Date'] = summary['Date'].dt.strftime('%Y-%m-%d')
    
    return summary.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
