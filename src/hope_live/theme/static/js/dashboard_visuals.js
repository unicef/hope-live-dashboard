document.addEventListener('DOMContentLoaded', function () {
    const timeFilterContainer = document.getElementById('time-filter-container');
    if (!timeFilterContainer) return;

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

    const REGION_NAMES = {
        'MENAR': gettext('Middle East and North Africa (MENA)'),
        'ESAR': gettext('Eastern and Southern Africa (ESA)'),
        'ECAR': gettext('Europe and Central Asia (ECA)'),
        'WCAR': gettext('West and Central Africa (WCA)'),
        'LACR': gettext('Latin America and Caribbean (LAC)'),
        'EAPR': gettext('East Asia and Pacific (EAP)'),
        'SAR': gettext('South Asia (SA)'),
    };

    function getRegionName(code) {
        return REGION_NAMES[code] || code;
    }

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

    function updateAll() {
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

        timelineChart.setOption(timelineOption, { notMerge: true });

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

        // Update Charts
        // Sector Chart (Donut with outside labels)
        const sectorData = sectorGroup.all()
            .filter(d => d.key !== '' && d.key !== null && d.value[currentMetric] > 0)
            .sort((a, b) => b.value[currentMetric] - a.value[currentMetric]);

        const hasAnySectorSelection = selectedSectors.size > 0;
        const sectorDonutData = sectorData.map(d => {
            const stableColor = getStableColor(d.key);
            return {
                name: d.key,
                value: d.value[currentMetric],
                itemStyle: {
                    color: selectedSectors.has(d.key) ? stableColor : (hasAnySectorSelection ? '#cbd5e1' : stableColor)
                }
            };
        });

        sectorChart.setOption({
            tooltip: {
                trigger: 'item',
                formatter: params => `${params.name}: <b>${formatFullVal(params.value)}</b> (${params.percent}%)`
            },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: {
                    show: true,
                    position: 'outside',
                    formatter: '{b}\n({d}%)',
                    fontSize: 11,
                    color: '#374151'
                },
                labelLine: {
                    show: true,
                    length: 15,
                    length2: 10,
                    smooth: false
                },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold', formatter: params => `${params.name}\n${formatMetric(params.value)}` }
                },
                data: sectorDonutData
            }]
        }, { notMerge: true });
        updateHorizontalBarChart(programChart, programGroup, selectedPrograms, 140, 10);
        // Delivery Donut Chart with outside labels
        const deliveryRawData = deliveryGroup.all()
            .map(d => ({ name: d.key, value: d.value[currentMetric] }))
            .filter(d => d.name !== '' && d.name !== null && d.value > 0);

        const hasAnyDeliverySelection = selectedDeliveries.size > 0;
        const deliverySeriesData = deliveryRawData.map(d => {
            const stableColor = getStableColor(d.name);
            return {
                name: d.name,
                value: d.value,
                itemStyle: {
                    color: selectedDeliveries.has(d.name) ? stableColor : (hasAnyDeliverySelection ? '#cbd5e1' : stableColor)
                }
            };
        });

        deliveryChart.setOption({
            tooltip: {
                trigger: 'item',
                formatter: params => `${params.name}: <b>${formatFullVal(params.value)}</b> (${params.percent}%)`
            },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: {
                    show: true,
                    position: 'outside',
                    formatter: '{b}\n({d}%)',
                    fontSize: 11,
                    color: '#374151'
                },
                labelLine: {
                    show: true,
                    length: 15,
                    length2: 10,
                    smooth: false
                },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold', formatter: params => `${params.name}\n${formatMetric(params.value)}` }
                },
                data: deliverySeriesData
            }]
        }, { notMerge: true });
        updateHorizontalBarChart(fspChart, fspGroup, selectedFsps, 140, 10);
        // Region Chart (with full-name mapping)
        const regionData = regionGroup.all()
            .map(d => {
                const valObj = d.value[activeDimType] || { usd: 0, qty: 0, payments: 0 };
                return { key: d.key, fullName: getRegionName(d.key), value: valObj[currentMetric] };
            })
            .filter(d => d.key !== '' && d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 100);

        const hasAnyRegionSelection = selectedRegions.size > 0;
        regionChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${getRegionName(params[0].name)}: <b>${formatFullVal(params[0].value)}</b>`
            },
            grid: { top: 20, bottom: 30, left: 140, right: 30 },
            xAxis: {
                type: 'value',
                axisLabel: { formatter: val => formatMetric(val), color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: regionData.map(d => d.key),
                inverse: true,
                axisLabel: {
                    color: '#1f2937',
                    fontWeight: 500,
                    formatter: val => getRegionName(val).length > 28 ? getRegionName(val).substring(0, 28) + '...' : getRegionName(val)
                }
            },
            series: [{
                type: 'bar',
                data: regionData.map(d => {
                    const stableColor = getStableColor(d.key);
                    return {
                        name: d.key,
                        value: d.value,
                        itemStyle: {
                            color: selectedRegions.has(d.key) ? stableColor : (hasAnyRegionSelection ? '#cbd5e1' : stableColor)
                        }
                    };
                }),
                barMaxWidth: 22,
                itemStyle: { borderRadius: [0, 4, 4, 0] }
            }]
        }, { notMerge: true });
        updateHorizontalBarChart(beneficiaryGroupChart, beneficiaryGroupGroup, selectedBeneficiaryGroups, 140);

        // 2. Country Chart (Donut with outside labels, all countries)
        const countryData = countryGroup.all()
            .map(d => {
                const valObj = d.value[activeDimType] || { usd: 0, qty: 0, payments: 0 };
                return { key: d.key, value: valObj[currentMetric] };
            })
            .filter(d => d.key !== '' && d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value);

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
            tooltip: {
                trigger: 'item',
                formatter: params => `${params.name}: <b>${formatFullVal(params.value)}</b> (${params.percent}%)`
            },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: {
                    show: true,
                    position: 'outside',
                    formatter: '{b}\n({d}%)',
                    fontSize: 11,
                    color: '#374151'
                },
                labelLine: {
                    show: true,
                    length: 15,
                    length2: 10,
                    smooth: false
                },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold', formatter: params => `${params.name}\n${formatMetric(params.value)}` }
                },
                data: countrySeriesData
            }]
        }, { notMerge: true });
    }

    // --- Interactive Filters Bindings ---
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
    async function loadRange(startDate, endDate) {
        try {
            const from = timeFilter.formatDateStr(startDate);
            const to = timeFilter.formatDateStr(endDate);
            const url = `${window.DASHBOARD_CONFIG.endpoint}?date_from=${from}&date_to=${to}&dashboard=${window.DASHBOARD_CONFIG.type}`;
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
            ndx.add(data);

            timeFilter.setBuffer(startDate, endDate);
            updateAll();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    // --- Time Filter Controller ---
    const timeFilter = new DashboardTimeFilter({
        onFilterChange: (startDate, endDate) => {
            if (timeFilter.isWithinBuffer(startDate, endDate)) {
                dateDimension.filterRange([startDate, endDate]);
                updateAll();
            } else {
                loadRange(startDate, endDate);
            }
        }
    });

    loadRange(timeFilter.currentRange.start, timeFilter.currentRange.end);
});
