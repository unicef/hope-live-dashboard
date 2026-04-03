document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    let ndx = crossfilter([]);

    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => d.dimension_type === 'sector' ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'sector';

    const moveMonths = dateDimension.group(d3.timeMonth);
    const individualsByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const sectorIndividualsGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_beneficiaries : 0);
    const sectorChildrenGroup = sectorDimension.group().reduceSum(d => d.dimension_type === 'sector' ? d.total_children : 0);
    const countryIndividualsGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const countryPwdGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_pwd : 0);

    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const sectorIndividualsChart = dc.rowChart('#sector-individuals-chart');
    const sectorChildrenChart = dc.rowChart('#sector-children-chart');
    const countryIndividualsChart = dc.rowChart('#country-individuals-chart');
    const countryPwdChart = dc.rowChart('#country-pwd-chart');

    // Set initial domain to prevent grid line errors
    const initialYear = new Date().getFullYear();
    const initialDomain = [new Date(initialYear, 0, 1), new Date(initialYear, 11, 31)];

    focusChart.width(null).height(200).margins({ top: 10, right: 50, bottom: 30, left: 60 })
        .dimension(dateDimension).group(individualsByMonthGroup).transitionDuration(500)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeMonth.round).xUnits(d3.timeMonths).elasticY(true)
        .renderHorizontalGridLines(true).rangeChart(rangeChart).brushOn(false).renderArea(true)
        .on('filtered', updateTotals);

    rangeChart.width(null).height(60).margins({ top: 0, right: 50, bottom: 20, left: 60 })
        .dimension(dateDimension).group(individualsByMonthGroup).centerBar(true).gap(1)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeMonth.round).xUnits(d3.timeMonths).yAxis().ticks(0);

    sectorIndividualsChart.width(null).height(300).margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(sectorDimension).group(sectorIndividualsGroup).elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0))
        .on('filtered', updateTotals);

    sectorChildrenChart.width(null).height(300).margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(sectorDimension).group(sectorChildrenGroup).elasticX(true)
        .data(group => group.all().filter(d => d.key !== null && d.value > 0)).colors(['#2C96D2'])
        .on('filtered', updateTotals);

    countryIndividualsChart.width(null).height(300).margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(countryDimension).group(countryIndividualsGroup).elasticX(true)
        .data(group => group.top(10)).on('filtered', updateTotals);

    countryPwdChart.width(null).height(300).margins({ top: 10, right: 10, bottom: 30, left: 10 })
        .dimension(countryDimension).group(countryPwdGroup).elasticX(true)
        .data(group => group.top(10)).colors(['#9333ea'])
        .on('filtered', updateTotals);

    function updateTotals() {
        const totalIndividuals = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0).value();
        const totalChildren = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_children : 0).value();
        const totalPwd = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_pwd : 0).value();

        document.getElementById('total-individuals').textContent = d3.format(',')(totalIndividuals);
        document.getElementById('total-children').textContent = d3.format(',')(totalChildren);
        document.getElementById('total-pwd').textContent = d3.format(',')(totalPwd);
    }

    async function loadData(year, isInitial = false) {
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

            const dateFormat = d3.timeParse('%Y-%m-%d');
            data.forEach(d => {
                d.date = dateFormat(d.date);
                d.total_beneficiaries = +d.total_beneficiaries;
                d.total_children = +d.total_children;
                d.total_pwd = +d.total_pwd;
            });

            ndx.remove();
            ndx.add(data);

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
            console.error('Error loading demographic data:', error);
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
