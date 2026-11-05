#!/usr/bin/env python3
"""Encode a contiguous PNG/JPEG frame sequence to looping GIF and silent MP4."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[-3000:])
    return result.stdout


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                           '-show_entries', 'stream=width,height,nb_read_frames,duration:format=duration',
                           '-of', 'json', str(path)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames-dir', required=True, type=Path)
    parser.add_argument('--pattern', default='%03d.png')
    parser.add_argument('--fps', type=float, default=24)
    parser.add_argument('--out-dir', required=True, type=Path)
    parser.add_argument('--stem', default='ins-live')
    parser.add_argument('--gif-width', type=int, default=720)
    args = parser.parse_args()
    for name in ('ffmpeg', 'ffprobe'):
        if not shutil.which(name):
            parser.error(f'{name} is required on PATH')
    match = re.fullmatch(r'%0([1-8])d\.(png|jpg|jpeg)', args.pattern)
    if not match:
        parser.error('Pattern must be a numbered sequence such as %03d.png')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.stem):
        parser.error('--stem must be a simple filename without directories')
    if not 1 <= args.fps <= 50 or not 64 <= args.gif_width <= 2160:
        parser.error('FPS must be 1–50 for GIF timing, and GIF width 64–2160')
    digits, ext = int(match[1]), match[2]
    frames = sorted(args.frames_dir.glob(f'*.{ext}'))
    numbered = [p for p in frames if re.fullmatch(rf'\d{{{digits}}}\.{ext}', p.name)]
    expected = [f'{i:0{digits}d}.{ext}' for i in range(len(numbered))]
    if len(numbered) < 2 or [p.name for p in numbered] != expected:
        parser.error('Need at least two consecutively numbered frames starting at zero, without gaps')
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    gif, mp4 = out / f'{args.stem}.gif', out / f'{args.stem}.mp4'
    manifest = out / f'{args.stem}.json'
    if any(p.exists() for p in (gif, mp4, manifest)):
        parser.error('Output already exists; choose a new stem or output directory')
    source = args.frames_dir.resolve() / args.pattern
    common = ['ffmpeg', '-v', 'error', '-n', '-framerate', str(args.fps), '-start_number', '0', '-i', str(source)]
    graph = (f"[0:v]scale=w='min({args.gif_width},iw)':h=-1:flags=lanczos,split[a][b];"
             '[a]palettegen=stats_mode=diff[p];'
             '[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle')
    run(common + ['-filter_complex', graph, '-frames:v', str(len(numbered)), '-loop', '0', str(gif)])
    run(common + ['-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-frames:v', str(len(numbered)),
                  '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', str(mp4)])
    reports = {}
    expected_duration = len(numbered) / args.fps
    for path in (gif, mp4):
        info = probe(path)
        stream = info['streams'][0]
        count = int(stream['nb_read_frames'])
        duration = float(info['format']['duration'])
        if count != len(numbered):
            raise RuntimeError(f'{path.name}: decoded {count} frames, expected {len(numbered)}')
        if abs(duration - expected_duration) > max(.12, expected_duration * .025):
            raise RuntimeError(f'{path.name}: unexpected duration {duration}')
        reports[path.suffix[1:]] = {'file': str(path), 'bytes': path.stat().st_size,
                                  'width': stream['width'], 'height': stream['height'],
                                  'frames': count, 'duration_seconds': duration}
    report = {'fps': args.fps, 'source_frames': len(numbered), 'outputs': reports,
              'note': 'Metadata checks do not verify aesthetics, motion quality or seamless looping. MP4 is silent; GIF is not Apple Live Photo.'}
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'manifest': str(manifest), 'outputs': reports}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, KeyError, ValueError) as exc:
        raise SystemExit(str(exc))
