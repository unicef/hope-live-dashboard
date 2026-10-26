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

    window.HopeChart = {
        palette: palette,
        regionColors: regionColors,
        getStableColor: getStableColor,
        getRegionColor: getRegionColor
    };
})();
