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
        d.total_beneficiaries = +d.total_beneficiaries;
    });

    // Create the Crossfilter instance
    const ndx = crossfilter(rawData);
    const all = ndx.groupAll();

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : null);
    const programDimension = ndx.dimension(d => d.dimension_type === 'program' ? d.dimension_value : null);
    const deliveryDimension = ndx.dimension(d => d.dimension_type === 'delivery_type' ? d.dimension_value : null);
    const fspDimension = ndx.dimension(d => d.dimension_type === 'financial_service_provider' ? d.dimension_value : null);
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : null);
    const currencyDimension = ndx.dimension(d => d.dimension_type === 'currency' ? d.dimension_value : null);

    const countryDimension = ndx.dimension(d => d.country_slug);
    const adminDimension = ndx.dimension(d => d.dimension_type === 'admin_area' ? d.dimension_value : null);
    const regionDimension = ndx.dimension(d => d.dimension_type === 'region' ? d.dimension_value : null);


    // Filter helper: To avoid double counting in global aggregates,
    // we should only consider one dimension type for totals.
    const primaryDimFilter = d => d.dimension_type === 'sector';

    // Groups
    // For the timeline, we only want to sum values once per underlying transaction.
    // We use a fake group to apply the primary dimension filter.
    function filteredGroup(group, filter) {
        return {
            all: function () {
                return group.all().filter(function (d) {
                    return filter(d);
                });
            },
            top: function (n) {
                return group.top(Infinity).filter(function (d) {
                    return filter(d);
                }).slice(0, n);
            }
        };
    }

    // Spending over time
    const moveMonths = dateDimension.group(d3.timeMonth);
    const volumeByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);

    // Sector Group (only values where type is sector)
    const sectorGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_usd : 0);
    const programGroup = programDimension.group().reduceSum(d => d.dimension_type === 'program' ? d.total_usd : 0);
    const deliveryGroup = deliveryDimension.group().reduceSum(d => d.dimension_type === 'delivery_type' ? d.total_usd : 0);
    const fspGroup = fspDimension.group().reduceSum(d => d.dimension_type === 'financial_service_provider' ? d.total_usd : 0);
    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.total_usd : 0);
    const currencyGroup = currencyDimension.group().reduceSum(d => d.dimension_type === 'currency' ? d.total_usd : 0);


    // Country Group (using primary dim records to avoid double counting)
    const countryGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);

    // Admin Group
    const adminGroup = adminDimension.group().reduceSum(d => d.dimension_type === 'admin_area' ? d.total_usd : 0);

    // Region Group
    const regionGroup = regionDimension.group().reduceSum(d => d.dimension_type === 'region' ? d.total_usd : 0);

    // Charts
    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const sectorChart = dc.rowChart('#sector-chart');
    const programChart = dc.rowChart('#program-chart');
    const deliveryChart = dc.rowChart('#delivery-chart');
    const fspChart = dc.rowChart('#fsp-chart');
    const statusChart = dc.rowChart('#status-chart');
    const currencyChart = dc.rowChart('#currency-chart');

    const countryChart = dc.rowChart('#country-chart');
    const adminChart = dc.rowChart('#admin-chart');
    const regionChart = dc.rowChart('#region-chart');

    const fullDomain = d3.extent(rawData, d => d.date);

    // Focus Chart Configuration
    focusChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 50, bottom: 30, left: 60 })
        .dimension(dateDimension)
        .group(volumeByMonthGroup)
        .transitionDuration(500)
        .x(d3.scaleTime().domain(fullDomain))
        .round(d3.timeMonth.round)
        .xUnits(d3.timeMonths)
        .elasticY(true)
        .renderHorizontalGridLines(true)
        .rangeChart(rangeChart)
        .brushOn(false)
        .renderArea(true)
        .on('filtered', function (chart, filter) {
            updateTotals();
        });

    // Range Chart Configuration
    rangeChart
        .width(null)
        .height(80)
        .margins({ top: 0, right: 50, bottom: 20, left: 60 })
        .dimension(dateDimension)
        .group(volumeByMonthGroup)
        .centerBar(true)
        .gap(1)
        .x(d3.scaleTime().domain(fullDomain))
        .round(d3.timeMonth.round)
        .xUnits(d3.timeMonths)
        .yAxis().ticks(0);


    // Sector Chart Configuration
    sectorChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(sectorDimension)
        .group(sectorGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', updateTotals);

    // Country Chart Configuration
    countryChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(countryDimension)
        .group(countryGroup)
        .elasticX(true)
        .data(group => group.top(10))
        .on('filtered', updateTotals);

    // Admin Chart Configuration
    adminChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(adminDimension)
        .group(adminGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0).slice(0, 10))
        .on('filtered', updateTotals);

    // Program Chart Configuration
    programChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(programDimension)
        .group(programGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', function (chart, filter) {
            updateTotals();
        });

    // Delivery Type Chart Configuration
    deliveryChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(deliveryDimension)
        .group(deliveryGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', function (chart, filter) {
            updateTotals();
        });

    // FSP Chart Configuration
    fspChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(fspDimension)
        .group(fspGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', function (chart, filter) {
            updateTotals();
        });

    // Status Chart Configuration
    statusChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(statusDimension)
        .group(statusGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', function (chart, filter) {
            updateTotals();
        });

    // Currency Chart Configuration
    currencyChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(currencyDimension)
        .group(currencyGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', function (chart, filter) {
            updateTotals();
        });


    // Region Chart Configuration
    regionChart
        .width(null)
        .height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(regionDimension)
        .group(regionGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0).slice(0, 10))
        .on('filtered', function (chart, filter) {
            updateTotals();
        });

    // Function to update the summary cards
    function updateTotals() {
        const totalUsd = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0).value();
        const totalPayments = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0).value();
        const totalIndividuals = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0).value();

        document.getElementById('total-disbursed').textContent = '$' + d3.format(',.2f')(totalUsd);
        document.getElementById('total-payments').textContent = d3.format(',')(totalPayments);
        document.getElementById('total-individuals').textContent = d3.format(',')(totalIndividuals);
    }

    // Initial render
    dc.renderAll();
    updateTotals();

    // Handle window resize
    window.addEventListener('resize', function () {
        focusChart.rescale();
        rangeChart.rescale();
        dc.renderAll();
    });

});
