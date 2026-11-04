## Energía libre de perturbación: energía libre de solvatación

### Caso de estudio: formaldehído en agua

La energía libre de solvatación describe el cambio de energía libre asociado con transferir una especie química desde una fase de referencia —habitualmente gas ideal— hasta una solución a dilución infinita:

$$
\Delta G_{\mathrm{solv}} =
G_{\mathrm{soluto,solución}}-
G_{\mathrm{soluto,gas}}
$$

Una $\Delta G_{\mathrm{solv}}<0$ indica que la transferencia al solvente es favorable bajo la convención y los estados estándar especificados. La magnitud depende de la identidad química, el estado de protonación, el solvente, la temperatura, el campo de fuerza, los estados estándar, el tratamiento electrostático, el tamaño de caja y el muestreo.

Este tutorial muestra un cálculo alquímico de una molécula neutra. El formaldehído sirve para ilustrar la mecánica de GROMACS, pero presenta una limitación química crítica: en agua reacciona para formar metanodiol. El resultado obtenido con una topología no reactiva corresponde al formaldehído molecular $\mathrm{H_2CO}$, no al equilibrio químico completo de una solución de formaldehído.

### 1. Fundamento del método

Los estados físicos A y B pueden tener distribuciones configuracionales con poca superposición. Se construye entonces un camino alquímico mediante $\lambda$:

$$
H(\mathbf{x};\lambda)
$$

Una interpolación conceptual sencilla es:

$$
H(\lambda)=(1-\lambda)H_A+\lambda H_B
$$

Los estados intermedios no necesitan ser físicamente realizables. Solo deben conectar los extremos mediante una ruta reversible con superposición estadística suficiente.

Para un desacoplamiento en solución:

```text
λ = 0                         λ = 1
soluto completamente          soluto sin interacciones
acoplado al agua              no enlazadas con el agua
```

Las interacciones internas del soluto se mantienen. La molécula desacoplada sigue presente en las coordenadas, pero no ejerce interacciones de Coulomb ni Lennard-Jones sobre el solvente.

### 2. FEP, TI, BAR y MBAR

La ecuación de Zwanzig es:

$$
\Delta G_{A\rightarrow B}
=
-k_\mathrm{B}T
\ln
\left\langle
\exp[-\beta(U_B-U_A)]
\right\rangle_A
$$

con $\beta=1/(k_\mathrm{B}T)$, o $\beta=1/(RT)$ para cantidades molares. Es exacta en el límite de muestreo infinito, pero ineficiente cuando A y B tienen poca superposición.

En integración termodinámica:

$$
\Delta G_{A\rightarrow B}
=
\int_0^1
\left\langle
\frac{\partial H}{\partial\lambda}
\right\rangle_\lambda
d\lambda
$$

TI requiere una grilla que resuelva la curvatura del integrando y una integración numérica apropiada.

BAR combina información en ambas direcciones entre dos estados vecinos. MBAR analiza todos los estados conjuntamente. Ninguno corrige una ruta alquímico mal diseñada ni grados de libertad sin muestrear.

Este tutorial utiliza **gmx bar**, incluido en GROMACS.

### 3. Convención de signo

Definamos:

- estado 0: formaldehído acoplado al agua;
- estado 1: formaldehído desacoplado del agua.

La simulación calcula:

$$
\Delta G_{0\rightarrow1}
=
G_{\mathrm{desacoplado}}-
G_{\mathrm{acoplado}}
=
\Delta G_{\mathrm{desacoplamiento}}
$$

Por lo tanto:

$$
\boxed{
\Delta G_{\mathrm{solv}}
=
-\Delta G_{0\rightarrow1}
}
$$

Si se invierten **couple-lambda0** y **couple-lambda1**, también se invierte el signo. Antes de interpretar un número, escriba qué representa cada extremo.

### 4. Separar Coulomb y Lennard-Jones

Apagar simultáneamente cargas y Lennard-Jones puede servir en un ejercicio corto, pero no es la ruta preferida para un resultado cuantitativo.

