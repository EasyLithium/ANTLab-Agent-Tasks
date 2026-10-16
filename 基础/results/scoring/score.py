"""判分脚本：解析 runs/ 下的 40 次主结果，输出逐例表 results/results.csv。

机械检查项（本脚本可自动完成）：
  1. JSON 可解析且 answer 非空；
  2. citations 均来自本次实际输入段落（original_passage_ids）；
  3. 耗时、usage 来源记录。

语义项（引用原文是否支撑结论）需人工复核，本脚本不自动判定，只保留字段供人工填写。
"""
import json, csv, re, sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parents[2]          # 基础/
RUNS = BASE / 'runs'
OUT = BASE / 'results'
SCORING = OUT / 'scoring'


def parse_content(content):
    """从模型输出提取 answer 与 citations，失败返回 ('', [])。"""
    try:
        obj = json.loads(content)
        return obj.get('answer', ''), obj.get('citations', [])
    except (json.JSONDecodeError, AttributeError):
        m = re.search(r'\{.*\}', content, re.S)
        if m:
            try:
                obj = json.loads(m.group(0))
                return obj.get('answer', ''), obj.get('citations', [])
            except json.JSONDecodeError:
                pass
        return '', []


def main():
    rows = []
    for path in sorted(RUNS.glob('*.json')):
        r = json.loads(path.read_text(encoding='utf-8'))
        input_ids = set(r.get('original_passage_ids', []))
        content = ''
        try:
            content = r['response']['choices'][0]['message']['content']
        except (KeyError, TypeError, IndexError):
            pass
        answer, citations = parse_content(content)
        bad = [c for c in citations if c not in input_ids]
        usage = r.get('usage') or {}
        rows.append({
            'run_id': r['run_id'],
            'case_id': r['case_id'],
            'condition': r['condition'],
            'variant': r['variant'],
            'status': r.get('status', ''),
            'answer': answer,
            'citations': ';'.join(citations),
            'citations_valid': '是' if not bad else '否',
            'json_valid': '是' if (answer and isinstance(citations, list)) else '否',
            'elapsed_seconds': round(r.get('elapsed_seconds') or 0, 2),
            'prompt_tokens': usage.get('prompt_tokens', ''),
            'completion_tokens': usage.get('completion_tokens', ''),
        })

    OUT.mkdir(exist_ok=True)
    SCORING.mkdir(exist_ok=True)
    fields = ['run_id', 'case_id', 'condition', 'variant', 'status', 'answer',
              'citations', 'citations_valid', 'json_valid',
              'elapsed_seconds', 'prompt_tokens', 'completion_tokens']
    with open(OUT / 'results.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    total = len(rows)
    print(f"共 {total} 条记录")
    print(f"JSON 有效(answer 非空): {sum(1 for r in rows if r['json_valid']=='是')}")
    print(f"引用全部来自输入: {sum(1 for r in rows if r['citations_valid']=='是')}")
    print(f"平均耗时: {sum(r['elapsed_seconds'] for r in rows)/total:.2f}s")

    # 按题聚合，观察各条件答案是否一致（配对观察）
    by_case = defaultdict(dict)
    for r in rows:
        by_case[r['case_id']][r['condition'] + '/' + r['variant']] = r['answer']
    print("\n== 各题各条件答案 ==")
    for cid in sorted(by_case):
        print(f"{cid}: " + " | ".join(f"{k}={v}" for k, v in sorted(by_case[cid].items())))


if __name__ == '__main__':
    main()
