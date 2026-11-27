# 60 · Field dictionary (61 fields)

The 61 fields are the minimum complete record of an experiment. “Required” means a value must exist; `N/A` is allowed only for F/G dimensions that genuinely do not apply, and must include a reason. The machine-readable copy is `assets/实验字段字典.csv`.

Conventions:
- `Req` = required for every experiment (Y/N).
- `N/A` = whether `N/A + reason` is permitted (Y/N).
- Types follow the CSV: `string`, `text`, `datetime`, `enum`, `object`, `array`, `url`.
- Every object field must include `method` and `source` for any number that enters a decision.

## A. 实验身份 (8)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| A01 | Experiment ID | string | Y | N | Globally unique, immutable. `EXP-{BU}-{YYYYMMDD}-{NNN}`; BU 2–6 uppercase letters; NNN daily sequence. Never reuse an archived ID. Regex `^EXP-[A-Z]{2,6}-\d{8}-\d{3}$`; uniqueness constraint. | 平台 |
| A02 | 实验名称 | string | Y | N | `{业务域}｜{干预摘要}｜{人群}`, ≤40 chars; describes what was done, not the result. Reject “成功/显著/提升” and vague names. | 负责人 |
| A03 | 实验负责人 | string | Y | N | One accountable DRI with real name/employee ID plus a backup; not a team mailbox. Validate against org directory and active status. | 负责人 |
| A04 | 开始时间 | datetime | Y | N | First real exposure, ISO 8601 with timezone. Store planned start separately. Must be ≤ A05 and ≤ first exposure log. | 平台 |
| A05 | 结束时间 | datetime | Y | N | Last exposure cutoff; distinguish “stop assignment” from “stop analysis.” Validate against data cutoff and analysis windows. | 平台 |
| A06 | 实验状态 | enum | Y | N | One of `Draft/InReview/Approved/Running/Paused/Completed/Analyzed/Decided/Archived/Aborted`; only legal transitions; log actor/time/reason. | 平台 |
| A07 | 实验背景 | text | Y | N | Six parts: baseline → evidence (data/interviews/complaints) → affected population → root-cause hypothesis → why now → alternatives and cost of inaction. ≥200 chars; must contain a baseline number and source. | 负责人 |
| A08 | 业务目标 | text | Y | N | `对{人群}，在{期限}内，使{结果指标}从{基线}达到{目标}，同时不损害{约束}`; align to OKR; separate output from outcome. Must contain baseline, target, deadline, constraint. | 业务 DRI |

## B. 实验设计 (8)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| B01 | Hypothesis | text | Y | N | Falsifiable causal statement with population, lever, control, primary metric, window, MDE, mechanism, refutation, and guardrail threshold. Must include MDE and a guardrail. | 负责人 |
| B02 | Treatment | object | Y | N | `{name, version, config, delivery, compliance}`. Version every config change; snapshot the config; link the PR/flag. Describe what actually happened, not the code branch name. | 产品/工程 |
| B03 | Control | object | Y | N | `{name, type, version, config}`; type ∈ current production / no feature / placebo. Default is current production; version must be contemporaneous and retrievable. | 产品/工程 |
| B04 | Randomization Unit | object | Y | N | `{unit_type, unit_id_field, hash_salt, strata, block_rule}`. Unit must match intervention and interference; `unit_id` must match the exposure log. | 数据科学 |
| B05 | Exposure定义 | text | Y | N | Exact event that counts as exposure, trigger condition, log table, timestamp, dedupe rule; distinguish reached from exposed. Event must exist and pass tracking QA. | 数据科学/工程 |
| B06 | 实验比例 | object | Y | N | `{control, treatment, ramp_plan}`; shares sum to 100%; ramp must not be outcome-driven. Validate against assignment table and SRM. | 负责人 |
| B07 | 实验周期 | object | Y | N | `{planned_start, planned_end, min_business_cycles, primary_window, long_term_windows}`; separate run time from observation window; cover ≥1 full business cycle. | 负责人 |
| B08 | 实验互斥 | object | Y | N | `{layer, conflict_group, excluded_exp_ids, orthogonal_to}`; document the conflict matrix; no same-layer overlap; check shared units/metrics/surfaces. | 平台/数据科学 |

