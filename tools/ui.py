"""Build the English menu labels as new vector assets."""

import json
import shutil
from hashlib import sha256
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from xml.sax.saxutils import escape

from steam_game import ROOT, VERSION


def svg(path, width, height, text, x, y, size, *, center=False, highlight=False, black=False, outline=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    decoration = ""
    if black:
        decoration = f'<rect width="{width}" height="{height}" fill="#000"/>'
    if highlight:
        box_height = min(height - 4, 42)
        decoration = (f'<rect x="3" y="{(height - box_height) / 2}" width="{width - 6}" height="{box_height}" rx="3" '
                      'fill="#262126" fill-opacity=".85" stroke="#8e8070"/>')
    anchor = "middle" if center else "start"
    color = "#fff" if highlight or black else "#ddd"
    lettering = (f'x="{x}" y="{y}" text-anchor="{anchor}" '
                 f'font-family="Georgia, serif" font-size="{size}"')
    text = escape(text)
    shadow = (f'<text {lettering} fill="none" stroke="#151515" stroke-width="2.5" '
              f'stroke-linejoin="round">{text}</text>') if outline else ""
    markup = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'{decoration}{shadow}<text {lettering} fill="{color}">{text}</text></svg>\n'
    )
    path.write_text(markup, encoding="utf-8")


def install_engine_menus(package):
    system = package / "tyrano" / "images" / "system" / "kiwame-en"
    buttons = {"modoru": "Resume", "save": "Save Game", "load": "Load Game", "config": "Settings",
               "title": "Return to Title", "close": "Back"}
    for name, label in buttons.items():
        w, h, size = (60, 33, 16) if name == "close" else (230, 50, 25)
        for suffix in ("", "2"):
            svg(system / f"{name}{suffix}.svg", w, h, label, w / 2, h / 2 + size / 3, size,
                center=True, highlight=bool(suffix))
    for name, title in {"menu": "Menu", "save": "Save Game", "load": "Load Game", "backlog": "Backlog"}.items():
        path = package / "tyrano" / "html" / f"{name}.html"
        text = path.read_text(encoding="utf-8-sig")
        text = text.replace("<div>", f'<div><h1 class="kiwame_en_menu_title">{title}</h1>', 1)
        for button in buttons:
            text = text.replace(f"tyrano/images/system/{button}.png", f"tyrano/images/system/kiwame-en/{button}.svg")
        text = text.replace('.replace(".png","2.png")', '.replace(".png","2.png").replace(".svg","2.svg")')
        path.write_text(text, encoding="utf-8")


def install_notebook(asset_root, maps):
    sources = ROOT / "work" / "ui"
    pages = {
        "RPGmap.jpg": ("old-school-floor-plan", "RPGmap.jpg"),
        "RPGmap2.jpg": ("old-school-equipment-list", "RPGmap3.jpg"),
        "RPGmap5.jpg": ("old-school-poem", "RPGmap3.jpg"),
        "RPGmap6.jpg": ("old-school-five-rumors", "RPGmap3.jpg"),
        "genkan3.jpg": ("old-school-yoshino-envelope", "genkan3.jpg"),
        "roka4.jpg": ("old-school-somei-envelope", "roka4.jpg"),
        "kagami.jpg": ("old-school-mirror", "kagami.jpg"),
        "kagami2.jpg": ("old-school-mirror-blood", "kagami2.jpg"),
        "harigami.jpg": ("old-school-music-chart", "harigami.jpg"),
    }
    notes = {
        "note_yosino.png": ("old-school-yoshino", "note_yosino.png"),
        "note_somei.png": ("old-school-somei", "note_somei.png"),
        "note_uranai.png": ("old-school-holy-water", "note_uranai.png"),
        "uranai.png": ("old-school-holy-water-insert", "uranai.png"),
        "memo_1.png": ("notebook-memo-1", "memo_1.png"),
    }
    for folder, mapping, assets in (("bgimage", "backgrounds", pages), ("fgimage", "images", notes)):
        for original, (name, image) in assets.items():
            filename = f"{name}.svg"
            target = f"kiwame-en/{filename}"
            svg_source = (sources / filename).read_text(encoding="utf-8")
            image_data = b64encode((asset_root / folder / "rpg" / image).read_bytes()).decode("ascii")
            marker = "__BACKGROUND_JPEG__" if folder == "bgimage" else "__SOURCE_IMAGE__"
            if svg_source.count(marker) != 1:
                raise ValueError(f"Expected one image placeholder in {filename}")
            (asset_root / folder / target).write_text(svg_source.replace(marker, image_data), encoding="utf-8")
            maps[mapping][f"rpg/{original}"] = target
    memos = (
        (240, 77, ("Lives of the Musicians, Vol. 4", "… Giuseppe Verdi")),
        (264, 85, ("The Devil's Melody", "… Erich Zann")),
    )
    for number, (width, height, lines) in enumerate(memos, 2):
        target = f"kiwame-en/notebook-memo-{number}.svg"
        lettering = "".join(f'<text x="12" y="{31 + i * 26}">{escape(line)}</text>'
                            for i, line in enumerate(lines))
        (asset_root / "fgimage" / target).write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            '<g fill="#222723" font-family="Segoe Print, Georgia, serif" font-size="15">'
            f'{lettering}</g></svg>\n', encoding="utf-8",
        )
        maps["images"][f"rpg/memo_{number}.png"] = target
    for suffix in ("", "2"):
        target = f"kiwame-en/notebook-map{suffix}.svg"
        svg(asset_root / "image" / target, 194, 55, "← Return to Map", 97, 35, 21,
            center=True, highlight=bool(suffix), outline=True)
        maps["buttons"][f"button/rpg/map{suffix}.png"] = target


