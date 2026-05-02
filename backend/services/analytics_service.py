import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests


class AnalyticsService:
    def __init__(self, data_service):
        self.data_service = data_service

    def load_processed_data(self):
        """
        Load the processed data as a pandas DataFrame
        """
        data = self.data_service.get_all_data()
        if data is None:
            return pd.DataFrame()
        return pd.DataFrame(data)

    def calculate_margin_analysis(self, commodity):
        """
        Marketing Margin Analysis
        Margin = Retail - Farmgate
        Farmer's Share = (Farmgate / Retail) × 100
        """
        data = self.data_service.get_commodity_data(commodity)

        if not data:
            return None

        df = pd.DataFrame(data)
        result = {'commodity': commodity, 'data': []}

        for _, row in df.iterrows():
            margin = row['Retail (average)'] - row['Farmgate (average)']
            farmer_share = (row['Farmgate (average)'] / row['Retail (average)']) * 100

            result['data'].append({
                'date': row['Date'],
                'farmgate': round(row['Farmgate (average)'], 3),
                'retail': round(row['Retail (average)'], 3),
                'margin': round(margin, 3),
                'farmer_share': round(farmer_share, 2)
            })

        return result

    def granger_causality_test(self, commodity, max_lag=3):
        data = self.data_service.get_commodity_data(commodity)

        if not data or len(data) < 10:
            print(f"DEBUG: Granger check failed for {commodity}: insufficient raw rows ({len(data) if data else 0})")
            return {
                'commodity': commodity,
                'error': 'Insufficient data for causality test'
            }

        df = pd.DataFrame(data).sort_values('Date')
        farmgate = df['Farmgate (average)'].astype(float)
        retail = df['Retail (average)'].astype(float)

        diff_data = pd.DataFrame({
            'Retail': retail.diff(),
            'Farmgate': farmgate.diff()
        }).dropna()

        print(f"DEBUG: Granger data for {commodity}: raw={len(df)}, diffed={len(diff_data)}")

        if len(diff_data) < max_lag + 2:
            return {
                'commodity': commodity,
                'error': 'Insufficient stationary data after differencing.'
            }

        max_lag = max(1, min(max_lag, 3, len(diff_data) // 4))
        test_input = diff_data[['Retail', 'Farmgate']].values

        try:
            selection = VAR(diff_data).select_order(maxlags=max_lag)
            selected_lag = getattr(selection, 'bic', None)
            if selected_lag is None and hasattr(selection, 'selected_orders'):
                selected_lag = selection.selected_orders.get('bic')
            selected_lag = int(selected_lag) if selected_lag is not None else 1
            if selected_lag < 1:
                selected_lag = 1
        except Exception as e:
            print(f"WARNING: VAR lag selection failed for {commodity}: {e}")
            selected_lag = 1

        try:
            raw_result = grangercausalitytests(test_input, maxlag=max_lag, verbose=False)
        except Exception as e:
            print(f"ERROR: Statsmodels grangercausalitytests failure for {commodity}: {e}")
            return {
                'commodity': commodity,
                'error': 'Granger causality test failed on the processed data.'
            }

        p_values = {}
        for lag, result in raw_result.items():
            stats_dict = result[0]
            p_val_tuple = stats_dict.get('ssr_ftest')
            if not p_val_tuple or len(p_val_tuple) < 2:
                continue

            p_val = float(p_val_tuple[1])
            p_values[f'lag_{lag}'] = round(p_val, 4)

        print(f"DEBUG: Granger p-values for {commodity}: {p_values}, bic_selected_lag={selected_lag}")

        if not p_values:
            return {
                'commodity': commodity,
                'error': 'Unable to extract valid p-values from the Granger test.'
            }

        selected_key = f'lag_{selected_lag}'
        selected_p = p_values.get(selected_key)
        if selected_p is None:
            selected_lag = min(p_values, key=lambda k: p_values[k]).split('_')[1]
            selected_p = p_values[f'lag_{selected_lag}']
            selected_lag = int(selected_lag)

        is_sig = selected_p < 0.05
        message = (
            f"Selected lag {selected_lag} by BIC is {'statistically significant' if is_sig else 'not statistically significant'} "
            f"(p = {selected_p:.4f})."
        )

        return {
            'commodity': commodity,
            'p_value': selected_p,
            'optimal_lag': selected_lag,
            'lag_selection_method': 'BIC',
            'max_lag_used': max_lag,
            'p_values': p_values,
            'is_significant': is_sig,
            'interpretation': 'Significant' if is_sig else 'Not significant',
            'message': message
        }

    def time_series_trends(self, commodity=None, frequency='monthly'):
        """
        Time-Series Trends Analysis
        """
        if commodity:
            data = self.data_service.get_commodity_data(commodity)
        else:
            data = self.data_service.get_all_data()

        if not data:
            return None

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])

        if commodity:
            return self._analyze_commodity_trend(df, commodity)
        else:
            return self._analyze_all_trends(df)

    def _analyze_commodity_trend(self, df, commodity):
        df = df.sort_values('Date')
        farmgate = df['Farmgate (average)'].values
        retail = df['Retail (average)'].values

        farmgate_growth = ((farmgate[-1] - farmgate[0]) / farmgate[0] * 100) if farmgate[0] != 0 else 0
        retail_growth = ((retail[-1] - retail[0]) / retail[0] * 100) if retail[0] != 0 else 0
        farmgate_volatility = np.std(np.diff(farmgate))
        retail_volatility = np.std(np.diff(retail))

        return {
            'commodity': commodity,
            'period_start': df['Date'].min().strftime('%Y-%m'),
            'period_end': df['Date'].max().strftime('%Y-%m'),
            'farmgate_growth_percent': round(float(farmgate_growth), 2),
            'retail_growth_percent': round(float(retail_growth), 2),
            'farmgate_volatility': round(float(farmgate_volatility), 3),
            'retail_volatility': round(float(retail_volatility), 3),
            'data_points': len(df)
        }

    def _analyze_all_trends(self, df):
        results = []
        for commodity in df['Commodity'].unique():
            cdf = df[df['Commodity'] == commodity]
            results.append(self._analyze_commodity_trend(cdf, commodity))
        return results