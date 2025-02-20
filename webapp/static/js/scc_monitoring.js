function updateSCCData() {
    fetch('/api/monitoring/scc')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update system totals
                document.getElementById('total-pv-power').textContent = data.summary.total_pv_power.toFixed(2) + ' W';
                document.getElementById('total-scc-power').textContent = data.summary.total_scc_power.toFixed(2) + ' W';
                document.getElementById('system-efficiency').textContent = data.summary.system_efficiency.toFixed(2) + ' %';

                // Update individual SCC data
                data.active_scc.forEach(sccNum => {
                    // Update status indicator
                    const statusEl = document.getElementById(`scc${sccNum}-status`);
                    if (statusEl) {
                        statusEl.style.backgroundColor = '#28a745'; // green for active
                    }

                    // Update PV metrics
                    updateMetric(`pv${sccNum}-voltage`, 'volt_pv', sccNum, data.data);
                    updateMetric(`pv${sccNum}-current`, 'curr_pv', sccNum, data.data);
                    updateMetric(`pv${sccNum}-power`, 'power_pv', sccNum, data.data);

                    // Update SCC metrics
                    updateMetric(`scc${sccNum}-voltage`, 'volt_scc', sccNum, data.data);
                    updateMetric(`scc${sccNum}-current`, 'curr_scc', sccNum, data.data);
                    updateMetric(`scc${sccNum}-power`, 'power_scc', sccNum, data.data);
                    updateMetric(`scc${sccNum}-temp`, 'temp_scc', sccNum, data.data);
                });
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateMetric(elementId, metric, sccNum, data) {
    const element = document.getElementById(elementId);
    if (element) {
        const key = `pv_module.data.${metric}${sccNum}`;
        const value = data[key] || '0.00';
        element.textContent = parseFloat(value).toFixed(2);
        
        // Add units
        if (metric.includes('volt')) {
            element.textContent += ' V';
        } else if (metric.includes('curr')) {
            element.textContent += ' A';
        } else if (metric.includes('power')) {
            element.textContent += ' W';
        } else if (metric.includes('temp')) {
            element.textContent += ' °C';
        }
    }
}

// Update data every 5 seconds
setInterval(updateSCCData, 5000);

// Initial update
document.addEventListener('DOMContentLoaded', updateSCCData);