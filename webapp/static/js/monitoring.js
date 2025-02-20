// static/js/monitoring.js
let isPolling = true;
let pollInterval = 2000;
let previousData = {};

function formatKey(key) {
    return key.split('.').pop()
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .toLowerCase()
        .replace(/\b\w/g, l => l.toUpperCase());
}

function updateData(containerId, data, previousData = {}) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    Object.entries(data).forEach(([key, value]) => {
        const formattedKey = formatKey(key);
        const div = document.createElement('div');
        div.className = 'value-box';
        
        // Check if value has changed
        const hasChanged = previousData[key] !== value;
        if (hasChanged) {
            div.classList.add('updated');
            setTimeout(() => div.classList.remove('updated'), 1000);
        }
        
        // Add appropriate units
        let displayValue = value;
        if (key.includes('volt')) displayValue += ' V';
        else if (key.includes('curr')) displayValue += ' A';
        else if (key.includes('power')) displayValue += ' W';
        else if (key.includes('temp')) displayValue += ' °C';
        else if (key.includes('hum')) displayValue += ' %';
        
        div.innerHTML = `<strong>${formattedKey}:</strong> ${displayValue}`;
        container.appendChild(div);
    });
}

function togglePolling() {
    isPolling = !isPolling;
    document.getElementById('polling-status').textContent = isPolling ? 'Stop' : 'Start';
    if (isPolling) {
        pollData();
    }
}

async function pollData() {
    if (!isPolling) return;

    try {
        document.getElementById('refresh-status').classList.add('active');

        const response = await fetch('/api/monitoring/latest');
        const data = await response.json();

        document.getElementById('timestamp').textContent = data.timestamp;
        document.getElementById('host').textContent = data.host;

        updateData('battery-data', data.battery, previousData.battery || {});
        updateData('solar-data', data.solar, previousData.solar || {});
        updateData('environment-data', data.environment, previousData.environment || {});

        previousData = data;

    } catch (error) {
        console.error('Error fetching data:', error);
    } finally {
        document.getElementById('refresh-status').classList.remove('active');
        if (isPolling) {
            setTimeout(pollData, pollInterval);
        }
    }
}

// Start polling when page loads
document.addEventListener('DOMContentLoaded', pollData);