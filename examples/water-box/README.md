# Laboratorio de propiedades del agua (GROMACS 2026.x)

Código complementario al capítulo [Proteína en agua](../../source/proteina-agua.md#laboratorio-de-agua-pura-condiciones-y-propiedades-fisicas). Reproduce una caja de agua sin solutos mediante modelos TIP4P-Ew o SPC/E de la familia OPLS-AA.

## Ejecución

Requiere `gmx` disponible en `PATH` y Python 3. Opcional: `pip install matplotlib` para gráficos PNG. Los scripts de análisis y ejecución usan exclusivamente la biblioteca estándar de Python.

```bash
cd examples/water-box

python3 run.py --model tip4pew --temperature 298.15 --pressure 1 \
    --box 3 --ensemble npt --npt-ns 1 --prod-ns 10 --seed 42

python3 run.py --model spce --temperature 310 --pressure 100 \
    --box 4 --ensemble nvt --npt-ns 2 --prod-ns 20 --seed 43
```

`--ensemble nvt` usa la caja tras una equilibración NPT a la presión solicitada, y entonces fija su volumen en producción. No extrapolar propiedades de fluctuaciones de volumen en NVT.

En cada ejecución se generan archivos MDP completos, una topología coherente con el modelo seleccionado, estructura `water.gro`, etapas `em`, `nvt`, `npt`, `md`, archivos de energía y trayectoria, `thermo.xvg`, `rdf_oo.xvg`, `msd_ow.xvg`, `summary.json`, `summary.csv` y `pmf_oo.csv`. Los PNG se generan cuando está instalado matplotlib.

Los resultados se guardan en `runs/<modelo>_<ensamble>_T<temperatura>_P<presión>_L<caja>_seed<semilla>/`. Nunca se sobrescribe un directorio ya existente. Se puede usar `--out` para elegir otra ruta.

### Ejemplos de experimentos

```bash
# Curva de densidad con temperatura variable
for T in 280 298.15 310 330; do
    python3 run.py --temperature "$T" --pressure 1 --prod-ns 10
done

# Efectos de tamaño finito: difusión y fluctuaciones
for L in 3 4 6; do
    python3 run.py --temperature 298.15 --pressure 1 --box "$L" --prod-ns 20
done
```

`summary.json` separa explícitamente propiedades aproximadas de fluctuación (`compressibility_fluct_bar_inv`, `thermal_expansion_fluct_K_inv`, `Cp_fluct_J_mol_K`). Son exploratorias y deben contrastarse con réplicas, análisis por bloques y autocorrelación.

### Reejecutar análisis

```bash
python3 analyze.py runs/tip4pew_npt_T298.15_P1_L3_seed42
```

Requiere `metadata.txt`, `thermo.xvg`, `rdf_oo.xvg` y `msd_ow.xvg` ya generados.

### Pruebas estáticas sin GROMACS

```bash
python3 -m unittest discover -s tests -p 'test_water_box.py' -v
```

Las pruebas comprueban generación de MDP NVT/NPT, conversión de tiempos, ajuste lineal, lectura de leyendas XVG y fallos por datos inconsistentes. No constituyen validación física de los modelos. La ejecución real debe realizarse en un equipo con GROMACS instalado.

**Fuentes:**

- [GASERI: TIP4P-Ew water](https://gaseri.org/en/tutorials/gromacs/1-tip4pew-water/)
- [Yoo Lab: Biomodeling water box](https://sites.google.com/view/yoo-lab/lectures/biomodeling/biomodeling-water-box)
- [Manual GROMACS 2026.3](https://manual.gromacs.org/2026.3/)
