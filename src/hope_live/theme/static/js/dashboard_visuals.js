document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    const usdFormat = d => {
        if (Math.abs(d) < 1) return '$0';
        return '$' + d3.format(".2s")(d).replace('G', 'B');
    };

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : '');
    const programDimension = ndx.dimension(d => d.dimension_type === 'program' ? d.dimension_value : '');
    const deliveryDimension = ndx.dimension(d => d.dimension_type === 'delivery_type' ? d.dimension_value : '');
    const fspDimension = ndx.dimension(d => d.dimension_type === 'financial_service_provider' ? d.dimension_value : '');
    const regionDimension = ndx.dimension(d => d.dimension_type === 'region' ? d.dimension_value : '');
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : '');
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'sector';

    // Groups
    const moveDays = dateDimension.group(d3.timeDay);
    const volumeByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const sectorGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_usd : 0);
    const programGroup = programDimension.group().reduceSum(d => d.dimension_type === 'program' ? d.total_usd : 0);
    const deliveryGroup = deliveryDimension.group().reduceSum(d => d.dimension_type === 'delivery_type' ? d.total_usd : 0);
    const fspGroup = fspDimension.group().reduceSum(d => d.dimension_type === 'financial_service_provider' ? d.total_usd : 0);
    const countryGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const regionGroup = regionDimension.group().reduceSum(d => d.dimension_type === 'region' ? d.total_usd : 0);

    // Active filters
    const selectedSectors = new Set();
    const selectedPrograms = new Set();
    const selectedDeliveries = new Set();
    const selectedFsps = new Set();
    const selectedRegions = new Set();
    const selectedCountries = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const sectorChart = echarts.init(document.getElementById('sector-chart'), 'macarons');
    const programChart = echarts.init(document.getElementById('program-chart'), 'macarons');
    const deliveryChart = echarts.init(document.getElementById('delivery-chart'), 'macarons');
    const fspChart = echarts.init(document.getElementById('fsp-chart'), 'macarons');
    const regionChart = echarts.init(document.getElementById('region-chart'), 'macarons');
    const countryChart = echarts.init(document.getElementById('country-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        sectorChart.resize();
        programChart.resize();
        deliveryChart.resize();
        fspChart.resize();
        regionChart.resize();
        countryChart.resize();
    });

    const pendingList = ["SENT TO PAYMENT GATEWAY", "SENT TO FSP", "PENDING"];
    const successfulList = [
        "Distribution Successful",
        "Partially Distributed",
        "Transaction Successful",
    ].map(s => s.toUpperCase());

    function updateTotals() {
        // Total Payments: Count from Sector rows (the most reliable source)
        const totalPayments = ndx.groupAll().reduceSum(d =>
            d.dimension_type === 'sector' ? d.payment_count : 0
        ).value();

        // Total Amount Paid: Sum only the Status rows matching successful statuses
        const totalPaid = ndx.groupAll().reduceSum(d =>
            (d.dimension_type === 'status' && successfulList.includes(String(d.dimension_value).toUpperCase())) ? d.total_usd : 0
        ).value();

        // Outstanding: Sum only the Status rows matching pending statuses
        const totalOutstanding = ndx.groupAll().reduceSum(d =>
            (d.dimension_type === 'status' && pendingList.includes(String(d.dimension_value).toUpperCase())) ? d.total_usd : 0
        ).value();

        const paymentsEl = document.getElementById('total-payments');
        if (paymentsEl) paymentsEl.textContent = d3.format(',')(totalPayments);

        const paidEl = document.getElementById('total-amount-paid');
        if (paidEl) paidEl.textContent = '$' + d3.format(',.0f')(totalPaid);

        const outEl = document.getElementById('outstanding-payments');
        if (outEl) outEl.textContent = '$' + d3.format(',.0f')(totalOutstanding);
    }

    function updateAll(filterSource = null) {
        updateTotals();

        // 1. Timeline Chart (Area time chart)
        const timelineData = volumeByDayGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %d, %Y")(date);
                    const formattedValue = d3.format(",.2f")(params[0].value[1]);
                    return `${formattedDate}<br/><b>$${formattedValue}</b> spending`;
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
                    formatter: val => usdFormat(val),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
            },
            series: [{
                name: 'Spending',
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

        // Helper to update horizontal bar charts (row charts)
        function updateHorizontalBarChart(chartObj, group, activeFiltersSet, leftMargin = 120, maxBars = 100) {
            const rawData = group.all()
                .filter(d => d.key !== '' && d.key !== null && d.value > 0)
                .sort((a, b) => b.value - a.value)
                .slice(0, maxBars);

            const hasAnySelection = activeFiltersSet.size > 0;
            const seriesData = rawData.map(d => ({
                name: d.key,
                value: d.value,
                itemStyle: {
                    color: activeFiltersSet.has(d.key)
                        ? '#2ec7c9'
                        : (hasAnySelection ? '#cbd5e1' : '#2ec7c9')
                }
            }));

            chartObj.setOption({
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    formatter: params => `${params[0].name}: <b>${usdFormat(params[0].value)}</b>`
                },
                grid: { top: 20, bottom: 30, left: leftMargin, right: 30 },
                xAxis: {
                    type: 'value',
                    axisLabel: { formatter: val => usdFormat(val), color: '#64748b' },
                    splitLine: { lineStyle: { color: '#f1f5f9' } }
                },
                yAxis: {
                    type: 'category',
                    data: rawData.map(d => d.key),
                    inverse: true,
                    axisLabel: {
                        color: '#1f2937',
                        fontWeight: 500,
                        formatter: val => val.length > 22 ? val.substring(0, 22) + '...' : val
                    }
                },
                series: [{
                    type: 'bar',
                    data: seriesData,
                    barMaxWidth: 22,
                    itemStyle: { borderRadius: [0, 4, 4, 0] }
                }]
            });
        }

        // Update Horizontal Bar charts
        updateHorizontalBarChart(sectorChart, sectorGroup, selectedSectors, 140);
        updateHorizontalBarChart(programChart, programGroup, selectedPrograms, 140, 10);
        updateHorizontalBarChart(deliveryChart, deliveryGroup, selectedDeliveries, 140);
        updateHorizontalBarChart(fspChart, fspGroup, selectedFsps, 140, 10);
        updateHorizontalBarChart(regionChart, regionGroup, selectedRegions, 140);

        // 2. Country Chart (Vertical Bar)
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
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}: <b>${usdFormat(params[0].value)}</b>` },
            grid: { top: 30, bottom: 95, left: 70, right: 20 },
            xAxis: {
                type: 'category',
                data: countryData.map(d => d.key),
                axisLabel: { rotate: 30, interval: 0, color: '#1f2937', fontWeight: 500 }
            },
            yAxis: {
                type: 'value',
                axisLabel: { formatter: val => usdFormat(val), color: '#64748b' },
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

    const bindFilterToggle = (chartObj, activeFiltersSet, dimension) => {
        chartObj.on('click', function (params) {
            const name = params.name;
            if (activeFiltersSet.has(name)) {
                activeFiltersSet.delete(name);
            } else {
                activeFiltersSet.add(name);
            }
            if (activeFiltersSet.size === 0) dimension.filterAll();
            else dimension.filterFunction(d => activeFiltersSet.has(d));
            updateAll();
        });
    };

    bindFilterToggle(sectorChart, selectedSectors, sectorDimension);
    bindFilterToggle(programChart, selectedPrograms, programDimension);
    bindFilterToggle(deliveryChart, selectedDeliveries, deliveryDimension);
    bindFilterToggle(fspChart, selectedFsps, fspDimension);
    bindFilterToggle(regionChart, selectedRegions, regionDimension);
    bindFilterToggle(countryChart, selectedCountries, countryDimension);

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

            // Clean filters (clear FIRST, then remove old data)
            selectedSectors.clear();
            selectedPrograms.clear();
            selectedDeliveries.clear();
            selectedFsps.clear();
            selectedRegions.clear();
            selectedCountries.clear();

            sectorDimension.filterAll();
            programDimension.filterAll();
            deliveryDimension.filterAll();
            fspDimension.filterAll();
            regionDimension.filterAll();
            countryDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(currentData);

            updateAll();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
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
