"""待候选人实现。避免读取dev_answers或题号/condition来构造答案。

冻结版本（v5）：条件严格筛选含批次代号关联 + 逐字摘录 + 类型分流计算 + 引用完整性。
improve()：按词法相关度重排段落（最相关在前），测试首因效应假设。
"""
import json
import re

_SYSTEM = (
    "你是文档信息核验助手。只能依据给定段落原文回答，禁止编造、禁止使用外部知识。"
    "作答步骤："
    "①严格筛选：与问题条件（项目、版本、月份、批次类型）不一致的段落是干扰项，必须忽略（尤其注意项目名不同、批次类型不同的段落）；"
    "但'批次XX的复核补页'这类补充页只写批次代号，批次代号一致就是同一批次，要一起使用。"
    "②定位并逐字摘录所有相关数字（可能在不同段落，原样抄出、不改数字、不心算）："
    "问'率/比例/支持率'→分子÷分母（分子=获支持数，分母=总数）；"
    "问'少多少/多多少/差值'→两个数相减取绝对值，结果一定为正数（如 10 与 7 的差是 3，不是 -3）；"
    "问具体编号/快照/数值→直接摘录该值。"
    "③选择题：先按规则排除不合格项，再在合格项中按规则选最优。"
    "④找不到完全匹配的记录或信息不足时，answer 填\"证据不足\"。"
    "⑤引用：把回答和计算用到的每一个段落 ID 都列进 citations（分子、分母、两个被比较的值都要列）。"
    "输出：只输出一个 JSON 对象，不要 markdown 代码块、不要任何解释文字。"
)


def prepare_messages(question, passages):
    blocks = [f"[{p['id']}] {p['text']}" for p in passages]
    docs = "\n".join(blocks)
    user = (
        f"问题：{question}\n\n"
        f"段落：\n{docs}\n\n"
        f"只输出一个 JSON 对象，格式：{{\"answer\":\"简短答案\",\"citations\":[\"段落ID\"]}}"
    )
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user},
    ]


def improve(question, passages):
    """按词法相关度重排：把与问题词面重叠最多的段落放到最前（利用首因效应）。
    只重排不修改内容；与 lexical.py 的词法口径一致，但不减少段落数量。"""
    terms = re.findall(r'[\u4e00-\u9fff]{2}项目|R\d+|\d{4}-\d{2}', question)
    grams = {question[i:i + 2] for i in range(len(question) - 1)}

    def score(p):
        body = p['text']
        return (sum(t in body for t in terms), sum(g in body for g in grams))

    return sorted(passages, key=score, reverse=True)
