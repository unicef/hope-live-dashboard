document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    let currentMetric = 'usd'; // Default metric: usd. Can be 'usd', 'qty', or 'payments'

    const formatMetric = (val, metric = currentMetric) => {
        if (metric === 'usd') {
            if (Math.abs(val) < 1) return '$0';
            return '$' + d3.format(".2s")(val).replace('G', 'B');
        } else {
            if (Math.abs(val) < 1) return '0';
            return d3.format(".2s")(val).replace('G', 'B');
        }
    };

    const formatFullVal = (val, metric = currentMetric) => {
        if (metric === 'usd') {
            return '$' + d3.format(",.2f")(val);
        } else {
            return d3.format(",")(val);
        }
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

    const fallbackCountryToRegion = {
        'afghanistan': 'SAR',
        'angola': 'ESAR',
        'armenia': 'ECAR',
        'bangladesh': 'SAR',
        'botswana': 'ESAR',
        'central-african-republic': 'WCAR',
        'chad': 'WCAR',
        'democratic-republic-of-congo': 'WCAR',
        'haiti': 'LACR',
        'kenya': 'ESAR',
        'madagascar': 'ESAR',
        'myanmar': 'EAPR',
        'nigeria': 'WCAR',
        'palestine-state-of': 'MENAR',
        'republic-of-cameroon': 'WCAR',
        'republic-of-mozambique': 'ESAR',
        'senegal': 'WCAR',
        'sierra-leone': 'WCAR',
        'somalia': 'ESAR',
        'south-sudan': 'ESAR',
        'sudan': 'MENAR',
        'syria': 'MENAR',
        'ukraine': 'ECAR',
        'vietnam': 'EAPR',
        'yemen': 'MENAR'
    };

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : '');
    const programDimension = ndx.dimension(d => d.dimension_type === 'program' ? d.dimension_value : '');
    const deliveryDimension = ndx.dimension(d => d.dimension_type === 'delivery_type' ? d.dimension_value : '');
    const fspDimension = ndx.dimension(d => d.dimension_type === 'financial_service_provider' ? d.dimension_value : '');
    const regionDimension = ndx.dimension(d => d.region);
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : '');
    const countryDimension = ndx.dimension(d => d.country_slug);
    const beneficiaryGroupDimension = ndx.dimension(d => d.dimension_type === 'beneficiary_group' ? d.dimension_value : '');

    const primaryDimFilter = d => d.dimension_type === 'sector';

    // Multi-metric custom reduction helper
    function reduceMetric(dimType) {
        return {
            add: (p, v) => {
                if (dimType) {
                    if (v.dimension_type === dimType) {
                        p.usd += +v.total_usd;
                        p.qty += +v.total_qty;
                        p.payments += +v.payment_count;
                    }
                } else {
                    const type = v.dimension_type;
                    if (!p[type]) p[type] = { usd: 0, qty: 0, payments: 0 };
                    p[type].usd += +v.total_usd;
                    p[type].qty += +v.total_qty;
                    p[type].payments += +v.payment_count;
                }
                return p;
            },
            remove: (p, v) => {
                if (dimType) {
                    if (v.dimension_type === dimType) {
                        p.usd -= +v.total_usd;
                        p.qty -= +v.total_qty;
                        p.payments -= +v.payment_count;
                    }
                } else {
                    const type = v.dimension_type;
                    if (!p[type]) p[type] = { usd: 0, qty: 0, payments: 0 };
                    p[type].usd -= +v.total_usd;
                    p[type].qty -= +v.total_qty;
                    p[type].payments -= +v.payment_count;
                }
                return p;
            },
            init: () => dimType ? { usd: 0, qty: 0, payments: 0 } : {}
        };
    }

    // Groups (aggregates usd, qty, and payments simultaneously)
    const moveDays = dateDimension.group(d3.timeDay);
    const volumeByDayGroup = moveDays.reduce(
        (p, v) => {
            const type = v.dimension_type;
            if (!p[type]) p[type] = { usd: 0, qty: 0, payments: 0 };
            p[type].usd += +v.total_usd;
            p[type].qty += +v.total_qty;
            p[type].payments += +v.payment_count;
            return p;
        },
        (p, v) => {
            const type = v.dimension_type;
            if (!p[type]) p[type] = { usd: 0, qty: 0, payments: 0 };
            p[type].usd -= +v.total_usd;
            p[type].qty -= +v.total_qty;
            p[type].payments -= +v.payment_count;
            return p;
        },
        () => ({})
    );

    const sectorGroup = sectorDimension.group().reduce(reduceMetric('sector').add, reduceMetric('sector').remove, reduceMetric('sector').init);
    const programGroup = programDimension.group().reduce(reduceMetric('program').add, reduceMetric('program').remove, reduceMetric('program').init);
    const deliveryGroup = deliveryDimension.group().reduce(reduceMetric('delivery_type').add, reduceMetric('delivery_type').remove, reduceMetric('delivery_type').init);
    const fspGroup = fspDimension.group().reduce(reduceMetric('financial_service_provider').add, reduceMetric('financial_service_provider').remove, reduceMetric('financial_service_provider').init);
    const countryGroup = countryDimension.group().reduce(reduceMetric().add, reduceMetric().remove, reduceMetric().init);
    const regionGroup = regionDimension.group().reduce(reduceMetric().add, reduceMetric().remove, reduceMetric().init);
    const beneficiaryGroupGroup = beneficiaryGroupDimension.group().reduce(reduceMetric('beneficiary_group').add, reduceMetric('beneficiary_group').remove, reduceMetric('beneficiary_group').init);

    // Active filters
    const selectedSectors = new Set();
    const selectedPrograms = new Set();
    const selectedDeliveries = new Set();
    const selectedFsps = new Set();
    const selectedRegions = new Set();
    const selectedCountries = new Set();
    const selectedBeneficiaryGroups = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const sectorChart = echarts.init(document.getElementById('sector-chart'), 'macarons');
    const programChart = echarts.init(document.getElementById('program-chart'), 'macarons');
    const deliveryChart = echarts.init(document.getElementById('delivery-chart'), 'macarons');
    const fspChart = echarts.init(document.getElementById('fsp-chart'), 'macarons');
    const regionChart = echarts.init(document.getElementById('region-chart'), 'macarons');
    const countryChart = echarts.init(document.getElementById('country-chart'), 'macarons');
    const beneficiaryGroupChart = echarts.init(document.getElementById('beneficiary-group-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        sectorChart.resize();
        programChart.resize();
        deliveryChart.resize();
        fspChart.resize();
        regionChart.resize();
        countryChart.resize();
        beneficiaryGroupChart.resize();
    });

    const pendingList = ["SENT TO PAYMENT GATEWAY", "SENT TO FSP", "PENDING"];
    const successfulList = [
        "Distribution Successful",
        "Partially Distributed",
        "Transaction Successful",
    ].map(s => s.toUpperCase());

    function updateTotals() {
        let activeDimType = 'sector';
        if (selectedPrograms.size > 0) activeDimType = 'program';
        else if (selectedDeliveries.size > 0) activeDimType = 'delivery_type';
        else if (selectedFsps.size > 0) activeDimType = 'financial_service_provider';
        else if (selectedSectors.size > 0) activeDimType = 'sector';

        // Total Payments: Count from active dimension rows
        const totalPayments = ndx.groupAll().reduceSum(d =>
            d.dimension_type === activeDimType ? d.payment_count : 0
        ).value();

        // Total Amount Paid: Sum only the Status rows matching successful statuses
        const totalPaid = ndx.groupAll().reduceSum(d =>
            (d.dimension_type === 'status' && successfulList.includes(String(d.dimension_value).toUpperCase())) ? d.total_usd : 0
        ).value();

        // Total Quantity: Sum from active dimension rows
        const totalQty = ndx.groupAll().reduceSum(d =>
            d.dimension_type === activeDimType ? d.total_qty : 0
        ).value();

        // Outstanding: Sum only the Status rows matching pending statuses
        const totalOutstanding = ndx.groupAll().reduceSum(d =>
            (d.dimension_type === 'status' && pendingList.includes(String(d.dimension_value).toUpperCase())) ? d.total_usd : 0
        ).value();

        const paymentsEl = document.getElementById('total-payments');
        if (paymentsEl) paymentsEl.textContent = d3.format(',')(totalPayments);

        const paidEl = document.getElementById('total-amount-paid');
        if (paidEl) paidEl.textContent = '$' + d3.format(',.0f')(totalPaid);

        const qtyEl = document.getElementById('total-qty-distributed');
        if (qtyEl) qtyEl.textContent = d3.format(',.0f')(totalQty);

        const outEl = document.getElementById('outstanding-payments');
        if (outEl) outEl.textContent = '$' + d3.format(',.0f')(totalOutstanding);
    }

    function updateAll(filterSource = null) {
        let activeDimType = 'sector';
        if (selectedPrograms.size > 0) activeDimType = 'program';
        else if (selectedDeliveries.size > 0) activeDimType = 'delivery_type';
        else if (selectedFsps.size > 0) activeDimType = 'financial_service_provider';
        else if (selectedSectors.size > 0) activeDimType = 'sector';

        updateTotals();

        // 1. Timeline Chart (Area time chart)
        const timelineData = volumeByDayGroup.all()
            .filter(d => d.key !== null)
            .map(d => {
                const valObj = d.value[activeDimType] || { usd: 0, qty: 0, payments: 0 };
                return [d.key.getTime(), valObj[currentMetric]];
            });

        const metricName = currentMetric === 'usd' ? gettext('Spending') : (currentMetric === 'qty' ? gettext('Quantity') : gettext('Payments'));
        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %d, %Y")(date);
                    const formattedValue = formatFullVal(params[0].value[1]);
                    return `${formattedDate}<br/><b>${formattedValue}</b> ${metricName.toLowerCase()}`;
                }
            },
            grid: { top: 20, bottom: 80, left: 70, right: 30 },
            xAxis: {
                type: 'time',
                axisLabel: { color: '#64748b' }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => formatMetric(val),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
            },
            series: [{
                name: metricName,
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
        function updateHorizontalBarChart(chartObj, group, activeFiltersSet, leftMargin = 120, maxBars = 100, isRegionalOrCountry = false) {
            const rawData = group.all()
                .map(d => {
                    if (isRegionalOrCountry) {
                        const valObj = d.value[activeDimType] || { usd: 0, qty: 0, payments: 0 };
                        return { key: d.key, value: valObj[currentMetric] };
                    } else {
                        return { key: d.key, value: d.value[currentMetric] };
                    }
                })
                .filter(d => d.key !== '' && d.key !== null && d.value > 0)
                .sort((a, b) => b.value - a.value)
                .slice(0, maxBars);

            const hasAnySelection = activeFiltersSet.size > 0;
            const seriesData = rawData.map(d => {
                const stableColor = getStableColor(d.key);
                return {
                    name: d.key,
                    value: d.value,
                    itemStyle: {
                        color: activeFiltersSet.has(d.key)
                            ? stableColor
                            : (hasAnySelection ? '#cbd5e1' : stableColor)
                    }
                };
            });

            chartObj.setOption({
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    formatter: params => `${params[0].name}: <b>${formatFullVal(params[0].value)}</b>`
                },
                grid: { top: 20, bottom: 30, left: leftMargin, right: 30 },
                xAxis: {
                    type: 'value',
                    axisLabel: { formatter: val => formatMetric(val), color: '#64748b' },
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
            }, { notMerge: true });
        }

        // Helper for Pie/Donut breakdown charts (e.g. Delivery Type)
        function updateDonutChart(chartObj, group, activeFiltersSet) {
            const rawData = group.all()
                .map(d => ({ name: d.key, value: d.value[currentMetric] }))
                .filter(d => d.name !== '' && d.name !== null && d.value > 0);

            const hasAnySelection = activeFiltersSet.size > 0;
            const seriesData = rawData.map(d => {
                const stableColor = getStableColor(d.name);
                return {
                    name: d.name,
                    value: d.value,
                    itemStyle: {
                        color: activeFiltersSet.has(d.name)
                            ? stableColor
                            : (hasAnySelection ? '#cbd5e1' : stableColor)
                    }
                };
            });

            chartObj.setOption({
                tooltip: {
                    trigger: 'item',
                    formatter: params => `${params.name}: <b>${formatFullVal(params.value)}</b> (${params.percent}%)`
                },
                legend: {
                    orient: 'horizontal',
                    bottom: 0,
                    textStyle: { color: '#64748b' }
                },
                series: [{
                    type: 'pie',
                    radius: ['45%', '70%'],
                    avoidLabelOverlap: true,
                    itemStyle: {
                        borderRadius: 6,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: 14,
                            fontWeight: 'bold',
                            formatter: params => `${params.name}\n${formatMetric(params.value)}`
                        }
                    },
                    data: seriesData
                }]
            }, { notMerge: true });
        }

        // Update Charts
        updateHorizontalBarChart(sectorChart, sectorGroup, selectedSectors, 140);
        updateHorizontalBarChart(programChart, programGroup, selectedPrograms, 140, 10);
        updateDonutChart(deliveryChart, deliveryGroup, selectedDeliveries); // Donut for delivery types!
        updateHorizontalBarChart(fspChart, fspGroup, selectedFsps, 140, 10);
        updateHorizontalBarChart(regionChart, regionGroup, selectedRegions, 140, 100, true);
        updateHorizontalBarChart(beneficiaryGroupChart, beneficiaryGroupGroup, selectedBeneficiaryGroups, 140);

        // 2. Country Chart (Vertical Bar)
        const countryData = countryGroup.all()
            .map(d => {
                const valObj = d.value[activeDimType] || { usd: 0, qty: 0, payments: 0 };
                return { key: d.key, value: valObj[currentMetric] };
            })
            .filter(d => d.key !== '' && d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 15);

        const hasAnyCountrySelection = selectedCountries.size > 0;
        const countrySeriesData = countryData.map(d => {
            const stableColor = getStableColor(d.key);
            return {
                name: d.key,
                value: d.value,
                itemStyle: {
                    color: selectedCountries.has(d.key)
                        ? stableColor
                        : (hasAnyCountrySelection ? '#cbd5e1' : stableColor)
                }
            };
        });

        countryChart.setOption({
            tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}: <b>${formatFullVal(params[0].value)}</b>` },
            grid: { top: 30, bottom: 95, left: 75, right: 20 },
            xAxis: {
                type: 'category',
                data: countryData.map(d => d.key),
                axisLabel: { rotate: 30, interval: 0, color: '#1f2937', fontWeight: 500 }
            },
            yAxis: {
                type: 'value',
                axisLabel: { formatter: val => formatMetric(val), color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            series: [{
                type: 'bar',
                data: countrySeriesData,
                barMaxWidth: 30,
                itemStyle: { borderRadius: [4, 4, 0, 0] }
            }]
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

    const bindFilterToggle = (chartObj, activeFiltersSet, dimension) => {
        chartObj.on('click', function (params) {
            const name = params.name;
            if (activeFiltersSet.has(name)) {
                activeFiltersSet.delete(name);
            } else {
                activeFiltersSet.add(name);
            }
            if (activeFiltersSet.size === 0) dimension.filterAll();
            else dimension.filterFunction(d => d === '' || activeFiltersSet.has(d));
            updateAll();
        });
    };

    bindFilterToggle(sectorChart, selectedSectors, sectorDimension);
    bindFilterToggle(programChart, selectedPrograms, programDimension);
    bindFilterToggle(deliveryChart, selectedDeliveries, deliveryDimension);
    bindFilterToggle(fspChart, selectedFsps, fspDimension);
    bindFilterToggle(regionChart, selectedRegions, regionDimension);
    bindFilterToggle(countryChart, selectedCountries, countryDimension);
    bindFilterToggle(beneficiaryGroupChart, selectedBeneficiaryGroups, beneficiaryGroupDimension);

    // Metric selector tab clicks
    const metricTabs = document.querySelectorAll('.metric-tab');
    metricTabs.forEach(btn => {
        btn.addEventListener('click', function() {
            metricTabs.forEach(b => {
                b.classList.remove('bg-white', 'shadow', 'text-blue-800', 'active-metric');
                b.classList.add('text-gray-600');
            });
            this.classList.add('bg-white', 'shadow', 'text-blue-800', 'active-metric');
            this.classList.remove('text-gray-600');
            currentMetric = this.dataset.metric;

            const timelineTitle = document.getElementById('timeline-title');
            if (timelineTitle) {
                if (currentMetric === 'usd') timelineTitle.textContent = gettext('Spending Timeline');
                else if (currentMetric === 'qty') timelineTitle.textContent = gettext('Quantity Distribution Timeline');
                else timelineTitle.textContent = gettext('Payments Timeline');
            }

            updateAll();
        });
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

            const countryToRegion = Object.assign({}, fallbackCountryToRegion);
            data.forEach(d => {
                if (d.dimension_type === 'region') {
                    countryToRegion[d.country_slug] = d.dimension_value;
                }
            });

            const dateFormat = d3.timeParse('%Y-%m-%d');
            data.forEach(d => {
                d.date = dateFormat(d.date);
                d.total_usd = +d.total_usd;
                d.total_qty = +d.total_qty || 0;
                d.payment_count = +d.payment_count;
                d.region = countryToRegion[d.country_slug] || '';
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
            selectedBeneficiaryGroups.clear();

            sectorDimension.filterAll();
            programDimension.filterAll();
            deliveryDimension.filterAll();
            fspDimension.filterAll();
            regionDimension.filterAll();
            countryDimension.filterAll();
            beneficiaryGroupDimension.filterAll();
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