## C. 数据质量 (7)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| C01 | 样本量 | object | Y | N | `{planned_per_arm, assigned, exposed, analyzable, power, mde, attrition}`; all four counts; analyzable/planned ≥80% or declare underpowered; attrition compared by arm. | 数据科学 |
| C02 | SRM | object | Y | N | `{chi_square, p_value, threshold, status, by_day, root_cause}`; status ∈ pass/watch/fail; p<0.001 blocks readout; check overall and by day/platform/channel/stratum. | 数据科学 |
| C03 | 实验前平衡性 | object | Y | N | `{method, max_smd, n_covariates_gt_0_1, variance_ratio_range, adjustment}`; SMD formula; max SMD <0.10 good, >0.20 block/investigate; pre-period covariates only. | 数据科学 |
| C04 | 曝光是否完整 | object | Y | N | `{exposure_rate, rate_diff_pp, missing_log_rate, delay_median_h, by_platform}`; event defined in B05; delivery/exposure gap explained; arm difference >10pp blocks. | 数据科学 |
| C05 | 是否存在污染 | object | Y | N | `{cross_exposure_rate, sources, evidence, mitigation, residual_risk}`; >5% disclose, >10% invalidate product-effect claim; even “none” must state detection method. | 数据科学 |
| C06 | 是否存在重复用户 | object | Y | N | `{duplicate_rate, canonical_rule, impact_on_metrics, sensitivity}`; report company/account/order separately; >2% requires denominator fix and sensitivity. | 数据科学 |
| C07 | 数据链路是否完整 | object | Y | N | `{lineage_url, freshness, reconciliation_diff, dq_checks, open_issues}`; lineage, freshness, reconciliation, nulls, schema, timezone, SQL version; any S1 fails blocks. | 数据工程 |

## D. 指标 (7)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| D01 | North Star | string | Y | N | Platform-level North Star with formula and the causal path from this experiment; not an experiment-specific metric. Must match company OKR. | 业务 DRI |
| D02 | Primary Metric | object | Y | N | Exactly one; `{id, definition, formula, window, denominator, direction, mde, expected_direction}`. Must directly test B01; one primary only. | 数据科学 |
| D03 | Secondary Metrics | array | Y | N | 2–4 mechanism/auxiliary metrics, each with expected direction and mechanism. More than 4 requires justification. | 数据科学 |
| D04 | Guardrail | array | Y | N | 3–6 non-inferiority metrics; each `{id, threshold, direction, owner, circuit_breaker}`. Every guardrail has an owner and action. | 业务/数据科学 |
| D05 | 指标口径 | text | Y | N | Numerator, denominator, window, dedupe, tax, refund/cancel, currency, exclusions, attribution, version. Must match D06 and the dashboard. | 分析师 |
| D06 | 指标计算SQL | url | Y | N | Version-controlled link plus commit/tag; executable; tested; reviewed by a non-author; no screenshots. | 分析师 |
| D07 | 实验前是否预设 | object | Y | N | `{preset, plan_hash, frozen_at, amendments}`; `preset=true` only if frozen before first exposure; `false` means exploratory only. | 负责人/数据科学 |

## E. 统计 (7)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| E01 | Effect | object | Y | N | `{estimator, estimate, unit, population, adjusted_for, cluster}`; estimator ∈ ITT/TOT/CATE; population must match D02; state cluster level. | 数据科学 |
| E02 | Relative Lift | object | Y | N | `{estimate, ci_low, ci_high, baseline}`; baseline >0; percentage/decimal consistent; always include CI. | 数据科学 |
| E03 | Absolute Lift | object | Y | N | `{estimate, ci_low, ci_high, unit, business_value}`; unit explicit (pp, ¥, orders); business value states assumptions. | 数据科学 |
| E04 | CI | object | Y | N | `{level, method, lower, upper}`; method ∈ cluster/delta/bootstrap/regression; must match the estimator and unit. | 数据科学 |
| E05 | P-value | object | Y | N | `{value, test, sided, adjusted}`; 3 decimals; `<0.001` below threshold; no stars-only reporting. | 数据科学 |
| E06 | Multiple Testing | object | Y | N | `{family, method, q, adjusted_p, discovered}`; family pre-registered; method ∈ BH/Holm/Bonferroni/none; adjust secondary/subgroups. | 数据科学 |
| E07 | Statistical Power | object | Y | N | `{design_power, mde, alpha, achieved_n, precision}`; design power, not post-hoc power; achieved n matches C01. | 数据科学 |

