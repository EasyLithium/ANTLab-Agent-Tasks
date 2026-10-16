"""修复回归测试：断言式验证（挑战 B）。

覆盖：
- 主故障回归：同 query 不同快照不再互相污染缓存（R01→R02）。
- 范围过滤：beta 文档在 k=1 时不再丢证据（R03）。
- 语义状态诚实化：support_status=not_checked（R04）。
- 未知组合 invalid_scope（R07）。
- 正常行为回归：R05/R06 证据不变。
- 等价变体：大小写、同输入重放、doc_ids 顺序（标识维度）。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fixed_engine import FixedEngine

data = json.loads((Path(__file__).parent / 'data.json').read_text(encoding='utf-8'))
CORPUS = data['corpus']


def get_case(cid):
    return [c for c in data['cases'] if c['id'] == cid][0]


def ev_ids(out):
    return [b['id'] for b in out['evidence']]


def run_cases(engine_cls):
    engine = engine_cls()
    results = {}
    for c in data['cases']:
        if c['reset_before']:
            engine = engine_cls()
        results[c['id']] = engine.evaluate(c['request'], CORPUS, c['draft'])
    return results


def check(name, cond, detail=''):
    assert cond, f"{name} FAILED: {detail}"
    print(f"PASS: {name}")


def main():
    results = run_cases(FixedEngine)

    # 1. 主故障回归：R01(v1) 后跑 R02(v2)，不得命中 v1 缓存
    r01, r02 = results['R01'], results['R02']
    check("R02 同 query 不同快照不再污染",
          ev_ids(r02) == ['b02'] and r02['cache_hit'] is False,
          f"evidence={ev_ids(r02)} cache_hit={r02['cache_hit']}")
    check("R01 仍返回 v1 证据", ev_ids(r01) == ['b01'], f"evidence={ev_ids(r01)}")

    # 2. 范围过滤：R03（beta, k=1）不再丢证据
    check("R03 范围过滤不丢证据", ev_ids(results['R03']) == ['b03'],
          f"evidence={ev_ids(results['R03'])}")

    # 3. 语义判据（规则版）：矛盾识别、数字匹配、无证据、无法判定
    check("R04 矛盾断言被识别为 contradicted",
          results['R04']['support_status'] == 'contradicted',
          f"support={results['R04']['support_status']}")
    check("R01 数字匹配判为 supported",
          results['R01']['support_status'] == 'supported'
          and results['R01']['support_basis'] == 'number_match',
          f"support={results['R01']['support_status']}/{results['R01'].get('support_basis')}")
    check("R02 数字匹配判为 supported",
          results['R02']['support_status'] == 'supported',
          f"support={results['R02']['support_status']}")
    check("R07 无证据判为 insufficient",
          results['R07']['support_status'] == 'insufficient',
          f"support={results['R07']['support_status']}")
    check("R05 规则无法判定时如实 not_checked",
          results['R05']['support_status'] == 'not_checked',
          f"support={results['R05']['support_status']}")

    # 4. 未知组合 invalid_scope
    check("R07 未知组合返回 invalid_scope",
          results['R07']['status'] == 'invalid_scope', f"status={results['R07']['status']}")

    # 5. 正常行为回归
    check("R05 正常行为保持", ev_ids(results['R05']) == ['b05'], f"evidence={ev_ids(results['R05'])}")
    check("R06 正常行为保持", ev_ids(results['R06']) == ['b06'], f"evidence={ev_ids(results['R06'])}")

    # 6. 等价变体
    eng = FixedEngine()
    base = get_case('R01')
    o1 = eng.evaluate(base['request'], CORPUS, base['draft'])
    req2 = dict(base['request']); req2['query'] = 'Timeout Request Threshold'
    o2 = eng.evaluate(req2, CORPUS, base['draft'])
    check("变体: 大小写等价（证据一致）", ev_ids(o1) == ev_ids(o2), f"{ev_ids(o1)} vs {ev_ids(o2)}")

    o3 = eng.evaluate(dict(base['request']), CORPUS, base['draft'])
    check("变体: 同输入重放命中缓存", o3['cache_hit'] is True and ev_ids(o3) == ev_ids(o1),
          f"cache_hit={o3['cache_hit']}")

    eng2 = FixedEngine()
    req_a = {'query': 'metadata', 'doc_ids': ['alpha', 'beta'], 'snapshot': 'v1', 'k': 2}
    req_b = {'query': 'metadata', 'doc_ids': ['beta', 'alpha'], 'snapshot': 'v1', 'k': 2}
    draft = {'answer': '文档编号为beta。', 'citations': ['b05'], 'origin': 'synthetic_fixture'}
    oa = eng2.evaluate(req_a, CORPUS, draft)
    ob = eng2.evaluate(req_b, CORPUS, draft)
    check("变体: doc_ids 顺序等价（证据一致）", ev_ids(oa) == ev_ids(ob),
          f"{ev_ids(oa)} vs {ev_ids(ob)}")

    print("\n全部断言通过")


if __name__ == '__main__':
    main()
