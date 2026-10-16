# AI、贡献与真实性声明

**真实 API 模型名称**：Qwen2.5-7B-Instruct-Q4_K_M（本地 llama.cpp 部署，`localhost:8000`，GPU 推理；未使用外部商业 API）。曾用 Qwen3-1.7B-Q8_0 做初探与位置效应对照。

**Token 消耗量级**：<10 万（40 次主请求约 7 万 token：prompt 约 6.9 万 + completion 约 1 千；精确 usage 见各 `runs/*.json` 的 `usage` 字段）。

**AI 工具与主要用途**：DeepSeek Harness（本会话所用 AI 助手）。用途：①环境搭建（git/llama.cpp 服务/WSL 环境配置）；②代码实现（`provider.py` 本地模型适配、`student.py` 提示词与 `improve()`、判分脚本；进阶B：`fixed_engine.py` 修复、`test_fix.py` 断言测试、`index.html` 状态展示）；③结果分析与报告/决策文档起草；④定位 Qwen3「思考型模型需关闭思考」等具体问题。

**本人核验并承担的关键判断及核验方法**：
- 思考模式关闭有效：本人发最小请求（"1+1等于几"）实测 `enable_thinking=false` 后 content 从空变为 `2`（记录于早期探测）。
- 本地模型接入成功：本人用 `curl localhost:8000/health`、`/v1/models` 及一次真实调用确认。
- 40 次主结果真实：本人逐条核对 `runs/*.json` 的 status/content/citations，确认 40/40 为 `ok`、引用均来自输入。
- 开发题 4/4：本人对照 `data/dev_answers.json` 核对 D01–D04 答案；引用与标准证据的差异（D01/D04 各缺一段）已如实写入报告。
- 位置效应非噪声：本人重跑 T02 R0 一次，输出与首次完全一致（88%/P588872），佐证 temperature=0 确定性（1.7B 阶段）。
- 进阶B：本人运行 `intervention.py`（区分性干预：全新引擎 R02 返回 b02，证明缓存键是元凶）、`test_fix.py`（14 项断言全部通过，含语义判据 4 项）、修复版 `server.py` 页面加载与 API 路径。

**未实现、未运行或未验证的内容**：①进阶题 A/C 未做（已选 B 并完成：故障复现、归因干预、最小修复、断言回归、等价变体、状态展示页面）；②T01–T08 无官方答案，正确答案率未验证（报告只给出稳定性/引用有效性/位置敏感性三项可机械核查结论）；③「改进是否优于基线」未做显著性判断（8 例样本过小）；④服务端贪心解码的完全确定性仅以 T02 一次重跑佐证，未全面验证；⑤开发题 D01/D04 的引用各缺一段标准证据（已如实记录，未强行调参掩盖）。

我确认没有把模拟输出、预测或 AI 编造数据当真实运行，没有隐瞒会改变结论的失败、调参、重试或标签使用。复用题包骨架（ANTLab-Agent-Tasks）与 `lexical.py` 词法口径已在源码/报告注明；提交包已检查无 API 密钥、Endpoint 和私人账号信息（`config.local.json`、`runs/` 由 `.gitignore` 排除）。

姓名/编号/日期：刘家瑄（25012100063）/ 2026-10-16。
