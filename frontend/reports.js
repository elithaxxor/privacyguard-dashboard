/**
 * PrivacyGuard Advanced Reporting Module
 * 
 * This module handles the reporting and analytics functionality of the PrivacyGuard dashboard.
 * It provides visualization of network events, privacy tool usage, and automation statistics
 * using Chart.js for data visualization.
 * 
 * Features:
 * - Real-time data updates every 30 seconds
 * - Interactive charts with animations
 * - Network activity timeline
 * - Privacy tools usage distribution
 * - Automation rules execution tracking
 */

// API endpoint configuration
const API_BASE_URL = 'http://localhost:8001/api';  // Using port 8001 for backend API

// DOM Elements
const elements = {
    // Summary counters
    totalNetworkEvents: document.getElementById('totalNetworkEvents'),
    totalPrivacyEvents: document.getElementById('totalPrivacyEvents'),
    totalAutomationEvents: document.getElementById('totalAutomationEvents'),
    
    // Chart canvases
    networkChart: document.getElementById('networkChart'),
    privacyChart: document.getElementById('privacyChart'),
    automationChart: document.getElementById('automationChart'),
    
    // Buttons
    refreshBtn: document.getElementById('refreshBtn')
};

// Chart.js defaults and plugins
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;
Chart.defaults.scale.grid.display = false;
Chart.defaults.plugins.legend.display = true;
Chart.defaults.plugins.tooltip.enabled = true;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.titleFont = { size: 14, family: "'Inter', sans-serif" };
Chart.defaults.plugins.tooltip.bodyFont = { size: 13, family: "'Inter', sans-serif" };

// Chart instances
let charts = {
    network: null,
    privacy: null,
    automation: null
};

// Chart dimensions and styles
const chartStyles = {
    backgroundColor: '#ffffff',
    borderColor: 'rgb(59, 130, 246)',
    borderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
    tension: 0.3
};

// Chart container dimensions
const chartDimensions = {
    width: '100%',
    height: '300px',
    padding: '20px'
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
    }
};

// Chart Configuration and Rendering
const chartConfig = {
    network: {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                title: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        family: "'Inter', sans-serif"
                    },
                    bodyFont: {
                        size: 13,
                        family: "'Inter', sans-serif"
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Events',
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    },
    privacy: {
        type: 'doughnut',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        family: "'Inter', sans-serif"
                    },
                    bodyFont: {
                        size: 13,
                        family: "'Inter', sans-serif"
                    }
                }
            },
            cutout: '70%'
        }
    },
    automation: {
        type: 'bar',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        family: "'Inter', sans-serif"
                    },
                    bodyFont: {
                        size: 13,
                        family: "'Inter', sans-serif"
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Executions',
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    }
};

// UI Update Functions
const ui = {
    updateSummaryCounters(data) {
        elements.totalNetworkEvents.textContent = data.networkEvents.total || '0';
        elements.totalPrivacyEvents.textContent = data.privacyEvents.total || '0';
        elements.totalAutomationEvents.textContent = data.automationEvents.total || '0';
    },

    createNetworkChart(data) {
        console.log('Creating network chart with data:', data.networkEvents);
        try {
            console.log('Network chart element:', elements.networkChart);
            if (!elements.networkChart) {
                console.error('Network chart element not found');
                return;
            }
            const ctx = elements.networkChart.getContext('2d');
            console.log('Network chart context:', ctx);
            if (charts.network) {
                charts.network.destroy();
            }
            charts.network = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.networkEvents.timeline.map(item => item.time),
                    datasets: [{
                        label: 'Interface Toggles',
                        data: data.networkEvents.timeline.map(item => item.count),
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('Network chart created successfully');
        } catch (error) {
            console.error('Error creating network chart:', error);
        }
    },

    createPrivacyChart(data) {
        console.log('Creating privacy chart with data:', data.privacyEvents);
        try {
            console.log('Privacy chart element:', elements.privacyChart);
            if (!elements.privacyChart) {
                console.error('Privacy chart element not found');
                return;
            }
            const ctx = elements.privacyChart.getContext('2d');
            console.log('Privacy chart context:', ctx);
            if (charts.privacy) {
                charts.privacy.destroy();
            }
            charts.privacy = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['VPN', 'Proxy', 'Tor'],
                    datasets: [{
                        data: [
                            data.privacyEvents.vpn || 0,
                            data.privacyEvents.proxy || 0,
                            data.privacyEvents.tor || 0
                        ],
                        backgroundColor: [
                            'rgb(59, 130, 246)',
                            'rgb(16, 185, 129)',
                            'rgb(249, 115, 22)'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    },
                    cutout: '60%'
                }
            });
            console.log('Privacy chart created successfully');
        } catch (error) {
            console.error('Error creating privacy chart:', error);
        }
    },

    createAutomationChart(data) {
        console.log('Creating automation chart with data:', data.automationEvents);
        try {
            console.log('Automation chart element:', elements.automationChart);
            if (!elements.automationChart) {
                console.error('Automation chart element not found');
                return;
            }
            const ctx = elements.automationChart.getContext('2d');
            console.log('Automation chart context:', ctx);
            if (charts.automation) {
                charts.automation.destroy();
            }
            charts.automation = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.automationEvents.rules.map(rule => rule.name),
                    datasets: [{
                        label: 'Rule Executions',
                        data: data.automationEvents.rules.map(rule => rule.executions),
                        backgroundColor: 'rgb(59, 130, 246)',
                        borderRadius: 6,
                        maxBarThickness: 40
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('Automation chart created successfully');
        } catch (error) {
            console.error('Error creating automation chart:', error);
        }
    },

    showError(message) {
        console.error('Error:', message);
        // TODO: Add UI error notification if needed
    }
};

// Data Loading and Chart Initialization
async function loadReportData() {
    try {
        const data = await api.get('/reports');
        
        if (data.status === 'success' && data.report) {
            // Update summary counters
            ui.updateSummaryCounters(data.report);
            
            // Create/update charts
            // Sort timeline data chronologically and filter out zero counts
            const sortedTimelineData = data.report.networkEvents.timeline
                .filter(item => item.count > 0)
                .sort((a, b) => {
                    return a.time.localeCompare(b.time);
                });
            data.report.networkEvents.timeline = sortedTimelineData;

            // Create charts with animation
            try {
                ui.createNetworkChart(data.report);
                ui.createPrivacyChart(data.report);
                ui.createAutomationChart(data.report);
                console.log('Charts created successfully');
            } catch (error) {
                console.error('Error creating charts:', error);
            }
        } else {
            throw new Error('Invalid data format received from API');
        }
    } catch (error) {
        ui.showError(error.message);
    }
}

// Event Listeners
function setupEventListeners() {
    elements.refreshBtn.addEventListener('click', loadReportData);
}

// Initialize
async function initialize() {
    setupEventListeners();
    await loadReportData();
    
    // Refresh data periodically (every 30 seconds)
    setInterval(loadReportData, 30000);
}

// Start the application
initialize().catch(error => {
    ui.showError('Failed to initialize application: ' + error.message);
});
