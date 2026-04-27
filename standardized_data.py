import pandas as pd
import numpy as np

# 1. Load the dataset
# We skip the first row (years) and second row (months) to clean the headers manually
file_path = 'FINAL Datasets- Farmgate & Retail Prices(Average, Margin).csv'
df_raw = pd.read_csv(file_path, header=None, skiprows=1)

# 2. Extract and Combine Date Headers
# Row 0 contains years (using ffill to handle merged cells)
# Row 1 contains the month names
years = df_raw.iloc[0, 2:].fillna(method='ffill').tolist()
months = df_raw.iloc[1, 2:].tolist()
date_cols = [f"{y}-{m}" for y, m in zip(years, months)]

# 3. Define the 8 target parent commodities
target_commodities = ['COCONUT', 'BANANA', 'MANGO', 'PINEAPPLE', 'CASSAVA', 'UBE', 'PALAY', 'CORN']
final_data = []

current_parent = None
current_type = None

# 4. Iterate through rows to parse varieties and associate them with parents
for idx, row in df_raw.iloc[2:].iterrows():
    type_indicator = str(row[0]).strip().upper()
    item_name = str(row[1]).strip().upper()
    
    # Track if the current section is FARMGATE or RETAIL
    if type_indicator == 'FARMGATE':
        current_type = 'FARMGATE'
    elif type_indicator == 'RETAIL':
        current_type = 'RETAIL'
    elif type_indicator in ['MARGIN', 'F/R']:
        current_type = None 
        
    # Check if the row is a Parent Header (e.g., "BANANA")
    if item_name in target_commodities:
        current_parent = item_name.capitalize()
        continue
    
    # Skip summary/average rows already present in the raw source
    if item_name in ['AVERAGE', 'MARGIN']:
        continue
        
    # Process numeric price data for sub-varieties
    if current_parent and current_type:
        prices = row[2:].tolist()
        for date_label, price in zip(date_cols, prices):
            try:
                # Clean string (remove commas and handle null symbols like '..')
                clean_price = str(price).replace(',', '').strip()
                if clean_price in ['', '..', '...']:
                    continue
                
                val = float(clean_price)
                if not np.isnan(val):
                    final_data.append({
                        'Month_Year': date_label,
                        'Commodity': current_parent,
                        'Type': current_type,
                        'Price': val
                    })
            except ValueError:
                continue

# 5. Aggregate Data
# Group by Date and Commodity to calculate the mean of all varieties
df_long = pd.DataFrame(final_data)
df_grouped = df_long.groupby(['Month_Year', 'Commodity', 'Type'])['Price'].mean().reset_index()

# 6. Pivot and Calculate Standard Columns
df_pivot = df_grouped.pivot_table(index=['Month_Year', 'Commodity'], 
                                  columns='Type', 
                                  values='Price').reset_index()

# Rename and calculate Margin
df_pivot['Farmgate (average)'] = df_pivot['FARMGATE'].round(3)
df_pivot['Retail (average)'] = df_pivot['RETAIL'].round(3)
df_pivot['Margin'] = (df_pivot['RETAIL'] - df_pivot['FARMGATE']).round(3)

# 7. Standardize Date Format (YYYY-MM)
def format_date_string(d):
    parts = d.split('-')
    return pd.to_datetime(f"{parts[0]} {parts[1]}", format='%Y %B').strftime('%Y-%m')

df_pivot['Date'] = df_pivot['Month_Year'].apply(format_date_string)

# 8. Final Output Selection
df_final = df_pivot[['Date', 'Commodity', 'Farmgate (average)', 'Retail (average)', 'Margin']]
df_final = df_final.sort_values(['Date', 'Commodity'])

# Save to CSV
df_final.to_csv("Standardized_Farmgate_Retail_Final_Data.csv", index=False)