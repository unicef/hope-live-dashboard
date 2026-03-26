document.addEventListener('DOMContentLoaded', function () {
    const dataElement = document.getElementById('dashboard-data');
    if (!dataElement) return;

    const rawData = JSON.parse(dataElement.textContent);

    // Format the data
    const dateFormatSpecifier = '%Y-%m-%d';
    const dateFormat = d3.timeParse(dateFormatSpecifier);

    rawData.forEach(function (d) {
        d.date = dateFormat(d.date);
        d.total_beneficiaries = +d.total_beneficiaries;
        d.total_children = +d.total_children;
        d.total_pwd = +d.total_pwd;
    });

    // Create the Crossfilter instance
    const ndx = crossfilter(rawData);

    // Dimensions
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    // Filter helper
    const primaryDimFilter = d => d.dimension_type === 'sector';

    // Groups
    // Timeline: Individuals over time
    const moveMonths = dateDimension.group(d3.timeMonth);
    const individualsByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);

    // Sector Groups
    const sectorIndividualsGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_beneficiaries : 0);
    const sectorChildrenGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_children : 0);

    // Country Groups
    const countryIndividualsGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const countryPwdGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_pwd : 0);

    // Charts
    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const sectorIndividualsChart = dc.rowChart('#sector-individuals-chart');
    const sectorChildrenChart = dc.rowChart('#sector-children-chart');
    const countryIndividualsChart = dc.rowChart('#country-individuals-chart');
    const countryPwdChart = dc.rowChart('#country-pwd-chart');

    const fullDomain = d3.extent(rawData, d => d.date);

    // Timeline Configuration (Focus)
    focusChart
        .width(null)
        .height(200)
        .margins({ top: 10, right: 50, bottom: 30, left: 60 })
        .dimension(dateDimension)
        .group(individualsByMonthGroup)
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
        .group(individualsByMonthGroup)
        .centerBar(true)
        .gap(1)
        .x(d3.scaleTime().domain(fullDomain))
        .round(d3.timeMonth.round)
        .xUnits(d3.timeMonths)
        .yAxis().ticks(0);


    // Sector Individuals
    sectorIndividualsChart
        .width(null).height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(sectorDimension)
        .group(sectorIndividualsGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', updateTotals);

    // Sector Children
    sectorChildrenChart
        .width(null).height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(sectorDimension)
        .group(sectorChildrenGroup)
        .elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .colors(['#2C96D2']) // UNICEF Primary Blue
        .on('filtered', updateTotals);

    // Country Individuals
    countryIndividualsChart
        .width(null).height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(countryDimension)
        .group(countryIndividualsGroup)
        .elasticX(true)
        .data(group => group.top(10))
        .on('filtered', updateTotals);

    // Country PWD
    countryPwdChart
        .width(null).height(300)
        .margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(countryDimension)
        .group(countryPwdGroup)
        .elasticX(true)
        .data(group => group.top(10))
        .colors(['#9333ea']) // Purple
        .on('filtered', updateTotals);

    function updateTotals() {
        const totalIndividuals = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0).value();
        const totalChildren = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_children : 0).value();
        const totalPwd = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_pwd : 0).value();

        document.getElementById('total-individuals').textContent = d3.format(',')(totalIndividuals);
        document.getElementById('total-children').textContent = d3.format(',')(totalChildren);
        document.getElementById('total-pwd').textContent = d3.format(',')(totalPwd);
    }

    dc.renderAll();
    updateTotals();

    window.addEventListener('resize', function () {
        focusChart.rescale();
        rangeChart.rescale();
        dc.renderAll();
    });

});
