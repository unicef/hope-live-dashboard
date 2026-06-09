document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : null);
    const categoryDimension = ndx.dimension(d => d.dimension_type === 'category' ? d.dimension_value : null);
    const issueTypeDimension = ndx.dimension(d => d.dimension_type === 'issue_type' ? d.dimension_value : null);
    const priorityDimension = ndx.dimension(d => d.dimension_type === 'priority' ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'category';

    // Groups
    const moveDays = dateDimension.group(d3.timeDay);
    const ticketsByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0);

    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.ticket_count : 0);
    const categoryGroup = categoryDimension.group().reduceSum(d => d.dimension_type === 'category' ? d.ticket_count : 0);
    const issueTypeGroup = issueTypeDimension.group().reduceSum(d => d.dimension_type === 'issue_type' ? d.ticket_count : 0);
    const priorityGroup = priorityDimension.group().reduceSum(d => d.dimension_type === 'priority' ? d.ticket_count : 0);
    const countryGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0);

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

        // 1. Timeline Chart (Area time chart)
        const timelineData = ticketsByDayGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %d, %Y")(date);
                    const formattedValue = d3.format(",")(params[0].value[1]);
                    return `${formattedDate}<br/><b>${formattedValue}</b> tickets`;
                }
            },
            grid: { top: 20, bottom: 80, left: 60, right: 30 },
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
            series: [{
                name: 'Tickets',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: { color: '#5ab1ef', width: 2.5 },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(90, 177, 239, 0.4)' },
                        { offset: 1, color: 'rgba(90, 177, 239, 0.02)' }
                    ])
                },
                data: timelineData
            }]
        };

        if (filterSource !== 'timeline') {
            timelineOption.dataZoom = [
                { type: 'inside', start: 0, end: 100 },
                { show: true, type: 'slider', start: 0, end: 100, bottom: 10, textStyle: { color: '#64748b' } }
            ];
            timelineChart.setOption(timelineOption, { notMerge: true });
        } else {
            timelineChart.setOption(timelineOption);
        }

        // 2. Status Chart (Donut Pie)
        const statusData = statusGroup.all().filter(d => d.key !== null && d.value > 0);
        statusChart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: <b>{c}</b> ({d}%)' },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, formatter: '{b}: {c}' },
                emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
                data: statusData.map(d => ({ name: d.key, value: d.value }))
            }]
        });

        // 3. Priority Chart (Donut Pie)
        const priorityData = priorityGroup.all().filter(d => d.key !== null && d.value > 0);
        priorityChart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: <b>{c}</b> ({d}%)' },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, formatter: '{b}: {c}' },
                emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
                data: priorityData.map(d => ({ name: d.key, value: d.value }))
            }]
        });

        // 4. Category Chart (Horizontal Bar / Row)
        const categoryData = categoryGroup.all().filter(d => d.key !== null && d.value > 0);
        categoryData.sort((a, b) => b.value - a.value);

        const hasAnyCategorySelection = selectedCategories.size > 0;
        const categorySeriesData = categoryData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedCategories.has(d.key)
                    ? '#2ec7c9'
                    : (hasAnyCategorySelection ? '#cbd5e1' : '#2ec7c9')
            }
        }));

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
        });

        // 5. Issue Type Chart (Horizontal Bar / Row)
        const issueTypeData = issueTypeGroup.all().filter(d => d.key !== null && d.value > 0);
        issueTypeData.sort((a, b) => b.value - a.value);

        const hasAnyIssueTypeSelection = selectedIssueTypes.size > 0;
        const issueTypeSeriesData = issueTypeData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedIssueTypes.has(d.key)
                    ? '#2ec7c9'
                    : (hasAnyIssueTypeSelection ? '#cbd5e1' : '#2ec7c9')
            }
        }));

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
        });

        // 6. Country Chart (Vertical Bar)
        const countryData = countryGroup.all()
            .filter(d => d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 15);

        const hasAnyCountrySelection = selectedCountries.size > 0;
        const countrySeriesData = countryData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedCountries.has(d.key)
                    ? '#2ec7c9'
                    : (hasAnyCountrySelection ? '#cbd5e1' : '#2ec7c9')
            }
        }));

        countryChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>` },
            grid: { top: 30, bottom: 95, left: 70, right: 20 },
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
            series: [{
                type: 'bar',
                data: countrySeriesData,
                barMaxWidth: 30,
                itemStyle: { borderRadius: [4, 4, 0, 0] }
            }]
        });
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
        else statusDimension.filterFunction(d => selectedStatuses.has(d));
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
        else priorityDimension.filterFunction(d => selectedPriorities.has(d));
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
        else categoryDimension.filterFunction(d => selectedCategories.has(d));
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
        else issueTypeDimension.filterFunction(d => selectedIssueTypes.has(d));
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
