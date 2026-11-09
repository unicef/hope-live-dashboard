document.addEventListener('DOMContentLoaded', function () {
    const timeFilterContainer = document.getElementById('time-filter-container');
    if (!timeFilterContainer) return;

    let currentMetric = 'individuals'; // Default metric: individuals. Can be: 'individuals', 'households', 'children', 'pwd'
    let activeCohort = 'ALL'; // Programme cohort filter: 'ALL', 'STANDARD' or 'SOCIAL'

    const fieldMap = {
        individuals: 'beneficiaries',
        households: 'households',
        children: 'children',
        pwd: 'pwd'
    };

    const labelMap = {
        individuals: gettext('Individuals reached'),
        households: gettext('Households reached'),
        children: gettext('Children reached'),
        pwd: gettext('Persons with disabilities reached')
    };

    const chartHelpers = window.HopeChart || {};
    const getStableColor = chartHelpers.getStableColor || (() => '#5470c6');
    const formatCountry = chartHelpers.formatCountryName || (value => value);

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Filter and Dimensions
    const primaryDimFilter = d => d.dimension_type === 'sector';
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => primaryDimFilter(d) ? d.dimension_value : '');
    const countryDimension = ndx.dimension(d => d.country_slug);
    const regionDimension = ndx.dimension(d => d.dimension_type === 'region' ? d.dimension_value : '');
    const programTypeDimension = ndx.dimension(d => d.program_type || 'STANDARD');

    function applyCohortFilter() {
        if (activeCohort === 'ALL') {
            programTypeDimension.filterAll();
        } else {
            programTypeDimension.filterFunction(d => d === activeCohort);
        }
    }

    // Multi-metric custom reduction helper
    function reduceDemographics(dimType) {
        return {
            add: (p, v) => {
                if (v.dimension_type === dimType) {
                    p.beneficiaries += +v.total_beneficiaries;
                    p.households += +v.total_households;
                    p.children += +v.total_children;
                    p.pwd += +v.total_pwd;
                }
                return p;
            },
            remove: (p, v) => {
                if (v.dimension_type === dimType) {
                    p.beneficiaries -= +v.total_beneficiaries;
                    p.households -= +v.total_households;
                    p.children -= +v.total_children;
                    p.pwd -= +v.total_pwd;
                }
                return p;
            },
            init: () => ({ beneficiaries: 0, households: 0, children: 0, pwd: 0 })
        };
    }

    // Groups
    const moveMonths = dateDimension.group(d3.timeMonth);
    const volumeByMonthGroup = moveMonths.reduce(
        (p, v) => {
            if (primaryDimFilter(v)) {
                p.beneficiaries += +v.total_beneficiaries;
                p.households += +v.total_households;
                p.children += +v.total_children;
                p.pwd += +v.total_pwd;
            }
            return p;
        },
        (p, v) => {
            if (primaryDimFilter(v)) {
                p.beneficiaries -= +v.total_beneficiaries;
                p.households -= +v.total_households;
                p.children -= +v.total_children;
                p.pwd -= +v.total_pwd;
            }
            return p;
        },
        () => ({ beneficiaries: 0, households: 0, children: 0, pwd: 0 })
    );

    const sectorGroup = sectorDimension.group().reduce(
        reduceDemographics('sector').add,
        reduceDemographics('sector').remove,
        reduceDemographics('sector').init
    );

    const countryGroup = countryDimension.group().reduce(
        reduceDemographics('sector').add,
        reduceDemographics('sector').remove,
        reduceDemographics('sector').init
    );

    const regionGroup = regionDimension.group().reduce(
        reduceDemographics('region').add,
        reduceDemographics('region').remove,
        reduceDemographics('region').init
    );


    // Active Filters Sets
    const selectedSectors = new Set();
    const selectedCountries = new Set();
    const countryFilter = chartHelpers.initCountryFilter({
        dimension: countryDimension,
        onChange: value => {
            selectedCountries.clear();
            if (value) selectedCountries.add(value);
            updateAll();
        }
    });


    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const sectorChildChart = echarts.init(document.getElementById('sector-children-chart'), 'macarons');
    const countryPwdChart = echarts.init(document.getElementById('country-pwd-chart'), 'macarons');
    const regionShareChart = echarts.init(document.getElementById('region-share-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        sectorChildChart.resize();
        countryPwdChart.resize();
        regionShareChart.resize();
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

    function updateAll() {
        updateTotals();

        const activeField = fieldMap[currentMetric];
        const activeLabel = labelMap[currentMetric];

        // 1. Timeline Chart (Area / Time Axis with linear gradient and smooth curves)
        const timelineData = volumeByMonthGroup.all()
            .filter(d => d.key !== null)
            .map(d => [d.key.getTime(), d.value[activeField]]);

        const timelineOption = {
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const date = new Date(params[0].value[0]);
                    const formattedDate = d3.timeFormat("%B %d, %Y")(date);
                    const formattedValue = d3.format(",")(params[0].value[1]);
                    return `${formattedDate}<br/><b>${formattedValue}</b> ${activeLabel.toLowerCase()}`;
                }
            },
            grid: {
                top: 15,
                bottom: 25,
                left: 60,
                right: 20
            },
            xAxis: {
                type: 'time',
                axisLabel: { color: '#64748b', formatter: value => d3.timeFormat('%b %y')(new Date(value)) }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    formatter: val => d3.format(".2s")(val).replace('G', 'B'),
                    color: '#64748b'
                },
                splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
            },
            series: [{
                name: activeLabel,
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

        timelineChart.setOption(timelineOption, { notMerge: true });

        // 2. Sector Distribution Chart (Donut with outside labels)
        const sectorData = sectorGroup.all().filter(d => d.key !== '' && d.key !== null && d.value.beneficiaries > 0);

        const hasAnySectorSelection = selectedSectors.size > 0;
        const sectorDonutData = sectorData.map(d => {
            const stableColor = getStableColor(d.key);
            const isSelected = selectedSectors.has(d.key);
            return {
                name: d.key,
                value: d.value[activeField],
                itemStyle: {
                    color: isSelected ? stableColor : (hasAnySectorSelection ? '#cbd5e1' : stableColor)
                }
            };
        }).filter(d => d.value > 0);

        sectorChildChart.setOption({
            tooltip: {
                trigger: 'item',
                formatter: '{b}: <b>{c}</b> ({d}%)'
            },
            series: [{
                type: 'pie',
                radius: ['45%', '70%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
                label: { show: true, position: 'outside', formatter: params => `${params.name}\n${d3.format(',')(params.value)} (${params.percent}%)`, fontSize: 11, color: '#374151' },
                labelLine: { show: true, length: 15, length2: 10, smooth: false },
                emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
                data: sectorDonutData
            }]
        }, { notMerge: true });

        // 3. Country share (horizontal bars, top 10 + Other)
        const allCountryData = countryGroup.all()
            .map(d => ({ key: d.key, value: d.value[activeField] }))
            .filter(d => d.key && d.value > 0)
            .sort((a, b) => b.value - a.value);
        const countryTotal = allCountryData.reduce((sum, d) => sum + d.value, 0);
        const countryBars = allCountryData.slice(0, 10).map(d => ({ ...d, name: formatCountry(d.key) }));
        const otherCountryValue = allCountryData.slice(10).reduce((sum, d) => sum + d.value, 0);
        if (otherCountryValue > 0) {
            countryBars.push({ key: gettext('Other'), name: gettext('Other'), value: otherCountryValue, isOther: true });
        }
        const countryShare = value => countryTotal > 0 ? (value / countryTotal) * 100 : 0;
        const hasAnyCountrySelection = selectedCountries.size > 0;

        countryPwdChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => {
                    const d = params[0].data;
                    return `${d.name}: <b>${d3.format(',')(d.value)}</b> (${countryShare(d.value).toFixed(1)}%)`;
                }
            },
            grid: { top: 15, bottom: 20, left: 170, right: 110 },
            xAxis: {
                type: 'value',
                axisLabel: { formatter: val => d3.format('.2s')(val).replace('G', 'B'), color: '#64748b', fontSize: 10 },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: countryBars.map(d => d.name),
                inverse: true,
                axisTick: { show: false },
                axisLine: { show: true, lineStyle: { color: '#f1f5f9' } },
                axisLabel: { width: 155, overflow: 'truncate', color: '#374151', fontSize: 10 }
            },
            series: [{
                type: 'bar',
                data: countryBars.map(d => {
                    const isSelected = selectedCountries.has(d.key);
                    const baseColor = d.isOther ? '#cbd5e1' : getStableColor(d.key);
                    return {
                        name: d.name,
                        value: d.value,
                        slug: d.key,
                        isOther: !!d.isOther,
                        itemStyle: {
                            color: isSelected ? getStableColor(d.key) : (hasAnyCountrySelection && !d.isOther ? '#cbd5e1' : baseColor)
                        }
                    };
                }),
                barMaxWidth: 20,
                showBackground: true,
                backgroundStyle: { color: 'rgba(241, 245, 249, 0.75)', borderRadius: [0, 4, 4, 0] },
                itemStyle: { borderRadius: [0, 4, 4, 0] },
                label: {
                    show: true,
                    position: 'right',
                    distance: 6,
                    formatter: params => {
                        const value = +params.value || 0;
                        return `${d3.format(',')(value)} (${countryShare(value).toFixed(1)}%)`;
                    },
                    color: '#0f172a',
                    fontWeight: 600,
                    fontSize: 10
                }
            }]
        }, { notMerge: true });

        // 4. Region share (horizontal bars with count + percentage)
        const regionData = regionGroup.all()
            .map(d => ({ key: d.key, value: d.value[activeField] }))
            .filter(d => d.key && d.value > 0)
            .sort((a, b) => b.value - a.value);
        const regionTotal = regionData.reduce((sum, d) => sum + d.value, 0);
        const regionShare = value => regionTotal > 0 ? (value / regionTotal) * 100 : 0;

        regionShareChart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                formatter: params => {
                    const value = +params[0].value || 0;
                    return `${params[0].name}: <b>${d3.format(',')(value)}</b> (${regionShare(value).toFixed(1)}%)`;
                }
            },
            grid: { top: 15, bottom: 25, left: 180, right: 110 },
            xAxis: {
                type: 'value',
                axisLabel: { formatter: val => d3.format('.2s')(val).replace('G', 'B'), color: '#64748b', fontSize: 10 },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            yAxis: {
                type: 'category',
                data: regionData.map(d => d.key),
                inverse: true,
                axisTick: { show: false },
                axisLine: { show: true, lineStyle: { color: '#f1f5f9' } },
                axisLabel: { width: 160, overflow: 'truncate', color: '#374151', fontSize: 10 }
            },
            series: [{
                type: 'bar',
                data: regionData.map(d => ({
                    value: d.value,
                    itemStyle: {
                        color: chartHelpers.getRegionColor ? chartHelpers.getRegionColor(d.key) : getStableColor(d.key)
                    }
                })),
                barMaxWidth: 22,
                showBackground: true,
                backgroundStyle: { color: 'rgba(241, 245, 249, 0.75)', borderRadius: [0, 4, 4, 0] },
                itemStyle: { borderRadius: [0, 4, 4, 0] },
                label: {
                    show: true,
                    position: 'right',
                    distance: 6,
                    formatter: params => {
                        const value = +params.value || 0;
                        return `${d3.format(',')(value)} (${regionShare(value).toFixed(1)}%)`;
                    },
                    color: '#0f172a',
                    fontWeight: 600,
                    fontSize: 10
                }
            }]
        }, { notMerge: true });

    }

    // --- Interactive Filters Bindings ---

    // Timeline Zoom
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

    sectorChildChart.on('click', handleSectorClick);

    // Country Filter Selection Toggle
    const handleCountryClick = function (params) {
        const countryName = (params.data && params.data.slug) || params.name;
        if (!countryName || (params.data && params.data.isOther)) return;
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

    countryPwdChart.on('click', handleCountryClick);

    const metricTabs = document.querySelectorAll('.metric-tab');

    function setActiveMetricTab(metric) {
        metricTabs.forEach(b => {
            b.classList.remove('bg-white', 'shadow', 'text-blue-800', 'active-metric');
            b.classList.add('text-gray-600');
        });
        const tab = document.getElementById(`btn-${metric}`);
        if (tab) {
            tab.classList.add('bg-white', 'shadow', 'text-blue-800', 'active-metric');
            tab.classList.remove('text-gray-600');
        }
    }

    function refreshMetricTitles() {
        const activeLabel = labelMap[currentMetric];

        const timelineTitle = document.getElementById('timeline-title');
        if (timelineTitle) timelineTitle.textContent = `${activeLabel} ${gettext('Timeline')}`;

        const sectorShareTitle = document.getElementById('sector-share-title');
        if (sectorShareTitle) sectorShareTitle.textContent = `${gettext('Sector share of')} ${activeLabel}`;

        const countryShareTitle = document.getElementById('country-share-title');
        if (countryShareTitle) countryShareTitle.textContent = `${gettext('Country share of')} ${activeLabel}`;

    }

    metricTabs.forEach(btn => {
        btn.addEventListener('click', function() {
            currentMetric = this.dataset.metric;
            setActiveMetricTab(currentMetric);
            refreshMetricTitles();
            updateAll();
        });
    });

    // Cohort tab selection (All / Standard / Social workers)
    const cohortTabs = document.querySelectorAll('.cohort-tab');
    // Household-level demographics are not collected for social-worker programmes.
    const SOCIAL_HIDDEN_METRICS = ['households', 'children', 'pwd'];

    function applyCohortUI() {
        const isSocial = activeCohort === 'SOCIAL';

        SOCIAL_HIDDEN_METRICS.forEach(metric => {
            const btn = document.getElementById(`btn-${metric}`);
            if (btn) btn.style.display = isSocial ? 'none' : '';
            const card = document.getElementById(`card-${metric}`);
            if (card) card.style.display = isSocial ? 'none' : '';
        });

        labelMap.individuals = isSocial ? gettext('Workers reached') : gettext('Individuals reached');

        const individualsTab = document.getElementById('btn-individuals');
        if (individualsTab) individualsTab.textContent = isSocial ? gettext('Workers') : gettext('Individuals');

        const cardTitle = document.getElementById('individuals-card-title');
        if (cardTitle) cardTitle.textContent = labelMap.individuals;

        if (isSocial && SOCIAL_HIDDEN_METRICS.includes(currentMetric)) {
            currentMetric = 'individuals';
            setActiveMetricTab(currentMetric);
        }
        refreshMetricTitles();
    }

    cohortTabs.forEach(btn => {
        btn.addEventListener('click', function () {
            cohortTabs.forEach(b => {
                b.classList.remove('bg-white', 'shadow', 'text-blue-800');
                b.classList.add('text-gray-600');
            });
            this.classList.add('bg-white', 'shadow', 'text-blue-800');
            this.classList.remove('text-gray-600');
            activeCohort = this.dataset.cohort || 'ALL';
            applyCohortFilter();
            applyCohortUI();
            updateAll();
        });
    });

    // --- Load Data ---
    async function loadRange(startDate, endDate) {
        try {
            const from = timeFilter.formatDateStr(startDate);
            const to = timeFilter.formatDateStr(endDate);
            const url = `${window.DASHBOARD_CONFIG.endpoint}?date_from=${from}&date_to=${to}&dashboard=${window.DASHBOARD_CONFIG.type}&time_grain=monthly`;
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
                d.program_type = d.program_type || 'STANDARD';
            });

            // Clean existing state and filters (clear filters FIRST, then remove old data)
            selectedSectors.clear();
            selectedCountries.clear();
            sectorDimension.filterAll();
            countryDimension.filterAll();
            dateDimension.filterAll();

            ndx.remove();
            ndx.add(data);
            countryFilter.populate(data);
            countryFilter.apply();
            selectedCountries.clear();
            if (countryFilter.value) selectedCountries.add(countryFilter.value);
            if (chartHelpers.setDataAsOf) chartHelpers.setDataAsOf(data);
            applyCohortFilter();

            timeFilter.setBuffer(startDate, endDate);
            updateAll();
        } catch (error) {
            console.error('Error loading demographic data:', error);
        }
    }

    // --- Time Filter Controller ---
    const timeFilter = new DashboardTimeFilter({
        onFilterChange: (startDate, endDate) => {
            if (timeFilter.isWithinBuffer(startDate, endDate)) {
                dateDimension.filterRange([startDate, endDate]);
                updateAll();
            } else {
                loadRange(startDate, endDate);
            }
        }
    });

    loadRange(timeFilter.currentRange.start, timeFilter.currentRange.end);
});