Una secuencia habitual es:

1. apagar electrostática mientras el volumen excluido permanece;
2. apagar Lennard-Jones mediante potenciales soft-core.

Si desaparece primero el volumen excluido, el solvente puede ocupar la posición del soluto mientras todavía existen cargas puntuales.

$$
\Delta G_{\mathrm{desacoplamiento}}
=
\Delta G_{\mathrm{Coulomb}}
+
\Delta G_{\mathrm{LJ}}
$$

Esta separación permite identificar qué componente necesita mayor densidad de estados λ.

### 5. Potenciales soft-core

La interpolación lineal de Lennard-Jones puede producir divergencias cuando dos partículas se superponen. Los potenciales soft-core mantienen finita la energía en estados intermedios.

```ini
sc-alpha       = 0.5
sc-power       = 1
sc-sigma       = 0.3
sc-coul        = no
```

Son valores iniciales, no constantes universales. **sc-power** requiere un entero y **sc-sigma** se expresa en nm. Como Coulomb se elimina antes que Lennard-Jones, no se activa soft-core electrostático.

### 6. Selección de estados λ

Agregar estados uniformemente no garantiza precisión. Conviene aumentar su densidad donde disminuye la superposición, crece la varianza, entra solvente en una cavidad o cambia rápidamente el potencial soft-core.

Grilla inicial de 19 estados:

```ini
coul-lambdas = 0.00 0.25 0.50 0.75 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00

vdw-lambdas  = 0.00 0.00 0.00 0.00 0.00 0.05 0.10 0.15 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.85 0.90 0.95 1.00
```

Los índices 0–4 descargan el soluto y los índices 4–18 eliminan Lennard-Jones. El estado 4 es común a ambas etapas. La grilla debe reajustarse después de analizar solapamiento y errores por intervalo.

### 7. Parametrización del formaldehído

La topología debe ser compatible con el campo de fuerza y el modelo de agua. No use automáticamente parámetros antiguos de CHARMM27 ni copie tipos de SwissParam sin validación.

Compruebe:

- fórmula $\mathrm{CH_2O}$;
- geometría trigonal plana;
- carga neta cero;
- nombres y orden de átomos;
- cargas parciales;
- parámetros enlazados;
- interacción del carbonilo;
- compatibilidad con el campo de fuerza;
- ausencia de tipos atómicos duplicados.

Organización sugerida:

```text
00_parametros/
    formaldehyde.gro
    formaldehyde.itp
    formaldehyde_atomtypes.itp
01_preparacion/
02_equilibracion/
03_fep/
04_analisis/
topol.top
```

Topología general:

```ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/formaldehyde_atomtypes.itp"
#include "00_parametros/formaldehyde.itp"
#include "campo_de_fuerza.ff/modelo_de_agua.itp"

[ system ]
Formaldehído molecular en agua

[ molecules ]
FOR    1
SOL    NUMERO_DE_AGUAS
```

**FOR** debe coincidir con `[ moleculetype ]`. Si existen varias moléculas FOR, **couple-moltype = FOR** perturbará todas. Para desacoplar una sola copia se necesita un tipo molecular exclusivo.

### 8. Construcción de la caja

```bash
gmx editconf \
    -f 00_parametros/formaldehyde.gro \
    -o 01_preparacion/formaldehyde_box.gro \
    -c \
    -d 1.2 \
    -bt dodecahedron
```

La distancia de 1.2 nm es inicial. Debe reducir interacciones con imágenes periódicas y ser coherente con los cortes.

```bash
gmx solvate \
    -cp 01_preparacion/formaldehyde_box.gro \
    -cs spc216.gro \
    -o 01_preparacion/formaldehyde_water.gro \
    -p topol.top
```

**spc216.gro** aporta coordenadas de agua de tres sitios. El modelo físico queda determinado por la topología incluida.

Para una sola molécula no hace falta insertarla en una caja vacía y luego redefinir otra caja: **editconf** seguido de **solvate** es suficiente.

