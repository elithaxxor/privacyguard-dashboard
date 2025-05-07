import logging
from logging.handlers import RotatingFileHandler
import json
from typing import Dict, Any, Optional
from functools import wraps
import time
from datetime import datetime, timedelta
from collections import defaultdict
import os
import re

class LoggerSetup:
    @staticmethod
    def setup_logger(name: str, config: Dict[str, Any]) -> logging.Logger:
        """
        Set up a logger with both file and console handlers.
        
        Args:
            name: Name of the logger
            config: Configuration dictionary containing logging settings
        
        Returns:
            logging.Logger: Configured logger instance
        """
        log_config = config.get('logging', {
            'level': 'INFO',
            'file': 'privacyguard.log',
            'max_size': 10485760,  # 10MB
            'backup_count': 3
        })

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(log_config.get('level', 'INFO'))

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )

        # File handler
        log_file = log_config.get('file', 'privacyguard.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get('max_size', 10485760),
            backupCount=log_config.get('backup_count', 3)
        )
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

class ConfigManager:
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config from {config_path}: {str(e)}")
            return {}

    @staticmethod
    def save_config(config: Dict[str, Any], config_path: str) -> bool:
        """
        Save configuration to a JSON file.
        
        Args:
            config: Configuration dictionary to save
            config_path: Path to save the configuration file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to save config to {config_path}: {str(e)}")
            return False

    @staticmethod
    def update_config(config_path: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update specific configuration values.
        
        Args:
            config_path: Path to the configuration file
            updates: Dictionary containing updates to apply
            
        Returns:
            dict: Updated configuration dictionary
        """
        current_config = ConfigManager.load_config(config_path)
        current_config.update(updates)
        if ConfigManager.save_config(current_config, config_path):
            return current_config
        return {}

class Performance:
    @staticmethod
    def timing_decorator(func):
        """
        Decorator to measure function execution time.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            logger = logging.getLogger(func.__module__)
            logger.debug(f"Function {func.__name__} took {end_time - start_time:.2f} seconds to execute")
            
            return result
        return wrapper

class ErrorHandler:
    @staticmethod
    def handle_errors(func):
        """
        Decorator to handle and log errors.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__module__)
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper

