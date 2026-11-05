#!/usr/bin/env python3
"""Check project records and file locks; never certifies visual quality or consent."""
import argparse
import hashlib
import json
from pathlib import Path

STAGES = ['proposals', 'selected', 'reference', 'keyframe', 'motion', 'delivery']
SKILL = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(value, message):
    if not value:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def local_file(root, value):
    need(text(value), 'Missing project evidence path')
    path = (root / value).resolve()
    need(path.is_relative_to(root), 'Evidence must stay inside project')
    need(path.is_file(), f'Missing evidence: {value}')
    return path


def ref_file(value):
    need(text(value), 'Missing reference path')
    path = (SKILL / value).resolve()
    need(path.is_relative_to(SKILL) and path.is_file(), f'Missing skill reference: {value}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('--source', type=Path, required=True)
    init.add_argument('--project-dir', type=Path, required=True)
    check = commands.add_parser('check')
    check.add_argument('record', type=Path)
    check.add_argument('--stage', choices=STAGES, required=True)
    check.add_argument('--seal', action='store_true')
    args = parser.parse_args()
    if args.command == 'init':
        source = args.source.resolve()
        need(source.is_file(), 'Source does not exist')
        root = args.project_dir.resolve()
        root.mkdir(parents=True, exist_ok=True)
        record = root / 'project.json'
        need(not record.exists(), 'Project already exists; do not overwrite selection')
        data = {'version': 1, 'source': {'path': str(source), 'sha256': digest(source)},
                'options': [], 'selection': None, 'checks': {}}
        record.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(record)
        return
    record = args.record.resolve()
    root = record.parent
    data = json.loads(record.read_text())
    source = Path(data['source']['path'])
    need(source.is_file() and digest(source) == data['source']['sha256'],
         'Source changed: create a new task or explicitly rebind the confirmed replacement')
    limit = STAGES.index(args.stage)
    options = data['options']
    need(isinstance(options, list) and 1 <= len(options) <= 3, 'Record up to three text proposals')
    if len(options) != 3:
        need(text(data.get('proposal_shortfall_reason')), 'Fewer than three requires a photo-specific reason')
    need(len({o['id'] for o in options}) == len(options), 'Option ids must be distinct')
    # Different ids alone do not prove creative difference; require written photo relations.
    for option in options:
        for key in ['effect_id', 'placement', 'interaction', 'motion', 'palette', 'reason']:
            need(text(option.get(key)), f'Option {option.get("id")}: missing {key}')
        need(option.get('references'), 'Each option needs a concrete reference')
        for value in option['references']:
            ref_file(value)
    if limit >= 1:
        selected = data.get('selection') or {}
        need(selected.get('option_id') in [o['id'] for o in options], 'No selected current option')
        need(selected.get('source_sha256') == data['source']['sha256'], 'Selection belongs to another photo')
        need(text(selected.get('user_message')), 'Record the actual current user selection; never infer it')
    checks = data.get('checks', {})
    for stage in ['reference', 'keyframe', 'motion', 'delivery']:
        if STAGES.index(stage) > limit:
            break
        report = checks.get(stage, {})
        need(report.get('passed') is True, f'{stage}: review is missing or failed')
        need(report.get('evidence'), f'{stage}: evidence missing')
        for item in report['evidence']:
            local_file(root, item)
        if stage == 'reference':
            need(report.get('reference_roles'), 'Reference roles missing')
            for role in report['reference_roles']:
                ref_file(role.get('path'))
                for key in ['role', 'inherit', 'exclude']:
                    need(text(role.get(key)), f'Reference role lacks {key}')
        else:
            need(text(report.get('observations')), f'{stage}: observations missing')
    if limit >= 3:
        keyframe = checks['keyframe']
        need(keyframe.get('lock_files'), 'Keyframe needs shared assets/layout lock files')
        hashes = {name: digest(local_file(root, name)) for name in keyframe['lock_files']}
        if args.seal:
            need(args.stage == 'keyframe', '--seal only applies to the keyframe review')
            keyframe['locked_sha256'] = hashes
            record.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        elif limit >= 4:
            need(keyframe.get('locked_sha256') == hashes,
                 'Visual master changed or was not sealed; review and seal keyframe before motion')
    elif args.seal:
        raise ValueError('--seal only applies to keyframe review')
    print(json.dumps({'stage': args.stage, 'record_checks': 'passed',
                      'limitation': 'Checks records/files only, not actual consent, tool viewing, or aesthetics.'}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise SystemExit(str(exc))