def late_battle_backgrounds(asset_root, backgrounds):
    sources = ROOT / "work" / "ui"
    folder = asset_root / "bgimage"
    reflected_window = "rpg/gahag-0114721715-1.jpg"
    if not (folder / reflected_window).is_file():
        raise ValueError("The original reflection image is missing from the package.")
    backgrounds["rpg/gahag.jpg"] = reflected_window

    artwork = {}
    for original, name, marker in (
        ("gonengo.png", "old-school-five-years-later.svg", "__SOURCE_IMAGE__"),
        ("syokuinsitu.jpg", "old-school-faculty-office.svg", "__BACKGROUND_JPEG__"),
        ("kagami1.jpg", "old-school-mirror-intact.svg", "__BACKGROUND_JPEG__"),
    ):
        template = (sources / name).read_text(encoding="utf-8")
        if template.count(marker) != 1:
            raise ValueError(f"Expected one embedded image in {name}.")
        source = f"rpg/{original}"
        image = b64encode((folder / source).read_bytes()).decode("ascii")
        target = f"kiwame-en/{name}"
        backgrounds[source] = target
        artwork[folder / target] = template.replace(marker, image).encode("utf-8")
    return artwork


def background_overlay_styles(mapping):
    selectors = []
    for original, name in mapping.items():
        urls = dict.fromkeys((original, quote(original, safe='/')))
        selectors.append(',\n'.join(f'.{layer}[style*="{url}"]::after'
                                     for layer in ('base_fore', 'base_back') for url in urls))
        selectors.append(f"{{ background-image: url('./data/bgimage/kiwame-en/{name}'); }}\n")
    return '\n'.join(selectors)


def dating_game_overlays(background):
    sources = ROOT / 'work' / 'ui'
    mapping = json.loads((sources / 'game-dating-overlays.json').read_text(encoding='utf-8'))
    assets = {}
    for original, name in mapping.items():
        if not (background / original).is_file():
            raise ValueError(f'Original background is missing: {original}')
        assets[background / 'kiwame-en' / name] = (sources / name).read_bytes()
    return assets, background_overlay_styles(mapping)