class NetworkUtils:
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Validate an IP address.
        
        Args:
            ip: IP address string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            parts = ip.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except (AttributeError, TypeError, ValueError):
            return False

    @staticmethod
    def format_interface_info(info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format network interface information for consistent output.
        
        Args:
            info: Raw interface information dictionary
            
        Returns:
            dict: Formatted interface information
        """
        return {
            'name': info.get('name', 'unknown'),
            'type': info.get('type', 'unknown'),
            'ip_address': info.get('ipv4_address', None),
            'mac_address': info.get('mac_address', None),
            'is_up': info.get('is_up', False),
            'last_updated': datetime.now().isoformat()
        }

class SecurityUtils:
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate configuration for security issues.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['proxy', 'vpn', 'tor', 'automation']
        return all(field in config for field in required_fields)

    @staticmethod
    def sanitize_log_message(message: str) -> str:
        """
        Sanitize log messages to prevent log injection.
        
        Args:
            message: Log message to sanitize
            
        Returns:
            str: Sanitized message
        """
        # Remove potential newlines and control characters
        return ' '.join(message.split())

class SystemUtils:
    @staticmethod
    def check_permissions() -> bool:
        """
        Check if the application has necessary permissions.
        
        Returns:
            bool: True if permissions are sufficient, False otherwise
        """
        try:
            return os.geteuid() == 0  # Check for root/admin privileges
        except AttributeError:
            return False  # Windows systems

    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """
        Get basic system information.
        
        Returns:
            dict: System information dictionary
        """
        return {
            'platform': os.name,
            'python_version': os.sys.version,
            'working_directory': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        }

class ReportGenerator:
    """
    ReportGenerator Class
    
    This class handles the generation of analytics and reporting data by parsing
    the application's log files. It aggregates various metrics including network
    events, privacy tool usage, and automation rule executions.
    
    Features:
    - Parses log files for event data
    - Aggregates metrics over time periods
    - Generates timeline data for visualizations
    - Tracks success/failure rates of operations
    - Monitors privacy tool usage patterns
    """
    
    @staticmethod
    def generate_report_data() -> Dict[str, Any]:
        """
        Generate aggregated report data from the log file.
        
        This method processes the log file to extract and aggregate various metrics:
        - Network interface events (enables/disables)
        - Privacy tool actions (VPN/Proxy/Tor toggles)
        - Automation rule executions
        - Timeline data for the last 24 hours
        
        Returns:
            Dict containing:
            - networkEvents: interface toggle counts and timeline
            - privacyEvents: VPN/Proxy/Tor usage statistics
            - automationEvents: rule execution counts
        
        Example return format:
        {
            'networkEvents': {
                'total': 10,
                'success': 8,
                'failure': 2,
                'timeline': [{'time': '14:00', 'count': 3}, ...]
            },
            'privacyEvents': {
                'total': 6,
                'vpn': 2,
                'proxy': 2,
                'tor': 2
            },
            'automationEvents': {
                'total': 4,
                'rules': [{'name': 'switch_to_wifi', 'executions': 2}, ...]
            }
        }
        """
        try:
            log_file = 'privacyguard.log'
            with open(log_file, 'r') as f:
                lines = f.readlines()

            # Initialize counters
            network_events = defaultdict(int)
            privacy_events = defaultdict(int)
            automation_events = defaultdict(int)
            timeline_events = []

            # Initialize timeline data structure (last 24 hours in 1-hour intervals)
            now = datetime.now()
            timeline = {
                (now - timedelta(hours=x)).strftime('%H:00'): 0 
                for x in range(24)
            }

            # Parse log lines
            for line in lines:
                try:
                    # Extract timestamp
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        hour = timestamp.strftime('%H:00')
                        
                        # Only process events from last 24 hours
                        if now - timestamp <= timedelta(hours=24):
                            # Network events
                            if "interface" in line:
                                if "Successfully" in line:
                                    network_events['success'] += 1
                                    timeline[hour] += 1
                                elif "Failed to" in line:
                                    network_events['failure'] += 1

                            # Privacy events
                            if "VPN" in line:
                                privacy_events['vpn'] += 1
                            elif "Proxy" in line:
                                privacy_events['proxy'] += 1
                            elif "Tor" in line:
                                privacy_events['tor'] += 1

                            # Automation events
                            if "Executed rule action" in line:
                                rule_match = re.search(r'action: (\w+)', line)
                                if rule_match:
                                    rule_name = rule_match.group(1)
                                    automation_events[rule_name] += 1

                except Exception as e:
                    logger.error(f"Error parsing log line: {str(e)}")
                    continue

            # Prepare timeline data
            timeline_data = [
                {'time': hour, 'count': count}
                for hour, count in timeline.items()
            ]

            # Prepare automation rules data
            automation_rules = [
                {'name': rule, 'executions': count}
                for rule, count in automation_events.items()
            ]

            return {
                'networkEvents': {
                    'total': sum(network_events.values()),
                    'success': network_events['success'],
                    'failure': network_events['failure'],
                    'timeline': timeline_data
                },
                'privacyEvents': {
                    'total': sum(privacy_events.values()),
                    'vpn': privacy_events['vpn'],
                    'proxy': privacy_events['proxy'],
                    'tor': privacy_events['tor']
                },
                'automationEvents': {
                    'total': sum(automation_events.values()),
                    'rules': automation_rules
                }
            }

        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            return {
                'error': str(e),
                'networkEvents': {'total': 0, 'timeline': []},
                'privacyEvents': {'total': 0},
                'automationEvents': {'total': 0, 'rules': []}
            }

# Initialize default logger
logger = LoggerSetup.setup_logger(
    'privacyguard',
    {'logging': {'level': 'INFO', 'file': 'privacyguard.log'}}
)
