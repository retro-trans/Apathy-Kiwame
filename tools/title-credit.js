/* Patch identity belongs to the live title UI, outside native saved layers. */
(function installTitleCredit() {
    'use strict';
    var info = window.kiwameEnglishUI && window.kiwameEnglishUI.titleCredit;
    var base = document.getElementById('tyrano_base');
    if (!info) return;
    if (!base || !window.TYRANO || !TYRANO.kag || !TYRANO.kag.ftag || !TYRANO.kag.ftag.array_tag) {
        setTimeout(installTitleCredit, 100);
        return;
    }
    if (document.getElementById('kiwame_title_credit')) return;
    var node = document.createElement('div');
    node.id = 'kiwame_title_credit';
    node.className = 'kiwame_title_credit';
    node.style.display = 'none';
    ['v' + info.version, info.credit].forEach(function (text) {
        var line = document.createElement('span');
        line.textContent = text;
        node.appendChild(line);
    });
    base.appendChild(node);
    function refresh() {
        var k = TYRANO.kag, t = k.ftag.array_tag[k.ftag.current_order_index];
        var visible = k.stat.current_scenario === 'title.ks' && t && t.name === 's' && $('img.op').is(':visible');
        var display = visible ? 'block' : 'none';
        if (node.style.display !== display) node.style.display = display;
    }
    refresh();
    setInterval(refresh, 100);
}());
