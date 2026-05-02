from flask import Blueprint, jsonify, request, current_app
import pandas as pd  # Required for dataframe operations
from statsmodels.tsa.stattools import grangercausalitytests # The missing piece causing the 500

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/causality/<commodity>', methods=['GET'])
def causality_test(commodity):
    """
    Granger Causality Test
    Uses the analytics service for consistent implementation
    """
    try:
        analytics_service = current_app.config['analytics_service']
        max_lag = request.args.get('max_lag', 3, type=int)
        max_lag = max(1, min(3, max_lag))  # clamp to a safe maximum lag

        print(f"DEBUG: /api/analysis/causality/{commodity} hit with max_lag={max_lag}")

        result = analytics_service.granger_causality_test(commodity, max_lag)
        print(f"DEBUG: Granger result for {commodity}: {result}")

        if 'error' in result:
            return jsonify({
                "commodity": commodity,
                "status": "Error",
                "detail": result['error'],
                "p_value": None,
                "optimal_lag": None,
                "is_significant": False,
                "message": result['error']
            }), 200

        return jsonify({
            "commodity": commodity,
            "status": "Success",
            "p_value": result['p_value'],
            "optimal_lag": result['optimal_lag'],
            "lag_selection_method": result.get('lag_selection_method', 'BIC'),
            "is_significant": result['is_significant'],
            "p_values": result.get('p_values', {}),
            "message": result['message']
        }), 200

    except Exception as e:
        print(f"ERROR: /api/analysis/causality/{commodity} exception: {e}")
        return jsonify({
            "commodity": commodity,
            "status": "Error",
            "detail": str(e),
            "p_value": None,
            "optimal_lag": None,
            "is_significant": False,
            "message": str(e)
        }), 500


@analysis_bp.route('/margin/<commodity>', methods=['GET'])
def margin_analysis(commodity):
    """
    Marketing Margin Analysis
    Endpoint: GET /api/analysis/margin/{commodity}
    """
    try:
        analytics_service = current_app.config['analytics_service']
        result = analytics_service.calculate_margin_analysis(commodity)

        if result is None:
            return jsonify({'error': f'No data found for {commodity}'}), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/trends', methods=['GET'])
def trends_analysis():
    """
    Time-Series Trends Analysis
    Endpoint: GET /api/analysis/trends?commodity=Mango
    """
    try:
        analytics_service = current_app.config['analytics_service']
        commodity = request.args.get('commodity', None)
        result = analytics_service.time_series_trends(commodity)

        if result is None:
            return jsonify({'error': 'No data available'}), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/margins/all', methods=['GET'])
def all_commodity_margins():
    """
    Average margin per commodity (for the bar chart)
    Endpoint: GET /api/analysis/margins/all
    Returns: [{commodity, avg_margin, avg_farmgate, avg_retail, avg_farmer_share}, ...]
    """
    try:
        data_service = current_app.config['data_service']
        commodities = ['Banana', 'Mango', 'Pineapple', 'Coconut', 'Palay', 'Corn']
        results = []

        for commodity in commodities:
            data = data_service.get_commodity_data(commodity)
            if not data:
                continue

            margins = [r['Margin'] for r in data if r.get('Margin') is not None]
            farmgates = [r['Farmgate (average)'] for r in data if r.get('Farmgate (average)') is not None]
            retails = [r['Retail (average)'] for r in data if r.get('Retail (average)') is not None]
            shares = [r['Farmer_Share'] for r in data if r.get('Farmer_Share') is not None]

            if not margins:
                continue

            results.append({
                'commodity': commodity,
                'avg_margin': round(sum(margins) / len(margins), 2),
                'avg_farmgate': round(sum(farmgates) / len(farmgates), 2),
                'avg_retail': round(sum(retails) / len(retails), 2),
                'avg_farmer_share': round(sum(shares) / len(shares), 2),
            })

        return jsonify({'data': results}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500