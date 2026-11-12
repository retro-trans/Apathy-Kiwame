/* Compatibility fixes for English text in the game's bundled TyranoScript 4.5. */
(function () {
    'use strict';
    var kag = tyrano.plugin.kag;
    var visual = window.kiwameEnglishUI;
    $.extend(window.tyrano_lang.word, {
        go_title: 'Return to the title screen?',
        exit_game: 'Close the game?',
        not_saved: 'There is no saved game yet.',
        tag: 'Tag',
        not_exists: ' does not exist',
        error: 'An error occurred. Check the scenario script.',
        label: 'Label',
        label_double: ' is duplicated in this scenario',
        error_occurred: 'An error occurred'
    });
    var choiceTops = {
        'op.ks': {'530': 414, '450': 480, '370': 546, '500': 414, '420': 480},
        'jiko.ks': {'350': 414, '270': 480},
        'game.ks': {
            '500': 414, '420': 480, '340': 546, '450': 414, '370': 480,
            '470': 348, '390': 414, '310': 480, '230': 546
        },
        'sindo.ks': {'500': 348, '420': 414, '340': 480, '260': 546,
            '450': 414, '370': 480, '290': 546, '470': 414, '390': 480},
        'arai.ks': {'500': 414, '420': 480, '340': 546, '260': 414,
            '180': 480, '100': 546, '450': 414, '370': 480, '290': 546},
        'jinniku.ks': {
            '500': 414, '420': 480, '340': 546, '260': 602,
            '450': 348, '370': 408, '290': 468, '210': 528, '130': 588
        }
    };
    var makeTag = kag.parser.makeTag;
    kag.parser.makeTag = function () {
        var tag = makeTag.apply(this, arguments);
        var pm = tag.pm;
        var translatedChoice = tag.name === 'glink' && pm.text && pm.text.charAt(0) === '\ue000';
        Object.keys(pm).forEach(function (key) {
            if (typeof pm[key] === 'string') pm[key] = pm[key].replace(/\ue001/g, ' ');
        });
        if (translatedChoice) {
            pm.text = pm.text.slice(1);
            // Convert the original right-to-left positions in reviewed menus.
            var scenario = this.kag.stat.current_scenario;
            var tops = choiceTops[scenario];
            var layouts = visual.choiceLayouts && visual.choiceLayouts[scenario];
            var top = layouts && layouts[String(tag.line + 1)];
            if (top === undefined && tops) top = tops[pm.x];
            if (pm.name === 'vertical' && top !== undefined) {
                pm.y = String(scenario === 'arai.ks' && pm.target === '*シーン020' ? 348 : top);
                pm.x = '82';
                pm.width = '750';
                pm.height = '46';
                pm.size = '23';
                pm.graphic = '';
                pm.enterimg = '';
                pm.name = 'kiwame_en_choice';
                if (scenario === 'inoti.ks' && tag.line + 1 >= 6368 && tag.line + 1 <= 6382) {
                    pm.x = '760';
                    pm.width = '158';
                    pm.height = '72';
                    pm.size = '19';
                    pm.name += ' kiwame_inoti_grid_choice';
                }
            }
        }
        return tag;
    };

    function wrap(name, before) {
        var original = kag.tag[name].start;
        kag.tag[name].start = function (pm) {
            before.call(this, pm);
            return original.call(this, pm);
        };
    }

    function latinPunctuation(text) {
        return text.replace(/[\u2026\u22ef]/g, '...').replace(/\u2025/g, '..');
    }
    function retainedOriginalJapanese(scenario, line) {
        return scenario === 'inoti.ks' && line >= 3356 && line <= 3438;
    }

    // Keep the original orders and click pauses, but let continuous English wrap.
    var hardBreak = kag.tag.r.start;
    kag.tag.r.start = function (pm) {
        var engine = this.kag;
        var tags = engine.ftag.array_tag;
        var order = engine.ftag.current_order_index;
        var tag = tags[order];
        var map = visual.flowBreaks && visual.flowBreaks[engine.stat.current_scenario];
        var ordinal = 0;
        if (tag && tag.name === 'r') {
            for (var index = order; index >= 0 && tags[index].line === tag.line; index--) {
                if (tags[index].name === 'r') ordinal++;
            }
        }
        var key = tag && String(tag.line + 1) + ':' + ordinal;
        var soft = map && ordinal && Object.prototype.hasOwnProperty.call(map, key);
        var separator = soft ? map[key] : '<br />';
        var log = this.kag.variable.tf.system.backlog;
        if (log.length && !engine.stat.log_clear) engine.pushBackLog(separator, 'join');
        if (!soft) return hardBreak.call(this, pm);
        engine.getMessageInnerLayer().find('p .current_span').append(document.createTextNode(separator));
        setTimeout(function () { engine.ftag.nextOrder(); }, 5);
    };

    wrap('button', function (pm) {
        if (visual.buttons[pm.graphic]) pm.graphic = visual.buttons[pm.graphic];
        if (visual.buttons[pm.enterimg]) pm.enterimg = visual.buttons[pm.enterimg];
    });
    wrap('bg', function (pm) {
        if (visual.backgrounds[pm.storage]) pm.storage = visual.backgrounds[pm.storage];
        var boardEvent = scenarioBoardEvent(this.kag, 'bg');
        if (!(boardEvent && boardEvent.retain_previous_until_clear)) clearBoardCaption();
        if (this.kag.stat.current_scenario === 'kazama.ks' && visual.boardCaptions) {
            var current = this.kag.ftag.array_tag[this.kag.ftag.current_order_index];
            var caption = current && visual.boardCaptions[String(current.line + 1)];
            if (caption) {
                boardTimer = setTimeout(function () {
                    boardCaption = $('<div class="kiwame_en_board_caption"></div>').text(latinPunctuation(caption.text));
                    $('.tyrano_base').append(boardCaption);
                }, Number(pm.time || 0) + Number(caption.delay || 100));
            }
        }
        applyScenarioBoardCaption(this.kag, 'bg');
    });
    wrap('layopt', function () { applyScenarioBoardCaption(this.kag, 'layopt'); });
    wrap('wait', function () { applyScenarioBoardCaption(this.kag, 'wait'); });
    wrap('image', function (pm) {
        if (visual.images[pm.storage]) pm.storage = visual.images[pm.storage];
    });
    wrap('chara_face', function (pm) {
        if (visual.images[pm.storage]) pm.storage = visual.images[pm.storage];
    });
    var localizedArai = !!visual.backgrounds['arai/CG/遺書を差し出す相沢.png'];
    var localizedKazama = !!visual.boardCaptions;
    var localizedIwashita = !!(visual.choiceLayouts && visual.choiceLayouts['iwashita.ks']);
    var localizedFukuzawa = !!(visual.choiceLayouts && visual.choiceLayouts['fukuzawa.ks']);
    var localizedHosoda = !!(visual.choiceLayouts && visual.choiceLayouts['hosoda.ks']);
    var localizedInoti = !!(visual.choiceLayouts && visual.choiceLayouts['inoti.ks']);
    var localizedSite = !!(visual.choiceLayouts && visual.choiceLayouts['site.ks']);
    var localizedJyuku = !!(visual.choiceLayouts && visual.choiceLayouts['jyuku.ks']);
    var localizedSyorei = !!(visual.choiceLayouts && visual.choiceLayouts['syorei.ks']);
    var boardTimer;
    var boardCaption;
    function clearBoardCaption() {
        clearTimeout(boardTimer);
        if (boardCaption) boardCaption.remove();
        boardCaption = null;
    }
    function scenarioBoardEvent(engine, trigger) {
        var events = visual.scenarioBoardCaptions && visual.scenarioBoardCaptions[engine.stat.current_scenario];
        var tag = engine.ftag.array_tag[engine.ftag.current_order_index];
        var event = events && tag && events[String(tag.line + 1)];
        return event && event.trigger === trigger ? event : null;
    }
    function applyScenarioBoardCaption(engine, trigger) {
        var event = scenarioBoardEvent(engine, trigger);
        if (!event) return;
        if (event.action === 'clear' && event.retain_previous_until_clear && event.delay_ms) {
            clearTimeout(boardTimer);
            boardTimer = setTimeout(clearBoardCaption, Number(event.delay_ms));
            return;
        }
        clearBoardCaption();
        if (event.action === 'show') {
            // Source-keyed triggers follow native transition completion.
            // Intermediate coin frames clear captions; no future clue is shown.
            boardTimer = setTimeout(function () {
                boardCaption = $('<div class="kiwame_en_board_caption"></div>').text(latinPunctuation(event.text));
                $('.tyrano_base').append(boardCaption);
            }, Number(event.delay_ms || 0));
        }
    }
    function compactEnglish(scenario) {
        return ['op.ks', 'jiko.ks', 'rpg/rpg_op.ks', 'maisou.ks', 'jinniku.ks', 'game.ks'].indexOf(scenario) !== -1 ||
            (scenario === 'sindo.ks' && visual.backgrounds['sindo/トランプ選択.jpg']) ||
            (scenario === 'arai.ks' && localizedArai) || (scenario === 'kazama.ks' && localizedKazama) ||
            (scenario === 'iwashita.ks' && localizedIwashita) ||
            (scenario === 'fukuzawa.ks' && localizedFukuzawa) ||
            (scenario === 'hosoda.ks' && localizedHosoda) ||
            (scenario === 'inoti.ks' && localizedInoti) ||
            (scenario === 'site.ks' && localizedSite) ||
            (scenario === 'jyuku.ks' && localizedJyuku) ||
            (scenario === 'syorei.ks' && localizedSyorei);
    }
    function applyInotiGridLayout(engine, scenario, savedLine, clearRetained) {
        var inner = engine.getMessageInnerLayer();
        if (clearRetained && inner.attr('data-kiwame-retained-clues') === '1') {
            inner.empty().removeAttr('data-kiwame-retained-clues');
        }
        var current = engine.ftag.array_tag[engine.ftag.current_order_index];
        var line = savedLine === undefined ? current && current.line + 1 : savedLine;
        var enabled = localizedInoti && scenario === 'inoti.ks';
        var hint = enabled && ((line >= 5297 && line <= 5337) || (line >= 6393 && line <= 6411));
        var confirm = enabled && line >= 6352 && line <= 6386;
        var layer = engine.layer.getLayer('message0', 'fore');
        layer.toggleClass('kiwame_inoti_hint_panel', !!hint);
        layer.toggleClass('kiwame_inoti_confirm_panel', !!confirm);
        engine.layer.getLayer('1', 'fore').toggleClass('kiwame_inoti_grid_overlay_hidden', !!hint);
        if (hint || confirm) {
            var image = hint ? visual.backgrounds['hukuzawa/CG/問題3.png'] : 'hukuzawa/CG/問題3_2.png';
            engine.layer.getLayer('base', 'fore').css('background-image', 'url("./data/bgimage/' + image + '")');
        }
    }
    wrap('p', function () {
        var k = this.kag, tag = k.ftag.array_tag[k.ftag.current_order_index];
        var line = tag && tag.line + 1;
        if (localizedInoti && k.stat.current_scenario === 'inoti.ks' && (line === 5313 || line === 6409)) {
            var copy = k.getMessageInnerLayer().clone();
            copy.find('.img_next').remove();
            k.tmp.kiwameInotiCluePage = copy.html();
        }
    });
    wrap('glink', function () {
        var k = this.kag, tag = k.ftag.array_tag[k.ftag.current_order_index];
        var line = tag && tag.line + 1, inner = k.getMessageInnerLayer();
        if (localizedInoti && k.stat.current_scenario === 'inoti.ks' && line >= 5325 && line <= 5333 &&
                k.tmp.kiwameInotiCluePage && !inner.text().trim()) {
            // Native p still advances/clears the page and backlog normally. Retain
            // its already-read clues beside the diagram while the choices show.
            inner.html(k.tmp.kiwameInotiCluePage).attr('data-kiwame-retained-clues', '1');
        }
    });
    function applyEnglishLayout(engine, scenario) {
        var compact = !!compactEnglish(scenario);
        engine.getMessageInnerLayer().toggleClass('kiwame_en_compact', compact);
        if (compact) {
            engine.stat.vertical = 'false';
            engine.config.defaultLineSpacing = String(27 - parseInt(engine.config.defaultFontSize, 10));
        }
    }
    function reflowLoadedText(layer, scenario) {
        var pairs = visual.flowPairs && visual.flowPairs[scenario];
        if (!pairs) return;
        var replacements = [];
        $(layer).find('p').each(function () {
            var paragraph = this;
            var breaks = Array.prototype.slice.call(paragraph.querySelectorAll('br'));
            breaks.forEach(function (br, index) {
                var before = document.createRange();
                var after = document.createRange();
                if (index) before.setStartAfter(breaks[index - 1]);
                else before.setStart(paragraph, 0);
                before.setEndBefore(br);
                after.setStartAfter(br);
                if (index + 1 < breaks.length) after.setEndBefore(breaks[index + 1]);
                else after.setEnd(paragraph, paragraph.childNodes.length);
                var a = before.toString().trim(), b = after.toString().trim();
                if (!a || !b) return;
                pairs.some(function (pair) {
                    if (a.slice(-pair[0].length) !== pair[0] || b.slice(0, pair[1].length) !== pair[1]) return false;
                    replacements.push({node: br, separator: pair[2]});
                    return true;
                });
            });
        });
        replacements.forEach(function (item) {
            item.node.parentNode.replaceChild(document.createTextNode(item.separator), item.node);
        });
    }
    var loadGameData = kag.menu.loadGameData;
    kag.menu.loadGameData = function (data) {
        var scenario = data.stat.current_scenario;
        // A wait from the abandoned scene must not advance a loaded normal slot.
        if (data.stat.is_wait !== true && this.kag.tmp.wait_id) {
            clearTimeout(this.kag.tmp.wait_id);
            this.kag.tmp.wait_id = '';
        }
        // Native loading reuses data.stat and changes its line while restoring layers.
        var preserveOriginalPunctuation = retainedOriginalJapanese(scenario, Number(data.stat.current_line) + 1);
        clearBoardCaption();
        var result = loadGameData.apply(this, arguments);
        applyEnglishLayout(this.kag, scenario);
        var grid = data.stat.f && data.stat.f.kiwameInotiGrid;
        applyInotiGridLayout(this.kag, scenario, grid ? grid.line : 0);
        // Older slots include already rendered text and its former inline spacing.
        var layer = this.kag.getMessageInnerLayer()[0];
        var walker = document.createTreeWalker(layer, 4, null, false);
        var node;
        if (!preserveOriginalPunctuation) {
            while ((node = walker.nextNode())) node.nodeValue = latinPunctuation(node.nodeValue);
        }
        reflowLoadedText(layer, scenario);
        return result;
    };
    wrap('position', function (pm) {
        var scenario = this.kag.stat.current_scenario;
        if (pm.layer === 'message0' && pm.frame === 'cg.png' &&
                (scenario === 'jinniku.ks' || scenario === 'game.ks' ||
                    (scenario === 'sindo.ks' && visual.backgrounds['sindo/トランプ選択.jpg']) ||
                    (scenario === 'arai.ks' && localizedArai) ||
                    (scenario === 'iwashita.ks' && localizedIwashita) ||
                    (scenario === 'fukuzawa.ks' && localizedFukuzawa) ||
                    (scenario === 'hosoda.ks' && localizedHosoda) ||
                    (scenario === 'site.ks' && localizedSite) ||
                    (scenario === 'jyuku.ks' && localizedJyuku) ||
                    (scenario === 'syorei.ks' && localizedSyorei))) {
            pm.left = '0';
            pm.width = '312';
        }
    });
    wrap('text', function (pm) {
        clearBoardCaption();
        applyInotiGridLayout(this.kag, this.kag.stat.current_scenario, undefined, true);
        var currentTag = this.kag.ftag.array_tag[this.kag.ftag.current_order_index];
        if (!this.kag.stat.is_script && !this.kag.stat.is_html &&
                !retainedOriginalJapanese(this.kag.stat.current_scenario, currentTag && currentTag.line + 1)) {
            pm.val = latinPunctuation(pm.val);
        }
        // The ending macro sets vertical mode and restores Japanese line spacing.
        var scenario = this.kag.stat.current_scenario;
        var current = this.kag.ftag.array_tag[this.kag.ftag.current_order_index];
        // Four original speaker labels have no break before the following speech.
        if (scenario === 'kazama.ks' && localizedKazama && current &&
                [1272, 1285, 1298, 5141].indexOf(current.line) !== -1) {
            this.kag.getMessageInnerLayer().find('p .current_span').append('<br />');
            this.kag.pushBackLog('<br />', 'join');
        }
        // These consecutive text rows have no break. The parser trims physical-line spaces.
        if (current && current.name === 'text' && ((scenario === 'rpg/batoru.ks' && current.line === 1539) ||
                (scenario === 'arai.ks' && localizedArai && current.line === 934))) {
            pm.val = ' ' + pm.val.replace(/^\s+/, '');
        }
        applyEnglishLayout(this.kag, scenario);
    });

    function showMovieCaptions(video, track, layout) {
        var overlay = document.createElement('div');
        var body = document.createElement('div');
        var headline;
        overlay.className = 'kiwame_en_movie_captions';
        body.className = 'kiwame_en_' + layout;
        if (layout === 'news_report') {
            headline = document.createElement('div');
            headline.className = 'kiwame_en_news_headline';
            overlay.appendChild(headline);
        }
        overlay.appendChild(body);
        overlay.style.zIndex = String(Number(video.style.zIndex) + 1);
        var parent = video.parentNode;
        parent.appendChild(overlay);

        function update() {
            var heading = '';
            var caption = '';
            Array.prototype.forEach.call(track.track.activeCues || [], function (cue) {
                if (cue.id === 'headline') heading = cue.text;
                else caption = cue.text;
            });
            if (headline) {
                headline.textContent = heading;
                headline.style.display = heading ? 'block' : 'none';
            }
            body.textContent = latinPunctuation(caption);
            body.style.display = caption ? 'block' : 'none';
            overlay.style.opacity = video.style.opacity;
        }

        function remove() {
            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            observer.disconnect();
            video.removeEventListener('timeupdate', update);
            track.removeEventListener('cuechange', update);
        }

        // The engine can remove a video on a scene change as well as at its end.
        var observer = new MutationObserver(function () {
            if (video.parentNode !== parent) remove();
        });
        observer.observe(parent, {childList: true});
        video.addEventListener('ended', remove);
        video.addEventListener('timeupdate', update);
        track.addEventListener('cuechange', update);
        update();
    }

    var captionLayouts = {
        'kiwame-en/cafeteria-news.vtt': 'news_report',
        'kiwame-en/cafeteria-earth.vtt': 'earth_intertitle'
    };
    var playVideo = kag.tag.movie.playVideo;
    kag.tag.movie.playVideo = function (pm) {
        var movie = visual.movies && visual.movies[pm.storage];
        var result = playVideo.call(this, movie ? $.extend({}, pm, {storage: movie}) : pm);
        var captions = visual.captions[pm.storage];
        if (captions) {
            var video = document.getElementById('bgmovie');
            var track = document.createElement('track');
            track.kind = 'subtitles';
            track.label = 'English';
            track.srclang = 'en';
            track.src = './data/video/' + captions;
            track.default = true;
            video.appendChild(track);
            var layout = captionLayouts[captions];
            if (layout) {
                track.track.mode = 'hidden';
                showMovieCaptions(video, track, layout);
            } else {
                track.track.mode = 'showing';
            }
        }
        return result;
    };

    var givenName = 'sf.yourname2';
    var familyName = 'sf.yourname1';
    var originalNames = [
        ['Sakagami', 'Shuichi', '坂上', '修一'], ['Arai', 'Shoji', '荒井', '昭二'],
        ['Shindo', 'Makoto', '新堂', '誠'], ['Kazama', 'Nozomu', '風間', '望'],
        ['Iwashita', 'Akemi', '岩下', '明美'], ['Fukuzawa', 'Reiko', '福沢', '玲子'],
        ['Hosoda', 'Tomoharu', '細田', '友晴'], ['Hino', 'Sadao', '日野', '貞夫'],
        ['Asahina', 'Shinya', '朝比奈', '慎也'], ['Kurata', 'Emi', '倉田', '恵美']
    ];

    function displayName(value, column) {
        return value === originalNames[0][column + 2] ? originalNames[0][column] : value;
    }

    wrap('ptext', function (pm) {
        pm.text = latinPunctuation(pm.text || '');
        if (pm.name === 'edlist_name' && /^ED\d{3}: /.test(pm.text)) {
            pm.width = '218px';
        }
        var current = this.kag.ftag.array_tag[this.kag.ftag.current_order_index];
        if (this.kag.stat.current_scenario === 'rpg/batoru.ks' && current &&
                current.line >= 3389 && current.line <= 3424) {
            // The original font leaves the chant's accented glyphs blank.
            pm.face = 'Georgia, serif';
            if (current.line >= 3405) {
                pm.name = 'kiwame_en_madness_chant';
                pm.size = '27';
                pm.y = String(Number(pm.y) - 25);
            }
        }
        // This panel's original text is assembled directly from the saved names.
        if (pm.layer !== '2' || pm.name !== 'name1' || pm.y !== '55') return;
        var saved = this.kag.variable.sf;
        var name = displayName(saved.yourname2, 1) + ' ' + displayName(saved.yourname1, 0);
        pm.text = $('<div>').text(name).html();
        pm.width = '154px';
    });

    wrap('edit', function (pm) {
        if (localizedHosoda && this.kag.stat.current_scenario === 'hosoda.ks' &&
                (pm.name === 'sf.yourname3' || pm.name === 'sf.yourname4')) {
            pm.maxchars = '12';
            pm.left = pm.name === 'sf.yourname3' ? '170' : '510';
            pm.width = '280';
            return;
        }
        if (pm.name !== familyName && pm.name !== givenName) return;
        pm.initial = displayName(pm.initial, pm.name === familyName ? 0 : 1);
        pm.maxchars = '12';
    });
    var edit = kag.tag.edit.start;
    kag.tag.edit.start = function (pm) {
        var result = edit.apply(this, arguments);
        if (localizedHosoda && this.kag.stat.current_scenario === 'hosoda.ks' &&
                (pm.name === 'sf.yourname3' || pm.name === 'sf.yourname4')) {
            this.kag.layer.getFreeLayer().find('.form[name="' + pm.name + '"]')
                .attr('placeholder', pm.name === 'sf.yourname3' ? 'Family name' : 'Given name')
                .attr('aria-label', pm.name === 'sf.yourname3' ? 'Family name' : 'Given name')
                .css({fontFamily: 'KiwameLatin, sans-serif', fontSize: '22px'});
        }
        return result;
    };

    var commit = kag.tag.commit.start;
    kag.tag.commit.start = function () {
        var forms = this.kag.layer.getFreeLayer().find('.form');
        var challenge = localizedHosoda && this.kag.stat.current_scenario === 'hosoda.ks';
        var family = forms.filter('[name="' + (challenge ? 'sf.yourname3' : familyName) + '"]');
        var given = forms.filter('[name="' + (challenge ? 'sf.yourname4' : givenName) + '"]');
        if (forms.length !== 2 || family.length !== 1 || given.length !== 1) return commit.call(this);
        var familyValue = family.val().trim();
        var givenValue = given.val().trim();
        originalNames.some(function (entry) {
            if (familyValue.toLowerCase() !== entry[0].toLowerCase() || givenValue.toLowerCase() !== entry[1].toLowerCase()) return false;
            familyValue = entry[2];
            givenValue = entry[3];
            return true;
        });
        this.kag.variable.sf[challenge ? 'yourname3' : 'yourname1'] = familyValue;
        this.kag.variable.sf[challenge ? 'yourname4' : 'yourname2'] = givenValue;
        if (!challenge) this.kag.saveSystemVariable();
        this.kag.ftag.nextOrder();
    };

    var microscopeViews = {
        '新校舎の正門': "the new school building's front gate",
        '旧校舎の屋上': 'the roof of the old school building',
        '見慣れぬ森': 'an unfamiliar forest'
    };
    var emb = kag.tag.emb.start;
    kag.tag.emb.start = function (pm) {
        var engine = this.kag;
        var values = visual.dynamicText && visual.dynamicText[pm.exp];
        if (values) {
            var canonical = engine.embScript(pm.exp);
            if (Object.prototype.hasOwnProperty.call(values, canonical)) {
                // Saved branch values remain canonical; only their visible words change.
                return engine.ftag.startTag('text', {val: $('<div>').text(String(values[canonical])).html(), backlog: 'join'});
            }
        }
        if (pm.exp === 'f.RPG荒井ルート_レンズ') {
            var view = engine.embScript(pm.exp);
            if (Object.prototype.hasOwnProperty.call(microscopeViews, view)) {
                // The Japanese values are also used as branch keys in the original script.
                return engine.ftag.startTag('text', {val: microscopeViews[view], backlog: 'join'});
            }
        }
        if (pm.exp !== familyName && pm.exp !== givenName) return emb.call(this, pm);
        var ftag = engine.ftag;
        var previous = ftag.array_tag[ftag.current_order_index - 1];
        var next = ftag.array_tag[ftag.current_order_index + 1];
        var value = displayName(engine.embScript(pm.exp), pm.exp === familyName ? 0 : 1);
        if (pm.exp === familyName && next && next.name === 'emb' && next.pm.exp === givenName) {
            value = displayName(engine.embScript(givenName), 1);
        } else if (pm.exp === givenName && previous && previous.name === 'emb' && previous.pm.exp === familyName) {
            value = ' ' + displayName(engine.embScript(familyName), 0);
        }
        ftag.startTag('text', {val: $('<div>').text(String(value)).html(), backlog: 'join'});
    };
}());
