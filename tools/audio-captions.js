/* English captions follow native sound time without changing audio or script waits. */
(function installAudioCaptions() {
    'use strict';
    var visual = window.kiwameEnglishUI;
    if (!visual || !visual.audioCaptions) return;
    if (!window.TYRANO || !TYRANO.kag || !TYRANO.kag.tag.playse || !TYRANO.kag.menu) {
        setTimeout(installAudioCaptions, 100);
        return;
    }
    var kag = TYRANO.kag;
    if (kag.menu.kiwameAudioCaptions) return;
    var active;
    function clear() {
        if (!active) return;
        active.events.forEach(function (event) { active.audio.removeEventListener(event, active.update); });
        active.node.remove();
        active = null;
    }
    function attach(audio, cue, line, buffer) {
        clear();
        var node = document.createElement('div');
        node.className = 'kiwame_en_audio_caption';
        node.setAttribute('aria-live', 'polite');
        node.setAttribute('data-kiwame-audio-line', String(line));
        node.style.cssText = 'position:absolute;left:50%;top:600px;transform:translateX(-50%);width:860px;max-width:calc(100% - 40px);box-sizing:border-box;padding:6px 14px;color:white;background:rgba(8,8,12,.92);border-radius:4px;text-align:center;font:23px/28px KiwameLatin,sans-serif;z-index:10000;pointer-events:none;display:none';
        node.textContent = cue.text;
        document.querySelector('.tyrano_base').appendChild(node);
        var item = {audio: audio, node: node, source: audio.src, buffer: String(buffer), events: ['play','playing','timeupdate','pause','ended','emptied']};
        item.update = function () {
            if (active !== item) return;
            if (audio.src !== item.source) { clear(); return; }
            var time = audio.currentTime;
            node.style.display = !audio.paused && !audio.ended && time >= cue.start && time < cue.end ? 'block' : 'none';
        };
        active = item;
        item.events.forEach(function (event) { audio.addEventListener(event, item.update); });
        item.update();
    }
    var playse = kag.tag.playse.start;
    var captionedPlayse = function (pm) {
        var tag = this.kag.ftag.array_tag[this.kag.ftag.current_order_index];
        var lines = visual.audioCaptions[this.kag.stat.current_scenario];
        var cue = lines && tag && lines[String(tag.line + 1)];
        var result = playse.apply(this, arguments);
        var buffer = pm.buf || '0';
        var audio = this.kag.tmp.map_se[buffer];
        if (cue && cue.storage === pm.storage) {
            if (audio && audio.addEventListener) attach(audio, cue, tag.line + 1, buffer);
        } else if (active && active.buffer === String(buffer)) clear();
        return result;
    };
    kag.tag.playse.start = captionedPlayse;
    if (kag.ftag.master_tag.playse && kag.ftag.master_tag.playse.start === playse) {
        kag.ftag.master_tag.playse.start = captionedPlayse;
    }
    var load = kag.menu.loadGameData;
    kag.menu.loadGameData = function () { clear(); return load.apply(this, arguments); };
    kag.menu.kiwameAudioCaptions = 1;
}());
