## Dinámica de una proteína en agua

### Caso: proteína monomérica

Este sistema contiene una proteína formada por aminoácidos estándar, agua e iones. Es útil para estudiar estabilidad conformacional, flexibilidad, compactación, estructura secundaria, exposición al solvente y movimientos colectivos. También sirve para relajar una estructura modelada, pero una dinámica molecular breve no corrige automáticamente errores de secuencia, plegamiento, protonación o ensamblaje.

El flujo general es:

```text
estructura inicial
    ↓
revisión y preparación
    ↓
topología con pdb2gmx
    ↓
caja periódica
    ↓
solvatación e iones
    ↓
minimización de energía
    ↓
equilibración NVT
    ↓
equilibración NPT
    ↓
dinámica de producción
    ↓
corrección de PBC y análisis
```

### 1. Definir qué estructura se simulará

Antes de ejecutar GROMACS, determine si la estructura representa realmente un monómero biológico. Una cadena aislada de un PDB puede ser:

- una proteína monomérica funcional;
- una subunidad extraída de un oligómero;
- una construcción truncada;
- una estructura con mutaciones o etiquetas;
- un modelo incompleto;
- una cadena estabilizada por contactos cristalográficos.

Simular una única cadena de una proteína oligomérica puede producir exposición artificial de superficies hidrofóbicas, pérdida de estructura o movimientos que no ocurren en la unidad biológica.

Revise como mínimo:

- residuos y segmentos faltantes;
- átomos con ocupación alternativa;
- residuos no estándar;
- terminales reales de la construcción;
- enlaces disulfuro;
- histidinas y otros grupos titulables;
- metales, cofactores, ligandos y aguas estructurales;
- mutaciones y modificaciones postraduccionales;
- orientación y entorno experimental de la proteína.

Conserve el archivo original y trabaje sobre una copia:

```bash
mkdir -p 00_entrada 01_preparacion 02_em 03_nvt 04_npt 05_md 06_analisis
cp protein.pdb 00_entrada/protein_original.pdb
```

### 2. Campo de fuerza y modelo de agua

No existe un campo de fuerza universalmente superior para todas las proteínas y propiedades. La elección debe justificarse por:

- tipo de proteína y entorno;
- propiedad que se medirá;
- calidad de la parametrización disponible;
- compatibilidad con cofactores o ligandos;
- antecedentes metodológicos comparables;
- modelo de agua utilizado durante el desarrollo o la validación del campo de fuerza.

No seleccione OPLS-AA, CHARMM, AMBER o GROMOS solo por el número que ocupa en el menú de **pdb2gmx**. Los números y campos instalados pueden cambiar entre equipos.

Liste las opciones disponibles:

```bash
gmx pdb2gmx -h
```

También puede iniciar **pdb2gmx** sin **-ff** para seleccionar el campo de fuerza interactivamente.

### 3. Limpieza de la estructura

Elimine únicamente componentes cuya ausencia esté justificada. Las aguas cristalográficas alejadas suelen descartarse, pero una molécula de agua conservada en un sitio catalítico o en una red de puentes de hidrógeno puede ser relevante.

Las conformaciones alternativas deben resolverse antes de **pdb2gmx**. No deben quedar dos posiciones incompatibles para el mismo átomo.

Verificación inicial:

```bash
grep '^ATOM\|^HETATM\|^TER\|^SSBOND' 00_entrada/protein_original.pdb \
    > 01_preparacion/structure_records.txt
```

Este comando solo extrae registros para inspección; no genera por sí mismo un PDB listo para simular.

### 4. Generación de la topología

Ejemplo interactivo:

```bash
cd 01_preparacion

gmx pdb2gmx \
    -f ../00_entrada/protein_original.pdb \
    -o protein_processed.gro \
    -p topol.top \
    -i posre_protein.itp
```

Ejemplo con campo de fuerza y agua indicados explícitamente:

```bash
gmx pdb2gmx \
    -f ../00_entrada/protein_original.pdb \
    -o protein_processed.gro \
    -p topol.top \
    -i posre_protein.itp \
    -ff charmm36-jul2022 \
    -water tip3p
```

El identificador **charmm36-jul2022** es un ejemplo. Debe coincidir con un campo instalado y con el protocolo elegido.

Opciones útiles:

| Opción        | Uso                                                                          |
| ------------- | ---------------------------------------------------------------------------- |
| **-ff**       | Selecciona el campo de fuerza.                                               |
| **-water**    | Selecciona el modelo de agua.                                                |
| **-ter**      | Permite elegir estados de los terminales.                                    |
| **-his**      | Permite seleccionar estados de protonación de histidinas.                    |
| **-ss**       | Permite elegir interactivamente enlaces disulfuro.                           |
| **-ignh**     | Ignora hidrógenos de entrada y los reconstruye. Debe usarse deliberadamente. |
| **-chainsep** | Controla cuándo separar cadenas en tipos moleculares.                        |
| **-merge**    | Controla la fusión de cadenas en un único tipo molecular.                    |

Consulte las opciones exactas de la instalación:

```bash
gmx pdb2gmx -h
```

**pdb2gmx** no asigna estados de protonación mediante una simulación de pH constante. Aplica plantillas y decisiones del usuario. Para histidina deben evaluarse las formas protonadas en Nδ, Nε o en ambos nitrógenos según su entorno.

Revise cuidadosamente la salida. Debe comprobar:

- residuos reconocidos;
- terminales asignados;
- carga total;
- enlaces disulfuro;
- átomos añadidos o eliminados;
- advertencias;
- nombre del tipo molecular generado.

Compruebe el archivo:

```bash
gmx check -f protein_processed.gro
```

### 5. Contenido esperado de la topología

Un **topol.top** típico incluye:

```ini
; Campo de fuerza
#include "charmm36-jul2022.ff/forcefield.itp"

; Topología de la proteína
#include "topol_Protein.itp"

; Agua
#include "charmm36-jul2022.ff/tip3p.itp"

; Iones
#include "charmm36-jul2022.ff/ions.itp"

[ system ]
Proteína monomérica en agua

[ molecules ]
Protein    1
```

La estructura exacta depende de la salida de **pdb2gmx**. No reescriba manualmente nombres sin cambiar también la definición `[ moleculetype ]` correspondiente.

El archivo de restricciones suele estar incluido dentro del ITP de la proteína:

```ini
#ifdef POSRES
#include "posre_protein.itp"
#endif
```

La inclusión debe permanecer dentro del ámbito del tipo molecular al que pertenecen sus índices.

### 6. Caja periódica

Para una proteína soluble aproximadamente globular:

```bash
gmx editconf \
    -f protein_processed.gro \
    -o protein_box.gro \
    -c \
    -d 1.0 \
    -bt dodecahedron
```

**-d 1.0** establece una distancia mínima de 1.0 nm, equivalente a 10 Å, entre el soluto y la caja. Debe ser compatible con los radios de corte y con el tamaño y movimiento esperados de la proteína.

Una caja dodecaédrica suele contener menos agua que una cúbica. Una caja cúbica puede ser más simple de visualizar, pero normalmente aumenta el número de átomos:

```bash
gmx editconf \
    -f protein_processed.gro \
    -o protein_box_cubic.gro \
    -c \
    -d 1.0 \
    -bt cubic
```

No use este protocolo de caja acuosa para una proteína transmembrana: necesita una bicapa, orientación y composición lipídica apropiadas.

### 7. Solvatación

```bash
gmx solvate     -cp protein_box.gro     -cs spc216.gro     -o protein_solv.gro     -p topol.top
```

**gmx solvate** actualiza la cantidad de solvente en `[ molecules ]`. Revise el final de **topol.top** y confirme que el agua utilizada es compatible con la topología elegida.

Compruebe que la proteína no cruza de forma problemática la caja y que no existen cavidades o solapamientos extraños mediante una inspección visual.

### 8. Neutralización y fuerza iónica

Archivo mínimo **ions.mdp**:

```ini
integrator      = steep
nsteps          = 0
emtol           = 1000.0

cutoff-scheme   = Verlet
coulombtype     = PME
rcoulomb        = 1.0
rvdw            = 1.0
pbc             = xyz
```

Genere el TPR:

```bash
gmx grompp     -f ions.mdp     -c protein_solv.gro     -p topol.top     -o ions.tpr
```

Neutralización con NaCl y concentración nominal de 0.15 mol L⁻¹:

```bash
gmx genion \
    -s ions.tpr \
    -o protein_solv_ions.gro \
    -p topol.top \
    -pname NA \
    -nname CL \
    -neutral \
    -conc 0.15
```

Seleccione el grupo de agua, normalmente **SOL**. No memorice su número: depende del sistema.

La opción **-neutral** incorpora los contraiones necesarios para que la carga total sea cero. **-conc 0.15** agrega sal hasta aproximar la concentración solicitada. Debido al volumen finito de la caja, la concentración efectiva puede diferir ligeramente.

Si el experimento requiere otra sal, deben existir parámetros compatibles para cada especie. Un ion metálico coordinado en un sitio activo no debe tratarse como un contraion difusible común.

### 9. Validación antes de minimizar

Genere una topología expandida:

```bash
gmx grompp \
    -f em.mdp \
    -c protein_solv_ions.gro \
    -p topol.top \
    -o em_test.tpr \
    -pp processed.top
```

**processed.top** permite revisar las inclusiones y macros después del preprocesamiento.

No continúe si existen:

- diferencias entre el número de átomos y coordenadas;
- carga total inesperada;
- residuos sin parametrizar;
- parámetros faltantes;
- nombres moleculares inconsistentes;
- advertencias no comprendidas.

No use **-maxwarn** para forzar la creación del TPR.

### 10. Minimización de energía

Archivo **em.mdp**:

```ini
title            = Minimización de proteína en agua
integrator       = steep
nsteps           = 50000
emtol            = 1000.0
emstep           = 0.01

cutoff-scheme    = Verlet
nstlist          = 20
rlist            = 1.0
coulombtype      = PME
rcoulomb         = 1.0
vdwtype          = Cut-off
rvdw             = 1.0
pbc              = xyz
```

Ejecución:

```bash
mkdir -p ../02_em
cd ../02_em

gmx grompp \
    -f ../01_preparacion/em.mdp \
    -c ../01_preparacion/protein_solv_ions.gro \
    -p ../01_preparacion/topol.top \
    -o em.tpr

gmx mdrun -deffnm em -v
```

Extraiga la energía potencial:

```bash
(echo Potential; echo 0) |
gmx energy     -f em.edr     -o ../06_analisis/em_potential.xvg
```

La minimización elimina contactos desfavorables; no equilibra temperatura, presión ni distribución conformacional. Revise energía potencial, fuerza máxima, átomo asociado a esa fuerza y posibles valores NaN.

### 11. Equilibración NVT

NVT estabiliza la temperatura con volumen fijo. Use restricciones posicionales inicialmente si necesita evitar una relajación brusca del soluto mientras se reorganizan agua e iones.

Parámetros principales:

```ini
title         = Equilibración NVT
define        = -DPOSRES

integrator    = md
dt            = 0.002
nsteps        = 50000
continuation  = no

gen-vel       = yes
gen-temp      = 300
gen-seed      = -1

constraints   = h-bonds

tcoupl        = V-rescale
tc-grps       = Protein Water_and_ions
tau-t         = 1.0 1.0
ref-t         = 300 300

pcoupl        = no
pbc           = xyz
```

Con **dt = 0.002 ps** y **nsteps = 50000**, la duración es 100 ps. El paso de 0.002 ps equivale a 2 fs.

```bash
mkdir -p ../03_nvt
cd ../03_nvt

gmx grompp \
    -f ../01_preparacion/nvt.mdp \
    -c ../02_em/em.gro \
    -r ../02_em/em.gro \
    -p ../01_preparacion/topol.top \
    -o nvt.tpr

gmx mdrun -deffnm nvt -v
```

Analice la temperatura:

```bash
(echo Temperature; echo 0) |
gmx energy     -f nvt.edr     -o ../06_analisis/nvt_temperature.xvg
```

### 12. Equilibración NPT

NPT ajusta presión, densidad y volumen. Continúe desde el checkpoint de NVT y no regenere velocidades:

```ini
title            = Equilibración NPT
define           = -DPOSRES

integrator       = md
dt               = 0.002
nsteps           = 250000
continuation     = yes
gen-vel          = no

constraints      = h-bonds

tcoupl           = V-rescale
tc-grps          = Protein Water_and_ions
tau-t            = 1.0 1.0
ref-t            = 300 300

pcoupl           = C-rescale
pcoupltype       = isotropic
tau-p            = 5.0
ref-p            = 1.0
compressibility  = 4.5e-5

pbc              = xyz
```

