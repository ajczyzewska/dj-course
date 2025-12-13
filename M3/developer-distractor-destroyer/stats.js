document.addEventListener('DOMContentLoaded', () => {
    displayStats();
    setupFilters();
});

let currentFilter = {
    periodType: 'all',
    startDate: null,
    endDate: null
};

function setupFilters() {
    const periodTypeSelect = document.getElementById('periodType');
    const dateRangeGroup = document.getElementById('dateRangeGroup');
    const dateRangeGroupEnd = document.getElementById('dateRangeGroupEnd');
    const applyFilterBtn = document.getElementById('applyFilter');
    const exportDataBtn = document.getElementById('exportData');
    const importDataBtn = document.getElementById('importData');
    const fileInput = document.getElementById('fileInput');

    periodTypeSelect.addEventListener('change', (e) => {
        const showDateRange = e.target.value === 'custom';
        dateRangeGroup.style.display = showDateRange ? 'flex' : 'none';
        dateRangeGroupEnd.style.display = showDateRange ? 'flex' : 'none';
    });

    applyFilterBtn.addEventListener('click', () => {
        currentFilter.periodType = periodTypeSelect.value;
        currentFilter.startDate = document.getElementById('startDate').value;
        currentFilter.endDate = document.getElementById('endDate').value;
        updateStatsWithFilter();
    });

    exportDataBtn.addEventListener('click', exportStats);
    importDataBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', importStats);
}

