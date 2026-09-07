/* SMW option order and URL values are authoritative; never synthesize IDs. */
var SampleRange = (function () {
    function family(text) {
        var match = /^(\D+)\d+$/.exec(text);
        return match ? match[1] : null;
    }

    function catalog(samples) {
        var items = [], byId = Object.create(null);
        samples.forEach(function (sample) {
            if (!sample.id || sample.id === '0' || byId[sample.id]) return;
            var item = {id: sample.id, text: sample.text, family: family(sample.text), index: items.length};
            items.push(item);
            byId[item.id] = item;
        });
        function range(from, to) {
            var start = byId[from], end = byId[to];
            if (!from || !to) return {error: 'empty', items: []};
            if (!start || !end) return {error: 'unknown', items: []};
            if (!start.family || start.family !== end.family) return {error: 'family', items: []};
            if (start.index > end.index) return {error: 'reverse', items: []};
            return {items: items.slice(start.index, end.index + 1).filter(function (item) {
                return item.family === start.family;
            })};
        }
        function query(term, page, from) {
            var start = byId[from], matches = [];
            term = (term || '').toLowerCase();
            items.forEach(function (item) {
                if (from && (!start || !start.family || item.family !== start.family || item.index < start.index)) return;
                if (item.text.toLowerCase().indexOf(term) !== -1) matches.push(item);
            });
            var offset = ((page || 1) - 1) * 50;
            return {results: matches.slice(offset, offset + 50), more: matches.length > offset + 50};
        }
        return {items: items, byId: byId, range: range, query: query};
    }
    return {catalog: catalog};
}());
if (typeof module !== 'undefined' && module.exports) module.exports = SampleRange;
