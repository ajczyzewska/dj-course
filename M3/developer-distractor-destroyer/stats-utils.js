// Utility functions for statistics aggregation and filtering

function aggregateByDay(timeDataWithTimestamps) {
    const grouped = {};

    timeDataWithTimestamps.forEach(entry => {
        const key = `${entry.date}|${entry.domain}`;
        if (!grouped[key]) {
            grouped[key] = {
                date: entry.date,
                domain: entry.domain,
                seconds: 0
            };
        }
        grouped[key].seconds += entry.seconds;
    });

    return Object.values(grouped);
}

function aggregateByWeek(timeDataWithTimestamps) {
    const grouped = {};

    timeDataWithTimestamps.forEach(entry => {
        const weekKey = `${entry.year}-W${String(entry.week).padStart(2, '0')}`;
        const key = `${weekKey}|${entry.domain}`;
        if (!grouped[key]) {
            grouped[key] = {
                week: weekKey,
                domain: entry.domain,
                seconds: 0
            };
        }
        grouped[key].seconds += entry.seconds;
    });

    return Object.values(grouped);
}

function aggregateByMonth(timeDataWithTimestamps) {
    const grouped = {};

    timeDataWithTimestamps.forEach(entry => {
        const monthKey = `${entry.year}-${String(entry.month).padStart(2, '0')}`;
        const key = `${monthKey}|${entry.domain}`;
        if (!grouped[key]) {
            grouped[key] = {
                month: monthKey,
                domain: entry.domain,
                seconds: 0
            };
        }
        grouped[key].seconds += entry.seconds;
    });

    return Object.values(grouped);
}

function filterByPeriod(timeDataWithTimestamps, startDate, endDate) {
    const start = new Date(startDate).getTime();
    const end = new Date(endDate).getTime();

    return timeDataWithTimestamps.filter(entry => {
        return entry.timestamp >= start && entry.timestamp <= end;
    });
}

function filterByDateRange(timeDataWithTimestamps, startDate, endDate) {
    return timeDataWithTimestamps.filter(entry => {
        return entry.date >= startDate && entry.date <= endDate;
    });
}

function getTotalsByDomain(aggregatedData, periodKey = 'date') {
    const totals = {};

    aggregatedData.forEach(entry => {
        if (!totals[entry.domain]) {
            totals[entry.domain] = 0;
        }
        totals[entry.domain] += entry.seconds;
    });

    return totals;
}

function getTimeSeriesData(aggregatedData, periodKey = 'date') {
    const series = {};

    aggregatedData.forEach(entry => {
        const period = entry[periodKey];
        if (!series[period]) {
            series[period] = {};
        }
        series[period][entry.domain] = entry.seconds;
    });

    return series;
}

function exportToJSON(data) {
    const exportData = {
        version: '1.0',
        exportDate: new Date().toISOString(),
        data: data
    };

    return JSON.stringify(exportData, null, 2);
}

function validateImportJSON(jsonString) {
    try {
        const data = JSON.parse(jsonString);

        if (!data.version) {
            return { valid: false, error: 'Missing version field' };
        }

        if (!data.data) {
            return { valid: false, error: 'Missing data field' };
        }

        return { valid: true, data: data.data };
    } catch (error) {
        return { valid: false, error: 'Invalid JSON format: ' + error.message };
    }
}

function mergeTimeData(existingData, newData) {
    if (!Array.isArray(existingData)) {
        existingData = [];
    }
    if (!Array.isArray(newData)) {
        newData = [];
    }

    const merged = [...existingData, ...newData];

    // Sort by timestamp
    merged.sort((a, b) => a.timestamp - b.timestamp);

    return merged;
}

function getDateRange(timeDataWithTimestamps) {
    if (!timeDataWithTimestamps || timeDataWithTimestamps.length === 0) {
        return { minDate: null, maxDate: null };
    }

    const dates = timeDataWithTimestamps.map(entry => entry.date);
    const minDate = dates.reduce((min, date) => date < min ? date : min);
    const maxDate = dates.reduce((max, date) => date > max ? date : max);

    return { minDate, maxDate };
}

function getAvailablePeriods(timeDataWithTimestamps) {
    const periods = {
        days: new Set(),
        weeks: new Set(),
        months: new Set()
    };

    timeDataWithTimestamps.forEach(entry => {
        periods.days.add(entry.date);
        periods.weeks.add(`${entry.year}-W${String(entry.week).padStart(2, '0')}`);
        periods.months.add(`${entry.year}-${String(entry.month).padStart(2, '0')}`);
    });

    return {
        days: Array.from(periods.days).sort(),
        weeks: Array.from(periods.weeks).sort(),
        months: Array.from(periods.months).sort()
    };
}
