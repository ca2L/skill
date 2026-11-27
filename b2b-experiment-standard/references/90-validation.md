# 验证与复现

> 目标：让读者能判断“这个包里的数字和文档是否可信”，而不是只看到一句“已验证”。
> 本文件记录**可复现的证据**、**未覆盖的边界**和**版本变更**。

## 1. 一键校验

在包根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

它会依次执行：

| 步骤 | 命令 | 检查 |
|---|---|---|
| 单元测试 | `python scripts/test_experiment_stats.py` | 功效、MDE、读数、SRM、SMD、CUPED 的数值与异常输入 |
| 案例复现 | `python scripts/reproduce_examples.py` | 统一案例的 4 条命令输出与文档数字一致 |
| 文档校验 | `python scripts/check_docs.py` | frontmatter、链接、字段数、代码围栏、关键章节 |

全部通过时退出码为 0；任何一步失败都会以非零退出，并打印失败项。

## 2. 统一案例的复现基线

案例全文见 `15-running-case.md`。以下是必须一致的基线：

| 量 | 值 | 来源 |
|---|---:|---|
| baseline Q2O | 0.084 | 实验前 90 天 |
| treatment Q2O | 0.092 | 30 天读数 |
| 每臂分析样本 | 16,000 / 15,850 | 分配后 ITT |
| 绝对提升 | +0.008 | 0.092 − 0.084 |
| 相对提升 | +9.5238% | 0.008 / 0.084 |
| 95% CI（绝对） | [0.00179276, 0.01420724] | Wald，未池化 SE |
| 95% CI（相对） | [2.1342%, 16.9134%] | 绝对 CI / 0.084 |
| p 值 | 0.011544 | 两比例 z 检验，池化 SE |
| 设计 MDE（11%）所需 n | 14,847/臂 | α=0.05，power=0.80 |
| 16,000/臂的实际 MDE | 10.5866% | 反推 |
| SRM | 卡方 0.706436，p=0.400629 | 16,000 vs 15,850，阈值 0.001 |

**解释约束**：观测 +9.52% 低于设计 MDE 11%，但 CI 上限 16.91% 包含 MDE；因此只能说“方向可信、幅度未达业务门槛”，不能说“达到设计目标”。

## 3. 脚本的统计口径

`scripts/experiment_stats.py` 是**设计/检查辅助器**，不是完整实验分析平台。

| 命令 | 方法 | 口径/限制 |
|---|---|---|
| `power-binary` | 两比例正态近似 | 未池化方差；含 cluster DEFF 与流失膨胀 |
| `power-continuous` | 两均值正态近似 | 假设等方差；含 DEFF/流失 |
| `mde-binary` | 对绝对 MDE 二分 | 用同一正态近似反推 |
| `test-binary` | 两比例 z 检验 + Wald CI | p 用池化 SE，CI 用未池化 SE；小样本/极端比例需 exact/bootstrap |
| `srm` | Pearson 卡方 | 期望比例可自定义；p<0.001 视为阻断 |
| `smd` | 合并标准差标准化 | 阈值 0.05/0.10 仅作筛查，不替代业务判断 |
| `cuped` | 单协变量 CUPED | 方差削减 ≈ `ρ²`；不处理多协变量/时间漂移 |

**未覆盖**：cluster-robust 回归、delta method 比率指标、序贯/Bayesian、多协变量 CUPED、分位数/尾部指标。这些在 `30-metrics-statistics.md` 有方法说明，但不能用本脚本直接算。

## 4. 证据等级

| 等级 | 含义 | 本包状态 |
|---|---|---|
| E1 | 脚本可复现，输出与文档逐项对齐 | 已覆盖：功效/MDE/读数/SRM/SMD/CUPED |
| E2 | 公式可手工推导，边界条件已写清 | 已覆盖：两比例、DEFF、CUPED |
| E3 | 独立实现交叉验证（R/statsmodels） | **未完成**，列为 P2 |
| E4 | 真实生产案例回放 | **未完成**，需要授权数据 |

对外表述时应写“脚本与文档已对齐（E1/E2），独立统计软件交叉验证待补（E3）”，不要写“统计上完全验证”。

## 5. 已知边界

1. **Wald 近似**：小样本、极端比例、稀有事件会偏；应改用 exact、Wilson、bootstrap。
2. **聚类**：脚本只做设计阶段的 DEFF 膨胀，不做分析阶段的 cluster-robust SE；有聚类结构时必须在分析代码中另做。
3. **比率指标**：GMV/企业、订单/企业等比率不能用普通 t 检验；需 delta 或 bootstrap。
4. **多重比较**：脚本不自动校正；BH/Holm 需在分析计划中显式执行。
5. **长期效应**：30 天主窗口之外的衰减、副作用、holdout/DID 需要额外数据，脚本不覆盖。
6. **数据质量**：SRM/SMD 只是门禁的一部分；曝光、污染、重复账户、血缘需查数据，不是跑一个公式就能证明。

## 6. 版本变更

### 1.1.0（2026-11-27）

- `SKILL.md` 从 12.2KB 压缩为 5 分钟入口卡，深度内容移到 references。
- 新增 `references/INDEX.md`、`05-glossary.md`、`15-running-case.md`、`90-validation.md`。
- 新增 `scripts/test_experiment_stats.py`、`reproduce_examples.py`、`check_docs.py`、`check.ps1`。
- `experiment_stats.py` 新增 `test-binary`；为 `inflate`、`mde_binary`、`srm` 增加输入校验。
- 统一案例改为 16,000/臂；修正 `70-anti-patterns.md` 旧案例的样本量与 p 值不一致。
- 修正 CUPED 方差削减表述为 `ρ²`（剩余方差 `1 − ρ²`）。

### 1.0.0（2026-11-18）

- 首个版本：61 字段、9 个 references、完整规范、61 行 CSV、统计脚本。

## 7. 发布前签核

- [ ] `scripts/check.ps1` 退出码 0。
- [ ] `15-running-case.md` 的 4 个数字与 `reproduce_examples.py` 输出一致。
- [ ] `60-field-dictionary.md` 与 `assets/实验字段字典.csv` 均为 61 个唯一 ID。
- [ ] `SKILL.md` ≤ 8KB，且没有把长文内容复制进入口。
- [ ] 所有相对链接可解析，代码围栏成对。
- [ ] 版本号、变更日志、zip 文件名一致。
