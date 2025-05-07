import netifaces
import logging
from pyroute2 import IPRoute
from typing import Dict, List, Optional
import subprocess
import json

logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.ip = IPRoute()
        self._setup_logging()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return {}

    def _setup_logging(self):
        """Configure logging for the network manager."""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=log_config.get('level', 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def get_available_interfaces(self) -> List[Dict]:
        """
        Get a list of available network interfaces with their details.
        Returns a list of dictionaries containing interface information.
        """
        try:
            interfaces = []
            for iface in netifaces.interfaces():
                try:
                    # Get interface addresses
                    addrs = netifaces.ifaddresses(iface)
                    
                    # Get IPv4 address if available
                    ipv4 = addrs.get(netifaces.AF_INET, [])
                    ipv4_addr = ipv4[0]['addr'] if ipv4 else None
                    
                    # Get interface flags and other details
                    link = self.ip.link('get', ifname=iface)[0]
                    
                    interface_info = {
                        'name': iface,
                        'ipv4_address': ipv4_addr,
                        'is_up': bool(link['flags'] & 1),  # Check if interface is UP
                        'type': self._determine_interface_type(iface),
                        'mac_address': addrs.get(netifaces.AF_LINK, [{}])[0].get('addr')
                    }
                    
                    interfaces.append(interface_info)
                except Exception as e:
                    logger.error(f"Error getting details for interface {iface}: {str(e)}")
                    continue
                    
            return interfaces
        except Exception as e:
            logger.error(f"Error listing network interfaces: {str(e)}")
            return []

    def _determine_interface_type(self, iface: str) -> str:
        """
        Determine the type of network interface (Wi-Fi, Cellular, Ethernet, etc.).
        """
        try:
            # Common naming patterns for different interface types
            if iface.startswith(('wlan', 'wifi', 'wlp')):
                return 'Wi-Fi'
            elif iface.startswith(('wwp', 'wwan')):
                return 'Cellular'
            elif iface.startswith(('eth', 'enp')):
                return 'Ethernet'
            elif iface == 'lo':
                return 'Loopback'
            else:
                return 'Unknown'
        except Exception as e:
            logger.error(f"Error determining interface type: {str(e)}")
            return 'Unknown'

    def set_preferred_routing(self, interface_name: str) -> bool:
        """
        Set the preferred routing interface.
        Returns True if successful, False otherwise.
        """
        try:
            # Verify interface exists
            if interface_name not in netifaces.interfaces():
                raise ValueError(f"Interface {interface_name} does not exist")

            # Get interface index
            idx = self.ip.link_lookup(ifname=interface_name)[0]

            # Set interface as default route
            self.ip.route('add', 
                         dst='default', 
                         oif=idx,
                         priority=100)

            logger.info(f"Successfully set {interface_name} as preferred routing interface")
            return True

        except Exception as e:
            logger.error(f"Failed to set preferred routing: {str(e)}")
            return False

    def get_current_routing(self) -> Dict:
        """
        Get current routing information.
        Returns a dictionary with routing details.
        """
        try:
            routes = []
            for route in self.ip.route('show'):
                if route.get('dst', '') == 'default':
                    idx = route.get('oif', 0)
                    interface = self.ip.get_links(idx)[0].get_attr('IFLA_IFNAME')
                    routes.append({
                        'interface': interface,
                        'priority': route.get('priority', 0),
                        'protocol': route.get('protocol', 'unknown')
                    })
            
            return {
                'default_routes': routes,
                'preferred_interface': self.config.get('preferred_interface')
            }
        except Exception as e:
            logger.error(f"Error getting routing information: {str(e)}")
            return {'error': str(e)}

    def check_interface_status(self, interface_name: str) -> Dict:
        """
        Check the status of a specific interface.
        Returns a dictionary with interface status details.
        """
        try:
            if interface_name not in netifaces.interfaces():
                raise ValueError(f"Interface {interface_name} does not exist")

            link = self.ip.link('get', ifname=interface_name)[0]
            addrs = netifaces.ifaddresses(interface_name)
            
            return {
                'name': interface_name,
                'is_up': bool(link['flags'] & 1),
                'ipv4_address': addrs.get(netifaces.AF_INET, [{}])[0].get('addr'),
                'mac_address': addrs.get(netifaces.AF_LINK, [{}])[0].get('addr'),
                'type': self._determine_interface_type(interface_name)
            }
        except Exception as e:
            logger.error(f"Error checking interface status: {str(e)}")
            return {'error': str(e)}

    def toggle_interface(self, interface_name: str, enable: bool) -> bool:
        """
        Enable or disable a network interface.
        Returns True if successful, False otherwise.
        """
        try:
            if interface_name not in netifaces.interfaces():
                raise ValueError(f"Interface {interface_name} does not exist")

            state = "up" if enable else "down"
            result = subprocess.run(['ip', 'link', 'set', interface_name, state],
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully set interface {interface_name} {state}")
                return True
            else:
                raise Exception(f"Failed to set interface {state}: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error toggling interface: {str(e)}")
            return False

    def cleanup(self):
        """Cleanup network manager resources."""
        try:
            self.ip.close()
            logger.info("Network manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
