"""Rebuild the scrolling English letter over the original movie, for preview only.

OpenCV analyzes moving dark lettering and reconstructs the covered video pixels.
FFmpeg performs compositing, text rendering and video encoding.
Original game files are read-only. Existing outputs are never overwritten.
"""
import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess

import cv2
import numpy as np

from steam_game import ROOT
from syorei_art import _Font

SOURCE = Path('M:/Steam/steamapps/common/Apathy_kiwame/package.nw/data/video/自己啓発.webm')
SPEED = 51.6
STEP = 15
FPS = 25
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))


def analyze_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray, cv2.morphologyEx(gray, cv2.MORPH_CLOSE, KERNEL) - gray


def lettering_mask(current, previous, following, time):
    if time < 3.5 or time > 108:
        return np.zeros((690, 960), dtype=np.uint8)
    gray, ink = current
    aligned_previous = cv2.warpAffine(previous[1], np.float32([[1, 0, 0], [0, 1, -SPEED*STEP/FPS]]), (960, 690))
    aligned_following = cv2.warpAffine(following[1], np.float32([[1, 0, 0], [0, 1, SPEED*STEP/FPS]]), (960, 690))
    support = (aligned_previous > 5) | (aligned_following > 5)
    changes = (cv2.absdiff(gray, previous[0]) > 10) | (cv2.absdiff(gray, following[0]) > 10)
    candidate = ((ink > 7) & support & changes).astype(np.uint8)
    candidate[:, :26] = 0
    candidate[:, 938:] = 0
    count, labels, stats, _ = cv2.connectedComponentsWithStats(candidate, 8)
    selected = np.zeros(count, dtype=np.uint8)
    for i in range(1, count):
        _, _, width, height, area = stats[i]
        if 2 <= area <= 2000 and width <= 115 and height <= 55:
            selected[i] = 255
    mask = selected[labels]
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    return cv2.GaussianBlur(mask, (5, 5), .8)


def at(time):
    cap = cv2.VideoCapture(str(SOURCE))
    n = round(time * FPS)
    items = []
    for index in [max(0,n-STEP), n, n+STEP]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = cap.read()
        if not ok:
            raise ValueError('Source frame read failed.')
        items.append(analyze_frame(frame))
    cap.release()
    return lettering_mask(items[1], items[0], items[2], n/FPS)


def write_pgm(path, mask):
    with path.open('xb') as stream:
        stream.write(b'P5\n960 690\n255\n' + mask.tobytes())


def restore_video(output, mask_path, at_time=None):
    """Spatial video restoration avoids crossfade colors leaking into glyphs."""
    if output.exists():
        raise ValueError('Choose a new output path.')
    cap = cv2.VideoCapture(str(SOURCE))
    masks = cv2.VideoCapture(str(mask_path))
    frames = 1 if at_time is not None else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if at_time is not None:
        for reader in (cap,masks):
            reader.set(cv2.CAP_PROP_POS_FRAMES,round(at_time*FPS))
    command = ['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n',
               '-f','rawvideo','-pixel_format','bgr24','-video_size','960x690',
               '-framerate','25','-i','pipe:0']
    command += (['-frames:v','1',str(output)] if at_time is not None else
                ['-c:v','ffv1','-level','3','-pix_fmt','bgr0',str(output)])
    encoder = subprocess.Popen(command,stdin=subprocess.PIPE)
    def restore(frame, mask):
        mask = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        solid = (mask > 12).astype(np.uint8)*255
        restored = cv2.inpaint(frame,solid,5,cv2.INPAINT_TELEA) if solid.any() else frame
        return restored.tobytes()
    try:
        with ThreadPoolExecutor(max_workers=8) as workers:
            pending = deque()
            for n in range(frames):
                ok, frame = cap.read()
                mask_ok, mask = masks.read()
                if not ok or not mask_ok:
                    raise ValueError('Source or mask ended early.')
                pending.append(workers.submit(restore,frame,mask))
                if len(pending) >= 16:
                    encoder.stdin.write(pending.popleft().result())
                if n % 500 == 0:
                    print(f'Restore {n}/{frames}',flush=True)
            while pending:
                encoder.stdin.write(pending.popleft().result())
    finally:
        cap.release()
        masks.release()
        encoder.stdin.close()
    if encoder.wait() != 0:
        raise ValueError('Restoration encoder failed.')
    return {'frames':frames,'method':'Telea spatial video inpainting, radius 5, mask threshold 12'}


