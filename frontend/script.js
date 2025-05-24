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
    privacyStatusContainer: document.getElementById('privacyStatus'),
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
    themeToggleBtn: document.getElementById('themeToggleBtn'),
    themeIcon: document.getElementById('themeIcon'),

    // Modal
    settingsModal: document.getElementById('settingsModal'),
    // Logs
    loadLogsBtn: document.getElementById('loadLogsBtn'),
    logFilter: document.getElementById('logFilter'),

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

// Toast container
const toastContainer = document.getElementById('toastContainer');

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
        // Update toggle buttons for privacy features
        ['vpn', 'proxy', 'tor'].forEach(feature => {
            const enabled = config[feature].enabled;
            const btn = document.querySelector(`.toggle-privacy[data-feature="${feature}"]`);
            if (btn) {
                btn.textContent = enabled ? 'Disable' : 'Enable';
                btn.dataset.action = enabled ? 'disable' : 'enable';
                if (enabled) {
                    btn.className = 'toggle-privacy px-3 py-1 rounded-md bg-red-100 text-red-600';
                } else {
                    btn.className = 'toggle-privacy px-3 py-1 rounded-md bg-green-100 text-green-600';
                }
            }
        });
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
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const bgColors = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500'
        };
        toast.className = `${bgColors[type] || bgColors.info} text-white px-4 py-2 rounded shadow-lg max-w-xs opacity-90`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('transition', 'opacity-0');
            toast.addEventListener('transitionend', () => toast.remove());
        }, 4000);
    },

    showError(message) {
        this.addLogEntry(message, 'error');
        this.showToast(message, 'error');
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
            ui.showToast('Dashboard refreshed', 'success');
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
            ui.showToast(`${interfaceName} ${action}d`, 'success');
            await handlers.refreshData();
        } catch (error) {
            ui.showError(`Failed to ${action} ${interfaceName}: ${error.message}`);
        }
    },
    // Toggle privacy feature (VPN, proxy, Tor)
    async togglePrivacy(event) {
        if (!event.target.matches('.toggle-privacy')) return;
        const feature = event.target.dataset.feature;
        const action = event.target.dataset.action;
        try {
            const data = {};
            data[feature] = { enabled: action === 'enable' };
            await api.post('/config', data);
            ui.addLogEntry(`${feature.toUpperCase()} ${action}d successfully`, 'success');
            ui.showToast(`${feature.toUpperCase()} ${action}d`, 'success');
            await handlers.refreshData();
        } catch (error) {
            ui.showError(`Failed to ${action} ${feature}: ${error.message}`);
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
            ui.showToast('Settings saved', 'success');
            elements.settingsModal.classList.add('hidden');
            await handlers.refreshData();
        } catch (error) {
            ui.showError('Failed to save settings: ' + error.message);
        }
    },

    toggleSettingsModal() {
        const modal = elements.settingsModal;
        modal.classList.toggle('hidden');
        const isOpen = !modal.classList.contains('hidden');
        if (isOpen) {
            // Focus the modal container
            const container = modal.querySelector('div[tabindex]');
            if (container) container.focus();
        } else {
            // Return focus to settings button
            elements.settingsBtn.focus();
        }
    }
  ,
  async loadServerLogs() {
    try {
      const res = await api.get('/logs');
      const logs = res.logs || [];
      elements.activityLogs.innerHTML = '';
      logs.reverse().forEach(line => {
        const el = document.createElement('div');
        el.textContent = line.trim();
        elements.activityLogs.appendChild(el);
      });
      ui.showToast('Server logs loaded', 'success');
    } catch (e) {
      ui.showError('Failed to load server logs: ' + e.message);
    }
  },
  filterLogs() {
    const term = elements.logFilter.value.toLowerCase();
    document.querySelectorAll('#activityLogs > div').forEach(el => {
      el.style.display = el.textContent.toLowerCase().includes(term) ? '' : 'none';
    });
  }
  ,
  toggleTheme() {
    const root = document.documentElement;
    root.classList.toggle('dark');
    const isDark = root.classList.contains('dark');
    elements.themeIcon.classList.toggle('fa-sun', isDark);
    elements.themeIcon.classList.toggle('fa-moon', !isDark);
    try {
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    } catch {}
  }
};

