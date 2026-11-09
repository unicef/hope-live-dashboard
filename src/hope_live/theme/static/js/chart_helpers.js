/* Shared chart palette and helpers.
 *
 * The dashboard page scripts used to duplicate the same palette and hash
 * function. Keeping them here means a category keeps the same colour on every
 * page.
 */
(function () {
    const palette = [
        '#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80',
        '#8d98b3', '#e5cf0d', '#97b552', '#95706d', '#dc69aa',
        '#07a2a4', '#9a7fd1', '#588dd5', '#f5994e', '#c05050',
        '#59678c', '#c9ab00', '#76933c', '#bc65a6'
    ];

    // Fixed colours for the seven UNICEF regions, so the region chart does not
    // depend on a hash that can collide with a country or programme.
    const regionColors = {
        MENAR: '#5ab1ef',
        ESAR: '#2ec7c9',
        ECAR: '#b6a2de',
        WCAR: '#ffb980',
        LACR: '#97b552',
        EAPR: '#d87a80',
        SAR: '#e5cf0d'
    };

    function getStableColor(name) {
        if (!name) return '#5470c6';
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            // Equivalent to ((hash << 5) - hash), but avoids the shift that
            // desynchronises the xgettext 0.21 JavaScript lexer.
            hash = name.charCodeAt(i) + (Math.imul(hash, 32) - hash);
        }
        return palette[Math.abs(hash) % palette.length];
    }

    function getRegionColor(code) {
        return regionColors[code] || getStableColor(code);
    }

    function timeAxisLabel(value) {
        return d3.timeFormat('%b %y')(new Date(value));
    }

    function formatCountryName(name) {
        if (!name) return '';
        return String(name).replace(/[-_]/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase());
    }

    function initCountryFilter(options) {
        const select = document.getElementById(options.selectId || 'country-filter');
        if (!select || !options.dimension) {
            return { populate: () => {}, apply: () => {}, get value() { return ''; } };
        }
        const dimension = options.dimension;
        const allLabel = select.dataset.allLabel || (select.options[0] && select.options[0].textContent) || 'All countries';
        let current = '';
        try {
            current = window.localStorage.getItem('hopeCountry')
                || new URLSearchParams(window.location.search).get('country')
                || '';
        } catch (error) {
            current = '';
        }

        function apply() {
            if (current) dimension.filter(current);
            else dimension.filterAll();
        }

        function render(values) {
            select.innerHTML = '';
            const all = document.createElement('option');
            all.value = '';
            all.textContent = allLabel;
            select.appendChild(all);
            values.forEach(value => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = formatCountryName(value);
                select.appendChild(option);
            });
            select.value = current;
        }

        select.addEventListener('change', () => {
            current = select.value;
            try {
                if (current) window.localStorage.setItem('hopeCountry', current);
                else window.localStorage.removeItem('hopeCountry');
                const url = new URL(window.location.href);
                if (current) url.searchParams.set('country', current);
                else url.searchParams.delete('country');
                window.history.replaceState({}, '', url);
            } catch (error) {
                // Private browsing or a blocked storage API: keep the in-memory filter.
            }
            apply();
            if (options.onChange) options.onChange(current);
        });

        return {
            populate(rows) {
                const values = Array.from(new Set((rows || [])
                    .map(row => row && row.country_slug)
                    .filter(Boolean)))
                    .sort((a, b) => formatCountryName(a).localeCompare(formatCountryName(b)));
                if (current && !values.includes(current)) {
                    current = '';
                    try { window.localStorage.removeItem('hopeCountry'); } catch (error) { /* ignore */ }
                }
                render(values);
            },
            apply,
            get value() { return current; }
        };
    }

    function setDataAsOf(rows) {
        const el = document.getElementById('data-as-of');
        if (!el) return;
        const dates = (rows || [])
            .map(row => (row && row.date instanceof Date ? row.date : new Date(row && row.date)))
            .filter(date => !Number.isNaN(date.getTime()));
        if (dates.length === 0) {
            el.textContent = '—';
            return;
        }
        const latest = new Date(Math.max(...dates.map(date => date.getTime())));
        el.textContent = d3.timeFormat('%d %b %Y')(latest);
    }

    window.HopeChart = {
        palette: palette,
        regionColors: regionColors,
        getStableColor: getStableColor,
        getRegionColor: getRegionColor,
        timeAxisLabel: timeAxisLabel,
        formatCountryName: formatCountryName,
        initCountryFilter: initCountryFilter,
        setDataAsOf: setDataAsOf
    };
})();
