#!/usr/bin/env python3
"""Optional local migration helper for old AgentCanary v1.3 HTML exports.

Reads ONLY embedded JSON, does not execute source HTML. Select cases to limit output.
Not a general OpenTelemetry converter. Uses conservative evidence classifications.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re

class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__();self.active=False;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script' and dict(attrs).get('id')=='report-data':self.active=True
    def handle_endtag(self,tag):
        if tag=='script' and self.active:self.active=False
    def handle_data(self,data):
        if self.active:self.parts.append(data)


def normalize(source,case_numbers=None):
    cases=[];cats=[];seen_categories=set()
    for case in source.get('cases',[]):
        if case_numbers and int(case.get('number',-1)) not in case_numbers:continue
        category=case.get('category','其他')
        if category not in seen_categories:
            cats.append({'id':category,'name':category});seen_categories.add(category)
        cc={'id':str(case['number']),'scenario_id':category,'name':case.get('name') or case.get('id') or str(case['number']),
            'instruction':{'en':'','zh':''},'runs':[]}
        for run in case.get('runs',[]):
            inst=run.get('instruction') or {}
            if not cc['instruction'].get('en'):
                cc['instruction']={'en':inst.get('en',''),'zh':inst.get('zh','')}
            kind={'成功':'success','失败':'defended','部分成功':'partial','未知':'unknown'}.get(run.get('outcome'),'unknown')
            outcome={'success':'攻击成功','defended':'攻击失败','partial':'部分成功','unknown':'结果未知'}[kind]
            env={'agent':{'id':'agent','name':'OpenClaw Agent','detail':run.get('model_label') or run.get('model') or ''},
                 'tools':[],'servers':[],'skills':[],'files':[],'links':[],'capabilities_complete':False}
            ids={'agent'};name_to_id={}
            for t in (run.get('scene',{}).get('tools') or []):
                name=t['name'];id='tool:'+name
                if id not in ids:
                    env['tools'].append({'id':id,'name':name,'used':True,'status':'observed'});ids.add(id)
                name_to_id[name]=id
            for f in run.get('scene',{}).get('files') or []:
                path=f.get('path','')
                if not path:continue
                id='file:'+path
                if id not in ids:
                    base=path.split('/')[-1] if path else path
                    env['files'].append({'id':id,'name':base or path,'detail':path,'status':'observed' if f.get('events') else 'configured', 'used':bool(f.get('events'))});ids.add(id)
            evs=[];links=[];linkset=set()
            for n,ev in enumerate(run.get('events') or []):
                role=ev.get('kind') or 'unknown'
                k={'answer':'final','tool':'tool','thinking':'thinking','user':'user'}.get(role,'error')
                src=str(ev.get('original',''))
                content={'id':'e'+str(n),'kind':k,'actor':'user' if k=='user' else 'tool' if k=='tool' else 'agent',
                         'title':{'user':'用户输入','thinking':'Thinking','tool':'工具调用','final':'最终回答','error':'运行异常'}[k],
                         'original':src,'translation_zh':ev.get('translation_zh',''),'resource_ids':['agent']}
                if k=='thinking':
                    # An extractor cannot truthfully infer nuanced reasoning by taking the first sentence.
                    # Leave missing and let an agent write a specific evidence-grounded sentence; QA flags it.
                    content['summary_zh']=''
                elif k=='user':content['summary_zh']=''
                elif k=='final':content['summary_zh']='查看最终回答'
                elif k=='tool':
                    name=ev.get('tool','tool');tid=name_to_id.get(name,'tool:'+name)
                    if tid not in ids:env['tools'].append({'id':tid,'name':name,'used':True,'status':'observed'});ids.add(tid)
                    invocation=('agent',tid,'invokes','observed')
                    if invocation not in linkset:
                        links.append({'from':'agent','to':tid,'kind':'invokes','evidence':'observed'});linkset.add(invocation)
                    args=ev.get('arguments') or {};result=str(ev.get('result') or '')
                    target=args.get('path','') or args.get('file','')
                    if target:target=str(target)
                    label=target.split('/')[-1] if target else ('shell' if name=='exec' else name)
                    content.update({'tool':name,'title':name+' → '+label,'args':json.dumps(args,ensure_ascii=False,indent=2),
                                    'result':result,'summary_zh':'工具返回成功' if result.startswith('Successfully') else '查看工具返回',
                                    'resource_ids':['agent',tid], 'file_evidence':'tool_result' if target else 'unknown'})
                    if target:
                        fid='file:'+target
                        if fid not in ids:
                            env['files'].append({'id':fid,'name':label,'detail':target,'status':'observed','used':True});ids.add(fid)
                        content['resource_ids'].append(fid)
                        read_observed = bool(result.strip()) and not re.search(r'(?im)^\s*(?:error\b|enoent\b|eacces\b)|no such file or directory|permission denied', result)
                        relkind='reads' if name=='read' and read_observed else 'writes' if name=='write' and result.lower().startswith('successfully wrote') else 'mentions'
                        evidence='tool_result' if relkind!='mentions' else 'command'
                        content['file_evidence']=evidence
                        relation=(tid,fid,relkind,evidence)
                        if relation not in linkset:links.append({'from':tid,'to':fid,'kind':relkind,'evidence':evidence});linkset.add(relation)
                    else:
                        # Evidence from explicitly parsed command references: mention only, not verified access.
                        command=str(args.get('command',''))
                        candidates=re.findall(r'(?<![\w])(?:~?/|\./)[\w./~-]+',command)
                        for path in dict.fromkeys(candidates):
                            path=path.rstrip(',.\\')
                            if path in ('/dev/null','./'):continue
                            fid='file:'+path
                            if fid not in ids:env['files'].append({'id':fid,'name':path.split('/')[-1] or path,'detail':path,'status':'mentioned','used':True});ids.add(fid)
                            content['resource_ids'].append(fid)
                            relation=(tid,fid,'mentions','command')
                            if relation not in linkset:links.append({'from':tid,'to':fid,'kind':'mentions','evidence':'command'});linkset.add(relation)
                    # A missing-file error does not establish a successful deletion.
                    # Keep shell targets as mentions until a normalizer can verify
                    # an explicit target-specific success or before/after snapshot.
                evs.append(content)
            env['links']=links
            cc['runs'].append({'id':run.get('id','run-'+str(len(cc['runs'])+1)),
                'model':run.get('model_label') or run.get('model') or 'Unknown',
                'outcome':{'kind':kind,'label':outcome},
                'highlight':run.get('observation') or '',
                'environment':env,'events':evs,
                'metadata':{'source':run.get('metadata',{}).get('source'),'grading':run.get('grading'), 'original_batch':run.get('batch')}})
        if cc['runs']:cases.append(cc)
    return {'title':source.get('title','AgentCanary复现'),'scenarios':cats,'cases':cases,'demo':False}


def main():
    ap=argparse.ArgumentParser(description='Migrate embedded AgentCanary v1.3 JSON without running untrusted HTML')
    ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cases',default='',help='Comma-separated numeric cases; blank for all')
    a=ap.parse_args();parser=ScriptParser();parser.feed(a.input.read_text(encoding='utf-8'))
    if not parser.parts:raise SystemExit('No report-data script element found; unsupported export')
    raw=json.loads(''.join(parser.parts))
    filt={int(x.strip()) for x in a.cases.split(',') if x.strip()} if a.cases else None
    result=normalize(raw,filt);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Imported {len(result["cases"])} cases, {sum(len(x["runs"]) for x in result["cases"])} runs (summaries need review)')

if __name__=='__main__':main()