// Event Listeners
function setupEventListeners() {
    elements.refreshBtn.addEventListener('click', handlers.refreshData);
    elements.settingsBtn.addEventListener('click', handlers.toggleSettingsModal);
    elements.closeSettingsBtn.addEventListener('click', handlers.toggleSettingsModal);
    elements.saveSettingsBtn.addEventListener('click', handlers.saveSettings);
    elements.interfacesList.addEventListener('click', handlers.toggleInterface);
    elements.privacyStatusContainer.addEventListener('click', handlers.togglePrivacy);
    elements.clearLogsBtn.addEventListener('click', () => {
        elements.activityLogs.innerHTML = '';
        ui.addLogEntry('Logs cleared', 'info');
        ui.showToast('Logs cleared', 'info');
    });
    elements.loadLogsBtn.addEventListener('click', handlers.loadServerLogs);
    elements.logFilter.addEventListener('input', handlers.filterLogs);
    // Theme toggle
    elements.themeToggleBtn.addEventListener('click', handlers.toggleTheme);
    // Global keydown for modal ESC and focus trap
    document.addEventListener('keydown', (e) => {
        const modal = elements.settingsModal;
        if (!modal.classList.contains('hidden')) {
            if (e.key === 'Escape') {
                handlers.toggleSettingsModal();
            }
            if (e.key === 'Tab') {
                const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (focusable.length === 0) return;
                const first = focusable[0];
                const last = focusable[focusable.length - 1];
                if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault(); first.focus();
                }
                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault(); last.focus();
                }
            }
        }
    });
}

// Drag-and-Drop Section Ordering
function saveSectionOrder() {
  try {
    const container = document.getElementById('dashboardContainer');
    const ids = Array.from(container.querySelectorAll('.draggable-section')).map(el => el.id);
    localStorage.setItem('dashboardOrder', JSON.stringify(ids));
  } catch {}
}

function loadSectionOrder() {
  try {
    const container = document.getElementById('dashboardContainer');
    const order = JSON.parse(localStorage.getItem('dashboardOrder') || '[]');
    order.forEach(id => {
      const el = document.getElementById(id);
      if (el) container.appendChild(el);
    });
  } catch {}
}

// Set up HTML5 drag-and-drop for sections
function setupDragAndDrop() {
  const container = document.getElementById('dashboardContainer');
  let draggedId = null;
  container.querySelectorAll('.draggable-section').forEach(section => {
    section.addEventListener('dragstart', e => {
      draggedId = section.id;
      section.classList.add('opacity-50');
      e.dataTransfer.effectAllowed = 'move';
    });
    section.addEventListener('dragend', () => {
      section.classList.remove('opacity-50');
      saveSectionOrder();
    });
    section.addEventListener('dragover', e => {
      e.preventDefault();
      section.classList.add('border-2', 'border-blue-400');
    });
    section.addEventListener('dragleave', () => {
      section.classList.remove('border-2', 'border-blue-400');
    });
    section.addEventListener('drop', e => {
      e.preventDefault();
      section.classList.remove('border-2', 'border-blue-400');
      if (draggedId && draggedId !== section.id) {
        const draggedEl = document.getElementById(draggedId);
        container.insertBefore(draggedEl, section);
      }
    });
  });
}

// Initialize
async function initialize() {
    setupEventListeners();
    setupDragAndDrop();
    loadSectionOrder();
    // Initialize theme from localStorage or system preference
    try {
        const saved = localStorage.getItem('theme');
        const useDark = saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
        if (useDark) {
            document.documentElement.classList.add('dark');
            elements.themeIcon.classList.add('fa-sun');
            elements.themeIcon.classList.remove('fa-moon');
        }
    } catch {}
    await handlers.refreshData();
    
    // Refresh data periodically
    setInterval(handlers.refreshData, 30000); // Every 30 seconds
}

// Start the application
initialize().catch(error => {
    ui.showError('Failed to initialize application: ' + error.message);
});