Aquí se simulan 500 ps. **ref-p** se expresa en bar y la compresibilidad en bar⁻¹. El valor 4.5 × 10⁻⁵ bar⁻¹ es habitual para agua líquida cerca de condiciones ambientales.

```bash
mkdir -p ../04_npt
cd ../04_npt

gmx grompp \
    -f ../01_preparacion/npt.mdp \
    -c ../03_nvt/nvt.gro \
    -r ../03_nvt/nvt.gro \
    -t ../03_nvt/nvt.cpt \
    -p ../01_preparacion/topol.top \
    -o npt.tpr

gmx mdrun -deffnm npt -v
```

Analice temperatura, presión, densidad y volumen:

```bash
(echo Temperature; echo Pressure; echo Density; echo Volume; echo 0) |
gmx energy     -f npt.edr     -o ../06_analisis/npt_thermodynamics.xvg
```

La presión instantánea fluctúa intensamente. Evalúe promedios por bloques, densidad y deriva temporal.

### 13. Dinámica de producción

Retire **define = -DPOSRES** salvo que mantener restricciones forme parte explícita del experimento.

Parámetros principales:

```ini
title            = Producción de proteína en agua

integrator       = md
dt               = 0.002
nsteps           = 50000000
continuation     = yes
gen-vel          = no

constraints      = h-bonds

tcoupl           = V-rescale
tc-grps          = Protein Water_and_ions
tau-t            = 1.0 1.0
ref-t            = 300 300

pcoupl           = Parrinello-Rahman
pcoupltype       = isotropic
tau-p            = 5.0
ref-p            = 1.0
compressibility  = 4.5e-5

pbc              = xyz
```

Con 50000000 pasos de 0.002 ps se simulan 100 ns. Agregue los parámetros de PME, Verlet y control de salida validados en el tutorial principal; no mezcle MDP de campos de fuerza diferentes sin revisar cortes y modificadores.

```bash
mkdir -p ../05_md
cd ../05_md

gmx grompp \
    -f ../01_preparacion/md.mdp \
    -c ../04_npt/npt.gro \
    -t ../04_npt/npt.cpt \
    -p ../01_preparacion/topol.top \
    -o md.tpr

gmx mdrun -deffnm md -v
```

Compruebe en el registro:

- ausencia de errores LINCS;
- temperatura, presión y densidad estables;
- rendimiento y uso esperado de CPU/GPU;
- frecuencia y tamaño de los archivos de salida;
- escritura periódica del checkpoint.

### 14. Controles estructurales mínimos

Corrija PBC antes de analizar:

```bash
echo Protein |
gmx trjconv \
    -s md.tpr \
    -f md.xtc \
    -o md_protein_center.gro \
    -center \
    -pbc mol \
    -ur compact
```

Para conservar una trayectoria XTC:

```bash
(echo Protein; echo Protein) |
gmx trjconv \
    -s md.tpr \
    -f md.xtc \
    -o md_protein_center.xtc \
    -center \
    -pbc mol \
    -ur compact
```

Ajuste rotación y traslación:

```bash
(echo Backbone; echo Protein) |
gmx trjconv     -s md.tpr     -f md_protein_center.xtc     -o md_protein_fit.xtc     -fit rot+trans
```

RMSD del backbone:

```bash
(echo Backbone; echo Backbone) |
gmx rms     -s md.tpr     -f md_protein_fit.xtc     -o ../06_analisis/rmsd_backbone.xvg     -tu ns
```

RMSF por residuo:

```bash
echo C-alpha |
gmx rmsf     -s md.tpr     -f md_protein_fit.xtc     -o ../06_analisis/rmsf_calpha.xvg     -res
```

Radio de giro:

```bash
gmx gyrate \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -sel 'group "Protein"' \
    -o ../06_analisis/gyrate_protein.xvg
```

Estructura secundaria:

```bash
gmx dssp \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -sel 'group "Protein"' \
    -o ../06_analisis/secondary_structure.dat
```

La disponibilidad y las opciones de **gmx dssp** deben comprobarse con:

```bash
gmx dssp -h
```

Una meseta de RMSD no demuestra convergencia. Compare bloques temporales, réplicas independientes y observables complementarios.

### 15. Diseñar el análisis antes de calcular observables

El análisis debe responder una pregunta física. Acumular RMSD, RMSF, SASA, puentes de hidrógeno y PCA sin definir qué hipótesis evalúa cada uno produce figuras, pero no necesariamente evidencia.

Antes de analizar, defina:

- qué intervalo se considera producción equilibrada;
- qué átomos representan mejor el fenómeno: Cα, backbone, todos los átomos pesados, sitio activo o dominios;
- qué estructura se usará como referencia;
- qué observable se espera que cambie y en qué dirección;
- cuántas réplicas independientes se compararán;
- cómo se estimará la incertidumbre.

El descarte inicial no debe elegirse porque “mejora” una curva. Examine temperatura, densidad, energía, RMSD y los observables relevantes por bloques. Si una transición lenta ocurre una sola vez, eliminar la parte anterior puede borrar un estado real en lugar de retirar equilibración.

Divida la producción en bloques temporales comparables. Por ejemplo, para una trayectoria de 100 ns puede contrastar 0–25, 25–50, 50–75 y 75–100 ns, además de repetir los análisis en réplicas independientes. La estabilidad del promedio entre bloques es más informativa que una línea aparentemente plana.

### 16. Exposición al solvente, enlaces y geometría funcional

El área accesible al solvente, SASA, depende de la superficie molecular y de una sonda que representa aproximadamente una molécula de agua. No equivale al área geométrica total ni mide por sí sola desplegamiento.

```bash
gmx sasa \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -surface 'group "Protein"' \
    -output 'group "Protein"' \
    -o ../06_analisis/sasa_total.xvg \
    -or ../06_analisis/sasa_residue.xvg
```

Compruebe la sintaxis de la versión instalada con **gmx sasa -h**. Para interpretar cambios conviene separar, cuando sea pertinente, superficie hidrofóbica e hidrofílica mediante grupos definidos y documentados.

Los puentes de hidrógeno intraproteicos pueden calcularse con:

