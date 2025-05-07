// API endpoint configuration
const API_BASE_URL = 'http://localhost:8001/api';  // Using port 8001 for backend API

// DOM Elements
const elements = {
    // Status elements
    currentInterface: document.getElementById('currentInterface'),
    ipAddress: document.getElementById('ipAddress'),
    vpnStatus: document.getElementById('vpnStatus'),
    proxyStatus: document.getElementById('proxyStatus'),
    torStatus: document.getElementById('torStatus'),
    autoStatus: document.getElementById('autoStatus'),
    activeRules: document.getElementById('activeRules'),
    interfacesList: document.getElementById('interfacesList'),
    activityLogs: document.getElementById('activityLogs'),

    // Buttons
    refreshBtn: document.getElementById('refreshBtn'),
    settingsBtn: document.getElementById('settingsBtn'),
    closeSettingsBtn: document.getElementById('closeSettingsBtn'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),
    clearLogsBtn: document.getElementById('clearLogsBtn'),

    // Modal
    settingsModal: document.getElementById('settingsModal'),

    // Settings form elements
    automationEnabled: document.getElementById('automationEnabled'),
    checkInterval: document.getElementById('checkInterval'),
    vpnEnabled: document.getElementById('vpnEnabled'),
    proxyEnabled: document.getElementById('proxyEnabled'),
    torEnabled: document.getElementById('torEnabled')
};

// API Functions
const api = {
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API Get Error:', error);
            throw error;
        }
    },

    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API Post Error:', error);
            throw error;
        }
    }
};

// UI Update Functions
const ui = {
    updateNetworkStatus(data) {
        elements.currentInterface.textContent = data.preferred_interface || 'None';
        elements.ipAddress.textContent = data.ip_address || 'Not available';
    },

    updatePrivacyStatus(config) {
        elements.vpnStatus.textContent = config.vpn.enabled ? 'Enabled' : 'Disabled';
        elements.proxyStatus.textContent = config.proxy.enabled ? 'Enabled' : 'Disabled';
        elements.torStatus.textContent = config.tor.enabled ? 'Enabled' : 'Disabled';

        // Update status colors
        elements.vpnStatus.className = config.vpn.enabled ? 'font-medium text-green-600' : 'font-medium text-red-600';
        elements.proxyStatus.className = config.proxy.enabled ? 'font-medium text-green-600' : 'font-medium text-red-600';
        elements.torStatus.className = config.tor.enabled ? 'font-medium text-green-600' : 'font-medium text-red-600';
    },

    updateAutomationStatus(data) {
        elements.autoStatus.textContent = data.enabled ? 'Enabled' : 'Disabled';
        elements.activeRules.textContent = data.active_rules?.length || '0';
        
        // Update status colors
        elements.autoStatus.className = data.enabled ? 'font-medium text-green-600' : 'font-medium text-red-600';
    },

    updateInterfacesList(interfaces) {
        elements.interfacesList.innerHTML = '';
        
        interfaces.forEach(iface => {
            const interfaceEl = document.createElement('div');
            interfaceEl.className = 'flex items-center justify-between p-4 bg-gray-50 rounded-lg';
            
            const statusClass = iface.is_up ? 'text-green-600' : 'text-red-600';
            const statusIcon = iface.is_up ? 'fa-check-circle' : 'fa-times-circle';
            
            interfaceEl.innerHTML = `
                <div class="flex items-center space-x-4">
                    <i class="fas ${iface.type === 'Wi-Fi' ? 'fa-wifi' : 'fa-network-wired'} text-blue-600"></i>
                    <div>
                        <h4 class="font-medium text-gray-800">${iface.name}</h4>
                        <p class="text-sm text-gray-600">${iface.ipv4_address || 'No IP'}</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <i class="fas ${statusIcon} ${statusClass}"></i>
                    <button class="toggle-interface px-3 py-1 rounded-md ${iface.is_up ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}"
                            data-interface="${iface.name}" data-action="${iface.is_up ? 'disable' : 'enable'}">
                        ${iface.is_up ? 'Disable' : 'Enable'}
                    </button>
                </div>
            `;
            
            elements.interfacesList.appendChild(interfaceEl);
        });
    },

    addLogEntry(message, type = 'info') {
        const logEl = document.createElement('div');
        const typeColors = {
            info: 'text-blue-600',
            success: 'text-green-600',
            error: 'text-red-600',
            warning: 'text-yellow-600'
        };
        
        logEl.className = `flex items-center space-x-2 text-sm ${typeColors[type] || typeColors.info}`;
        logEl.innerHTML = `
            <span class="font-medium">[${new Date().toLocaleTimeString()}]</span>
            <span>${message}</span>
        `;
        
        elements.activityLogs.insertBefore(logEl, elements.activityLogs.firstChild);
    },

    showError(message) {
        this.addLogEntry(message, 'error');
    }
};

