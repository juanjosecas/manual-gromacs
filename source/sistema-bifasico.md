## Sistema bifásico

### Modelo de dos solventes: 1-octanol–agua

Un sistema bifásico permite estudiar la distribución de moléculas entre dos medios líquidos, la estructura de la interfaz, la penetración mutua de los solventes y, con un protocolo específico, propiedades como el coeficiente de partición. El sistema no debe tratarse como una caja acuosa convencional: contiene dos fases condensadas, dos interfaces por las condiciones periódicas de contorno y una composición que cambia durante la equilibración.

Este ejemplo describe la construcción de una capa de 1-octanol en contacto con agua. Los nombres de archivos, residuos y tipos atómicos son ejemplos; deben coincidir exactamente con la parametrización utilizada.

El flujo recomendado es:

```text
parametrización del 1-octanol
    ↓
validación de una molécula aislada
    ↓
construcción del líquido de 1-octanol
    ↓
EM y equilibración del líquido puro
    ↓
ampliación de la caja en z
    ↓
incorporación del agua
    ↓
EM → NVT → NPT o NVT de interfaz
    ↓
producción y perfiles a lo largo de z
```

### 1. Decidir qué sistema físico se quiere representar

Antes de construir la caja, defina:

- temperatura y presión;
- campo de fuerza y modelo de agua;
- dimensiones laterales de la interfaz;
- espesor mínimo de cada fase;
- composición inicial;
- presencia de solutos, iones o contraiones;
- duración de la equilibración;
- observable que se calculará.

El sistema inicial puede contener 1-octanol puro y agua pura, pero las fases de equilibrio no serán químicamente puras: parte del agua ingresará en la región rica en octanol y parte del octanol ingresará en la región acuosa. Para estudios de partición conviene considerar fases previamente saturadas o equilibrar el sistema durante un tiempo suficiente. Una configuración visualmente separada no demuestra que se haya alcanzado el equilibrio composicional.

Debido a la periodicidad, una lámina de octanol rodeada por agua genera normalmente dos interfaces aproximadamente paralelas al plano xy. El tamaño de la caja en z debe evitar que ambas interfaces interactúen de manera artificial.

### 2. Parametrización del 1-octanol

El 1-octanol no es un residuo proteico estándar y no debe procesarse con **gmx pdb2gmx** como si fuera un aminoácido. Se necesitan:

- coordenadas tridimensionales;
- topología molecular;
- tipos atómicos;
- cargas parciales;
- parámetros enlazados;
- parámetros de Lennard-Jones compatibles con el campo de fuerza;
- reglas de combinación coherentes con el resto del sistema.

SMILES del 1-octanol:

```text
CCCCCCCCO
```

SwissParam genera parámetros compatibles con la familia CHARMM y puede ser útil para una prueba inicial. No convierte automáticamente esos parámetros en una parametrización validada para propiedades de partición o de interfaz. Para un trabajo cuantitativo deben comprobarse, al menos:

- carga total igual a cero;
- geometría y conformaciones;
- densidad del líquido;
- entalpía de vaporización, si corresponde;
- solubilidad mutua con agua;
- distribución de cargas;
- compatibilidad exacta con la versión del campo de fuerza.

No mezcle una topología generada para CHARMM con un campo AMBER, GROMOS u OPLS. Tampoco copie bloques `[ atomtypes ]` sin comprobar si los nombres ya existen: dos tipos con el mismo nombre y parámetros diferentes invalidan la topología.

Una organización sencilla es:

```text
00_parametros/
    octanol.gro
    octanol.itp
    octanol_atomtypes.itp
01_octanol_liquido/
02_interfaz/
03_em/
04_nvt/
05_npt/
06_md/
07_analisis/
topol.top
```

### 3. Revisar la topología molecular

El archivo **octanol.itp** debe contener un único `[ moleculetype ]` y las secciones moleculares correspondientes:

```ini
[ moleculetype ]
; nombre    nrexcl
OCT         3

[ atoms ]
; nr  tipo  resnr  residuo  átomo  cgnr  carga  masa
; ...

[ bonds ]
; ...

[ pairs ]
; ...

[ angles ]
; ...

[ dihedrals ]
; ...
```

Si el generador entrega tipos atómicos nuevos, colóquelos en un archivo separado que se incluya inmediatamente después del campo de fuerza y antes de **octanol.itp**:

```ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/octanol_atomtypes.itp"
#include "00_parametros/octanol.itp"
```

No coloque `[ atomtypes ]` después de haber comenzado una definición `[ moleculetype ]`. El preprocesador de topologías exige un orden específico de directivas.

