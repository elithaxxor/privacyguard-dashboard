import subprocess
import logging
import platform

logger = logging.getLogger(__name__)

class PrivacyManager:
    """
    Manages privacy services: VPN, Proxy, Tor by starting/stopping system services or commands.
    """
    def __init__(self, config_path: str = 'config.json'):
        # Load initial config from file
        import json
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}

    def _run_command(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Ran command successfully: {cmd}")
                return True
            logger.error(f"Command failed ({cmd}): {result.stderr.strip()}")
            return False
        except Exception as e:
            logger.error(f"Error running command {cmd}: {e}")
            return False

    def _default_cmd(self, feature: str, enable: bool):
        # Default systemctl service names
        svc_map = {
            'vpn': 'openvpn-client@client',
            'proxy': 'privoxy',
            'tor': 'tor'
        }
        service = svc_map.get(feature)
        if not service:
            return None
        action = 'start' if enable else 'stop'
        # Only Linux service management supported by default
        system = platform.system()
        if system == 'Linux':
            return ['systemctl', action, service]
        # On macOS, use Homebrew services if available
        if system == 'Darwin':
            return ['brew', 'services', action, service]
        # Fallback: no default command for this platform
        return None

    def set_enabled(self, feature: str, enable: bool) -> bool:
        """
        Enable or disable a privacy feature by name.
        feature: 'vpn', 'proxy', or 'tor'
        enable: True to enable, False to disable
        """
        # Update in-memory config
        cfg = self.config.get(feature, {})
        cfg['enabled'] = enable
        self.config[feature] = cfg
        # Determine command
        # Allow config override keys 'enable_cmd' and 'disable_cmd'
        cmd = None
        if enable:
            cmd = cfg.get('enable_cmd') or self._default_cmd(feature, True)
        else:
            cmd = cfg.get('disable_cmd') or self._default_cmd(feature, False)
        if not cmd:
            logger.warning(f"No command configured for {feature}")
            return False
        return self._run_command(cmd)