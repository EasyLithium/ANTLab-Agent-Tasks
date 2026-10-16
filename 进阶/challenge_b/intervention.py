"""区分性干预与修复验证。

先于代码检查记录的两个假说：
H1（缓存污染）：缓存键只含 query，同 query 不同范围/版本互相命中旧缓存。
   预测：全新引擎重跑 R02（v2 请求）应返回 b02(v2)；而共享引擎（R01 后跑 R02）返回 b01(v1)。
H2（排序/范围逻辑错）：即使无缓存，v2 请求也错误返回 v1 证据。
   预测：全新引擎重跑 R02 仍返回 b01(v1)。
干预后结论看输出。
"""
import json
import sys

sys.path.insert(0, '.')
from challenge import Engine as Buggy
from fixed_engine import FixedEngine

data = json.load(open('data.json', encoding='utf-8'))


def get_case(cid):
    return [c for c in data['cases'] if c['id'] == cid][0]


print("=== 区分性干预（先预测后执行） ===")
print("预测 H1: 全新引擎 R02 -> evidence=[b02], cache_hit=False")
print("预测 H2: 全新引擎 R02 -> evidence=[b01] 或空")
r02 = get_case('R02')
fresh = Buggy()
out = fresh.evaluate(r02['request'], data['corpus'], r02['draft'])
print(f"实际: R02 全新 Buggy 引擎 -> evidence={[b['id'] for b in out['evidence']]} cache_hit={out['cache_hit']}")
print("结论: " + ("H1 成立：无缓存时行为正确，元凶是缓存键过窄" if [b['id'] for b in out['evidence']] == ['b02'] else "H2 成立"))

print("\n=== 修复版引擎全用例 ===")
fixed = FixedEngine()
for c in data['cases']:
    if c['reset_before']:
        fixed = FixedEngine()
    o = fixed.evaluate(c['request'], data['corpus'], c['draft'])
    print(f"  {c['id']}: status={o['status']} evidence={[b['id'] for b in o['evidence']]} "
          f"locator={o['locator_status']} support={o['support_status']} cache_hit={o['cache_hit']}")

print("\n=== 等价变体（同一输入不同大小写/顺序，缓存应复用或等价） ===")
v = FixedEngine()
base = get_case('R01')
o1 = v.evaluate(base['request'], data['corpus'], base['draft'])
req2 = dict(base['request']); req2['query'] = 'Timeout Request Threshold'  # 大小写变体（归一化后等价）
o2 = v.evaluate(req2, data['corpus'], base['draft'])
print(f"  变体1(大小写): evidence1={[b['id'] for b in o1['evidence']]} evidence2={[b['id'] for b in o2['evidence']]} "
      f"cache_hit2={o2['cache_hit']} (期望: 相同证据且命中缓存)")
req3 = dict(base['request']); req3['doc_ids'] = ['alpha']  # 相同顺序
o3 = v.evaluate(req3, data['corpus'], base['draft'])
print(f"  变体2(重放同输入): cache_hit={o3['cache_hit']} (期望 True)")
