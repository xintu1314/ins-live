#!/usr/bin/env python3
"""Extract timestamped reference samples and an aspect-preserving contact sheet."""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[-3000:])
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    parser.add_argument('--count', type=int, default=12)
    parser.add_argument('--start', type=float, default=0)
    parser.add_argument('--end', type=float)
    args = parser.parse_args()
    for name in ('ffmpeg', 'ffprobe'):
        if not shutil.which(name):
            parser.error(f'{name} is required on PATH')
    if not args.input.is_file():
        parser.error('Input file does not exist')
    if not 2 <= args.count <= 24:
        parser.error('--count must be 2–24')
    meta = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(args.input)]))
    video = next((s for s in meta['streams'] if s['codec_type'] == 'video'), None)
    if not video:
        parser.error('Input has no video stream')
    duration = float(meta['format']['duration'])
    end = duration if args.end is None else args.end
    if not 0 <= args.start < end <= duration + .001:
        parser.error('Require 0 <= start < end <= duration')
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob('frame-*.jpg')) or (out / 'contact.jpg').exists() or (out / 'samples.json').exists():
        parser.error('Output contains prior samples; choose a new directory')
    times = [args.start + (end - args.start) * i / args.count for i in range(args.count)]
    entries = []
    for i, timestamp in enumerate(times):
        target = out / f'frame-{i:03d}.jpg'
        run(['ffmpeg', '-v', 'error', '-n', '-i', str(args.input), '-ss', f'{timestamp:.6f}',
             '-map', '0:v:0', '-frames:v', '1', '-vf',
             'scale=360:480:force_original_aspect_ratio=decrease,pad=360:480:(ow-iw)/2:(oh-ih)/2:color=black',
             '-q:v', '2', str(target)])
        if not target.is_file():
            raise RuntimeError(f'No frame extracted at {timestamp:.6f}s')
        entries.append({'file': target.name, 'requested_time_seconds': round(timestamp, 6)})
    cols = min(4, args.count)
    rows = math.ceil(args.count / cols)
    run(['ffmpeg', '-v', 'error', '-n', '-framerate', '1', '-start_number', '0',
         '-i', str(out / 'frame-%03d.jpg'), '-vf', f'tile={cols}x{rows}:nb_frames={args.count}',
         '-frames:v', '1', '-q:v', '2', str(out / 'contact.jpg')])
    report = {'input': str(args.input.resolve()), 'duration': duration,
              'width': video['width'], 'height': video['height'],
              'note': 'Times are requested seek times; decoded frames follow source timestamps. Contact cells are read left-to-right, top-to-bottom.',
              'samples': entries}
    (out / 'samples.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'contact': str(out / 'contact.jpg'), 'samples': str(out / 'samples.json')}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, KeyError, ValueError) as exc:
        raise SystemExit(str(exc))
