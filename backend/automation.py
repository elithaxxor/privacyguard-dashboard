from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from network_manager import NetworkManager
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AutomationManager:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.network_manager = NetworkManager(config_path)
        self.scheduler = BackgroundScheduler()
        self._setup_logging()
        self.running_jobs = {}

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return {}

    def _setup_logging(self):
        """Configure logging for the automation manager."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=log_config.get('level', 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def start(self):
        """Start the automation scheduler."""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Automation scheduler started")
                self._schedule_tasks()
        except Exception as e:
            logger.error(f"Failed to start automation scheduler: {str(e)}")

    def stop(self):
        """Stop the automation scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Automation scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop automation scheduler: {str(e)}")

    def _schedule_tasks(self):
        """Schedule all automated tasks based on configuration."""
        automation_config = self.config.get('automation', {})
        if not automation_config.get('enabled', False):
            logger.info("Automation is disabled in configuration")
            return

        interval = automation_config.get('check_interval', 60)  # Default 60 seconds
        rules = automation_config.get('rules', [])

        for rule in rules:
            if rule.get('enabled', False):
                self._add_rule_job(rule, interval)

    def _add_rule_job(self, rule: Dict, interval: int):
        """Add a job for a specific rule."""
        try:
            job_id = f"rule_{rule['condition']}_{rule['action']}"
            
            # Remove existing job if it exists
            if job_id in self.running_jobs:
                self.scheduler.remove_job(job_id)
                
            # Add new job
            self.scheduler.add_job(
                func=self._execute_rule,
                trigger=IntervalTrigger(seconds=interval),
                args=[rule],
                id=job_id,
                name=f"AutoRule: {rule['condition']}"
            )
            
            self.running_jobs[job_id] = rule
            logger.info(f"Scheduled automation rule: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to add rule job: {str(e)}")

    def _execute_rule(self, rule: Dict):
        """Execute a specific automation rule."""
        try:
            condition_met = self._check_condition(rule['condition'])
            if condition_met:
                self._perform_action(rule['action'])
                logger.info(f"Executed rule action: {rule['action']}")
        except Exception as e:
            logger.error(f"Failed to execute rule: {str(e)}")

    def _check_condition(self, condition: str) -> bool:
        """Check if a condition is met."""
        try:
            if condition == 'wifi_available':
                interfaces = self.network_manager.get_available_interfaces()
                return any(i['type'] == 'Wi-Fi' and i['is_up'] for i in interfaces)
                
            elif condition == 'wifi_weak_signal':
                # This would require additional implementation to check Wi-Fi signal strength
                # For now, we'll return False
                return False
                
            elif condition == 'cellular_available':
                interfaces = self.network_manager.get_available_interfaces()
                return any(i['type'] == 'Cellular' and i['is_up'] for i in interfaces)
                
            else:
                logger.warning(f"Unknown condition: {condition}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking condition {condition}: {str(e)}")
            return False

    def _perform_action(self, action: str):
        """Perform the specified action."""
        try:
            if action == 'switch_to_wifi':
                wifi_interfaces = [i for i in self.network_manager.get_available_interfaces() 
                                 if i['type'] == 'Wi-Fi' and i['is_up']]
                if wifi_interfaces:
                    self.network_manager.set_preferred_routing(wifi_interfaces[0]['name'])
                    
            elif action == 'switch_to_cellular':
                cellular_interfaces = [i for i in self.network_manager.get_available_interfaces() 
                                    if i['type'] == 'Cellular' and i['is_up']]
                if cellular_interfaces:
                    self.network_manager.set_preferred_routing(cellular_interfaces[0]['name'])
                    
            else:
                logger.warning(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error performing action {action}: {str(e)}")

    def get_status(self) -> Dict:
        """Get current automation status."""
        try:
            return {
                'enabled': self.config.get('automation', {}).get('enabled', False),
                'running': self.scheduler.running,
                'active_rules': list(self.running_jobs.values()),
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting automation status: {str(e)}")
            return {'error': str(e)}

    def update_config(self, new_config: Dict):
        """Update automation configuration."""
        try:
            self.config['automation'] = new_config
            
            # Stop current scheduler
            self.stop()
            
            # Clear running jobs
            self.running_jobs.clear()
            
            # Restart with new configuration if enabled
            if new_config.get('enabled', False):
                self.start()
                
            logger.info("Automation configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update automation config: {str(e)}")
            raise
