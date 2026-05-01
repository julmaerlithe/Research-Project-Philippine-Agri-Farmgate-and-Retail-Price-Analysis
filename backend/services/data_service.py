import pandas as pd
import numpy as np
import os


class DataService:
    def __init__(self):
        self.data_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'FINAL Datasets - Farmgate&Retail Prices (Average, Margin).csv'
        )
        self.df_standardized = None
        self.load_and_standardize_data()

    def load_and_standardize_data(self):
        try:
            df_raw = pd.read_csv(self.data_path, header=None, skiprows=1)

            years = df_raw.iloc[0, 2:].ffill().tolist()
            months = df_raw.iloc[1, 2:].tolist()
            date_cols = [f"{y}-{m}" for y, m in zip(years, months)]

            target_commodities = ['COCONUT', 'BANANA', 'MANGO', 'PINEAPPLE',
                                   'CASSAVA', 'UBE', 'PALAY', 'CORN']
            final_data = []

            current_parent = None
            current_type = None

            for idx, row in df_raw.iloc[2:].iterrows():
                type_indicator = str(row[0]).strip().upper()
                item_name = str(row[1]).strip().upper()

                if type_indicator == 'FARMGATE':
                    current_type = 'FARMGATE'
                elif type_indicator == 'RETAIL':
                    current_type = 'RETAIL'
                elif type_indicator in ['MARGIN', 'F/R']:
                    current_type = None

                if item_name in target_commodities:
                    current_parent = item_name.capitalize()
                    continue

                if item_name in ['AVERAGE', 'MARGIN']:
                    continue

                if current_parent and current_type:
                    prices = row[2:].tolist()
                    for date_label, price in zip(date_cols, prices):
                        try:
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

            df_long = pd.DataFrame(final_data)
            df_grouped = df_long.groupby(
                ['Month_Year', 'Commodity', 'Type'])['Price'].mean().reset_index()

            df_pivot = df_grouped.pivot_table(
                index=['Month_Year', 'Commodity'],
                columns='Type',
                values='Price'
            ).reset_index()

            df_pivot['Farmgate (average)'] = df_pivot['FARMGATE'].round(3)
            df_pivot['Retail (average)'] = df_pivot['RETAIL'].round(3)
            df_pivot['Margin'] = (df_pivot['RETAIL'] - df_pivot['FARMGATE']).round(3)
            df_pivot['Farmer_Share'] = (
                (df_pivot['FARMGATE'] / df_pivot['RETAIL']) * 100).round(2)

            def format_date_string(d):
                parts = d.split('-')
                return pd.to_datetime(
                    f"{parts[0]} {parts[1]}", format='%Y %B').strftime('%Y-%m')

            df_pivot['Date'] = df_pivot['Month_Year'].apply(format_date_string)

            self.df_standardized = df_pivot[[
                'Date', 'Commodity', 'Farmgate (average)',
                'Retail (average)', 'Margin', 'Farmer_Share'
            ]]
            self.df_standardized = self.df_standardized.sort_values(
                ['Date', 'Commodity'])

            print("Data loaded and standardized successfully")

        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.df_standardized = None

    def get_all_data(self):
        if self.df_standardized is None:
            return None
        return self.df_standardized.to_dict('records')

    def get_commodity_data(self, commodity):
        if self.df_standardized is None:
            return None
        commodity_data = self.df_standardized[
            self.df_standardized['Commodity'].str.lower() == commodity.lower()
        ]
        return commodity_data.to_dict('records')

    def get_commodities(self):
        if self.df_standardized is None:
            return []
        return self.df_standardized['Commodity'].unique().tolist()