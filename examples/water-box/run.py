#!/usr/bin/env python3
"""Run a reproducible pure-water box: minimization, NVT, NPT and production.

Requires GROMACS 2026.x on PATH; Python 3 standard library only.
Usage: python3 run.py --model tip4pew --temperature 298.15 --pressure 1 --prod-ns 10
"""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

MODELS = {
    "tip4pew": ("oplsaa.ff/tip4pew.itp", "tip4p.gro"),
    "spce": ("oplsaa.ff/spce.itp", "spc216.gro"),
}
COMMON = """\
cutoff-scheme          = Verlet
nstlist                = 20
rlist                  = 1.0
coulombtype            = PME
rcoulomb               = 1.0
vdwtype                = Cut-off
rvdw                   = 1.0
DispCorr               = EnerPres
pbc                    = xyz
"""


def run(args: list[str], directory: Path, log: str, stdin: str | None = None) -> None:
    """Execute a command, record its exact output and stop on nonzero exit."""
    print("+", " ".join(args), flush=True)
    with (directory / log).open("w", encoding="utf-8") as output:
        proc = subprocess.run(
            args, cwd=directory, input=stdin, text=True, stdout=output,
            stderr=subprocess.STDOUT, check=False,
        )
    if proc.returncode:
        tail = (directory / log).read_text(encoding="utf-8", errors="replace").splitlines()[-30:]
        raise RuntimeError(f"Error ({proc.returncode}) en {' '.join(args)}:\n" + "\n".join(tail))


def steps(ns: float) -> int:
    return round(ns * 500_000)  # dt=0.002 ps = 2 fs