def stream_backgrounds(background):
    layout = json.loads((ROOT / 'work' / 'ui' / 'game-stream-clues.json').read_text(encoding='utf-8'))
    definitions = '''<defs>
      <linearGradient id="banner" x2="0" y2="1">
        <stop stop-color="#494949"/><stop offset="1" stop-color="#383838"/>
      </linearGradient>
      <linearGradient id="red-banner" x2="0" y2="1">
        <stop stop-color="#754748"/><stop offset="1" stop-color="#613c3d"/>
      </linearGradient>
      <linearGradient id="red">
        <stop stop-color="#ef100d"/><stop offset=".56" stop-color="#fb1713"/>
        <stop offset="1" stop-color="#ea110b"/>
      </linearGradient>
      <pattern id="scan" patternUnits="userSpaceOnUse" width="1" height="11">
        <rect width="1" height="4" fill="#000" opacity=".12"/>
      </pattern>
    </defs>'''
    assets, mapping = {}, {}
    for original, count in layout['still_assets'].items():
        if not (background / 'game' / 'sindo' / original).is_file():
            raise ValueError(f'Original stream background is missing: {original}')
        red = original.startswith('赤')
        title = original == 'タイトル.gif'
        name = 'game-stream-title.svg' if title else f'game-stream-red-{count}.svg' if red else 'game-stream-banner.svg'
        mapping[f'game/sindo/{original}'] = name
        elements = []
        banner = 'red-banner' if red else 'banner'
        elements.append(f'<rect x="211" y="603" width="467" height="47" fill="url(#{banner})"/>')
        elements.append('<rect x="211" y="603" width="467" height="47" fill="url(#scan)"/>')
        elements.append('<text x="443" y="640" fill="#eee" text-anchor="middle" '
                        'font-family="Arial, sans-serif" font-size="36" textLength="588" '
                        f'lengthAdjust="spacingAndGlyphs">{escape(layout["banner"]["label"])}</text>')
        if title:
            elements.append('<rect x="185" y="192" width="591" height="80" fill="#1e1e1e"/>')
            elements.append('<rect x="185" y="192" width="591" height="80" fill="url(#scan)"/>')
            elements.append('<text x="480" y="257" fill="#fff" text-anchor="middle" '
                            'font-family="Courier New, monospace" font-size="64" font-weight="bold" '
                            'letter-spacing="3">CRIMINAL KIDS</text>')
        for row in layout['rows'][:count]:
            top = row['top']
            left = layout['labels_left']
            cover = f'x="{left - 5}" y="{top}" width="265" height="{layout["row_height"]}"'
            elements.append(f'<rect {cover} fill="url(#red)"/><rect {cover} fill="url(#scan)"/>')
            elements.append(f'<text x="{left}" y="{top + 39}" fill="#fff" font-weight="bold" '
                            f'font-family="Courier New, monospace" font-size="34">{row["label"]}</text>')
        assets[background / 'kiwame-en' / name] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="690">'
            + definitions + ''.join(elements) + '</svg>\n').encode('utf-8')
    return assets, background_overlay_styles(mapping)


def mountain_game_backgrounds(background, mapping):
    sources = ROOT / 'work' / 'ui'
    spec = json.loads((sources / 'game-mountain-screens.json').read_text(encoding='utf-8'))
    artwork = {}
    for number, info in enumerate(spec['hud']['assets'], 1):
        source = 'game/arai/' + info['asset']
        target = f'kiwame-en/game-mountain-hud-{number}.svg'
        original = b64encode((background / source).read_bytes()).decode('ascii')
        values = {'BACKGROUND_JPEG': original, 'STAGE_COVER_WIDTH': info['stage']['cover']['width'],
                  'STAGE_TEXT': escape(info['stage']['en']), 'STAGE_FONT_SIZE': info['stage']['font_size'],
                  'ELEVATION_M': info['status']['elevation_m']}
        template = (sources / spec['hud']['template']).read_text(encoding='utf-8')
        for key, value in values.items():
            template = template.replace(f'__{key}__', str(value))
        artwork[background / target] = template.encode('utf-8')
        mapping[source] = target
    for name in ('credits', 'newspaper'):
        info = spec[name]
        source = 'game/arai/' + info['asset']
        target = 'kiwame-en/' + info['template']
        original = b64encode((background / source).read_bytes()).decode('ascii')
        template = (sources / info['template']).read_text(encoding='utf-8')
        artwork[background / target] = template.replace('__BACKGROUND_JPEG__', original).encode('utf-8')
        mapping[source] = target
    template = (sources / 'game-mountain-stage-map.svg').read_text(encoding='utf-8')
    for number, info in enumerate(spec['stage_select']['assets'], 1):
        source = 'game/arai/' + info['asset']
        target = f'kiwame-en/game-mountain-stage-map-{number}.svg'
        original = b64encode((background / source).read_bytes()).decode('ascii')
        artwork[background / target] = template.replace('__BACKGROUND_JPEG__', original).replace(
            '__UNLOCKED_OPACITY__', '1' if info.get('additional_labels') else '0').encode('utf-8')
        mapping[source] = target
    return artwork


