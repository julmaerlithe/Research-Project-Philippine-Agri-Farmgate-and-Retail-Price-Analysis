from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os      

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService   
from services.analytics_service import AnalyticsService
from routes.prices import prices_bp
from routes.analysis import analysis_bp

app = Flask(__name__)
CORS(app)

data_service = DataService()
analytics_service = AnalyticsService(data_service)

app.config['data_service'] = data_service
app.config['analytics_service'] = analytics_service 

app.register_blueprint(prices_bp)
app.register_blueprint(analysis_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'Backend is running'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')