def mdp(temperature: float, pressure: float, nsteps: int, *, mode: str, seed: int = 42) -> str:
    lines = [
        "integrator             = md",
        "dt                     = 0.002",
        f"nsteps                 = {nsteps}",
        f"continuation           = {'no' if mode == 'nvt' else 'yes'}",
        f"gen-vel                = {'yes' if mode == 'nvt' else 'no'}",
        "constraints            = h-bonds",
        "constraint-algorithm   = lincs",
        "tcoupl                 = V-rescale",
        "tc-grps                = System",
        "tau-t                  = 1.0",
        f"ref-t                  = {temperature}",
        "nstenergy              = 500",
        "nstcalcenergy          = 20",
        "nstlog                 = 5000",
        "nstxout-compressed     = 1000",
    ]
    if mode in {"nvt", "nvt-production"}:
        if mode == "nvt":
            lines += [f"gen-temp               = {temperature}", f"gen-seed               = {seed}"]
        lines += ["pcoupl                 = no"]
    else:
        lines += [
            "pcoupl                 = C-rescale",
            "pcoupltype             = isotropic",
            "tau-p                  = 5.0",
            f"ref-p                  = {pressure}",
            "compressibility        = 4.5e-5",
        ]
    return "\n".join(lines) + "\n" + COMMON


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, default="tip4pew")
    parser.add_argument("--ensemble", choices=("npt", "nvt"), default="npt",
                        help="Ensamble de producción; siempre equilibra primero en NPT")
    parser.add_argument("--temperature", type=float, default=298.15, help="Kelvin")
    parser.add_argument("--pressure", type=float, default=1.0, help="bar")
    parser.add_argument("--box", type=float, default=3.0, help="Longitud cúbica inicial (nm)")
    parser.add_argument("--npt-ns", type=float, default=1.0, help="Equilibración NPT (ns)")
    parser.add_argument("--prod-ns", type=float, default=10.0, help="Producción (ns)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, help="Directorio de resultados; no debe existir")
    opts = parser.parse_args()
    t, p, box, npt, prod = opts.temperature, opts.pressure, opts.box, opts.npt_ns, opts.prod_ns
    if not all(map(math.isfinite, (t, p, box, npt, prod))):
        parser.error("Los parámetros deben ser finitos.")
    if not (240 <= t <= 450 and 0.1 <= p <= 1000 and box >= 2.5):
        parser.error("Rango didáctico: T=240..450 K, P=0.1..1000 bar, caja>=2.5 nm.")
    if npt <= 0 or prod < 0.2 or opts.seed <= 0:
        parser.error("NPT debe ser positivo; producción >=0.2 ns; semilla positiva.")
    if not shutil.which("gmx"):
        parser.error("No se encontró gmx en PATH; cargar GMXRC antes de ejecutar.")

    name = f"{opts.model}_{opts.ensemble}_T{t:g}_P{p:g}_L{box:g}_seed{opts.seed}"
    directory = (opts.out or (Path.cwd() / "runs" / name)).resolve()
    if directory.exists():
        parser.error(f"Ya existe {directory}; no se sobreescriben resultados.")
    directory.mkdir(parents=True)
    itp, water_structure = MODELS[opts.model]
    (directory / "topol.top").write_text(
        '#include "oplsaa.ff/forcefield.itp"\n'
        f'#include "{itp}"\n\n'
        f"[ system ]\nAgua pura {opts.model}\n\n"
        "[ molecules ]\n; gmx solvate añade SOL y su cantidad.\n", encoding="utf-8"
    )
    run(["gmx", "--version"], directory, "version.log")
    run([
        "gmx", "solvate", "-cs", water_structure, "-box",
        str(box), str(box), str(box), "-o", "water.gro", "-p", "topol.top",
    ], directory, "solvate.log")
    topology = (directory / "topol.top").read_text(encoding="utf-8")
    matches = re.findall(r"(?m)^\s*SOL\s+(\d+)\s*$", topology)
    if len(matches) != 1 or int(matches[0]) <= 0:
        raise RuntimeError("gmx solvate no registró correctamente las moléculas SOL.")
    number_water = int(matches[0])

    (directory / "em.mdp").write_text(
        "integrator = steep\nnsteps = 50000\nemtol = 1000\nemstep = 0.01\n" + COMMON,
        encoding="utf-8",
    )
    (directory / "nvt.mdp").write_text(mdp(t, p, 50_000, mode="nvt", seed=opts.seed), encoding="utf-8")
    (directory / "npt.mdp").write_text(mdp(t, p, steps(npt), mode="npt"), encoding="utf-8")
    (directory / "md.mdp").write_text(
        mdp(t, p, steps(prod), mode="md" if opts.ensemble == "npt" else "nvt-production"),
        encoding="utf-8",
    )

    stages = [
        ("em", ["-c", "water.gro"]),
        ("nvt", ["-c", "em.gro"]),
        ("npt", ["-c", "nvt.gro", "-t", "nvt.cpt"]),
        ("md", ["-c", "npt.gro", "-t", "npt.cpt"]),
    ]
    for stage, continuation in stages:
        run([
            "gmx", "grompp", "-f", stage + ".mdp",
            *continuation, "-p", "topol.top", "-o", stage + ".tpr",
        ], directory, f"grompp_{stage}.log")
        run(["gmx", "mdrun", "-deffnm", stage], directory, f"mdrun_{stage}.log")

    run([
        "gmx", "energy", "-f", "md.edr", "-xvg", "none", "-o", "thermo.xvg",
    ], directory, "energy.log", "Temperature\nPressure\nDensity\nVolume\nEnthalpy\n0\n")
    run([
        "gmx", "rdf", "-s", "md.tpr", "-f", "md.xtc",
        "-ref", "name OW", "-sel", "name OW",
        "-o", "rdf_oo.xvg", "-cn", "coordination_oo.xvg", "-xvg", "none",
    ], directory, "rdf.log")
    run([
        "gmx", "msd", "-s", "md.tpr", "-f", "md.xtc",
        "-sel", "name OW", "-maxtau", "100", "-beginfit", "20",
        "-endfit", "80", "-o", "msd_ow.xvg", "-xvg", "none",
    ], directory, "msd.log")
    (directory / "metadata.txt").write_text(
        f"model={opts.model}\nensemble={opts.ensemble}\nT_K={t}\nP_bar={p}\nL_nm={box}\n"
        f"Nwater={number_water}\nNPT_ns={npt}\nproduction_ns={prod}\n"
        f"seed={opts.seed}\n",
        encoding="utf-8",
    )
    run([sys.executable, str(Path(__file__).resolve().with_name("analyze.py")), str(directory)],
        directory, "analysis.log")
    print(f"Resultados: {directory}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
