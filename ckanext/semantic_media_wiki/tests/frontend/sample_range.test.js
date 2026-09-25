const test = require('node:test');
const assert = require('node:assert/strict');
const {catalog} = require('../../public/statics/sample_link/sample_range');
const titles = ['A0001', 'X0005', 'X0006', 'X0008', 'X0010', 'X0011', 'X0012', 'B0045'];
const options = titles.map(text => ({id: 'https://wiki/' + text, text}));
const samples = catalog([{id: '0', text: 'None selected'}, ...options]);
const url = name => 'https://wiki/' + name;

test('inclusive real range skips missing IDs', () => {
    assert.deepEqual(samples.range(url('X0005'), url('X0012')).items.map(item => item.text), titles.slice(1, 7));
});
test('reverse, cross-prefix, unknown and empty ranges are rejected', () => {
    assert.equal(samples.range(url('X0012'), url('X0005')).error, 'reverse');
    assert.equal(samples.range(url('A0001'), url('B0045')).error, 'family');
    assert.equal(samples.range(url('X0007'), url('X0012')).error, 'unknown');
    for (const [from, to] of [['', ''], ['', url('X0005')], [url('X0005'), '']]) {
        assert.equal(samples.range(from, to).error, 'empty');
    }
});
test('manual search includes arbitrary families and excludes the placeholder', () => {
    assert.equal(samples.query('b0045', 1).results[0].id, url('B0045'));
    assert.equal(samples.query('', 1).results.length, titles.length);
});
test('To search only includes the same family at or after From', () => {
    assert.deepEqual(samples.query('', 1, url('X0010')).results.map(item => item.text), ['X0010', 'X0011', 'X0012']);
});
test('catalog removes duplicate URLs and does not invent sorting', () => {
    const ordered = catalog([options[4], options[1], options[4]]);
    assert.deepEqual(ordered.range(url('X0010'), url('X0005')).items.map(item => item.text), ['X0010', 'X0005']);
});
test('unrecognized names remain manual options but cannot define a range', () => {
    const other = catalog([{id: 'custom', text: 'Custom sample'}]);
    assert.equal(other.query('custom', 1).results.length, 1);
    assert.equal(other.range('custom', 'custom').error, 'family');
});
test('5900+ options are paginated in batches of 50', () => {
    const large = catalog(Array.from({length: 6000}, (_, i) => ({id: String(i + 1), text: 'X' + i})));
    assert.equal(large.query('', 1).results.length, 50);
    assert.equal(large.query('', 1).more, true);
    assert.equal(large.query('', 120).more, false);
});
