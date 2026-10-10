"""待候选人实现。避免读取dev_answers或题号/condition来构造答案。

当前为最小可跑版本：仅为打通 dry-run 请求链，prompt 需由本人后续设计、核查、解释。
"""
import json

_SYSTEM = (
    "你是科研文档信息核验助手。你只能依据下面给出的段落原文回答问题，"
    "不得使用外部知识，不得编造段落中不存在的信息。"
    "当段落信息不足以回答问题时，answer 必须为\"证据不足\"，"
    "citations 列出支持该判断的检查来源段落ID。"
)


def prepare_messages(question, passages):
    """返回 [{"role":"system|user", "content":"..."}, ...]。
    passages 仅含 id/source/text，不包含答案或条件标记。
    必须请求 JSON 对象: {"answer": "简短答案", "citations": ["P..."]}。"""
    blocks = []
    for p in passages:
        blocks.append(f"[{p['id']}] 来源：{p['source']}\n{p['text']}")
    docs = "\n\n".join(blocks)
    user = (
        f"问题：{question}\n\n"
        f"给定段落：\n{docs}\n\n"
        f"请严格只输出一个 JSON 对象，不要输出任何其他文字，格式如下：\n"
        f'{{"answer": "简短答案", "citations": ["段落ID"]}}'
    )
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user},
    ]


def improve(question, passages):
    """返回重新组织/选择的原段落列表，不能修改 id/source/text 或使用答案标签。
    默认恒等映射仅用于联通，不算已完成改进。"""
    return passages
