document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Set modern D3 color scheme to avoid d3.schemeCategory20c deprecation warning
    dc.config.defaultColors(d3.schemeCategory10);

    let ndx = crossfilter([]);
    const dataCache = {};

    const dateDimension = ndx.dimension(d => d.date);
    const primaryDimFilter = d => String(d.dimension_type).toLowerCase() === 'sector';
    const sectorDimension = ndx.dimension(d => primaryDimFilter(d) ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const moveDays = dateDimension.group(d3.timeDay);
    const moveMonths = dateDimension.group(d3.timeMonth);
    const individualsByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const individualsByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const sectorIndividualsGroup = sectorDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const sectorChildrenGroup = sectorDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_children : 0);
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

    focusChart.width(null).height(200).margins({ top: 10, right: 50, bottom: 30, left: 90 })
        .dimension(dateDimension).group(individualsByMonthGroup)
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
        .dimension(dateDimension).group(individualsByDayGroup).centerBar(true).gap(2)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeDay.round).alwaysUseRounding(true).xUnits(d3.timeDays).elasticY(true)
        .filterPrinter(function (filters) {
            const dateFmt = d3.timeFormat("%b %d, %Y");
            return `[${dateFmt(filters[0][0])} to ${dateFmt(filters[0][1])}]`;
        })
        .yAxis().ticks(0);

    const demoMargins = { top: 10, right: 30, bottom: 30, left: 20 };

    [sectorIndividualsChart, sectorChildrenChart, countryIndividualsChart, countryPwdChart].forEach(chart => {
        chart.width(null).height(350).margins(demoMargins).elasticX(true).gap(10).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(d3.format(".2s"));
    });

    sectorIndividualsChart.dimension(sectorDimension).group(sectorIndividualsGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    sectorChildrenChart.dimension(sectorDimension).group(sectorChildrenGroup).colors(['#2C96D2']).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    countryIndividualsChart.dimension(countryDimension).group(countryIndividualsGroup).data(group => group.top(10));
    countryPwdChart.dimension(countryDimension).group(countryPwdGroup).colors(['#9333ea']).data(group => group.top(10));

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
                    d.total_beneficiaries = +d.total_beneficiaries;
                    d.total_children = +d.total_children;
                    d.total_pwd = +d.total_pwd;
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
