class LogViewer {
    constructor() {
        this.loadingEl = document.getElementById('loading');
        this.errorEl = document.getElementById('error');
        this.containerEl = document.getElementById('logContainer');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.limitSelect = document.getElementById('limitSelect');
        
        this.init();
    }
    
    init() {
        this.refreshBtn.addEventListener('click', () => this.loadLogs());
        this.limitSelect.addEventListener('change', () => this.loadLogs());
        this.loadLogs();
    }
    
    async loadLogs() {
        try {
            this.showLoading();
            const limit = this.limitSelect.value;
            const response = await fetch(`/api/logs?limit=${limit}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.renderLogs(data.logs);
            this.hideLoading();
        } catch (error) {
            this.showError(`Failed to load logs: ${error.message}`);
        }
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
            this.containerEl.innerHTML = '<div class="log-entry"><p>No logs found.</p></div>';
            return;
        }
        
        const html = logs.map(log => this.renderLogEntry(log)).join('');
        this.containerEl.innerHTML = html;
    }
    
    renderLogEntry(log) {
        const logClass = this.getLogClass(log.log_message);
        const deviceStatus = this.renderDeviceStatus(log.device_status);
        const timestamp = new Date(log.received_at).toLocaleString();
        
        return `
            <div class="log-entry ${logClass}">
                <div class="log-header">
                    <div class="log-info">
                        <div class="log-field">
                            <label>Device ID</label>
                            <span>${log.device_id}</span>
                        </div>
                        <div class="log-field">
                            <label>Log ID</label>
                            <span>${log.log_id}</span>
                        </div>
                        <div class="log-field">
                            <label>Source</label>
                            <span>${log.log_sourcefile}:${log.log_codeline}</span>
                        </div>
                        <div class="log-field">
                            <label>Firmware Version</label>
                            <span>${log.device_status.current_fw_version || 'N/A'}</span>
                        </div>
                        <div class="log-field">
                            <label>Battery</label>
                            <span>${log.device_status.battery_voltage || 'N/A'}V</span>
                        </div>
                        <div class="log-field">
                            <label>WiFi RSSI</label>
                            <span>${log.device_status.wifi_rssi_level || 'N/A'} dBm</span>
                        </div>
                    </div>
                    <div class="timestamp">${timestamp}</div>
                </div>
                
                <div class="log-message">${log.log_message}</div>
                
                ${deviceStatus}
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
                <div class="status-item">
                    <span class="label">${key.replace(/_/g, ' ')}</span>
                    <span class="value">${value}</span>
                </div>
            `).join('');
        
        return `
            <div class="device-status">
                <h4>Device Status</h4>
                <div class="status-grid">
                    ${statusItems}
                </div>
            </div>
        `;
    }
}

// Initialize the log viewer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LogViewer();
});