```bash
gmx hbond \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -r 'group "Protein"' \
    -t 'group "Protein"' \
    -num ../06_analisis/hbonds_intraprotein.xvg
```

La interfaz de **gmx hbond** cambió entre versiones. Revise **gmx hbond -h** y registre los cortes geométricos utilizados. Un mayor número de puentes no significa automáticamente una estructura más estable: importa qué interacciones aparecen, su ocupación y si conectan regiones funcionales.

Para una distancia entre dominios, residuos catalíticos o extremos de una compuerta, cree grupos específicos en **index.ndx** y use:

```bash
gmx distance \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -n index.ndx \
    -select 'com of group "Domain_A" plus com of group "Domain_B"' \
    -oall ../06_analisis/domain_distance.xvg
```

Una distancia entre centros de masa puede ocultar rotaciones. Cuando la geometría sea funcional, combine distancias, ángulos y contactos definidos a partir de residuos concretos.

### 17. Ángulos diedros, contactos y estructura secundaria

La estabilidad del plegamiento no queda descrita por un RMSD global. Los cambios locales pueden examinarse mediante ángulos φ/ψ, matrices de distancia y evolución de la estructura secundaria.

Diagrama de Ramachandran muestreado durante la trayectoria:

```bash
gmx rama \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -o ../06_analisis/ramachandran.xvg
```

Matriz media de distancias entre residuos:

```bash
echo Protein | \
gmx mdmat \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -mean ../06_analisis/mean_distance_map.xpm \
    -frames ../06_analisis/distance_map_frames.xpm
```

La opción **-frames** puede generar archivos grandes; úsela solo cuando se necesite evolución temporal. Para contactos funcionales es preferible definir pares de residuos y calcular ocupaciones con un corte explícito, en lugar de interpretar visualmente toda la matriz.

La estructura secundaria ya puede obtenerse con **gmx dssp**. Resuma la ocupación por residuo y por bloque, no solo una representación coloreada. Una hélice presente el 60 % del tiempo no es equivalente a una transición irreversible de hélice a coil.

### 18. Fundamento de PCA o dinámica esencial

El análisis de componentes principales, PCA, intenta separar movimientos colectivos de gran amplitud de fluctuaciones locales. Después de eliminar traslación y rotación, se construye la matriz de covarianza de las coordenadas:

$$
C_{ij}=\left\langle
\left(x_i-\langle x_i\rangle\right)
\left(x_j-\langle x_j\rangle\right)
\right\rangle
$$

Su diagonalización produce autovectores $\mathbf{v}_k$ y autovalores $\lambda_k$:

$$
\mathbf{C}\mathbf{v}_k=\lambda_k\mathbf{v}_k
$$

- $\mathbf{v}_k$ define una dirección colectiva en el espacio de coordenadas;
- $\lambda_k$ es la varianza a lo largo de esa dirección;
- los componentes se ordenan de mayor a menor varianza;
- la fracción de fluctuación explicada por el componente $k$ es:

$$
f_k=\frac{\lambda_k}{\sum_j\lambda_j}
$$

La proyección del fotograma $t$ sobre el componente $k$ es:

$$
p_k(t)=\mathbf{v}_k^{\mathrm{T}}
\left[\mathbf{x}(t)-\langle\mathbf{x}\rangle\right]
$$

“Principal” significa mayor varianza, no mayor importancia biológica. PC1 puede representar una relajación inicial, difusión no convergida o un movimiento inducido por una mala preparación. La interpretación funcional requiere localizar qué dominios se mueven, comprobar recurrencia y contrastar réplicas o datos experimentales.

PCA cartesiano depende de la selección atómica y del ajuste. Para dinámica global suele ser razonable usar backbone o Cα. Incluir cadenas laterales e hidrógenos aumenta dimensionalidad y puede hacer que movimientos locales oculten los modos colectivos.

### 19. PCA con gmx covar y gmx anaeig

Use una trayectoria con la proteína entera y sin saltos periódicos. No es necesario ajustar previamente la trayectoria: **gmx covar** realiza un ajuste de mínimos cuadrados usando el primer grupo solicitado. Así se evita ajustar dos veces con criterios diferentes.

Construcción y diagonalización de la matriz de covarianza:

```bash
gmx covar \
    -s md.tpr \
    -f md_protein_center.xtc \
    -o ../06_analisis/pca_eigenval.xvg \
    -v ../06_analisis/pca_eigenvec.trr \
    -av ../06_analisis/pca_average.pdb \
    -l ../06_analisis/pca_covar.log
```

Seleccione **Backbone** para el ajuste y **Backbone** para la matriz. Si se elige otro grupo, debe conservarse exactamente la misma selección en las proyecciones posteriores.

La covarianza cartesiana estándar no está ponderada por masa salvo que se solicite la opción correspondiente. Para Cα la diferencia es irrelevante porque todos los átomos seleccionados son carbonos; para selecciones heterogéneas debe declararse si se utilizó ponderación por masa.

Proyección sobre PC1 y PC2:

```bash
gmx anaeig \
    -v ../06_analisis/pca_eigenvec.trr \
    -s md.tpr \
    -f md_protein_center.xtc \
    -first 1 \
    -last 2 \
    -2d ../06_analisis/pca_pc1_pc2.xvg
```

Evolución temporal de PC1:

```bash
gmx anaeig \
    -v ../06_analisis/pca_eigenvec.trr \
    -s md.tpr \
    -f md_protein_center.xtc \
    -first 1 \
    -last 1 \
    -proj ../06_analisis/pca_pc1_time.xvg
```

Estructuras extremas interpoladas a lo largo de PC1:

```bash
gmx anaeig \
    -v ../06_analisis/pca_eigenvec.trr \
    -s md.tpr \
    -f md_protein_center.xtc \
    -first 1 \
    -last 1 \
    -extr ../06_analisis/pca_pc1_extremes.pdb \
    -nframes 30
```

Las estructuras intermedias generadas con **-extr** son una interpolación para visualizar el vector. No constituyen una trayectoria física ni prueban que la proteína recorra suavemente ese camino.

### 20. Interpretación y convergencia de PCA

Examine en conjunto:

1. espectro de autovalores;
2. fracción acumulada de varianza;
3. proyecciones de cada componente en función del tiempo;
4. mapa PC1–PC2 coloreado por tiempo o réplica;
5. movimiento estructural de los primeros componentes;
6. estabilidad de los autovectores entre bloques y réplicas.

