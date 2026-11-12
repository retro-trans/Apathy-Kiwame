/* Keep Life's grid state with new save slots; enabled only by its English UI map. */
(function installInotiGridLifecycle() {
    'use strict';
    if (!window.kiwameEnglishUI || !window.kiwameEnglishUI.inotiGridLifecycle) return;
    if (!window.TYRANO || !TYRANO.kag || !TYRANO.kag.menu || !TYRANO.kag.menu.snapSave) {
        setTimeout(installInotiGridLifecycle, 100);
        return;
    }
    var kag = TYRANO.kag;
    if (kag.menu.kiwameInotiGridLifecycle) return;
    var key = 'kiwameInotiGrid';
    function isGridLine(line) { return line >= 5297 && line <= 6411; }
    function booleanArray(values, count) {
        return Array.isArray(values) && values.length === count && values.every(function (value) {
            return typeof value === 'boolean';
        });
    }
    var snapSave = kag.menu.snapSave;
    kag.menu.snapSave = function () {
        var k = this.kag, tag = k.ftag.array_tag[k.ftag.current_order_index];
        var line = tag && tag.line + 1;
        if (k.stat.current_scenario === 'inoti.ks' && isGridLine(line)) {
            var state = {version: 1, line: line, order: k.ftag.current_order_index - 1,
                flags: [], cells: []};
            for (var n = 1; n <= 5; n++) state.flags.push(k.variable.sf['ボタン' + n] === true);
            for (var x = 1; x <= 5; x++) for (var y = 1; y <= 5; y++) {
                state.cells.push(k.variable.sf['x' + x + '_y' + y] === true);
            }
            k.stat.f[key] = state;
        } else {
            delete k.stat.f[key];
        }
        return snapSave.apply(this, arguments);
    };
    var loadGameData = kag.menu.loadGameData;
    kag.menu.loadGameData = function (data) {
        var state = data && data.stat && data.stat.f && data.stat.f[key];
        if (data && data.stat && data.stat.current_scenario === 'inoti.ks' && state &&
                state.version === 1 && isGridLine(state.line) && state.order === data.current_order_index &&
                booleanArray(state.flags, 5) && booleanArray(state.cells, 25)) {
            var sf = this.kag.variable.sf;
            for (var n = 1; n <= 5; n++) sf['ボタン' + n] = state.flags[n - 1];
            for (var x = 1; x <= 5; x++) for (var y = 1; y <= 5; y++) {
                sf['x' + x + '_y' + y] = state.cells[(x - 1) * 5 + y - 1];
            }
        }
        return loadGameData.apply(this, arguments);
    };
    kag.menu.kiwameInotiGridLifecycle = 1;
}());
