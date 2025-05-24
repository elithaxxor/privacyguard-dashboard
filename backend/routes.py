from flask import Blueprint, jsonify, request, current_app
from network_manager import NetworkManager
from automation import AutomationManager
from privacy_manager import PrivacyManager
from utils import ReportGenerator
import logging
from typing import Dict, Any
from functools import wraps
import json

# Create blueprint
api = Blueprint('api', __name__)
network_manager = NetworkManager()
automation_manager = AutomationManager()
privacy_manager = PrivacyManager()
logger = logging.getLogger(__name__)

def handle_errors(f):
    """Decorator to handle errors in routes"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': str(e),
                'status': 'error'
            }), 500
    return wrapper

@api.route('/interfaces', methods=['GET'])
@handle_errors
def get_interfaces():
    """Get all available network interfaces"""
    interfaces = network_manager.get_available_interfaces()
    return jsonify({
        'interfaces': interfaces,
        'status': 'success'
    })

@api.route('/routing', methods=['GET'])
@handle_errors
def get_routing():
    """Get current routing information, including preferred interface IP"""
    routing_info = network_manager.get_current_routing()
    # Determine preferred interface: use actual default route if available
    if 'error' not in routing_info:
        routes = routing_info.get('default_routes', []) or []
        preferred = routes[0]['interface'] if routes else routing_info.get('preferred_interface')
        routing_info['preferred_interface'] = preferred
        # Include IP address of preferred interface if available
        ip_addr = None
        if preferred:
            status = network_manager.check_interface_status(preferred)
            if status and not status.get('error'):
                ip_addr = status.get('ipv4_address')
        routing_info['ip_address'] = ip_addr
    return jsonify({
        'routing': routing_info,
        'status': 'success'
    })

@api.route('/routing/preferred', methods=['POST'])
@handle_errors
def set_preferred_routing():
    """Set preferred routing interface"""
    data = request.get_json()
    if not data or 'interface' not in data:
        return jsonify({
            'error': 'Missing interface parameter',
            'status': 'error'
        }), 400

    success = network_manager.set_preferred_routing(data['interface'])
    if success:
        return jsonify({
            'message': f"Successfully set {data['interface']} as preferred route",
            'status': 'success'
        })
    else:
        return jsonify({
            'error': f"Failed to set {data['interface']} as preferred route",
            'status': 'error'
        }), 500

@api.route('/interface/<name>/status', methods=['GET'])
@handle_errors
def get_interface_status(name: str):
    """Get status of a specific interface"""
    status = network_manager.check_interface_status(name)
    if 'error' in status:
        return jsonify({
            'error': status['error'],
            'status': 'error'
        }), 404
    return jsonify({
        'interface_status': status,
        'status': 'success'
    })

@api.route('/interface/<name>/toggle', methods=['POST'])
@handle_errors
def toggle_interface(name: str):
    """Toggle interface state (enable/disable)"""
    data = request.get_json()
    if not data or 'enable' not in data:
        return jsonify({
            'error': 'Missing enable parameter',
            'status': 'error'
        }), 400

    success = network_manager.toggle_interface(name, data['enable'])
    if success:
        state = "enabled" if data['enable'] else "disabled"
        return jsonify({
            'message': f"Successfully {state} interface {name}",
            'status': 'success'
        })
    else:
        return jsonify({
            'error': f"Failed to toggle interface {name}",
            'status': 'error'
        }), 500

@api.route('/config', methods=['GET'])
@handle_errors
def get_config():
    """Get current configuration"""
    config = current_app.config.get('privacy_config', {})
    return jsonify({
        'config': config,
        'status': 'success'
    })

@api.route('/config', methods=['POST'])
@handle_errors
def update_config():
    """Update configuration"""
    data = request.get_json()
    if not data:
        return jsonify({
            'error': 'No configuration data provided',
            'status': 'error'
        }), 400

    try:
        # Update configuration
        current_config = current_app.config.get('privacy_config', {})
        current_config.update(data)
        current_app.config['privacy_config'] = current_config

        # Save to file
        with open('config.json', 'w') as f:
            json.dump(current_config, f, indent=2)
        # Propagate new configuration in-memory
        try:
            network_manager.config = current_config
            automation_cfg = current_config.get('automation', {})
            automation_manager.update_config(automation_cfg)
            # Toggle privacy features (VPN, Proxy, Tor)
            privacy_manager.config = current_config
            for feature in ('vpn', 'proxy', 'tor'):
                enabled = current_config.get(feature, {}).get('enabled', False)
                try:
                    privacy_manager.set_enabled(feature, enabled)
                except Exception as ex:
                    logger.error(f"Error toggling {feature}: {ex}")
        except Exception as ex:
            logger.error(f"Error propagating config changes: {ex}")
        return jsonify({
            'message': 'Configuration updated successfully',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to update configuration: {str(e)}',
            'status': 'error'
        }), 500

@api.route('/automation/status', methods=['GET'])
@handle_errors
def get_automation_status():
    """Get automation status"""
    status = automation_manager.get_status()
    return jsonify(status)

@api.route('/logs', methods=['GET'])
@handle_errors
def get_logs():
    """Get recent log entries"""
    try:
        log_config = current_app.config.get('privacy_config', {}).get('logging', {})
        log_file = log_config.get('file', 'privacyguard.log')
        
        # Read last 100 lines of log file
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]
        
        return jsonify({
            'logs': logs,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve logs: {str(e)}',
            'status': 'error'
        }), 500

# Register error handlers
@api.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Resource not found',
        'status': 'error'
    }), 404

@api.route('/reports', methods=['GET'])
@handle_errors
def get_reports():
    """Get aggregated report data from logs"""
    report_data = ReportGenerator.generate_report_data()
    return jsonify({
        'report': report_data,
        'status': 'success'
    })

@api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500