function exportStats() {
    chrome.storage.local.get(['timeDataWithTimestamps', 'timeData', 'gotchaStats'], (result) => {
        const exportData = {
            timeDataWithTimestamps: result.timeDataWithTimestamps || [],
            timeData: result.timeData || {},
            gotchaStats: result.gotchaStats || {}
        };

        const jsonString = exportToJSON(exportData);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `developer-distractor-stats-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}

function importStats(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        const validation = validateImportJSON(e.target.result);

        if (!validation.valid) {
            alert('Błąd importu: ' + validation.error);
            return;
        }

        const importedData = validation.data;

        chrome.storage.local.get(['timeDataWithTimestamps', 'timeData', 'gotchaStats'], (result) => {
            const mergedTimestamps = mergeTimeData(
                result.timeDataWithTimestamps || [],
                importedData.timeDataWithTimestamps || []
            );

            const mergedTimeData = {
                ...(result.timeData || {}),
                ...(importedData.timeData || {})
            };

            const mergedGotchaStats = {
                ...(result.gotchaStats || {}),
                ...(importedData.gotchaStats || {})
            };

            chrome.storage.local.set({
                timeDataWithTimestamps: mergedTimestamps,
                timeData: mergedTimeData,
                gotchaStats: mergedGotchaStats
            }, () => {
                alert('Statystyki zaimportowane pomyślnie!');
                updateStatsWithFilter();
            });
        });
    };

    reader.readAsText(file);
    event.target.value = '';
}

function displayStats() {
    document.title = 'Time Statistics - Developer Distractor Destroyer';

    const timeStatsList = document.getElementById('statsList');
    const timeChartCanvas = document.getElementById('timeChart').getContext('2d');
    const clearTimeStatsBtn = document.getElementById('clearTimeStats');
    let timeChart = null;

    const gotchaStatsList = document.getElementById('gotchaList');
    const gotchaChartCanvas = document.getElementById('gotchaChart').getContext('2d');
    const clearGotchaStatsBtn = document.getElementById('clearGotchaStats');
    let gotchaChart = null;

    let intervalId = null;

    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    function updateStatsWithFilter() {
        chrome.storage.local.get(['timeDataWithTimestamps', 'timeData', 'gotchaStats'], (result) => {
            let filteredData = result.timeDataWithTimestamps || [];

            if (currentFilter.periodType === 'custom' && currentFilter.startDate && currentFilter.endDate) {
                filteredData = filterByDateRange(filteredData, currentFilter.startDate, currentFilter.endDate);
            } else if (currentFilter.periodType === 'day') {
                const today = new Date().toISOString().split('T')[0];
                filteredData = filteredData.filter(entry => entry.date === today);
            } else if (currentFilter.periodType === 'week') {
                const now = new Date();
                const currentWeek = getWeekNumber(now);
                const currentYear = now.getFullYear();
                filteredData = filteredData.filter(entry => entry.week === currentWeek && entry.year === currentYear);
            } else if (currentFilter.periodType === 'month') {
                const now = new Date();
                const currentMonth = now.getMonth() + 1;
                const currentYear = now.getFullYear();
                filteredData = filteredData.filter(entry => entry.month === currentMonth && entry.year === currentYear);
            }

            const timeData = getTotalsByDomain(filteredData);
            updateStats(timeData, result.gotchaStats || {});
        });
    }

    function getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }

    function updateStats(timeData = null, gotchaData = null) {
        if (timeData === null || gotchaData === null) {
            chrome.storage.local.get(['timeData', 'gotchaStats'], (result) => {
                updateStats(result.timeData || {}, result.gotchaStats || {});
            });
            return;
        }

        // Time Stats
        timeStatsList.innerHTML = '';
        const sortedTimeSites = Object.entries(timeData).sort((a, b) => b[1] - a[1]);
    
            if (sortedTimeSites.length === 0) {
                timeStatsList.innerHTML = '<div class="stat-item">No time tracking data yet.</div>';
                document.getElementById('timeChart').style.display = 'none';
            } else {
                document.getElementById('timeChart').style.display = 'block';
                sortedTimeSites.forEach(([site, time]) => {
                    const statItem = createStatItem(site, formatTime(time), timeChart, timeStatsList);
                    timeStatsList.appendChild(statItem);
                });
                renderPieChart(sortedTimeSites);
            }

        // Gotcha Stats
        gotchaStatsList.innerHTML = '';
        const sortedGotchaSites = Object.entries(gotchaData).sort((a, b) => b[1] - a[1]);

            if (sortedGotchaSites.length === 0) {
                gotchaStatsList.innerHTML = '<div class="stat-item">No "gotcha" data yet.</div>';
                document.getElementById('gotchaChart').style.display = 'none';
            } else {
                document.getElementById('gotchaChart').style.display = 'block';
                sortedGotchaSites.forEach(([site, count]) => {
                    const statItem = createStatItem(site, `${count} times`, gotchaChart, gotchaStatsList);
                    gotchaStatsList.appendChild(statItem);
                });
                renderGotchaChart(sortedGotchaSites);
            }
    }

    function removeStatEntry(statType, siteToRemove) {
        chrome.storage.local.get([statType], (result) => {
            const stats = result[statType];
            if (stats && stats[siteToRemove]) {
                delete stats[siteToRemove];
                let dataToSet = {};
                dataToSet[statType] = stats;
                chrome.storage.local.set(dataToSet, () => {
                    updateStats();
                });
            }
        });
    }

    function createStatItem(site, value, chart, listElement) {
        const statItem = document.createElement('div');
        statItem.className = 'stat-item';
        statItem.dataset.site = site;

        if (chart) {
            const index = chart.data.labels.indexOf(site);
            if (index !== -1 && !chart.getDataVisibility(index)) {
                statItem.classList.add('disabled');
            }
        }

        const siteText = document.createElement('span');
        siteText.textContent = site;

        const valueContainer = document.createElement('div');
        valueContainer.className = 'value-container';

        const valueText = document.createElement('span');
        valueText.textContent = value;

        const deleteBtn = document.createElement('span');
        deleteBtn.className = 'delete-stat-btn';
        deleteBtn.textContent = '❌';

        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const statType = listElement.id === 'statsList' ? 'timeData' : 'gotchaStats';
            if (confirm(`Are you sure you want to delete stats for "${site}"?`)) {
                removeStatEntry(statType, site);
            }
        });

        valueContainer.appendChild(valueText);
        valueContainer.appendChild(deleteBtn);

        statItem.appendChild(siteText);
        statItem.appendChild(valueContainer);

        statItem.addEventListener('click', () => {
            if (!chart) return;
            const index = chart.data.labels.indexOf(site);
            if (index !== -1) {
                chart.toggleDataVisibility(index);
                chart.update();
                statItem.classList.toggle('disabled', !chart.getDataVisibility(index));
            }
        });

        statItem.addEventListener('mouseover', () => {
            if (!chart) return;
            const index = chart.data.labels.indexOf(site);
            if (index !== -1) {
                chart.setActiveElements([{ datasetIndex: 0, index: index }]);
                chart.update();
            }
        });

        statItem.addEventListener('mouseout', () => {
            if (!chart) return;
            chart.setActiveElements([]);
            chart.update();
        });

        return statItem;
    }

    function renderPieChart(data) {
        const labels = data.map(item => item[0]);
        const values = data.map(item => item[1]);

        if (timeChart) {
            timeChart.data.labels = labels;
            timeChart.data.datasets[0].data = values;
            timeChart.update();
            return;
        }

        timeChart = new Chart(timeChartCanvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Time Spent (seconds)',
                    data: values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: 'white'
                        },
                        onClick: (e, legendItem, legend) => {
                            const index = legendItem.index;
                            const ci = legend.chart;
                            
                            ci.toggleDataVisibility(index);
                            ci.update();

                            const isVisible = ci.getDataVisibility(index);
                            const statItem = timeStatsList.querySelector(`.stat-item[data-site="${legendItem.text}"]`);
                            if (statItem) {
                                statItem.classList.toggle('disabled', !isVisible);
                            }
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += formatTime(context.parsed);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderGotchaChart(data) {
        const labels = data.map(item => item[0]);
        const values = data.map(item => item[1]);

        if (gotchaChart) {
            gotchaChart.data.labels = labels;
            gotchaChart.data.datasets[0].data = values;
            gotchaChart.update();
            return;
        }

        gotchaChart = new Chart(gotchaChartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '"Gotcha" Count',
                    data: values,
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'white'
                        }
                    },
                    y: {
                        ticks: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }

    clearTimeStatsBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all time statistics? This cannot be undone.')) {
            chrome.storage.local.set({ timeData: {}, currentSessionTime: 0 }, () => {
                if (timeChart) {
                    timeChart.destroy();
                    timeChart = null;
                }
                updateStats();
            });
        }
    });

    clearGotchaStatsBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all "gotcha" statistics? This cannot be undone.')) {
            chrome.storage.local.set({ gotchaStats: {} }, () => {
                if (gotchaChart) {
                    gotchaChart.destroy();
                    gotchaChart = null;
                }
                updateStats();
            });
        }
    });

    // Initial update
    updateStats();

    // Set up auto-refresh
    intervalId = setInterval(updateStats, 5000);

    // Clean up the interval when the page is hidden
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            clearInterval(intervalId);
        } else {
            intervalId = setInterval(updateStats, 5000);
        }
    });
} 