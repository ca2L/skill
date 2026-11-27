#!/usr/bin/env python3
"""Unit tests for experiment_stats.py. Stdlib only.

Run: python scripts/test_experiment_stats.py
"""
from __future__ import annotations

import argparse
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("experiment_stats.py")
_spec = importlib.util.spec_from_file_location("experiment_stats", MODULE_PATH)
stats = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stats)


def ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


class TestPower(unittest.TestCase):
    def test_binary_canonical(self) -> None:
        out = stats.power_binary(
            ns(baseline=0.084, mde_relative=0.11, alpha=0.05, power=0.80,
               icc=0.0, cluster_size=1.0, attrition=0.0)
        )
        self.assertEqual(out["individual_n_per_arm"], 14847)
        self.assertAlmostEqual(out["absolute_mde"], 0.00924, places=6)
        self.assertEqual(out["design_effect"], 1.0)

    def test_binary_cluster_inflation(self) -> None:
        out = stats.power_binary(
            ns(baseline=0.084, mde_relative=0.08, alpha=0.05, power=0.80,
               icc=0.05, cluster_size=5.0, attrition=0.10)
        )
        self.assertAlmostEqual(out["design_effect"], 1.2, places=4)
        self.assertGreater(out["n_per_arm_after_deff"], out["individual_n_per_arm"])
        self.assertGreater(out["n_per_arm_after_attrition"], out["n_per_arm_after_deff"])
        self.assertIsNotNone(out["clusters_per_arm"])

    def test_continuous(self) -> None:
        out = stats.power_continuous(
            ns(sigma=120, delta=10, alpha=0.05, power=0.80,
               icc=0.02, cluster_size=4.0, attrition=0.05)
        )
        self.assertGreater(out["n_per_arm_after_attrition"], 0)
        self.assertAlmostEqual(out["design_effect"], 1.06, places=4)

    def test_bad_power_inputs(self) -> None:
        with self.assertRaises(ValueError):
            stats.power_binary(
                ns(baseline=0.0, mde_relative=0.1, alpha=0.05, power=0.80,
                   icc=0.0, cluster_size=1.0, attrition=0.0)
            )
        with self.assertRaises(ValueError):
            stats.inflate(100, 1.1, 5, 0)
        with self.assertRaises(ValueError):
            stats.inflate(100, 0.1, 0.5, 0)
        with self.assertRaises(ValueError):
            stats.inflate(100, 0.1, 5, 1.0)


class TestMDE(unittest.TestCase):
    def test_canonical(self) -> None:
        out = stats.mde_binary(
            ns(baseline=0.084, n_per_arm=16000, alpha=0.05, power=0.80)
        )
        self.assertAlmostEqual(out["absolute_mde"], 0.008893, places=6)
        self.assertAlmostEqual(out["relative_mde"], 0.105866, places=6)

    def test_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            stats.mde_binary(ns(baseline=0.0, n_per_arm=1000, alpha=0.05, power=0.80))
        with self.assertRaises(ValueError):
            stats.mde_binary(ns(baseline=0.1, n_per_arm=0, alpha=0.05, power=0.80))


class TestReadout(unittest.TestCase):
    def test_canonical(self) -> None:
        out = stats.test_binary(
            ns(baseline=0.084, treatment=0.092, n_per_arm=16000, alpha=0.05)
        )
        self.assertAlmostEqual(out["absolute_lift"], 0.008, places=8)
        self.assertAlmostEqual(out["relative_lift"], 0.095238, places=6)
        self.assertAlmostEqual(out["p_value"], 0.011544, places=6)
        self.assertAlmostEqual(out["ci_absolute"][0], 0.00179276, places=8)
        self.assertAlmostEqual(out["ci_absolute"][1], 0.01420724, places=8)
        self.assertAlmostEqual(out["ci_relative"][0], 0.021342, places=6)
        self.assertAlmostEqual(out["ci_relative"][1], 0.169134, places=6)
        self.assertTrue(out["significant"])

    def test_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            stats.test_binary(ns(baseline=0.0, treatment=0.1, n_per_arm=100, alpha=0.05))
        with self.assertRaises(ValueError):
            stats.test_binary(ns(baseline=0.1, treatment=1.0, n_per_arm=100, alpha=0.05))
        with self.assertRaises(ValueError):
            stats.test_binary(ns(baseline=0.1, treatment=0.2, n_per_arm=0, alpha=0.05))


class TestDataQuality(unittest.TestCase):
    def test_srm_pass(self) -> None:
        out = stats.srm(ns(counts=[16000, 15850], expected=None, threshold=0.001))
        self.assertEqual(out["status"], "pass")
        self.assertAlmostEqual(out["chi_square"], 0.706436, places=6)
        self.assertAlmostEqual(out["p_value"], 0.400629, places=6)

    def test_srm_fail(self) -> None:
        out = stats.srm(ns(counts=[8000, 10000], expected=None, threshold=0.001))
        self.assertEqual(out["status"], "fail")

    def test_srm_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            stats.srm(ns(counts=[-1, 100], expected=None, threshold=0.001))
        with self.assertRaises(ValueError):
            stats.srm(ns(counts=[0, 0], expected=None, threshold=0.001))
        with self.assertRaises(ValueError):
            stats.srm(ns(counts=[10, 20], expected=[0.5, 0.6], threshold=0.001))
        with self.assertRaises(ValueError):
            stats.srm(ns(counts=[10, 20], expected=[0.5, 0.5, 0.0], threshold=0.001))

    def test_smd(self) -> None:
        out = stats.smd(ns(mean_t=10, mean_c=9.5, sd_t=4, sd_c=4.2))
        self.assertAlmostEqual(out["abs_smd"], 0.1219, places=3)
        self.assertEqual(out["interpretation"], "investigate")

    def test_smd_zero_variance(self) -> None:
        with self.assertRaises(ValueError):
            stats.smd(ns(mean_t=10, mean_c=9.5, sd_t=0, sd_c=0))


class TestCUPED(unittest.TestCase):
    def test_canonical(self) -> None:
        out = stats.cuped(ns(x="1,2,3,4,5,6", y="2,4,5,8,9,11"))
        self.assertAlmostEqual(out["correlation"], 0.9930, places=3)
        self.assertAlmostEqual(out["variance_reduction"], 0.9861, places=3)
        self.assertAlmostEqual(out["residual_variance_ratio"], 0.0139, places=3)

    def test_bad_inputs(self) -> None:
        with self.assertRaises(ValueError):
            stats.cuped(ns(x="1,2", y="3,4"))
        with self.assertRaises(ValueError):
            stats.cuped(ns(x="1,1,1", y="2,3,4"))


class TestDesignEffect(unittest.TestCase):
    def test_values(self) -> None:
        self.assertEqual(stats.design_effect(1, 0.5), 1.0)
        self.assertEqual(stats.design_effect(5, 0.0), 1.0)
        self.assertAlmostEqual(stats.design_effect(5, 0.05), 1.2, places=6)
        self.assertAlmostEqual(stats.design_effect(10, 0.1), 1.9, places=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