// Event Handlers
const handlers = {
    async refreshData() {
        try {
            const [interfaces, routing, config, automation] = await Promise.all([
                api.get('/interfaces'),
                api.get('/routing'),
                api.get('/config'),
                api.get('/automation/status')
            ]);

            ui.updateNetworkStatus(routing.routing);
            ui.updatePrivacyStatus(config.config);
            ui.updateAutomationStatus(automation);
            ui.updateInterfacesList(interfaces.interfaces);
            
            ui.addLogEntry('Dashboard refreshed successfully', 'success');
        } catch (error) {
            ui.showError('Failed to refresh dashboard: ' + error.message);
        }
    },

    async toggleInterface(event) {
        if (!event.target.matches('.toggle-interface')) return;
        
        const interfaceName = event.target.dataset.interface;
        const action = event.target.dataset.action;
        
        try {
            await api.post(`/interface/${interfaceName}/toggle`, {
                enable: action === 'enable'
            });
            
            ui.addLogEntry(`${interfaceName} ${action}d successfully`, 'success');
            await handlers.refreshData();
        } catch (error) {
            ui.showError(`Failed to ${action} ${interfaceName}: ${error.message}`);
        }
    },

    async saveSettings() {
        const newConfig = {
            automation: {
                enabled: elements.automationEnabled.checked,
                check_interval: parseInt(elements.checkInterval.value)
            },
            vpn: {
                enabled: elements.vpnEnabled.checked
            },
            proxy: {
                enabled: elements.proxyEnabled.checked
            },
            tor: {
                enabled: elements.torEnabled.checked
            }
        };

        try {
            await api.post('/config', newConfig);
            ui.addLogEntry('Settings saved successfully', 'success');
            elements.settingsModal.classList.add('hidden');
            await handlers.refreshData();
        } catch (error) {
            ui.showError('Failed to save settings: ' + error.message);
        }
    },

    toggleSettingsModal() {
        elements.settingsModal.classList.toggle('hidden');
    }
};

// Event Listeners
function setupEventListeners() {
    elements.refreshBtn.addEventListener('click', handlers.refreshData);
    elements.settingsBtn.addEventListener('click', handlers.toggleSettingsModal);
    elements.closeSettingsBtn.addEventListener('click', handlers.toggleSettingsModal);
    elements.saveSettingsBtn.addEventListener('click', handlers.saveSettings);
    elements.interfacesList.addEventListener('click', handlers.toggleInterface);
    elements.clearLogsBtn.addEventListener('click', () => {
        elements.activityLogs.innerHTML = '';
        ui.addLogEntry('Logs cleared', 'info');
    });
}

// Initialize
async function initialize() {
    setupEventListeners();
    await handlers.refreshData();
    
    // Refresh data periodically
    setInterval(handlers.refreshData, 30000); // Every 30 seconds
}

// Start the application
initialize().catch(error => {
    ui.showError('Failed to initialize application: ' + error.message);
});
