function remove_empty_bins(source_group) {
    return {
        all: function () {
            return source_group.all().filter(d => d.key !== '' && d.key !== null && d.value > 0);
        }
    };
}

document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Set modern D3 color scheme to avoid d3.schemeCategory20c deprecation warning
    dc.config.defaultColors(d3.schemeCategory10);

    const usdFormat = d => {
        if (Math.abs(d) < 1) return '$0';
        return '$' + d3.format(".2s")(d).replace('G', 'B');
    };

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);
    const dataCache = {};
    let all = ndx.groupAll();

    // Separate Dimensions for each chart to allow cross-filtering
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
    const moveMonths = dateDimension.group(d3.timeMonth);
    const volumeByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const volumeByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const sectorGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_usd : 0);
    const programGroup = programDimension.group().reduceSum(d => d.dimension_type === 'program' ? d.total_usd : 0);
    const deliveryGroup = deliveryDimension.group().reduceSum(d => d.dimension_type === 'delivery_type' ? d.total_usd : 0);
    const fspGroup = fspDimension.group().reduceSum(d => d.dimension_type === 'financial_service_provider' ? d.total_usd : 0);
    const countryGroup = countryDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_usd : 0);
    const regionGroup = regionDimension.group().reduceSum(d => d.dimension_type === 'region' ? d.total_usd : 0);
    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.total_usd : 0);

    // Charts
    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const sectorChart = dc.rowChart('#sector-chart').dimension(sectorDimension).group(remove_empty_bins(sectorGroup));
    const programChart = dc.rowChart('#program-chart').dimension(programDimension).group(remove_empty_bins(programGroup));
    const deliveryChart = dc.rowChart('#delivery-chart').dimension(deliveryDimension).group(remove_empty_bins(deliveryGroup));
    const fspChart = dc.rowChart('#fsp-chart').dimension(fspDimension).group(remove_empty_bins(fspGroup));
    const countryChart = dc.barChart('#country-chart')
        .dimension(countryDimension)
        .group(remove_empty_bins(countryGroup))
        .width(null)
        .height(400)
        .margins({ top: 20, right: 20, bottom: 80, left: 80 })
        .x(d3.scaleBand())
        .xUnits(dc.units.ordinal)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .brushOn(false)
        .barPadding(0.4)
        .on('filtered', updateTotals);
    const regionChart = dc.rowChart('#region-chart').dimension(regionDimension).group(remove_empty_bins(regionGroup));

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

    focusChart.yAxis().tickFormat(usdFormat);
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


    // 2. Apply common configurations
    [programChart, fspChart].forEach(chart => {
        chart.width(null).height(850).margins(rowChartMargins).elasticX(true).gap(2).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(usdFormat);
    });

    [deliveryChart, regionChart].forEach(chart => {
        chart.width(null).height(400).margins(rowChartMargins).elasticX(true).gap(2).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(usdFormat);
    });

    sectorChart.width(null).height(400).margins(rowChartMargins).elasticX(true).gap(4).on('filtered', updateTotals);
    sectorChart.xAxis().ticks(3).tickFormat(usdFormat);

    countryChart.yAxis().tickFormat(usdFormat);

    // Rotate labels so they don't overlap
    countryChart.on('renderlet', function(chart) {
        chart.selectAll('g.x text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end');
    });

    // 3. (No longer needed – remove_empty_bins handles filtering)

    const pendingList = ["Sent to Payment Gateway", "Sent to FSP", "Pending"].map(s => s.toUpperCase());
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

                // (No need to filter by time_grain – the API now does this)

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