Compruebe que la coordenada de una molécula aislada tenga exactamente los mismos átomos, nombres y orden que la sección `[ atoms ]`:

```bash
gmx check -f 00_parametros/octanol.gro
```

Para inspeccionar la topología expandida:

```bash
gmx grompp \
    -f em_single.mdp \
    -c 00_parametros/octanol.gro \
    -p topol_single.top \
    -o octanol_single.tpr \
    -pp octanol_single_processed.top
```

No use **-maxwarn** para ocultar incompatibilidades.

### 4. Calcular el número inicial de moléculas

El número de moléculas no debe elegirse de manera arbitraria. A partir de una densidad objetivo:

$$
N = \frac{\rho V N_\mathrm{A}}{M}
$$

donde:

- $N$ es el número de moléculas;
- $\rho$ es la densidad;
- $V$ es el volumen;
- $N_\mathrm{A}$ es la constante de Avogadro;
- $M$ es la masa molar.

Para usar $\rho$ en g·cm⁻³, $V$ en nm³ y $M$ en g·mol⁻¹:

$$
N = \frac{\rho\,V\,10^{-21}\,N_\mathrm{A}}{M}
$$

porque:

$$
1\ \mathrm{nm^3}=10^{-21}\ \mathrm{cm^3}
$$

Para 1-octanol, $M = 130.23\ \mathrm{g\,mol^{-1}}$. Usando como ejemplo $\rho \approx 0.827\ \mathrm{g\,cm^{-3}}$ y una caja de 5 × 5 × 5 nm:

$$
V=125\ \mathrm{nm^3}
$$

$$
N \approx 478\ \text{moléculas}
$$

Por lo tanto, 500 moléculas son razonables como punto de partida para una caja cercana a 5 nm por lado. En cambio, 500 moléculas en 10 × 10 × 10 nm corresponden aproximadamente a:

$$
\rho \approx 0.108\ \mathrm{g\,cm^{-3}}
$$

Ese sistema está muy subdensificado y contiene grandes huecos. La presión NPT inicial puede ser extrema y la caja tendría que contraerse de manera drástica.

La densidad experimental utilizada debe corresponder a la temperatura del protocolo. El valor inicial solo aproxima el volumen; la caja debe equilibrarse con el modelo molecular elegido.

### 5. Construir el líquido de 1-octanol

Centre una molécula y asegúrese de que las coordenadas estén expresadas en nanómetros:

```bash
gmx editconf \
    -f 00_parametros/octanol.gro \
    -o 00_parametros/octanol_centered.gro \
    -center 0 0 0
```

Inserte las moléculas en una caja inicial de 5 × 5 × 5 nm:

```bash
mkdir -p 01_octanol_liquido

gmx insert-molecules \
    -ci 00_parametros/octanol_centered.gro \
    -nmol 500 \
    -box 5 5 5 \
    -try 500 \
    -seed 2026 \
    -o 01_octanol_liquido/octanol_box.gro
```

**gmx insert-molecules** evita solapamientos mediante radios atómicos, pero no garantiza que el número solicitado pueda insertarse. Revise la línea final y use el número realmente añadido en `[ molecules ]`.

Si no logra insertar todas las moléculas:

- aumente moderadamente la caja;
- incremente **-try**;
- revise radios y nombres atómicos;
- inserte una cantidad menor y comprima durante una equilibración controlada;
- no reduzca agresivamente **-scale** sin inspeccionar los contactos creados.

No use una semilla aleatoria indefinida si desea reproducibilidad.

Topología inicial:

```ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/octanol_atomtypes.itp"
#include "00_parametros/octanol.itp"

[ system ]
1-octanol líquido

[ molecules ]
; molécula    cantidad
OCT           500
```

El nombre **OCT** debe ser idéntico al definido en `[ moleculetype ]`.

### 6. Minimizar el líquido de 1-octanol

Archivo **em_octanol.mdp**:

```ini
title           = Minimización del líquido de 1-octanol
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

Los cortes son ejemplos. Deben reemplazarse por los valores recomendados para el campo de fuerza seleccionado.

```bash
mkdir -p 03_em

gmx grompp \
    -f em_octanol.mdp \
    -c 01_octanol_liquido/octanol_box.gro \
    -p topol.top \
    -o 03_em/octanol_em.tpr \
    -pp 03_em/octanol_processed.top

gmx mdrun \
    -deffnm 03_em/octanol_em \
    -v
