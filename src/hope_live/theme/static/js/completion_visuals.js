document.addEventListener('DOMContentLoaded', function () {
    const timeFilterContainer = document.getElementById('time-filter-container');
    if (!timeFilterContainer) return;

    let currentMetric = 'payments'; // Default metric: payments. Can be 'payments' or 'usd'
    let countryView = 'absolute'; // Country chart: 'absolute' or 'share' (100% stacked)

    // Shared semantic colours: green = reconciled, amber = still open,
    // teal = delivered (matches the financial dashboard's Delivered stage).
    const RECONCILED_COLOR = '#97b552';
    const OPEN_COLOR = '#ffb980';
    const DELIVERY_COLOR = '#2ec7c9';

    const formatCompact = (val) => {
        if (currentMetric === 'usd') {
            if (Math.abs(val) < 1) return '$0';
            return '$' + d3.format(".2s")(val).replace('G', 'B');
        }
        if (Math.abs(val) < 1000) return d3.format(",")(val);
        return d3.format(".2s")(val).replace('G', 'B');
    };

    const formatCountryName = (slug) => {
        if (!slug) return '';
        const minorWords = new Set(['of', 'and', 'the', 'for']);
        return String(slug)
            .split('-')
            .map((part, index) => (index > 0 && minorWords.has(part)) ? part : part.charAt(0).toUpperCase() + part.slice(1))
            .join(' ');
    };

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
    const verificationDimension = ndx.dimension(d => d.dimension_type === 'verification' ? d.dimension_value : '');

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

    // Verification rows (dimension_type = verification) are summed by their
    // value: SELECTED, VERIFIED, PENDING and DISCREPANCIES.
    const verificationGroup = verificationDimension.group().reduce(
        (p, v) => {
            if (v.dimension_type === 'verification') {
                p.payments += v.payment_count;
                p.usd += +v.total_usd;
            }
            return p;
        },
        (p, v) => {
            if (v.dimension_type === 'verification') {
                p.payments -= v.payment_count;
                p.usd -= +v.total_usd;
            }
            return p;
        },
        () => ({ payments: 0, usd: 0 })
    );

    // Active filters
    const selectedCountries = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const countryChart = echarts.init(document.getElementById('status-country-chart'), 'macarons');
    const completionGauge = echarts.init(document.getElementById('completion-gauge'), 'macarons');
    const ratesEl = document.getElementById('completion-rates-chart');
    const ratesChart = ratesEl ? echarts.init(ratesEl, 'macarons') : null;

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        countryChart.resize();
        completionGauge.resize();
        if (ratesChart) ratesChart.resize();
    });

    const pendingList = ["SENT TO PAYMENT GATEWAY", "SENT TO FSP", "PENDING"];
    const successfulList = [
        "DISTRIBUTION SUCCESSFUL",
        "PARTIALLY DISTRIBUTED",
        "TRANSACTION SUCCESSFUL",
    ].map(s => s.toUpperCase());

    // Financial rows are used only for the delivery success rate chart.
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

        updateVerificationPanel();

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

    // Payment verification figures. The card stays hidden until the completion
    // feed emits verification rows (Phase 5 query work).
    function updateVerificationPanel() {
        const card = document.getElementById('verification-card');
        if (!card) return;

        const totals = { selected: 0, verified: 0, pending: 0, discrepancies: 0 };
        verificationGroup.all().forEach(d => {
            if (!d.key) return;
            const key = String(d.key).trim().toUpperCase();
            if (key === 'SELECTED') totals.selected += d.value.payments;
            else if (key === 'VERIFIED') totals.verified += d.value.payments;
            else if (key === 'PENDING') totals.pending += d.value.payments;
            else if (key === 'DISCREPANCIES' || key === 'DISCREPANCY') totals.discrepancies += d.value.payments;
        });

        const hasData = totals.selected + totals.verified + totals.pending + totals.discrepancies > 0;
        card.classList.toggle('hidden', !hasData);
        if (!hasData) return;

        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = d3.format(',')(value);
        };
        setText('verification-selected', totals.selected);
        setText('verification-verified', totals.verified);
        setText('verification-pending', totals.pending);
        setText('verification-discrepancies', totals.discrepancies);

        const rateEl = document.getElementById('verification-rate');
        if (rateEl) {
            const rate = totals.selected > 0 ? (totals.verified / totals.selected) * 100 : 0;
            rateEl.textContent = `${rate.toFixed(1)}%`;
        }
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
                data: [gettext('Reconciled'), gettext('Pending Reconciliation')],
                top: 0,
                right: 20,
                icon: 'roundRect'
            },
            grid: {
                top: 30,
                bottom: 25,
                left: 60,
                right: 20
            },
            xAxis: {
                type: 'time',
                axisLabel: { color: '#64748b', formatter: value => d3.timeFormat('%b %y')(new Date(value)) }
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
                    color: RECONCILED_COLOR,
                    barMaxWidth: 35,
                    data: reconciledData
                },
                {
                    name: gettext('Pending Reconciliation'),
                    type: 'bar',
                    stack: 'total',
                    color: OPEN_COLOR,
                    barMaxWidth: 35,
                    data: openedData
                }
            ]
        };

        timelineChart.setOption(timelineOption, { notMerge: true });

        // 2. Stacked Country Chart (top 10): absolute values or 100% share
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

        const isShareView = countryView === 'share';
        const hasAnyCountrySelection = selectedCountries.size > 0;
        const reconciledShare = d => d.total > 0 ? (d.reconciled / d.total) * 100 : 0;

        const countrySeriesDataReconciled = countryData.map(d => {
            const isSelected = selectedCountries.has(d.key);
            const opacity = isSelected ? 1 : (hasAnyCountrySelection ? 0.35 : 1);
            return {
                value: isShareView ? reconciledShare(d) : d.reconciled,
                itemStyle: { color: RECONCILED_COLOR, opacity: opacity },
                // In share view the rate label rides on the reconciled segment;
                // in absolute view it only labels the total when open is zero
                // (otherwise the open segment carries the total label).
                label: {
                    show: isShareView || d.opened === 0,
                    position: 'top',
                    formatter: isShareView ? `${reconciledShare(d).toFixed(1)}%` : formatCompact(d.total),
                    color: '#0f172a',
                    fontWeight: 600,
                    fontSize: 10
                }
            };
        });

        const countrySeriesDataOpened = countryData.map(d => {
            const isSelected = selectedCountries.has(d.key);
            const opacity = isSelected ? 1 : (hasAnyCountrySelection ? 0.35 : 1);
            return {
                value: isShareView ? 100 - reconciledShare(d) : d.opened,
                itemStyle: { color: OPEN_COLOR, opacity: opacity },
                label: {
                    show: !isShareView && d.opened > 0,
                    position: 'top',
                    formatter: formatCompact(d.total),
                    color: '#0f172a',
                    fontWeight: 600,
                    fontSize: 10
                }
            };
        });

        countryChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: function (params) {
                    const d = countryData[params[0].dataIndex];
                    if (!d) return '';
                    let tooltipHtml = `${formatCountryName(d.key)}<br/>`;
                    if (isShareView) {
                        const pct = reconciledShare(d);
                        tooltipHtml += `${params[0].marker} ${gettext('Reconciled')}: <b>${pct.toFixed(1)}%</b> (${formatFullVal(d.reconciled)} ${unitName})<br/>`;
                        tooltipHtml += `${params[1].marker} ${gettext('Pending Reconciliation')}: <b>${(100 - pct).toFixed(1)}%</b> (${formatFullVal(d.opened)} ${unitName})<br/>`;
                        tooltipHtml += `${gettext('Total')}: ${formatFullVal(d.total)} ${unitName}`;
                    } else {
                        params.forEach(p => {
                            tooltipHtml += `${p.marker} ${p.seriesName}: <b>${formatFullVal(p.value)}</b> ${unitName}<br/>`;
                        });
                    }
                    return tooltipHtml;
                }
            },
            legend: {
                data: [gettext('Reconciled'), gettext('Pending Reconciliation')],
                top: 0,
                right: 20
            },
            grid: { top: 48, bottom: 75, left: 60, right: 20 },
            xAxis: {
                type: 'category',
                data: countryData.map(d => d.key),
                axisLabel: {
                    rotate: 30,
                    interval: 0,
                    width: 115,
                    overflow: 'truncate',
                    formatter: val => formatCountryName(val),
                    color: '#1f2937',
                    fontWeight: 500
                }
            },
            yAxis: {
                type: 'value',
                min: 0,
                max: isShareView ? 100 : null,
                axisLabel: {
                    formatter: val => isShareView ? `${val}%` : formatMetric(val),
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
                    color: RECONCILED_COLOR,
                    data: countrySeriesDataReconciled,
                    itemStyle: { borderRadius: [0, 0, 0, 0] }
                },
                {
                    name: gettext('Pending Reconciliation'),
                    type: 'bar',
                    stack: 'total',
                    barMaxWidth: 30,
                    color: OPEN_COLOR,
                    data: countrySeriesDataOpened,
                    itemStyle: { borderRadius: [4, 4, 0, 0] }
                }
            ]
        }, { notMerge: true });


        updateRatesChart();
    }

    // Reconciliation and delivery success rates by country: two bars per
    // country, sorted by reconciliation rate. The 80% dashed line is a
    // reference guide, not a threshold.
    function updateRatesChart() {
        if (!ratesChart) return;

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
                country: country,
                reconciliationRate: (rec.reconciled / totalReconciled) * 100,
                deliveryRate: (deliv.delivered / totalDelivery) * 100,
                reconciled: rec.reconciled,
                totalReconciled: totalReconciled,
                delivered: deliv.delivered,
                totalDelivery: totalDelivery
            });
        });

        // Keep the largest countries so the chart stays readable, then order
        // by reconciliation rate (category axes render bottom-up, so the
        // highest rate ends up at the top).
        const visible = points
            .sort((a, b) => b.totalReconciled - a.totalReconciled)
            .slice(0, 12)
            .sort((a, b) => a.reconciliationRate - b.reconciliationRate);

        if (visible.length === 0) {
            ratesChart.setOption({
                title: {
                    text: gettext('No country has both completion and financial data for this period.'),
                    left: 'center',
                    top: 'middle',
                    textStyle: { color: '#94a3b8', fontSize: 12, fontWeight: 400 }
                }
            }, { notMerge: true });
            return;
        }

        const rateFormatter = params => `${params.value.toFixed(1)}%`;

        ratesChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => {
                    const p = visible[params[0].dataIndex];
                    if (!p) return '';
                    return `<b>${formatCountryName(p.country)}</b><br/>` +
                        `${params[0].marker} ${gettext('Reconciliation rate')}: <b>${p.reconciliationRate.toFixed(1)}%</b> ` +
                        `(${formatFullVal(p.reconciled)} / ${formatFullVal(p.totalReconciled)})<br/>` +
                        `${params[1].marker} ${gettext('Delivery success rate')}: <b>${p.deliveryRate.toFixed(1)}%</b> ` +
                        `(${formatFullVal(p.delivered)} / ${formatFullVal(p.totalDelivery)})`;
                }
            },
            legend: {
                data: [gettext('Reconciliation rate'), gettext('Delivery success rate')],
                top: 0,
                right: 20
            },
            grid: { top: 38, right: 70, bottom: 30, left: 140 },
            xAxis: {
                type: 'value',
                min: 0,
                max: 100,
                axisLabel: { formatter: '{value}%', color: '#64748b' },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: visible.map(p => formatCountryName(p.country)),
                axisLabel: {
                    color: '#1f2937',
                    fontWeight: 500,
                    fontSize: 10,
                    lineHeight: 11,
                    width: 130,
                    overflow: 'break'
                },
                axisTick: { show: false },
                axisLine: { lineStyle: { color: '#e2e8f0' } }
            },
            series: [
                {
                    name: gettext('Reconciliation rate'),
                    type: 'bar',
                    barMaxWidth: 10,
                    barGap: '20%',
                    itemStyle: { color: RECONCILED_COLOR, borderRadius: [0, 3, 3, 0] },
                    data: visible.map(p => p.reconciliationRate),
                    label: {
                        show: true,
                        position: 'right',
                        distance: 4,
                        formatter: rateFormatter,
                        color: '#0f172a',
                        fontWeight: 600,
                        fontSize: 10
                    },
                    markLine: {
                        silent: true,
                        symbol: 'none',
                        lineStyle: { type: 'dashed', color: '#cbd5e1' },
                        label: {
                            formatter: gettext('80% reference'),
                            position: 'insideEndTop',
                            rotate: 0,
                            color: '#94a3b8',
                            fontSize: 10
                        },
                        data: [{ xAxis: 80 }]
                    }
                },
                {
                    name: gettext('Delivery success rate'),
                    type: 'bar',
                    barMaxWidth: 10,
                    itemStyle: { color: DELIVERY_COLOR, borderRadius: [0, 3, 3, 0] },
                    data: visible.map(p => p.deliveryRate),
                    label: {
                        show: true,
                        position: 'right',
                        distance: 4,
                        formatter: rateFormatter,
                        color: '#475569',
                        fontWeight: 600,
                        fontSize: 10
                    }
                }
            ]
        }, { notMerge: true });
    }

    async function loadFinancialForRates(from, to) {
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
            console.error('Error loading financial data for the delivery success rate:', error);
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
                if (openedTitle) openedTitle.textContent = gettext('Pending Reconciliation amount (USD)');
                if (timelineTitle) timelineTitle.textContent = gettext('Reconciliation timeline (USD)');
                if (countryTitle) countryTitle.textContent = gettext('Reconciliation status by country (USD)');
            } else {
                if (reconciledTitle) reconciledTitle.textContent = gettext('Reconciled payments');
                if (openedTitle) openedTitle.textContent = gettext('Pending Reconciliation payments');
                if (timelineTitle) timelineTitle.textContent = gettext('Reconciliation timeline');
                if (countryTitle) countryTitle.textContent = gettext('Reconciliation status by country');
            }


            updateAll();
        });
    });

    // Country chart view toggle: absolute values or 100% stacked shares
    const countryViewTabs = document.querySelectorAll('.country-view-tab');
    countryViewTabs.forEach(btn => {
        btn.addEventListener('click', function() {
            countryView = this.id === 'country-view-share' ? 'share' : 'absolute';
            countryViewTabs.forEach(b => {
                b.classList.remove('bg-white', 'shadow', 'text-blue-800');
                b.classList.add('text-gray-600');
            });
            this.classList.add('bg-white', 'shadow', 'text-blue-800');
            this.classList.remove('text-gray-600');
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
            countryDimension.filterAll();
            verificationDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(data);
            if (chartHelpers.setDataAsOf) chartHelpers.setDataAsOf(data);

            await loadFinancialForRates(from, to);

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