## F. 异质性 (7)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| F01 | 新/老用户 | object | Y | Y | Define new/existing with a pre-period window (e.g., no paid order in 180d); report n, lift, CI, interaction p for both. Distinguish new company vs new buyer at an existing company. | 数据科学 |
| F02 | 高/低价值用户 | object | Y | Y | Split on **pre-period** 12-month net GMV quantile (e.g., top 20% vs rest); never use in-experiment GMV; report cut point and both effects. | 数据科学 |
| F03 | 高频/低频 | object | Y | Y | Pre-period 90-day order count or purchase-cycle ratio `gap/avg_interval`; state truncation handling; report both effects. | 数据科学 |
| F04 | 渠道 | object | Y | Y | Mutually exclusive channel taxonomy (organic, sales-led, partner, API, offline); attribution version; merge small channels. | 数据科学 |
| F05 | 商品 | object | Y | Y | Category/price band/SKU/long-tail vs hero; note inventory and cross-category spillover; check category sample size. | 数据科学 |
| F06 | 商家 | object | Y | Y | Seller tier/region/fulfillment capability; keep buyer-side and seller-side metrics separate; check seller clusters. | 数据科学 |
| F07 | 其他业务关键维度 | array | Y | Y | Industry, company size, buying role, region, contract type, payment terms, credit rating; ≤5 dimensions; pre-register and correct. | 数据科学 |

## G. 长期 (6)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| G01 | 7天 | object | Y | Y | Cumulative 7-day effect `{lift, ci, p, n, events}`; same definition as primary; note start point. | 数据科学 |
| G02 | 14天 | object | Y | Y | Cumulative 14-day effect; state whether it includes day 7; watch stabilization. | 数据科学 |
| G03 | 30天 | object | Y | Y | 30-day primary-window effect; must reconcile with E02/E03; explain if different. | 数据科学 |
| G04 | 全量后 | object | Y | Y | `{rollout_date, holdout_pct, method, windows, effect}`; method ∈ holdout/DID/synthetic control/ITS; state control source and assumptions. | 业务/数据科学 |
| G05 | 是否衰减 | object | Y | Y | `{decay_30_7, decay_90_30, classification, evidence}`; classification ∈ stable/decay/reverse/strengthen/delayed; must align with G01–G03. | 数据科学 |
| G06 | 是否存在副作用 | object | Y | Y | `{metrics, findings, severity, mitigation, owner}`; cover every guardrail, cannibalization, seller/buyer fairness, support cost; “none” still states scope. | 业务/数据科学 |

## H. 决策 (6)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| H01 | 实验结论 | object | Y | N | Statistical facts only: `{primary_effect, ci, p, guardrail, dq, subgroups}`; must match E module; no business judgment. | 数据科学 |
| H02 | 业务结论 | text | Y | N | “So what”: for whom, how much value, transferability, remaining uncertainty; separate fact from judgment; cite H01. | 业务 DRI |
| H03 | 是否全量 | object | Y | N | `{value, scope, ramp, monitoring, holdout}`; value ∈ yes/no/partial; yes requires ramp, monitoring, holdout; partial states scope. | 业务 DRI |
| H04 | 是否停止 | object | Y | N | `{value, reason, resume_condition}`; value ∈ yes/no/pause; yes states harm/futility/cost/strategic; pause states resume condition; must not contradict H03. | 业务 DRI |
| H05 | 是否定向 | object | Y | N | `{value, segment, rule, validation}`; value ∈ yes/no/explore; yes states segment, targeting rule, validation plan; explore states hypothesis. | 业务 DRI |
| H06 | 是否需要二次实验 | object | Y | N | `{value, question, design_changes, parent_exp_id}`; value ∈ yes/no; if yes, state the new question and design changes; parent link valid. | 业务 DRI |

## I. 沉淀 (5)

| ID | Field | Type | Req | N/A | Definition and validation | Owner |
|---|---|---|---|---|---|---|
| I01 | 实验文档 | url | Y | N | Main document with design, analysis, decision, appendix; version and access permissions; link resolves. | 负责人 |
| I02 | SQL | url | Y | N | Repository path + commit/tag; executable; tests and owner; reproducible. | 分析师 |
| I03 | Dashboard | url | Y | N | Standard tabs (overview, DQ, primary, guardrails, subgroups, long-term, decision); permissions and refresh correct. | 分析师 |
| I04 | 知识库 | string | Y | N | Experiment card ID + ≥3 tags + one-line conclusion; searchable; no orphan cards. | 负责人 |
| I05 | 可复用经验 | object | Y | N | `{pattern, mechanism, effect_range, boundary, reuse_count}`; state conditions and boundary, not slogans; link evidence. | 负责人/数据科学 |

