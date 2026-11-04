## Múltiples moléculas de ligandos y de proteínas

Los sistemas con varias cadenas proteicas y varios ligandos requieren distinguir tres conceptos:

1. **Copia molecular:** instancia concreta con coordenadas propias.
2. **Tipo molecular:** definición de la molécula en una sección `[ moleculetype ]`.
3. **Nombre de residuo:** etiqueta empleada en las coordenadas y en las selecciones.

Dos ligandos químicamente idénticos, con los mismos átomos, orden atómico, enlaces, cargas y parámetros, pueden ser dos copias del mismo tipo molecular. Sus posiciones y conformaciones iniciales pueden ser diferentes. En cambio, ligandos distintos o copias que deban recibir topologías diferentes necesitan tipos moleculares separados.

### Caso 1: varias copias de un ligando idéntico

La estructura PDB 1OKE contiene dos cadenas proteicas y varias moléculas no proteicas, entre ellas dos moléculas BOG. Si ambas copias de BOG tienen la misma composición y parametrización, se necesita una sola topología molecular para BOG.

Antes de parametrizar:

- extraiga una copia completa del ligando;
- revise protonación, carga formal, estereoquímica y orden de enlaces;
- confirme que ambas copias tienen los mismos átomos;
- conserve las coordenadas originales de cada copia;
- use el mismo orden atómico en las coordenadas y en la topología.

Puede asignarse **BOG** como nombre de residuo y como nombre del tipo molecular. Las dos copias se distinguen mediante su número de residuo y, si el formato lo permite, su cadena.

Ejemplo simplificado de coordenadas:

```text
HETATM    1  C1  BOG C   1     -14.258  79.953  45.302  1.00  0.00           C
HETATM    2  O1  BOG C   1     -13.074  79.344  45.814  1.00  0.00           O
...
TER
HETATM   49  C1  BOG D   2     -17.418  58.852   3.720  1.00  0.00           C
HETATM   50  O1  BOG D   2     -16.140  59.295   3.262  1.00  0.00           O
...
```

Los números de átomo deben ser únicos dentro del PDB. Los números de residuo o identificadores de cadena diferentes facilitan el análisis, aunque GROMACS asigna la topología principalmente según el orden de las moléculas.

Topología molecular:

```ini
[ moleculetype ]
; nombre   nrexcl
BOG        3

[ atoms ]
; nr  tipo  resnr  residuo  átomo  cgnr  carga  masa
1     ...   1      BOG      C1     1     ...    12.011
2     ...   1      BOG      O1     2     ...    15.999
; ...
```

En **topol.top** se incluye una sola vez:

```ini
; Parámetros generales
#include "charmm36-jul2022.ff/forcefield.itp"

; Parámetros adicionales del ligando, si corresponden
#include "bog_atomtypes.itp"

; Definición del tipo molecular BOG
#include "bog.itp"

; Cadenas proteicas generadas por pdb2gmx
#include "topol_Protein_chain_A.itp"
#include "topol_Protein_chain_B.itp"
```

Al final del archivo:

```ini
[ system ]
Proteína 1OKE con dos moléculas BOG

[ molecules ]
; tipo molecular       cantidad
Protein_chain_A         1
Protein_chain_B         1
BOG                     2
```

La sección `[ molecules ]` indica que existen dos instancias de BOG. No deben incluirse dos copias idénticas de **bog.itp** porque se redefinirían los mismos tipos o el mismo `[ moleculetype ]`.

El orden de las coordenadas debe ser:

```text
Protein_chain_A
Protein_chain_B
BOG, copia 1
BOG, copia 2
```

Este orden debe coincidir exactamente con `[ molecules ]`.

### Cuándo son necesarias topologías separadas

Use tipos moleculares diferentes, por ejemplo **LIGA** y **LIGB**, cuando:

- los ligandos son químicamente distintos;
- tienen diferente protonación o carga;
- una copia contiene átomos o enlaces diferentes;
- se parametrizaron con términos diferentes;
- se aplicarán restricciones posicionales distintas;
- se realizarán transformaciones alquí­micas o cálculos de energía libre diferentes por copia.

En ese caso:

```ini
#include "ligand_A.itp"
#include "ligand_B.itp"

[ molecules ]
Protein_chain_A    1
Protein_chain_B    1
LIGA               1
LIGB               1
```

Duplicar una topología solo para cambiar el nombre del residuo suele ser innecesario. Si se crean **LIGA** y **LIGB**, ambos archivos deben tener nombres de `[ moleculetype ]` diferentes y todos sus índices deben seguir siendo locales a cada molécula.

