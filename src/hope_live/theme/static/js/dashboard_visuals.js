document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Set modern D3 color scheme to avoid d3.schemeCategory20c deprecation warning
    dc.config.defaultColors(d3.schemeCategory10);

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);
    const dataCache = {};
    let all = ndx.groupAll();

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    // One shared dimension – dimension_value is the key for all row charts
    const valueDimension = ndx.dimension(d => d.dimension_value);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'sector';

    // Groups
    const moveDays = dateDimension.group(d3.timeDay);
    const moveMonths = dateDimension.group(d3.timeMonth);
    const volumeByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const volumeByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const sectorGroup = valueDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_usd : 0);
    const programGroup = valueDimension.group().reduceSum(d => d.dimension_type === 'program' ? d.total_usd : 0);
    const deliveryGroup = valueDimension.group().reduceSum(d => d.dimension_type === 'delivery_type' ? d.total_usd : 0);
    const fspGroup = valueDimension.group().reduceSum(d => d.dimension_type === 'financial_service_provider' ? d.total_usd : 0);
    const countryGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const regionGroup = valueDimension.group().reduceSum(d => d.dimension_type === 'region' ? d.total_usd : 0);

    // Charts
    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const sectorChart = dc.rowChart('#sector-chart');
    const programChart = dc.rowChart('#program-chart');
    const deliveryChart = dc.rowChart('#delivery-chart');
    const fspChart = dc.rowChart('#fsp-chart');
    const countryChart = dc.rowChart('#country-chart');
    const regionChart = dc.rowChart('#region-chart');

    // Set initial domain to prevent grid line errors
    const initialYear = new Date().getFullYear();
    const initialDomain = [new Date(initialYear, 0, 1), new Date(initialYear, 11, 31)];

    // Chart configurations (keep your existing setup)
    focusChart
        .width(null).height(300)
        .margins({ top: 10, right: 50, bottom: 30, left: 90 })
        .dimension(dateDimension)
        .group(volumeByMonthGroup)
        .curve(d3.curveMonotoneX)
        .transitionDuration(500)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeMonth.round)
        .xUnits(d3.timeMonths)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .rangeChart(rangeChart)
        .brushOn(false)
        .renderArea(true)
        .title(function(d) {
            const formatTime = d3.timeFormat("%B %Y");
            const formatValue = d3.format(",.2f");
            return `${formatTime(d.key)}: $${formatValue(d.value)}`;
        })
        .on('filtered', updateTotals);

    focusChart.yAxis().tickFormat(d => '$' + d3.format(".2s")(d).replace('G', 'B'));
    focusChart.xAxis().ticks(d3.timeMonth.every(1));  // Show one label per month

    rangeChart
        .width(null).height(80)
        .margins({ top: 0, right: 50, bottom: 20, left: 90 })
        .dimension(dateDimension)
        .group(volumeByDayGroup)
        .centerBar(true)
        .gap(2)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeDay.round)
        .alwaysUseRounding(true)
        .xUnits(d3.timeDays)
        .elasticY(true)
        .filterPrinter(function (filters) {
            const dateFmt = d3.timeFormat("%b %d, %Y");
            return `[${dateFmt(filters[0][0])} to ${dateFmt(filters[0][1])}]`;
        })
        .yAxis().ticks(0);

    const rowChartMargins = { top: 10, right: 30, bottom: 30, left: 20 };

    // 1. Assign dimensions and groups FIRST
    sectorChart.dimension(valueDimension).group(sectorGroup);
    programChart.dimension(valueDimension).group(programGroup);
    deliveryChart.dimension(valueDimension).group(deliveryGroup);
    fspChart.dimension(valueDimension).group(fspGroup);
    countryChart.dimension(countryDimension).group(countryGroup);
    regionChart.dimension(valueDimension).group(regionGroup);

    // 2. Apply common configurations
    [countryChart, programChart, fspChart].forEach(chart => {
        chart.width(null).height(850).margins(rowChartMargins).elasticX(true).gap(2).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(d => '$' + d3.format(".2s")(d).replace('G', 'B'));
    });

    [deliveryChart, regionChart].forEach(chart => {
        chart.width(null).height(400).margins(rowChartMargins).elasticX(true).gap(2).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(d => '$' + d3.format(".2s")(d).replace('G', 'B'));
    });

    sectorChart.width(null).height(400).margins(rowChartMargins).elasticX(true).gap(4).on('filtered', updateTotals);
    sectorChart.xAxis().ticks(3).tickFormat(d => '$' + d3.format(".2s")(d).replace('G', 'B'));

    // 3. Apply specific data filters AFTER groups are set
    sectorChart.data(group => group.top(15).filter(d => d.key !== null && d.value > 0));
    deliveryChart.data(group => group.top(15).filter(d => d.key !== null && d.value > 0));
    countryChart.data(group => group.all().filter(d => d.key !== null && d.value > 0));
    regionChart.data(group => group.top(10).filter(d => d.key !== null && d.value > 0));

    programChart.data(group => group.top(25).filter(d => d.key !== null && d.value > 0));
    fspChart.data(group => group.top(25).filter(d => d.key !== null && d.value > 0));

    const pendingList = ["Sent to Payment Gateway", "Sent to FSP", "Pending"];
    const successfulList = [
        "Distribution Successful",
        "Partially Distributed",
        "Transaction Successful",
    ];

    function updateTotals() {
        const totalPayments = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0).value();

        const totalPaid = ndx.groupAll().reduceSum(d =>
            (d.dimension_type === 'status' && successfulList.includes(d.dimension_value)) ? d.total_usd : 0
        ).value();

        const totalOutstanding = ndx.groupAll().reduceSum(d =>
            (d.dimension_type === 'status' && pendingList.includes(d.dimension_value)) ? d.total_usd : 0
        ).value();

        const paymentsEl = document.getElementById('total-payments');
        if (paymentsEl) paymentsEl.textContent = d3.format(',')(totalPayments);

        const paidEl = document.getElementById('total-amount-paid');
        if (paidEl) paidEl.textContent = '$' + d3.format(',.2f')(totalPaid);

        const outEl = document.getElementById('outstanding-payments');
        if (outEl) outEl.textContent = '$' + d3.format(',.2f')(totalOutstanding);
    }

    async function loadData(year, isInitial = false) {
        try {
            let data;

            // Check cache first
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

                // No time_grain filter – the backend decides what to send
                const dateFormat = d3.timeParse('%Y-%m-%d');
                data.forEach(d => {
                    d.date = dateFormat(d.date);
                    d.total_usd = +d.total_usd;
                    d.payment_count = +d.payment_count;
                });

                dataCache[year] = data;  // Store in cache
            }

            const now = new Date();
            now.setHours(23, 59, 59, 999);
            const currentData = data.filter(d => d.date <= now);

            ndx.remove();
            ndx.add(currentData);

            const yearDomain = [new Date(year, 0, 1), new Date(year, 11, 31)];
            focusChart.x(d3.scaleTime().domain(yearDomain));
            rangeChart.x(d3.scaleTime().domain(yearDomain));

            if (isInitial) {
                dc.renderAll();
            } else {
                dc.redrawAll();
            }
            updateTotals();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    // Tab switching
    tabsContainer.querySelectorAll('.year-tab').forEach(btn => {
        btn.addEventListener('click', function() {
            tabsContainer.querySelectorAll('.year-tab').forEach(b =>
                b.classList.remove('bg-white', 'shadow', 'text-blue-600', 'active-tab'));
            this.classList.add('bg-white', 'shadow', 'text-blue-600', 'active-tab');
            loadData(this.dataset.year);
        });
    });

    // Initial load
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
