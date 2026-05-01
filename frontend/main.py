from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

@app.route('/')
def index():
    """Serve main HTML"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')