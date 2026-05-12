from flask import Blueprint, jsonify, request, current_app

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/causality/<commodity>', methods=['GET'])
def causality_test(commodity):
    """
    Granger Causality Test
    Endpoint: GET /api/analysis/causality/{commodity}
    """
    try:
        analytics_service = current_app.config['analytics_service']
        max_lag = request.args.get('max_lag', 3, type=int)
        max_lag = max(1, min(3, max_lag))

        result = analytics_service.granger_causality_test(commodity, max_lag)

        if 'error' in result:
            return jsonify({
                'commodity': commodity,
                'status': 'Error',
                'detail': result['error'],
                'p_value': None,
                'min_p_value': None,
                'optimal_lag': None,
                'lag': None,
                'max_lag_used': max_lag,
                'p_values': {},
                'is_significant': False,
                'message': result['error']
            }), 200

        return jsonify({
            'commodity': commodity,
            'status': 'Success',
            'p_value': result['p_value'],
            'min_p_value': result['min_p_value'],
            'optimal_lag': result['optimal_lag'],
            'lag': result['lag'],
            'max_lag_used': result['max_lag_used'],
            'lag_selection_method': result['lag_selection_method'],
            'p_values': result['p_values'],
            'is_significant': result['is_significant'],
            'significant': result['significant'],
            'interpretation': result['interpretation'],
            'message': result['message']
        }), 200

    except Exception as e:
        return jsonify({
            'commodity': commodity,
            'status': 'Error',
            'detail': str(e),
            'p_value': None,
            'min_p_value': None,
            'optimal_lag': None,
            'lag': None,
            'p_values': {},
            'is_significant': False,
            'message': str(e)
        }), 500

@analysis_bp.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    """
    Full dashboard data model.
    Endpoint: GET /api/analysis/dashboard-data?max_lag=3
    Returns the same shape as the frontend DATA object:
    {commodities, margin, granger, trends, yearly}
    """
    try:
        analytics_service = current_app.config['analytics_service']
        max_lag = request.args.get('max_lag', 3, type=int)
        max_lag = max(1, min(3, max_lag))
        return jsonify(analytics_service.dashboard_data(max_lag)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    Endpoint: GET /api/analysis/trends?commodity=Mango&frequency=monthly
    Aggregates data monthly or yearly
    Identifies trends, inflation, and seasonal patterns
    """
    try:
        analytics_service = current_app.config['analytics_service']
        commodity = request.args.get('commodity', None)
        frequency = request.args.get('frequency', 'monthly')  # Default to monthly

        # Validate frequency parameter
        if frequency not in ['monthly', 'yearly']:
            return jsonify({'error': 'Frequency must be either "monthly" or "yearly"'}), 400

        result = analytics_service.time_series_trends(commodity, frequency)

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
        analytics_service = current_app.config['analytics_service']
        commodities = analytics_service.get_objective_commodities()
        results = []

        for commodity in commodities:
            summary = analytics_service.calculate_margin_summary(commodity)
            if not summary:
                continue

            results.append({
                'commodity': commodity,
                'avg_margin': summary['avg_margin'],
                'avg_farmgate': summary['avg_farmgate'],
                'avg_retail': summary['avg_retail'],
                'avg_farmer_share': summary['avg_farmers_share'],
            })

        return jsonify({'data': results}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
