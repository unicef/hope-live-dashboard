document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    const statusMap = {
        "1": gettext("New"),
        "2": gettext("Assigned"),
        "3": gettext("In Progress"),
        "4": gettext("On Hold"),
        "5": gettext("For Approval"),
        "6": gettext("Closed")
    };

    const categoryMap = {
        "1": gettext("Payment Verification"),
        "2": gettext("Data Change"),
        "3": gettext("Sensitive Grievance"),
        "4": gettext("Grievance Complaint"),
        "5": gettext("Negative Feedback"),
        "6": gettext("Referral"),
        "7": gettext("Positive Feedback"),
        "8": gettext("Needs Adjudication"),
        "9": gettext("System Flagging"),
        "10": gettext("Beneficiary")
    };

    const priorityMap = {
        "0": gettext("Not Set"),
        "1": gettext("High"),
        "2": gettext("Medium"),
        "3": gettext("Low")
    };

    const issueTypeMap = {
        "1": gettext("Data breach"),
        "2": gettext("Bribery, corruption or kickback"),
        "3": gettext("Fraud and forgery"),
        "4": gettext("Fraud involving misuse of programme funds by third party"),
        "5": gettext("Harassment and abuse of authority"),
        "6": gettext("Inappropriate staff conduct"),
        "7": gettext("Unauthorized use, misuse or waste of UNICEF property or funds"),
        "8": gettext("Conflict of interest"),
        "9": gettext("Gross mismanagement"),
        "10": gettext("Personal disputes"),
        "11": gettext("Sexual harassment and sexual exploitation"),
        "12": gettext("Miscellaneous"),
        "13": gettext("Household Data Update"),
        "14": gettext("Individual Data Update"),
        "15": gettext("Withdraw Individual"),
        "16": gettext("Add Individual"),
        "17": gettext("Withdraw Household"),
        "18": gettext("Payment Related Complaint"),
        "19": gettext("FSP Related Complaint"),
        "20": gettext("Registration Related Complaint"),
        "21": gettext("Other Complaint"),
        "22": gettext("Partner Related Complaint"),
        "23": gettext("Unique Identifiers Similarity"),
        "24": gettext("Biographical Data Similarity"),
        "25": gettext("Biometrics Similarity"),
        "26": gettext("Update Delegate")
    };

    const colorPalette = [
        '#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80',
        '#8d98b3', '#e5cf0d', '#97b552', '#95706d', '#dc69aa',
        '#07a2a4', '#9a7fd1', '#588dd5', '#f5994e', '#c05050',
        '#59678c', '#c9ab00', '#76933c', '#bc65a6'
    ];

    function getStableColor(name) {
        if (!name) return '#5470c6';
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        const index = Math.abs(hash) % colorPalette.length;
        return colorPalette[index];
    }

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : '');
    const categoryDimension = ndx.dimension(d => d.dimension_type === 'category' ? d.dimension_value : '');
    const issueTypeDimension = ndx.dimension(d => d.dimension_type === 'issue_type' ? d.dimension_value : '');
    const priorityDimension = ndx.dimension(d => d.dimension_type === 'priority' ? d.dimension_value : '');
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'category';

    // Groups
    const moveDays = dateDimension.group(d3.timeDay);

    // Custom reduction to split Open vs Resolved tickets over time
    const ticketsByDayGroup = moveDays.reduce(
        (p, v) => {
            if (v.dimension_type === 'status') {
                const status = String(v.dimension_value).toUpperCase();
                if (status.includes('RESOLVED') || status.includes('CLOSED')) {
                    p.resolved += v.ticket_count;
                } else {
                    p.open += v.ticket_count;
                }
            }
            return p;
        },
        (p, v) => {
            if (v.dimension_type === 'status') {
                const status = String(v.dimension_value).toUpperCase();
                if (status.includes('RESOLVED') || status.includes('CLOSED')) {
                    p.resolved -= v.ticket_count;
                } else {
                    p.open -= v.ticket_count;
                }
            }
            return p;
        },
        () => ({ open: 0, resolved: 0 })
    );

    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.ticket_count : 0);
    const categoryGroup = categoryDimension.group().reduceSum(d => d.dimension_type === 'category' ? d.ticket_count : 0);
    const issueTypeGroup = issueTypeDimension.group().reduceSum(d => d.dimension_type === 'issue_type' ? d.ticket_count : 0);
    const priorityGroup = priorityDimension.group().reduceSum(d => d.dimension_type === 'priority' ? d.ticket_count : 0);

    // Custom reduction to split Open vs Resolved tickets by country
    const countryGroup = countryDimension.group().reduce(
        (p, v) => {
            if (v.dimension_type === 'status') {
                const status = String(v.dimension_value).toUpperCase();
                if (status.includes('RESOLVED') || status.includes('CLOSED')) {
                    p.resolved += v.ticket_count;
                } else {
                    p.open += v.ticket_count;
                }
            }
            return p;
        },
        (p, v) => {
            if (v.dimension_type === 'status') {
                const status = String(v.dimension_value).toUpperCase();
                if (status.includes('RESOLVED') || status.includes('CLOSED')) {
                    p.resolved -= v.ticket_count;
                } else {
                    p.open -= v.ticket_count;
                }
            }
            return p;
        },
        () => ({ open: 0, resolved: 0 })
    );

    // Active filters
    const selectedStatuses = new Set();
    const selectedCategories = new Set();
    const selectedIssueTypes = new Set();
    const selectedPriorities = new Set();
    const selectedCountries = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const statusChart = echarts.init(document.getElementById('grievance-status-chart'), 'macarons');
    const priorityChart = echarts.init(document.getElementById('grievance-priority-chart'), 'macarons');
    const categoryChart = echarts.init(document.getElementById('grievance-category-chart'), 'macarons');
    const issueTypeChart = echarts.init(document.getElementById('grievance-issue-type-chart'), 'macarons');
    const countryChart = echarts.init(document.getElementById('grievance-country-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        statusChart.resize();
        priorityChart.resize();
        categoryChart.resize();
        issueTypeChart.resize();
        countryChart.resize();
    });

    function updateTotals() {
        const totalTickets = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0).value();
        const totalTicketsElement = document.getElementById('total-tickets');
        if (totalTicketsElement) {
            totalTicketsElement.textContent = d3.format(',')(totalTickets);
        }
    }

    function updateAll(filterSource = null) {
        updateTotals();

        // 1. Timeline Chart (Stacked Area Chart of Open vs Resolved Tickets)
        const timelineDataOpen = ticketsByDayGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value.open]);

        const timelineDataResolved = ticketsByDayGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value.resolved]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %d, %Y")(date);
                    let tooltipHtml = `${formattedDate}<br/>`;
                    params.forEach(p => {
                        tooltipHtml += `${p.marker} ${p.seriesName}: <b>${d3.format(",")(p.value[1])}</b> ${gettext('tickets')}<br/>`;
                    });
                    return tooltipHtml;
                }
            },
            legend: {
                data: [gettext('Closed'), gettext('Open & Active')],
                bottom: 0,
                icon: 'roundRect'
            },
            grid: { top: 20, bottom: 80, left: 70, right: 30 },
            xAxis: {
                type: 'time',
                axisLabel: { color: '#64748b' }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
            },
            series: [
                {
                    name: gettext('Closed'),
                    type: 'line',
                    stack: 'total',
                    smooth: true,
                    symbol: 'none',
                    lineStyle: { color: '#97b552', width: 2 },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(151, 181, 82, 0.4)' },
                            { offset: 1, color: 'rgba(151, 181, 82, 0.02)' }
                        ])
                    },
                    data: timelineDataResolved
                },
                {
                    name: gettext('Open & Active'),
                    type: 'line',
                    stack: 'total',
                    smooth: true,
                    symbol: 'none',
                    lineStyle: { color: '#d87a80', width: 2 },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(216, 122, 128, 0.4)' },
                            { offset: 1, color: 'rgba(216, 122, 128, 0.02)' }
                        ])
                    },
                    data: timelineDataOpen
                }
            ]
        };

        if (filterSource !== 'timeline') {
            timelineOption.dataZoom = [
                { type: 'inside', start: 0, end: 100 },
                { show: true, type: 'slider', start: 0, end: 100, bottom: 25, textStyle: { color: '#64748b' } }
            ];
            timelineChart.setOption(timelineOption, { notMerge: true });
        } else {
            timelineChart.setOption(timelineOption);
        }

        // 2. Status Chart (Donut Pie)
        const statusData = statusGroup.all().filter(d => d.key !== '' && d.key !== null && d.value > 0);
        statusChart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: <b>{c}</b> ({d}%)' },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, position: 'outside', formatter: '{b}: {c}', fontSize: 11, color: '#374151' },
                labelLine: { show: true, length: 15, length2: 10, smooth: false },
                emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
                data: statusData.map(d => ({ name: d.key, value: d.value }))
            }]
        }, { notMerge: true });

        // 3. Priority Chart (Donut Pie)
        const priorityData = priorityGroup.all().filter(d => d.key !== '' && d.key !== null && d.value > 0);
        priorityChart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: <b>{c}</b> ({d}%)' },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, position: 'outside', formatter: '{b}: {c}', fontSize: 11, color: '#374151' },
                labelLine: { show: true, length: 15, length2: 10, smooth: false },
                emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
                data: priorityData.map(d => ({ name: d.key, value: d.value }))
            }]
        }, { notMerge: true });

        // 4. Category Chart (Horizontal Bar / Row)
        const categoryData = categoryGroup.all().filter(d => d.key !== '' && d.key !== null && d.value > 0);
        categoryData.sort((a, b) => b.value - a.value);

        const hasAnyCategorySelection = selectedCategories.size > 0;
        const categorySeriesData = categoryData.map(d => {
            const stableColor = getStableColor(d.key);
            return {
                name: d.key,
                value: d.value,
                itemStyle: {
                    color: selectedCategories.has(d.key)
                        ? stableColor
                        : (hasAnyCategorySelection ? '#cbd5e1' : stableColor)
                }
            };
        });

        categoryChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>` },
            grid: { top: 20, bottom: 30, left: 140, right: 30 },
            xAxis: {
                type: 'value',
                axisLabel: { formatter: val => d3.format(".2s")(val).replace('G', 'B'), color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: categoryData.map(d => d.key),
                inverse: true,
                axisLabel: { color: '#1f2937', fontWeight: 500 }
            },
            series: [{
                type: 'bar',
                data: categorySeriesData,
                barMaxWidth: 22,
                itemStyle: { borderRadius: [0, 4, 4, 0] }
            }]
        }, { notMerge: true });

        // 5. Issue Type Chart (Horizontal Bar / Row)
        const issueTypeData = issueTypeGroup.all().filter(d => d.key !== '' && d.key !== null && d.value > 0);
        issueTypeData.sort((a, b) => b.value - a.value);

        const hasAnyIssueTypeSelection = selectedIssueTypes.size > 0;
        const issueTypeSeriesData = issueTypeData.map(d => {
            const stableColor = getStableColor(d.key);
            return {
                name: d.key,
                value: d.value,
                itemStyle: {
                    color: selectedIssueTypes.has(d.key)
                        ? stableColor
                        : (hasAnyIssueTypeSelection ? '#cbd5e1' : stableColor)
                }
            };
        });

        issueTypeChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>` },
            grid: { top: 20, bottom: 30, left: 140, right: 30 },
            xAxis: {
                type: 'value',
                axisLabel: { formatter: val => d3.format(".2s")(val).replace('G', 'B'), color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: issueTypeData.map(d => d.key),
                inverse: true,
                axisLabel: { color: '#1f2937', fontWeight: 500 }
            },
            series: [{
                type: 'bar',
                data: issueTypeSeriesData,
                barMaxWidth: 22,
                itemStyle: { borderRadius: [0, 4, 4, 0] }
            }]
        }, { notMerge: true });

        // 6. Country Chart (Stacked status bar)
        const countryData = countryGroup.all()
            .map(d => ({
                key: d.key,
                open: d.value.open,
                resolved: d.value.resolved,
                total: d.value.open + d.value.resolved
            }))
            .filter(d => d.key !== null && d.total > 0)
            .sort((a, b) => b.total - a.total)
            .slice(0, 15);

        const hasAnyCountrySelection = selectedCountries.size > 0;

        const countrySeriesDataResolved = countryData.map(d => {
            const isSelected = selectedCountries.has(d.key);
            const opacity = isSelected ? 1 : (hasAnyCountrySelection ? 0.35 : 1);
            return {
                value: d.resolved,
                itemStyle: { color: '#97b552', opacity: opacity }
            };
        });

        const countrySeriesDataOpen = countryData.map(d => {
            const isSelected = selectedCountries.has(d.key);
            const opacity = isSelected ? 1 : (hasAnyCountrySelection ? 0.35 : 1);
            return {
                value: d.open,
                itemStyle: { color: '#d87a80', opacity: opacity }
            };
        });

        countryChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: function (params) {
                    let tooltipHtml = `${params[0].name}<br/>`;
                    params.forEach(p => {
                        tooltipHtml += `${p.marker} ${p.seriesName}: <b>${d3.format(",")(p.value)}</b> ${gettext('tickets')}<br/>`;
                    });
                    return tooltipHtml;
                }
            },
            legend: {
                data: [gettext('Closed'), gettext('Open & Active')],
                top: 0,
                right: 20
            },
            grid: { top: 35, bottom: 95, left: 75, right: 20 },
            xAxis: {
                type: 'category',
                data: countryData.map(d => d.key),
                axisLabel: { rotate: 30, interval: 0, color: '#1f2937', fontWeight: 500 }
            },
            yAxis: {
                type: 'value',
                axisLabel: { formatter: val => d3.format(".2s")(val).replace('G', 'B'), color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            series: [
                {
                    name: gettext('Closed'),
                    type: 'bar',
                    stack: 'status',
                    barMaxWidth: 30,
                    data: countrySeriesDataResolved,
                    itemStyle: { borderRadius: [0, 0, 0, 0] }
                },
                {
                    name: gettext('Open & Active'),
                    type: 'bar',
                    stack: 'status',
                    barMaxWidth: 30,
                    data: countrySeriesDataOpen,
                    itemStyle: { borderRadius: [4, 4, 0, 0] }
                }
            ]
        }, { notMerge: true });
    }

    // --- Interactive Filters Bindings ---
    timelineChart.on('datazoom', function (params) {
        const option = timelineChart.getOption();
        const startVal = option.dataZoom[0].startValue;
        const endVal = option.dataZoom[0].endValue;

        if (startVal !== undefined && endVal !== undefined) {
            const startDate = new Date(startVal);
            const endDate = new Date(endVal);
            dateDimension.filterRange([startDate, endDate]);
            updateAll('timeline');
        }
    });

    statusChart.on('click', function (params) {
        const name = params.name;
        if (selectedStatuses.has(name)) {
            selectedStatuses.delete(name);
        } else {
            selectedStatuses.add(name);
        }
        if (selectedStatuses.size === 0) statusDimension.filterAll();
        else statusDimension.filterFunction(d => d === '' || selectedStatuses.has(d));
        updateAll();
    });

    priorityChart.on('click', function (params) {
        const name = params.name;
        if (selectedPriorities.has(name)) {
            selectedPriorities.delete(name);
        } else {
            selectedPriorities.add(name);
        }
        if (selectedPriorities.size === 0) priorityDimension.filterAll();
        else priorityDimension.filterFunction(d => d === '' || selectedPriorities.has(d));
        updateAll();
    });

    categoryChart.on('click', function (params) {
        const name = params.name;
        if (selectedCategories.has(name)) {
            selectedCategories.delete(name);
        } else {
            selectedCategories.add(name);
        }
        if (selectedCategories.size === 0) categoryDimension.filterAll();
        else categoryDimension.filterFunction(d => d === '' || selectedCategories.has(d));
        updateAll();
    });

    issueTypeChart.on('click', function (params) {
        const name = params.name;
        if (selectedIssueTypes.has(name)) {
            selectedIssueTypes.delete(name);
        } else {
            selectedIssueTypes.add(name);
        }
        if (selectedIssueTypes.size === 0) issueTypeDimension.filterAll();
        else issueTypeDimension.filterFunction(d => d === '' || selectedIssueTypes.has(d));
        updateAll();
    });

    countryChart.on('click', function (params) {
        const name = params.name;
        if (selectedCountries.has(name)) {
            selectedCountries.delete(name);
        } else {
            selectedCountries.add(name);
        }
        if (selectedCountries.size === 0) countryDimension.filterAll();
        else countryDimension.filterFunction(d => selectedCountries.has(d));
        updateAll();
    });

    // --- Load Data ---
    async function loadData(year) {
        try {
            const url = `${window.DASHBOARD_CONFIG.endpoint}?year=${year}&dashboard=grievance`;
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                if (response.status === 403) {
                    console.error('Authentication required. Please log in.');
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            const dateFormat = d3.timeParse('%Y-%m-%d');
            data.forEach(d => {
                d.date = dateFormat(d.date);
                d.ticket_count = +d.ticket_count;

                // Map numeric choices to human-readable strings
                const valStr = String(d.dimension_value);
                if (d.dimension_type === 'status' && statusMap[valStr]) {
                    d.dimension_value = statusMap[valStr];
                } else if (d.dimension_type === 'category' && categoryMap[valStr]) {
                    d.dimension_value = categoryMap[valStr];
                } else if (d.dimension_type === 'priority' && priorityMap[valStr]) {
                    d.dimension_value = priorityMap[valStr];
                } else if (d.dimension_type === 'issue_type' && issueTypeMap[valStr]) {
                    d.dimension_value = issueTypeMap[valStr];
                }
            });

            const now = new Date();
            now.setHours(23, 59, 59, 999);
            const currentData = data.filter(d => d.date <= now);

            // Clean filters (clear FIRST, then remove old data)
            selectedStatuses.clear();
            selectedCategories.clear();
            selectedIssueTypes.clear();
            selectedPriorities.clear();
            selectedCountries.clear();

            statusDimension.filterAll();
            categoryDimension.filterAll();
            issueTypeDimension.filterAll();
            priorityDimension.filterAll();
            countryDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(currentData);

            updateAll();
        } catch (error) {
            console.error('Error loading grievance data:', error);
        }
    }

    tabsContainer.querySelectorAll('.year-tab').forEach(btn => {
        btn.addEventListener('click', function() {
            tabsContainer.querySelectorAll('.year-tab').forEach(b =>
                b.classList.remove('bg-white', 'shadow', 'text-blue-600', 'active-tab'));
            this.classList.add('bg-white', 'shadow', 'text-blue-600', 'active-tab');
            loadData(this.dataset.year);
        });
    });

    const firstYear = tabsContainer.querySelector('.active-tab')?.dataset.year;
    if (firstYear) {
        loadData(firstYear);
    }
});