## Object schemas

### B02 Treatment / B03 Control

```json
{
  "name": "4h quote SLA",
  "version": "v1.2.0",
  "type": "current_production",
  "config": {"sla_hours": 4, "applies_to": ["new_inquiry"]},
  "delivery": "server_policy + crm_task",
  "compliance": {"applied_rate": 0.93, "source": "crm_action"},
  "rollback": {"flag": "quote_sla_v2", "owner": "eng-oncall"}
}
```

### B04 Randomization Unit

```json
{
  "unit_type": "company",
  "unit_id_field": "canonical_company_id",
  "hash_salt": "b2b_quote_sla_20261118",
  "hash_version": "murmur3_32",
  "strata": ["industry", "gmv_band", "region"],
  "block_rule": "stratified_block_randomization",
  "cluster_level": "company"
}
```

### B06 Split / B07 Period / B08 Exclusion

```json
{
  "control": 50,
  "treatment": 50,
  "ramp_plan": ["5%", "25%", "50%", "100%"],
  "planned_start": "2026-11-18",
  "planned_end": "2026-12-16",
  "min_business_cycles": 1,
  "primary_window": "30d",
  "long_term_windows": ["7d", "14d", "30d", "60d"],
  "layer": "quote_ux",
  "conflict_group": "quote_pricing",
  "excluded_exp_ids": ["EXP-B2B-20261020-004"],
  "orthogonal_to": ["EXP-B2B-20261101-002"]
}
```

### C01–C07 Data quality

```json
{
  "sample_size": {"planned_per_arm": 4200, "assigned": 4310, "exposed": 3020,
                  "analyzable": 2870, "power": 0.80, "mde": "8%", "attrition": 0.33},
  "srm": {"chi_square": 1.42, "p_value": 0.23, "threshold": 0.001,
          "status": "pass", "by_day": "pass", "root_cause": null},
  "balance": {"method": "SMD", "max_smd": 0.04, "n_covariates_gt_0_1": 0,
              "variance_ratio_range": [0.92, 1.08], "adjustment": "CUPED + strata"},
  "exposure": {"exposure_rate": 0.71, "rate_diff_pp": 1.2,
               "missing_log_rate": 0.004, "delay_median_h": 2.1,
               "by_platform": {"web": 0.74, "app": 0.61, "api": 0.88}},
  "contamination": {"cross_exposure_rate": 0.018, "sources": ["multi_account"],
                    "evidence": "canonical ID overlap", "mitigation": "company hash",
                    "residual_risk": "low"},
  "duplicates": {"duplicate_rate": 0.006, "canonical_rule": "USCC + domain",
                 "impact_on_metrics": "<0.2%", "sensitivity": "stable"},
  "lineage": {"lineage_url": "https://bi.example.com/lineage/EXP-...",
              "freshness": "T+1 06:00", "reconciliation_diff": 0.001,
              "dq_checks": "12/12 pass", "open_issues": []}
}
```

### D02/D03/D04/D07 Metrics

```json
{
  "primary": {"id": "M_B2B_Q2O_30D", "definition": "企业首次有效询盘后30天内下单",
              "formula": "orders / quote_requests", "window": "30d",
              "denominator": "valid_inquiry_companies", "direction": "up",
              "mde": "8%", "expected_direction": "up"},
  "secondary": [
    {"id": "M_B2B_QUOTE_ACCEPT", "expected": "up", "mechanism": "trust"},
    {"id": "M_B2B_QUOTE_LATENCY_P50", "expected": "down", "mechanism": "speed"}
  ],
  "guardrails": [
    {"id": "M_B2B_CANCEL_RATE", "threshold": "+2pp", "direction": "up",
     "owner": "ops.quote", "circuit_breaker": "disable_if_breach_2_consecutive_days"}
  ],
  "preset": {"preset": true, "plan_hash": "sha256:...",
             "frozen_at": "2026-11-17T18:00:00+08:00", "amendments": []}
}
```

### E01–E07 Statistics

