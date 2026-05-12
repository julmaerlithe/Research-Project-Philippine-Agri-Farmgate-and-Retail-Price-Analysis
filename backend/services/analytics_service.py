import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests


OBJECTIVE_COMMODITIES = [
    'Rice',
    'Corn',
    'Coconut',
    'Cassava',
    'Banana',
    'Pineapple',
    'Mango',
]


class AnalyticsService:
    def __init__(self, data_service):
        self.data_service = data_service

    def load_processed_data(self):
        data = self.data_service.get_all_data()
        if data is None:
            return pd.DataFrame()
        return pd.DataFrame(data)

    def calculate_margin_analysis(self, commodity):
        """
        Marketing Margin Analysis.
        Margin = Retail - Farmgate
        Farmer's Share = (Farmgate / Retail) * 100
        """
        data = self.data_service.get_commodity_data(commodity)
        if not data:
            return None

        df = pd.DataFrame(data).sort_values('Date')
        result = {'commodity': commodity, 'data': []}

        for _, row in df.iterrows():
            farmgate = float(row['Farmgate (average)'])
            retail = float(row['Retail (average)'])
            margin = self._calculate_margin(farmgate, retail)
            farmer_share = self._calculate_farmer_share(farmgate, retail)

            result['data'].append({
                'date': row['Date'],
                'farmgate': round(farmgate, 3),
                'retail': round(retail, 3),
                'margin': round(margin, 3),
                'farmer_share': round(farmer_share, 2),
            })

        return result

    def calculate_margin_summary(self, commodity):
        """
        Dashboard-compatible margin summary for one commodity.
        """
        analysis = self.calculate_margin_analysis(commodity)
        if not analysis or not analysis['data']:
            return None

        rows = analysis['data']
        avg = lambda key: sum(row[key] for row in rows) / len(rows)
        margins = [row['margin'] for row in rows]

        return {
            'avg_farmgate': round(avg('farmgate'), 2),
            'avg_retail': round(avg('retail'), 2),
            'avg_margin': round(avg('margin'), 2),
            'avg_farmers_share': round(avg('farmer_share'), 2),
            'min_margin': round(min(margins), 2),
            'max_margin': round(max(margins), 2),
            'monthly': [
                {
                    'date': row['date'],
                    'farmgate': row['farmgate'],
                    'retail': row['retail'],
                    'margin': row['margin'],
                    'farmers_share': row['farmer_share'],
                }
                for row in rows
            ],
        }

    def granger_causality_test(self, commodity, max_lag=3):
        """
        Test whether farmgate prices predict retail prices.
        Runs lag-specific tests from 1 to max_lag and reports the minimum p-value,
        matching the simplified dashboard logic.
        """
        data = self.data_service.get_commodity_data(commodity)
        if not data or len(data) < 10:
            return {
                'commodity': commodity,
                'error': 'Insufficient data for causality test',
            }

        df = pd.DataFrame(data).sort_values('Date')
        diff_data = pd.DataFrame({
            'Retail': df['Retail (average)'].astype(float).diff(),
            'Farmgate': df['Farmgate (average)'].astype(float).diff(),
        }).dropna()

        max_lag = max(1, min(int(max_lag), 3, len(diff_data) // 4))
        if len(diff_data) < max_lag + 2:
            return {
                'commodity': commodity,
                'error': 'Insufficient stationary data after differencing.',
            }

        test_input = diff_data[['Retail', 'Farmgate']].values

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    'ignore',
                    message='verbose is deprecated',
                    category=FutureWarning,
                )
                raw_result = grangercausalitytests(test_input, maxlag=max_lag, verbose=False)
        except Exception:
            return {
                'commodity': commodity,
                'error': 'Granger causality test failed on the processed data.',
            }

        p_values = {}
        for lag, result in raw_result.items():
            p_val_tuple = result[0].get('ssr_ftest')
            if p_val_tuple and len(p_val_tuple) >= 2:
                p_values[f'lag_{lag}'] = round(float(p_val_tuple[1]), 4)

        if not p_values:
            return {
                'commodity': commodity,
                'error': 'Unable to extract valid p-values from the Granger test.',
            }

        selected_key, p_value = min(p_values.items(), key=lambda item: item[1])
        selected_lag = int(selected_key.split('_')[1])
        is_significant = p_value < 0.05
        interpretation = (
            'Farmgate prices significantly predict retail prices'
            if is_significant
            else 'No significant price transmission detected'
        )

        return {
            'commodity': commodity,
            'p_value': p_value,
            'min_p_value': p_value,
            'optimal_lag': selected_lag,
            'lag': selected_lag,
            'max_lag_used': max_lag,
            'lag_selection_method': f'Minimum p-value across lags 1-{max_lag}',
            'p_values': p_values,
            'is_significant': is_significant,
            'significant': is_significant,
            'interpretation': interpretation,
            'message': f'{interpretation} (p = {p_value:.4f}, lag {selected_lag}).',
        }

    def dashboard_data(self, max_lag=3):
        """
        Return the same data model used by the provided dashboard code:
        commodities, margin summaries, Granger summaries, monthly trends, and yearly summaries.
        """
        commodities = self.get_objective_commodities()

        margin = {}
        granger = {}
        yearly = {}

        for commodity in commodities:
            summary = self.calculate_margin_summary(commodity)
            if not summary:
                continue

            margin[commodity] = summary
            yearly[commodity] = self._yearly_summary(summary['monthly'])

            causality = self.granger_causality_test(commodity, max_lag)
            if 'error' in causality:
                granger[commodity] = {
                    'p_values': {},
                    'min_p_value': None,
                    'significant': False,
                    'interpretation': causality['error'],
                }
            else:
                granger[commodity] = {
                    'p_values': {
                        key.replace('lag_', ''): value
                        for key, value in causality['p_values'].items()
                    },
                    'min_p_value': causality['min_p_value'],
                    'significant': causality['is_significant'],
                    'interpretation': causality['interpretation'],
                }

        return {
            'commodities': list(margin.keys()),
            'margin': margin,
            'granger': granger,
            'trends': self._all_commodity_monthly_trends(margin),
            'yearly': yearly,
        }

    def time_series_trends(self, commodity=None, frequency='monthly'):
        """
        Time-Series Trends Analysis.
        Aggregates data monthly or yearly and identifies trend, inflation,
        volatility, and seasonal patterns.
        """
        data = (
            self.data_service.get_commodity_data(commodity)
            if commodity
            else self.data_service.get_all_data()
        )
        if not data:
            return None

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])

        if commodity:
            return self._analyze_commodity_trends(df, commodity, frequency)
        return self._analyze_all_commodity_trends(df, frequency)

    def _analyze_commodity_trends(self, df, commodity, frequency='monthly'):
        df = df.sort_values('Date').copy()
        df.set_index('Date', inplace=True)

        if frequency == 'monthly':
            aggregated = df.resample('ME').agg({
                'Farmgate (average)': 'mean',
                'Retail (average)': 'mean',
            })
        elif frequency == 'yearly':
            aggregated = df.resample('YE').agg({
                'Farmgate (average)': 'mean',
                'Retail (average)': 'mean',
            })
        else:
            aggregated = df[['Farmgate (average)', 'Retail (average)']]

        aggregated = aggregated.dropna()
        if len(aggregated) < 3:
            return {
                'commodity': commodity,
                'frequency': frequency,
                'error': 'Insufficient data for trend analysis',
            }

        aggregated['Margin'] = aggregated.apply(
            lambda row: self._calculate_margin(
                row['Farmgate (average)'],
                row['Retail (average)'],
            ),
            axis=1,
        )
        aggregated['Farmer_Share'] = aggregated.apply(
            lambda row: self._calculate_farmer_share(
                row['Farmgate (average)'],
                row['Retail (average)'],
            ),
            axis=1,
        )

        farmgate_volatility = aggregated['Farmgate (average)'].pct_change().std() * 100
        retail_volatility = aggregated['Retail (average)'].pct_change().std() * 100
        margin_volatility = aggregated['Margin'].pct_change().std() * 100
        aggregated['Farmgate_Growth_Rate'] = aggregated['Farmgate (average)'].pct_change().apply(
            lambda value: value * 100 if pd.notna(value) else None
        )
        aggregated['Retail_Growth_Rate'] = aggregated['Retail (average)'].pct_change().apply(
            lambda value: value * 100 if pd.notna(value) else None
        )
        aggregated['Margin_Growth_Rate'] = aggregated['Margin'].pct_change().apply(
            lambda value: value * 100 if pd.notna(value) else None
        )

        farmgate_trend = self._calculate_trend_components(aggregated['Farmgate (average)'])
        retail_trend = self._calculate_trend_components(aggregated['Retail (average)'])
        margin_trend = self._calculate_trend_components(aggregated['Margin'])

        return {
            'commodity': commodity,
            'frequency': frequency,
            'period_start': aggregated.index.min().strftime('%Y-%m-%d'),
            'period_end': aggregated.index.max().strftime('%Y-%m-%d'),
            'data_points': len(aggregated),
            'formulas': {
                'trend_equation': 'Yt = a + bt',
                'growth_rate': '((Pt - Pt-1) / Pt-1) * 100',
                'marketing_margin': 'Retail Price - Farm-gate Price',
                'farmer_share': '(Farm-gate Price / Retail Price) * 100',
            },
            'trends': {
                'farmgate_trend': farmgate_trend['slope'],
                'retail_trend': retail_trend['slope'],
                'margin_trend': margin_trend['slope'],
            },
            'trend_equations': {
                'farmgate': farmgate_trend,
                'retail': retail_trend,
                'margin': margin_trend,
            },
            'volatility': {
                'farmgate_volatility_percent': round(farmgate_volatility, 2),
                'retail_volatility_percent': round(retail_volatility, 2),
                'margin_volatility_percent': round(margin_volatility, 2),
            },
            'seasonal_patterns': (
                self._analyze_seasonality(aggregated, frequency)
                if len(aggregated) >= 12
                else {}
            ),
            'inflation_analysis': self._calculate_inflation(aggregated),
            'aggregated_data': [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'farmgate_avg': round(row['Farmgate (average)'], 3),
                    'retail_avg': round(row['Retail (average)'], 3),
                    'margin': round(row['Margin'], 3),
                    'farmer_share': round(row['Farmer_Share'], 2),
                    'farmgate_growth_rate_percent': self._round_optional(row['Farmgate_Growth_Rate'], 2),
                    'retail_growth_rate_percent': self._round_optional(row['Retail_Growth_Rate'], 2),
                    'margin_growth_rate_percent': self._round_optional(row['Margin_Growth_Rate'], 2),
                }
                for date, row in aggregated.iterrows()
            ],
        }

    def _analyze_all_commodity_trends(self, df, frequency='monthly'):
        results = []
        for commodity in self.get_objective_commodities():
            cdf = df[df['Commodity'] == commodity]
            if cdf.empty:
                continue
            results.append(self._analyze_commodity_trends(cdf, commodity, frequency))
        return results

    def get_objective_commodities(self):
        available = set(self.data_service.get_commodities())
        return [
            commodity
            for commodity in OBJECTIVE_COMMODITIES
            if commodity in available
        ]

    @staticmethod
    def _calculate_margin(farmgate, retail):
        return float(retail) - float(farmgate)

    @staticmethod
    def _calculate_farmer_share(farmgate, retail):
        retail = float(retail)
        if retail == 0:
            return 0.0
        return (float(farmgate) / retail) * 100

    def _yearly_summary(self, monthly_rows):
        df = pd.DataFrame(monthly_rows)
        if df.empty:
            return []

        df['year'] = df['date'].str.slice(0, 4).astype(int)
        yearly = df.groupby('year').agg({
            'farmgate': 'mean',
            'retail': 'mean',
            'margin': 'mean',
        }).reset_index()

        return [
            {
                'year': int(row['year']),
                'farmgate': round(float(row['farmgate']), 2),
                'retail': round(float(row['retail']), 2),
                'margin': round(float(row['margin']), 2),
            }
            for _, row in yearly.iterrows()
        ]

    def _all_commodity_monthly_trends(self, margin):
        rows_by_date = {}
        for summary in margin.values():
            for row in summary['monthly']:
                rows_by_date.setdefault(row['date'], []).append(row)

        trends = []
        for date in sorted(rows_by_date):
            rows = rows_by_date[date]
            trends.append({
                'date': date,
                'avg_farmgate': round(sum(row['farmgate'] for row in rows) / len(rows), 2),
                'avg_retail': round(sum(row['retail'] for row in rows) / len(rows), 2),
                'avg_margin': round(sum(row['margin'] for row in rows) / len(rows), 2),
            })

        return trends

    def _calculate_trend(self, series):
        return self._calculate_trend_components(series)['slope']

    def _calculate_trend_components(self, series):
        if len(series) < 2:
            return {
                'intercept': 0.0,
                'slope': 0.0,
                'equation': 'Yt = 0.0000 + 0.0000t',
            }

        x = np.arange(len(series))
        y = series.values
        valid_mask = ~np.isnan(y)
        x = x[valid_mask]
        y = y[valid_mask]

        if len(x) < 2:
            return {
                'intercept': 0.0,
                'slope': 0.0,
                'equation': 'Yt = 0.0000 + 0.0000t',
            }

        try:
            slope, intercept = np.polyfit(x, y, 1)
            intercept = round(float(intercept), 4)
            slope = round(float(slope), 4)
            sign = '+' if slope >= 0 else '-'
            return {
                'intercept': intercept,
                'slope': slope,
                'equation': f'Yt = {intercept:.4f} {sign} {abs(slope):.4f}t',
            }
        except Exception:
            return {
                'intercept': 0.0,
                'slope': 0.0,
                'equation': 'Yt = 0.0000 + 0.0000t',
            }

    @staticmethod
    def _round_optional(value, digits):
        if pd.isna(value):
            return None
        return round(float(value), digits)

    def _analyze_seasonality(self, df, frequency):
        if len(df) < 12:
            return {'error': 'Insufficient data for seasonal analysis'}

        try:
            if frequency == 'monthly':
                monthly_avg = df.groupby(df.index.month).mean()
                seasonal_strength = {}

                for col in ['Farmgate (average)', 'Retail (average)', 'Margin']:
                    if col in df.columns:
                        values = monthly_avg[col].values
                        seasonal_strength[col] = (
                            (np.std(values) / np.mean(values)) * 100
                            if np.mean(values) != 0
                            else 0
                        )

                return {
                    'seasonal_strength_farmgate': round(seasonal_strength.get('Farmgate (average)', 0), 2),
                    'seasonal_strength_retail': round(seasonal_strength.get('Retail (average)', 0), 2),
                    'seasonal_strength_margin': round(seasonal_strength.get('Margin', 0), 2),
                    'peak_months': {
                        'farmgate': int(monthly_avg['Farmgate (average)'].idxmax()),
                        'retail': int(monthly_avg['Retail (average)'].idxmax()),
                        'margin': int(monthly_avg['Margin'].idxmax()),
                    },
                }
        except Exception as e:
            return {'error': f'Seasonal analysis failed: {str(e)}'}

        return {}

    def _calculate_inflation(self, df):
        try:
            yearly_data = df.resample('YE').mean()
            if len(yearly_data) < 2:
                return {'error': 'Insufficient yearly data for inflation analysis'}

            inflation_rates = {}
            for col in ['Farmgate (average)', 'Retail (average)', 'Margin']:
                if col in yearly_data.columns:
                    pct_change = yearly_data[col].pct_change() * 100
                    inflation_rates[col] = {
                        'avg_annual_inflation': round(pct_change.mean(), 2),
                        'max_inflation': round(pct_change.max(), 2),
                        'min_inflation': round(pct_change.min(), 2),
                        'volatility': round(pct_change.std(), 2),
                    }

            return inflation_rates
        except Exception as e:
            return {'error': f'Inflation analysis failed: {str(e)}'}