```

Revise energía potencial, fuerza máxima, contactos anómalos y valores NaN. La convergencia numérica de la minimización no demuestra que la densidad o la estructura del líquido sean correctas.

### 7. Equilibrar primero la fase de 1-octanol

Una trayectoria de 1 ps es insuficiente para equilibrar un líquido construido por inserción aleatoria. Use primero NVT para estabilizar la temperatura y luego NPT para ajustar densidad y volumen.

Ejemplo NVT:

```ini
title           = NVT del 1-octanol
integrator      = md
dt              = 0.002
nsteps          = 250000
continuation    = no
gen-vel         = yes
gen-temp        = 300
gen-seed        = 2026

constraints     = h-bonds
tcoupl          = V-rescale
tc-grps         = System
tau-t           = 1.0
ref-t           = 300

pcoupl          = no
pbc             = xyz
```

Con 250000 pasos de 0.002 ps se simulan 500 ps.

```bash
mkdir -p 04_nvt

gmx grompp \
    -f nvt_octanol.mdp \
    -c 03_em/octanol_em.gro \
    -p topol.top \
    -o 04_nvt/octanol_nvt.tpr

gmx mdrun \
    -deffnm 04_nvt/octanol_nvt \
    -v
```

Ejemplo NPT isotrópico:

```ini
title            = NPT del 1-octanol
integrator       = md
dt               = 0.002
nsteps           = 2500000
continuation     = yes
gen-vel          = no

constraints      = h-bonds
tcoupl           = V-rescale
tc-grps          = System
tau-t            = 1.0
ref-t            = 300

pcoupl            = C-rescale
pcoupltype        = isotropic
tau-p             = 5.0
ref-p             = 1.0
compressibility   = 8.0e-5

pbc              = xyz
```

Aquí se simulan 5 ns. La compresibilidad es un valor inicial ilustrativo y debe reemplazarse por un valor justificado para el líquido y las condiciones elegidas.

```bash
mkdir -p 05_npt

gmx grompp \
    -f npt_octanol.mdp \
    -c 04_nvt/octanol_nvt.gro \
    -t 04_nvt/octanol_nvt.cpt \
    -p topol.top \
    -o 05_npt/octanol_npt.tpr

gmx mdrun \
    -deffnm 05_npt/octanol_npt \
    -v
```

Controle densidad, volumen, presión y energía:

```bash
(echo Density; echo Volume; echo Pressure; echo Potential; echo 0) | \
gmx energy \
    -f 05_npt/octanol_npt.edr \
    -o 07_analisis/octanol_bulk_properties.xvg
```

La presión instantánea tiene fluctuaciones grandes. Compare promedios por bloques y compruebe que densidad y volumen hayan alcanzado una región estacionaria.

### 8. Preparar la lámina de 1-octanol

Use la última configuración equilibrada, no un PDB extraído arbitrariamente de una trayectoria. El formato GRO conserva la caja con precisión suficiente y evita pérdidas innecesarias de información.

Primero consulte las dimensiones finales:

```bash
gmx check -f 05_npt/octanol_npt.gro
```

Supóngase, solo como ejemplo, que la caja equilibrada mide aproximadamente 5 × 5 × 5 nm. Amplíe únicamente z para crear espacio para el agua:

```bash
mkdir -p 02_interfaz

gmx editconf \
    -f 05_npt/octanol_npt.gro \
    -o 02_interfaz/octanol_slab_box.gro \
    -box 5 5 12 \
    -center 2.5 2.5 6.0
```

Use los valores reales de $L_x$ y $L_y$ de la fase equilibrada. Cambiarlos en este paso impone una deformación lateral. La región vacía debe quedar distribuida a ambos lados de la lámina para generar dos interfaces equivalentes.

Compruebe visualmente:

- que el octanol forme una única lámina continua;
- que no quede dividido por una representación incorrecta de PBC;
- que exista espacio suficiente para el agua;
- que los grupos hidroxilo no hayan sido orientados artificialmente de forma uniforme.

### 9. Incorporar el agua

Incluya la topología de agua compatible con el campo de fuerza antes de la sección `[ system ]`:

```ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/octanol_atomtypes.itp"
#include "00_parametros/octanol.itp"
#include "campo_de_fuerza.ff/modelo_de_agua.itp"

[ system ]
Interfaz 1-octanol–agua

[ molecules ]
; molécula    cantidad
OCT           500
```

Solvate usando explícitamente una caja de agua:

```bash
gmx solvate \
    -cp 02_interfaz/octanol_slab_box.gro \
    -cs spc216.gro \
    -o 02_interfaz/octanol_water.gro \
    -p topol.top
