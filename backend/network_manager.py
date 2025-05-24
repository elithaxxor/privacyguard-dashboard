import netifaces
import logging
import sys
from pyroute2 import IPRoute
from typing import Dict, List, Optional
import subprocess
import platform
import json

logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self._setup_logging()
        try:
            self.ip = IPRoute()
        except Exception as e:
            logger.warning(f"Could not initialize IPRoute: {e}. Network operations disabled.")
            self.ip = None

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
        if self.ip is None:
            logger.warning("get_available_interfaces: IPRoute not available; using fallback via netifaces.")
            interfaces = []
            for iface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(iface)
                    ipv4 = addrs.get(netifaces.AF_INET, [])
                    ipv4_addr = ipv4[0]['addr'] if ipv4 else None
                    mac_addr = addrs.get(netifaces.AF_LINK, [{}])[0].get('addr')
                    interfaces.append({
                        'name': iface,
                        'ipv4_address': ipv4_addr,
                        'is_up': None,
                        'type': 'Unknown',
                        'mac_address': mac_addr
                    })
                except Exception as e:
                    logger.error(f"Error getting details for interface {iface}: {e}")
            return interfaces
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

            # Replace default route to use this interface
            # This will remove any existing default route and add the new one
            self.ip.route('replace',
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
        if self.ip is None:
            logger.warning("get_current_routing: IPRoute not available; returning empty routing info.")
            return {
                'default_routes': [],
                'preferred_interface': self.config.get('preferred_interface')
            }
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
        if self.ip is None:
            logger.warning("check_interface_status: IPRoute not available; using fallback via netifaces.")
            try:
                if interface_name not in netifaces.interfaces():
                    raise ValueError(f"Interface {interface_name} does not exist")
                addrs = netifaces.ifaddresses(interface_name)
                ipv4_addr = addrs.get(netifaces.AF_INET, [{}])[0].get('addr')
                mac_addr = addrs.get(netifaces.AF_LINK, [{}])[0].get('addr')
                return {
                    'name': interface_name,
                    'is_up': None,
                    'ipv4_address': ipv4_addr,
                    'mac_address': mac_addr,
                    'type': self._determine_interface_type(interface_name)
                }
            except Exception as fallback_e:
                logger.error(f"Error checking interface status fallback: {fallback_e}")
                return {'error': str(fallback_e)}
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
            system = platform.system()
            if system == 'Linux':
                cmd = ['ip', 'link', 'set', interface_name, state]
            elif system == 'Darwin':
                cmd = ['ifconfig', interface_name, state]
            else:
                raise Exception(f"Unsupported OS: {system}, cannot toggle interface")
            result = subprocess.run(cmd, capture_output=True, text=True)
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
