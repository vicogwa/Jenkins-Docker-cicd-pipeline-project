
from flask import Flask, jsonify
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    logger.info("Root endpoint accessed")
    return jsonify({
        'message': 'Hello from CI/CD Pipeline!',
        'version': os.environ.get('APP_VERSION', '1.0.0'),
        'environment': os.environ.get('ENV', 'development')
    })

@app.route('/health')
def health():
    logger.info("Health endpoint accessed")
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    logger.info("Starting Flask application on 0.0.0.0:5000")
    
    # Use debug=False in containers for stability
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=debug_mode,
        threaded=True
    )