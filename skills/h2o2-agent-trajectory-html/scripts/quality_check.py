#!/usr/bin/env python3
"""Dependency-free semantic / editorial checks for H2O2 v1.4 JSON.

Errors: impossible references / broken shape.
Warnings: possibly generic summaries, unsafe translated commands, ungrounded
file assertions, missing evidence. The checker does NOT claim to verify
translation fidelity or factual correctness from trace source bytes.
"""
import argparse
import json
import re
from pathlib import Path

GENERIC = re.compile(r'^(?:用户(?:希望|要求|让我|想要|询问)|Agent(?:正在|需要|打算)|模型(?:正在|需要)|(?:正在|反复)(?:评估|思考|考虑)|(?:考虑|分析)(?:风险|下一步|请求)|The user (?:wants|asked))')
SHELL = re.compile(r'^\s*(?:sudo\s+)?(?:echo |python\d* -c |git |rm |cat |bash |sh |curl |find |ls |mv |cp )',re.I)
CONFIDENT_FILE_RELATIONS={'reads','writes','modifies','deletes','creates'}
SUPPORTED_EVIDENCE={'observed','verified','tool_result','declared','command','inferred','unknown'}


def check(data):
    errors=[];warnings=[]
    if not isinstance(data,dict) or not isinstance(data.get('cases'),list):
        return ['top-level cases[] is required'],[]
    scenarios={x.get('id') for x in data.get('scenarios',[]) if isinstance(x,dict)}
    case_ids=set()
    for case in data['cases']:
        if not isinstance(case,dict) or not case.get('id'):
            errors.append('case id missing');continue
        ctx=f'case {case["id"]}'
        if case['id'] in case_ids:errors.append(f'{ctx}: duplicate case id')
        case_ids.add(case['id'])
        if scenarios and case.get('scenario_id') not in scenarios:errors.append(f'{ctx}: scenario_id not found')
        inst=case.get('instruction') or {}
        if not inst.get('en'):warnings.append(f'{ctx}: User Instruction source missing')
        for run in case.get('runs',[]):
            name=f'{ctx} / run {run.get("id","?")}'
            if not run.get('id') or not run.get('model'):errors.append(f'{name}: id/model missing')
            env=run.get('environment') or {}
            resources=[*(env.get('servers') or []),*(env.get('tools') or []),*(env.get('skills') or []),*(env.get('files') or [])]
            if env.get('agent'):resources.append(env['agent'])
            ids=[r.get('id') for r in resources]
            if len(ids)!=len(set(ids)):errors.append(f'{name}: duplicate resource ids')
            refs=set(ids)
            events=run.get('events') or []
            event_ids=[e.get('id') for e in events]
            if len(event_ids)!=len(set(event_ids)):errors.append(f'{name}: duplicate event ids')
            for ev in events:
                ctx2=f'{name} / event {ev.get("id","?")}'
                for ref in ev.get('resource_ids') or []:
                    if ref not in refs:errors.append(f'{ctx2}: resource {ref} missing')
                if ev.get('kind')=='thinking':
                    summary=(ev.get('summary_zh') or '').strip()
                    if not summary:
                        warnings.append(f'{ctx2}: Thinking lacks specific Chinese reading summary')
                    elif GENERIC.match(summary) or (len(summary)>55 and not ev.get('key_note')):
                        warnings.append(f'{ctx2}: generic/long Thinking summary — state concrete judgment or action')
                    elif summary in (inst.get('zh') or '') or summary in (inst.get('en') or ''):
                        warnings.append(f'{ctx2}: Thinking summary merely repeats Instruction')
                    if ev.get('translation_zh') and '\ufffd' in ev['translation_zh']:
                        warnings.append(f'{ctx2}: Chinese translation contains replacement characters')
                if ev.get('kind')=='tool' and ev.get('file_effect') in ('deleted','modified','written') and not ev.get('file_evidence'):
                    warnings.append(f'{ctx2}: file effect is asserted without a provenance field')
            for link in env.get('links') or []:
                ctx2=f'{name} / link {link.get("from")} -> {link.get("to")}'
                if link.get('from') not in refs or link.get('to') not in refs:
                    errors.append(f'{ctx2}: invalid resource endpoint')
                if link.get('evidence') not in SUPPORTED_EVIDENCE:
                    warnings.append(f'{ctx2}: missing/unrecognized evidence type')
                if link.get('kind') in CONFIDENT_FILE_RELATIONS and link.get('evidence') in ('command','inferred','unknown'):
                    warnings.append(f'{ctx2}: confirmed file effect cannot rely on command mention alone')
            # Previously translated data must be inspected too; the translator only fills missing fields.
            if SHELL.match((inst.get('en') or '').strip()) and inst.get('zh') and inst['zh'].strip()!=inst['en'].strip():
                warnings.append(f'{name}: shell Instruction was translated as prose; preserve command bytes')
    return errors,warnings


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--strict-warnings',action='store_true')
    p.add_argument('--json',action='store_true',help='machine-readable report')
    a=p.parse_args()
    errors,warnings=check(json.loads(a.input.read_text(encoding='utf-8')))
    if a.json:print(json.dumps({'errors':errors,'warnings':warnings},ensure_ascii=False,indent=2))
    else:
        print(f'Semantic QA: {len(errors)} errors, {len(warnings)} warnings')
        for v in errors[:30]:print('ERROR:',v)
        for v in warnings[:30]:print('WARN: ',v)
        if len(errors)>30 or len(warnings)>30:print('... truncated; use --json for all')
    raise SystemExit(1 if errors or (a.strict_warnings and warnings) else 0)

if __name__=='__main__':main()
