/* Non-graphic Life adaptation; original order positions remain compatible with saves. */
(function installLifeSummary() {
    'use strict';
    var spec = window.kiwameEnglishUI && window.kiwameEnglishUI.lifeSummary;
    if (!spec) return;
    if (!window.TYRANO || !TYRANO.kag || !TYRANO.kag.ftag || !TYRANO.kag.ftag.master_tag.text || !TYRANO.kag.menu) {
        setTimeout(installLifeSummary, 100);
        return;
    }
    var kag = TYRANO.kag;
    if (kag.menu.kiwameLifeSummary) return;
    function pageFor(line) {
        for (var i = 0; i < spec.pages.length; i++) if (line <= spec.pages[i].last) return spec.pages[i];
        return spec.pages[spec.pages.length - 1];
    }
    function summaryLine(k) {
        var t = k.ftag.array_tag[k.ftag.current_order_index];
        var line = t && t.line + 1;
        return k.stat.current_scenario === 'inoti.ks' && line >= spec.source_range[0] && line <= spec.source_range[1] ? line : 0;
    }
    ['text', 'r', 'l', 'p'].forEach(function (name) {
        var tag = kag.ftag.master_tag[name], original = tag.start;
        tag.start = function (pm) {
            var line = summaryLine(this.kag);
            if (!line) return original.apply(this, arguments);
            var page = pageFor(line);
            if (name === 'text' && line === page.show) {
                this.kag.layer.clearMessageInnerLayerAll();
                this.kag.stat.log_clear = true;
                this.kag.ftag.hideNextImg();
                return original.apply(this, arguments);
            }
            if (name === 'p' && line === page.pause) return original.apply(this, arguments);
            if ((name === 'l' || name === 'p') && this.kag.tmp.kiwameSummaryLoadedPause === line) {
                delete this.kag.tmp.kiwameSummaryLoadedPause;
                return original.apply(this, arguments);
            }
            // Ellipsis placeholders retain text-tag positions but never enter the display/log.
            return this.kag.ftag.nextOrder();
        };
    });
    function savedLine(data) {
        if (!data || !data.stat || data.stat.current_scenario !== 'inoti.ks') return 0;
        var line = Number(data.stat.current_line) + 1;
        return line >= spec.legacy_load_range[0] && line <= spec.legacy_load_range[1] ? line : 0;
    }
    var getSaveData = kag.menu.getSaveData;
    kag.menu.getSaveData = function () {
        var result = getSaveData.apply(this, arguments);
        if (!this.kiwameSummaryMenuRead) return result;
        (result.data || []).forEach(function (slot) {
            if (savedLine(slot)) {
                // Menu-only view; disk save bytes and story state are never rewritten.
                slot.title = 'Life - adapted summary';
                slot.img_data = '';
            }
        });
        return result;
    };
    ['displayLoad', 'displaySave'].forEach(function (name) {
        var original = kag.menu[name];
        kag.menu[name] = function () {
            var previous = this.kiwameSummaryMenuRead;
            this.kiwameSummaryMenuRead = true;
            try { return original.apply(this, arguments); }
            finally { this.kiwameSummaryMenuRead = previous; }
        };
    });
    var loadGameData = kag.menu.loadGameData;
    kag.menu.loadGameData = function (data) {
        var line = savedLine(data);
        if (line) {
            // Sanitize before native setLayerHtml can mount a legacy rendered passage.
            data = $.extend(true, {}, data);
            var page = pageFor(line);
            var body = $('<div>').text(page.text).html();
            var text = '<p><span class="current_span">' + body + '</span></p>';
            ['map_layer_fore', 'map_layer_back'].forEach(function (group) {
                Object.keys(data.layer[group]).forEach(function (key) {
                    if (key.indexOf('message') === 0) {
                        data.layer[group][key] = data.layer[group][key].replace(/(<div\b[^>]*\bclass="[^"]*\bmessage_inner\b[^"]*"[^>]*>)[\s\S]*?(<\/div>)/g, '$1' + (key === 'message0' ? text : '') + '$2');
                    } else {
                        var node = kag.layer[group][key].clone().empty();
                        if (key === 'base') node.css('background-image', 'url("./data/bgimage/kuro.jpg")');
                        data.layer[group][key] = node.outerHTML();
                    }
                });
            });
            data.layer.layer_free = kag.layer.getFreeLayer().clone().empty().hide().outerHTML();
            data.layer.layer_blend = {};
            data.stat.current_save_str = page.text;
            data.stat.is_hide_message = false;
            data.stat.is_adding_text = false;
            data.stat.is_click_text = false;
            data.stat.is_skip = false;
            data.stat.is_auto = false;
            kag.tmp.kiwameSummaryLoadedPause = line;
        } else {
            delete kag.tmp.kiwameSummaryLoadedPause;
        }
        var args = Array.prototype.slice.call(arguments);
        args[0] = data;
        return loadGameData.apply(this, args);
    };
    kag.menu.kiwameLifeSummary = 1;
}());
