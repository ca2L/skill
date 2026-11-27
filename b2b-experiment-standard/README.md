# B2B 电商实验规范 · DSH Skill

把《B2B 电商平台实验规范》沉淀成一个可复用的 DeepSeek Harness Skill：既能指导新实验设计，也能审计已有实验、搭建实验治理体系。

- **Skill 名称**：`b2b-experiment-standard`
- **适用**：B2B / 企业采购 / 询盘报价 / 商家侧 / 定价 / 履约 / 销售区域等实验场景
- **不适用**：纯 B2C 增长实验、只写 SQL/画图、需要法律意见的定价合规判断
- **依赖**：无。脚本只用 Python 标准库

## 目录结构

```text
b2b-experiment-standard/
├── SKILL.md                     # 技能入口：5 分钟卡、三种模式、八条硬规则、默认值、输出契约
├── README.md                    # 本文件
├── references/
│   ├── INDEX.md                 # 路由表：L1/L2/L3 读什么，按问题跳转
│   ├── 00-triage.md             # 10 个前置问题、60 分钟设计流程、最小可用实验 spec
│   ├── 05-glossary.md           # 中英文术语、易混概念、写作约定
│   ├── 10-design.md             # 假设、随机单元、分流、曝光、周期、功效、CUPED、特殊设计
│   ├── 15-running-case.md       # 统一报价 SLA 案例：设计、DQ、读数、决策、复现命令
│   ├── 20-data-quality.md       # SRM、平衡性、曝光完整性、污染、重复账户、血缘、DQ 评分卡
│   ├── 30-metrics-statistics.md # 指标树/口径/SQL、ITT/TOT、聚类稳健、Delta、BH/Holm、序贯
│   ├── 40-decision-longterm.md  # 异质性、7/14/30/60/90 天、衰减、副作用、holdout、决策矩阵
│   ├── 50-templates.md          # 设计一页纸、预注册、61 字段示例、读数、决策记录、SQL 骨架
│   ├── 60-field-dictionary.md   # 61 字段逐项定义、类型、校验、owner、对象 schema
│   ├── 70-anti-patterns.md      # 20 个反模式 + 3 个 B2B 案例 + 红队问题
│   ├── 80-governance-platform.md# G0–G7、RACI、平台表结构/API、合规、30/60/90 落地
│   └── 90-validation.md         # 复现基线、证据等级、已知边界、版本变更
├── assets/
│   ├── B2B电商平台实验规范.md    # 完整长文规范（约 125KB，仅查证，不要求通读）
│   └── 实验字段字典.csv          # 61 字段机读字典
└── scripts/
    ├── experiment_stats.py      # 功效/MDE/读数/SRM/SMD/CUPED 计算器，输出 JSON
    ├── test_experiment_stats.py # 单元测试与异常输入
    ├── reproduce_examples.py    # 统一案例的 4 条命令回放
    ├── check_docs.py            # frontmatter/链接/字段/表格/版本检查
    └── check.ps1                # 一键运行以上三项
```

## 安装

DSH 只扫描技能根目录下**第一层**的 `<name>/SKILL.md` 或 `<name>.md`。把整个 `b2b-experiment-standard` 文件夹放到以下任一位置：

