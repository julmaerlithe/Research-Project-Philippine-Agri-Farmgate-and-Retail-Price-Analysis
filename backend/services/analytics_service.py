import numpy as np
from scipy import stats
import pandas as pd


class AnalyticsService:
    def __init__(self, data_service):
        self.data_service = data_service

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

    def granger_causality_test(self, commodity, max_lag=4):
        data = self.data_service.get_commodity_data(commodity)

        if not data or len(data) < 10:
            return {
                'commodity': commodity,
                'error': 'Insufficient data for causality test'
            }

        df = pd.DataFrame(data).sort_values('Date')
        farmgate = df['Farmgate (average)'].values.astype(float)
        retail = df['Retail (average)'].values.astype(float)

        # Normalize to prevent F-stat overflow
        farmgate = (farmgate - farmgate.mean()) / (farmgate.std() + 1e-8)
        retail = (retail - retail.mean()) / (retail.std() + 1e-8)

        max_lag = max(1, min(max_lag, len(farmgate) // 4))

        best_p = 1.0
        best_lag = max_lag

        for lag in range(1, max_lag + 1):
            X_data, y_data = [], []

            for i in range(lag, len(farmgate)):
                lagged_fg = farmgate[i - lag:i]
                lagged_rt = retail[i - lag:i]
                X_data.append(np.concatenate([lagged_fg, lagged_rt]))
                y_data.append(retail[i])

            if len(X_data) < 5:
                continue

            X = np.array(X_data)
            y = np.array(y_data)
            X_c = np.column_stack([np.ones(len(X)), X])

            try:
                from numpy.linalg import lstsq
                coeffs = lstsq(X_c, y, rcond=None)[0]
                y_pred = X_c @ coeffs
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - np.mean(y)) ** 2)

                if ss_tot == 0:
                    continue

                r2 = min(max(1 - (ss_res / ss_tot), 0), 0.9999)

                n = len(y)
                k = X.shape[1]
                if (n - k - 1) <= 0:
                    continue

                f_stat = (r2 / k) / ((1 - r2) / (n - k - 1))
                p = float(1 - stats.f.cdf(f_stat, k, n - k - 1))
                p = max(p, 0.0001)  # floor to avoid showing 0.0000

                if p < best_p:
                    best_p = p
                    best_lag = lag

            except Exception:
                continue

        best_p = round(best_p, 4)
        is_sig = best_p < 0.05

        return {
            'commodity': commodity,
            'p_value': best_p,
            'optimal_lag': best_lag,
            'max_lag_used': max_lag,
            'is_significant': is_sig,
            'interpretation': 'Significant' if is_sig else 'Not significant',
            'message': (
                'Retail prices respond to farmgate price changes, '
                'suggesting effective price transmission.'
            ) if is_sig else (
                'Weak price transmission detected. Farmgate changes may not '
                'efficiently reach retail markets.'
            )
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