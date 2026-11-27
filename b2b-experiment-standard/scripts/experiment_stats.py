#!/usr/bin/env python3
"""Reproducible helpers for B2B experiment design and data-quality checks.

Stdlib only. Outputs JSON so results can be pasted into a design doc or readout.

Examples:
  python experiment_stats.py power-binary --baseline 0.084 --mde-relative 0.08 \
      --icc 0.05 --cluster-size 5 --attrition 0.10
  python experiment_stats.py power-continuous --sigma 120 --delta 10 --cluster-size 4 --icc 0.02
  python experiment_stats.py mde-binary --baseline 0.084 --n-per-arm 3000
  python experiment_stats.py test-binary --baseline 0.084 --treatment 0.092 --n-per-arm 16000
  python experiment_stats.py srm --counts 16000 15850
  python experiment_stats.py smd --mean-t 10 --mean-c 9.5 --sd-t 4 --sd-c 4.2
  python experiment_stats.py cuped --x 1,2,3,4 --y 2,4,5,8
"""
from __future__ import annotations

import argparse
import json
import math
from statistics import NormalDist, mean, stdev


def z(p: float) -> float:
    return NormalDist().inv_cdf(p)


def _gammaincc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x), Numerical Recipes style."""
    if x < 0 or a <= 0:
        raise ValueError("a and x must be positive")
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap = a
        total = 1.0 / a
        delta = total
        for _ in range(1000):
            ap += 1.0
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * 1e-14:
                break
        return 1.0 - total * math.exp(-x + a * math.log(x) - gln)
    b = x + 1.0 - a
    c = 1e300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(stat: float, df: int) -> float:
    return _gammaincc(df / 2.0, stat / 2.0)


def design_effect(cluster_size: float, icc: float) -> float:
    if cluster_size <= 1 or icc <= 0:
        return 1.0
    return 1.0 + (cluster_size - 1.0) * icc


def inflate(n: float, icc: float, cluster_size: float, attrition: float) -> dict:
    if not 0.0 <= icc <= 1.0:
        raise ValueError("icc must be between 0 and 1")
    if cluster_size < 1.0:
        raise ValueError("cluster_size must be >= 1")
    if not 0.0 <= attrition < 1.0:
        raise ValueError("attrition must be in [0, 1)")
    deff = design_effect(cluster_size, icc)
    n_adj = n * deff
    n_final = n_adj / (1.0 - attrition) if attrition < 1 else float("inf")
    return {
        "individual_n_per_arm": math.ceil(n),
        "design_effect": round(deff, 4),
        "n_per_arm_after_deff": math.ceil(n_adj),
        "n_per_arm_after_attrition": math.ceil(n_final),
        "clusters_per_arm": math.ceil(n_final / cluster_size) if cluster_size > 1 else None,
        "attrition": attrition,
        "cluster_size": cluster_size,
        "icc": icc,
    }


def power_binary(args: argparse.Namespace) -> dict:
    p0 = args.baseline
    p1 = args.baseline * (1.0 + args.mde_relative)
    if not (0 < p0 < 1 and 0 < p1 < 1):
        raise ValueError("baseline and baseline*(1+mde) must be in (0, 1)")
    za = z(1.0 - args.alpha / 2.0)
    zb = z(args.power)
    n = ((za + zb) ** 2) * (p0 * (1 - p0) + p1 * (1 - p1)) / ((p1 - p0) ** 2)
    out = {
        "method": "binary_two_proportion",
        "baseline": p0,
        "treatment_assumed": round(p1, 6),
        "absolute_mde": round(p1 - p0, 6),
        "relative_mde": args.mde_relative,
        "alpha": args.alpha,
        "power": args.power,
    }
    out.update(inflate(n, args.icc, args.cluster_size, args.attrition))
    return out


def power_continuous(args: argparse.Namespace) -> dict:
    za = z(1.0 - args.alpha / 2.0)
    zb = z(args.power)
    n = 2.0 * ((za + zb) ** 2) * (args.sigma ** 2) / (args.delta ** 2)
    out = {
        "method": "continuous_two_mean",
        "sigma": args.sigma,
        "delta": args.delta,
        "alpha": args.alpha,
        "power": args.power,
    }
    out.update(inflate(n, args.icc, args.cluster_size, args.attrition))
    return out


def _n_binary(p0: float, p1: float, alpha: float, power: float) -> float:
    za = z(1.0 - alpha / 2.0)
    zb = z(power)
    return ((za + zb) ** 2) * (p0 * (1 - p0) + p1 * (1 - p1)) / ((p1 - p0) ** 2)


def mde_binary(args: argparse.Namespace) -> dict:
    p0 = args.baseline
    if not 0.0 < p0 < 1.0:
        raise ValueError("baseline must be in (0, 1)")
    if args.n_per_arm <= 0:
        raise ValueError("n_per_arm must be positive")
    lo, hi = 0.0, 1.0 - p0 - 1e-9
    target = args.n_per_arm
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _n_binary(p0, p0 + mid, args.alpha, args.power) > target:
            lo = mid
        else:
            hi = mid
    abs_mde = (lo + hi) / 2.0
    return {
        "method": "binary_mde_bisection",
        "baseline": p0,
        "n_per_arm": target,
        "alpha": args.alpha,
        "power": args.power,
        "absolute_mde": round(abs_mde, 6),
        "relative_mde": round(abs_mde / p0, 6),
        "treatment_assumed": round(p0 + abs_mde, 6),
    }


def test_binary(args: argparse.Namespace) -> dict:
    """Two-proportion readout: difference, relative lift, CI, and p-value."""
    p0, p1 = args.baseline, args.treatment
    n = args.n_per_arm
    if not 0.0 < p0 < 1.0 or not 0.0 < p1 < 1.0:
        raise ValueError("baseline and treatment must be in (0, 1)")
    if n <= 0:
        raise ValueError("n_per_arm must be positive")
    diff = p1 - p0
    se_unpooled = math.sqrt(p0 * (1.0 - p0) / n + p1 * (1.0 - p1) / n)
    p_pool = (p0 + p1) / 2.0
    se_pooled = math.sqrt(2.0 * p_pool * (1.0 - p_pool) / n)
    z_stat = diff / se_pooled
    p_value = 2.0 * (1.0 - NormalDist().cdf(abs(z_stat)))
    z_crit = z(1.0 - args.alpha / 2.0)
    ci_abs = (diff - z_crit * se_unpooled, diff + z_crit * se_unpooled)
    return {
        "method": "two_proportion_wald",
        "baseline": p0,
        "treatment": p1,
        "n_per_arm": n,
        "absolute_lift": round(diff, 6),
        "relative_lift": round(diff / p0, 6),
        "standard_error": round(se_unpooled, 8),
        "z_statistic": round(z_stat, 6),
        "p_value": p_value,
        "alpha": args.alpha,
        "ci_absolute": [round(ci_abs[0], 8), round(ci_abs[1], 8)],
        "ci_relative": [round(ci_abs[0] / p0, 6), round(ci_abs[1] / p0, 6)],
        "significant": p_value < args.alpha,
        "note": "Wald CI; for small n or extreme p use an exact or bootstrap method",
    }


def srm(args: argparse.Namespace) -> dict:
    counts = args.counts
    if len(counts) < 2:
        raise ValueError("need at least two arm counts")
    if any(c < 0 for c in counts):
        raise ValueError("counts must be non-negative")
    total = sum(counts)
    if total == 0:
        raise ValueError("counts sum to zero")
    expected = args.expected or [1.0 / len(counts)] * len(counts)
    if len(expected) != len(counts):
        raise ValueError("expected proportions must match counts")
    if any(e <= 0 for e in expected):
        raise ValueError("expected proportions must be positive")
    if abs(sum(expected) - 1.0) > 1e-6:
        raise ValueError("expected proportions must sum to 1")
    stat = sum((o - total * e) ** 2 / (total * e) for o, e in zip(counts, expected))
    df = len(counts) - 1
    p = chi2_sf(stat, df)
    return {
        "counts": counts,
        "expected_proportions": expected,
        "total": total,
        "chi_square": round(stat, 6),
        "df": df,
        "p_value": p,
        "threshold": args.threshold,
        "status": "fail" if p < args.threshold else "pass",
        "note": "p < threshold is a blocking S1; do not reweight to fix",
    }


def smd(args: argparse.Namespace) -> dict:
    pooled = math.sqrt((args.sd_t ** 2 + args.sd_c ** 2) / 2.0)
    if pooled == 0:
        raise ValueError("pooled SD is zero")
    value = (args.mean_t - args.mean_c) / pooled
    return {
        "smd": round(value, 6),
        "abs_smd": round(abs(value), 6),
        "mean_t": args.mean_t,
        "mean_c": args.mean_c,
        "sd_t": args.sd_t,
        "sd_c": args.sd_c,
        "interpretation": (
            "good" if abs(value) < 0.05 else "acceptable" if abs(value) <= 0.10 else "investigate"
        ),
    }


def cuped(args: argparse.Namespace) -> dict:
    x = [float(v) for v in args.x.split(",")]
    y = [float(v) for v in args.y.split(",")]
    if len(x) != len(y) or len(x) < 3:
        raise ValueError("x and y must be equal length, at least 3")
    mx, my = mean(x), mean(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / (len(x) - 1)
    var_x = sum((a - mx) ** 2 for a in x) / (len(x) - 1)
    var_y = sum((b - my) ** 2 for b in y) / (len(y) - 1)
    if var_x == 0:
        raise ValueError("x has zero variance")
    theta = cov / var_x
    rho = cov / math.sqrt(var_x * var_y) if var_y > 0 else 0.0
    adjusted = [b - theta * (a - mx) for a, b in zip(x, y)]
    return {
        "n": len(x),
        "theta": round(theta, 6),
        "correlation": round(rho, 6),
        "variance_reduction": round(rho ** 2, 6),
        "residual_variance_ratio": round(1 - rho ** 2, 6),
        "equivalent_sample_multiplier": round(1 / (1 - rho ** 2), 4) if rho ** 2 < 1 else None,
        "adjusted_mean": round(mean(adjusted), 6),
        "adjusted_sd": round(stdev(adjusted), 6),
        "raw_mean": round(my, 6),
        "raw_sd": round(stdev(y), 6),
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("power-binary", help="sample size for a two-proportion test")
    b.add_argument("--baseline", type=float, required=True)
    b.add_argument("--mde-relative", type=float, required=True)
    b.add_argument("--alpha", type=float, default=0.05)
    b.add_argument("--power", type=float, default=0.80)
    b.add_argument("--icc", type=float, default=0.0)
    b.add_argument("--cluster-size", type=float, default=1.0)
    b.add_argument("--attrition", type=float, default=0.0)
    b.set_defaults(func=power_binary)

    c = sub.add_parser("power-continuous", help="sample size for a two-mean test")
    c.add_argument("--sigma", type=float, required=True)
    c.add_argument("--delta", type=float, required=True)
    c.add_argument("--alpha", type=float, default=0.05)
    c.add_argument("--power", type=float, default=0.80)
    c.add_argument("--icc", type=float, default=0.0)
    c.add_argument("--cluster-size", type=float, default=1.0)
    c.add_argument("--attrition", type=float, default=0.0)
    c.set_defaults(func=power_continuous)

    m = sub.add_parser("mde-binary", help="minimum detectable effect given n per arm")
    m.add_argument("--baseline", type=float, required=True)
    m.add_argument("--n-per-arm", type=float, required=True)
    m.add_argument("--alpha", type=float, default=0.05)
    m.add_argument("--power", type=float, default=0.80)
    m.set_defaults(func=mde_binary)

    t = sub.add_parser("test-binary", help="two-proportion readout: lift, CI, p-value")
    t.add_argument("--baseline", type=float, required=True)
    t.add_argument("--treatment", type=float, required=True)
    t.add_argument("--n-per-arm", type=float, required=True)
    t.add_argument("--alpha", type=float, default=0.05)
    t.set_defaults(func=test_binary)

    s = sub.add_parser("srm", help="chi-square SRM check")
    s.add_argument("--counts", type=int, nargs="+", required=True)
    s.add_argument("--expected", type=float, nargs="+")
    s.add_argument("--threshold", type=float, default=0.001)
    s.set_defaults(func=srm)

    d = sub.add_parser("smd", help="standardized mean difference")
    d.add_argument("--mean-t", type=float, required=True)
    d.add_argument("--mean-c", type=float, required=True)
    d.add_argument("--sd-t", type=float, required=True)
    d.add_argument("--sd-c", type=float, required=True)
    d.set_defaults(func=smd)

    u = sub.add_parser("cuped", help="CUPED theta and variance reduction")
    u.add_argument("--x", required=True, help="comma-separated pre-period values")
    u.add_argument("--y", required=True, help="comma-separated outcome values")
    u.set_defaults(func=cuped)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
