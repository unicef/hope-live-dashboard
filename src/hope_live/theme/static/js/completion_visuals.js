document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    const dateDimension = ndx.dimension(d => d.date);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'status';

    const moveDays = dateDimension.group(d3.timeDay);
    const moveMonths = dateDimension.group(d3.timeMonth);

    // Groups
    const reconciledMonthGroup = moveMonths.reduceSum(d => {
        if (!primaryDimFilter(d) || !d.dimension_value) return 0;
        const key = String(d.dimension_value).toUpperCase();
        return (key.includes('RECONCILED') || key.includes('PAID')) ? d.payment_count : 0;
    });

    const openedMonthGroup = moveMonths.reduceSum(d => {
        if (!primaryDimFilter(d) || !d.dimension_value) return 0;
        const key = String(d.dimension_value).toUpperCase();
        return (key.includes('OPEN') || key.includes('PENDING')) ? d.payment_count : 0;
    });

    const countryStatusGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0);

    // Active filters
    const selectedCountries = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const countryChart = echarts.init(document.getElementById('status-country-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        countryChart.resize();
    });

    function updateTotals() {
        const totalReconciled = ndx.groupAll().reduceSum(d => {
            if (!primaryDimFilter(d) || !d.dimension_value) return 0;
            const key = String(d.dimension_value).toUpperCase();
            return (key.includes('RECONCILED') || key.includes('PAID')) ? d.payment_count : 0;
        }).value();

        const totalOpened = ndx.groupAll().reduceSum(d => {
            if (!primaryDimFilter(d) || !d.dimension_value) return 0;
            const key = String(d.dimension_value).toUpperCase();
            return (key.includes('OPEN') || key.includes('PENDING')) ? d.payment_count : 0;
        }).value();

        const total = totalReconciled + totalOpened;
        const reconciledPct = total > 0 ? (totalReconciled / total * 100).toFixed(1) : 0;
        const openedPct = total > 0 ? (totalOpened / total * 100).toFixed(1) : 0;

        document.getElementById('total-reconciled').textContent = `${d3.format(',')(totalReconciled)} (${reconciledPct}% out of ${d3.format(',')(total)} total payments)`;
        document.getElementById('total-opened').textContent = `${d3.format(',')(totalOpened)} (${openedPct}% out of ${d3.format(',')(total)} total payments)`;
    }

    function updateAll(filterSource = null) {
        updateTotals();

        // 1. Stacked Monthly Timeline Chart
        const reconciledData = reconciledMonthGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value]);

        const openedData = openedMonthGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %Y")(date);
                    let tooltipHtml = `${formattedDate}<br/>`;
                    params.forEach(p => {
                        tooltipHtml += `${p.marker} ${p.seriesName}: <b>${d3.format(",")(p.value[1])}</b> payments<br/>`;
                    });
                    return tooltipHtml;
                }
            },
            legend: {
                data: ['Reconciled', 'Still Opened'],
                bottom: 0,
                icon: 'roundRect'
            },
            grid: {
                top: 20,
                bottom: 80,
                left: 60,
                right: 30
            },
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
                    name: 'Reconciled',
                    type: 'bar',
                    stack: 'total',
                    color: '#97b552',
                    barMaxWidth: 35,
                    data: reconciledData
                },
                {
                    name: 'Still Opened',
                    type: 'bar',
                    stack: 'total',
                    color: '#5ab1ef',
                    barMaxWidth: 35,
                    data: openedData
                }
            ]
        };

        if (filterSource !== 'timeline') {
            timelineOption.dataZoom = [
                {
                    type: 'inside',
                    start: 0,
                    end: 100
                },
                {
                    show: true,
                    type: 'slider',
                    start: 0,
                    end: 100,
                    bottom: 30,
                    textStyle: { color: '#64748b' }
                }
            ];
            timelineChart.setOption(timelineOption, { notMerge: true });
        } else {
            timelineChart.setOption(timelineOption);
        }

        // 2. Country Chart
        const countryData = countryStatusGroup.all()
            .filter(d => d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 15);

        const hasAnyCountrySelection = selectedCountries.size > 0;
        const countrySeriesData = countryData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedCountries.has(d.key)
                    ? '#5ab1ef'
                    : (hasAnyCountrySelection ? '#cbd5e1' : '#5ab1ef')
            }
        }));

        countryChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b> payments`
            },
            grid: { top: 30, bottom: 95, left: 70, right: 20 },
            xAxis: {
                type: 'category',
                data: countryData.map(d => d.key),
                axisLabel: {
                    rotate: 30,
                    interval: 0,
                    color: '#1f2937',
                    fontWeight: 500
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
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

    // --- Interaction Bindings ---
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

    countryChart.on('click', function (params) {
        const countryName = params.name;
        if (selectedCountries.has(countryName)) {
            selectedCountries.delete(countryName);
        } else {
            selectedCountries.add(countryName);
        }

        if (selectedCountries.size === 0) {
            countryDimension.filterAll();
        } else {
            countryDimension.filterFunction(d => selectedCountries.has(d));
        }
        updateAll();
    });

    // --- Load Data ---
    async function loadData(year) {
        try {
            const url = `${window.DASHBOARD_CONFIG.endpoint}?year=${year}&dashboard=${window.DASHBOARD_CONFIG.type}`;
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
                d.total_usd = +d.total_usd;
                d.payment_count = +d.payment_count;
            });

            const now = new Date();
            now.setHours(23, 59, 59, 999);
            const currentData = data.filter(d => d.date <= now);

            // Clean state (clear filters FIRST, then remove old data)
            selectedCountries.clear();
            countryDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(currentData);

            updateAll();
        } catch (error) {
            console.error('Error loading completion data:', error);
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