```json
{
  "effect": {"estimator": "ITT", "estimate": 0.094, "unit": "relative",
             "population": "all_assigned", "adjusted_for": ["pre_gmv", "segment"],
             "cluster": "company"},
  "relative_lift": {"estimate": 0.112, "ci_low": 0.021, "ci_high": 0.167, "baseline": 0.084},
  "absolute_lift": {"estimate": 0.0094, "ci_low": 0.0018, "ci_high": 0.0141,
                    "unit": "pp", "business_value": "¥4.2M annualized"},
  "ci": {"level": 0.95, "method": "cluster_robust", "lower": 0.021, "upper": 0.167},
  "p_value": {"value": 0.008, "test": "wald", "sided": 2, "adjusted": false},
  "multiple_testing": {"family": "secondary", "method": "BH", "q": 0.10,
                       "adjusted_p": [0.03, 0.11], "discovered": 1},
  "power": {"design_power": 0.80, "mde": "8%", "alpha": 0.05,
            "achieved_n": 2870, "precision": "±5.8pp"}
}
```

### F01–F07 Heterogeneity

```json
{
  "new_vs_existing": {"definition": "no paid order in 180d", "n_new": 820,
                      "lift_new": 0.12, "n_existing": 2050, "lift_existing": 0.07,
                      "p_interaction": 0.04, "adjusted_p": 0.08, "preregistered": true},
  "value": {"split": "top20_pre_12m_net_gmv", "lift_high": 0.02, "lift_low": 0.11,
            "p_interaction": 0.03, "preregistered": true},
  "frequency": {"metric": "orders_90d", "high": ">=3", "lift_high": 0.03,
                "lift_low": 0.09, "p_interaction": 0.31},
  "channel": {"taxonomy": "v1", "effects": {"organic": 0.12, "sales_led": 0.14, "api": 0.05}},
  "category": {"effects": {"MRO": 0.06, "consumables": 0.10}, "spillover_checked": true},
  "seller": {"tier": {"KA": 0.03, "long_tail": 0.08}, "buyer_seller_separated": true},
  "other": [{"dim": "industry", "levels": ["manufacturing", "retail"], "method": "BH"}]
}
```

### G01–G06 Long-term

```json
{
  "d7": {"lift": 0.12, "ci": [0.04, 0.20], "p": 0.003, "n": 2860, "events": 412},
  "d14": {"lift": 0.11, "ci": [0.03, 0.19], "p": 0.006, "n": 2840},
  "d30": {"lift": 0.094, "ci": [0.021, 0.167], "p": 0.008, "n": 2800},
  "post_rollout": {"rollout_date": "2027-01-05", "holdout_pct": 0.08,
                   "method": "holdout", "windows": ["30d", "60d"], "effect": null},
  "decay": {"decay_30_7": 0.78, "decay_90_30": null, "classification": "stable",
            "evidence": "flat cumulative curve after day 14"},
  "side_effects": {"metrics": ["cancel_rate", "seller_quote_rate"],
                   "findings": "none", "severity": "none",
                   "mitigation": "monitor", "owner": "ops.quote"}
}
```

### H01–H06 Decision

```json
{
  "experiment_conclusion": {"primary_effect": "+11.2%", "ci": "[2.1, 16.7]",
                             "p": 0.008, "guardrail": "pass", "dq": "pass",
                             "subgroups": {"new": "+15%", "existing": "+7%"}},
  "business_conclusion": "对新客更强，建议全量并保留8% holdout 60天。",
  "scale": {"value": "yes", "scope": "all_mid_market", "ramp": "5→25→50→100",
            "monitoring": "daily_guardrail", "holdout": 0.08},
  "stop": {"value": "no", "reason": null, "resume_condition": null},
  "target": {"value": "no", "segment": null, "rule": null, "validation": null},
  "retest": {"value": "no", "question": null, "design_changes": null, "parent_exp_id": null}
}
```

### I05 Reusable lesson

```json
{
  "pattern": "lead-time transparency on quote page",
  "mechanism": "reduces uncertainty and comparison shopping",
  "effect_range": "+6% to +16% relative Q2O",
  "boundary": "requires reliable fulfillment promise; strongest for new buyers",
  "reuse_count": 2,
  "evidence": ["EXP-B2B-20261118-001", "EXP-B2B-20270210-003"]
}
```

## Completeness rule

A record is complete only when:
- all 61 IDs appear once;
- all required fields are non-empty or `N/A + reason` (F/G only);
- every numeric claim has `method` and `source`;
- object fields contain the subfields listed above;
- the plan hash and SQL hash resolve;
- H and I fields are filled after the decision, not left as “TBD”.
