from flask import Flask, jsonify
from flask_cors import CORS
import logging
import json
import os
from logging.handlers import RotatingFileHandler
from routes import api

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        app.logger.error(f"Failed to load config: {str(e)}")
        return {}

# Configure logging
def setup_logging(config):
    log_config = config.get('logging', {
        'level': 'INFO',
        'file': 'privacyguard.log',
        'max_size': 10485760,  # 10MB
        'backup_count': 3
    })

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler
    file_handler = RotatingFileHandler(
        log_config['file'],
        maxBytes=log_config['max_size'],
        backupCount=log_config['backup_count']
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Set up the logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_config['level'])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Internal Server Error'}), 500

# Initialize the application
def init_app():
    # Load configuration
    config = load_config()
    app.config['privacy_config'] = config
    
    # Setup logging
    setup_logging(config)
    
    app.logger.info('PrivacyGuard Backend initialized successfully')
    return app

if __name__ == '__main__':
    app = init_app()
    app.run(host='0.0.0.0', port=8001, debug=True)  # Using port 8001 for backend