def game_story_artwork(background, maps):
    sources = ROOT / 'work' / 'ui'
    artwork = {}
    for original, template, name, splatter in (
        ('title/title_ゲーム実況怪談.png', 'game-streamers-ghost-story-title', 'game-streamer-title-1', '0'),
        ('title/title_ゲーム実況怪談B.png', 'game-streamers-ghost-story-title', 'game-streamer-title-2', '1'),
        ('sindo/game/マジル名刺.jpg', 'majiru-business-card', 'majiru-business-card', None),
        ('title/狂気山脈1.png', 'mountains-of-madness-title', 'mountains-of-madness-title', None),
        ('title/恋獄ゲーム1.png', 'loves-purgatory-title', 'loves-purgatory-title-1', None),
        ('title/恋獄ゲーム2.png', 'loves-purgatory-title', 'loves-purgatory-title-2', None),
    ):
        marker = '__BACKGROUND_JPEG__' if original.endswith('.jpg') else '__SOURCE_IMAGE__'
        template = (sources / f'{template}.svg').read_text(encoding='utf-8')
        if template.count(marker) != 1:
            raise ValueError(f'Expected one embedded image in {name}.')
        image = b64encode((background / original).read_bytes()).decode('ascii')
        template = template.replace(marker, image)
        if splatter is not None:
            template = template.replace('__SPLATTER_OPACITY__', splatter)
        target = f'kiwame-en/{name}.svg'
        artwork[background / target] = template.encode('utf-8')
        maps['backgrounds'][original] = target
    artwork.update(mountain_game_backgrounds(background, maps['backgrounds']))
    dating, dating_styles = dating_game_overlays(background)
    stream, stream_styles = stream_backgrounds(background)
    artwork.update(dating)
    artwork.update(stream)
    return artwork, dating_styles + stream_styles


def install_game_streams(asset_root, maps):
    from stream_video import render

    video = asset_root / 'video'
    maps['movies'] = {}

    def render_clip(number):
        original = f'実況{number}.webm'
        target = f'kiwame-en/game-stream-{number:02}.webm'
        count = render(video / original, video / target, number)
        return original, target, count

    with ThreadPoolExecutor(max_workers=3) as pool:
        for original, target, count in pool.map(render_clip, range(1, 17)):
            maps['movies'][original] = target
            print(f'  {target}: {count} English chat cues')


def storyteller_artwork(asset_root, maps):
    spec = json.loads((ROOT / 'work/ui/storyteller-names.json').read_text(encoding='utf-8'))
    glossary = json.loads((ROOT / 'work/glossary/core.json').read_text(encoding='utf-8'))
    names = {item['id']: item['en'] for item in glossary['characters']}
    width, height = spec['button_size']['width'], spec['button_size']['height']
    artwork = {}
    for button in spec['buttons']:
        label = escape(names[button['id']])
        for state, directory, mapping, suffix in (
            ('normal', 'image', 'buttons', '1'), ('hover', 'image', 'buttons', '2'),
            ('seen', 'fgimage', 'images', '2'),
        ):
            target = f'kiwame-en/storyteller-{button["id"]}-{state}.svg'
            source = f'kataribe/{button["asset"]}{suffix}.png'
            if not (asset_root / directory / source).is_file():
                raise ValueError(f'Original storyteller asset is missing: {directory}/{source}')
            highlight = ('<rect width="204" height="45" fill="#535355" fill-opacity=".78"/>'
                         '<path d="M10 7 L31 22.5 10 38 Z" fill="#fff"/>') if state == 'hover' else ''
            color = '#aaa' if state == 'seen' else '#fff'
            markup = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
                      f'{highlight}<text x="39" y="31" fill="{color}" font-family="Georgia, serif" '
                      f'font-size="19">{label}</text></svg>\n')
            artwork[asset_root / directory / target] = markup.encode('utf-8')
            maps[mapping][source] = target
    heading = escape(spec['heading']['label'])
    for identity, asset, directory, mapping in [('all', 'なし', 'bgimage', 'backgrounds'), *(
            (button['id'], button['asset'], 'fgimage', 'images') for button in spec['buttons'])]:
        source = f'語り部選択/{asset}.png'
        target = f'kiwame-en/storytellers-{identity}.svg'
        image = b64encode((asset_root / directory / source).read_bytes()).decode('ascii')
        markup = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                  'width="960" height="690">'
                  f'<image width="960" height="690" xlink:href="data:image/png;base64,{image}"/>'
                  '<path d="M550 100 H960 V150 H534 Z" fill="#101012"/>'
                  '<text x="746" y="134" text-anchor="middle" fill="#fff" '
                  f'font-family="Georgia, serif" font-size="28">{heading}</text></svg>\n')
        artwork[asset_root / directory / target] = markup.encode('utf-8')
        maps[mapping][source] = target
    return artwork


