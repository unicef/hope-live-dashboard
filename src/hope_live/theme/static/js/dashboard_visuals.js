document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);
    let all = ndx.groupAll();

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
    const statusGroup = statusDimension.group().reduceSum(d => d.dimension_type === 'status' ? d.total_usd : 0);
    const currencyGroup = currencyDimension.group().reduceSum(d => d.dimension_type === 'currency' ? d.total_usd : 0);
    const countryGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0);
    const adminGroup = adminDimension.group().reduceSum(d => d.dimension_type === 'admin_area' ? d.total_usd : 0);
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

    rangeChart
        .width(null).height(80)
        .margins({ top: 0, right: 50, bottom: 20, left: 90 })
        .dimension(dateDimension)
        .group(volumeByDayGroup)
        .centerBar(true)
        .gap(2)
        .x(d3.scaleTime().domain(initialDomain))  // Set initial scale
        .round(d3.timeDay.round)
        .xUnits(d3.timeDays)
        .filterPrinter(function (filters) {
            const dateFmt = d3.timeFormat("%b %d, %Y");
            return `[${dateFmt(filters[0][0])} to ${dateFmt(filters[0][1])}]`;
        })
        .yAxis().ticks(0);

    const rowChartMargins = { top: 10, right: 30, bottom: 30, left: 180 };

    [adminChart, programChart, fspChart].forEach(chart => {
        chart.width(null).height(750).margins(rowChartMargins).elasticX(true).gap(5).data(group => group.top(30)).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(d => '$' + d3.format(".2s")(d).replace('G', 'B'));
    });

    [sectorChart, deliveryChart, statusChart, currencyChart, countryChart, regionChart].forEach(chart => {
        chart.width(null).height(400).margins(rowChartMargins).elasticX(true).gap(10).on('filtered', updateTotals);
        chart.xAxis().ticks(4).tickFormat(d => '$' + d3.format(".2s")(d).replace('G', 'B'));
    });

    sectorChart.dimension(sectorDimension).group(sectorGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    countryChart.dimension(countryDimension).group(countryGroup).data(group => group.top(10));
    adminChart.dimension(adminDimension).group(adminGroup);
    programChart.dimension(programDimension).group(programGroup);
    deliveryChart.dimension(deliveryDimension).group(deliveryGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    fspChart.dimension(fspDimension).group(fspGroup);
    statusChart.dimension(statusDimension).group(statusGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    currencyChart.dimension(currencyDimension).group(currencyGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0));
    regionChart.dimension(regionDimension).group(regionGroup).data(group => group.all().filter(d => d.key !== null && d.value > 0).slice(0, 10));

    function updateTotals() {
        const totalUsd = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_usd : 0).value();
        const totalPayments = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.payment_count : 0).value();

        document.getElementById('total-disbursed').textContent = '$' + d3.format(',.2f')(totalUsd);
        document.getElementById('total-payments').textContent = d3.format(',')(totalPayments);
        // Removed total-individuals as per your requirement
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
                d.total_usd = +d.total_usd;
                d.payment_count = +d.payment_count;
            });

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