### 9. Minimización

```ini
title           = EM de formaldehído en agua
integrator      = steep
nsteps          = 50000
emtol           = 1000.0
emstep          = 0.01

cutoff-scheme   = Verlet
nstlist         = 20
rlist           = 1.2
coulombtype     = PME
rcoulomb        = 1.2
vdwtype         = Cut-off
rvdw            = 1.2
pbc             = xyz
```

Los cortes deben adaptarse al campo de fuerza.

```bash
mkdir -p 02_equilibracion

gmx grompp \
    -f em.mdp \
    -c 01_preparacion/formaldehyde_water.gro \
    -p topol.top \
    -o 02_equilibracion/em.tpr \
    -pp 02_equilibracion/processed.top

gmx mdrun \
    -deffnm 02_equilibracion/em \
    -v
```

Terminar por alcanzar **nsteps** sin cumplir **emtol** no significa convergencia. Una fuerza máxima de miles de kJ·mol⁻¹·nm⁻¹ debe investigarse.

### 10. Equilibración física previa

NVT:

```ini
title         = NVT previa a FEP
integrator    = md
dt            = 0.002
nsteps        = 250000
continuation  = no
gen-vel       = yes
gen-temp      = 298.15
gen-seed      = 2026

constraints   = h-bonds
tcoupl        = V-rescale
tc-grps       = System
tau-t         = 1.0
ref-t         = 298.15
pcoupl        = no
pbc           = xyz
```

```bash
gmx grompp \
    -f nvt.mdp \
    -c 02_equilibracion/em.gro \
    -p topol.top \
    -o 02_equilibracion/nvt.tpr

gmx mdrun -deffnm 02_equilibracion/nvt -v
```

NPT:

```ini
title            = NPT previa a FEP
integrator       = md
dt               = 0.002
nsteps           = 1000000
continuation     = yes
gen-vel          = no

constraints      = h-bonds
tcoupl           = V-rescale
tc-grps          = System
tau-t            = 1.0
ref-t            = 298.15

pcoupl            = C-rescale
pcoupltype        = isotropic
tau-p             = 5.0
ref-p             = 1.0
compressibility   = 4.5e-5
pbc               = xyz
```

```bash
gmx grompp \
    -f npt.mdp \
    -c 02_equilibracion/nvt.gro \
    -t 02_equilibracion/nvt.cpt \
    -p topol.top \
    -o 02_equilibracion/npt.tpr

gmx mdrun -deffnm 02_equilibracion/npt -v
```

Cuarenta picosegundos no constituyen una duración universal de equilibración. Evalúe densidad, volumen, energía y relajación del solvente.

### 11. Bloque MDP para desacoplamiento

Mantenga los parámetros no enlazados del protocolo validado y añada:

```ini
free-energy            = yes
couple-moltype         = FOR

; λ=0 acoplado; λ=1 desacoplado
couple-lambda0         = vdw-q
couple-lambda1         = none
couple-intramol        = no

coul-lambdas = 0.00 0.25 0.50 0.75 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00
vdw-lambdas  = 0.00 0.00 0.00 0.00 0.00 0.05 0.10 0.15 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.85 0.90 0.95 1.00

init-lambda-state      = LAMBDA_STATE
calc-lambda-neighbors  = 1

sc-alpha               = 0.5
sc-power               = 1
sc-sigma               = 0.3
sc-coul                = no

nstdhdl                = 100
dhdl-derivatives       = yes
separate-dhdl-file     = yes
```

**calc-lambda-neighbors = 1** calcula diferencias con estados vecinos para BAR. **nstdhdl** debe ser múltiplo de **nstcalcenergy**.

**init-lambda-state** es el índice entero de las listas, no el valor de λ. No use simultáneamente **fep-lambdas** y **coul-lambdas/vdw-lambdas** para describir la misma ruta sin controlar cómo se forma el vector λ.

### 12. Equilibrar cada estado

Prepare:

