let isPolling = true;
let pollInterval = 2000;
let selectedBms = 1;
let previousData = null;

function updateBMSStatus(data) {
    for (let i = 1; i <= 16; i++) {
        const dot = document.getElementById(`bms-dot-${i}`);
        if (!dot) continue;

        // Ubah pengecekan communication sesuai dengan format data baru
        const isActive = data[`battery_bank.data.com_bms${i}`] === "1";
        
        dot.className = `w-12 h-8 md:rounded-lg flex items-center m-1 justify-center text-white text-sm cursor-pointer hover:opacity-80 transition-opacity duration-300 ${
            isActive ? "bg-green-500 dark:bg-green-600" : "bg-red-500 dark:bg-red-600"
        }`;
    }
}

function updateCellVoltages(data) {
    const cellVoltages = [];
    
    // First, collect all cell voltages
    for (let i = 1; i <= 14; i++) {
        const key = `battery_bank.cell${i}_volt_bms${selectedBms}`;
        const voltage = parseFloat(data[key] || 0) * 1000;
        cellVoltages.push(voltage);
    }
    
    // Calculate average voltage
    const avgVoltage = cellVoltages.reduce((a, b) => a + b, 0) / cellVoltages.length;
    
    // Define voltage ranges for coloring
    const deviationThreshold = avgVoltage * 0.05; // 5% deviation
    
    for (let i = 1; i <= 14; i++) {
        const voltage = cellVoltages[i - 1];

        // Update cell voltage display in BMS panel
        const cellDisplay = document.getElementById(`cell${i}`);
        if (cellDisplay) {
            cellDisplay.textContent = `${voltage.toFixed(0)} mV`;
        }

        // Update graph bars
        const bar = document.getElementById(`bar-${i}`);
        if (bar) {
            const heightPercentage = ((voltage - 2500) / (3500 - 2500)) * 100;
            bar.style.height = `${Math.max(0, Math.min(100, heightPercentage))}%`;
            bar.title = `${voltage.toFixed(0)} mV`;

            // Determine bar color based on deviation from average
            if (Math.abs(voltage - avgVoltage) > deviationThreshold) {
                // Far from average - red color
                bar.className = "rounded-t w-full transition-all duration-300 hover:opacity-80 bg-red-500 dark:bg-red-600";
            } else {
                // Close to average - blue color
                bar.className = "rounded-t w-full transition-all duration-300 hover:opacity-80 bg-blue-500 dark:bg-blue-600";
            }
        }
    }
    
    return cellVoltages;
}

function updateBatteryMetrics(data) {
    const metrics = {
        'voltage': [`battery_bank.data.volt_bms${selectedBms}`, 'V'],
        'current': [`battery_bank.data.curr_bms${selectedBms}`, 'A'],
        'soc': [`battery_bank.data.soc_bms${selectedBms}`, '%'],
        'soh': [`battery_bank.data.soh_bms${selectedBms}`, '%'],
        'temperature': [`battery_bank.data.amb_temp_bms${selectedBms}`, '°C']
    };

    for (const [id, [key, unit]] of Object.entries(metrics)) {
        const element = document.getElementById(id);
        if (element) {
            const value = data[key];
            const formattedValue = value ? `${parseFloat(value).toFixed(2)}${unit}` : 'N/A';
            if (element.textContent !== formattedValue) {
                element.textContent = formattedValue;
                element.classList.add('value-updated');
                setTimeout(() => element.classList.remove('value-updated'), 1000);
            }
        }
    }
}

