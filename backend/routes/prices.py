from flask import Blueprint, jsonify, current_app

prices_bp = Blueprint('prices', __name__, url_prefix='/api/prices')


@prices_bp.route('/all', methods=['GET'])
def get_all_prices():
    """Get all standardized price data"""
    try:
        data_service = current_app.config['data_service']
        data = data_service.get_all_data()

        if data is None:
            return jsonify({'error': 'Data not available'}), 500

        return jsonify({'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prices_bp.route('/commodities', methods=['GET'])
def get_commodities():
    """Get list of available commodities"""
    try:
        data_service = current_app.config['data_service']
        commodities = data_service.get_commodities()
        return jsonify({'commodities': commodities}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prices_bp.route('/<commodity>', methods=['GET'])
def get_commodity_prices(commodity):
    """Get prices for specific commodity"""
    try:
        data_service = current_app.config['data_service']
        data = data_service.get_commodity_data(commodity)

        if not data:
            return jsonify({'error': f'No data found for {commodity}'}), 404

        return jsonify({'commodity': commodity, 'data': data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500