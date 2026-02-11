document.addEventListener('DOMContentLoaded', function () {
    const dataElement = document.getElementById('dashboard-data');
    if (!dataElement) return;

    const rawData = JSON.parse(dataElement.textContent);

    // Format the data
    const dateFormatSpecifier = '%Y-%m-%d';
    const dateFormat = d3.timeParse(dateFormatSpecifier);

    rawData.forEach(function (d) {
        d.date = dateFormat(d.date);
        d.total_usd = +d.total_usd;
        d.payment_count = +d.payment_count;
    });

    // Create the Crossfilter instance
    const ndx = crossfilter(rawData);

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : 'N/A');
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    // Filter helper
    const primaryDimFilter = d => d.dimension_type === 'status';

    // Groups
    // Timeline: Total payments over time
    const moveMonths = dateDimension.group(d3.timeMonth);
    const paymentsByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0);

    // Status Pie Group
    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.payment_count : 0);

    // Sector-Status Stacked Group (using helper to simplify)
    // For simplicity, we'll just show status distribution in row charts
    const sectorStatusGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.payment_count : 0);
    const countryStatusGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0);

    // Charts
    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const statusPieChart = dc.pieChart('#reconciliation-pie-chart');
    const sectorChart = dc.rowChart('#status-sector-chart');
    const countryChart = dc.rowChart('#status-country-chart');

    const fullDomain = d3.extent(rawData, d => d.date);

    // Timeline Configuration (Focus)
    focusChart
        .width(null)
        .height(200)
        .margins({ top: 10, right: 50, bottom: 30, left: 60 })
        .dimension(dateDimension)
        .group(paymentsByMonthGroup)
        .transitionDuration(500)
        .x(d3.scaleTime().domain(fullDomain))
        .round(d3.timeMonth.round)
        .xUnits(d3.timeMonths)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .rangeChart(rangeChart)
        .brushOn(false)
        .renderArea(true)
        .on('filtered', updateTotals);

    // Timeline Configuration (Range)
    rangeChart
        .width(null)
        .height(60)
        .margins({ top: 0, right: 50, bottom: 20, left: 60 })
        .dimension(dateDimension)
        .group(paymentsByMonthGroup)
        .centerBar(true)
        .gap(1)
        .x(d3.scaleTime().domain(fullDomain))
        .round(d3.timeMonth.round)
        .xUnits(d3.timeMonths)
        .yAxis().ticks(0);


    // Status Pie
    statusPieChart
        .width(300).height(300)
        .radius(100)
        .innerRadius(40)
        .dimension(statusDimension)
        .group(statusGroup)
        .label(d => `${d.key}: ${d.value}`)
        .on('filtered', updateTotals);

    // Status by Sector
    sectorChart
        .width(null).height(400)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(sectorDimension)
        .group(sectorStatusGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== 'N/A' && d.value > 0))
        .on('filtered', updateTotals);

    // Status by Country
    countryChart
        .width(null).height(400)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(countryDimension)
        .group(countryStatusGroup)
        .elasticX(true)
        .data(group => group.top(15))
        .on('filtered', updateTotals);

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

    dc.renderAll();
    updateTotals();

    window.addEventListener('resize', function () {
        focusChart.rescale();
        rangeChart.rescale();
        dc.renderAll();
    });

});
