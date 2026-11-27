# 参考索引：先读哪一页

> 这是**路由表**，不是阅读清单。不要从 `assets/B2B电商平台实验规范.md` 第一页读到最后一页；先按任务选路径，再按标题/关键词跳读。

## 1. 三条读取路径

| 层级 | 时间 | 读什么 | 目的 |
|---|---|---|---|
| **L1** | 5 分钟 | `../SKILL.md` | 知道边界、六步流程、八条硬规则、默认值、输出契约 |
| **L2** | 30 分钟 | `00-triage.md` → `15-running-case.md` → 按任务选 `10-design.md` / `20-data-quality.md` / `40-decision-longterm.md` | 能完成一次设计、审计或决策 |
| **L3** | 按需 | `30-metrics-statistics.md`、`50-templates.md`、`60-field-dictionary.md`、`70-anti-patterns.md`、`80-governance-platform.md` | 查公式、模板、字段、平台细节 |
| **查证** | 只跳读 | `05-glossary.md`、`90-validation.md`、`assets/B2B电商平台实验规范.md` | 统一术语、看验证证据、回溯长文 |

**长文使用规则**：`assets/B2B电商平台实验规范.md` 是 122KB 归档，只按标题或关键词检索单节；不要把全文加载进上下文，也不要以它作为入口。

## 2. 按问题路由

| 你现在要做什么 | 先读 | 再查 |
|---|---|---|
| 判断要不要做实验 | `00-triage.md` 的“先问 10 个问题” | `../SKILL.md` §8 停止条件 |
| 写假设、选随机单元、算样本 | `10-design.md` | `30-metrics-statistics.md` 功效公式；`scripts/experiment_stats.py` |
| 判断 SRM/曝光/污染/重复账户 | `20-data-quality.md` | `50-templates.md` 的 SQL 骨架 |
| 定义主指标、护栏、口径 | `30-metrics-statistics.md` | `60-field-dictionary.md` D 模块 |
| 读数、算 CI/p、处理多重比较 | `30-metrics-statistics.md` | `15-running-case.md` 的复现数字 |
| 看子群、长期、衰减、副作用 | `40-decision-longterm.md` | `50-templates.md` 的 holdout 计划 |
| 做全量/定向/迭代/停止/复测 | `40-decision-longterm.md` | `50-templates.md` 的决策记录 |
| 写预注册、设计一页纸、读数报告 | `50-templates.md` | `60-field-dictionary.md` 全字段 |
| 查某个字段的定义/类型/owner | `60-field-dictionary.md` | `assets/实验字段字典.csv` |
| 评审别人的实验、找反模式 | `70-anti-patterns.md` | `20-data-quality.md` 的评分卡 |
| 建平台、门禁、RACI、合规 | `80-governance-platform.md` | `50-templates.md` 的 SQL/DDL |
| 怀疑数字算错 | `15-running-case.md` | `90-validation.md` 的复现命令 |
| 统一中英文术语 | `05-glossary.md` | — |

## 3. 推荐组合

**设计一个新实验（最小组合）**

```text
SKILL.md
  → 00-triage.md（10 问 + 最小 spec）
  → 10-design.md（单元/功效/预注册）
  → 30-metrics-statistics.md（主指标/护栏/口径）
  → 50-templates.md（设计一页纸 + 预注册 YAML）
```

**审计一个已有实验（最小组合）**

```text
SKILL.md
  → 20-data-quality.md（S1/S2/S3 评分卡）
  → 30-metrics-statistics.md（重算效应）
  → 40-decision-longterm.md（护栏/子群/长期/决策）
  → 70-anti-patterns.md（对照反模式）
```

**建制度/平台（最小组合）**

```text
SKILL.md
  → 80-governance-platform.md（G0–G7、RACI、表结构）
  → 60-field-dictionary.md（字段基线）
  → 50-templates.md（模板/SQL）
```

## 4. 维护规则

- **改字段**：先改 `60-field-dictionary.md` 与 `assets/实验字段字典.csv`，再改 `50-templates.md` 的 YAML；三处 ID、类型、必填性必须一致。
- **改数字**：先改 `15-running-case.md`，再同步 `90-validation.md` 和 `70-anti-patterns.md`；同一案例只保留一套样本量/效应/CI。
- **改统计方法**：先改 `scripts/experiment_stats.py`，再加 `scripts/test_experiment_stats.py` 断言，最后改 `30-metrics-statistics.md` 的文字。
- **改入口**：`SKILL.md` 保持在 8KB 以内；新增内容优先放 references，不往入口堆。
- **发布前**：运行 `scripts/check.ps1`，通过后再打包。