def mask_video(output):
    if output.exists():
        raise ValueError('Choose a new output path.')
    cap = cv2.VideoCapture(str(SOURCE))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    command = ['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n',
               '-f','rawvideo','-pixel_format','gray','-video_size','960x690',
               '-framerate','25','-i','pipe:0','-c:v','ffv1','-pix_fmt','gray',str(output)]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
    cache = {}
    loaded = -1
    coverage = []
    try:
        for n in range(frames):
            while loaded < min(frames-1,n+STEP):
                ok, frame = cap.read()
                if not ok:
                    raise ValueError('Source video ended early.')
                loaded += 1
                cache[loaded] = analyze_frame(frame)
            mask = lettering_mask(cache[n], cache[max(0,n-STEP)], cache[min(frames-1,n+STEP)], n/FPS)
            encoder.stdin.write(mask.tobytes())
            coverage.append(int((mask > 127).sum()))
            if n-STEP-1 in cache:
                del cache[n-STEP-1]
            if n % 500 == 0:
                print(f'Mask {n}/{frames}', flush=True)
    finally:
        cap.release()
        encoder.stdin.close()
    if encoder.wait() != 0:
        raise ValueError('Mask encoder failed.')
    result = {'frames':frames,'fps':FPS,'scrollSpeed':SPEED,'neighborFrames':STEP,
              'maxMaskPixels':max(coverage),'meanMaskPixels':sum(coverage)/len(coverage),
              'sourceSha256':sha256(SOURCE.read_bytes()).hexdigest()}
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def english_layout():
    """Reflow the reviewed captions into the original continuous upward motion."""
    path = ROOT / 'work/translation/en/media/self-help.vtt'
    font_path = Path('C:/Windows/Fonts/segoepr.ttf')
    font = _Font(font_path)
    result = []
    previous_end = 0
    # Source paragraph positions measured on its 66-pixel line grid. Keeping
    # these anchors aligns the translated content with the original montage.
    rows = [0,2,4,6,9,13,17,22,27,29,31,35,37,43,48,51,54,56,59,61,63,65,68,71]
    blocks = path.read_text(encoding='utf-8').strip().split('\n\n')[1:-1]
    assert len(rows) == len(blocks)
    for row, block in zip(rows, blocks):
        timing, *text = block.splitlines()
        text = ' '.join(text).replace('\u2026', '...')
        lines = font.wrap(text, 28, 870)
        if len(lines)>1 and font.width(lines[-1],28)<220:
            # Avoid a stranded final word when both complete sentences fit.
            sentences = re.split(r'(?<=[.!?]) +',' '.join(lines[-2:]))
            if len(sentences)==2 and all(font.width(s,28)<=870 for s in sentences):
                lines[-2:] = sentences
        top = 896 + row*66
        if top < previous_end + 30:
            raise ValueError('English paragraph exceeds its source timing slot.')
        for index, line in enumerate(lines):
            result.append({'text':line,'x':40,'documentY':top+index*48})
        previous_end = top+(len(lines)-1)*48+28
    original = ' '.join(' '.join(b.splitlines()[1:]) for b in blocks).replace('\u2026','...')
    assert ' '.join(line['text'] for line in result) == original
    return font_path, result


def render(output, mask, start=0, duration=None, restored=None):
    if output.exists():
        raise ValueError('Choose a new output path.')
    folder = output.parent / (output.stem + '-render')
    if folder.exists():
        raise ValueError('Choose a new render folder.')
    folder.mkdir(parents=True)
    font, lines = english_layout()
    shutil.copyfile(font, folder/'letter-font.ttf')
    if restored is None:
        raise ValueError('Render requires the restored video.')
    chain = [
        '[1:v]settb=1/1000,setpts=N*40+3,format=gbrp[letterless]',
    ]
    draws = []
    for n, line in enumerate(lines):
        name = f'line-{n:02}.txt'
        (folder/name).write_text(line['text'],encoding='utf-8')
        draws.append(f"drawtext=fontfile=letter-font.ttf:textfile={name}:expansion=none:"
                     f"fontcolor=0x181712:fontsize=28:x={line['x']}:y='{line['documentY']}-{SPEED}*t':"
                     "alpha='if(lt(t,104.4),1,max(0,(107.2-t)/2.8))':enable='lt(t,107.2)'")
    # The final book photograph remains original; retain its existing translated
    # title as a small caption, rather than painting over the physical book.
    (folder/'book-title.txt').write_text('The Wonderful Self-Harm Guide',encoding='utf-8')
    draws.append("drawtext=fontfile=letter-font.ttf:textfile=book-title.txt:expansion=none:"
                 "fontcolor=white:fontsize=25:x=(w-tw)/2:y=h-47:box=1:boxcolor=black@0.65:boxborderw=8:"
                 "enable='between(t,110,121)'")
    chain.append('[letterless]'+','.join(draws)+'[out]')
    (folder/'filter.txt').write_text(';\n'.join(chain),encoding='utf-8')
    plan = {'version':'0.8.2-preview','source':str(SOURCE),'mask':str(mask.resolve()),
            'sourceSha256':sha256(SOURCE.read_bytes()).hexdigest(),
            'font':'Segoe Print (rendered only; font not distributed)',
            'fps':FPS,'size':[960,690],'scrollSpeed':SPEED,'lines':lines,
            'sourceParagraphRows':[0,2,4,6,9,13,17,22,27,29,31,35,37,43,48,51,54,56,59,61,63,65,68,71],
            'cleanup':'Telea spatial video inpainting, radius 5, mask threshold 12',
            'restoredVideo':str(restored.resolve()),
            'letterFade':[104.4,107.2], 'bookTitleCaption':[110,121],
            'scope':'Preview only. Main Steam files and saves unchanged.'}
    (folder/'layout.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    command = ['ffmpeg','-nostdin','-hide_banner','-loglevel','warning','-stats','-n',
               '-i',str(SOURCE),'-i',str(restored.resolve()),'-/filter_complex','filter.txt',
               '-map','[out]','-map','0:a:0']
    if start:
        command += ['-ss',str(start)]
    if duration:
        command += ['-t',str(duration)]
    command += ['-c:v','libvpx','-b:v','3M','-crf','10','-qmin','4','-qmax','25',
                '-threads','8','-fps_mode','passthrough','-enc_time_base:v','1/1000',
                '-deadline','good','-cpu-used','3',
                '-pix_fmt','yuv420p','-c:a','copy',str(output.resolve())]
    subprocess.run(command,cwd=folder,check=True)
    if not start and duration is None:
        plan = verify(output)
    return plan


