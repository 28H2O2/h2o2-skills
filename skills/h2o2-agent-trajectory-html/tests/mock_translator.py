#!/usr/bin/env python3
# JSON protocol mock: for testing orchestration only. NOT a translation engine.
import json,sys
j=json.load(sys.stdin)
json.dump({'translations':[{'id':x['id'],'text':'中文测试：'+x['text']} for x in j['requests']]},sys.stdout,ensure_ascii=False)
