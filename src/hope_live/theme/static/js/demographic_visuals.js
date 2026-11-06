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

    // Initialize empty Crossfilter
    let ndx = crossfilter([]);

    // Filter and Dimensions
    const primaryDimFilter = d => d.dimension_type === 'sector';
    const dateDimension = ndx.dimension(d => d.date);
    const sectorDimension = ndx.dimension(d => primaryDimFilter(d) ? d.dimension_value : '');
    const countryDimension = ndx.dimension(d => d.country_slug);
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


    // Active Filters Sets
    const selectedSectors = new Set();
    const selectedCountries = new Set();

    // Initialize ECharts instances with macarons theme
    const timelineChart = echarts.init(document.getElementById('time-focus-chart'), 'macarons');
    const sectorChildChart = echarts.init(document.getElementById('sector-children-chart'), 'macarons');
    const countryPwdChart = echarts.init(document.getElementById('country-pwd-chart'), 'macarons');

    // Resize Handler
    window.addEventListener('resize', function () {
        timelineChart.resize();
        sectorChildChart.resize();
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
                axisLabel: { color: '#64748b', formatter: value => d3.timeFormat('%b %Y')(new Date(value)) }
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

        // 3. Country Distribution Chart (Donut, top 10)
        const countryData = countryGroup.all()
            .map(d => ({ key: d.key, value: d.value[activeField] }))
            .filter(d => d.key !== null && d.value > 0)
            .sort((a, b) => b.value - a.value)
            .slice(0, 10);

        const hasAnyCountrySelection = selectedCountries.size > 0;
        const countryDonutData = countryData.map(d => {
            const stableColor = getStableColor(d.key);
            const isSelected = selectedCountries.has(d.key);
            return {
                name: d.key,
                value: d.value,
                itemStyle: {
                    color: isSelected ? stableColor : (hasAnyCountrySelection ? '#cbd5e1' : stableColor)
                }
            };
        }).filter(d => d.value > 0);

        countryPwdChart.setOption({
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
                data: countryDonutData
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
