/**
 * Shared Time Filter Controller
 * Supports quick presets and custom date range calculation with Crossfilter integration.
 */
class DashboardTimeFilter {
    constructor(options = {}) {
        this.container = document.getElementById('time-filter-container');
        if (!this.container) return;

        this.onFilterChange = options.onFilterChange || (() => {});
        this.granularity = this.container.dataset.granularity || 'daily';
        this.currentPreset = options.defaultPreset || 'this_year';
        this.currentRange = this.calculatePresetRange(this.currentPreset);
        this.buffer = { start: null, end: null };

        this.initUI();
    }

    static parseLocalDate(value) {
        // Parse "YYYY-MM-DD" as local midnight (matches d3.timeParse('%Y-%m-%d')).
        const parts = value.split('-').map(Number);
        return new Date(parts[0], parts[1] - 1, parts[2], 0, 0, 0, 0);
    }

    formatDateStr(d) {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    }

    calculatePresetRange(preset) {
        const now = new Date();
        const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
        let start;

        switch (preset) {
            case 'today':
                start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
                break;
            case 'this_week': {
                const day = now.getDay(); // 0 = Sunday
                const mondayOffset = day === 0 ? -6 : 1 - day;
                start = new Date(now.getFullYear(), now.getMonth(), now.getDate() + mondayOffset, 0, 0, 0, 0);
                break;
            }
            case 'this_month':
                start = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0, 0);
                break;
            case 'last_3_months':
                start = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 90, 0, 0, 0, 0);
                break;
            case 'this_year':
            default:
                start = new Date(now.getFullYear(), 0, 1, 0, 0, 0, 0);
                break;
        }

        return { start, end };
    }

    setBuffer(start, end) {
        this.buffer = { start, end };
    }

    isWithinBuffer(start, end) {
        if (!this.buffer.start || !this.buffer.end) return false;
        return start >= this.buffer.start && end <= this.buffer.end;
    }

    updateLabel(start, end) {
        const label = document.getElementById('active-range-label');
        if (!label) return;
        const opts = { month: 'short', day: 'numeric', year: 'numeric' };
        label.textContent = `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
    }

    initUI() {
        if (this.granularity === 'monthly') {
            this.container.querySelectorAll('[data-daily-only]').forEach(el => {
                el.style.display = 'none';
            });
        }

        const presetBtns = this.container.querySelectorAll('.time-preset-btn');
        const customInputs = document.getElementById('custom-range-inputs');
        const dateFromInput = document.getElementById('filter-date-from');
        const dateToInput = document.getElementById('filter-date-to');
        const applyBtn = document.getElementById('btn-apply-custom-range');

        [dateFromInput, dateToInput].forEach(input => {
            if (!input) return;
            input.addEventListener('click', () => {
                if (typeof input.showPicker === 'function') {
                    try {
                        input.showPicker();
                    } catch (e) {
                        // Ignore context/security errors; fall back to native behavior.
                    }
                }
            });
        });

        presetBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = btn.dataset.preset;
                this.setActiveButton(btn);

                if (preset === 'custom') {
                    customInputs.classList.remove('hidden');
                    customInputs.classList.add('flex');
                    dateFromInput.value = this.formatDateStr(this.currentRange.start);
                    dateToInput.value = this.formatDateStr(this.currentRange.end);
                    return;
                }

                customInputs.classList.add('hidden');
                customInputs.classList.remove('flex');
                this.currentPreset = preset;
                this.currentRange = this.calculatePresetRange(preset);
                this.updateLabel(this.currentRange.start, this.currentRange.end);
                this.onFilterChange(this.currentRange.start, this.currentRange.end, preset);
            });
        });

        applyBtn.addEventListener('click', () => {
            if (dateFromInput.value && dateToInput.value) {
                const start = DashboardTimeFilter.parseLocalDate(dateFromInput.value);
                const end = DashboardTimeFilter.parseLocalDate(dateToInput.value);
                end.setHours(23, 59, 59, 999);
                if (start > end) return;
                this.currentPreset = 'custom';
                this.currentRange = { start, end };
                this.updateLabel(start, end);
                this.onFilterChange(start, end, 'custom');
            }
        });

        this.setActiveButton(this.container.querySelector(`[data-preset="${this.currentPreset}"]`));
        this.updateLabel(this.currentRange.start, this.currentRange.end);
    }

    setActiveButton(btn) {
        if (!btn) return;
        this.container.querySelectorAll('.time-preset-btn').forEach(b => {
            b.classList.remove('bg-blue-50', 'text-blue-800', 'active-preset', 'shadow-sm');
            b.classList.add('bg-gray-100', 'text-gray-700');
        });
        btn.classList.add('bg-blue-50', 'text-blue-800', 'active-preset', 'shadow-sm');
        btn.classList.remove('bg-gray-100', 'text-gray-700');
    }
}

window.DashboardTimeFilter = DashboardTimeFilter;