```

**spc216.gro** aporta una configuración geométrica de agua de tres sitios; la interacción efectiva queda definida por la topología incluida. Verifique que el modelo de agua sea el recomendado para el campo de fuerza.

**gmx solvate** elimina moléculas que solapan con el octanol y actualiza el número de agua en `[ molecules ]`. La salida final debe quedar, por ejemplo:

```ini
[ molecules ]
; molécula    cantidad
OCT           500
SOL           4442
```

El valor 4442 no es universal. Depende de las dimensiones finales, la densidad de la lámina y los criterios geométricos de solvatación. Use el número informado por su propia ejecución.

Revise el orden: las coordenadas contienen primero OCT y después SOL, por lo que `[ molecules ]` debe seguir el mismo orden.

Compruebe el sistema:

```bash
gmx check -f 02_interfaz/octanol_water.gro
```

### 10. Minimización y equilibración de la interfaz

La interfaz recién construida contiene contactos y una distribución no equilibrada de ambos líquidos. Ejecute nuevamente EM, NVT y una equilibración apropiada de volumen o área.

```bash
gmx grompp \
    -f em_interface.mdp \
    -c 02_interfaz/octanol_water.gro \
    -p topol.top \
    -o 03_em/interface_em.tpr \
    -pp 03_em/interface_processed.top

gmx mdrun \
    -deffnm 03_em/interface_em \
    -v
```

NVT:

```bash
gmx grompp \
    -f nvt_interface.mdp \
    -c 03_em/interface_em.gro \
    -p topol.top \
    -o 04_nvt/interface_nvt.tpr

gmx mdrun \
    -deffnm 04_nvt/interface_nvt \
    -v
```

Para una interfaz plana existen dos estrategias principales:

| Estrategia                           | Ventaja                                              | Limitación                                                           |
| ------------------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------- |
| NPT semiisotrópico                   | Permite ajustar por separado el plano xy y el eje z. | Las fluctuaciones del área pueden modificar la interfaz.             |
| NVT con caja previamente equilibrada | Mantiene fija el área interfacial.                   | Requiere haber determinado antes dimensiones y densidades adecuadas. |

Ejemplo NPT semiisotrópico:

```ini
pcoupl            = C-rescale
pcoupltype        = semiisotropic
tau-p             = 5.0
ref-p             = 1.0 1.0
compressibility   = 4.5e-5 4.5e-5
```

Los dos valores corresponden al plano xy y al eje z. No copie automáticamente la compresibilidad del agua para todo el sistema: debe justificarse según el protocolo y comprobarse que la caja no derive o colapse.

El acoplamiento por tensión superficial también existe, pero no debe utilizarse solo porque el sistema tenga una interfaz. Requiere una tensión objetivo y una interpretación consistente del ensamble.

Para producción, continúe desde el checkpoint:

```bash
gmx grompp \
    -f md_interface.mdp \
    -c 05_npt/interface_npt.gro \
    -t 05_npt/interface_npt.cpt \
    -p topol.top \
    -o 06_md/interface_md.tpr

gmx mdrun \
    -deffnm 06_md/interface_md \
    -v
```

### 11. Controles mínimos de la trayectoria

Corrija únicamente la representación periódica necesaria para visualizar. No centre el sistema de una manera que desplace la interfaz entre fotogramas sin documentarlo.

Extraiga una configuración:

```bash
echo System | \
gmx trjconv \
    -s 06_md/interface_md.tpr \
    -f 06_md/interface_md.xtc \
    -o 07_analisis/interface_last.gro \
    -dump 100000
```

El tiempo de **-dump** se expresa en ps. En este ejemplo, 100000 ps equivalen a 100 ns.

Perfil de densidad de masa a lo largo de z:

```bash
gmx density \
    -s 06_md/interface_md.tpr \
    -f 06_md/interface_md.xtc \
    -n index.ndx \
    -d Z \
    -sl 200 \
    -dens mass \
    -o 07_analisis/density_z.xvg
```

Cree grupos separados para OCT y SOL y analice ambos perfiles. Un sistema bifásico equilibrado debe mostrar:

- una región rica en agua;
- una región rica en octanol;
- dos zonas interfaciales;
- densidades aproximadamente constantes en el centro de cada fase, si el espesor es suficiente;
- ausencia de deriva sistemática del espesor o de la posición de la lámina.

La anchura de la interfaz depende del binning. Repita el cálculo con distintos valores de **-sl** para verificar que la conclusión no sea un artefacto de discretización.

### 12. Propiedades y análisis adicionales

#### Penetración mutua de los solventes

Los perfiles de densidad de OCT y SOL permiten estimar la presencia de agua en la fase rica en octanol y de octanol en la fase acuosa. Descarte la etapa transitoria y compare bloques temporales independientes.

#### Orientación del 1-octanol

Puede analizarse el ángulo entre el vector C1–O del 1-octanol y el eje z:

```bash
gmx gangle \
    -s 06_md/interface_md.tpr \
    -f 06_md/interface_md.xtc \
    -n index.ndx \
    -g1 vector \
    -group1 'vector connecting atomnr START END' \
    -g2 z \
    -oav 07_analisis/octanol_orientation.xvg