| 作用域 | 路径 | 优先级 |
|---|---|---:|
| 项目级（推荐，随仓库共享） | `<projectRoot>/.dsh/skills/b2b-experiment-standard/` | 100 |
| 项目级兼容目录 | `<projectRoot>/.agents/skills/b2b-experiment-standard/` | 200 |
| 用户级（所有项目可用） | `C:\Users\<user>\.dsh\skills\b2b-experiment-standard\` | 400 |

注意：
- 不要把 `SKILL.md` 放到更深一层（如 `references/SKILL.md`），不会被发现。
- 新增或修改 `SKILL.md` 后，DSH 会刷新技能目录；若未出现，重启会话/应用。
- 只复制 `SKILL.md` 不够，`references/`、`assets/`、`scripts/` 要一起复制。

## 怎么用

在对话里直接描述任务即可，例如：

- “按 B2B 实验规范，设计一个报价 SLA 从 24h 缩到 4h 的实验。”
- “审计这个实验：SRM p=0.002，曝光率 treatment 比 control 低 8pp，还能读数吗？”
- “帮我把这份读数转成决策记录，判断全量/定向/停止。”
- “给我们平台写一套实验字段字典和 G0–G7 门禁。”
- “卖家履约工具的实验，买家纠纷率上升，怎么判断是不是副作用？”

Skill 会按三种模式工作：
1. **设计**：决策 → 假设 → 随机单元 → 功效 → 指标树 → 预注册 → 上线门禁。
2. **审计**：重建设计 → DQ 评分卡 → 重算效应 → 护栏/异质性/长期 → 决策建议。
3. **建制**：61 字段 → 门禁/RACI → 平台表结构 → 模板 → 30/60/90 落地。

不确定先读哪一页时，看 `references/INDEX.md` 的路由表；不要从 125KB 长文第一页开始读。

## 脚本

```bash
# 比例指标功效（含聚类 DEFF 与流失膨胀）
python scripts/experiment_stats.py power-binary \
  --baseline 0.084 --mde-relative 0.08 \
  --icc 0.05 --cluster-size 5 --attrition 0.10

# 连续指标功效
python scripts/experiment_stats.py power-continuous \
  --sigma 120 --delta 10 --cluster-size 4 --icc 0.02

# 给定样本反推 MDE
python scripts/experiment_stats.py mde-binary --baseline 0.084 --n-per-arm 3000

# 两比例读数：绝对/相对提升、CI、p 值
python scripts/experiment_stats.py test-binary \
  --baseline 0.084 --treatment 0.092 --n-per-arm 16000

# SRM 卡方
python scripts/experiment_stats.py srm --counts 16000 15850

# 平衡性 SMD
python scripts/experiment_stats.py smd \
  --mean-t 10 --mean-c 9.5 --sd-t 4 --sd-c 4.2

# CUPED：θ、方差削减、等效样本倍数
python scripts/experiment_stats.py cuped \
  --x 1,2,3,4,5,6 --y 2,4,5,8,9,11
```

输出为 JSON，可直接粘进设计文档或读数报告。

## 核心立场

- **决策先行**：说不出“结果阳性/阴性/持平分别做什么”，就不要开实验。
- **账户/企业为默认随机单元**：B2B 的干预、合同、价格和干扰通常都在企业层。
- **ITT 为主**：曝光/依从/TOT 只作次要解释，不能替代随机化。
- **SRM 是门禁**：p < 0.001 先停下来查分流，不要靠重加权“修复”。
- **效应要完整**：绝对提升 + 相对提升 + 95% CI + MDE + 业务价值，缺一不可。
- **护栏有牙齿**：每个 guardrail 有 owner、阈值、熔断动作，且能否决全量。
- **长期与副作用**：30 天是主窗口，不是终点；复购/留存看 60–90 天，全量后靠 holdout/DID/合成控制。
- **沉淀是实验的一部分**：文档、SQL、Dashboard、知识卡、可复用经验，缺一不算闭环。

## 质量与验证

本包已做以下检查：

- 61 个字段与 CSV 逐项对齐，模块计数 A8/B8/C7/D7/E7/F7/G6/H6/I5。
- 所有引用文件存在，`SKILL.md` frontmatter 为合法 kebab-case name + description。
- `scripts/test_experiment_stats.py` 覆盖功效、MDE、读数、SRM、SMD、CUPED 与异常输入。
- `scripts/reproduce_examples.py` 回放统一案例的 4 条命令，逐项比对文档数字。
- `scripts/check_docs.py` 检查入口大小、链接、表格、字段覆盖和版本标记。
- 修正了 CUPED 方差削减公式：方差削减应为 `ρ²`，剩余方差为 `1 − ρ²`（长文规范同步修正）。

一键运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```

证据等级与未覆盖边界见 `references/90-validation.md`：脚本与文档已对齐（E1/E2），R/statsmodels 独立交叉验证和真实生产回放仍是 P2。

## 版本

- Skill 版本：1.1.0
- 对应规范：1.0.0（2026-11-18）
- 维护：实验平台/数据科学团队
- 建议评审周期：每季度一次，或平台 schema / 统计方法变更时即时更新
