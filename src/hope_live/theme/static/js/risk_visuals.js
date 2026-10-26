document.addEventListener('DOMContentLoaded', function () {
    const timeFilterContainer = document.getElementById('time-filter-container');
    if (!timeFilterContainer) return;

    const severityLabels = {
        critical: gettext('Critical'),
        warning: gettext('Warning'),
        caution: gettext('Caution'),
        normal: gettext('Normal')
    };
    const trendLabels = {
        up: gettext('Increasing'),
        down: gettext('Decreasing'),
        neutral: gettext('Neutral')
    };

    const moduleMeta = {
        payment: {
            label: gettext('Payment Operations'),
            subtitle: gettext('Payment, Reconciliation & Verification bottlenecks'),
            icon: '💳',
            barColor: '#10b981',
            badgeBg: 'bg-emerald-100 text-emerald-800'
        },
        payments: {
            label: gettext('Payment Operations'),
            subtitle: gettext('Payment, Reconciliation & Verification bottlenecks'),
            icon: '💳',
            barColor: '#10b981',
            badgeBg: 'bg-emerald-100 text-emerald-800'
        },
        registration: {
            label: gettext('Registration & Population'),
            subtitle: gettext('KYC, Identity documents & Geographic verification'),
            icon: '📝',
            barColor: '#3b82f6',
            badgeBg: 'bg-blue-100 text-blue-800'
        },
        deduplication: {
            label: gettext('Deduplication & Adjudication'),
            subtitle: gettext('Biometric, Needs-Adjudication & Cross-channel duplicate issues'),
            icon: '🔍',
            barColor: '#a855f7',
            badgeBg: 'bg-purple-100 text-purple-800'
        },
        verification: {
            label: gettext('Payment Verification'),
            subtitle: gettext('PVP execution, overdue tickets & high failure rates'),
            icon: '✅',
            barColor: '#f97316',
            badgeBg: 'bg-orange-100 text-orange-800'
        },
        grievance: {
            label: gettext('Grievances & Safeguarding'),
            subtitle: gettext('Sensitive complaints, zero-reporting & FSP concentrations'),
            icon: '📣',
            barColor: '#ef4444',
            badgeBg: 'bg-red-100 text-red-800'
        },
        grievances: {
            label: gettext('Grievances & Safeguarding'),
            subtitle: gettext('Sensitive complaints, zero-reporting & FSP concentrations'),
            icon: '📣',
            barColor: '#ef4444',
            badgeBg: 'bg-red-100 text-red-800'
        },
        targeting: {
            label: gettext('Targeting & Eligibility'),
            subtitle: gettext('Vulnerability criteria & payment readiness anomalies'),
            icon: '🎯',
            barColor: '#f59e0b',
            badgeBg: 'bg-amber-100 text-amber-800'
        }
    };

    let currentCategory = 'all';
    let currentProgram = 'all';
    let currentCountry = 'all';
    let selectedModule = null;

    let ndx = crossfilter([]);

    const dateDimension = ndx.dimension(d => d.date);
    const moduleDimension = ndx.dimension(d => d.module);
    const severityDimension = ndx.dimension(d => d.severity);
    const trendDimension = ndx.dimension(d => d.trend);
    const countryDimension = ndx.dimension(d => d.country_slug);
    const categoryDimension = ndx.dimension(d => d.category || '');
    const programDimension = ndx.dimension(d => d.program_name || '');

    const volumeByDayGroup = dateDimension.group(d3.timeDay).reduceSum(d => d.issue_count);
    const moduleGroup = moduleDimension.group().reduceSum(d => d.issue_count);
    const severityGroup = severityDimension.group().reduceSum(d => d.issue_count);
    const trendGroup = trendDimension.group().reduceSum(d => d.issue_count);

    // Risk display data is derived from the records that pass the current filters.
    // A crossfilter reducer is not used for this: its `remove` path cannot refresh
    // labels, so switching country left the previous country's programme/severity/
    // percentage on screen while only the counts were correct.
    function recordTime(value) {
        if (value instanceof Date) return value.getTime();
        return Date.parse(value) || 0;
    }

    function applyLatestMetadata(target, record) {
        const value = recordTime(record.date);
        if (value >= target.dateValue) {
            target.dateValue = value;
            target.risk_name = record.risk_name;
            target.module = record.module;
            target.severity = record.severity;
            target.trend = record.trend;
            target.percentage = record.percentage;
            target.unit_label = record.unit_label;
            target.description = record.description;
        }
    }

    function collectFilteredRisks() {
        const byRisk = new Map();
        const byRow = new Map();

        ndx.allFiltered().forEach(record => {
            if (!record.risk_code) return;

            let risk = byRisk.get(record.risk_code);
            if (!risk) {
                risk = { risk_code: record.risk_code, issue_count: 0, dateValue: -1 };
                byRisk.set(record.risk_code, risk);
            }
            risk.issue_count += record.issue_count;
            applyLatestMetadata(risk, record);

            const rowKey = JSON.stringify([record.risk_code, record.country_slug, record.program_name]);
            let row = byRow.get(rowKey);
            if (!row) {
                row = {
                    risk_code: record.risk_code,
                    country: record.country_slug,
                    program_name: record.program_name,
                    issue_count: 0,
                    dateValue: -1
                };
                byRow.set(rowKey, row);
            }
            row.issue_count += record.issue_count;
            applyLatestMetadata(row, record);
        });

        return {
            byRisk: Array.from(byRisk.values()).filter(r => r.issue_count > 0),
            byRow: Array.from(byRow.values()).filter(r => r.issue_count > 0)
        };
    }

    const totalIssues = ndx.groupAll().reduceSum(d => d.issue_count);
    const criticalIssues = ndx.groupAll().reduceSum(d => (d.severity === 'critical' ? d.issue_count : 0));

    // Initialize Timeline ECharts
    const timelineElement = document.getElementById('time-focus-chart');
    const timelineChart = timelineElement ? echarts.init(timelineElement, 'macarons') : null;

    window.addEventListener('resize', function () {
        if (timelineChart) timelineChart.resize();
    });

    function formatCount(val) {
        return d3.format(',')(val || 0);
    }

    function updateKPIs() {
        const totalEl = document.getElementById('total-issues');
        const critEl = document.getElementById('total-critical');
        if (totalEl) totalEl.textContent = formatCount(totalIssues.value());
        if (critEl) critEl.textContent = formatCount(criticalIssues.value());
    }

    function renderSeverityBadge(sev) {
        const badges = {
            critical: '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-600 text-white shadow-xs">Critical</span>',
            warning: '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500 text-white shadow-xs">Warning</span>',
            caution: '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-yellow-400 text-yellow-950 shadow-xs">Caution</span>',
            normal: '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-600 text-white shadow-xs">Normal</span>'
        };
        return badges[sev] || `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-200 text-gray-800">${sev}</span>`;
    }

    function renderTrendBadge(trend) {
        if (trend === 'up') {
            return '<span class="inline-flex items-center gap-0.5 text-xs font-bold text-red-600" title="' + gettext('Increasing') + '"><span class="text-sm">↗</span> ' + gettext('Up') + '</span>';
        }
        if (trend === 'down') {
            return '<span class="inline-flex items-center gap-0.5 text-xs font-bold text-emerald-600" title="' + gettext('Decreasing') + '"><span class="text-sm">↘</span> ' + gettext('Down') + '</span>';
        }
        return '<span class="inline-flex items-center gap-0.5 text-xs font-semibold text-gray-400" title="' + gettext('Neutral') + '"><span class="text-sm">—</span> ' + gettext('Stable') + '</span>';
    }

    function updateModuleBars() {
        const container = document.getElementById('module-distribution-list');
        const countBadge = document.getElementById('modules-monitored-count');
        if (!container) return;

        const total = totalIssues.value();
        const modData = moduleGroup.all()
            .filter(d => d.key && d.value > 0)
            .sort((a, b) => b.value - a.value);

        if (countBadge) {
            countBadge.textContent = `${modData.length} ${gettext('modules')}`;
        }

        if (modData.length === 0) {
            container.innerHTML = `<div class="text-xs text-gray-400 py-3 text-center italic">${gettext('No active module issues')}</div>`;
            return;
        }

        container.innerHTML = modData.map(d => {
            const meta = moduleMeta[d.key.toLowerCase()] || {
                label: d.key.charAt(0).toUpperCase() + d.key.slice(1),
                barColor: '#3b82f6',
                icon: '📁'
            };
            const pct = total > 0 ? ((d.value / total) * 100).toFixed(1) : '0.0';
            const isSelected = selectedModule === d.key;
            const selectedClass = isSelected
                ? 'ring-2 ring-blue-500 bg-blue-50/70 shadow-xs'
                : 'hover:bg-gray-50';

            return `
            <div class="p-2.5 rounded-lg cursor-pointer transition-all border border-gray-200/80 ${selectedClass} module-bar-item" data-module="${d.key}">
                <div class="flex items-center justify-between text-xs mb-1.5">
                    <div class="flex items-center gap-1.5 font-bold text-gray-800">
                        <span>${meta.icon}</span>
                        <span>${meta.label}</span>
                    </div>
                    <div class="text-gray-700 font-bold tabular-nums">
                        <span>${formatCount(d.value)}</span>
                        <span class="text-[10px] font-normal text-gray-400 ml-1">(${pct}%)</span>
                    </div>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-300" style="width: ${pct}%; background-color: ${meta.barColor}"></div>
                </div>
            </div>`;
        }).join('');

        container.querySelectorAll('.module-bar-item').forEach(el => {
            el.addEventListener('click', function () {
                const mod = this.dataset.module;
                if (selectedModule === mod) {
                    selectedModule = null;
                    moduleDimension.filterAll();
                } else {
                    selectedModule = mod;
                    moduleDimension.filter(mod);
                }
                updateAll();
            });
        });
    }

    function updateOperationalCards() {
        const container = document.getElementById('operational-modules-container');
        if (!container) return;

        const activeRisks = collectFilteredRisks().byRisk;

        if (activeRisks.length === 0) {
            container.innerHTML = `
            <div class="bg-white rounded-xl shadow-2xs border border-gray-200 p-8 text-center">
                <div class="text-2xl mb-2">🎉</div>
                <h4 class="text-sm font-bold text-gray-900">${gettext('No Operational Risk Anomalies')}</h4>
                <p class="text-xs text-gray-500 mt-1">${gettext('All operational thresholds are within normal tolerances for the selected filters.')}</p>
            </div>`;
            return;
        }

        // Group risks by module
        const byModule = {};
        activeRisks.forEach(risk => {
            const modKey = (risk.module || 'other').toLowerCase();
            if (!byModule[modKey]) byModule[modKey] = [];
            byModule[modKey].push(risk);
        });

        const html = Object.keys(byModule).map(modKey => {
            const meta = moduleMeta[modKey] || {
                label: modKey.toUpperCase(),
                subtitle: gettext('Operational metrics and bottlenecks'),
                icon: '📁',
                barColor: '#3b82f6',
                badgeBg: 'bg-blue-100 text-blue-800'
            };
            const items = byModule[modKey].sort((a, b) => {
                const rank = { critical: 4, warning: 3, caution: 2, normal: 1 };
                return (rank[b.severity] || 0) - (rank[a.severity] || 0);
            });
            const moduleTotal = items.reduce((acc, cur) => acc + cur.issue_count, 0);

            const cardsHtml = items.map(v => {
                const sev = v.severity || 'normal';
                const sevStyles = {
                    critical: 'bg-red-50/80 border-red-500 text-red-700',
                    warning: 'bg-amber-50/80 border-amber-500 text-amber-700',
                    caution: 'bg-yellow-50/80 border-yellow-400 text-yellow-800',
                    normal: 'bg-emerald-50/80 border-emerald-500 text-emerald-700'
                };
                const styleClass = sevStyles[sev] || sevStyles.normal;

                let trendIcon = '<span class="text-gray-400 font-black text-sm" title="' + gettext('Stable') + '">—</span>';
                if (v.trend === 'up') {
                    trendIcon = '<span class="text-red-600 font-black text-sm" title="' + gettext('Increasing') + '">↗</span>';
                } else if (v.trend === 'down') {
                    trendIcon = '<span class="text-emerald-600 font-black text-sm" title="' + gettext('Decreasing') + '">↘</span>';
                }

                const unit = v.unit_label || gettext('issues');
                const valDisplay = v.percentage !== null && v.percentage !== undefined
                    ? `${v.percentage}% <span class="text-[11px] font-normal text-gray-500">(${formatCount(v.issue_count)})</span>`
                    : `${formatCount(v.issue_count)} <span class="text-[11px] font-normal text-gray-500">${unit}</span>`;

                return `
                <div class="rounded-xl border p-3 border-l-4 transition-all shadow-2xs ${styleClass} flex flex-col justify-between">
                    <div class="flex items-start justify-between gap-2 mb-1.5">
                        <h5 class="text-xs font-bold text-gray-900 leading-snug">${v.risk_name || v.risk_code}</h5>
                        <div class="flex items-center gap-1 shrink-0">
                            ${trendIcon}
                        </div>
                    </div>
                    <div class="text-lg font-black leading-none mb-1 tabular-nums">
                        ${valDisplay}
                    </div>
                    <div class="text-[10px] text-gray-600 line-clamp-2 leading-tight">
                        ${v.description || ''}
                    </div>
                </div>`;
            }).join('');

            return `
            <div class="bg-white rounded-xl shadow-2xs border border-gray-200 p-3.5 transition-all">
                <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-3 border-b border-gray-100">
                    <div class="flex items-center gap-2">
                        <span class="text-lg">${meta.icon}</span>
                        <div>
                            <h4 class="text-xs font-bold uppercase tracking-wider text-gray-900 leading-tight">${meta.label}</h4>
                            <p class="text-[10px] text-gray-500">${meta.subtitle}</p>
                        </div>
                    </div>
                    <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full ${meta.badgeBg}">
                        ${formatCount(moduleTotal)} ${gettext('Issues')}
                    </span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                    ${cardsHtml}
                </div>
            </div>`;
        }).join('');

        container.innerHTML = html;
    }

    function updateTopTable() {
        const rows = collectFilteredRisks().byRow
            .sort((a, b) => b.issue_count - a.issue_count);

        const tableBody = document.getElementById('risk-top-table');
        if (!tableBody) return;

        tableBody.innerHTML = rows.map(v => {
            const pct = v.percentage !== null && v.percentage !== undefined ? `${v.percentage}%` : '—';
            return `<tr class="hover:bg-slate-50/80 transition-colors">
                <td class="py-2.5 px-3 font-semibold text-gray-900 text-xs">${escapeHtml(v.risk_name || v.risk_code)}</td>
                <td class="py-2.5 px-3 text-gray-600 text-xs">${escapeHtml(formatCountry(v.country))}</td>
                <td class="py-2.5 px-3 text-gray-600 text-xs">${escapeHtml(v.module)}</td>
                <td class="py-2.5 px-3 text-gray-600 text-xs">${escapeHtml(v.program_name || '—')}</td>
                <td class="py-2.5 px-3 text-center">${renderSeverityBadge(v.severity)}</td>
                <td class="py-2.5 px-3 text-center">${renderTrendBadge(v.trend)}</td>
                <td class="py-2.5 px-3 text-right font-bold text-gray-900 text-xs tabular-nums">${formatCount(v.issue_count)}</td>
                <td class="py-2.5 px-3 text-right font-semibold text-gray-700 text-xs tabular-nums">${pct}</td>
            </tr>`;
        }).join('');
    }

    function updateAll() {
        updateKPIs();
        updateModuleBars();
        updateOperationalCards();
        updateTopTable();

        // Issues Timeline Chart
        if (timelineChart) {
            const timelineData = volumeByDayGroup.all()
                .filter(d => d.key !== null)
                .map(d => [d.key.getTime(), d.value]);

            timelineChart.setOption({
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        const date = new Date(params[0].value[0]);
                        return `${d3.timeFormat('%B %d, %Y')(date)}<br/><b>${formatCount(params[0].value[1])}</b> ${gettext('issues')}`;
                    }
                },
                toolbox: {
                    show: true,
                    right: 10,
                    top: 0,
                    feature: {
                        saveAsImage: {
                            show: true,
                            title: gettext('Download PNG'),
                            name: 'risk_timeline',
                            pixelRatio: 2,
                            backgroundColor: '#ffffff'
                        }
                    }
                },
                grid: { top: 15, bottom: 25, left: 45, right: 15 },
                xAxis: { type: 'time', axisLabel: { color: '#64748b', fontSize: 10, formatter: value => d3.timeFormat('%b')(new Date(value)) } },
                yAxis: {
                    type: 'value',
                    axisLabel: { color: '#64748b', fontSize: 10 },
                    splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
                },
                series: [{
                    name: gettext('Issues'),
                    type: 'bar',
                    data: timelineData,
                    itemStyle: { color: '#00adef', borderRadius: [2, 2, 0, 0] },
                    barMaxWidth: 16
                }]
            }, { notMerge: true });
        }
    }

    // --- Load Data ---
    async function loadRange(startDate, endDate) {
        try {
            const from = timeFilter.formatDateStr(startDate);
            const to = timeFilter.formatDateStr(endDate);
            const url = `${window.DASHBOARD_CONFIG.endpoint}?date_from=${from}&date_to=${to}&dashboard=risk`;
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
                d.issue_count = +d.issue_count;
                d.percentage = d.percentage === null || d.percentage === undefined ? null : +d.percentage;
                d.severity = d.severity || 'normal';
                d.trend = d.trend || 'neutral';
                d.module = d.module || '';
                d.program_name = d.program_name || '';
                d.category = d.category || '';
                d.risk_code = d.risk_code || d.dimension_value || '';
                d.description = d.description || '';
                d.unit_label = d.unit_label || '';
            });

            dateDimension.filterAll();
            ndx.remove();
            ndx.add(data);

            timeFilter.setBuffer(startDate, endDate);
            populateFilters(data);
            updateAll();
        } catch (error) {
            console.error('Error loading risk data:', error);
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

    // --- Category Tabs ---
    const categoryTabs = document.querySelectorAll('.risk-category-tab');
    categoryTabs.forEach(btn => {
        btn.addEventListener('click', function () {
            currentCategory = this.dataset.category;
            categoryTabs.forEach(b => {
                b.classList.remove('bg-blue-50', 'text-blue-800', 'border-blue-200', 'active-category');
                b.classList.add('bg-gray-100', 'text-gray-700');
            });
            this.classList.add('bg-blue-50', 'text-blue-800', 'border-blue-200', 'active-category');
            this.classList.remove('bg-gray-100', 'text-gray-700');

            if (currentCategory === 'all') {
                categoryDimension.filterAll();
            } else {
                categoryDimension.filter(currentCategory);
            }
            updateAll();
        });
    });

    // --- Country / Programme filters (searchable, single-select) ---
    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function normaliseText(value) {
        return String(value == null ? '' : value)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    }

    function formatCountry(slug) {
        return String(slug || '')
            .split('-')
            .filter(Boolean)
            .map(part => part.charAt(0).toUpperCase() + part.slice(1))
            .join(' ');
    }

    function createCombobox(config) {
        const { input, list, clearButton, onSelect } = config;
        if (!input || !list) return null;

        let items = [];
        let visible = [];
        let activeIndex = -1;
        let selectedValue = '';
        let selectedLabel = '';
        let currentQuery = '';
        let expanded = false;

        function syncClearButton() {
            if (clearButton) clearButton.style.display = selectedValue ? 'flex' : 'none';
        }

        function setExpanded(value) {
            expanded = value;
            input.setAttribute('aria-expanded', value ? 'true' : 'false');
            list.classList.toggle('hidden', !value);
        }

        function render(nextQuery) {
            if (nextQuery !== undefined) currentQuery = nextQuery;
            const query = normaliseText(currentQuery);
            visible = items.filter(item => !query || normaliseText(item.label).includes(query));

            if (!visible.length) {
                activeIndex = -1;
                list.innerHTML = `<li class="px-3 py-2 text-gray-400" role="presentation">${escapeHtml(gettext('No matching results'))}</li>`;
                input.removeAttribute('aria-activedescendant');
                return;
            }

            if (activeIndex < 0 || activeIndex >= visible.length) activeIndex = 0;
            list.innerHTML = visible.map((item, index) => {
                const isActive = index === activeIndex;
                const isSelected = item.value === selectedValue;
                return `<li id="${list.id}-option-${index}" role="option" data-index="${index}" aria-selected="${isSelected}" title="${escapeHtml(item.label)}" class="cursor-pointer truncate px-3 py-1.5 ${isActive ? 'bg-sky-50 text-[#00adef]' : 'text-gray-700'} ${isSelected ? 'font-bold' : ''}">${escapeHtml(item.label)}</li>`;
            }).join('');
            input.setAttribute('aria-activedescendant', `${list.id}-option-${activeIndex}`);
        }

        function scrollActiveIntoView() {
            const option = list.querySelector(`[data-index="${activeIndex}"]`);
            if (option && option.scrollIntoView) option.scrollIntoView({ block: 'nearest' });
        }

        function open() {
            if (!items.length) return;
            render('');
            setExpanded(true);
            scrollActiveIntoView();
        }

        function close() {
            setExpanded(false);
            input.value = selectedLabel;
        }

        function select(index) {
            const item = visible[index];
            if (!item) return;
            selectedValue = item.value;
            selectedLabel = item.label;
            input.value = item.label;
            syncClearButton();
            setExpanded(false);
            onSelect(item.value);
        }

        function clear() {
            selectedValue = '';
            selectedLabel = '';
            input.value = '';
            syncClearButton();
            setExpanded(false);
            onSelect('');
        }

        function setItems(nextItems) {
            items = nextItems.slice();
            const match = items.find(item => item.value === selectedValue);
            if (match) {
                selectedLabel = match.label;
            } else {
                selectedValue = '';
                selectedLabel = '';
            }
            input.value = selectedLabel;
            syncClearButton();
        }

        input.addEventListener('focus', open);
        input.addEventListener('input', () => {
            activeIndex = 0;
            render(input.value);
            setExpanded(true);
            scrollActiveIntoView();
        });
        input.addEventListener('keydown', event => {
            if (event.key === 'ArrowDown') {
                event.preventDefault();
                if (!expanded) { open(); return; }
                activeIndex = Math.min(activeIndex + 1, visible.length - 1);
                render();
                scrollActiveIntoView();
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                render();
                scrollActiveIntoView();
            } else if (event.key === 'Enter') {
                if (expanded) { event.preventDefault(); select(activeIndex); }
            } else if (event.key === 'Escape') {
                if (expanded) { event.preventDefault(); close(); }
            } else if (event.key === 'Tab') {
                close();
            }
        });
        list.addEventListener('mousedown', event => {
            event.preventDefault();
            const option = event.target.closest('[data-index]');
            if (option) select(Number(option.dataset.index));
        });
        if (clearButton) {
            clearButton.addEventListener('mousedown', event => event.preventDefault());
            clearButton.addEventListener('click', event => {
                event.preventDefault();
                clear();
            });
        }
        document.addEventListener('mousedown', event => {
            if (expanded && !list.contains(event.target) && event.target !== input) close();
        });

        syncClearButton();
        return { setItems };
    }

    const programCombobox = createCombobox({
        input: document.getElementById('program-filter-input'),
        list: document.getElementById('program-filter-list'),
        clearButton: document.getElementById('program-filter-clear'),
        onSelect: value => {
            currentProgram = value || 'all';
            if (value) programDimension.filter(value);
            else programDimension.filterAll();
            updateAll();
        }
    });

    const countryCombobox = createCombobox({
        input: document.getElementById('country-filter-input'),
        list: document.getElementById('country-filter-list'),
        clearButton: document.getElementById('country-filter-clear'),
        onSelect: value => {
            currentCountry = value || 'all';
            if (value) countryDimension.filter(value);
            else countryDimension.filterAll();
            updateAll();
        }
    });

    function populateFilters(data) {
        const programs = Array.from(new Set(data.map(d => d.program_name).filter(Boolean)))
            .sort((a, b) => a.localeCompare(b));
        const countries = Array.from(new Set(data.map(d => d.country_slug).filter(Boolean)))
            .sort((a, b) => formatCountry(a).localeCompare(formatCountry(b)));

        if (currentProgram !== 'all' && !programs.includes(currentProgram)) {
            currentProgram = 'all';
            programDimension.filterAll();
        }
        if (currentCountry !== 'all' && !countries.includes(currentCountry)) {
            currentCountry = 'all';
            countryDimension.filterAll();
        }

        if (programCombobox) programCombobox.setItems(programs.map(name => ({ value: name, label: name })));
        if (countryCombobox) countryCombobox.setItems(countries.map(slug => ({ value: slug, label: formatCountry(slug) })));
    }

    loadRange(timeFilter.currentRange.start, timeFilter.currentRange.end);
});