```

La selección debe adaptarse a los índices reales. Para obtener una distribución molecular completa puede ser necesario definir pares equivalentes para todas las moléculas.

#### Tensión interfacial

Para una lámina con dos interfaces planas normales a z:

$$
\gamma =
\frac{L_z}{2}
\left[
P_{zz}-
\frac{P_{xx}+P_{yy}}{2}
\right]
$$

El factor 1/2 aparece porque la caja periódica contiene dos interfaces. $P_{xx}$, $P_{yy}$ y $P_{zz}$ son los componentes diagonales del tensor de presión.

Extraiga los componentes con **gmx energy**:

```bash
(echo Pres-XX; echo Pres-YY; echo Pres-ZZ; echo Box-Z; echo 0) | \
gmx energy \
    -f 06_md/interface_md.edr \
    -o 07_analisis/pressure_tensor.xvg
```

La tensión interfacial converge lentamente porque el tensor de presión es ruidoso. Deben usarse trayectorias suficientemente largas, promedios por bloques y unidades consistentes. En GROMACS, presión se informa en bar y longitud en nm; el resultado no queda automáticamente en mN·m⁻¹ sin conversión.

La equivalencia útil es:

$$
1\ \mathrm{bar\,nm}=0.1\ \mathrm{mN\,m^{-1}}
$$

#### Coeficiente de partición

Contar espontáneamente un soluto en cada fase puede servir si ocurren muchas transiciones reversibles. Para moléculas con barreras altas, una única trayectoria suele quedar atrapada en una fase y no permite estimar un coeficiente de partición confiable. En esos casos se requieren métodos de energía libre y réplicas, no solo una caja bifásica más larga.

### 13. Errores frecuentes

- Usar 500 moléculas en una caja de 10 nm por lado sin calcular la densidad.
- Parametrizar octanol con un campo de fuerza y combinarlo con otro.
- Duplicar tipos atómicos con nombres iguales.
- Confundir el solvente de coordenadas **spc216.gro** con el modelo definido en la topología.
- Conservar el número de moléculas solicitado cuando **insert-molecules** insertó menos.
- Escribir `[ molecules ]` en un orden distinto al archivo de coordenadas.
- Extraer un PDB intermedio y perder precisión de caja o velocidades sin necesidad.
- Equilibrar solo 1 ps.
- Interpretar separación visual como equilibrio termodinámico.
- Calcular promedios incluyendo la construcción y relajación inicial.
- Aplicar un barostato isotrópico a una interfaz sin evaluar la deformación del área.
- Interpretar ausencia de cruces del soluto como evidencia de partición estable.

### 14. Criterios para iniciar la producción

Continúe únicamente cuando:

- la carga y los tipos atómicos sean correctos;
- la topología expandida no contenga conflictos;
- el número y orden de moléculas coincidan con las coordenadas;
- no existan huecos ni solapamientos graves;
- el octanol puro reproduzca razonablemente la densidad objetivo;
- temperatura, energía y dimensiones de caja sean estacionarias;
- se hayan formado dos regiones de densidad definidas;
- la fase rica en cada solvente tenga espesor suficiente;
- las advertencias de **gmx grompp** estén comprendidas y resueltas;
- el protocolo de producción y los análisis se hayan definido de antemano.

### Fuentes

1. [Preparación de sistemas en GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/system-preparation.html)
2. [Referencia de gmx insert-molecules](https://manual.gromacs.org/current/onlinehelp/gmx-insert-molecules.html)
3. [Referencia de gmx solvate](https://manual.gromacs.org/current/onlinehelp/gmx-solvate.html)
4. [Referencia de gmx editconf](https://manual.gromacs.org/current/onlinehelp/gmx-editconf.html)
5. [Referencia de gmx trjconv](https://manual.gromacs.org/current/onlinehelp/gmx-trjconv.html)
6. [Unidades de GROMACS](https://manual.gromacs.org/current/reference-manual/definitions.html)
7. [Opciones de archivos MDP](https://manual.gromacs.org/current/user-guide/mdp-options.html)