def shindo_story_artwork(asset_root, maps):
    background = asset_root / 'bgimage'
    original = 'sindo/トランプ選択.jpg'
    target = 'kiwame-en/shindo-card-select.svg'
    template = (ROOT / 'work/ui/shindo-card-select.svg').read_text(encoding='utf-8')
    image = b64encode((background / original).read_bytes()).decode('ascii')
    artwork = storyteller_artwork(asset_root, maps)
    artwork[background / target] = template.replace('__BACKGROUND_JPEG__', image).encode('utf-8')
    maps['backgrounds'][original] = target
    hallway = 'sindo/学校廊下1.jpg'
    if not (background / hallway).is_file():
        raise ValueError(f'Original school hallway is missing: {hallway}')
    maps['backgrounds']['sindo/学校廊下.jpg'] = hallway
    return artwork


def arai_story_artwork(asset_root, maps):
    sources = ROOT / 'work' / 'ui'
    spec = json.loads((sources / 'arai-suicide-note.json').read_text(encoding='utf-8'))
    template = (sources / spec['template']).read_text(encoding='utf-8')
    background = asset_root / 'bgimage'
    artwork = {}
    for index, note in enumerate(spec['artwork'], 1):
        original = note['source']
        target = f'kiwame-en/arai-suicide-note-{index}.svg'
        image = b64encode((background / original).read_bytes()).decode('ascii')
        markup = template.replace('__BACKGROUND_PNG__', image).replace('__TEXT_BLUR__', str(note['blur']))
        artwork[background / target] = markup.encode('utf-8')
        maps['backgrounds'][original] = target
    return artwork


def settings_artwork(package, maps, config_script=None):
    sources = ROOT / 'work' / 'ui'
    spec = json.loads((sources / 'settings-controls.json').read_text(encoding='utf-8'))
    assets = package / 'data'
    background = assets / 'bgimage' / 'kiwame-en'
    settings = spec['settings']
    template = (sources / settings['template']).read_text(encoding='utf-8')
    image = b64encode((assets / settings['background']).read_bytes()).decode('ascii')
    files = {
        background / 'settings.svg': template.replace('__BACKGROUND_PNG__', image).encode('utf-8'),
        background / 'controls.svg': (sources / spec['controls']['template']).read_bytes(),
    }
    maps['backgrounds']['../../data/' + settings['background']] = 'kiwame-en/settings.svg'
    maps['backgrounds']['operation.png'] = 'kiwame-en/controls.svg'
    config = assets / 'scenario' / 'config.ks'
    script = config.read_bytes() if config_script is None else config_script
    for button in settings['buttons']:
        for suffix in ('', '2'):
            source = f'config/{button["asset"]}{suffix}.png'
            target = f'kiwame-en/{button["id"]}{suffix}.svg'
            old_url = f'data/image/{source}'.encode('ascii')
            script = script.replace(old_url, f'data/image/{target}'.encode('ascii'))
            maps['buttons'][source] = target
    files[config] = script
    return files


def write_settings_artwork(package, maps, files):
    spec = json.loads((ROOT / 'work/ui/settings-controls.json').read_text(encoding='utf-8'))
    for path, content in files.items():
        path.write_bytes(content)
    for button in spec['settings']['buttons']:
        width, height = button['width'], button['height']
        size = 16 if height < 40 else 21
        for suffix in ('', '2'):
            target = maps['buttons'][f'config/{button["asset"]}{suffix}.png']
            label = button.get('active_label', button['label']) if suffix else button['label']
            svg(package / 'data/image' / target, width, height, label,
                width / 2, height / 2 + size / 3, size, center=True, highlight=bool(suffix))


