#!/usr/bin/env python3
"""Offline-first translation preparation for H2O2 research reports.

v1.4: protected code/commands/paths, bounded batches, fail-open originals,
per-segment cache, visible quality warnings. No remote fallback.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_CACHE = Path.home() / '.cache' / 'h2o2-research-design-html' / 'translation-cache.json'
VALID_BACKENDS = {'apple', 'none', 'command'}
COMMAND = re.compile(r'^\s*(?:\$\s*)?(?:sudo\s+)?(?:echo\s+|python(?:3)?\s+-c\s+|bash\s+-c\s+|sh\s+-c\s+|cat\s+|rm\s+|mv\s+|cp\s+|curl\s+|git\s+|find\s+|grep\s+|sed\s+|awk\s+|chmod\s+|ls\s+|npm\s+|pip\s+|swift\s+|export\s+|docker\s+)', re.I)
# Do not send these pieces to translation; preserve source bytes verbatim.
PROTECTED = re.compile(
    r'(```[\s\S]*?```|`[^`\n]+`|(?<!\w)/(?:[\w.~-]+/)*[\w.~-]+|'
    r'(?<!\w)~/(?:[\w.~-]+/)*[\w.~-]+|'
    r'\b(?:[\w.-]+\.(?:md|txt|json|py|sh|yaml|yml|env))\b|'
    r'\b(?:API_KEY|SECRET_KEY|ACCESS_TOKEN|DB_PASSWORD|SOUL\.md|SKILL\.md)\b|'
    r'\b(?:git\s+commit|git\s+add|git\s+push|Tool\s+Call|Tool\s+Result)\b)', re.I
)


def digest(text, backend, namespace='default'):
    return hashlib.sha256(('v1.4|en>zh-Hans|' + backend + '|' + namespace + '|' + text).encode()).hexdigest()


def check_identifiers(original, translation):
    tokens = set(re.findall(r'`[^`\n]+`|(?<!\w)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+|\b[A-Za-z0-9_.-]+\.(?:md|txt|json|py|sh|yaml|yml)\b|\b[A-Z][A-Z0-9_]{2,}\b', original))
    return all(t in translation for t in tokens)


def quality_ok(original, result):
    if not isinstance(result, str) or not result.strip() or '\ufffd' in result:
        return False
    return check_identifiers(original, result)


def mac_version_ok():
    if platform.system() != 'Darwin':
        return False
    version = platform.mac_ver()[0].split('.')[0]
    return version.isdigit() and int(version) >= 26


def apple_command():
    if not mac_version_ok():
        raise RuntimeError('Apple CLI requires macOS 26+ with en/zh language resources installed.')
    package = HERE / 'apple-translate'
    result = subprocess.run(['swift', 'build', '--package-path', str(package), '-c', 'release'], text=True, capture_output=True, timeout=240)
    if result.returncode:
        diagnostics = result.stdout + '\n' + result.stderr
        errors = [line for line in diagnostics.splitlines() if 'error:' in line]
        raise RuntimeError('Swift build failed: ' + ('\n'.join(errors) or diagnostics[-1000:]))
    binary = package / '.build' / 'release' / 'h2o2-apple-translate'
    if not binary.exists():
        raise RuntimeError('Swift executable missing')
    return [str(binary)]


def run_batch(requests, backend, command=None, argv=None):
    if backend == 'none' or not requests:
        return {}
    argv = argv or (apple_command() if backend == 'apple' else shlex.split(command or ''))
    if not argv:
        raise RuntimeError('--backend command requires --command')
    payload = json.dumps({'requests': [{'id': str(i), 'text': txt} for i, txt in enumerate(requests)]}, ensure_ascii=False)
    proc = subprocess.run(argv, input=payload, text=True, capture_output=True, timeout=180)
    if proc.returncode:
        raise RuntimeError(f'Translator failed ({proc.returncode}): {proc.stderr[-700:]}')
    obj = json.loads(proc.stdout)
    returned = obj.get('translations', [])
    mapping = {row['id']: row['text'] for row in returned}
    if len(returned) != len(requests) or set(mapping) != {str(i) for i in range(len(requests))}:
        raise RuntimeError('Translator response IDs/count mismatch')
    return {txt: mapping[str(i)] for i, txt in enumerate(requests)}


def segments(text):
    return [s for s in re.split(r'(\n\s*\n)', text) if s]


def translatable(part):
    return bool(part.strip() and re.search(r'[A-Za-z]{3,}', part) and not COMMAND.match(part))


def safe_pieces(text):
    """Split, never edit protected code/filenames; retain paragraph separators."""
    for para in segments(text):
        if not para.strip() or COMMAND.match(para) or para.lstrip().startswith('```'):
            yield para, False
            continue
        cursor = 0
        for m in PROTECTED.finditer(para):
            if m.start() > cursor:
                pre = para[cursor:m.start()]
                yield pre, translatable(pre)
            yield m.group(), False
            cursor = m.end()
        if cursor < len(para):
            remainder = para[cursor:]
            yield remainder, translatable(remainder)


def targets_of(data):
    for case in data.get('cases', []):
        inst = case.get('instruction') or {}
        if inst.get('en') and not inst.get('zh'):
            yield inst, 'zh', inst['en']
        for run in case.get('runs', []):
            for e in run.get('events', []):
                if e.get('kind') == 'thinking' and e.get('original') and not e.get('translation_zh'):
                    yield e, 'translation_zh', e['original']


def prepare(data, backend, command=None, cache_path=DEFAULT_CACHE, use_cache=True, batch_size=20, namespace='default'):
    if batch_size < 1:
        raise ValueError('batch_size must be >=1')
    result = copy.deepcopy(data)
    targets = list(targets_of(result))
    cache = {}
    if use_cache and cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding='utf-8'))
        except (ValueError, OSError):
            pass
    missing = []
    for _, _, source in targets:
        for chunk, want in safe_pieces(source):
            if want and digest(chunk, backend, namespace) not in cache and chunk not in missing:
                missing.append(chunk)
    errors, invalid, attempts = [], 0, 0
    argv = None
    if backend != 'none' and missing:
        try:
            argv = apple_command() if backend == 'apple' else shlex.split(command or '')
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
            errors.append(str(exc))
    if backend != 'none' and argv:
        for start in range(0, len(missing), batch_size):
            batch = missing[start:start+batch_size]
            attempts += 1
            try:
                translated = run_batch(batch, backend, command, argv)
            except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
                errors.append(f'batch {start//batch_size+1}: {exc}')
                # Failure isolation: try each segment instead of sacrificing the entire batch.
                translated = {}
                for source in batch:
                    try:
                        translated.update(run_batch([source], backend, command, argv))
                    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired):
                        pass
            for source, chinese in translated.items():
                if quality_ok(source, chinese):
                    cache[digest(source, backend, namespace)] = chinese
                else:
                    invalid += 1
    translated_items=failed_items=unchanged_code=0
    for target, field, source in targets:
        result_parts=[];bad=False;has_prose=False
        for chunk, want in safe_pieces(source):
            if not want:
                result_parts.append(chunk)
            else:
                has_prose=True
                cached = cache.get(digest(chunk, backend, namespace))
                if backend!='none' and cached and quality_ok(chunk, cached):
                    result_parts.append(cached)
                else:
                    bad=True;break
        if not bad and result_parts and backend!='none':
            chinese=''.join(result_parts)
            if not quality_ok(source, chinese):
                bad=True
            else:
                target[field]=chinese
                target['translation_status']='translated_'+backend if has_prose else 'preserved_command'
                translated_items+=1
                if not has_prose:unchanged_code+=1
        if bad or backend=='none':
            target['translation_status']='untranslated' if backend=='none' else 'failed_or_unavailable'
            failed_items+=1
    if use_cache and backend!='none' and cache:
        cache_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temp=cache_path.with_name(cache_path.name+'.tmp')
        with temp.open('w',encoding='utf-8') as f:
            os.chmod(temp,0o600)
            json.dump(cache,f,ensure_ascii=False,indent=1)
        temp.replace(cache_path)
    return result, {'targets':len(targets),'translated':translated_items,'untranslated':failed_items,'protected_code_only':unchanged_code,'invalid_segments':invalid,'batches':attempts,'error':'; '.join(errors) if errors else None}


def main():
    p=argparse.ArgumentParser(description='H2O2 offline-first translation preparation')
    p.add_argument('--input',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--backend',choices=sorted(VALID_BACKENDS),default='apple')
    p.add_argument('--command');p.add_argument('--cache-namespace',default='default')
    p.add_argument('--batch-size',type=int,default=20)
    p.add_argument('--no-cache',action='store_true');p.add_argument('--cache-path',type=Path,default=DEFAULT_CACHE)
    p.add_argument('--self-test',metavar='ENGLISH_TEXT')
    a=p.parse_args()
    if a.backend=='command' and not a.command:p.error('command backend needs --command')
    if a.self_test is not None:
        try:
            text=a.self_test
            if not any(w for _,w in safe_pieces(text)):
                print(json.dumps({'original':text,'zh':text,'status':'preserved_command'},ensure_ascii=False));return
            res=run_batch([text],a.backend,a.command)
            print(json.dumps(res,ensure_ascii=False));return
        except Exception as exc:
            print('Translation unavailable: '+str(exc),file=sys.stderr);sys.exit(2)
    if not a.input or not a.output:p.error('--input and --output required')
    raw=json.loads(a.input.read_text(encoding='utf-8'))
    out,status=prepare(raw,a.backend,a.command,a.cache_path,not a.no_cache,a.batch_size,a.cache_namespace)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(status,ensure_ascii=False))
    if status['error']:print(status['error'],file=sys.stderr)

if __name__=='__main__':main()