- **fep_equilibration.template.mdp** para relajar cada Hamiltoniano;
- **fep_production.template.mdp** para acumular datos.

Ambos contienen **LAMBDA_STATE**.

Equilibración por ventana:

```ini
nsteps       = 250000
nstdhdl      = 0
gen-vel      = yes
gen-temp     = 298.15
gen-seed     = -1
```

Producción por ventana:

```ini
nsteps       = 2500000
nstdhdl      = 100
gen-vel      = no
continuation = yes
```

Con $dt=0.002\ \mathrm{ps}$, corresponden a 0.5 ns y 5 ns. Son puntos de partida, no garantías de convergencia.

### 13. Crear y ejecutar las ventanas

Script para Bash 4 o superior:

```bash
#!/usr/bin/env bash
set -euo pipefail

GMX_COMMAND="${GMX_COMMAND:-gmx}"
START_STRUCTURE="02_equilibracion/npt.gro"
TOPOLOGY="topol.top"

for STATE in $(seq 0 18)
do
    DIRECTORY=$(printf "03_fep/lambda_%02d" "${STATE}")
    mkdir -p "${DIRECTORY}"

    sed "s/LAMBDA_STATE/${STATE}/g" \
        fep_equilibration.template.mdp \
        > "${DIRECTORY}/equilibration.mdp"

    sed "s/LAMBDA_STATE/${STATE}/g" \
        fep_production.template.mdp \
        > "${DIRECTORY}/production.mdp"

    "${GMX_COMMAND}" grompp \
        -f "${DIRECTORY}/equilibration.mdp" \
        -c "${START_STRUCTURE}" \
        -p "${TOPOLOGY}" \
        -o "${DIRECTORY}/equilibration.tpr"

    "${GMX_COMMAND}" mdrun \
        -deffnm "${DIRECTORY}/equilibration" \
        -v

    "${GMX_COMMAND}" grompp \
        -f "${DIRECTORY}/production.mdp" \
        -c "${DIRECTORY}/equilibration.gro" \
        -t "${DIRECTORY}/equilibration.cpt" \
        -p "${TOPOLOGY}" \
        -o "${DIRECTORY}/production.tpr"

    "${GMX_COMMAND}" mdrun \
        -deffnm "${DIRECTORY}/production" \
        -dhdl "${DIRECTORY}/dhdl.xvg" \
        -v
done
```

```bash
chmod +x run_fep.sh
bash -n run_fep.sh
./run_fep.sh
```

Las ventanas son independientes después de generar sus TPR y pueden ejecutarse como un array de trabajos. No use el mismo directorio o nombre de salida para ventanas diferentes.

### 14. Ejecución en un array HPC

Ejemplo mínimo basado en **SLURM_ARRAY_TASK_ID**:

```bash
STATE="${SLURM_ARRAY_TASK_ID}"
DIRECTORY=$(printf "03_fep/lambda_%02d" "${STATE}")

gmx mdrun \
    -deffnm "${DIRECTORY}/production" \
    -dhdl "${DIRECTORY}/dhdl.xvg" \
    -v
```

Los TPR deben haberse generado previamente. Los recursos, GPU, partición y tiempo dependen del clúster.

Registre:

```text
estado | coul-lambda | vdw-lambda | semilla | duración | estado del trabajo
```

### 15. Continuar una ventana

```bash
gmx mdrun \
    -deffnm 03_fep/lambda_07/production \
    -cpi 03_fep/lambda_07/production.cpt \
    -append \
    -dhdl 03_fep/lambda_07/dhdl.xvg \
    -v
```

No regenere el TPR si solo continúa el mismo Hamiltoniano. Si cambia MDP, duración o λ, documente el nuevo segmento.

### 16. Análisis con BAR

Los directorios llevan ceros iniciales para que el glob preserve el orden:

```bash
mkdir -p 04_analisis

gmx bar \
    -b 500 \
    -f 03_fep/lambda_*/dhdl.xvg \
    -o 04_analisis/bar_deltaG.xvg \
    -oi 04_analisis/bar_integral.xvg \
    -oh 04_analisis/bar_histograms.xvg \
    -prec 3
```