### Sistemas con muchas cadenas: ejemplo 6BKK

La estructura 6BKK corresponde al dominio transmembrana M2 de influenza A unido a amantadina. El sistema biológico y la unidad cristalográfica deben revisarse antes de simular: no debe suponerse que todas las cadenas del PDB forman la unidad funcional.

Prepare la proteína sin eliminar ligandos o cofactores hasta haber registrado su identidad y posición. Luego genere la topología de las cadenas:

```bash
gmx pdb2gmx \
    -f protein_only.pdb \
    -o protein_processed.gro \
    -p topol.top \
    -i posre_protein.itp \
    -water tip3p
```

Seleccione un campo de fuerza compatible con la topología de amantadina. No use automáticamente CHARMM27 por aparecer en protocolos antiguos; registre el campo de fuerza concreto disponible en la instalación.

Si **pdb2gmx** separa las cadenas en archivos ITP, **topol.top** puede contener:

```ini
#include "topol_Protein_chain_A.itp"
#include "topol_Protein_chain_B.itp"
#include "topol_Protein_chain_C.itp"
#include "topol_Protein_chain_D.itp"
#include "topol_Protein_chain_E.itp"
#include "topol_Protein_chain_F.itp"
#include "topol_Protein_chain_G.itp"
#include "topol_Protein_chain_H.itp"
```

La cantidad y el orden deben verificarse en la salida real. No copie esta lista a otro sistema.

Si existen dos amantadinas idénticas:

```ini
[ molecules ]
Protein_chain_A    1
Protein_chain_B    1
Protein_chain_C    1
Protein_chain_D    1
Protein_chain_E    1
Protein_chain_F    1
Protein_chain_G    1
Protein_chain_H    1
AMA                2
```

Cada copia debe tener coordenadas propias, números de átomo válidos y el mismo orden interno que **ama.itp**.

### Construcción y validación de las coordenadas

Después de combinar proteína y ligandos:

```bash
gmx editconf     -f protein_ligands.pdb     -o complex.gro
```

Revise el archivo:

```bash
gmx check -f complex.gro
```

Genere un TPR de validación antes de solvatar. Puede usarse un MDP mínimo:

```ini
integrator      = steep
nsteps          = 0
cutoff-scheme   = Verlet
coulombtype     = PME
rcoulomb        = 1.0
rvdw            = 1.0
pbc             = xyz
```

```bash
gmx grompp \
    -f validate.mdp \
    -c complex.gro \
    -p topol.top \
    -o validate.tpr \
    -pp processed.top
```

La opción **-pp processed.top** guarda la topología ya expandida por el preprocesador. Resulta útil para comprobar el orden de las inclusiones, macros y restricciones activadas.

No continúe si aparece alguno de estos problemas:

- número de coordenadas distinto del número de átomos de la topología;
- tipos atómicos desconocidos;
- parámetros enlazados ausentes;
- carga total inesperada;
- redefiniciones de `[ atomtypes ]`;
- nombres distintos entre `[ molecules ]` y `[ moleculetype ]`.

No use **-maxwarn** para forzar el TPR sin comprender cada advertencia.

### Caja, solvatación e iones

Para una proteína soluble:

```bash
gmx editconf     -f complex.gro     -o complex_box.gro     -c     -d 1.0     -bt dodecahedron
```

Para un sistema de membrana no debe construirse una caja acuosa genérica alrededor de la proteína. Primero debe definirse la membrana, su orientación, composición y espesor mediante un protocolo específico.

Solvatación:

```bash
gmx solvate     -cp complex_box.gro     -cs spc216.gro     -o complex_solv.gro     -p topol.top
```

Preprocesamiento para iones:

```bash
gmx grompp     -f ions.mdp     -c complex_solv.gro     -p topol.top     -o ions.tpr
```

Neutralización y NaCl 0.15 mol L⁻¹:

```bash
gmx genion \
    -s ions.tpr \
    -o complex_solv_ions.gro \
    -p topol.top \
    -pname NA \
    -nname CL \
    -neutral \
    -conc 0.15
```

Seleccione el grupo de solvente, normalmente **SOL**. El número del grupo depende del sistema.

### Restricciones de posición

#### Múltiples copias del mismo tipo molecular

Si dos ligandos son instancias del mismo `[ moleculetype ]`, un único archivo de restricciones incluido dentro de esa topología se aplica a todas las copias:

```bash
gmx genrestr     -f bog_only.gro     -o posre_bog.itp     -fc 1000 1000 1000
```

Incluya las restricciones inmediatamente después de la definición de BOG:

```ini
#include "bog.itp"

#ifdef POSRES_BOG
#include "posre_bog.itp"
#endif
```

Active la macro durante la equilibración:

```ini
define = -DPOSRES -DPOSRES_BOG
```

No genere **posre_BOG1.itp** y **posre_BOG2.itp** para incluirlos sobre un único tipo molecular. Los índices de las restricciones son locales al tipo molecular, por lo que ambas copias usarán la misma selección local.

#### Restricciones diferentes para cada copia

Si BOG1 y BOG2 deben tener restricciones diferentes, defina dos tipos moleculares:

```ini
#include "bog1.itp"
#ifdef POSRES_BOG1
#include "posre_bog1.itp"
#endif

#include "bog2.itp"
#ifdef POSRES_BOG2
#include "posre_bog2.itp"
#endif
```

```ini
[ molecules ]
Protein_chain_A    1
Protein_chain_B    1
BOG1               1
BOG2               1
```

Esta duplicación aumenta el mantenimiento y solo se justifica si las copias requieren un tratamiento realmente diferente.

#### Cadenas proteicas

Las restricciones de cada cadena deben estar dentro del ámbito del `[ moleculetype ]` correspondiente. Los ITP generados por **pdb2gmx** suelen incluir su propio archivo de restricciones mediante la macro **POSRES**. Revise cada archivo antes de añadir nuevas inclusiones.

Ejemplo dentro de **topol_Protein_chain_A.itp**:

```ini
[ moleculetype ]
Protein_chain_A    3

; átomos, enlaces y otros términos
; ...

#ifdef POSRES
#include "posre_Protein_chain_A.itp"
#endif
```

No reúna al final de **topol.top** restricciones de varias moléculas como si utilizaran índices globales.

### Grupos de índice para varias cadenas y ligandos

Cree grupos explícitos:

```bash
gmx make_ndx     -f complex_solv_ions.gro     -o index.ndx
```

Ejemplo interactivo para dos ligandos con residuo BOG:

```text
r BOG
name 18 BOG_all
"Protein" | 18
name 19 Protein_BOG
q
```

Los números 18 y 19 son ejemplos. Use los asignados en su sesión.

Las dos copias pueden seleccionarse por número de residuo, cadena o índice atómico. La sintaxis exacta depende de la información conservada en el archivo:

```bash
gmx select     -s complex_solv_ions.gro     -n index.ndx     -select 'resname BOG'
```

Para separar las copias por número de residuo:

```bash
gmx select     -s complex_solv_ions.gro     -select 'resname BOG and resid 1'     -on bog_1.ndx

gmx select     -s complex_solv_ions.gro     -select 'resname BOG and resid 2'     -on bog_2.ndx
```

Si los números de residuo no son únicos entre cadenas, seleccione además por identificador de cadena cuando esté disponible o utilice rangos de índices verificados.

### Minimización y equilibración

La minimización sigue el flujo general:

```bash
gmx grompp \
    -f em.mdp \
    -c complex_solv_ions.gro \
    -p topol.top \
    -n index.ndx \
    -o em.tpr

gmx mdrun -deffnm em -v
```

NVT con restricciones:

```bash
gmx grompp \
    -f nvt.mdp \
    -c em.gro \
    -r em.gro \
    -p topol.top \
    -n index.ndx \
    -o nvt.tpr

gmx mdrun -deffnm nvt -v
```

NPT continuando coordenadas y velocidades:

```bash
gmx grompp \
    -f npt.mdp \
    -c nvt.gro \
    -r nvt.gro \
    -t nvt.cpt \
    -p topol.top \
    -n index.ndx \
    -o npt.tpr

gmx mdrun -deffnm npt -v
```

No use el barostato Berendsen para obtener un ensamble de producción. Para equilibración, **C-rescale** permite controlar la presión y genera el ensamble correcto. Para producción suele utilizarse **Parrinello-Rahman**, según el sistema y el protocolo.

Ejemplo de acoplamiento durante NPT:

```ini
tcoupl           = V-rescale
tc-grps          = Protein_LIG Water_and_ions
tau-t            = 1.0 1.0
ref-t            = 300 300

pcoupl           = C-rescale
pcoupltype       = isotropic
tau-p            = 5.0
ref-p            = 1.0
compressibility  = 4.5e-5
```

