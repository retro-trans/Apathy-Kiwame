"""Render the stream's English lettering over the locally installed footage."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

from steam_game import ROOT


VTT = re.compile(r'chat-\d+\n(\S+) --> (\S+) line:(\d+)%\n([^\n]+)')
MEDIA = ROOT / 'work' / 'translation' / 'en' / 'media'
UI = ROOT / 'work' / 'ui'
CLUES = json.loads((UI / 'game-stream-clues.json').read_text(encoding='utf-8'))
TITLE = CLUES['banner']['label']
FADES = {
    1: (8.32, 9.16), 2: (15.00, 15.76), 3: (13.60, 15.04), 4: (11.52, 12.64),
    5: (10.00, 10.04), 6: (13.68, 14.96), 7: (7.56, 8.84), 8: (6.56, 7.84),
    9: (15.643, 16.963), 10: (20.683, 21.963), 11: (3.683, 4.963), 12: (13.723, 14.963),
    13: (7.03, 7.07), 14: (4.03, 4.07), 15: (19.24, 19.40),
    16: (29.36, 29.40),
}


def seconds(stamp):
    hours, minutes, seconds = stamp.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def cues(clip):
    path = MEDIA / f'game-stream-{clip:02}.vtt'
    data = path.read_text(encoding='utf-8')
    blocks = data.strip().split('\n\n')
    if blocks.pop(0) != 'WEBVTT':
        raise ValueError(f'Invalid WebVTT header in {path.name}')
    result = []
    for block in blocks:
        match = VTT.fullmatch(block)
        if not match:
            raise ValueError(f'Invalid timed chat cue in {path.name}')
        start, end, line, text = match.groups()
        start, end, line = seconds(start), seconds(end), int(line)
        if not 0 <= start < end or not 0 <= line <= 100:
            raise ValueError(f'Invalid cue geometry in {path.name}')
        result.append((start, end, line, text))
    return result


def isolate_chat(clip):
    # Difference from the clean opening frame isolates bright chat glyphs.
    # Keep the original moving footage everywhere outside that mask.
    difference = "'if(gt(x-y,if(gt(y,160),17,35)),255,0)'"
    planes = range(3) if clip == 16 else range(1)
    channels = ':'.join(f'c{plane}={difference}' for plane in planes)
    mask = f'[live][reference]lut2={channels}'
    if 6 <= clip <= 15:
        mask += ',format=gray'
    mask += ',dilation,dilation'
    if clip != 16:
        bottom = 595 if clip in (9, 10, 15) else 588
        mask += f',drawbox=x=0:y={bottom}:w=960:h={690 - bottom}:color=black:t=fill'
    if clip == 4:
        # The blue wall breaks during this clip. Preserve its thin animated edge.
        mask += ',drawbox=x=306:y=381:w=15:h=108:color=black:t=fill'
    if clip >= 6:
        mask += ',dilation'
    if clip == 15:
        mask += ",drawbox=x=0:y=0:w=960:h=84:color=black:t=fill:enable='gte(t,18.20)'"
    active = "=enable='between(t,1.32,29.36)'" if clip == 16 else ''
    return [
        '[0:v]format=gbrp,split[base][live_rgb]',
        '[1:v]format=gbrp,split[clean][ref_rgb]',
        "[live_rgb]geq=g='min(g(X,Y),b(X,Y))':b='b(X,Y)':r='r(X,Y)':interpolation=nearest,extractplanes=g[live]",
        "[ref_rgb]geq=g='min(g(X,Y),b(X,Y))':b='b(X,Y)':r='r(X,Y)':interpolation=nearest,extractplanes=g[reference]",
        mask + ',format=gbrp[mask]',
        f'[base][clean][mask]maskedmerge{active}[screen]',
    ]


def isolate_clue_labels(clip):
    # Restrict the cleanup to the label column so the original number animation remains visible.
    cover = ('drawbox=x=0:y=0:w=574:h=690:color=black:t=fill,'
             'drawbox=x=852:y=0:w=108:h=690:color=black:t=fill,'
             'drawbox=x=0:y=0:w=960:h=129:color=black:t=fill,'
             'drawbox=x=0:y=537:w=960:h=153:color=black:t=fill')
    fade_start, fade_end = FADES[clip]
    return [
        '[screen]split[lettered][live_labels]',
        "[live_labels]extractplanes=g,lut=c0='if(gt(val,43),255,0)',format=gray,dilation,dilation,"
        + cover + ',format=gbrp[label_mask]',
        f'[2:v]format=gbrp,fade=t=out:st={fade_start}:d={fade_end - fade_start:.4f}[blank_red]',
        '[lettered][blank_red][label_mask]maskedmerge[red_clean]',
    ]


def clue_draws(clip, folder, opacity):
    timing = {}
    if clip == 5:
        notes = json.loads((UI / 'game-stream-05-clue-reveal.json').read_text(encoding='utf-8'))
        timing = {item['row']: (item['label_first_visible_ms'] / 1000, item['label_stable_ms'] / 1000)
                  for item in notes['rows']}
    elif clip == 11:
        notes = json.loads((MEDIA / 'game-stream-11.notes.json').read_text(encoding='utf-8'))
        row = notes['clue_rows']['added_row']
        timing[7] = (row['label_first_visible_seconds'], row['label_settled_seconds'])
    draws = []
    for index, row in enumerate(CLUES['rows'][:6 if clip < 11 else 7], 1):
        name = f'clue-{index:02}'
        label = row['label']
        y = row['top'] + 9
        style = ('drawtext=fontfile=clue-font.ttf:expansion=none:fontcolor=white:fontsize=36:'
                 f'x={CLUES["labels_left"]}:y={y}:{opacity}')
        start, end = timing.get(index, (0, 0))
        if index in timing:
            step = (end - start) / (len(label) - 1)
            for count in range(1, len(label)):
                filename = f'{name}-{count:02}.txt'
                (folder / filename).write_text(label[:count], encoding='utf-8')
                first, next_letter = start + (count - 1) * step, start + count * step
                draws.append(f"{style}:textfile={filename}:enable='gte(t,{first:.3f})*lt(t,{next_letter:.3f})'")
        filename = name + '.txt'
        (folder / filename).write_text(label, encoding='utf-8')
        draws.append(f"{style}:textfile={filename}:enable='gte(t,{end:.3f})'")
    return draws


def ending_video_dialogue(folder):
    effects = json.loads((UI / 'game-stream-13-16-effects.json').read_text(encoding='utf-8'))
    scene = next(item for item in effects['clips'] if item['clip'] == 16)
    show = "enable='lt(t,0.44)+gte(t,29.64)'"
    graph = [
        '[2:v]format=gbrp,crop=127:396:773:94,colorchannelmixer=rr=.378:gg=.378:bb=.378[room]',
        f'[screen][room]overlay=774:94:format=gbrp:{show}[scene_en]',
    ]
    draws = [f'drawbox=x=553:y=656:w=407:h=32:color=black:t=fill:{show}']
    for index, field in enumerate(scene['baked_dialogue']['columns']):
        name = f'ending-text-{index}.txt'
        (folder / name).write_text(field['label'], encoding='utf-8')
        draws.append(f'drawtext=fontfile=story-font.ttf:expansion=none:fontcolor=white:fontsize=24:'
                     f'borderw=1:bordercolor=black:textfile={name}:x=40:y={62 + index * 28}:{show}')
    for item in scene['baked_buttons']:
        name = item['id'] + '.txt'
        (folder / name).write_text(item['label'], encoding='utf-8')
        center = item['bounds']['x'] + item['bounds']['width'] / 2
        draws.append(f'drawtext=fontfile=story-font.ttf:expansion=none:fontcolor=white:fontsize=16:'
                     f'textfile={name}:x={center}-tw/2:y=670-th/2:{show}')
    return graph, draws


def shadowed_clues(clip, folder, banner, opacity):
    # The red plane records the silhouette and closing mask. Recover its
    # attenuation against the source plate and apply it to the English lettering.
    glitch = {13: (2.48, 3.11), 14: (2.52, 3.15)}.get(clip)
    visibility = f":enable='not(between(t,{glitch[0]},{glitch[1]}))'" if glitch else ''
    blur = "gblur=sigma=3:enable='lt(t,18.28)'" if clip == 15 else 'gblur=sigma=3'
    attenuation = "'clip(255*x/max(y,1),0,255)'"
    channels = ':'.join(f'c{plane}={attenuation}' for plane in range(3))
    lettering = ','.join([banner, *clue_draws(clip, folder, opacity)])
    return [
        '[screen]split[scene][live_shade]',
        '[2:v]format=gbrp,split[blank][unshadowed]',
        '[live_shade]extractplanes=r[actual_red]',
        '[unshadowed]extractplanes=r[reference_red]',
        f'[actual_red][reference_red]lut2={channels},{blur},format=gbrp[shade]',
        '[blank]format=yuv444p,split[paint][sample]',
        '[sample]crop=12:49:184:602,scale=624:49[strip]',
        '[paint][strip]overlay=128:602:format=yuv444,' + lettering + ',format=gbrp[ink]',
        '[shade][ink]blend=all_mode=multiply,format=gbrp,split[rows][title]',
        '[rows]crop=278:408:574:129[row_patch]',
        '[title]crop=624:49:128:602[title_patch]',
        f'[scene][row_patch]overlay=574:129:format=yuv444{visibility}[with_rows]',
        f'[with_rows][title_patch]overlay=128:602:format=yuv444{visibility}[scene_en]',
    ]


def filter_graph(clip, folder, chat, sample_time, frame_count):
    graph = isolate_chat(clip) if chat else ['[0:v]format=gbrp[screen]']
    scene = 'screen'
    if 5 <= clip <= 12:
        graph.extend(isolate_clue_labels(clip))
        scene = 'red_clean'
    fade_start, fade_end = FADES[clip]
    opacity = f"alpha='clip(({fade_end}-t)/({fade_end}-{fade_start}),0,1)'"
    font = 'fontfile=stream-font.ttf:expansion=none:fontcolor=white:' + opacity
    (folder / 'banner.txt').write_text(TITLE, encoding='utf-8')
    banner = f'drawtext={font}:textfile=banner.txt:fontsize=32:x=443-tw/2:y=626-th/2'
    if clip == 16:
        ending_graph, draws = ending_video_dialogue(folder)
        graph.extend(ending_graph)
    elif 13 <= clip <= 15:
        graph.extend(shadowed_clues(clip, folder, banner, opacity))
        draws = []
    else:
        graph.extend([
            f'[{scene}]format=yuv444p,split[scene][banner_sample]',
            '[banner_sample]crop=12:49:184:602,scale=470:49[banner_strip]',
            '[scene][banner_strip]overlay=208:602:format=yuv444[scene_en]',
        ])
        draws = [banner]
    if 5 <= clip <= 12:
        draws.extend(clue_draws(clip, folder, opacity))
    for i, (start, end, lane, text) in enumerate(chat, 1):
        name = f'chat-{i:02}.txt'
        (folder / name).write_text(text, encoding='utf-8')
        x = f'960-(960+tw)*(t-{start:.3f})/({end:.3f}-{start:.3f})'
        draws.append(f"drawtext={font}:textfile={name}:fontsize=40:borderw={2 if clip >= 5 else 1}:bordercolor=black:"
                     f"x='{x}':y={lane * 6.9:.1f}-th/2:enable='between(t,{start:.3f},{end:.3f})'")
    if sample_time is not None:
        draws.append(f"select='gte(t,{sample_time})'")
    elif frame_count is not None:
        draws.extend(['fps=25', f'trim=end_frame={frame_count}'])
    graph.append('[scene_en]' + (','.join(draws) or 'null') + '[out]')
    return ';\n'.join(graph)


def render(source, output, clip, sample_time=None):
    chat = cues(clip)
    with TemporaryDirectory(prefix='kiwame-stream-') as temporary:
        folder = Path(temporary)
        fonts = Path(os.environ['WINDIR']) / 'Fonts'
        shutil.copyfile(fonts / 'arialbd.ttf', folder / 'stream-font.ttf')
        ffmpeg = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-n']
        reference_time = ['-ss', '11'] if clip == 16 else []
        subprocess.run(ffmpeg + reference_time + ['-i', str(source), '-frames:v', '1', 'clean.png'], cwd=folder, check=True)
        extra_input = []
        if 5 <= clip <= 15:
            shutil.copyfile(fonts / 'consolab.ttf', folder / 'clue-font.ttf')
            blank = source.with_name('実況5.webm')
            subprocess.run(ffmpeg + ['-i', str(blank), '-frames:v', '1', 'red.png'], cwd=folder, check=True)
            extra_input = ['-loop', '1', '-framerate', '25', '-i', 'red.png']
        elif clip == 16:
            shutil.copyfile(fonts / 'georgia.ttf', folder / 'story-font.ttf')
            extra_input = ['-i', str(source.parents[1] / 'bgimage' / 'gakko' / 'busitu.jpg')]
        frame_count = None
        if clip >= 5 and sample_time is None:
            frame_count = int(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                                                       '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0',
                                                       str(source)], text=True).strip())
        (folder / 'filters.txt').write_text(filter_graph(clip, folder, chat, sample_time, frame_count), encoding='utf-8')
        if sample_time is not None:
            options = ['-frames:v', '1']
        else:
            options = ['-map', '0:a?', '-c:a', 'copy', '-c:v', 'libvpx', '-crf', '14', '-b:v', '3M',
                       '-deadline', 'good', '-cpu-used', '3', '-threads', '4', '-pix_fmt', 'yuv420p']
        subprocess.run(ffmpeg + ['-filter_complex_threads', '2', '-i', str(source), '-i', 'clean.png'] + extra_input +
                       ['-/filter_complex', 'filters.txt', '-map', '[out]'] + options + [str(output)],
                       cwd=folder, check=True)
    return len(chat)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('clip', type=int, choices=FADES)
    parser.add_argument('output', type=Path)
    parser.add_argument('--package', type=Path, default=ROOT / 'work' / 'debug' / 'kiwame-base' / 'package.nw')
    parser.add_argument('--at', type=float, help='Render a single PNG preview at this time in seconds.')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    source = (args.package / 'data' / 'video' / f'実況{args.clip}.webm').resolve(strict=True)
    output = args.output.resolve()
    if output.exists() or output.suffix != ('.png' if args.at is not None else '.webm'):
        parser.error('Choose a new PNG preview or WebM output path.')
    if args.at is not None and not 0 <= args.at <= FADES[args.clip][1]:
        parser.error('Preview time is outside the translated part of the clip.')
    print(f'{source.name}: {len(cues(args.clip))} timed English messages -> {output}', flush=True)
    if not args.dry_run:
        render(source, output, args.clip, args.at)


if __name__ == '__main__':
    main()
