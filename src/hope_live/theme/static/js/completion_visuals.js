document.addEventListener('DOMContentLoaded', function () {
    const timeFilterContainer = document.getElementById('time-filter-container');
    if (!timeFilterContainer) return;

    let currentMetric = 'payments'; // Default metric: payments. Can be 'payments' or 'usd'

    const formatMetric = (val) => {
        if (currentMetric === 'usd') {
            if (Math.abs(val) < 1) return '$0';
            return '$' + d3.format(".2s")(val).replace('G', 'B');
        } else {
            return d3.format(",")(val);
        }
    };

    const formatFullVal = (val) => {
        if (currentMetric === 'usd') {
            return '$' + d3.format(",.2f")(val);
        } else {
            return d3.format(",")(val);
        }
    };

    const chartHelpers = window.HopeChart || {};
    const getStableColor = chartHelpers.getStableColor || (() => '#5470c6');

    let ndx = crossfilter([]);

    const dateDimension = ndx.dimension(d => d.date);
    const countryDimension = ndx.dimension(d => d.country_slug);
    const beneficiaryGroupDimension = ndx.dimension(d => d.dimension_type === 'beneficiary_group' ? d.dimension_value : '');

    const primaryDimFilter = d => d.dimension_type === 'status';

    const moveDays = dateDimension.group(d3.timeDay);
    const moveMonths = dateDimension.group(d3.timeMonth);

    // Groups (aggregates usd and payments simultaneously)
    const reconciledMonthGroup = moveMonths.reduce(
        (p, v) => {
            if (primaryDimFilter(v) && v.dimension_value) {
                const key = String(v.dimension_value).toUpperCase();
                if (key.includes('RECONCILED') || key.includes('PAID')) {
                    p.payments += v.payment_count;
                    p.usd += +v.total_usd;
                }
            }
            return p;
        },
        (p, v) => {
            if (primaryDimFilter(v) && v.dimension_value) {
                const key = String(v.dimension_value).toUpperCase();
                if (key.includes('RECONCILED') || key.includes('PAID')) {
                    p.payments -= v.payment_count;
                    p.usd -= +v.total_usd;
                }
            }
            return p;
        },
        () => ({ payments: 0, usd: 0 })
    );

    const openedMonthGroup = moveMonths.reduce(
        (p, v) => {
            if (primaryDimFilter(v) && v.dimension_value) {
                const key = String(v.dimension_value).toUpperCase();
                if (key.includes('OPEN') || key.includes('PENDING')) {
                    p.payments += v.payment_count;
                    p.usd += +v.total_usd;
                }
            }
            return p;
        },
        (p, v) => {
            if (primaryDimFilter(v) && v.dimension_value) {
                const key = String(v.dimension_value).toUpperCase();
                if (key.includes('OPEN') || key.includes('PENDING')) {
                    p.payments -= v.payment_count;
                    p.usd -= +v.total_usd;
                }
            }
            return p;
        },
        () => ({ payments: 0, usd: 0 })
    );

    const countryStatusGroup = countryDimension.group().reduce(
        (p, v) => {
            if (primaryDimFilter(v) && v.dimension_value) {
                const key = String(v.dimension_value).toUpperCase();
                const isReconciled = (key.includes('RECONCILED') || key.includes('PAID'));
                const isOpened = (key.includes('OPEN') || key.includes('PENDING'));
                if (isReconciled) {
                    p.reconciled_payments += v.payment_count;
                    p.reconciled_usd += +v.total_usd;
                } else if (isOpened) {
                    p.opened_payments += v.payment_count;
                    p.opened_usd += +v.total_usd;
                }
            }
            return p;
        },
        (p, v) => {
            if (primaryDimFilter(v) && v.dimension_value) {
                const key = String(v.dimension_value).toUpperCase();
                const isReconciled = (key.includes('RECONCILED') || key.includes('PAID'));
                const isOpened = (key.includes('OPEN') || key.includes('PENDING'));
                if (isReconciled) {
                    p.reconciled_payments -= v.payment_count;
                    p.reconciled_usd -= +v.total_usd;
                } else if (isOpened) {
                    p.opened_payments -= v.payment_count;
                    p.opened_usd -= +v.total_usd;
                }
            }
            return p;
        },
        () => ({ reconciled_payments: 0, reconciled_usd: 0, opened_payments: 0, opened_usd: 0 })
    );

    const beneficiaryGroupGroup = beneficiaryGroupDimension.group().reduce(
        (p, v) => {
            if (v.dimension_type === 'beneficiary_group') {
                p.payments += v.payment_count;
                p.usd += +v.total_usd;
            }
            return p;
        },
        (p, v) => {
            if (v.dimension_type === 'beneficiary_group') {
                p.payments -= v.payment_count;
                p.usd -= +v.total_usd;
            }
            return p;
        },
        () => ({ payments: 0, usd: 0 })
    );

    // Active filters
    const selectedCountries = new Set();
    const selectedBeneficiaryGroups = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const countryChart = echarts.init(document.getElementById('status-country-chart'), 'macarons');
    const completionGauge = echarts.init(document.getElementById('completion-gauge'), 'macarons');
    const beneficiaryGroupChart = echarts.init(document.getElementById('beneficiary-group-chart'), 'macarons');
    const quadrantEl = document.getElementById('quality-quadrant-chart');
    const quadrantChart = quadrantEl ? echarts.init(quadrantEl, 'macarons') : null;

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        countryChart.resize();
        completionGauge.resize();
        beneficiaryGroupChart.resize();
        if (quadrantChart) quadrantChart.resize();
    });

    const pendingList = ["SENT TO PAYMENT GATEWAY", "SENT TO FSP", "PENDING"];
    const successfulList = [
        "DISTRIBUTION SUCCESSFUL",
        "PARTIALLY DISTRIBUTED",
        "TRANSACTION SUCCESSFUL",
    ].map(s => s.toUpperCase());

    // Financial rows are used only for the delivery axis of the quality quadrant.
    let financialRows = [];
    let activeRange = null;

    function updateTotals() {
        const totalReconciled = ndx.groupAll().reduceSum(d => {
            if (!primaryDimFilter(d) || !d.dimension_value) return 0;
            const key = String(d.dimension_value).toUpperCase();
            const match = (key.includes('RECONCILED') || key.includes('PAID'));
            return match ? (currentMetric === 'usd' ? +d.total_usd : d.payment_count) : 0;
        }).value();

        const totalOpened = ndx.groupAll().reduceSum(d => {
            if (!primaryDimFilter(d) || !d.dimension_value) return 0;
            const key = String(d.dimension_value).toUpperCase();
            const match = (key.includes('OPEN') || key.includes('PENDING'));
            return match ? (currentMetric === 'usd' ? +d.total_usd : d.payment_count) : 0;
        }).value();

        const total = totalReconciled + totalOpened;
        const reconciledPct = total > 0 ? (totalReconciled / total * 100).toFixed(1) : 0;
        const openedPct = total > 0 ? (totalOpened / total * 100).toFixed(1) : 0;
        const completionRate = total > 0 ? (totalReconciled / total * 100) : 0;

        const outOfReconciled = interpolate(gettext('%s out of %s total'), [reconciledPct + '%', formatFullVal(total)]);
        document.getElementById('total-reconciled').textContent = `${formatFullVal(totalReconciled)} (${outOfReconciled})`;

        const outOfOpened = interpolate(gettext('%s out of %s total'), [openedPct + '%', formatFullVal(total)]);
        document.getElementById('total-opened').textContent = `${formatFullVal(totalOpened)} (${outOfOpened})`;
        document.getElementById('completion-rate-text').textContent = `${completionRate.toFixed(1)}%`;

        // Update ECharts micro-gauge
        completionGauge.setOption({
            series: [{
                type: 'gauge',
                startAngle: 180,
                endAngle: 0,
                center: ['50%', '75%'],
                radius: '95%',
                min: 0,
                max: 100,
                splitNumber: 2,
                axisLine: {
                    lineStyle: {
                        width: 5,
                        color: [
                            [0.3, '#d87a80'],
                            [0.7, '#ffb980'],
                            [1, '#2ec7c9']
                        ]
                    }
                },
                pointer: {
                    icon: 'path://M12.8,29.5C13,29.5,13,29.5,13,29.5c0-0.4-0.3-0.7-0.7-0.7c-0.4,0-0.7,0.3-0.7,0.7C11.6,29.5,11.7,29.5,12.8,29.5z',
                    width: 2.5,
                    length: '60%',
                    offsetCenter: [0, 2]
                },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                title: { show: false },
                detail: { show: false },
                data: [{ value: completionRate.toFixed(1) }]
            }]
        }, { notMerge: true });
    }

    function updateAll() {
        updateTotals();

        const unitName = currentMetric === 'usd' ? 'USD' : gettext('payments');

        // 1. Stacked Monthly Timeline Chart
        const reconciledData = reconciledMonthGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value[currentMetric]]);

        const openedData = openedMonthGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value[currentMetric]]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %Y")(date);
                    let tooltipHtml = `${formattedDate}<br/>`;
                    params.forEach(p => {
                        tooltipHtml += `${p.marker} ${p.seriesName}: <b>${formatFullVal(p.value[1])}</b> ${unitName}<br/>`;
                    });
                    return tooltipHtml;
                }
            },
            legend: {
                data: [gettext('Reconciled'), gettext('Still open')],
                bottom: 0,
                icon: 'roundRect'
            },
            grid: {
                top: 15,
                bottom: 30,
                left: 60,
                right: 20
            },
            xAxis: {
                type: 'time',
                axisLabel: { color: '#64748b', formatter: value => d3.timeFormat('%b')(new Date(value)) }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => formatMetric(val),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
            },
            series: [
                {
                    name: gettext('Reconciled'),
                    type: 'bar',
                    stack: 'total',
                    color: '#97b552',
                    barMaxWidth: 35,
                    data: reconciledData
                },
                {
                    name: gettext('Still open'),
                    type: 'bar',
                    stack: 'total',
                    color: '#5ab1ef',
                    barMaxWidth: 35,
                    data: openedData
                }
            ]
        };

        timelineChart.setOption(timelineOption, { notMerge: true });

        // 2. Stacked Country Chart (top 10)
        const countryData = countryStatusGroup.all()
            .map(d => {
                const reconciled = currentMetric === 'usd' ? d.value.reconciled_usd : d.value.reconciled_payments;
                const opened = currentMetric === 'usd' ? d.value.opened_usd : d.value.opened_payments;
                return {
                    key: d.key,
                    reconciled: reconciled,
                    opened: opened,
                    total: reconciled + opened
                };
            })
            .filter(d => d.key !== '' && d.key !== null && d.total > 0)
            .sort((a, b) => b.total - a.total)
            .slice(0, 10);

        const hasAnyCountrySelection = selectedCountries.size > 0;
        const countrySeriesDataReconciled = countryData.map(d => {
            const isSelected = selectedCountries.has(d.key);
            const opacity = isSelected ? 1 : (hasAnyCountrySelection ? 0.35 : 1);
            return {
                value: d.reconciled,
                itemStyle: { color: '#97b552', opacity: opacity }
            };
        });

        const countrySeriesDataOpened = countryData.map(d => {
            const isSelected = selectedCountries.has(d.key);
            const opacity = isSelected ? 1 : (hasAnyCountrySelection ? 0.35 : 1);
            return {
                value: d.opened,
                itemStyle: { color: '#5ab1ef', opacity: opacity }
            };
        });

        countryChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: function (params) {
                    let tooltipHtml = `${params[0].name}<br/>`;
                    params.forEach(p => {
                        tooltipHtml += `${p.marker} ${p.seriesName}: <b>${formatFullVal(p.value)}</b> ${unitName}<br/>`;
                    });
                    return tooltipHtml;
                }
            },
            legend: {
                data: [gettext('Reconciled'), gettext('Still open')],
                top: 0,
                right: 20
            },
            grid: { top: 30, bottom: 55, left: 60, right: 20 },
            xAxis: {
                type: 'category',
                data: countryData.map(d => d.key),
                axisLabel: {
                    rotate: 30,
                    interval: 0,
                    width: 80,
                    overflow: 'truncate',
                    color: '#1f2937',
                    fontWeight: 500
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => formatMetric(val),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            series: [
                {
                    name: gettext('Reconciled'),
                    type: 'bar',
                    stack: 'total',
                    barMaxWidth: 30,
                    data: countrySeriesDataReconciled,
                    itemStyle: { borderRadius: [0, 0, 0, 0] }
                },
                {
                    name: gettext('Still open'),
                    type: 'bar',
                    stack: 'total',
                    barMaxWidth: 30,
                    data: countrySeriesDataOpened,
                    itemStyle: { borderRadius: [4, 4, 0, 0] },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: params => formatMetric(countryData[params.dataIndex] ? countryData[params.dataIndex].total : params.value),
                        color: '#0f172a',
                        fontWeight: 600,
                        fontSize: 10
                    }
                }
            ]
        }, { notMerge: true });

        // Beneficiary Group Chart (top 10)
        const bgData = beneficiaryGroupGroup.all()
            .map(d => ({ key: d.key, value: d.value[currentMetric] }))
            .filter(d => d.key !== '' && d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 10);

        const hasAnyBgSelection = selectedBeneficiaryGroups.size > 0;
        const bgSeriesData = bgData.map(d => {
            const stableColor = getStableColor(d.key);
            return {
                name: d.key,
                value: d.value,
                itemStyle: {
                    color: selectedBeneficiaryGroups.has(d.key) ? stableColor : (hasAnyBgSelection ? '#cbd5e1' : stableColor)
                }
            };
        });

        beneficiaryGroupChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${params[0].name}: <b>${formatFullVal(params[0].value)}</b> ${unitName}`
            },
            grid: { top: 15, bottom: 25, left: 220, right: 60 },
            xAxis: {
                type: 'value',
                axisLabel: { formatter: val => formatMetric(val), color: '#64748b', fontSize: 10 },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: bgData.map(d => d.key),
                inverse: true,
                axisTick: { show: false },
                axisLine: { show: true, lineStyle: { color: '#f1f5f9' } },
                axisLabel: {
                    show: true,
                    width: 200,
                    overflow: 'truncate',
                    color: '#374151',
                    fontSize: 10
                }
            },
            series: [{
                type: 'bar',
                data: bgSeriesData,
                barMaxWidth: 22,
                showBackground: true,
                backgroundStyle: { color: 'rgba(241, 245, 249, 0.75)', borderRadius: [0, 4, 4, 0] },
                itemStyle: { borderRadius: [0, 4, 4, 0] },
                label: {
                    show: true,
                    position: 'right',
                    distance: 6,
                    formatter: params => formatMetric(params.value),
                    color: '#0f172a',
                    fontWeight: 600,
                    fontSize: 11
                }
            }]
        }, { notMerge: true });

        updateQuadrant();
    }

    // Quality quadrant: reconciliation rate (completion) versus delivery success rate (financial)
    function updateQuadrant() {
        if (!quadrantChart) return;

        const reconciliation = {};
        countryStatusGroup.all().forEach(d => {
            if (!d.key) return;
            const reconciled = currentMetric === 'usd' ? d.value.reconciled_usd : d.value.reconciled_payments;
            const opened = currentMetric === 'usd' ? d.value.opened_usd : d.value.opened_payments;
            reconciliation[d.key] = { reconciled: reconciled, opened: opened };
        });

        const metricKey = currentMetric === 'usd' ? 'total_usd' : 'payment_count';
        const delivery = {};
        financialRows.forEach(r => {
            if (r.dimension_type !== 'status') return;
            if (activeRange && r.date && (r.date < activeRange.start || r.date > activeRange.end)) return;
            if (selectedCountries.size > 0 && !selectedCountries.has(r.country_slug)) return;

            const key = String(r.dimension_value || '').toUpperCase();
            if (!pendingList.includes(key) && !successfulList.includes(key)) return;

            if (!delivery[r.country_slug]) delivery[r.country_slug] = { delivered: 0, pending: 0 };
            const value = +r[metricKey] || 0;
            if (successfulList.includes(key)) delivery[r.country_slug].delivered += value;
            else delivery[r.country_slug].pending += value;
        });

        const points = [];
        Object.keys(reconciliation).forEach(country => {
            const rec = reconciliation[country];
            const totalReconciled = rec.reconciled + rec.opened;
            const deliv = delivery[country];
            if (!deliv || totalReconciled <= 0) return;
            const totalDelivery = deliv.delivered + deliv.pending;
            if (totalDelivery <= 0) return;

            points.push({
                name: country,
                value: [
                    (rec.reconciled / totalReconciled) * 100,
                    (deliv.delivered / totalDelivery) * 100,
                    totalReconciled
                ],
                itemStyle: { color: getStableColor(country) }
            });
        });

        const maxVolume = points.reduce((max, p) => Math.max(max, p.value[2]), 0) || 1;

        quadrantChart.setOption({
            tooltip: {
                trigger: 'item',
                formatter: params => {
                    const reconPct = params.value[0];
                    const deliveryPct = params.value[1];
                    const volume = params.value[2];
                    return `<b>${params.name}</b><br/>${gettext('Reconciliation rate')}: ${reconPct.toFixed(1)}%<br/>` +
                        `${gettext('Delivery success rate')}: ${deliveryPct.toFixed(1)}%<br/>` +
                        `${gettext('Reconciled volume')}: ${formatFullVal(volume)}`;
                }
            },
            grid: { top: 30, right: 35, bottom: 55, left: 65 },
            xAxis: {
                type: 'value',
                min: 0,
                max: 100,
                name: gettext('Reconciliation rate (%)'),
                nameLocation: 'middle',
                nameGap: 32,
                nameTextStyle: { color: '#475569', fontSize: 11 },
                axisLabel: { formatter: '{value}%', color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: 100,
                name: gettext('Delivery success rate (%)'),
                nameLocation: 'middle',
                nameGap: 46,
                nameTextStyle: { color: '#475569', fontSize: 11 },
                axisLabel: { formatter: '{value}%', color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            series: [{
                type: 'scatter',
                data: points,
                symbolSize: value => 10 + 30 * Math.sqrt(value[2] / maxVolume),
                label: {
                    show: true,
                    position: 'top',
                    fontSize: 10,
                    color: '#374151',
                    formatter: params => params.name
                },
                markLine: {
                    silent: true,
                    symbol: 'none',
                    lineStyle: { type: 'dashed', color: '#cbd5e1' },
                    data: [{ xAxis: 80 }, { yAxis: 80 }]
                }
            }]
        }, { notMerge: true });
    }

    async function loadFinancialForQuadrant(from, to) {
        try {
            const url = `${window.DASHBOARD_CONFIG.endpoint}?date_from=${from}&date_to=${to}&dashboard=financial`;
            const response = await fetch(url, {
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) return;

            const rows = await response.json();
            const dateFormat = d3.timeParse('%Y-%m-%d');
            rows.forEach(r => {
                r.date = dateFormat(r.date);
                r.total_usd = +r.total_usd || 0;
                r.payment_count = +r.payment_count || 0;
            });
            financialRows = rows;
        } catch (error) {
            console.error('Error loading financial data for the quality quadrant:', error);
        }
    }

    // --- Interaction Bindings ---
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

    beneficiaryGroupChart.on('click', function (params) {
        const name = params.name;
        if (selectedBeneficiaryGroups.has(name)) {
            selectedBeneficiaryGroups.delete(name);
        } else {
            selectedBeneficiaryGroups.add(name);
        }
        if (selectedBeneficiaryGroups.size === 0) {
            beneficiaryGroupDimension.filterAll();
        } else {
            beneficiaryGroupDimension.filterFunction(d => selectedBeneficiaryGroups.has(d));
        }
        updateAll();
    });

    // Metric selector toggler
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

            // Update card and chart titles
            const reconciledTitle = document.getElementById('reconciled-card-title');
            const openedTitle = document.getElementById('opened-card-title');
            const timelineTitle = document.getElementById('timeline-title');
            const countryTitle = document.getElementById('country-chart-title');

            if (currentMetric === 'usd') {
                if (reconciledTitle) reconciledTitle.textContent = gettext('Reconciled amount (USD)');
                if (openedTitle) openedTitle.textContent = gettext('Still open amount (USD)');
                if (timelineTitle) timelineTitle.textContent = gettext('Reconciliation timeline (USD)');
                if (countryTitle) countryTitle.textContent = gettext('Reconciliation status by country (USD)');
            } else {
                if (reconciledTitle) reconciledTitle.textContent = gettext('Reconciled payments');
                if (openedTitle) openedTitle.textContent = gettext('Still open payments');
                if (timelineTitle) timelineTitle.textContent = gettext('Reconciliation timeline');
                if (countryTitle) countryTitle.textContent = gettext('Reconciliation status by country');
            }

            const bgTitle = document.getElementById('bg-title');
            if (bgTitle) {
                bgTitle.textContent = currentMetric === 'usd'
                    ? gettext('Cash disbursed by beneficiary group')
                    : gettext('Payments by beneficiary group');
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
            activeRange = { start: startDate, end: endDate };

            const dateFormat = d3.timeParse('%Y-%m-%d');
            data.forEach(d => {
                d.date = dateFormat(d.date);
                d.total_usd = +d.total_usd;
                d.payment_count = +d.payment_count;
            });

            // Clean state (clear filters FIRST, then remove old data)
            selectedCountries.clear();
            selectedBeneficiaryGroups.clear();
            countryDimension.filterAll();
            beneficiaryGroupDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(data);

            await loadFinancialForQuadrant(from, to);

            timeFilter.setBuffer(startDate, endDate);
            updateAll();
        } catch (error) {
            console.error('Error loading completion data:', error);
        }
    }

    // --- Time Filter Controller ---
    const timeFilter = new DashboardTimeFilter({
        onFilterChange: (startDate, endDate) => {
            if (timeFilter.isWithinBuffer(startDate, endDate)) {
                activeRange = { start: startDate, end: endDate };
                dateDimension.filterRange([startDate, endDate]);
                updateAll();
            } else {
                loadRange(startDate, endDate);
            }
        }
    });

    loadRange(timeFilter.currentRange.start, timeFilter.currentRange.end);
});
