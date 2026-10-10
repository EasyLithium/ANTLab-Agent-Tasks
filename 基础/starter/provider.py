import os, json, time, urllib.request, urllib.error
from urllib.parse import urlparse

def call_model(messages, config, mock=False):
    if mock:
        return {'status':'mock','elapsed_seconds':0.0,
                'response':{'choices':[{'message':{'content':'{"answer":"MOCK_NOT_EVIDENCE","citations":[]}'}}]},
                'usage':None,'http_status':None}
    endpoint=config['endpoint']
    scheme=urlparse(endpoint).scheme
    if scheme not in ('https','http'):
        raise ValueError('endpoint必须为http或https')
    # 本地 llama.cpp 通常无需密钥；若设置 ASSESSMENT_API_KEY 则附加 Bearer，否则不发送 Authorization。
    key=os.environ.get('ASSESSMENT_API_KEY','')
    params=config.get('parameters',{})
    if not isinstance(params,dict) or set(params)&{'messages','model','stream'}:
        raise ValueError('parameters不可覆盖messages/model/stream')
    body={'model':config['model'],'messages':messages,'stream':False,**params}
    headers={'Content-Type':'application/json'}
    if key:
        headers['Authorization']='Bearer '+key
    req=urllib.request.Request(endpoint, data=json.dumps(body,ensure_ascii=False).encode(),
                               headers=headers)
    start=time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=float(config.get('timeout_seconds',90))) as response:
            raw=response.read().decode('utf-8'); status=response.status
        try: parsed=json.loads(raw)
        except json.JSONDecodeError:
            return {'status':'invalid_provider_json','elapsed_seconds':time.perf_counter()-start,
                    'response':raw,'usage':None,'http_status':status}
        return {'status':'ok','elapsed_seconds':time.perf_counter()-start,'response':parsed,
                'usage':parsed.get('usage') if isinstance(parsed,dict) else None,'http_status':status}
    except urllib.error.HTTPError as e:
        # 不保存错误页正文，避免意外收录请求凭据；成功模型响应原样保存。
        return {'status':'http_error','elapsed_seconds':time.perf_counter()-start,
                'http_status':e.code,'error':'HTTP '+str(e.code),'response':None,'usage':None}
    except (urllib.error.URLError,TimeoutError) as e:
        return {'status':'transport_error','elapsed_seconds':time.perf_counter()-start,
                'http_status':None,'error':type(e).__name__,'response':None,'usage':None}