Un mapa PC1–PC2 con varias nubes puede indicar estados conformacionales, pero también muestreo insuficiente. La conexión temporal entre puntos y la revisita de cada región son esenciales. Una trayectoria que avanza una sola vez de izquierda a derecha no demuestra equilibrio entre dos estados.

El contenido coseno ayuda a detectar modos parecidos a una difusión aleatoria finita:

```bash
gmx analyze \
    -f ../06_analisis/pca_pc1_time.xvg \
    -cc ../06_analisis/pca_pc1_cosine.xvg
```

Un contenido coseno alto sugiere muestreo insuficiente del modo, pero no demuestra que la dirección carezca de significado físico. Compare además PCA calculados por separado sobre mitades de la trayectoria y sobre réplicas. El solapamiento entre subespacios es más exigente que comparar solamente autovalores.

Para comparar dos sistemas —por ejemplo proteína libre y complejo— no calcule dos PCA independientes y llame “PC1” al mismo movimiento. Los ejes son específicos de cada conjunto. Construya una base común con trayectorias concatenadas o proyecte ambas trayectorias sobre los autovectores obtenidos de un único conjunto de referencia. Los sistemas deben contener los mismos átomos, en el mismo orden, y usar el mismo ajuste.

### 21. Agrupamiento y paisaje conformacional

El agrupamiento busca estructuras representativas; PCA reduce dimensionalidad. No son equivalentes. Un análisis puede agrupar por RMSD, contactos o distancias funcionales, según la pregunta.

Ejemplo de agrupamiento por RMSD del backbone:

```bash
echo Backbone | \
gmx cluster \
    -s md.tpr \
    -f md_protein_fit.xtc \
    -method gromos \
    -cutoff 0.20 \
    -o ../06_analisis/cluster_rmsd.xpm \
    -g ../06_analisis/cluster.log \
    -sz ../06_analisis/cluster_sizes.xvg \
    -cl ../06_analisis/cluster_representatives.pdb
```

El corte de 0.20 nm es solo un punto de partida. Debe evaluarse su sensibilidad: un corte pequeño fragmenta el conjunto y uno grande mezcla estados distintos. Informe selección, métrica, método y corte.

Un paisaje de energía libre aparente en dos coordenadas $q_1,q_2$ se obtiene de la probabilidad muestreada:

$$
F(q_1,q_2)=-k_{\mathrm B}T\ln P(q_1,q_2)+C
$$

Con PC1 y PC2 puede estimarse mediante:

```bash
gmx sham \
    -f ../06_analisis/pca_pc1_pc2.xvg \
    -ls ../06_analisis/pca_free_energy.xpm
```

El resultado depende del binning, el muestreo y las coordenadas elegidas. Un mínimo oscuro no es una energía absoluta ni demuestra un estado termodinámico convergido. Regiones no visitadas no tienen probabilidad estimable; no deben interpretarse como barreras cuantificadas.

### 22. Comparación con información experimental

Una simulación gana valor cuando sus observables se conectan con mediciones independientes. Según el sistema pueden compararse:

- estructuras de rayos X o cryo-EM, considerando contactos cristalinos y resolución;
- factores B, con cautela por desorden estático y efectos del cristal;
- ensambles de RMN, NOE, parámetros de orden o acoplamientos residuales;
- datos SAXS, FRET, HDX-MS o mutagénesis;
- distancias conocidas del sitio activo;
- estados abiertos y cerrados depositados en PDB.

La relación idealizada entre desplazamiento cuadrático medio isotrópico y factor B es:

$$
B=\frac{8\pi^2}{3}\langle u^2\rangle
$$

No compare directamente RMSF de solución con factores B cristalográficos como si fueran la misma magnitud. El factor B incluye contribuciones del cristal, refinamiento y desorden, mientras que RMSF depende del alineamiento, la ventana temporal y el campo de fuerza. Son comparables principalmente como perfiles cualitativos o mediante un modelo explícito.

Para proyectar un conjunto de estructuras experimentales sobre una base PCA deben alinearse, contener una selección atómica común y respetar el mismo orden. La coincidencia parcial indica que la simulación visita movimientos compatibles; la ausencia de coincidencia puede reflejar tiempo insuficiente, ligandos ausentes, condiciones diferentes o sesgo del campo de fuerza.

### 23. Aplicación del esquema a otros tipos de simulación

La lógica general —corregir PBC, seleccionar un marco de referencia, comprobar estabilidad, analizar coordenadas funcionales, estimar incertidumbre y comparar réplicas— se transfiere a otros sistemas. Los comandos no pueden copiarse sin modificar selecciones y significado físico.

| Sistema               | Parte reutilizable                      | Adaptación necesaria                                                                                                        |
| --------------------- | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Proteína–ligando      | RMSD/RMSF de proteína, PCA, clustering  | Ajustar por proteína; analizar pose, contactos y distancias del ligando por separado.                                       |
| Oligómero             | PCA, contactos, distancias y clustering | Decidir si el ajuste usa una subunidad o el ensamblado; separar movimientos internos de reorganización cuaternaria.         |
| Membrana–proteína     | Análisis de proteína y modos colectivos | Hacer moléculas enteras; no usar trayectoria ajustada para difusión lipídica, área o fluctuaciones de caja.                 |
| Proteína con cofactor | Controles estructurales y PCA           | Incluir el cofactor solo si su parametrización y la selección responden a la pregunta; controlar geometría de coordinación. |
| Coarse-grained        | PCA, clustering y contactos             | Usar partículas equivalentes, interpretar otra resolución y no comparar amplitudes directamente con all-atom.               |
| Réplicas o variantes  | Base PCA común y análisis por bloques   | Mantener idénticos átomos, orden, referencia y preprocesamiento; cuantificar variabilidad entre réplicas.                   |

PCA no debe aplicarse indiscriminadamente a todas las coordenadas del sistema. Incluir agua, iones o lípidos junto con la proteína genera una matriz dominada por difusión y permutación de moléculas equivalentes. Para solvente y membrana son preferibles densidades, difusión, orientación, contactos o variables colectivas específicas.

### 24. Proteínas modeladas o inicialmente inestables

Si la estructura proviene de homología, predicción o modelado de bucles:

- revise regiones de baja confianza;
- minimice contactos locales antes de interpretar movimientos;
- use calentamiento gradual si el sistema presenta inestabilidad inicial;
- considere un paso de integración menor, por ejemplo 1 fs, durante las primeras etapas;
- reduzca las restricciones por etapas en vez de retirarlas abruptamente;
- no interprete la relajación del modelo como un cambio biológico.

Ejemplo de liberación gradual:

```ini
; Etapa inicial
define = -DPOSRES
```

Puede generar archivos de restricciones con constantes decrecientes, por ejemplo 1000, 500, 100 y 0 kJ mol⁻¹ nm⁻², manteniendo la duración y los criterios documentados. Cada etapa debe continuar desde las coordenadas y velocidades de la anterior.

### 25. Cofactores, metales y residuos no estándar

Una proteína que contiene solo residuos reconocidos por el campo de fuerza puede procesarse directamente mediante **pdb2gmx**. Un cofactor orgánico, grupo prostético o residuo modificado requiere parámetros compatibles.

No todos los cofactores deben tratarse como ligandos independientes. Existen varios casos:

- **cofactor no covalente:** puede definirse como otro `[ moleculetype ]`;
- **grupo covalente:** requiere enlaces y parámetros entre proteína y cofactor;
- **residuo modificado:** puede necesitar una entrada RTP y reglas de enlace;
- **metal estructural o catalítico:** exige un modelo específico de coordinación;
- **ion difusible:** puede usar la topología iónica del campo de fuerza.

Un metal coordinado no debe reemplazarse por un ion genérico sin evaluar geometría, estado de oxidación, coordinación y transferencia de carga.

Valide siempre que el orden de las coordenadas coincida con `[ molecules ]` y que la carga total sea la esperada.

### 26. Monómeros, oligómeros y estabilidad artificial

Cambiar el identificador de cadena o agrupar átomos en **index.ndx** no crea enlaces ni estabiliza físicamente un oligómero. Los grupos sirven para selecciones, acoplamiento, salida o análisis.

Si una estructura polimérica se desarma durante la simulación, investigue primero:

- si se simuló la unidad biológica correcta;
- si faltan cadenas, lípidos, ligandos o cofactores;
- si las interfaces dependen del pH o fuerza iónica;
- si se perdieron enlaces covalentes o disulfuro;
- si la orientación inicial es correcta;
- si existen errores de PBC o visualización;
- si la escala temporal observada es compatible con el fenómeno.

Las restricciones de posición pueden mantener una geometría, pero también impedir la dinámica que se pretende estudiar. Para conservar contactos específicos pueden emplearse restricciones de distancia, siempre que exista una justificación física o experimental. Congelar grupos completos altera más drásticamente la dinámica y debe evitarse salvo casos técnicos muy controlados.

Las restricciones aplicadas durante producción deben informarse porque modifican el ensamble y limitan la interpretación de fluctuaciones, RMSD, RMSF y transiciones conformacionales.

### 27. Criterio para continuar

Proceda a EM, NVT, NPT y producción únicamente cuando:

- la estructura inicial represente la especie biológica correcta;
- todos los componentes estén parametrizados;
- la topología y las coordenadas tengan el mismo número de átomos;
- la carga total sea razonable;
- las advertencias de **grompp** estén resueltas;
- caja, solvente e iones sean apropiados;
- se haya definido de antemano qué propiedades se analizarán.

Para una proteína monomérica formada exclusivamente por aminoácidos estándar, el flujo EM → NVT → NPT → MD suele ser suficiente. La presencia de cofactores, modificaciones, metales, membranas o interfaces oligoméricas requiere un protocolo específico; no debe resolverse mediante restricciones genéricas sin modelar antes la química faltante.

### Fuentes

