"""Measure the original ending's per-channel deformation and shading; no pixel edits.

Dry-run by default. --output writes numerical effect data for the native renderer.
The original Japanese lettering is only a registration reference, never output.
"""
import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from steam_game import ROOT


def analyze(assets):
    spec = json.loads((ROOT / 'work/ui/rpg-game-over.json').read_text(encoding='utf-8'))
    for key, digest in [('animated_source', 'animated_sha256'), ('still_source', 'still_sha256')]:
        if sha256((assets / spec[key]).read_bytes()).hexdigest() != spec[digest]:
            raise ValueError('Unexpected original ending reference.')
    original = Image.open(assets / spec['animated_source'])
    base = cv2.resize(np.array(Image.open(assets / spec['still_source']).convert('L')),
                      (640, 460), interpolation=cv2.INTER_AREA)
    yy, xx = np.mgrid[:460, :640].astype(np.float32)
    gx, gy = np.meshgrid(np.arange(0, 641, 4, dtype=np.float32),
                         np.arange(176, 289, 4, dtype=np.float32))
    gx = np.minimum(gx, 639)
    solver = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    solver.setFinestScale(0)
    solver.setGradientDescentIterations(80)
    solver.setVariationalRefinementIterations(25)
    output, errors, raw_errors, motions, shading = [], [], [], [], []
    for index in range(original.n_frames):
        original.seek(index)
        target = np.array(original.convert('RGB'))
        fields = np.empty((*gx.shape, 9), dtype=np.float32)
        for channel in range(3):
            target_channel = np.ascontiguousarray(target[:, :, channel])
            # Backward flow: each output pixel samples the unwarped reference.
            flow = solver.calc(target_channel, base, None)
            flow = cv2.GaussianBlur(flow, (7, 7), 1.2)
            warped = cv2.remap(base, xx + flow[:, :, 0], yy + flow[:, :, 1],
                               cv2.INTER_LINEAR).astype(np.float32)
            observed = target_channel.astype(np.float32)
            energy = cv2.GaussianBlur(warped * warped, (41, 41), 0)
            gain = cv2.GaussianBlur(warped * observed, (41, 41), 0) / (energy + 1)
            gain = np.clip(gain, 0, 1.5)
            for component, data in enumerate((flow[:, :, 0], flow[:, :, 1], gain)):
                fields[:, :, channel * 3 + component] = cv2.remap(data, gx, gy, cv2.INTER_LINEAR)
            mask = (target_channel > 20) | (warped > 20)
            errors.append(float(np.abs(warped * gain - observed)[mask].mean()))
            raw_errors.append(float(np.abs(base.astype(np.float32) - observed)[mask].mean()))
        packed = fields.copy()
        packed[:, :, [0, 1, 3, 4, 6, 7]] *= 256
        packed[:, :, [2, 5, 8]] *= 4096
        packed = np.rint(packed).clip(-32768, 32767).astype('<i2')
        output.append(base64.b64encode(packed.tobytes()).decode('ascii'))
        foreground = fields[5:23, 15:145]
        motions.append(float(np.percentile(np.abs(foreground[:, :, [0, 1, 3, 4, 6, 7]]), 95)))
        shading.append(float(np.percentile(foreground[:, :, [2, 5, 8]], 10)))
    if original.n_frames != 78:
        raise ValueError('Unexpected frame count.')
    return {'width': 640, 'height': 460, 'frameMs': 50, 'step': 4, 'y0': 176,
            'gridWidth': gx.shape[1], 'gridHeight': gx.shape[0], 'channelsPerNode': 9,
            'flowScale': 256, 'gainScale': 4096, 'frames': output,
            'analysis': {'referenceGifSha256': spec['animated_sha256'],
                         'referenceStillSha256': spec['still_sha256'],
                         'opencv': cv2.__version__, 'method': 'DIS backward optical flow per RGB channel; smooth multiplicative shading',
                         'referenceReconstructionMeanAbsoluteError': round(float(np.mean(errors)), 3),
                         'unwarpedReferenceMeanAbsoluteError': round(float(np.mean(raw_errors)), 3),
                         'maximumFrame95PercentDisplacementPx': round(max(motions), 3),
                         'minimumFrame10PercentGain': round(min(shading), 3)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = analyze(args.assets)
    print(json.dumps({'dry_run': args.output is None, 'frames': len(result['frames']),
                      'analysis': result['analysis'], 'output': str(args.output) if args.output else None}))
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, separators=(',', ':'))
            stream.write('\n')


if __name__ == '__main__':
    main()