def verify(output):
    # A full preview must retain every video frame and every original audio
    # packet, including its timestamp. Short excerpts are intentionally exempt.
    folder = output.parent / (output.stem + '-render')
    plan = json.loads((folder/'layout.json').read_text(encoding='utf-8'))
    def probe(path, *options):
        return json.loads(subprocess.check_output(
            ['ffprobe','-v','error',*options,'-of','json',str(path)],encoding='utf-8'))
    original_audio = probe(SOURCE,'-select_streams','a:0','-show_packets',
                           '-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,data_hash')
    rendered_audio = probe(output.resolve(),'-select_streams','a:0','-show_packets',
                           '-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,data_hash')
    if original_audio != rendered_audio:
        raise ValueError('Original audio packets or timing changed.')
    original_video = probe(SOURCE,'-select_streams','v:0','-show_packets',
                           '-show_entries','packet=pts,dts,duration')
    rendered_video = probe(output.resolve(),'-select_streams','v:0','-show_packets',
                           '-show_entries','packet=pts,dts,duration')
    if original_video != rendered_video:
        raise ValueError('Original video frame timing changed.')
    info = probe(output.resolve(),'-count_frames','-show_entries',
                 'format=duration:stream=index,codec_name,width,height,avg_frame_rate,nb_read_frames,start_time')
    video = info['streams'][0]
    assert (video['width'],video['height'],video['avg_frame_rate'],video['nb_read_frames']) == (960,690,'25/1','3149')
    assert abs(float(info['format']['duration'])-125.963) < .002
    assert sha256(SOURCE.read_bytes()).hexdigest() == plan['sourceSha256']
    plan.update({'outputSha256':sha256(output.read_bytes()).hexdigest(),
                 'audioPacketsIdentical':True,'audioPacketCount':len(original_audio['packets']),
                 'videoPacketTimingIdentical':True,
                 'probe':info,'output':str(output.resolve())})
    with (folder/'verification.json').open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(plan,indent=2)+'\n')
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--at', type=float)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--mask', type=Path)
    parser.add_argument('--start', type=float, default=0)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--restore', action='store_true')
    parser.add_argument('--restored', type=Path)
    args = parser.parse_args()
    if args.restore:
        if not args.output or not args.mask:
            parser.error('--restore requires --output and --mask')
        print(json.dumps(restore_video(args.output,args.mask,args.at)))
    elif args.verify:
        print(json.dumps(verify(args.verify)))
    elif args.render:
        if not args.output or not args.mask or not args.restored:
            parser.error('--render requires --output, --mask and --restored')
        print(json.dumps(render(args.output,args.mask,args.start,args.duration,args.restored)))
    elif args.at is not None:
        mask = at(args.at)
        print(json.dumps({'time':args.at,'maskPixels':int((mask>127).sum()),'output':str(args.output) if args.output else None}))
        if args.output:
            write_pgm(args.output,mask)
    elif args.output:
        print(json.dumps(mask_video(args.output)))
    else:
        print(json.dumps({'source':str(SOURCE),'fps':FPS,'scrollSpeed':SPEED,'output':None}))


if __name__ == '__main__':
    main()