def install(package):
    spec = json.loads((ROOT / "work" / "ui" / "english.json").read_text(encoding="utf-8"))
    asset_root = package / "data"
    maps = {"buttons": {}, "backgrounds": {}, "images": {}, "captions": {}}
    width, height = spec["title_button_size"]
    for button in spec["title_buttons"] + spec["name_buttons"] + spec["dialogue_buttons"] + spec["rpg_buttons"]:
        w, h = button.get("width", width), button.get("height", height)
        title = "width" not in button
        for state in ("normal", "hover"):
            rpg = button["id"].startswith("rpg-")
            folder = "title" if title else "rpg" if rpg else "button"
            source = f"{folder}/{button[state]}.png"
            target = f"kiwame-en/{button['id']}-{state}.svg"
            size = 28 if title else 16 if h <= 34 else 24
            baseline = 55 if title else h / 2 + size / 3
            svg(asset_root / "image" / target, w, h, button["label"], 30 if title else w / 2,
                baseline, size, center=not title, highlight=state == "hover", outline=rpg)
            maps["buttons"][source] = target
    for key, source in (("name_confirm", "名前2.jpg"), ("name_rejected", "名前3.jpg")):
        target = f"kiwame-en/{key}.svg"
        svg(asset_root / "bgimage" / target, 960, 690, spec[key], 480, 252, 28, center=True, black=True)
        maps["backgrounds"][source] = target
    svg(asset_root / "bgimage" / "kiwame-en" / "name-prompt.svg", 375, 51, spec["name_prompt"], 13, 36, 28, black=True)
    for slug, original in (("self-help", "title/自己啓発"), ("burying-the-lie", "title/嘘の埋葬"),
                           ("old-school-building", "rpg/op")):
        card = (ROOT / "work" / "ui" / f"{slug}-title.svg").read_text(encoding="utf-8")
        for index, accent in ((1, "#fff"), (2, "#e70018")):
            target = f"kiwame-en/{slug}-title-{index}.svg"
            (asset_root / "bgimage" / target).write_text(card.replace("#ed002a", accent), encoding="utf-8")
            maps["backgrounds"][f"{original}{index}.png"] = target
    cafeteria = "human-flesh-cafeteria-title.svg"
    target = f"kiwame-en/{cafeteria}"
    shutil.copyfile(ROOT / "work" / "ui" / cafeteria, asset_root / "bgimage" / target)
    maps["backgrounds"]["title/title_人肉食堂A.png"] = target
    target = "kiwame-en/cafeteria-time-card.svg"
    svg(asset_root / "bgimage" / target, 960, 690, "30 years later", 480, 369, 68, center=True, black=True)
    maps["backgrounds"]["jinniku/date.jpg"] = target
    for name, label in spec["rpg_stage_labels"].items():
        target = f"kiwame-en/stage-{name}.svg"
        path = asset_root / "fgimage" / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="521" height="52">'
            '<text x="12" y="35" fill="#fff" stroke="#000" stroke-width="1.3" '
            f'font-family="Georgia, serif" font-size="25" font-weight="bold">{escape(label)}</text></svg>\n',
            encoding="utf-8",
        )
        maps["images"][f"rpg/stage_name_{name}.png"] = target
    cover = "old-school-building-field-notes.svg"
    target = f"kiwame-en/{cover}"
    shutil.copyfile(ROOT / "work" / "ui" / cover, asset_root / "fgimage" / target)
    maps["images"]["rpg/note_top.png"] = target
    install_notebook(asset_root, maps)
    for path, data in late_battle_backgrounds(asset_root, maps["backgrounds"]).items():
        path.write_bytes(data)
    for movie, filename in (("自己啓発.webm", "self-help.vtt"), ("ニュース.webm", "cafeteria-news.vtt"),
                            ("地球爆発.webm", "cafeteria-earth.vtt")):
        target = f"kiwame-en/{filename}"
        movie_captions = asset_root / "video" / target
        movie_captions.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "work" / "translation" / "en" / "media" / filename, movie_captions)
        maps["captions"][movie] = target
    font_root = ROOT / 'tools' / 'fonts' / 'genei-latin'
    font_target = package / 'fonts'
    font_target.mkdir(exist_ok=True)
    for name in ('GenEiLateGoP_v2.ttf', 'LICENSE.txt', 'NOTICE.txt'):
        shutil.copyfile(font_root / name, font_target / name)
    styles = (ROOT / 'tools' / 'english.css').read_bytes()
    if (ROOT / 'work' / 'translation' / 'en' / 'game.en.json').is_file():
        artwork, extra_styles = game_story_artwork(asset_root / 'bgimage', maps)
        for path, data in artwork.items():
            path.write_bytes(data)
        styles += extra_styles.encode('utf-8')
        install_game_streams(asset_root, maps)
    if (ROOT / 'work' / 'translation' / 'en' / 'sindo.en.json').is_file():
        for path, data in shindo_story_artwork(asset_root, maps).items():
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'arai.en.json').is_file():
        for path, data in arai_story_artwork(asset_root, maps).items():
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'kazama.en.json').is_file():
        from kazama_ui import artwork
        for path, data in artwork(asset_root, maps).items():
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'iwashita.en.json').is_file():
        from iwashita_ui import artwork
        for path, data in artwork(asset_root, maps).items():
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'fukuzawa.en.json').is_file():
        from fukuzawa_ui import artwork
        for path, data in artwork(asset_root, maps).items():
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'hosoda.en.json').is_file():
        from hosoda_ui import artwork
        for path, data in artwork(asset_root, maps).items():
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'inoti.en.json').is_file():
        from inoti_ui import artwork
        for path, data in artwork(asset_root, maps).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if (ROOT / 'work' / 'translation' / 'en' / 'site.en.json').is_file():
        from site_ui import artwork
        for path, data in artwork(asset_root, maps).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    for route in ('jyuku', 'syorei'):
        if (ROOT / f'work/translation/en/{route}.en.json').is_file():
            from importlib import import_module
            for path, data in import_module(route + '_art').artwork(asset_root, maps).items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    from common_art import artwork as common_artwork
    for path, data in common_artwork(asset_root, maps).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    from remaining_routes import readable_startup
    startup = asset_root / 'scenario/first.ks'
    startup.write_bytes(readable_startup(startup.read_bytes()))
    maps['readableStartupPause'] = {'scenario': 'first.ks', 'line': 11, 'tag': 'l'}
    maps['titleCredit'] = {'version': VERSION, 'credit': 'github.com/retro-trans'}
    shutil.copyfile(ROOT / 'tools/title-credit.js', package / 'title-credit.js')
    from life_summary import install as install_life_summary
    install_life_summary(package, maps)
    if (ROOT / 'work' / 'translation' / 'en' / 'config.en.json').is_file():
        write_settings_artwork(package, maps, settings_artwork(package, maps))
    (package / 'english.css').write_bytes(styles)
    from text_flow import install_map
    install_map(maps)
    for route in ('jyuku', 'syorei'):
        layout = ROOT / f'work/ui/{route}-layout.json'
        if layout.is_file() and (ROOT / f'work/translation/en/{route}.en.json').is_file():
            maps.setdefault('choiceLayouts', {})[route + '.ks'] = json.loads(layout.read_text(encoding='utf-8'))['choices']
        if (ROOT / f'work/translation/en/{route}.en.json').is_file():
            from remaining_routes import repair
            route_path = asset_root / f'scenario/{route}.ks'
            route_path.write_bytes(repair(route + '.ks', route_path.read_bytes()))
    maps['dynamicText'] = json.loads((ROOT / 'work/ui/dynamic-text.json').read_text(encoding='utf-8'))['mappings']
    for caption_file in sorted((ROOT / 'work/translation/en/audio').glob('*.en.json')):
        caption_data = json.loads(caption_file.read_text(encoding='utf-8'))
        route = caption_data['scenario']
        script = (asset_root / 'scenario' / route).read_text(encoding='utf-8').splitlines()
        cues = {}
        for cue in caption_data['cues']:
            assert sha256((asset_root / 'sound' / cue['storage']).read_bytes()).hexdigest() == cue['audio_sha256']
            assert '[playse ' in script[cue['line'] - 1] and cue['storage'] in script[cue['line'] - 1]
            cues[str(cue['line'])] = {key: cue[key] for key in ('storage', 'start', 'end', 'text')}
        maps.setdefault('audioCaptions', {})[route] = cues
    if maps.get('audioCaptions'):
        shutil.copyfile(ROOT / 'tools/audio-captions.js', package / 'audio-captions.js')
    (package / 'english-ui.js').write_bytes(('window.kiwameEnglishUI = ' + json.dumps(maps) + ';\n').encode('utf-8'))
    install_engine_menus(package)
