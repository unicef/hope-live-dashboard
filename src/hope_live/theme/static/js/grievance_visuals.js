document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Set modern D3 color scheme
    dc.config.defaultColors(d3.schemeCategory10);

    let ndx = crossfilter([]);
    const dataCache = {};

    // Dimensions from user spec
    const dateDimension = ndx.dimension(d => d.date);
    const statusDimension = ndx.dimension(d => d.dimension_type === 'status' ? d.dimension_value : null);
    const categoryDimension = ndx.dimension(d => d.dimension_type === 'category' ? d.dimension_value : null);
    const issueTypeDimension = ndx.dimension(d => d.dimension_type === 'issue_type' ? d.dimension_value : null);
    const priorityDimension = ndx.dimension(d => d.dimension_type === 'priority' ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    const primaryDimFilter = d => d.dimension_type === 'category'; // Arbitrarily chosen for total counts

    // Groups
    const moveDays = dateDimension.group(d3.timeDay);
    const moveMonths = dateDimension.group(d3.timeMonth);
    const ticketsByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0);
    const ticketsByMonthGroup = moveMonths.reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0);

    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.ticket_count : 0);
    const categoryGroup = categoryDimension.group().reduceSum(d => d.dimension_type === 'category' ? d.ticket_count : 0);
    const issueTypeGroup = issueTypeDimension.group().reduceSum(d => d.dimension_type === 'issue_type' ? d.ticket_count : 0);
    const priorityGroup = priorityDimension.group().reduceSum(d => d.dimension_type === 'priority' ? d.ticket_count : 0);
    const countryGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0);

    // Charts
    const focusChart = dc.lineChart('#time-focus-chart');
    const rangeChart = dc.barChart('#time-range-chart');
    const statusChart = dc.pieChart('#grievance-status-chart');
    const categoryChart = dc.rowChart('#grievance-category-chart');
    const issueTypeChart = dc.rowChart('#grievance-issue-type-chart');
    const priorityChart = dc.pieChart('#grievance-priority-chart');
    const countryChart = dc.rowChart('#grievance-country-chart');

    // Set initial domain
    const initialYear = new Date().getFullYear();
    const initialDomain = [new Date(initialYear, 0, 1), new Date(initialYear, 11, 31)];

    focusChart.width(null).height(200).margins({ top: 10, right: 50, bottom: 30, left: 90 })
        .dimension(dateDimension).group(ticketsByMonthGroup)
        .transitionDuration(500)
        .x(d3.scaleTime().domain(initialDomain))
        .round(d3.timeMonth.round).xUnits(d3.timeMonths).elasticY(true)
        .renderArea(true)
        .curve(d3.curveMonotoneX)
        .mouseZoomable(true)
        .renderHorizontalGridLines(true).rangeChart(rangeChart).brushOn(false)
        .title(function(d) {
            const formatTime = d3.timeFormat("%B %Y");
            const formatValue = d3.format(",");
            return `${formatTime(d.key)}: ${formatValue(d.value)}`;
        })
        .on('filtered', updateTotals);

    focusChart.yAxis().tickFormat(d => d3.format(".2s")(d).replace('G', 'B'));


    rangeChart.width(null).height(60).margins({ top: 0, right: 50, bottom: 20, left: 90 })
        .dimension(dateDimension).group(ticketsByDayGroup).centerBar(true).gap(2)
        .x(d3.scaleTime().domain(initialDomain))
        .round(d3.timeDay.round).alwaysUseRounding(true).xUnits(d3.timeDays).elasticY(true)
        .filterPrinter(function (filters) {
            const dateFmt = d3.timeFormat("%b %d, %Y");
            return `[${dateFmt(filters[0][0])} to ${dateFmt(filters[0][1])}]`;
        })
        .yAxis().ticks(0);

    statusChart.width(300).height(300).radius(100).innerRadius(40)
        .dimension(statusDimension).group(statusGroup)
        .label(d => `${d.key}: ${d.value}`).on('filtered', updateTotals);

    priorityChart.width(300).height(300).radius(100).innerRadius(40)
        .dimension(priorityDimension).group(priorityGroup)
        .label(d => `${d.key}: ${d.value}`).on('filtered', updateTotals);

    const rowChartMargins = { top: 10, right: 30, bottom: 30, left: 180 };

    [categoryChart, issueTypeChart, countryChart].forEach(chart => {
        chart.width(null).height(450).margins(rowChartMargins).elasticX(true).gap(10).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(d3.format(".2s"));
    });

    categoryChart.dimension(categoryDimension).group(categoryGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    issueTypeChart.dimension(issueTypeDimension).group(issueTypeGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    countryChart.dimension(countryDimension).group(countryGroup).data(group => group.top(15));

    function updateTotals() {
        const totalTickets = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.ticket_count : 0).value();
        const totalTicketsElement = document.getElementById('total-tickets');
        if (totalTicketsElement) {
            totalTicketsElement.textContent = d3.format(',')(totalTickets);
        }
    }

    async function loadData(year, isInitial = false) {
        try {
            let data;

            if (dataCache[year]) {
                data = dataCache[year];
            } else {
                const url = `${window.DASHBOARD_CONFIG.endpoint}?year=${year}&dashboard=grievance`;
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
                    d.ticket_count = +d.ticket_count;
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
            console.error('Error loading grievance data:', error);
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
        loadData(firstYear, true);
    }

    window.addEventListener('resize', function () {
        focusChart.rescale();
        rangeChart.rescale();
        dc.renderAll();
    });
});
