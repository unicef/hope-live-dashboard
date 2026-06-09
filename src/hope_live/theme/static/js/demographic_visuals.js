document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.getElementById('tabs-container');
    if (!tabsContainer) return;

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Filter and Dimensions
    const primaryDimFilter = d => d.dimension_type === 'sector';
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => primaryDimFilter(d) ? d.dimension_value : null);
    const countryDimension = ndx.dimension(d => d.country_slug);

    // Groups
    const moveDays = dateDimension.group(d3.timeDay);
    const individualsByDayGroup = moveDays.reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const sectorIndividualsGroup = sectorDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const sectorChildrenGroup = sectorDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_children : 0);
    const countryIndividualsGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0);
    const countryPwdGroup = countryDimension.group().reduceSum(d => primaryDimFilter(d) ? d.total_pwd : 0);

    // Active Filters Sets
    const selectedSectors = new Set();
    const selectedCountries = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const sectorIndChart = echarts.init(document.getElementById('sector-individuals-chart'), 'macarons');
    const sectorChildChart = echarts.init(document.getElementById('sector-children-chart'), 'macarons');
    const countryIndChart = echarts.init(document.getElementById('country-individuals-chart'), 'macarons');
    const countryPwdChart = echarts.init(document.getElementById('country-pwd-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        sectorIndChart.resize();
        sectorChildChart.resize();
        countryIndChart.resize();
        countryPwdChart.resize();
    });

    function updateTotals() {
        const totalIndividuals = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_beneficiaries : 0).value();
        const totalChildren = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_children : 0).value();
        const totalPwd = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_pwd : 0).value();
        const totalHouseholds = ndx.groupAll().reduceSum(d => primaryDimFilter(d) ? d.total_households : 0).value();

        document.getElementById('total-individuals').textContent = d3.format(',')(totalIndividuals);
        document.getElementById('total-children').textContent = d3.format(',')(totalChildren);
        document.getElementById('total-pwd').textContent = d3.format(',')(totalPwd);
        document.getElementById('total-households').textContent = d3.format(',')(totalHouseholds);
    }

    function updateAll(filterSource = null) {
        updateTotals();

        // 1. Timeline Chart (Area / Time Axis with linear gradient and smooth curves)
        const timelineData = individualsByDayGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %d, %Y")(date);
                    const formattedValue = d3.format(",")(params[0].value[1]);
                    return `${formattedDate}<br/><b>${formattedValue}</b> individuals`;
                }
            },
            grid: {
                top: 20,
                bottom: 80,
                left: 60,
                right: 30
            },
            xAxis: {
                type: 'time',
                axisLabel: {
                    color: '#64748b'
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: function (val) {
                        return d3.format(".2s")(val).replace('G', 'B');
                    },
                    color: '#64748b'
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed',
                        color: '#f1f5f9'
                    }
                }
            },
            series: [{
                name: 'Individuals Reached',
                type: 'line',
                smooth: true,
                symbol: 'none',
                lineStyle: {
                    color: '#2ec7c9',
                    width: 2.5
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(46, 199, 201, 0.4)' },
                        { offset: 1, color: 'rgba(46, 199, 201, 0.02)' }
                    ])
                },
                data: timelineData
            }]
        };

        if (filterSource !== 'timeline') {
            timelineOption.dataZoom = [
                {
                    type: 'inside',
                    start: 0,
                    end: 100
                },
                {
                    show: true,
                    type: 'slider',
                    start: 0,
                    end: 100,
                    bottom: 10,
                    textStyle: {
                        color: '#64748b'
                    }
                }
            ];
            timelineChart.setOption(timelineOption, { notMerge: true });
        } else {
            timelineChart.setOption(timelineOption);
        }

        // 2. Sector Individuals Chart (Horizontal bar)
        const secIndData = sectorIndividualsGroup.all().filter(d => d.key !== null && d.value > 0);
        secIndData.sort((a, b) => b.value - a.value);

        const hasAnySectorSelection = selectedSectors.size > 0;
        const secIndSeriesData = secIndData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedSectors.has(d.key)
                    ? '#2ec7c9'
                    : (hasAnySectorSelection ? '#cbd5e1' : '#2ec7c9')
            }
        }));

        sectorIndChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>`
            },
            grid: { top: 20, bottom: 30, left: 140, right: 30 },
            xAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: secIndData.map(d => d.key),
                inverse: true,
                axisLabel: { color: '#1f2937', fontWeight: 500 }
            },
            series: [{
                type: 'bar',
                data: secIndSeriesData,
                barMaxWidth: 25,
                itemStyle: { borderRadius: [0, 4, 4, 0] }
            }]
        });

        // 3. Sector Children Chart (Horizontal bar)
        const secChildData = sectorChildrenGroup.all().filter(d => d.key !== null && d.value > 0);
        secChildData.sort((a, b) => b.value - a.value);

        const secChildSeriesData = secChildData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedSectors.has(d.key)
                    ? '#5ab1ef'
                    : (hasAnySectorSelection ? '#cbd5e1' : '#5ab1ef')
            }
        }));

        sectorChildChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>`
            },
            grid: { top: 20, bottom: 30, left: 140, right: 30 },
            xAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: secChildData.map(d => d.key),
                inverse: true,
                axisLabel: { color: '#1f2937', fontWeight: 500 }
            },
            series: [{
                type: 'bar',
                data: secChildSeriesData,
                barMaxWidth: 25,
                itemStyle: { borderRadius: [0, 4, 4, 0] }
            }]
        });

        // 4. Country Individuals Chart (Vertical bar)
        const countryIndData = countryIndividualsGroup.all()
            .filter(d => d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 15);

        const hasAnyCountrySelection = selectedCountries.size > 0;
        const countryIndSeriesData = countryIndData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedCountries.has(d.key)
                    ? '#2ec7c9'
                    : (hasAnyCountrySelection ? '#cbd5e1' : '#2ec7c9')
            }
        }));

        countryIndChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>`
            },
            grid: { top: 30, bottom: 95, left: 70, right: 20 },
            xAxis: {
                type: 'category',
                data: countryIndData.map(d => d.key),
                axisLabel: {
                    rotate: 30,
                    interval: 0,
                    color: '#1f2937',
                    fontWeight: 500
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            series: [{
                type: 'bar',
                data: countryIndSeriesData,
                barMaxWidth: 30,
                itemStyle: { borderRadius: [4, 4, 0, 0] }
            }]
        });

        // 5. Country PWD Chart (Vertical bar)
        const countryPwdData = countryPwdGroup.all()
            .filter(d => d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 15);

        const countryPwdSeriesData = countryPwdData.map(d => ({
            name: d.key,
            value: d.value,
            itemStyle: {
                color: selectedCountries.has(d.key)
                    ? '#b6a2de'
                    : (hasAnyCountrySelection ? '#cbd5e1' : '#b6a2de')
            }
        }));

        countryPwdChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => `${params[0].name}: <b>${d3.format(",")(params[0].value)}</b>`
            },
            grid: { top: 30, bottom: 95, left: 70, right: 20 },
            xAxis: {
                type: 'category',
                data: countryPwdData.map(d => d.key),
                axisLabel: {
                    rotate: 30,
                    interval: 0,
                    color: '#1f2937',
                    fontWeight: 500
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            series: [{
                type: 'bar',
                data: countryPwdSeriesData,
                barMaxWidth: 30,
                itemStyle: { borderRadius: [4, 4, 0, 0] }
            }]
        });
    }

    // --- Interactive Filters Bindings ---

    // Timeline Zoom
    timelineChart.on('datazoom', function (params) {
        const option = timelineChart.getOption();
        const startVal = option.dataZoom[0].startValue;
        const endVal = option.dataZoom[0].endValue;

        if (startVal !== undefined && endVal !== undefined) {
            const startDate = new Date(startVal);
            const endDate = new Date(endVal);
            dateDimension.filterRange([startDate, endDate]);
            updateAll('timeline');
        }
    });

    // Sector Filter Selection Toggle
    const handleSectorClick = function (params) {
        const sectorName = params.name;
        if (selectedSectors.has(sectorName)) {
            selectedSectors.delete(sectorName);
        } else {
            selectedSectors.add(sectorName);
        }

        if (selectedSectors.size === 0) {
            sectorDimension.filterAll();
        } else {
            sectorDimension.filterFunction(d => selectedSectors.has(d));
        }
        updateAll();
    };

    sectorIndChart.on('click', handleSectorClick);
    sectorChildChart.on('click', handleSectorClick);

    // Country Filter Selection Toggle
    const handleCountryClick = function (params) {
        const countryName = params.name;
        if (selectedCountries.has(countryName)) {
            selectedCountries.delete(countryName);
        } else {
            selectedCountries.add(countryName);
        }

        if (selectedCountries.size === 0) {
            countryDimension.filterAll();
        } else {
            countryDimension.filterFunction(d => selectedCountries.has(d));
        }
        updateAll();
    };

    countryIndChart.on('click', handleCountryClick);
    countryPwdChart.on('click', handleCountryClick);

    // --- Load Data ---
    async function loadData(year) {
        try {
            const url = `${window.DASHBOARD_CONFIG.endpoint}?year=${year}&dashboard=${window.DASHBOARD_CONFIG.type}&time_grain=daily`;
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
                d.total_households = +d.total_households || 0;
            });

            const now = new Date();
            now.setHours(23, 59, 59, 999);
            const currentData = data.filter(d => d.date <= now);

            // Clean existing state and filters (clear filters FIRST, then remove old data)
            selectedSectors.clear();
            selectedCountries.clear();
            sectorDimension.filterAll();
            countryDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(currentData);

            updateAll();
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
        loadData(firstYear);
    }
});
