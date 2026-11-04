#!/usr/bin/env python3
"""Extract bulk-water properties from a GROMACS water-box run.

No external Python dependencies. Optional plots require matplotlib.
Thermodynamic fluctuation estimators need converged NPT sampling.
"""
from __future__ import annotations

import csv
import json
import math
import statistics as stats
import sys
from pathlib import Path

R = 0.008314462618  # kJ mol^-1 K^-1
KB_BAR_NM3_K = 0.1380649  # k_B in bar nm^3 K^-1


def read_xvg(path: Path) -> list[list[float]]:
    data: list[list[float]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "@")):
            continue
        if line == "&":
            break
        try:
            row = [float(x) for x in line.split()]
        except ValueError as exc:
            raise ValueError(f"Fila no numérica en {path}: {line}") from exc
        if not all(map(math.isfinite, row)):
            raise ValueError(f"Datos no finitos en {path}: {line}")
        if data and len(row) != len(data[0]):
            raise ValueError(f"Columnas inconsistentes en {path}")
        data.append(row)
    if not data:
        raise ValueError(f"Sin datos numéricos: {path}")
    return data


def linear_fit(x: list[float], y: list[float]) -> float:
    x_mean, y_mean = stats.mean(x), stats.mean(y)
    den = sum((z - x_mean) ** 2 for z in x)
    if not den:
        raise ValueError("No hay suficientes tiempos distintos.")
    return sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y)) / den


def block_se(values: list[float], n_blocks: int = 5) -> float | None:
    if len(values) < 10 * n_blocks:
        return None
    means = [
        stats.mean(values[(i * len(values)) // n_blocks:((i + 1) * len(values)) // n_blocks])
        for i in range(n_blocks)
    ]
    return stats.stdev(means) / math.sqrt(n_blocks)


def plot_results(folder: Path, time: list[float], density: list[float],
                 rdf: list[list[float]], msd: list[list[float]],
                 pmf: list[tuple[float, float]]) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no instalado; se omiten PNG, se conservan XVG y CSV.")
        return

    def save(x, y, xlabel, ylabel, filename):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(x, y, linewidth=1.5)
        ax.set(xlabel=xlabel, ylabel=ylabel)
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(folder / filename, dpi=160)
        plt.close(fig)

    save([x / 1000 for x in time], density, "Tiempo (ns)", "Densidad (kg/m³)", "density.png")
    save([r[0] for r in rdf], [r[1] for r in rdf], "r (nm)", "gOO(r)", "rdf_oo.png")
    save([r[0] for r in msd], [r[1] for r in msd], "Tiempo de retardo (ps)",
         "MSD (nm²)", "msd_ow.png")
    if pmf:
        save([r for r, _ in pmf], [v for _, v in pmf],
             "r (nm)", "PMF estructural (kJ/mol)", "pmf_oo.png")


def main(folder: Path) -> None:
    metadata = dict(
        line.split("=", 1)
        for line in (folder / "metadata.txt").read_text(encoding="utf-8").splitlines()
        if "=" in line
    )
    n_water = int(metadata["Nwater"])
    thermo = read_xvg(folder / "thermo.xvg")
    if len(thermo[0]) != 6 or len(thermo) < 20:
        raise ValueError("Se esperaban 6 columnas: tiempo, T, P, rho, V, H; y >=20 filas.")
    # El orden de columnas corresponde al orden de selección enviado a gmx energy en run.py.
    time, temperature, pressure, density, volume, enthalpy = map(list, zip(*thermo))
    t = stats.mean(temperature)
    vol = stats.mean(volume)
    rho = stats.mean(density)

    # Fluctuaciones NPT: valores exploratorios (muestreo y tamaño finito sensibles).
    var_vol = stats.pvariance(volume)
    var_h = stats.pvariance(enthalpy)
    cov_vh = stats.mean((v - vol) * (h - stats.mean(enthalpy))
                        for v, h in zip(volume, enthalpy))
    kappa = var_vol / (KB_BAR_NM3_K * t * vol)  # bar^-1
    alpha = cov_vh / (R * t * t * vol)  # K^-1, H en kJ/mol del sistema
    cp = (var_h / (R * t * t)) * 1000 / n_water  # J mol^-1_water K^-1

    rdf = read_xvg(folder / "rdf_oo.xvg")
    msd = read_xvg(folder / "msd_ow.xvg")
    if min(len(rdf[0]), len(msd[0])) < 2:
        raise ValueError("RDF/MSD requieren al menos dos columnas.")
    fit = [row for row in msd if 20 <= row[0] <= 80]
    diffusion = None
    if len(fit) >= 5:
        slope = linear_fit([row[0] for row in fit], [row[1] for row in fit])
        diffusion = slope / 6 * 1e-6  # (nm²/ps) -> m²/s
    peaks = [row for row in rdf if 0.20 <= row[0] <= 0.45]
    peak_r, peak_g = (max(peaks, key=lambda r: r[1])[:2] if peaks else (None, None))
    pmf = [(r[0], -R * t * math.log(r[1])) for r in rdf if r[1] > 0 and r[0] >= 0.2]
    with (folder / "pmf_oo.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["r_nm", "W_kJ_mol"])
        writer.writerows(pmf)

    result = {
        "model": metadata["model"],
        "temperature_target_K": float(metadata["T_K"]),
        "pressure_target_bar": float(metadata["P_bar"]),
        "Nwater": n_water,
        "temperature_mean_K": t,
        "pressure_mean_bar": stats.mean(pressure),
        "density_mean_kg_m3": rho,
        "density_block_se_kg_m3": block_se(density),
        "volume_mean_nm3": vol,
        "diffusion_OW_m2_s": diffusion,
        "rdf_first_peak_r_nm": peak_r,
        "rdf_first_peak_g": peak_g,
        "compressibility_fluct_bar_inv": kappa,
        "thermal_expansion_fluct_K_inv": alpha,
        "Cp_fluct_J_mol_K": cp,
        "n_thermo_samples": len(thermo),
        "caveat": "Estimadores de fluctuación no validados: requieren mayor muestreo, autocorrelación y réplicas.",
    }
    (folder / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (folder / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result))
        writer.writeheader()
        writer.writerow(result)
    plot_results(folder, time, density, rdf, msd, pmf)
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python3 analyze.py DIRECTORIO")
    main(Path(sys.argv[1]).resolve())
