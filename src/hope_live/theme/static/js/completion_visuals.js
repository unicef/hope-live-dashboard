document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Set modern D3 color scheme to avoid d3.schemeCategory20c deprecation warning
    dc.config.defaultColors(d3.schemeCategory10);

    let ndx = crossfilter([]);
    const dataCache = {};

    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : 'N/A');
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'status';

    const moveDays = dateDimension.group(d3.timeDay);
    const moveMonths = dateDimension.group(d3.timeMonth);
    const paymentsByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0);
    const paymentsByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0);
    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.payment_count : 0);
    const sectorStatusGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.payment_count : 0);
    const countryStatusGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0);

    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const statusPieChart = dc.pieChart('#reconciliation-pie-chart');
    const sectorChart = dc.rowChart('#status-sector-chart');
    const countryChart = dc.rowChart('#status-country-chart');

    // Set initial domain to prevent grid line errors
    const initialYear = new Date().getFullYear();
    const initialDomain = [new Date(initialYear, 0, 1), new Date(initialYear, 11, 31)];

    focusChart.width(null).height(200).margins({ top: 10, right: 50, bottom: 30, left: 90 })
        .dimension(dateDimension).group(paymentsByMonthGroup)
        .curve(d3.curveMonotoneX).transitionDuration(500)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeMonth.round).xUnits(d3.timeMonths).elasticY(true)
        .renderHorizontalGridLines(true).rangeChart(rangeChart).brushOn(false).renderArea(true)
        .title(function(d) {
            const formatTime = d3.timeFormat("%B %Y");
            const formatValue = d3.format(",");
            return `${formatTime(d.key)}: ${formatValue(d.value)}`;
        })
        .on('filtered', updateTotals);

    focusChart.yAxis().tickFormat(d => d3.format(".2s")(d).replace('G', 'B'));

    rangeChart.width(null).height(60).margins({ top: 0, right: 50, bottom: 20, left: 90 })
        .dimension(dateDimension).group(paymentsByDayGroup).centerBar(true).gap(2)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeDay.round).alwaysUseRounding(true).xUnits(d3.timeDays).elasticY(true)
        .filterPrinter(function (filters) {
            const dateFmt = d3.timeFormat("%b %d, %Y");
            return `[${dateFmt(filters[0][0])} to ${dateFmt(filters[0][1])}]`;
        })
        .yAxis().ticks(0);

    statusPieChart.width(300).height(300).radius(100).innerRadius(40)
        .dimension(statusDimension).group(statusGroup)
        .label(d => `${d.key}: ${d.value}`).on('filtered', updateTotals);

    sectorChart.width(null).height(450).margins({ top: 10, right: 30, bottom: 30, left: 180 })
        .dimension(sectorDimension).group(sectorStatusGroup).elasticX(true).gap(10)
        .data(group => group.all().filter(d => d.key !== 'N/A' && d.value > 0))
        .on('filtered', updateTotals);
    sectorChart.xAxis().ticks(4).tickFormat(d3.format(".2s"));

    countryChart.width(null).height(450).margins({ top: 10, right: 30, bottom: 30, left: 180 })
        .dimension(countryDimension).group(countryStatusGroup).elasticX(true).gap(10)
        .data(group => group.top(15))
        .on('filtered', updateTotals);
    countryChart.xAxis().ticks(4).tickFormat(d3.format(".2s"));

    function updateTotals() {
        const reconciliationData = statusGroup.all();
        let reconciled = 0;
        let opened = 0;

        reconciliationData.forEach(d => {
            if (d.key === null) return;
            const key = d.key.toUpperCase();
            if (key.includes('RECONCILED') || key.includes('PAID')) {
                reconciled += d.value;
            } else if (key.includes('OPEN') || key.includes('PENDING')) {
                opened += d.value;
            }
        });

        document.getElementById('total-reconciled').textContent = d3.format(',')(reconciled);
        document.getElementById('total-opened').textContent = d3.format(',')(opened);
    }

    async function loadData(year, isInitial = false) {
        try {
            let data;

            if (dataCache[year]) {
                data = dataCache[year];
            } else {
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

                data = await response.json();

                const dateFormat = d3.timeParse('%Y-%m-%d');
                data.forEach(d => {
                    d.date = dateFormat(d.date);
                    d.total_usd = +d.total_usd;
                    d.payment_count = +d.payment_count;
                });

                dataCache[year] = data;
            }

            const now = new Date();
            now.setHours(23, 59, 59, 999);
            const currentData = data.filter(d => d.date <= now);

            ndx.remove();
            ndx.add(currentData);

            const yearDomain = [new Date(year, 0, 1), new Date(year, 11, 31)];
            focusChart.x(d3.scaleTime().domain(yearDomain));
            rangeChart.x(d3.scaleTime().domain(yearDomain));

            // Use renderAll on initial load, redrawAll for updates
            if (isInitial) {
                dc.renderAll();
            } else {
                dc.redrawAll();
            }
            updateTotals();
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
        loadData(firstYear, true);  // Pass true for initial load
    }

    window.addEventListener('resize', function () {
        focusChart.rescale();
        rangeChart.rescale();
        dc.renderAll();
    });
});