**-b 500** descarta 500 ps de cada archivo. Determine el descarte mediante la relajación real de las ventanas, no por copia del ejemplo.

Con la convención usada:

$$
\Delta G_{\mathrm{solv}}
=
-\Delta G_{\mathrm{BAR}}
$$

### 17. Diagnóstico de BAR

Revise por cada par:

- $\Delta G$ parcial;
- incertidumbre;
- entropías relativas **s_A** y **s_B**;
- desviación esperada por muestra;
- histogramas;
- consistencia entre ventanas.

Las entropías relativas son indicadores de distancia entre distribuciones; valores grandes sugieren peor superposición.

El error de BAR no incluye automáticamente error del campo de fuerza, modelo de agua, especie química, estado estándar, tamaño finito o muestreo conformacional ausente. Precisión estadística no implica exactitud química.

### 18. Convergencia temporal y réplicas

Repita BAR con distintos descartes:

```bash
gmx bar -b 250  -f 03_fep/lambda_*/dhdl.xvg
gmx bar -b 500  -f 03_fep/lambda_*/dhdl.xvg
gmx bar -b 1000 -f 03_fep/lambda_*/dhdl.xvg
```

Una estimación defendible debe mostrar:

- ausencia de deriva;
- superposición bilateral;
- contribuciones sin saltos dominantes;
- compatibilidad entre mitades temporales;
- compatibilidad entre réplicas;
- menor incertidumbre al aumentar datos efectivos.

Las filas consecutivas están correlacionadas. El número de filas no es el número de muestras independientes.

Use semillas distintas y vuelva a equilibrar las ventanas para cada réplica. Trayectorias con el mismo checkpoint y velocidades no son independientes.

### 19. Refinar la grilla

Agregue estados entre $\lambda_i$ y $\lambda_{i+1}$ si los histogramas apenas se superponen, el error parcial domina, **s_A/s_B** aumentan abruptamente o el solvente entra y sale de forma discontinua.

No agregue ventanas donde el solapamiento ya es alto si el cuello de botella está en otra región. Redistribuya el cálculo.

### 20. Unidades de energía

GROMACS informa energías molares en kJ·mol⁻¹.

$$
1\ \mathrm{kcal\,mol^{-1}}
=
4.184\ \mathrm{kJ\,mol^{-1}}
$$

$$
1\ \mathrm{eV\ por\ molécula}
=
96.485332\ \mathrm{kJ\,mol^{-1}}
$$

$$
1\ E_h
=
2625.50\ \mathrm{kJ\,mol^{-1}}
$$

Por tanto:

$$
-0.151256\ \mathrm{eV}
\times
96.485332
=
-14.59399\ \mathrm{kJ\,mol^{-1}}
$$

El valor anterior, −14.5934028 kJ·mol⁻¹, difiere ligeramente por el factor de conversión empleado. Esa diferencia es despreciable frente a la incertidumbre física, pero debe usarse una constante consistente.

### 21. Energía térmica

A 298.15 K:

$$
RT=
(8.314462618\times10^{-3})
(298.15)
=
2.47896\ \mathrm{kJ\,mol^{-1}}
$$

Una unidad $k_\mathrm{B}T$ por partícula equivale numéricamente a una unidad $RT$ por mol.

$$
-14.594\ \mathrm{kJ\,mol^{-1}}
\approx
-5.89\ k_\mathrm{B}T
$$

No multiplique por el número de Avogadro una energía ya expresada por mol.

### 22. Tiempo y λ

$$
1000\ \mathrm{ps}=1\ \mathrm{ns}
$$

Con:

```ini
dt     = 0.002
nsteps = 2500000
```

$$
t=0.002\ \mathrm{ps}\times2500000
=5000\ \mathrm{ps}
=5\ \mathrm{ns}
$$

λ es adimensional; **init-lambda-state** es un índice entero.

### 23. Estados estándar

