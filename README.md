# ANTLab Agent Tasks

文档阅读与信息核验方向 Agent 项目的应用层开发者招募考核：先完成基础题，再从进阶 A/B/C 中选择一套完成。

**截止时间：北京时间 2026 年 10 月 16 日 23:59（UTC+8）。**

## 本次提交（Agent 方向）

- **所选方向**：Agent
- **最终分支**：`main`
- **最终 commit SHA**：`f4d697ea029191528369e598e4338f1516759be4`（填写姓名编号后的内容提交；最终收尾提交见 git log 最新一条）
- **报告**：[report.md](report.md)　**决策**：[decisions.md](decisions.md)　**声明**：[declaration.md](declaration.md)

### 启动与复算命令（在 `基础/` 目录下）

```powershell
# 32 次基线（本地模型，无费用；真实调用，会消耗本地算力）
python starter/runner.py --split evaluation --condition all --limit 32 --paid --config config.local.json
# 8 次改进
python starter/runner.py --split evaluation --condition R0 --variant improved --limit 8 --paid --config config.local.json
# 生成逐例表 results/results.csv
python results/scoring/score.py
```

### 完成 / 未完成

| 内容 | 状态 |
|---|---|
| 基础题 40 次主请求（32 基线 + 8 改进） | ✅ 完成，全 ok |
| 基础题逐例判分 + `results/results.csv` | ✅ 完成 |
| 基础题诊断（位置效应）+ 变体（ID 重映射） | ✅ 完成 |
| 三项决定 + AI 声明 + 复现说明 | ✅ 完成 |
| 进阶题 B（系统失效诊断） | ✅ 完成（故障复现 + 归因干预 + 最小修复 + 断言回归 + 等价变体 + 状态页面） |

## 从哪开始

1. 先读 [开始阅读.md](开始阅读.md)（总体规则、时间、提交方式）。
2. 基础题（必做）：[基础/README.md](基础/README.md) 与 基础/01_考核题目.md。
3. 进阶题（三选一）：[进阶/README.md](进阶/README.md)，在 A / B / C 中选一套。

## 目录结构

```text
开始阅读.md              入口：总体规则、截止时间、提交方式
基础/                    基础题：12 题（4 开发题有公开答案 + 8 评测题），
                         R0/R1/R2/K 四种输入组织条件；模型 API 自费，
                         主请求量与运行命令见 基础/README.md
进阶/                    进阶题（A/B/C 三选一）
├─ 01_A_研究机制迁移.md        A：主张→证据→支持状态机制迁移与对照
├─ 02_B_系统失效诊断.md        B：源码审查、故障归因与修复
├─ 03_C_产品假设验证.md        C：围绕自选用户任务的产品假设验证
├─ materials/                 两份 CC Attribution 公开论文（P1/P2）及抽取数据
├─ challenge_b/               B 题文档查证样机（30 行 Engine，含预埋故障）
└─ templates/                 声明与整合报告模板
```

## 规则要点

- 准备时间为一周（包含基础题和进阶题）；模型调用使用自己的 API，费用自理；实验输入、原始响应、失败和前后对照须保留在仓库中。
- AI 可辅助阅读、实现和排错；需记录它对关键决定的影响、本人如何核验，以及实际完成和未完成的内容。
- 提交：把作品推送到自己的 GitHub 仓库，并在收集表登记仓库链接与最终 commit SHA；收集表地址与仓库评审账号见 Q 群公布（详见 进阶/05_提交与报告格式.md 与 进阶/06_收集表填写说明.md）。
- 本包不含评委参考答案、评测标签、内部开发教程或商业书籍全文。
- 文件完整性：`基础/文件校验.json` 与 `进阶/文件校验.json` 提供逐文件 SHA256，可自行校验。