1. [Preparación de sistemas en GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/system-preparation.html)
2. [Referencia de gmx pdb2gmx](https://manual.gromacs.org/current/onlinehelp/gmx-pdb2gmx.html)
3. [Campos de fuerza en GROMACS](https://manual.gromacs.org/current/user-guide/force-fields.html)
4. [Referencia de gmx solvate](https://manual.gromacs.org/current/onlinehelp/gmx-solvate.html)
5. [Opciones de archivos MDP](https://manual.gromacs.org/current/user-guide/mdp-options.html)
6. [Tutorial práctico de PCA de trayectorias moleculares, Universidad del Sarre](https://biophys.uni-saarland.de/courses/comp-mol-bio/pract06/)
7. [Referencia oficial de gmx covar](https://manual.gromacs.org/current/onlinehelp/gmx-covar.html#gmx-covar)
8. [Referencia oficial de gmx anaeig](https://manual.gromacs.org/current/onlinehelp/gmx-anaeig.html#gmx-anaeig)
9. [Tutorial introductorio de simulación de proteínas con GROMACS, J. Phys. Chem. B](https://pubs.acs.org/doi/10.1021/acs.jpcb.4c04050)
10. [Revisión sobre aprendizaje automático en el análisis de simulaciones biomoleculares](https://www.tandfonline.com/doi/full/10.1080/23746149.2021.2006080)
11. [Guía práctica complementaria de dinámica esencial con GROMACS](https://stemskillslab.com/how-to-do-pca-gromacs-trajectory-essential-dynamics/)

## Laboratorio de agua pura: condiciones y propiedades físicas

Este laboratorio es **independiente del protocolo de proteína monomérica** desarrollado arriba. Su objetivo es trabajar con una caja de agua sin solutos para aislar el efecto de temperatura, presión, tamaño de la caja, ensamble y modelo molecular sobre las propiedades del líquido. Los archivos ejecutables están en [`examples/water-box/`](https://github.com/juanjosecas/manual-gromacs/tree/main/examples/water-box).

Los tutoriales de [Barnett y Miletić (GASERI)](https://gaseri.org/en/tutorials/gromacs/1-tip4pew-water/) y [Yoo Lab](https://sites.google.com/view/yoo-lab/lectures/biomodeling/biomodeling-water-box) proporcionan los dos puntos de partida. El primero utiliza TIP4P-Ew para reproducir la densidad del agua cerca de 298 K y 1 bar; el segundo introduce las distribuciones radiales, difusión y energía libre derivada de `g(r)`. Aquí se agrega una exploración sistemática de variables, con archivos MDP completos generados por un script y análisis reproducible. Se utiliza GROMACS **2026.x**, con las opciones descritas en su [manual de parámetros](https://manual.gromacs.org/2026.3/user-guide/mdp-options.html).

### Hipótesis y condiciones de control

Para comparar una propiedad, cambiar **una variable cada vez** y mantener fijos modelo, método de integración, electrostática, longitud de producción y tamaño de caja, salvo en experimentos diseñados para evaluar estos factores. Comparar propiedades de TIP4P-Ew y SPC/E *es comparar modelos*, no dos estados termodinámicos de una misma representación molecular.

| Experimento | Condiciones de ejemplo | Magnitudes a seguir | Interpretación |
| --- | --- | --- | --- |
| Temperatura | 280, 298.15, 310, 330 K a 1 bar | Densidad, difusión, `gOO(r)`, `Cp` | Expansión y reorganización del líquido; no extrapolar a cambio de fase |
| Presión | 1, 100, 500 bar a 298.15 K | Densidad, volumen, `gOO(r)` | Respuesta del volumen a presión; comprobar convergencia NPT |
| Modelo de agua | TIP4P-Ew frente a SPC/E a la misma T, P y caja | Densidad, `D`, estructura y `Cp` | Sensibilidad a parametrización; comparar con datos experimentales por propiedad |
| Tamaño de caja | 3, 4, 6 nm | Difusión, fluctuaciones, `gOO(r)` | Efectos de tamaño finito; el coeficiente de difusión tiene correcciones hidrodinámicas |
| Ensamble | Producción NPT frente a NVT tras igual equilibración | Energía, densidad, difusión | NVT fija el volumen; no permite estimar compresibilidad por fluctuaciones de volumen |

**Advertencia física:** a 1 bar, el calentamiento hasta 450 K o enfriamiento pronunciado pueden llevar al sistema real fuera de la región de líquido estable. Una caja periódica homogénea puede permanecer metaestable o impedir la nucleación de otra fase. El rango numérico aceptado por el script sirve para explorar, no garantiza que represente agua líquida en equilibrio para toda combinación. Para estudiar ebullición, congelación, interfaces o coexistencia hace falta un diseño distinto.

### Elegir el modelo molecular

El ejemplo usa únicamente modelos disponibles en distribuciones habituales de GROMACS, combinados con la familia OPLS-AA:

| Modelo | Topología | Coordenadas iniciales | Observación |
| --- | --- | --- | --- |
| TIP4P-Ew | `oplsaa.ff/tip4pew.itp` | `tip4p.gro` | Cuatro sitios, uno virtual; orientado a propiedades del agua líquida |
| SPC/E | `oplsaa.ff/spce.itp` | `spc216.gro` | Tres sitios rígidos; simple y económico |

Un archivo `.gro` suministra geometría inicial: **no define por sí solo el campo de fuerza**. El modelo efectivo queda fijado por el `.itp`. No usar una geometría de tres sitios con una topología de cuatro sitios ni mezclar parámetros de distintas familias sin comprobar compatibilidad. Para introducir OPC o TIP4P/2005 hay que incorporar y validar sus topologías; el ejecutor no los ofrece como opciones automáticas.

### Ejecutar un primer experimento

Se necesita GROMACS instalado y `gmx` accesible en `PATH` (o cargar `GMXRC`), junto con Python 3. No hace falta `numpy` para el procesamiento tabular; `matplotlib` es opcional para generar PNG.

```bash
git clone https://github.com/juanjosecas/manual-gromacs.git
cd manual-gromacs/examples/water-box

python3 run.py --model tip4pew \
    --temperature 298.15 \
    --pressure 1 \
    --box 3 \
    --ensemble npt \
    --npt-ns 1 \
    --prod-ns 10 \
    --seed 42
```

Los parámetros se expresan en **K, bar, nm y ns**. La caja inicial tiene aproximadamente 3 nm por lado. `--npt-ns 1` y `--prod-ns 10` son tiempos de *ejemplo*, no de convergencia garantizada. Cada experimento crea su propio directorio `runs/` y aborta si éste ya existe; no sobrescribe datos.

El script genera, dentro de ese directorio:

- `topol.top` y `water.gro`: topología y estructura, con número de moléculas `SOL` actualizado automáticamente por `gmx solvate`.
- `em.mdp`, `nvt.mdp`, `npt.mdp`, `md.mdp`: protocolos íntegros, editables, con `dt = 0.002 ps`, PME, cortes de 1 nm, corrección de dispersión `EnerPres`, termostato V-rescale y barostato C-rescale en NPT.
- `em.*`, `nvt.*`, `npt.*`, `md.*`: topologías compiladas, checkpoints, energías y trayectorias.
- `thermo.xvg`, `rdf_oo.xvg`, `coordination_oo.xvg`, `msd_ow.xvg`: termodinámica, estructura y movilidad.
- `summary.json`, `summary.csv`, `pmf_oo.csv` y gráficos PNG, si `matplotlib` está instalado.

La secuencia es **solvatar → minimizar → NVT (100 ps) → NPT → producción → análisis**. Las etapas NPT y producción se continúan usando checkpoints, sin regenerar velocidades. La presión instantánea fluctúa intensamente en cajas pequeñas: evaluar el promedio y su incertidumbre, no un fotograma.

### Probar distintas condiciones

Una matriz temperatura–presión pequeña permite ver tendencias antes de invertir tiempo en cálculos largos:

```bash
for T in 280 298.15 310 330; do
    for P in 1 100 500; do
        python3 run.py --model tip4pew --temperature "$T" \
            --pressure "$P" --box 3 --npt-ns 2 --prod-ns 10 --seed 42
    done
done
```

Cada combinación tiene una equilibración independiente. No corresponde iniciar las doce producciones desde el mismo checkpoint de NPT de 298 K si cambian sus condiciones termodinámicas.

Comparación entre representaciones:

```bash
for MODEL in tip4pew spce; do
    python3 run.py --model "$MODEL" --temperature 298.15 \
        --pressure 1 --box 4 --npt-ns 2 --prod-ns 20 --seed 42
done
```

Para estudiar el efecto del volumen fijo, `--ensemble nvt` mantiene en producción el volumen obtenido tras equilibrar previamente a la presión indicada. **La presión de producción pasa a ser un observable**, no una variable fijada por barostato:

```bash
python3 run.py --model tip4pew --temperature 298.15 \
    --pressure 1 --ensemble nvt --npt-ns 2 --prod-ns 10
```

Las réplicas requieren semillas distintas (`--seed 42`, `43`, `44`, etc.). La duración debería aumentarse hasta estabilizar los promedios por bloques. Este experimento no usa calentamiento por etapas ni un protocolo de coexistencia de fases.

### Propiedades macroscópicas y relación con observables microscópicos

| Propiedad | Estimador | Fuente | Condición |
| --- | --- | --- | --- |
| Temperatura, presión, volumen | Promedios temporales | `gmx energy`, archivo `md.edr` | Verificar estacionariedad y unidades |
| Densidad `ρ` | Masa total dividida por volumen; media temporal | `Density` en `md.edr` | NPT para comparar estados a presión impuesta |
| Difusión `D` | `MSD(t) ≈ 6Dt` a tiempos largos | `gmx msd` sobre oxígenos de agua | Intervalo lineal, PBC y tamaño finito |
| Estructura `gOO(r)` | Distribución radial O–O | `gmx rdf` | Normalización y convergencia hacia 1 a distancias grandes |
| Coordinación | Integral de `g(r)` hasta el primer mínimo | `gmx rdf -cn` | Elegir el primer mínimo explícitamente |
| Potencial de fuerza media estructural | `W(r) = -RT ln gOO(r) + C` | `rdf_oo.xvg` → `pmf_oo.csv` | Solo donde `g(r)>0`; constante de referencia arbitraria |
| Compresibilidad isotérmica `κT` | Fluctuaciones de volumen | `md.edr` y `summary.json` | Solo NPT; alta sensibilidad a muestreo |
| Dilatación térmica `αP` | Covarianza volumen–entalpía | `md.edr` y `summary.json` | Solo NPT; sensible a fluctuaciones |
| Capacidad calorífica `Cp` | Fluctuaciones de entalpía | `md.edr` y `summary.json` | Solo NPT; modelo clásico y correcciones cuánticas |
| Viscosidad `η` | Green–Kubo o fórmula de Einstein del tensor de presión | `gmx energy -evisco`, estudio separado | Alta frecuencia de muestreo, simulaciones largas y réplicas |

Para líquidos isotrópicos homogéneos:

$$
\kappa_T = \frac{\langle V^2\rangle-\langle V\rangle^2}
{k_{\mathrm B}T\langle V\rangle},
\qquad
\alpha_P = \frac{\langle VH\rangle-\langle V\rangle\langle H\rangle}
{k_{\mathrm B}T^2\langle V\rangle}.
$$

La capacidad calorífica isobárica total está relacionada con las fluctuaciones de entalpía:

$$
C_P = \frac{\langle H^2\rangle-\langle H\rangle^2}{k_{\mathrm B}T^2}.
$$

El script realiza las conversiones pertinentes a **bar⁻¹**, **K⁻¹** y **J mol⁻¹ de agua K⁻¹**. Para estos estimadores la caja es el sistema estadístico; debe normalizarse el resultado de `Cp` por número de moléculas. Son estimaciones preliminares, sin corrección por autocorrelación ni error de tamaño finito. **El valor de `compressibility` del archivo MDP es un parámetro de acoplamiento de presión, no la compresibilidad que mide el análisis**.

Para obtener la difusión de forma independiente:

```bash
cd runs/tip4pew_npt_T298.15_P1_L3_seed42
gmx msd -s md.tpr -f md.xtc -sel 'name OW' \
    -maxtau 100 -beginfit 20 -endfit 80 -o msd_check.xvg
```

El coeficiente `D` del script se ajusta entre 20–80 ps usando la relación de Einstein, y se expresa en m²/s. En sistemas pequeños, la dependencia de `D` con el tamaño de caja puede ser significativa. La viscosidad y el coeficiente dieléctrico **no se reportan automáticamente**: requieren protocolos específicos, muestreo más prolongado y validación independiente.

Para explorar `g(r)` y el número de coordinación:

```bash
gmx rdf -s md.tpr -f md.xtc -ref 'name OW' -sel 'name OW' \
    -o rdf_oo_check.xvg -cn coordination_oo_check.xvg
```

La posición e intensidad del primer pico informan sobre la organización local del líquido. La expresión `-RT ln g(r)` describe un **potencial de fuerza media estructural**, que incorpora efectos del entorno; no es el potencial de interacción aislado de dos moléculas ni una energía de unión estándar.

### Interpretación, convergencia y límites

1. **Densidad:** verificar un tramo estacionario y comparar el resultado del modelo con datos experimentales a la misma temperatura y presión. El agua real cerca de 298.15 K y 1 bar tiene densidad próxima a 997 kg/m³; el resultado depende del modelo.
2. **Difusión:** inspeccionar el MSD completo y ajustar una región lineal; una curva que se satura o presenta saltos indica problemas de muestreo o PBC. Repetir en cajas mayores.
3. **Fluctuaciones:** `κT`, `αP` y `Cp` convergen más lentamente que la densidad. El error por bloques reportado para densidad es una aproximación, **no un intervalo de confianza validado**.
4. **Comparación de estados:** al variar presión o temperatura, reevaluar la equilibración, volumen, parámetros de acoplamiento y región de estabilidad del modelo. Si se busca cuantificar el error, utilizar varias réplicas.
5. **Viscosidad y transiciones de fase:** reservar para protocolos independientes; no inferir viscosidad a partir de 10 ns ni considerar una caja homogénea como demostración de coexistencia líquido–vapor.

Referencias específicas:

- [GASERI — GROMACS tutorial 1: Water](https://gaseri.org/en/tutorials/gromacs/1-tip4pew-water/).
- [Yoo Lab — Biomodeling: water box](https://sites.google.com/view/yoo-lab/lectures/biomodeling/biomodeling-water-box).
- [GROMACS — gmx energy y propiedades de fluctuación](https://manual.gromacs.org/2026.3/onlinehelp/gmx-energy.html).
- [GROMACS — gmx msd](https://manual.gromacs.org/2026.3/onlinehelp/gmx-msd.html).
- [GROMACS — gmx rdf](https://manual.gromacs.org/2026.3/onlinehelp/gmx-rdf.html).
- [GROMACS — cálculo de viscosidad](https://manual.gromacs.org/2024.2/reference-manual/special/viscosity-calculation.html).
