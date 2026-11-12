/* Loaded only in the isolated QA copy. */
(function () {
    'use strict';

    var fs = require('fs');
    var path = require('path');
    var trace = [];
    var snapshots = {};
    var activePreview = false;

    // Only the QA launcher requests silence; ordinary test-build launches keep audio.
    if (process.env.KIWAME_QA_AUDIO_MUTE === '1') {
        var audioPlay = window.HTMLMediaElement.prototype.play;
        window.HTMLMediaElement.prototype.play = function () {
            this.muted = true;
            return audioPlay.apply(this, arguments);
        };
    }

    function game() {
        if (!window.TYRANO || !TYRANO.kag || !TYRANO.kag.ftag.master_tag.text) {
            throw new Error('The scenario interpreter is still starting.');
        }
        return TYRANO.kag;
    }

    function idle(kag) {
        return !activePreview && !kag.stat.is_adding_text && !kag.stat.is_trans &&
            kag.stat.is_strong_stop === true;
    }

    function requireIdle(kag) {
        if (!idle(kag)) throw new Error('Pause at a menu or choice first.');
    }

    function state() {
        var kag = game();
        var ftag = kag.ftag;
        var current = ftag.array_tag[ftag.current_order_index];
        return {
            scenario: kag.stat.current_scenario,
            line: current && Number.isInteger(current.line) ? current.line + 1 : null,
            tag: current ? current.name : null,
            order: ftag.current_order_index,
            strongStop: kag.stat.is_strong_stop === true,
            addingText: kag.stat.is_adding_text === true,
            message: kag.getMessageInnerLayer().text().slice(-500),
            choices: inspect('.event-setting-element').filter(function (item) { return item.width && item.height; })
        };
    }

    function inspect(selector) {
        return Array.prototype.map.call(document.querySelectorAll(selector), function (element) {
            var rect = element.getBoundingClientRect();
            var css = getComputedStyle(element);
            return {id: element.id, text: element.textContent.trim(), x: rect.left,
                y: rect.top, width: rect.width, height: rect.height,
                font: css.fontFamily, size: css.fontSize, writingMode: css.webkitWritingMode};
        });
    }

    function captureTrace() {
        var ftag = game().ftag;
        if (ftag.kiwameTrace) return;
        var next = ftag.nextOrder;
        ftag.nextOrder = function () {
            var tag = this.array_tag[this.current_order_index + 1];
            if (tag && !this.kag.stat.is_strong_stop && !this.kag.stat.is_adding_text) {
                trace.push({scenario: this.kag.stat.current_scenario,
                    line: Number.isInteger(tag.line) ? tag.line + 1 : null, tag: tag.name});
                if (trace.length > 200) trace.shift();
            }
            return next.apply(this, arguments);
        };
        ftag.kiwameTrace = true;
    }

    function snapshot(name) {
        var kag = game();
        requireIdle(kag);
        snapshots[name] = {state: state(), variables: JSON.parse(JSON.stringify(kag.stat.f)),
            system: JSON.parse(JSON.stringify(kag.variable.sf))};
        return snapshots[name];
    }

    function preview(text) {
        var kag = game();
        requireIdle(kag);
        if (typeof text !== 'string' || !text.length || text.length > 1500 || /[<>&\[\]]/.test(text)) {
            throw new Error('Supply 1–1500 plain text characters.');
        }
        var layer = kag.getMessageInnerLayer();
        var parent = layer.parent();
        var previous = layer.contents().detach();
        var savedVisibility = parent[0].style.display;
        var prior = {skip: kag.stat.is_skip, nowait: kag.stat.is_nowait, ruby: kag.stat.ruby_str,
            adding: kag.stat.is_adding_text, click: kag.stat.is_click_text, hide: kag.stat.is_hide_message,
            logJoin: kag.stat.log_join, charaText: kag.stat.f_chara_ptext};
        var ftag = kag.ftag;
        var originalNext = ftag.nextOrder;
        var originalLog = kag.pushBackLog;
        activePreview = true;
        kag.stat.is_nowait = true;
        kag.stat.is_hide_message = false;
        kag.stat.ruby_str = '';
        kag.pushBackLog = function () {};
        ftag.nextOrder = function () {
            ftag.nextOrder = originalNext;
            kag.pushBackLog = originalLog;
        };
        parent.show();
        var textTag = ftag.master_tag.text;
        if (kag.stat.vertical === 'true') textTag.showMessageVertical(text, {backlog: 'add'});
        else textTag.showMessage(text, {backlog: 'add'});
        return function () {
            if (ftag.nextOrder !== originalNext) throw new Error('Wait for the preview to finish drawing.');
            layer.empty().append(previous);
            parent[0].style.display = savedVisibility;
            kag.stat.is_skip = prior.skip;
            kag.stat.is_nowait = prior.nowait;
            kag.stat.ruby_str = prior.ruby;
            kag.stat.is_adding_text = prior.adding;
            kag.stat.is_click_text = prior.click;
            kag.stat.is_hide_message = prior.hide;
            kag.stat.log_join = prior.logJoin;
            kag.stat.f_chara_ptext = prior.charaText;
            activePreview = false;
        };
    }

    function reload() {
        var kag = game();
        requireIdle(kag);
        var scenario = kag.stat.current_scenario;
        if (!/^(?:[a-z0-9_]+\/)*[a-z0-9_]+\.ks$/i.test(scenario)) throw new Error('Invalid scenario path.');
        var diskPath = path.join(path.dirname(process.execPath), 'package.nw', 'data', 'scenario', scenario);
        var parsed = kag.parser.parseScenario(fs.readFileSync(diskPath, 'utf8').replace(/^\ufeff/, ''));
        var previous = kag.ftag.array_tag;
        if (previous.length !== parsed.array_s.length || previous.some(function (tag, i) {
            return tag.name !== parsed.array_s[i].name || tag.line !== parsed.array_s[i].line;
        })) throw new Error('Scenario structure changed. Restart the isolated build.');
        kag.cache_scenario['./data/scenario/' + scenario] = parsed;
        kag.stat.map_label = parsed.map_label;
        kag.ftag.array_tag = parsed.array_s;
        return {scenario: scenario, tags: parsed.array_s.length, order: kag.ftag.current_order_index};
    }

    function metrics() {
        var kag = game();
        var layer = kag.getMessageInnerLayer()[0];
        var span = layer.querySelector('.current_span') || layer;
        var css = getComputedStyle(span);
        var canvas = document.createElement('canvas').getContext('2d');
        canvas.font = css.fontSize + ' ' + css.fontFamily;
        return {font: canvas.font, narrow: canvas.measureText('iiiii').width, wide: canvas.measureText('WWWWW').width,
            layerWidth: layer.clientWidth, layerHeight: layer.clientHeight,
            contentHeight: layer.querySelector('p') ? layer.querySelector('p').getBoundingClientRect().height : 0};
    }

    var clearPreview;
    window.kiwameQA = {
        state: state,
        inspect: inspect,
        metrics: metrics,
        reload: reload,
        trace: function () { captureTrace(); return trace.slice(); },
        snapshot: snapshot,
        saved: function (name) { return snapshots[name] || null; },
        click: function (selector) {
            if (activePreview) throw new Error('Clear the preview before sending input.');
            var matches = $(selector).filter(':visible');
            if (matches.length !== 1) throw new Error('Input must identify exactly one visible target.');
            matches.trigger('click');
            return matches.length;
        },
        advance: function () { return this.click('.layer_event_click'); },
        jump: function (scenario, label) {
            var kag = game();
            requireIdle(kag);
            if (!/^(?:[a-z0-9_]+\/)*[a-z0-9_]+\.ks$/i.test(scenario)) throw new Error('Invalid scenario path.');
            delete kag.cache_scenario['./data/scenario/' + scenario];
            kag.loadScenario(scenario, function (tags) { kag.ftag.buildTag(tags, label || ''); });
            return true;
        },
        preview: function (text) { clearPreview = preview(text); return true; },
        clearPreview: function () { if (clearPreview) clearPreview(); clearPreview = null; return true; }
    };
}());
