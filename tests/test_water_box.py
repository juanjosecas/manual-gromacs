"""Static regression tests for pure-water MD input generation and XVG analysis.

Do not execute molecular dynamics: these tests run without GROMACS.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "examples" / "water-box"


def load(name):
    spec = importlib.util.spec_from_file_location(name, BASE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load("run")
analysis = load("analyze")


class WaterBoxTests(unittest.TestCase):
    def test_timescale(self):
        self.assertEqual(runner.steps(1), 500_000)
        self.assertEqual(runner.steps(10), 5_000_000)

    def test_ensemble_switch(self):
        npt = runner.mdp(298.15, 1, 500_000, mode="md")
        nvt = runner.mdp(298.15, 1, 500_000, mode="nvt-production")
        initial = runner.mdp(298.15, 1, 50_000, mode="nvt")
        self.assertIn("pcoupl                 = C-rescale", npt)
        self.assertIn("pcoupl                 = no", nvt)
        self.assertIn("gen-vel                = no", nvt)
        self.assertIn("continuation           = yes", nvt)
        self.assertIn("gen-vel                = yes", initial)
        self.assertIn("DispCorr               = EnerPres", npt)

    def test_xvg_legends_order_independent(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "thermo.xvg"
            path.write_text(
                '@ s0 legend "Density"\n'
                '@ s1 legend "Volume"\n'
                '@ s2 legend "Pressure"\n'
                '@ s3 legend "Enthalpy"\n'
                '@ s4 legend "Temperature"\n'
                '0 998 27 1.5 -40000 298\n'
                '1 999 26.9 2.0 -40010 299\n',
                encoding="utf-8",
            )
            time, t, p, rho, vol, enthalpy = analysis.read_thermo(path, "npt")
            self.assertEqual(time, [0, 1])
            self.assertEqual(t, [298, 299])
            self.assertEqual(p, [1.5, 2.0])
            self.assertEqual(rho, [998, 999])
            self.assertEqual(vol, [27, 26.9])
            self.assertEqual(enthalpy, [-40000, -40010])

    def test_xvg_missing_legend_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "thermo.xvg"
            path.write_text("0 1 2\n1 2 3\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                analysis.read_thermo(path, "npt")

    def test_msd_linear_fit(self):
        self.assertAlmostEqual(analysis.linear_fit([1, 2, 3], [2, 4, 6]), 2.0)

    def test_block_error(self):
        self.assertIsNone(analysis.block_se(list(range(10))))
        self.assertGreater(analysis.block_se(list(range(100))), 0)


if __name__ == "__main__":
    unittest.main()
