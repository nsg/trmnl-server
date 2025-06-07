class LogViewer {
    constructor() {
        this.loadingEl = document.getElementById('loading');
        this.errorEl = document.getElementById('error');
        this.containerEl = document.getElementById('logContainer');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.limitSelect = document.getElementById('limitSelect');
        this.autoRefreshSelect = document.getElementById('autoRefreshSelect');
        this.autoRefreshIndicator = document.getElementById('autoRefreshIndicator');
        this.autoRefreshTimer = null;
        this.lastLogsData = null;
        
        this.init();
    }
    
    init() {
        this.refreshBtn.addEventListener('click', () => this.loadLogs(true));
        this.limitSelect.addEventListener('change', () => this.loadLogs(true));
        this.autoRefreshSelect.addEventListener('change', () => this.setupAutoRefresh());
        this.loadLogs(true);
        this.setupAutoRefresh();
    }
    
    setupAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
        }
        
        const interval = parseInt(this.autoRefreshSelect.value);
        if (interval > 0) {
            this.autoRefreshIndicator.classList.add('active');
            this.autoRefreshTimer = setInterval(() => {
                this.loadLogs(false);
            }, interval * 1000);
        } else {
            this.autoRefreshIndicator.classList.remove('active');
        }
    }
    
    async loadLogs(forceUpdate = false) {
        try {
            if (forceUpdate || !this.lastLogsData) {
                this.showLoading();
            }
            
            const limit = this.limitSelect.value;
            const response = await fetch(`/api/logs?limit=${limit}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (this.hasDataChanged(data)) {
                this.lastLogsData = data;
                this.renderLogs(data.logs);
            }
            
            this.hideLoading();
        } catch (error) {
            this.showError(`Failed to load logs: ${error.message}`);
        }
    }
    
    hasDataChanged(newData) {
        if (!this.lastLogsData) {
            return true;
        }
        
        if (newData.logs.length !== this.lastLogsData.logs.length) {
            return true;
        }
        
        const compareCount = Math.min(5, newData.logs.length);
        for (let i = 0; i < compareCount; i++) {
            const newLog = newData.logs[i];
            const oldLog = this.lastLogsData.logs[i];
            
            if (!oldLog || 
                newLog.log_id !== oldLog.log_id || 
                newLog.received_at !== oldLog.received_at) {
                return true;
            }
        }
        
        return false;
    }
    
    showLoading() {
        this.loadingEl.style.display = 'block';
        this.errorEl.style.display = 'none';
        this.containerEl.style.display = 'none';
    }
    
    hideLoading() {
        this.loadingEl.style.display = 'none';
        this.containerEl.style.display = 'block';
    }
    
    showError(message) {
        this.loadingEl.style.display = 'none';
        this.errorEl.textContent = message;
        this.errorEl.style.display = 'block';
        this.containerEl.style.display = 'none';
    }
    
    renderLogs(logs) {
        if (logs.length === 0) {
            this.containerEl.innerHTML = '<div class="log-entry"><div class="log-summary"><p>No logs found.</p></div></div>';
            return;
        }
        
        const html = logs.map(log => this.renderLogEntry(log)).join('');
        this.containerEl.innerHTML = html;
        
        this.containerEl.querySelectorAll('.log-summary').forEach(summary => {
            summary.addEventListener('click', (e) => {
                const logEntry = e.currentTarget.closest('.log-entry');
                logEntry.classList.toggle('expanded');
            });
        });
    }
    
    renderLogEntry(log) {
        const logClass = this.getLogClass(log.log_message);
        const deviceStatus = this.renderDeviceStatus(log.device_status);
        const timestamp = new Date(log.received_at).toISOString().replace('T', ' ').substring(0, 19);
        
        const messagePreview = log.log_message.length > 80 
            ? log.log_message.substring(0, 80) + '...'
            : log.log_message;
        
        return `
            <div class="log-entry ${logClass}">
                <div class="log-summary">
                    <div class="expand-arrow"></div>
                    <div class="log-summary-content">
                        <div class="log-message-preview">${messagePreview}</div>
                        <div class="log-meta">
                            <span>Device: ${log.device_id}</span>
                            <span class="timestamp-bold">${timestamp}</span>
                        </div>
                    </div>
                </div>
                
                <div class="log-details">
                    <div class="log-message-full">${log.log_message}</div>
                    
                    <div class="log-details-content">
                        <div class="log-details-left">
                            <div class="log-info-compact">
                                <div class="log-field-compact">
                                    <span class="label">Device ID</span>
                                    <span class="value">${log.device_id}</span>
                                </div>
                                <div class="log-field-compact">
                                    <span class="label">Log ID</span>
                                    <span class="value">${log.log_id}</span>
                                </div>
                                <div class="log-field-compact">
                                    <span class="label">Source</span>
                                    <span class="value">${log.log_sourcefile}:${log.log_codeline}</span>
                                </div>
                                <div class="log-field-compact">
                                    <span class="label">Firmware</span>
                                    <span class="value">${log.device_status.current_fw_version || 'N/A'}</span>
                                </div>
                                <div class="log-field-compact">
                                    <span class="label">Battery</span>
                                    <span class="value">${log.device_status.battery_voltage || 'N/A'}V</span>
                                </div>
                                <div class="log-field-compact">
                                    <span class="label">WiFi RSSI</span>
                                    <span class="value">${log.device_status.wifi_rssi_level || 'N/A'} dBm</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="log-details-right">
                            ${deviceStatus}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getLogClass(message) {
        const lowerMsg = message.toLowerCase();
        if (lowerMsg.includes('error') || lowerMsg.includes('failed')) {
            return 'error';
        }
        if (lowerMsg.includes('warning') || lowerMsg.includes('warn')) {
            return 'warning';
        }
        return '';
    }
    
    renderDeviceStatus(status) {
        if (!status || Object.keys(status).length === 0) {
            return '';
        }
        
        const statusItems = Object.entries(status)
            .map(([key, value]) => `
                <div class="log-field-compact">
                    <span class="label">${key.replace(/_/g, ' ')}</span>
                    <span class="value">${value}</span>
                </div>
            `).join('');
        
        return `
            <div class="log-info-compact">
                ${statusItems}
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new LogViewer();
});