Una referencia experimental puede usar gas ideal a 1 atm o 1 bar, solución a 1 mol·L⁻¹, dilución infinita o una convención de ley de Henry.

La conversión gas–solución contiene:

$$
\Delta G^\circ_{\mathrm{corr}}
=
RT\ln
\left(
\frac{C^\circ RT}{p^\circ}
\right)
$$

A 298.15 K, la magnitud entre 1 atm y 1 mol·L⁻¹ es aproximadamente 7.9 kJ·mol⁻¹. El signo depende de la dirección y de la definición original.

No aplique esta corrección sin identificar las convenciones experimental y computacional.

### 24. Tamaño finito y carga

Para solutos con carga neta, PME y una caja periódica con fondo neutralizante introducen correcciones dependientes de la carga, la caja, la constante dieléctrica y la convención electrostática.

El formaldehído aquí es neutro y no requiere la corrección principal de carga neta. Persisten posibles efectos de tamaño y dipolo.

No compare transformaciones que cambian la carga neta sin un protocolo específico.

### 25. Limitación química del formaldehído

En agua:

$$
\mathrm{H_2CO + H_2O
\rightleftharpoons
CH_2(OH)_2}
$$

El producto es metanodiol o metilenglicol. Según la concentración también pueden existir oligómeros.

Un campo de fuerza clásico de topología fija no rompe el enlace C=O, no forma enlaces C–O, no transfiere protones y no convierte formaldehído en metanodiol.

Este cálculo estima:

$$
\mathrm{H_2CO(g)}
\rightarrow
\mathrm{H_2CO(aq)}
$$

para formaldehído mantenido artificialmente como tal. No estima directamente:

$$
\mathrm{H_2CO(g)+H_2O(l)}
\rightarrow
\mathrm{CH_2(OH)_2(aq)}
$$

ni la solubilidad total de formaldehído.

### 26. Ciclo químico correcto

El proceso efectivo puede descomponerse:

$$
\Delta G^\circ_{\mathrm{global}}
=
\Delta G^\circ_{\mathrm{solv}}(\mathrm{H_2CO})
+
\Delta G^\circ_{\mathrm{hidratación,aq}}
$$

Alternativas:

- calcular solo solvatación física de $\mathrm{H_2CO}$ y declararlo;
- parametrizar metanodiol como especie diferente;
- calcular la hidratación covalente mediante QM/MM o estructura electrónica;
- combinar solvatación y reacción en un ciclo termodinámico;
- usar etanol o metanol como ejemplo pedagógico no reactivo.

El tutorial oficial de GROMACS usa etanol, una elección más clara para enseñar el procedimiento general. El formaldehído resulta útil para mostrar que la especie química debe definirse antes del cálculo.

### 27. Comparación con el valor atribuido a NIST

El texto anterior cita:

$$
-0.151256\ \mathrm{eV}
=
-14.59399\ \mathrm{kJ\,mol^{-1}}
$$

Antes de compararlo con BAR deben coincidir:

- especie;
- sentido solvatación/desolvatación;
- temperatura;
- estado estándar;
- solvente;
- definición de dilución;
- inclusión de hidratación covalente;
- convención de la base.

La página general del proyecto NIST no reemplaza el registro específico con sus metadatos. Un acuerdo numérico accidental puede ocultar signos opuestos o procesos químicos distintos.

### 28. Interpretación de resultados

Un resultado como:

$$
-22.94\pm1.04\ \mathrm{kJ\,mol^{-1}}
$$

solo es interpretable si se informa:

- extremos de λ;
- signo aplicado a BAR;
- tiempo descartado;
- duración por ventana;
- grilla;
- réplicas;
- método de incertidumbre;
- campo de fuerza;
- agua;
- temperatura;
- correcciones;
- especie química.

El ± suele representar incertidumbre estadística condicionada al muestreo. No incluye errores de parametrización o química ausente.

### 29. Controles adicionales