function updateDisplayForBms(data) {
    const isActive = data[`battery_bank.data.com_bms${selectedBms}`] === "1";
    
    if (!isActive) {
        ["voltage", "current", "soc", "soh", "temperature", "cell-max", "cell-min", "difference"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = "N/A";
        });

        document.getElementById("battery-status").textContent = "Inactive";
        document.getElementById("battery-status").className = "text-lg text-red-500 dark:text-red-600";
        return;
    }

    updateBatteryMetrics(data);
    const cellVoltages = updateCellVoltages(data);

    // Update cell statistics
    const maxVoltage = Math.max(...cellVoltages);
    const minVoltage = Math.min(...cellVoltages);
    const difference = maxVoltage - minVoltage;

    document.getElementById('cell-max').textContent = `${maxVoltage.toFixed(0)} mV`;
    document.getElementById('cell-min').textContent = `${minVoltage.toFixed(0)} mV`;
    document.getElementById('difference').textContent = `${difference.toFixed(0)} mV`;

    // Update battery status
    const statusElement = document.getElementById("battery-status");
    if (statusElement) {
        let status;
        let className;
        if (difference <= 100) {
            status = "Excellent";
            className = "text-lg text-green-500 dark:text-green-600";
        } else if (difference <= 200) {
            status = "Good";
            className = "text-lg text-blue-500 dark:text-blue-600";
        } else if (difference <= 300) {
            status = "Fair";
            className = "text-lg text-yellow-500 dark:text-yellow-600";
        } else {
            status = "Poor";
            className = "text-lg text-red-500 dark:text-red-600";
        }
        statusElement.textContent = status;
        statusElement.className = className;
    }
}

function initializeBMSStatus() {
    const bmsStatus = document.getElementById("bms-status");
    if (!bmsStatus) return;
    
    bmsStatus.innerHTML = "";

    for (let i = 1; i <= 16; i++) {
        const dot = document.createElement("div");
        dot.id = `bms-dot-${i}`;
        dot.className = "w-12 h-8 md:rounded-lg flex items-center m-1 justify-center text-white text-sm bg-gray-400 dark:bg-gray-600 cursor-pointer hover:opacity-80 transition-opacity duration-300";
        dot.textContent = i;

        dot.addEventListener("click", () => {
            selectedBms = i;
            if (previousData) {
                updateDisplayForBms(previousData);
            }
            document.getElementById("bms-title").innerHTML = `<i class="fa-solid fa-battery-full mr-2"></i>BMS ${i}`;
        });

        bmsStatus.appendChild(dot);
    }
}

function initializeCellGraph() {
    const cellGraph = document.getElementById("cell-graph");
    if (!cellGraph) return;
    
    cellGraph.innerHTML = "";

    for (let i = 0; i < 14; i++) {
        const barContainer = document.createElement("div");
        barContainer.className = "flex flex-col justify-end w-full mx-0.5 relative z-10";

        const bar = document.createElement("div");
        bar.className = "bg-gray-300 dark:bg-gray-600 rounded-t w-full transition-all duration-300 hover:opacity-80";
        bar.style.height = "0%";
        bar.id = `bar-${i + 1}`;

        const label = document.createElement("div");
        label.className = "text-xs text-center mt-2 absolute -bottom-6 w-full dark:text-gray-300";
        label.textContent = `${i + 1}`;

        barContainer.appendChild(bar);
        barContainer.appendChild(label);
        cellGraph.appendChild(barContainer);
    }
}

async function pollBatteryData() {
    if (!isPolling) return;

    try {
        const response = await fetch('/api/monitoring/battery');
        const result = await response.json();

        console.log('Battery data:', result); // Debug log

        if (result.status === 'success' && result.data) {
            updateBMSStatus(result.data);
            updateDisplayForBms(result.data);
            previousData = result.data;
        }
    } catch (error) {
        console.error('Error fetching battery data:', error);
    } finally {
        if (isPolling) {
            setTimeout(pollBatteryData, pollInterval);
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing battery monitoring...'); // Debug log
    initializeBMSStatus();
    initializeCellGraph();
    pollBatteryData();

    // Handle sync button
    document.addEventListener('togglePolling', () => {
        isPolling = !isPolling;
        if (isPolling) {
            pollBatteryData();
        }
    });
});