**tau-t** y **tau-p** se expresan en ps; **ref-t**, en K; **ref-p**, en bar; la compresibilidad, en bar⁻¹.

El tiempo de simulación se calcula como:

```text
tiempo = dt × nsteps
```

Con **dt = 0.002 ps** y **nsteps = 500000**, el tiempo es 1000 ps, equivalente a 1 ns. En el texto anterior, **nsteps = 20000** se interpretaba erróneamente como 60 ns: en realidad corresponde a 40 ps con un paso de 2 fs.

### Producción

Genere el TPR sin las macros de restricciones, salvo que formen parte deliberada del experimento:

```bash
gmx grompp \
    -f md.mdp \
    -c npt.gro \
    -t npt.cpt \
    -p topol.top \
    -n index.ndx \
    -o md.tpr

gmx mdrun -deffnm md -v
```

Compruebe que **md.mdp** contiene **continuation = yes** y **gen-vel = no**. La producción debe continuar las velocidades de NPT.

Para revisar métodos y parámetros contenidos en el TPR:

```bash
gmx dump -s md.tpr > md_tpr_dump.txt
gmx report-methods -s md.tpr -o methods.tex
```

**gmx report-methods** genera una descripción de métodos a partir del TPR. Debe revisarse antes de incorporarla a un manuscrito.

### Preparación de la trayectoria

Haga las moléculas completas:

```bash
echo System |
gmx trjconv     -s md.tpr     -f md.xtc     -o md_whole.xtc     -pbc whole
```

Centre el complejo completo:

```bash
(echo Protein_LIG; echo System) |
gmx trjconv \
    -s md.tpr \
    -f md_whole.xtc \
    -o md_center.xtc \
    -center \
    -pbc mol \
    -ur compact \
    -n index.ndx
```

Ajuste rotación y traslación respecto del backbone de todas las cadenas:

```bash
(echo Backbone; echo System) |
gmx trjconv     -s md.tpr     -f md_center.xtc     -o md_fit.xtc     -fit rot+trans     -n index.ndx
```

Para oligómeros, inspeccione que el grupo usado para centrar contiene todas las cadenas funcionales y todos los ligandos relevantes.

### RMSD de cada ligando

Si ambas copias están en un mismo grupo, **gmx rms** calcula un único RMSD sobre el conjunto completo; no produce automáticamente una curva independiente por molécula.

Cree grupos separados para BOG1 y BOG2 y calcule cada curva después de ajustar sobre la proteína:

```bash
(echo Backbone; echo BOG1) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_bog1.xvg     -tu ns

(echo Backbone; echo BOG2) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_bog2.xvg     -tu ns
```

El primer grupo selecciona los átomos usados para el ajuste; el segundo, los átomos cuyo RMSD se calcula. Para ligandos simétricos, el RMSD convencional puede mostrar saltos por permutaciones de átomos equivalentes y debe interpretarse con cuidado.

Comando extra para medir la distancia mínima de cada ligando a la proteína:

```bash
gmx pairdist \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -ref 'group "Protein"' \
    -sel 'group "BOG1"' 'group "BOG2"' \
    -type min \
    -o ligand_protein_mindist.xvg
```

### RMSD de cadenas individuales

Cree grupos para cada cadena y use el oligómero completo como grupo de ajuste si desea comparar movimientos internos bajo una referencia común:

```bash
(echo Backbone; echo Chain_A) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_chain_A.xvg     -tu ns

(echo Backbone; echo Chain_B) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_chain_B.xvg     -tu ns
```

Si cada cadena se ajusta sobre sí misma, se elimina su movimiento relativo respecto del oligómero. Ambas estrategias responden preguntas diferentes y no deben mezclarse en una misma comparación.

### RMSD de la proteína, todas las cadenas juntas

Después de corregir PBC y ajustar la trayectoria:

```bash
(echo Backbone; echo Backbone) |
gmx rms \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -o md_rmsd_protein_all_chains.xvg \
    -tu ns
```

Este RMSD describe el cambio del backbone del conjunto de cadenas respecto de la referencia seleccionada. Puede aumentar por reorganización cuaternaria aunque cada cadena conserve su estructura interna. Por eso conviene compararlo con los RMSD por cadena y con distancias entre centros de masa:

```bash
gmx distance \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -select 'com of group "Chain_A" plus com of group "Chain_B"' \
    -oall chain_A_chain_B_distance.xvg
```