```bash
gmx trjconv \
    -s 03_fep/lambda_00/production.tpr \
    -f 03_fep/lambda_00/production.xtc \
    -o 04_analisis/lambda_00_snapshot.gro \
    -dump 5000

gmx trjconv \
    -s 03_fep/lambda_18/production.tpr \
    -f 03_fep/lambda_18/production.xtc \
    -o 04_analisis/lambda_18_snapshot.gro \
    -dump 5000
```

Controle temperatura, volumen, errores LINCS, integridad del soluto, respuesta del solvente, ausencia de singularidades, producción de archivos de diferencias de energía y estado λ informado en el log.

En el extremo desacoplado el solvente puede ocupar el espacio del soluto. Es un comportamiento esperado con soft-core.

### 30. Errores frecuentes

- No definir los estados extremos.
- Confundir solvatación con desolvatación.
- Usar **vdwq** en vez de la sintaxis actual **vdw-q**.
- Eliminar Lennard-Jones antes que las cargas.
- Usar cinco λ uniformes y asumir convergencia.
- Desacoplar Coulomb y Lennard-Jones simultáneamente sin validación.
- No equilibrar cada ventana.
- Copiar arbitrariamente el descarte **-b**.
- Reutilizar un directorio para varias ventanas.
- Usar archivos sin orden definido.
- Tratar muestras correlacionadas como independientes.
- Informar solamente el error de BAR.
- Confundir eV por molécula con kJ·mol⁻¹.
- Multiplicar otra vez por $N_A$.
- Ignorar el estado estándar.
- Perturbar varias copias del mismo **moleculetype**.
- Cambiar carga neta sin correcciones.
- Comparar formaldehído molecular con formaldehído total acuoso.
- Aceptar una minimización que no alcanzó su criterio.
- Usar **-maxwarn** para producir el TPR.

### 31. Reproducibilidad mínima

Informe:

- versión exacta de GROMACS;
- origen y versión de parámetros;
- modelo de agua;
- topología molecular;
- caja y número de aguas;
- temperatura y presión;
- integrador y paso;
- lista completa de λ;
- parámetros soft-core;
- equilibración y producción;
- frecuencia de diferencias de energía;
- método de análisis y descarte;
- réplicas y semillas;
- correcciones;
- signo de $\Delta G$;
- especie química calculada.

### 32. Criterios de aceptación

El cálculo es técnicamente defendible cuando:

- los extremos están definidos;
- la topología es químicamente correcta;
- todas las ventanas terminaron;
- existe superposición entre vecinos;
- las contribuciones parciales son estables;
- el resultado converge temporalmente;
- las réplicas son compatibles;
- unidades y signo son inequívocos;
- se aplicaron las correcciones necesarias;
- el dato experimental usa una convención comparable;
- la especie simulada coincide con la experimental.

Para formaldehído acuoso en equilibrio, el último criterio no se cumple si solo se modela $\mathrm{H_2CO}$ mediante una topología clásica fija.

### Fuentes

1. [Tutorial oficial de energía libre de solvatación de GROMACS](https://tutorials.gromacs.org/docs/free-energy-of-solvation.html)
2. [Opciones MDP de energía libre en GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/mdp-options.html)
3. [Referencia de gmx bar](https://manual.gromacs.org/current/onlinehelp/gmx-bar.html)
4. [Perturbation Free-Energy Toolkit](https://pmc.ncbi.nlm.nih.gov/articles/PMC8479811/)
5. [Guidelines for the analysis of free energy calculations](https://link.springer.com/article/10.1007/s10822-015-9840-9)
6. [Python tool for relative free-energy calculations in GROMACS](https://link.springer.com/article/10.1007/s10822-015-9873-0)
7. [Tutorial histórico de FEP con GROMACS](http://www.mdtutorials.com/gmx/2018/free_energy/index.html)
8. [Revisión adicional proporcionada](https://pmc.ncbi.nlm.nih.gov/articles/PMC12163693/)
9. [Proyecto NIST sobre energías libres de solvatación](https://www.nist.gov/programs-projects/solvation-free-energies)
