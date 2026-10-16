"""修复版 Engine（挑战 B）。

主故障修复（深挖对象）：缓存键仅含 query，导致「换资料版本却显示旧结论」（R02：
v2 请求命中 v1 缓存）。修复：缓存键改为完整 request+draft 的规范化 JSON。

同时修复的另三个 spec 违约（登记于报告，各附证据）：
- k 先于范围过滤（R03：范围外条目抢占名额）→ 改为先按 doc_ids+snapshot 过滤再排序取 k。
- 仅凭引用 ID 有效就标 supported（R04：证据与答案矛盾仍标 supported）→
  改为独立的规则版语义判据（rule_support），三态：supported / contradicted / insufficient，
  判据无法覆盖时如实 not_checked；依据写入 support_basis 供审阅追溯。
- 未知 doc_ids/snapshot 组合返回 invalid_scope（R07）。
"""
import copy
import json
import re
import time
import uuid

# 玩具级规则判据的词典（非真实语义理解，见 rule_support 文档）
_STRONG_CLAIMS = ('保证', '确保', '一定', '必定', '立即', '全部')
_NEG_MARKERS = ('没有', '未', '不', '仅', '只', '无关', '不含')


def rule_support(answer, evidence):
    """最小规则版语义判据（玩具级；比"仅 ID 有效"更强的独立检查，但不是真实语义理解）。

    - 无证据 → ('insufficient', 'no_evidence')
    - 答案含强断言词（保证/确保/立即…）且证据文本含否定词（没有/未/仅/只…）
      → ('contradicted', 'negation_conflict')
    - 答案中的全部数字都出现在证据文本里 → ('supported', 'number_match')，弱启发式
    - 其他 → ('not_checked', 'no_rule_match')
    """
    texts = [b['text'] for b in evidence]
    joined = ' '.join(texts)
    if not texts:
        return 'insufficient', 'no_evidence'
    if any(w in answer for w in _STRONG_CLAIMS) and any(w in joined for w in _NEG_MARKERS):
        return 'contradicted', 'negation_conflict'
    nums = re.findall(r'\d+', answer)
    if nums and all(n in joined for n in nums):
        return 'supported', 'number_match'
    return 'not_checked', 'no_rule_match'


class FixedEngine:
    def __init__(self):
        self.cache = {}

    def evaluate(self, request, corpus, draft):
        started = time.perf_counter()
        # 修复1（主）：缓存键包含完整请求与 draft；同 query 但不同范围/版本/k/draft 不再互相污染
        key = json.dumps({'request': request, 'draft': draft},
                         sort_keys=True, ensure_ascii=False)
        hit = key in self.cache
        if hit:
            result = copy.deepcopy(self.cache[key])
        else:
            terms = set(request['query'].strip().lower().split())
            # 修复2：先按范围过滤，再排序取 k（范围外条目不再抢占名额）
            in_scope = [b for b in corpus
                        if b['doc_id'] in request['doc_ids']
                        and b['snapshot'] == request['snapshot']]
            # 修复4：未知组合返回 invalid_scope（规格1）
            if not in_scope:
                support, basis = 'insufficient', 'no_evidence'
                result = {'answer': draft['answer'], 'citations': draft['citations'],
                          'evidence': [], 'locator_status': 'invalid',
                          'support_status': support, 'support_basis': basis,
                          'judgment_source': 'rule', 'status': 'invalid_scope'}
                result.update(request_id=str(uuid.uuid4()), request=copy.deepcopy(request),
                              cache_hit=False, elapsed_ms=(time.perf_counter() - started) * 1000,
                              run_kind='offline_replay')
                return result
            ranked = sorted(in_scope, key=lambda b: (-len(terms & set(b['tags'])), b['id']))
            selected = [b for b in ranked[:request['k']] if terms & set(b['tags'])]
            evidence = selected
            citations = draft['citations']
            valid = bool(citations) and set(citations).issubset({b['id'] for b in evidence})
            # 修复3：独立规则版语义判据；只有 ID 有效不再冒充 supported
            support, basis = rule_support(draft['answer'], evidence)
            result = {'answer': draft['answer'], 'citations': citations, 'evidence': evidence,
                      'locator_status': 'valid' if valid else 'invalid',
                      'support_status': support, 'support_basis': basis,
                      'judgment_source': 'rule', 'status': 'ok'}
            self.cache[key] = copy.deepcopy(result)
        result.update(request_id=str(uuid.uuid4()), request=copy.deepcopy(request), cache_hit=hit,
                      elapsed_ms=(time.perf_counter() - started) * 1000, run_kind='offline_replay')
        return result
