# Caso: 1 proteína - 1 ligando

Este tutorial describe la preparación, simulación y análisis de un complejo proteína–ligando con **GROMACS 2026.3**. Se supone que el ligando ya está colocado en la pose inicial que se desea estudiar.

Los nombres de archivos son ejemplos. Conviene mantener nombres explícitos y una carpeta por etapa:

```bash
mkdir -p 00_entrada 01_preparacion 02_em 03_nvt 04_npt 05_md 06_analisis
```

## Objetivo y alcance del tutorial

El sistema estudiado contiene una proteína receptora, un ligando, solvente explícito e iones. El objetivo es construir un modelo atomístico consistente, eliminar contactos desfavorables, equilibrarlo y generar un conjunto de conformaciones que permita describir la estabilidad estructural y las interacciones del complejo.

Este procedimiento puede responder preguntas como:

- si una pose permanece estable durante el intervalo simulado;
- qué residuos mantienen contacto con el ligando;
- qué puentes de hidrógeno, contactos hidrofóbicos o interacciones iónicas son persistentes;
- qué regiones de la proteína cambian su movilidad;
- si aparecen reorganizaciones del sitio de unión o entrada de agua.

Una trayectoria aislada no demuestra afinidad, mecanismo de acción ni convergencia termodinámica. Tampoco convierte una pose de docking en una estructura experimental. La afinidad requiere métodos y diseños específicos —por ejemplo FEP, LIE, MM/PBSA o potencial de fuerza media— y réplicas suficientes para estimar incertidumbre.

## Conceptos que deben distinguirse

| Concepto            | Definición operativa                                                                                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Receptor**        | Macromolécula que contiene el sitio de unión. En este tutorial es una proteína soluble.                                                                                                   |
| **Ligando**         | Molécula cuya pose e interacciones con el receptor se estudian. Puede poseer varios estados de protonación, tautómeros o estereoisómeros.                                                 |
| **Pose**            | Posición, orientación y conformación del ligando dentro del sitio de unión.                                                                                                               |
| **Microestado**     | Combinación concreta de protonación, tautomería y, cuando corresponda, estereoquímica. Dos microestados del mismo compuesto son sistemas químicos diferentes para una simulación clásica. |
| **Coordenadas**     | Posiciones atómicas almacenadas en PDB, GRO u otro formato. No contienen por sí solas una descripción completa de las interacciones.                                                      |
| **Topología**       | Conectividad, tipos atómicos, cargas, masas y parámetros que definen cómo se calcula la energía.                                                                                          |
| **Campo de fuerza** | Conjunto de forma funcional y parámetros usado para aproximar la energía potencial.                                                                                                       |
| **Protocolo**       | Secuencia documentada de preparación, minimización, equilibración, producción y análisis.                                                                                                 |
| **Réplica**         | Simulación independiente, normalmente iniciada con velocidades aleatorias diferentes y, si corresponde, otra conformación inicial.                                                        |

Una estructura químicamente correcta requiere coherencia entre coordenadas y topología: mismo número y orden de átomos, mismos nombres de residuos y átomos, misma conectividad, misma carga formal y mismo microestado.

## Modelo físico aproximado

La dinámica molecular clásica integra las ecuaciones de movimiento de Newton:

$$
m_i\frac{d^2\mathbf r_i}{dt^2}
=
\mathbf F_i
=
-\nabla_i U(\mathbf r).
$$

La fuerza sobre cada átomo se obtiene del gradiente de una función de energía potencial. En forma esquemática,

$$
U =
U_{\mathrm{enlaces}}
+U_{\mathrm{ángulos}}
+U_{\mathrm{diedros}}
+U_{\mathrm{impropios}}
+U_{\mathrm{LJ}}
+U_{\mathrm{Coulomb}}
+U_{\mathrm{restricciones}}.
$$

Para un par de átomos, las contribuciones no enlazantes más habituales son

$$
U_{\mathrm{LJ}}(r)
=
4\varepsilon
\left[
\left(\frac{\sigma}{r}\right)^{12}
-
\left(\frac{\sigma}{r}\right)^6
\right]
$$

y

$$
U_{\mathrm{Coulomb}}(r)
=
\frac{1}{4\pi\varepsilon_0\varepsilon_r}
\frac{q_iq_j}{r}.
$$

El término de Lennard-Jones representa de manera aproximada la repulsión de corto alcance y la dispersión. El término electrostático depende de las cargas parciales asignadas por el campo de fuerza. En los campos de fuerza biomoleculares convencionales estas cargas suelen ser fijas: no se modela explícitamente la polarización electrónica inducida.

Las ecuaciones anteriores explican por qué una topología no puede improvisarse a partir de una geometría. Cambiar cargas, tipos atómicos, reglas de combinación o parámetros torsionales cambia la superficie de energía potencial y, por tanto, el sistema que se está simulando.

## Archivos y flujo de información

Los archivos cumplen funciones diferentes:

| Archivo     | Función                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| **PDB/GRO** | Coordenadas, nombres de átomos y residuos; GRO incluye la caja.                                            |
| **TOP/ITP** | Topología y parámetros del sistema.                                                                        |
| **MDP**     | Algoritmo, paso temporal, termostato, barostato, cortes y frecuencia de salida.                            |
| **NDX**     | Grupos de átomos definidos para acoplamiento, restricciones o análisis.                                    |
| **TPR**     | Entrada binaria compilada por **gmx grompp** a partir de coordenadas, topología, MDP y, si se usa, índice. |
| **CPT**     | Estado completo necesario para continuar una simulación.                                                   |
| **XTC/TRR** | Trayectoria; XTC contiene coordenadas comprimidas y TRR puede contener coordenadas, velocidades y fuerzas. |
| **EDR**     | Energías y variables termodinámicas.                                                                       |
| **LOG**     | Registro de parámetros efectivos, rendimiento, advertencias y evolución de la corrida.                     |

El flujo mínimo es:

$$
\text{coordenadas}+\text{topología}+\text{MDP}
\xrightarrow{\texttt{gmx grompp}}
\text{TPR}
\xrightarrow{\texttt{gmx mdrun}}
\text{trayectoria}+\text{energías}+\text{checkpoint}.
$$

**gmx grompp** no es una formalidad: expande directivas del preprocesador, valida parte de la coherencia del sistema y escribe en el TPR los parámetros efectivos. Debe conservarse el archivo MDP procesado generado con **-po** cuando se desea auditar exactamente qué se ejecutó.

## Decisiones previas que no debe tomar GROMACS

Antes de ejecutar **pdb2gmx** deben quedar documentadas:

1. identidad biológica de la estructura, cadenas y ensamblaje oligomérico;
2. residuos o átomos faltantes y método usado para reconstruirlos;
3. conformaciones alternativas retenidas;
4. estados de protonación de residuos titulables;
5. presencia de enlaces disulfuro, metales, cofactores y aguas estructurales;
6. microestado, carga formal y estereoquímica del ligando;
7. origen de la pose inicial;
8. campo de fuerza y modelo de agua;
9. condiciones experimentales que se intentan representar: temperatura, presión, pH y composición salina.

GROMACS puede detectar inconsistencias sintácticas, pero no puede decidir si el tautómero, la pose, el ensamblaje biológico o la química de coordinación elegidos son correctos.

## Etapas y criterios para avanzar

| Etapa        | Finalidad                                      | Criterio mínimo antes de continuar                                   |
| ------------ | ---------------------------------------------- | -------------------------------------------------------------------- |
| Preparación  | Definir composición, microestados y parámetros | Coordenadas y topología coherentes; carga y conectividad verificadas |
| Minimización | Eliminar contactos y fuerzas excesivas         | Sin NaN; fuerza máxima y geometría aceptables                        |
| NVT          | Ajustar temperatura a volumen fijo             | Temperatura estable y estructura sin deformaciones                   |
| NPT          | Ajustar densidad y volumen                     | Densidad y volumen estacionarios; presión media compatible           |
| Producción   | Muestrear el conjunto definido                 | Sin inestabilidad; duración y réplicas justificadas                  |
| Análisis     | Responder preguntas predefinidas               | PBC, ajuste, selección e intervalo documentados                      |

Una etapa no se valida porque el comando terminó sin error. La salida estructural, el log y las variables relevantes deben inspeccionarse antes de usarla como entrada de la etapa siguiente.

## Requisitos básicos

Archivos iniciales:

- **protein.pdb:** estructura de la proteína.
- **ligand.pdb** o **ligand.mol2:** ligando con geometría, estereoquímica, protonación y carga formal revisadas.
- **ligand.itp:** topología del ligando compatible con el campo de fuerza de la proteína.
- **ions.mdp**, **em.mdp**, **nvt.mdp**, **npt.mdp** y **md.mdp:** parámetros de cada etapa.

Antes de procesar la proteína deben revisarse residuos faltantes, conformaciones alternativas, enlaces disulfuro, metales, cofactores, aguas estructurales y estados de protonación. Eliminar automáticamente todos los heteroátomos puede destruir información necesaria.

El ligando debe conservar la pose obtenida por cristalografía, docking u otro procedimiento. Un archivo MOL2 puede contener tipos atómicos y cargas, pero eso no demuestra que sean compatibles con el campo de fuerza seleccionado.

## Unidades utilizadas por GROMACS

| Magnitud                                      | Unidad habitual |
| --------------------------------------------- | --------------- |
| Distancia                                     | nm              |
| Tiempo                                        | ps              |
| Temperatura                                   | K               |
| Presión                                       | bar             |
| Energía                                       | kJ mol⁻¹        |
| Fuerza                                        | kJ mol⁻¹ nm⁻¹   |
| Velocidad                                     | nm ps⁻¹         |
| Constante de fuerza de restricción posicional | kJ mol⁻¹ nm⁻²   |

Equivalencias útiles:

$$
1\ \mathrm{nm}=10\ \text{Å}
$$

$$
1\ \mathrm{ps}=10^{-12}\ \mathrm{s},\qquad
1\ \mathrm{ns}=1000\ \mathrm{ps}
$$

$$
1\ \mathrm{kcal\ mol^{-1}}=4.184\ \mathrm{kJ\ mol^{-1}}
$$

No convierta distancias de Å a nm de forma implícita. Una distancia de corte de 1.0 en un archivo MDP significa 1.0 nm, es decir, 10 Å.

## Preparación del ligando

La protonación debe corresponder al pH y al microentorno que se pretende simular. Añadir hidrógenos con una herramienta de conversión no sustituye esta decisión química.

Conversión básica con Open Babel:

```bash
obabel -ipdb ligand.pdb -omol2 -O ligand.mol2 -h
```

Protonación aproximada a pH 7.4:

```bash
obabel -ipdb ligand.pdb -omol2 -O ligand_pH7.4.mol2 -p 7.4
```

La opción **-p 7.4** predice una forma de protonación. Para moléculas con tautomería, centros ionizables acoplados o metales, el resultado debe verificarse. También deben revisarse carga formal, orden de enlaces y estereoquímica.

GROMACS no parametriza automáticamente moléculas orgánicas arbitrarias. La topología debe obtenerse con una herramienta apropiada para la familia del campo de fuerza:

- CHARMM: parámetros compatibles con CGenFF/CHARMM; SwissParam puede generar una aproximación compatible con CHARMM36 para moléculas pequeñas.
- AMBER: parámetros compatibles con GAFF u otra metodología AMBER.
- OPLS-AA: tipos y cargas consistentes con OPLS.
- GROMOS: parámetros desarrollados bajo las convenciones GROMOS.
- AnteChamber/ACPYPE: tipos GAFF o GAFF2 y cargas parciales AM1-BCC.
- LigParGen: tipos OPLS-AA y cargas parciales CM1A-LBCC.

No deben mezclarse tipos atómicos, reglas de combinación, cargas o términos de CHARMM y AMBER sin una transformación validada. Lamentablemente, la conversión de topologías entre familias de campos de fuerza no es trivial y no puede automatizarse sin riesgo de errores.

### Parametrización del ligando con ACPYPE

**ACPYPE** (*AnteChamber PYthon Parser interfacE*) automatiza la parametrización mediante herramientas de AmberTools y convierte el resultado a formatos utilizables por GROMACS. Para una molécula pequeña ejecuta, en esencia:

1. **Antechamber**, que asigna tipos atómicos GAFF o GAFF2 y cargas parciales;
2. **parmchk2**, que busca parámetros ausentes y genera las adiciones necesarias;
3. **tleap**, que construye la topología y las coordenadas AMBER;
4. la conversión de la topología AMBER al formato de GROMACS.

#### Correspondencia con el campo de fuerza

Los parámetros producidos de esta manera pertenecen a la familia **AMBER**:

| Opción de ACPYPE | Parametrización                                            | Uso previsto                                                                                                         |
| ---------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `-a gaff`        | General Amber Force Field, GAFF                            | Moléculas orgánicas pequeñas dentro de un sistema AMBER compatible.                                                  |
| `-a gaff2`       | General Amber Force Field 2, GAFF2                         | Opción preferente para moléculas pequeñas cuando se utiliza una parametrización AMBER moderna.                       |
| `-a amber`       | Tipos AMBER para residuos reconocidos y GAFF como respaldo | Péptidos o sistemas que pueden compararse con plantillas AMBER; no es la opción habitual para un ligando arbitrario. |
| `-a amber2`      | Tipos AMBER y GAFF2 como respaldo                          | Variante equivalente basada en GAFF2.                                                                                |

La opción **`-o gmx`** solicita archivos con sintaxis de GROMACS; **no convierte GAFF2 en CHARMM, CGenFF, OPLS-AA o GROMOS**. Del mismo modo, que ACPYPE pueda escribir un archivo denominado CHARMM significa que cambia el formato, no que los parámetros hayan sido desarrollados bajo CGenFF.

Una combinación coherente es, por ejemplo:

```text
proteína: AMBER14SB o un port AMBER validado para GROMACS
ligando:  GAFF2 generado mediante ACPYPE/Antechamber
agua:     modelo recomendado para el campo AMBER elegido
```

No mezcle directamente una proteína CHARMM36 con un ligando GAFF2. Las familias pueden diferir en cargas, torsiones, reglas de combinación y factores de escala para interacciones 1–4. Un TPR que compila sin errores no demuestra compatibilidad física.

En los ports AMBER para GROMACS deben conservarse las convenciones AMBER declaradas en `[ defaults ]`, incluidas las reglas de combinación y los factores **fudgeLJ/fudgeQQ**. No copie el bloque `[ defaults ]` de la topología completa de ACPYPE dentro de una topología ya creada por **pdb2gmx**.

#### Instalación reproducible

Una instalación aislada mediante conda puede prepararse con:

```bash
conda create -n acpype -c conda-forge \
    acpype ambertools openbabel

conda activate acpype
acpype -h
antechamber -h
obabel -V
```

Registre las versiones exactas:

```bash
conda list | grep -E 'acpype|ambertools|openbabel'
```

La distribución actual de ACPYPE también puede instalarse mediante `pip` en plataformas para las que existan ruedas con las herramientas de AmberTools incorporadas. La disponibilidad depende del sistema operativo y de la arquitectura; para un protocolo reproducible conviene registrar tanto la versión de ACPYPE como la de AmberTools realmente utilizada.

#### Preparación del archivo de entrada

Para la parametrización es preferible un archivo MOL2 o SDF con:

- orden de enlaces correcto;
- aromaticidad revisada;
- protonación y tautomería definidas;
- estereoquímica correcta;
- coordenadas tridimensionales razonables;
- carga formal conocida.

Un PDB no representa de manera inequívoca órdenes de enlace ni carga formal. Si solo se dispone de PDB, la conversión mediante Open Babel debe revisarse antes de ejecutar ACPYPE:

```bash
obabel ligand.pdb \
    -O LIG.mol2 \
    -h
```

Si se parte de SDF:

```bash
obabel ligand.sdf \
    -O LIG.mol2
```

No use automáticamente **`--gen3d`** sobre una geometría experimental o una pose de docking que se desea conservar. La generación tridimensional crea otra conformación.

#### Ejecución con GAFF2

Para un ligando neutro llamado **LIG**:

```bash
acpype \
    -i LIG.mol2 \
    -b LIG \
    -c abcg2 \
    -n 0 \
    -a gaff2 \
    -o gmx
```

La documentación actual de ACPYPE recomienda **`abcg2`** como método de cargas para GAFF2. El método AM1-BCC clásico puede solicitarse con:

```bash
acpype \
    -i LIG.mol2 \
    -b LIG \
    -c bcc \
    -n 0 \
    -a gaff2 \
    -o gmx
```

No combine cargas generadas mediante métodos diferentes dentro de una misma serie de ligandos si se pretende comparar resultados. El método, la versión de AmberTools y la geometría usada para calcular las cargas forman parte del protocolo.

La opción **`-n`** es la carga neta entera del microestado simulado. Ejemplos:

```bash
# Catión monovalente
acpype -i LIG_plus.mol2 -b LIP -c abcg2 -n 1 -a gaff2 -o gmx

# Anión monovalente
acpype -i LIG_minus.mol2 -b LIM -c abcg2 -n -1 -a gaff2 -o gmx
```

No utilice `-n 0` porque sea el valor del ejemplo. Una carga neta incorrecta cambia todas las cargas parciales y la electrostática del ligando.

Para cargas obtenidas por otro procedimiento cuántico o ajustadas externamente, prepare un MOL2 que ya contenga esas cargas y consulte la opción:

```bash
acpype -i LIG_charged.mol2 -b LIG -c user -n 0 -a gaff2 -o gmx
```

La carga indicada mediante **`-n`** debe coincidir con la suma de las cargas suministradas.

#### Archivos generados

La ejecución crea normalmente el directorio **`LIG.acpype/`**. Entre los archivos relevantes pueden encontrarse:

```text
LIG_GMX.gro       coordenadas para GROMACS
LIG_GMX.itp       tipos, cargas y parámetros del ligando
LIG_GMX.top       topología completa para probar el ligando aislado
LIG_AC.mol2       molécula procesada por Antechamber
LIG_AC.frcmod     parámetros complementarios producidos por parmchk2
```

Los nombres exactos pueden variar entre versiones. Conserve también la salida estándar y los archivos de registro: allí aparecen advertencias de Antechamber, convergencia de cargas y parámetros inferidos por analogía.

#### Validación del resultado

Antes de incorporarlo al complejo, revise:

- suma de cargas parciales y carga neta;
- tipos atómicos asignados;
- orden de enlaces y aromaticidad;
- geometría de anillos, amidas y centros quirales;
- parámetros informados como ausentes o inferidos;
- nombres y orden de átomos entre GRO, MOL2 e ITP;
- energía y geometría después de una minimización corta;
- presencia de fuerzas excesivas, NaN o advertencias de **grompp**.

Prueba independiente del ligando:

```bash
cd LIG.acpype

gmx grompp \
    -f ../em_ligand.mdp \
    -c LIG_GMX.gro \
    -p LIG_GMX.top \
    -pp LIG_processed.top \
    -o LIG_em.tpr

gmx mdrun \
    -deffnm LIG_em \
    -v
```

Una minimización exitosa solo verifica coherencia mecánica básica. No valida cargas, torsiones, estados de protonación ni la capacidad del modelo para reproducir conformaciones o propiedades experimentales.

#### Incorporación en una topología AMBER de proteína–ligando

No incluya **`LIG_GMX.top`** completo dentro de **topol.top**, porque contiene secciones globales que ya existen. Utilice el ITP del ligando y asegúrese de que sus tipos atómicos se definan antes de ser usados.

Esquema conceptual:

```ini
; Campo de fuerza AMBER seleccionado mediante pdb2gmx
#include "amber14sb.ff/forcefield.itp"

; El ITP de ACPYPE puede contener [ atomtypes ]; debe aparecer
; antes de cualquier [ moleculetype ] que use esos tipos.
#include "LIG_GMX.itp"

; Topología de la proteína
#include "topol_Protein.itp"

; Agua e iones compatibles con el campo de fuerza
#include "amber14sb.ff/tip3p.itp"
#include "amber14sb.ff/ions.itp"

[ system ]
Complejo proteína–ligando

[ molecules ]
Protein    1
LIG        1
```

El identificador `amber14sb.ff` es ilustrativo: debe coincidir con el directorio realmente instalado. Si el ITP de ACPYPE contiene `[ atomtypes ]` y se incluye después de la topología de la proteína, **grompp** puede detenerse con un error de orden de directivas. Como alternativa, separe los tipos del ligando en **ligand_atomtypes.itp**, inclúyalos inmediatamente después de **forcefield.itp** y deje las secciones `[ moleculetype ]`, `[ atoms ]`, enlaces, ángulos y diedros en **LIG.itp**.

El orden de `[ molecules ]` debe reproducir el orden de las moléculas en el archivo de coordenadas. El nombre **LIG** debe coincidir exactamente con el valor definido en `[ moleculetype ]`, no solo con el nombre de residuo mostrado en el GRO.

Genere siempre una topología preprocesada para auditar la integración:

```bash
gmx grompp \
    -f em.mdp \
    -c complex.gro \
    -p topol.top \
    -pp complex_processed.top \
    -o complex_em.tpr
```

No use **`-maxwarn`** para ignorar cargas inesperadas, átomos ausentes, directivas fuera de orden o parámetros duplicados.

#### Cuándo ACPYPE no es suficiente

ACPYPE y GAFF2 requieren una revisión adicional o una estrategia diferente para:

- metales coordinados y compuestos organometálicos;
- enlaces covalentes entre ligando y proteína;
- estados electrónicos abiertos;
- moléculas con química poco representada por GAFF2;
- sistemas para los que se necesita compatibilidad estricta con CHARMM/CGenFF, OPLS o GROMOS;
- torsiones críticas que deben validarse contra cálculos cuánticos;
- transformaciones alquímicas donde la correspondencia atómica y la topología híbrida requieren construcción específica.

Para una proteína parametrizada con CHARMM36, use una ruta CGenFF compatible. Para OPLS-AA o GROMOS, emplee parámetros desarrollados y validados bajo las convenciones respectivas. Convertir el archivo final a sintaxis de GROMACS no resuelve la incompatibilidad entre familias.

### Alternativa: parametrización con SwissParam para CHARMM36

[SwissParam](https://www.swissparam.ch/) es una alternativa práctica para obtener parámetros de moléculas orgánicas pequeñas en sistemas que utilizan la familia **CHARMM**. La salida actual está orientada, de manera predeterminada, a **CHARMM36** y contiene archivos preparados para GROMACS.

Esta ruta es alternativa a ACPYPE, no una etapa posterior:

| Sistema de la proteína | Ruta coherente para el ligando | No combinar directamente |
| --- | --- | --- |
| AMBER, por ejemplo AMBER14SB | ACPYPE/Antechamber con GAFF2 | SwissParam/CHARMM36 |
| CHARMM36 | SwissParam o una parametrización CGenFF validada | ACPYPE/GAFF2 |

SwissParam produce parámetros compatibles con las convenciones de CHARMM36, pero una asignación automática por analogía no equivale a una parametrización exhaustivamente validada. Para ligandos con torsiones críticas, cargas inusuales, metales, estados electrónicos especiales o química poco representada se requiere una revisión más profunda, idealmente frente a cálculos cuánticos y datos experimentales.

#### Preparación del MOL2

El archivo MOL2 enviado a SwissParam debe contener **todos los hidrógenos**. Antes del envío deben verificarse:

- estado de protonación y tautomería;
- carga formal;
- órdenes de enlace y aromaticidad;
- estereoquímica;
- nombres atómicos únicos;
- geometría tridimensional razonable.

Si se parte de una pose de docking o de una estructura experimental, conserve esa geometría:

```bash
obabel ligand.sdf \
    -O LIG.mol2
```

Si el archivo carece de hidrógenos:

```bash
obabel ligand.sdf \
    -O LIG.mol2 \
    -h
```

No utilice `--gen3d` cuando necesite preservar una pose. La protonación agregada automáticamente debe revisarse; Open Babel no sustituye la asignación química del microestado.

SwissParam también acepta MOL2 generado con ChimeraX o proveniente de una base de datos química. Abra el archivo final y compruebe que las secciones `@<TRIPOS>ATOM` y `@<TRIPOS>BOND` representen correctamente la molécula.

#### Uso mediante la interfaz web

1. Envíe `LIG.mol2` a [SwissParam](https://www.swissparam.ch/).
2. Descargue el archivo de resultados.
3. Descomprímalo en un directorio separado:

```bash
mkdir -p swissparam_LIG
tar -xzf results.tar.gz -C swissparam_LIG
find swissparam_LIG -maxdepth 2 -type f -print
```

Para GROMACS, los archivos centrales son normalmente:

```text
lig.pdb    coordenadas del ligando con hidrógenos
lig.itp    tipos, cargas y parámetros del ligando
```

Los nombres pueden variar; compruebe el contenido en lugar de renombrar archivos a ciegas.

#### Uso desde la línea de comandos

SwissParam expone un servicio HTTP. Para una molécula pequeña no covalente:

```bash
curl -fsS \
    -F "myMol2=@LIG.mol2" \
    "https://www.swissparam.ch:8443/startparam?approach=both"
```

El servidor devuelve un número de sesión. Sustituya `NUMERO_DE_SESION` en los comandos siguientes:

```bash
curl -fsS \
    "https://www.swissparam.ch:8443/checksession?sessionNumber=NUMERO_DE_SESION"
```

Cuando el cálculo haya finalizado:

```bash
curl -fL \
    "https://www.swissparam.ch:8443/retrievesession?sessionNumber=NUMERO_DE_SESION" \
    -o LIG_swissparam.tar.gz

mkdir -p swissparam_LIG

tar -xzf LIG_swissparam.tar.gz -C swissparam_LIG
```

El argumento `approach` puede ser `both`, `mmff-based` o `match`. En este tutorial se mantiene el valor general `both`. No agregue las opciones `c22` o `c27`: solicitan convenciones CHARMM antiguas y dejarían de ser coherentes con una proteína preparada con CHARMM36.

El envío mediante web o `curl` transfiere la estructura del ligando a un servidor externo. Esto debe considerarse si la molécula está sujeta a confidencialidad.

#### Preparación coherente de la proteína

Prepare la proteína con la versión de CHARMM36 instalada y documentada en el entorno:

```bash
gmx pdb2gmx \
    -f protein.pdb \
    -o protein_processed.gro \
    -p topol.top \
    -i posre_protein.itp \
    -ff charmm36-jul2022 \
    -water tip3p
```

`charmm36-jul2022` es un ejemplo de identificador. Use el nombre real del directorio `.ff` instalado. No seleccione AMBER, OPLS-AA o GROMOS para la proteína cuando el ligando proviene de SwissParam/CHARMM36.

Deben mantenerse también el modelo de agua y los parámetros de iones distribuidos con el campo CHARMM seleccionado. No copie una sección `[ defaults ]` adicional desde otra topología.

#### Integración del ligando en `topol.top`

El archivo `lig.itp` de SwissParam puede contener `[ atomtypes ]` y `[ pairtypes ]`. Estas directivas deben aparecer antes de cualquier `[ moleculetype ]`. Por ello, el ITP del ligando debe incluirse inmediatamente después de `forcefield.itp` y antes de la topología de la proteína:

```ini
; Parámetros globales de CHARMM36
#include "charmm36-jul2022.ff/forcefield.itp"

; SwissParam: puede definir atomtypes y pairtypes
#include "lig.itp"

; Topología generada para la proteína
#include "topol_Protein.itp"

; Agua e iones del mismo campo de fuerza
#include "charmm36-jul2022.ff/tip3p.itp"
#include "charmm36-jul2022.ff/ions.itp"

[ system ]
Complejo proteína–ligando con CHARMM36

[ molecules ]
Protein    1
LIG        1
```

El nombre `LIG` debe coincidir exactamente con el valor definido en `[ moleculetype ]` dentro de `lig.itp`. No lo deduzca únicamente del nombre de residuo del PDB.

Si hay agua, la línea del ligando debe preceder a `SOL`:

```ini
[ molecules ]
Protein    1
LIG        1
SOL        12543
```

Para varios ligandos SwissParam no deben incluirse varios ITP completos de forma secuencial si cada uno contiene sus propios bloques `[ atomtypes ]` y `[ pairtypes ]`. Separe o combine primero todos los tipos y pares en un archivo incluido antes de cualquier `[ moleculetype ]`; mantenga después una topología molecular por especie.

#### Incorporación de las coordenadas

Use el `lig.pdb` producido por SwissParam porque sus nombres y orden atómicos corresponden al ITP. Compruebe que la geometría siga representando la pose seleccionada. Si necesita transferir coordenadas desde otra pose, la correspondencia debe hacerse por identidad atómica, no por número de línea.

La construcción del complejo debe seguir la estrategia general de este tutorial:

1. proteína procesada con `pdb2gmx`;
2. ligando con nombres y orden compatibles con `lig.itp`;
3. proteína antes que ligando si ese es el orden de `[ molecules ]`;
4. inspección visual del sitio de unión;
5. solvatación e incorporación posterior de iones.

No utilice `gmx insert-molecules` para reinsertar un ligando ya posicionado en el sitio de unión: esa operación puede cambiar la colocación que se pretende conservar.

#### Restricciones de posición y validación

SwissParam puede proporcionar restricciones controladas mediante `POSRES_LIGAND`. Si el ITP contiene ese bloque y se desean restricciones para proteína y ligando:

```ini
define = -DPOSRES -DPOSRES_LIGAND
```

Los nombres de las macros deben verificarse en los ITP; no suponga que todos los paquetes de salida contienen exactamente el mismo bloque.

Antes de solvatar el sistema, genere una topología preprocesada:

```bash
gmx grompp \
    -f em.mdp \
    -c complex.gro \
    -p topol.top \
    -pp complex_processed.top \
    -o complex_em.tpr
```

Revise:

- carga total del ligando y del sistema;
- correspondencia entre átomos de `lig.pdb` y `lig.itp`;
- ausencia de tipos o parámetros duplicados;
- orden de las directivas en `complex_processed.top`;
- geometría del ligando después de una minimización;
- fuerzas máximas, enlaces, ángulos y torsiones críticas.

No use `-maxwarn` para ocultar errores de orden, cargas inesperadas o parámetros duplicados. Una minimización exitosa demuestra consistencia mecánica básica, no calidad química suficiente.

Documentación utilizada:

- [SwissParam: integración con GROMACS](https://www.swissparam.ch/howto_gromacs.php)
- [SwissParam: uso desde la línea de comandos](https://www.swissparam.ch/command-line.php)
- [SwissParam: preparación correcta de archivos MOL2](https://www.swissparam.ch/howto_mol2.php)

Ejemplo mínimo de un archivo ITP:

```ini
[ moleculetype ]
; nombre   nrexcl
LIG        3

[ atoms ]
; nr  type  resnr  residuo  átomo  cgnr  carga  masa
1     CG2R61  1     LIG      C1     1     0.12   12.011
2     NG2R50  1     LIG      N1     2    -0.32   14.007
; ...
```

Las líneas iniciadas por punto y coma son comentarios. El nombre definido en `[ moleculetype ]` debe coincidir exactamente con el utilizado en `[ molecules ]`. La suma de las cargas parciales debe reproducir la carga formal esperada dentro de la precisión numérica del modelo.

El valor de **nrexcl** depende de la convención del campo de fuerza. No debe cambiarse solo para eliminar errores de preprocesamiento.

## Preparación de la proteína

Ejecute **pdb2gmx** sobre una copia de la estructura original:

```bash
cd 01_preparacion

gmx pdb2gmx -f ../00_entrada/protein.pdb \
            -o protein_processed.gro \ 
            -p topol.top \
            -i posre_protein.itp \ 
            -water tip3p
```

Seleccione el campo de fuerza de manera interactiva o especifíquelo mediante **-ff** si el identificador instalado está documentado:

```bash
gmx pdb2gmx -f ../00_entrada/protein.pdb \
            -o protein_processed.gro \
            -p topol.top \
            -i posre_protein.itp \
            -ff charmm36-jul2022 \
            -water tip3p
```

El nombre disponible puede diferir según los campos de fuerza instalados. Consulte:

```bash
gmx pdb2gmx -h
```

Evite **-ignh** como opción automática: descarta los hidrógenos presentes y los regenera según las plantillas del campo de fuerza. Puede ser útil, pero también elimina estados de protonación definidos previamente.

Compruebe la estructura:

```bash
gmx check -f protein_processed.gro
```

Revise en la salida de **pdb2gmx**:

- residuos y átomos no reconocidos;
- carga total de la proteína;
- enlaces disulfuro;
- terminales asignados;
- histidinas y otros residuos titulables;
- moléculas separadas por cadena.

## Construcción del complejo

Las coordenadas finales deben contener primero la proteína y después el ligando si ese es el orden declarado en la topología. No concatene directamente dos archivos GRO completos: cada uno contiene título, número de átomos y caja.

Use un editor molecular o un script validado para combinar las coordenadas sin alterar la pose. Después inspeccione el complejo visualmente y descarte solapamientos.

En **topol.top**, incluya la topología del ligando después de los parámetros generales del campo de fuerza y antes de las topologías de agua e iones:

```ini
; Parámetros generales
#include "charmm36-jul2022.ff/forcefield.itp"

; Tipos o parámetros adicionales del ligando, si existen
#include "ligand_atomtypes.itp"

; Topología molecular del ligando
#include "ligand.itp"

; Topología de la proteína generada por pdb2gmx
#include "topol_Protein_chain_A.itp"
```

Una sección `[ atomtypes ]` debe aparecer antes de cualquier `[ moleculetype ]` que utilice esos tipos. No incluya el mismo bloque de tipos atómicos más de una vez.

Al final de **topol.top**:

```ini
[ system ]
Complejo proteína–ligando

[ molecules ]
; molécula          cantidad
Protein_chain_A     1
LIG                 1
```

El orden en `[ molecules ]` debe coincidir con el orden de las moléculas en el archivo de coordenadas. La cantidad representa moléculas, no átomos ni residuos.

## Caja periódica

Para una proteína soluble aproximadamente globular, una caja dodecaédrica reduce el número de moléculas de agua respecto de una caja cúbica:

```bash
gmx editconf -f complex.gro \
    -o complex_box.gro \
    -c \
    -d 1.0 \
    -bt dodecahedron
```

**-d 1.0** establece una distancia mínima de 1.0 nm entre el soluto y el límite de la caja. No es una constante universal. Debe ser compatible con los radios de corte y con los movimientos esperados del sistema.

Compruebe el volumen y los vectores de caja:

```bash
gmx editconf -f complex_box.gro
```

## Solvatación

```bash
gmx solvate -cp complex_box.gro \
            -cs spc216.gro \
            -o complex_solv.gro \
            -p topol.top
```

El nombre **spc216.gro** identifica una configuración preequilibrada distribuida con GROMACS. La topología final del agua está determinada por el modelo elegido en **pdb2gmx**, por lo que debe mantenerse la compatibilidad entre campo de fuerza, archivo de agua y topología.

**gmx solvate** actualiza automáticamente el número de moléculas de solvente en **topol.top**. Revise la sección `[ molecules ]` después del comando.

## Neutralización y concentración salina

Archivo **ions.mdp** mínimo:

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

Genere un TPR temporal:

```bash
gmx grompp -f ions.mdp -c complex_solv.gro -p topol.top -o ions.tpr
```

Añada NaCl, neutralice la carga neta y solicite una concentración nominal de 0.15 mol L⁻¹:

```bash
gmx genion -s ions.tpr -o complex_solv_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15
```

Seleccione el grupo de solvente, normalmente **SOL**, cuando el programa pregunte qué moléculas reemplazar. No use un número de grupo copiado de otro sistema.

Vayamos un poco al tema de los "grupos". Es un concepto que GROMACS utiliza para organizar átomos y moléculas en conjuntos. Por ejemplo, cuando se le pide al usuario que seleccione un grupo de solvente, GROMACS muestra una lista de grupos predefinidos (como SOL, Protein, LIG, etc.) y el usuario debe elegir el grupo correspondiente al solvente que desea reemplazar con iones. En los archivos de topología, los grupos se definen en la sección `[ molecules ]`, y cada grupo tiene un número de identificación que GROMACS utiliza internamente. Por eso es importante no copiar números de grupo de otros sistemas, ya que pueden no coincidir con la estructura actual.

La concentración se relaciona con el número de pares iónicos mediante:

$$
N_{\mathrm{pares}} \approx c\,N_A\,V
$$

donde **c** es la concentración en mol L⁻¹, $N_A$ es la constante de Avogadro y **V** es el volumen en litros. Debido a que el número de iones debe ser entero y la caja es pequeña, la concentración efectiva puede diferir del valor solicitado.

La opción **-neutral** agrega los contraiones necesarios para llevar la carga neta a cero. **-conc 0.15** agrega además la sal correspondiente a la concentración solicitada. Revise la cantidad final de NA y CL en **topol.top**.

Concentración de sal y fuerza iónica no son siempre equivalentes. La fuerza iónica se define como

$$
I=\frac{1}{2}\sum_i c_i z_i^2,
$$

donde $c_i$ es la concentración molar de la especie iónica $i$ y $z_i$ su número de carga. Para NaCl ideal, 0.15 mol L⁻¹ corresponde aproximadamente a $I=0.15$ mol L⁻¹. La presencia de contraiones añadidos para neutralizar una proteína cargada modifica la composición y la fuerza iónica efectiva; el efecto es más visible en cajas pequeñas o con solutos muy cargados.

## Grupos de índice

Los números de grupo cambian con la composición del sistema. Cree los grupos necesarios y documente las selecciones:

```bash
gmx make_ndx -f complex_solv_ions.gro -o index.ndx
```

Ejemplo interactivo:

```text
r LIG
"Protein" | "LIG"
name 18 Protein_LIG
q
```

El número 18 es ilustrativo: debe reemplazarse por el número asignado durante esa sesión. El grupo **Protein_LIG** resulta útil para centrar y visualizar el complejo, pero no crea una única molécula física. "Interactivo" significa que el usuario escribe comandos en la terminal; no es un script automático. La salida **index.ndx** contiene los grupos de índice y puede editarse con un editor de texto. Se puede "automatizar"? Es posible, pero la interacción permite verificar que los grupos creados coincidan con lo esperado. Si tuvieramos mucha seguridad de los índices de los átomos, podríamos crear un script que genere el archivo de índice directamente, pero la revisión visual es una buena práctica para evitar errores. Si supiéramos exactamente como se llama el grupo que queremos, podríamos usar una modificación de la línea de comandos para crear el grupo sin interacción, ejemplo:

```bash
echo "r LIG" | gmx make_ndx -f complex_solv_ions.gro -o index.ndx
```

ó

```bash
echo -e "r LIG\nname 18 Protein_LIG\nq" | gmx make_ndx -f complex_solv_ions.gro -o index.ndx
```

el "-e" permite interpretar los saltos de línea. Pero la interacción permite verificar que los grupos creados coincidan con lo esperado.

Puede examinar selecciones modernas con:

```bash
gmx select -s complex_solv_ions.gro -select 'group "Protein" or resname LIG'
```

## Restricciones de posición del ligando

Genere las restricciones usando una estructura que contenga solamente el ligando y cuyo orden atómico coincida con **ligand.itp**:

```bash
gmx genrestr -f ligand.gro -o posre_ligand.itp -fc 1000 1000 1000
```

Seleccione **LIG**. Los índices del archivo de restricciones son locales al `[ moleculetype ]`. Si se usa la estructura completa y se generan índices globales, las restricciones pueden apuntar a átomos incorrectos. **-fc** define la fuerza de restricción en cada eje. El valor 1000 corresponde a 1000 kJ mol⁻¹ nm⁻². Cuanto mayor sea la constante de fuerza, más rígida será la restricción. La fuerza de restricción debe ser suficiente para mantener el ligando en su sitio durante la equilibración, pero no tan alta como para generar fuerzas excesivas o artefactos.

Incluya el archivo inmediatamente después de la topología del ligando:

```ini
#include "ligand.itp"

#ifdef POSRES_LIG
#include "posre_ligand.itp"
#endif
```

El valor 1000 corresponde a 1000 kJ mol⁻¹ nm⁻² en cada eje. La energía armónica de una restricción unidimensional es:

$$
V(x)=\frac{1}{2}k(x-x_0)^2
$$

donde **k** es la constante de fuerza y $x_0$ la posición de referencia.

Active las restricciones desde el MDP:

```ini
define = -DPOSRES -DPOSRES_LIG
```

El archivo indicado mediante **gmx grompp -r** proporciona las coordenadas de referencia. Las restricciones se usan normalmente durante la equilibración y se eliminan en producción.

## Minimización de energía

Archivo **em.mdp**:

```ini
title            = Minimización de energía
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

Preprocese y ejecute:

```bash
mkdir -p ../02_em
cd ../02_em

gmx grompp -f ../01_preparacion/em.mdp \
    -c ../01_preparacion/complex_solv_ions.gro \
    -p ../01_preparacion/topol.top \ 
    -o em.tpr

gmx mdrun -deffnm em -v
```

El criterio **emtol = 1000** significa que la minimización puede finalizar cuando la fuerza máxima sea menor que 1000 kJ mol⁻¹ nm⁻¹:

$$
F_{\max}=\max_i\left|-\nabla_i U\right|.
$$

Este valor es habitual antes de equilibrar, pero no garantiza que la estructura represente un mínimo profundo ni que el sistema esté equilibrado. La minimización desplaza coordenadas cuesta abajo sobre la superficie de energía potencial; no genera un conjunto termodinámico y no sustituye NVT o NPT.

Extraiga la energía potencial:

```bash
(echo Potential; echo 0) | gmx energy -f em.edr -o ../06_analisis/em_potential.xvg
```

Compruebe:

- descenso de la energía potencial;
- ausencia de valores NaN;
- fuerza máxima final;
- átomo sobre el cual actúa la fuerza máxima;
- advertencias de LINCS o contactos anómalos.

No use **-maxwarn** para ocultar advertencias de **grompp**. Debe entenderse la causa antes de continuar.

## Equilibración NVT

NVT significa número de partículas, volumen y temperatura fijos. En el conjunto canónico NVT permanecen fijos el número de partículas $N$, el volumen $V$ y la temperatura objetivo $T$. El termostato modifica la dinámica para muestrear la distribución correspondiente; no debe interpretarse como una simple corrección periódica de velocidades. Se usa para estabilizar la temperatura antes de permitir que el volumen fluctúe en NPT.

La probabilidad de un microestado de energía $E$ es proporcional a

$$
P(E)\propto \exp\left(-\frac{E}{k_{\mathrm B}T}\right).
$$

En esta etapa se estabiliza la temperatura manteniendo fijo el volumen. Ejemplo a 300 K durante 100 ps:

```ini
title                    = Equilibración NVT
define                   = -DPOSRES -DPOSRES_LIG

integrator               = md
dt                       = 0.002
nsteps                   = 50000
continuation             = no

gen-vel                  = yes
gen-temp                 = 300
gen-seed                 = -1

constraints              = h-bonds
constraint-algorithm     = lincs

cutoff-scheme            = Verlet
nstlist                  = 20
rlist                    = 1.0
coulombtype              = PME
rcoulomb                 = 1.0
vdwtype                  = Cut-off
rvdw                     = 1.0

tcoupl                   = V-rescale
tc-grps                  = Protein_LIG Water_and_ions
tau-t                    = 1.0 1.0
ref-t                    = 300 300

pcoupl                   = no
pbc                      = xyz

nstxout-compressed       = 500
compressed-x-precision   = 1000
nstenergy                = 500
nstlog                   = 500
```

El tiempo simulado es:

$$
t_{\mathrm{total}}=\mathrm{dt}\times\mathrm{nsteps}
$$

En este ejemplo:

$$
0.002\ \mathrm{ps}\times 50000=100\ \mathrm{ps}
$$

Con restricciones sobre enlaces con hidrógeno, un paso de 0.002 ps equivale a 2 fs.

Ejecución:

```bash
mkdir -p ../03_nvt
cd ../03_nvt

gmx grompp -f ../01_preparacion/nvt.mdp \
    -c ../02_em/em.gro \
    -r ../02_em/em.gro \
    -t ../02_em/em.cpt \
    -p ../01_preparacion/topol.top \
    -n ../01_preparacion/index.ndx \
    -o nvt.tpr

gmx mdrun -deffnm nvt -v
```

Las velocidades se generan una sola vez. Para las etapas posteriores se conserva el estado mediante el checkpoint.

Análisis de temperatura:

```bash
(echo Temperature; echo 0) | gmx energy -f nvt.edr -o ../06_analisis/nvt_temperature.xvg
```

La temperatura debe evaluarse como serie temporal y promedio, no por un único valor final.

## Equilibración NPT

NPT significa número de partículas, presión y temperatura fijos. En el conjunto isotérmico-isobárico NPT permanecen fijos $N$, la temperatura objetivo $T$ y la presión objetivo $P$, mientras el volumen fluctúa. El barostato modifica los vectores de caja y las coordenadas para permitir que la densidad se relaje.

La presión instantánea es una magnitud ruidosa, especialmente en cajas pequeñas. El criterio práctico no es obtener una línea plana en 1 bar, sino comprobar que volumen y densidad alcanzaron un régimen estacionario y que la presión promedio es compatible con el objetivo dentro de su incertidumbre.

Ejemplo de 500 ps con barostato C-rescale:

```ini
title                    = Equilibración NPT
define                   = -DPOSRES -DPOSRES_LIG

integrator               = md
dt                       = 0.002
nsteps                   = 250000
continuation             = yes
gen-vel                  = no

constraints              = h-bonds
constraint-algorithm     = lincs

cutoff-scheme            = Verlet
nstlist                  = 20
rlist                    = 1.0
coulombtype              = PME
rcoulomb                 = 1.0
vdwtype                  = Cut-off
rvdw                     = 1.0

tcoupl                   = V-rescale
tc-grps                  = Protein_LIG Water_and_ions
tau-t                    = 1.0 1.0
ref-t                    = 300 300

pcoupl                   = C-rescale
pcoupltype               = isotropic
tau-p                    = 5.0
ref-p                    = 1.0
compressibility          = 4.5e-5

pbc                      = xyz

nstxout-compressed       = 500
compressed-x-precision   = 1000
nstenergy                = 500
nstlog                   = 500
```

**ref-p = 1.0** significa 1 bar. **compressibility = 4.5e-5 bar⁻¹** es un valor habitual para agua líquida cerca de condiciones ambientales; debe adaptarse si el medio no es agua.

Ejecución:

```bash
mkdir -p ../04_npt
cd ../04_npt

gmx grompp -f ../01_preparacion/npt.mdp \
    -c ../03_nvt/nvt.gro \
    -r ../03_nvt/nvt.gro \
    -t ../03_nvt/nvt.cpt \
    -p ../01_preparacion/topol.top \
    -n ../01_preparacion/index.ndx \
    -o npt.tpr

gmx mdrun -deffnm npt -v
```

Extraiga presión y densidad:

```bash
(echo Pressure; echo Density; echo 0) |
gmx energy -f npt.edr -o ../06_analisis/npt_pressure_density.xvg
```

La presión instantánea fluctúa mucho en sistemas pequeños. Evalúe promedios por bloques, densidad y volumen. Si existe una deriva sistemática, prolongue la equilibración desde el checkpoint.

## Dinámica molecular de producción

Durante producción se retiran las restricciones posicionales, salvo que formen parte explícita del protocolo. El siguiente MDP describe 100 ns:

```ini
title                    = Producción NPT

integrator               = md
dt                       = 0.002
nsteps                   = 50000000
continuation             = yes
gen-vel                  = no

constraints              = h-bonds
constraint-algorithm     = lincs

cutoff-scheme            = Verlet
nstlist                  = 20
rlist                    = 1.0
coulombtype              = PME
rcoulomb                 = 1.0
vdwtype                  = Cut-off
rvdw                     = 1.0

tcoupl                   = V-rescale
tc-grps                  = Protein_LIG Water_and_ions
tau-t                    = 1.0 1.0
ref-t                    = 300 300

pcoupl                   = Parrinello-Rahman
pcoupltype               = isotropic
tau-p                    = 5.0
ref-p                    = 1.0
compressibility          = 4.5e-5

pbc                      = xyz

nstxout-compressed       = 5000
compressed-x-precision   = 1000
nstenergy                = 5000
nstlog                   = 5000
```

Con 2 fs por paso:

$$
50000000\times 0.002\ \mathrm{ps}
=100000\ \mathrm{ps}
=100\ \mathrm{ns}
$$

Ejecución:

```bash
mkdir -p ../05_md
cd ../05_md

gmx grompp \
    -f ../01_preparacion/md.mdp \
    -c ../04_npt/npt.gro \
    -t ../04_npt/npt.cpt \
    -p ../01_preparacion/topol.top \
    -n ../01_preparacion/index.ndx \
    -o md.tpr

gmx mdrun -deffnm md -v
```

Archivos principales:

| Archivo    | Contenido                                                                    |
| ---------- | ---------------------------------------------------------------------------- |
| **md.tpr** | Topología, parámetros, coordenadas y estado de entrada.                      |
| **md.xtc** | Coordenadas comprimidas.                                                     |
| **md.edr** | Energías y variables termodinámicas.                                         |
| **md.log** | Registro detallado de la ejecución.                                          |
| **md.cpt** | Checkpoint para continuar.                                                   |
| **md.gro** | Coordenadas finales.                                                         |
| **md.trr** | Coordenadas, velocidades o fuerzas en precisión completa, si se solicitaron. |

No es necesario generar TRR si el análisis no requiere velocidades, fuerzas o coordenadas de precisión completa.

## Continuación y extensión

Para reanudar una ejecución interrumpida:

```bash
gmx mdrun -deffnm md -cpi md.cpt -append
```

**-append** verifica y continúa los archivos existentes. Use **-noappend** solo cuando necesite segmentos separados.

Si el TPR agotó el número de pasos, extiéndalo. **-extend** se expresa en picosegundos:

```bash
gmx convert-tpr     -s md.tpr     -extend 50000     -o md_extended.tpr

gmx mdrun     -s md_extended.tpr     -deffnm md     -cpi md.cpt     -append
```

Aquí se agregan 50000 ps, equivalentes a 50 ns.

Concatenación de segmentos XTC:

```bash
gmx trjcat     -f md.part0001.xtc md.part0002.xtc     -o md_complete.xtc
```

Revise el orden y los tiempos. La concatenación no corrige superposiciones temporales ni discontinuidades físicas.

## Corrección de condiciones periódicas

Las condiciones periódicas pueden separar visualmente moléculas que continúan próximas. No existe una única secuencia válida para todos los sistemas. Para un complejo soluble:

```bash
echo System |
gmx trjconv     -s md.tpr     -f md.xtc     -o md_whole.xtc     -pbc whole
```

Trayectoria sin saltos, útil para difusión:

```bash
echo System |
gmx trjconv     -s md.tpr     -f md_whole.xtc     -o md_nojump.xtc     -pbc nojump
```

Centre el complejo y lleve las moléculas a una caja compacta:

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

Elimine rotación y traslación ajustando el backbone:

```bash
(echo Backbone; echo System) |
gmx trjconv     -s md.tpr     -f md_center.xtc     -o md_fit.xtc     -fit rot+trans     -n index.ndx
```

El orden importa: no aplique **-pbc nojump** después de centrar. Inspeccione visualmente la trayectoria final.

Extracción de una estructura a 50 ns:

```bash
echo Protein_LIG |
gmx trjconv \
    -s md.tpr \
    -f md_fit.xtc \
    -o frame_50ns.pdb \
    -dump 50 \
    -tu ns \
    -n index.ndx
```

## Análisis de resultados

Use el mismo intervalo de producción, tratamiento de PBC y selección en todas las réplicas. Los archivos XVG son texto y pueden analizarse con Grace, Python, R u otro programa.

### RMSD

El RMSD mide la desviación respecto de una referencia después del ajuste:

$$
\mathrm{RMSD}(t)=
\sqrt{\frac{1}{M}\sum_i m_i
\left\|\mathbf r_i(t)-\mathbf r_i^{\mathrm{ref}}\right\|^2}
$$

donde **M** es la masa total de los átomos seleccionados. Una meseta indica estabilidad relativa frente a esa referencia, no convergencia termodinámica.

```bash
mkdir -p ../06_analisis/rmsd

(echo Backbone; echo Backbone) |
gmx rms \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -o ../06_analisis/rmsd/rmsd_backbone.xvg \
    -tu ns
```

RMSD del ligando después de ajustar la proteína:

```bash
(echo Backbone; echo LIG) |
gmx rms \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -o ../06_analisis/rmsd/rmsd_ligand_fit_protein.xvg \
    -tu ns
```

### Radio de giro

```bash
gmx gyrate \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -sel 'group "Protein"' \
    -o ../06_analisis/gyrate_protein.xvg
```

El radio de giro informa sobre la compacidad global. Debe interpretarse junto con RMSD, estructura secundaria y contactos internos.

### Distancias y contactos proteína–ligando

Distancia entre el centro geométrico del ligando y un átomo de referencia:

```bash
gmx distance \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -select 'com of group "LIG" plus com of resid 123 and name CA' \
    -oall ../06_analisis/dist_lig_res123.xvg
```

El residuo 123 es un ejemplo y debe reemplazarse. Para distancia mínima y número de contactos:

```bash
(echo Protein; echo LIG) |
gmx mindist \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -od ../06_analisis/mindist_protein_lig.xvg \
    -on ../06_analisis/contacts_protein_lig.xvg \
    -d 0.4
```

**-d 0.4** establece un umbral de contacto de 0.4 nm, equivalente a 4 Å. Debe informarse el umbral utilizado.

### Puentes de hidrógeno

GROMACS 2026 incluye la implementación moderna de **gmx hbond**, incorporada inicialmente en GROMACS 2024:

```bash
gmx hbond \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -r 'group "Protein"' \
    -t 'group "LIG"' \
    -num ../06_analisis/hbonds_protein_lig.xvg
```

Las selecciones de referencia y objetivo deben ser idénticas o no solaparse. Los valores recomendados por la herramienta son 0.35 nm para distancia y 30 grados para el criterio angular. Si se modifican, deben reportarse.

### Contactos iónicos

Un contacto corto entre grupos cargados puede estudiarse mediante selecciones explícitas:

```bash
gmx pairdist \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -ref 'group "Protein_charged"' \
    -sel 'group "LIG_charged"' \
    -type min \
    -o ../06_analisis/ion_pairs.xvg
```

Los grupos **Protein_charged** y **LIG_charged** deben construirse previamente según los átomos efectivamente cargados. Una distancia corta no demuestra por sí sola una interacción energéticamente favorable.

### Área accesible al solvente

```bash
gmx sasa \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -surface 'group "Protein_LIG"' \
    -output 'group "Protein_LIG"' \
    -o ../06_analisis/sasa_complex.xvg \
    -or ../06_analisis/sasa_per_residue.xvg
```

SASA depende de la selección, los radios atómicos y la sonda. Una disminución del área expuesta del ligando puede acompañar su enterramiento, pero no equivale a energía de unión.

### Variables termodinámicas

```bash
(echo Temperature; echo Pressure; echo Density; echo Volume; echo Potential; echo 0) |
gmx energy     -f md.edr     -o ../06_analisis/thermodynamics.xvg
```

Los nombres disponibles dependen del contenido de EDR. Evalúe promedios por bloques y deriva temporal. La presión instantánea suele presentar fluctuaciones grandes.

### Desplazamiento cuadrático medio

**gmx msd** usa selecciones modernas:

```bash
gmx msd \
    -s md.tpr \
    -f md_nojump.xtc \
    -n index.ndx \
    -sel 'group "LIG"' \
    -o ../06_analisis/msd_ligand.xvg
```

Difusión lateral en el plano XY:

```bash
gmx msd \
    -s md.tpr \
    -f md_nojump.xtc \
    -n index.ndx \
    -sel 'group "LIG"' \
    -lateral z \
    -o ../06_analisis/msd_ligand_xy.xvg
```

La estimación del coeficiente de difusión se basa en la región lineal de la relación de Einstein:

$$
\left\langle |\mathbf r(t)-\mathbf r(0)|^2\right\rangle=2dDt
$$

donde **d** es la dimensionalidad: 3 para difusión tridimensional y 2 para difusión lateral. Debe elegirse un intervalo de ajuste en el régimen difusivo; el tramo inicial balístico y las regiones con muestreo insuficiente sesgan el resultado.

### Mapas de densidad

```bash
echo LIG |
gmx densmap \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -od ../06_analisis/density_ligand.xpm \
    -aver z
```

El sistema debe estar alineado previamente. Informe el eje promediado, la resolución de la grilla y la selección.

### Fluctuación de los residuos

La RMSF mide la fluctuación de cada átomo alrededor de su posición promedio:

$$
\mathrm{RMSF}_i=
\sqrt{
\left\langle
\left\|\mathbf r_i(t)-\langle\mathbf r_i\rangle\right\|^2
\right\rangle}
$$

Primero ajuste la trayectoria sobre una región estructuralmente estable:

```bash
mkdir -p ../06_analisis/rmsf

echo Backbone |
gmx trjconv \
    -s md.tpr \
    -f md_center.xtc \
    -o ../06_analisis/rmsf/md_fit_backbone.xtc \
    -fit rot+trans \
    -n index.ndx
```

Calcule RMSF por residuo usando C-alpha:

```bash
echo C-alpha |
gmx rmsf \
    -s md.tpr \
    -f ../06_analisis/rmsf/md_fit_backbone.xtc \
    -n index.ndx \
    -o ../06_analisis/rmsf/rmsf_calpha.xvg \
    -res \
    -oq ../06_analisis/rmsf/rmsf_calpha_bfactor.pdb
```

**-oq** escribe los valores convertidos al campo B del PDB. La relación isotrópica es:

$$
B_i=\frac{8\pi^2}{3}\mathrm{RMSF}_i^2
$$

Para evaluar estabilidad temporal, compare bloques de igual duración:

```bash
echo C-alpha |
gmx rmsf \
    -s md.tpr \
    -f ../06_analisis/rmsf/md_fit_backbone.xtc \
    -n index.ndx \
    -b 20 \
    -e 40 \
    -tu ns \
    -res \
    -o ../06_analisis/rmsf/rmsf_20_40ns.xvg

echo C-alpha |
gmx rmsf \
    -s md.tpr \
    -f ../06_analisis/rmsf/md_fit_backbone.xtc \
    -n index.ndx \
    -b 40 \
    -e 60 \
    -tu ns \
    -res \
    -o ../06_analisis/rmsf/rmsf_40_60ns.xvg
```

Picos persistentes suelen corresponder a terminales, bucles o regiones expuestas. Cambios localizados cerca del sitio de unión pueden sugerir estabilización o reorganización, pero deben contrastarse con contactos, estructura secundaria, RMSD y réplicas independientes.

No compare RMSF obtenidas con distinta alineación, selección, duración o intervalo temporal.

## Control de calidad y reproducibilidad

Conserve:

- versión exacta de GROMACS y salida de **gmx --version**;
- estructuras iniciales y decisiones de protonación;
- campo de fuerza, modelo de agua y método de parametrización del ligando;
- archivos MDP, TOP, ITP y NDX;
- TPR, checkpoints y registros;
- comandos ejecutados;
- semillas y configuración de hardware;
- intervalo y selección utilizados en cada análisis.

Use réplicas independientes cuando la conclusión dependa del muestreo. RMSD, RMSF, contactos, puentes de hidrógeno y distancias no son estimaciones directas de afinidad ni energía libre de unión.

## Fuentes

1. [Formatos de archivo de GROMACS 2026.3](https://manual.gromacs.org/current/reference-manual/file-formats.html)
2. [Topologías de GROMACS](https://manual.gromacs.org/current/reference-manual/topologies/topologies.html)
3. [Manual de análisis](https://manual.gromacs.org/current/reference-manual/analysis/analysis.html)
4. [Opciones de archivos MDP](https://manual.gromacs.org/current/user-guide/mdp-options.html)
5. [Referencia de comandos de GROMACS](https://manual.gromacs.org/current/onlinehelp/gmx.html)
6. [Flujo general de una simulación en GROMACS](https://manual.gromacs.org/current/user-guide/flow.html)
7. [Definiciones y unidades](https://manual.gromacs.org/current/reference-manual/definitions.html)
8. [Dinámica molecular](https://manual.gromacs.org/current/reference-manual/algorithms/molecular-dynamics.html)
9. [Condiciones periódicas de contorno](https://manual.gromacs.org/current/reference-manual/algorithms/periodic-boundary-conditions.html)
10. [Algoritmos de restricciones](https://manual.gromacs.org/current/reference-manual/algorithms/constraint-algorithms.html)
11. [Documentación oficial de ACPYPE](https://alanwilter.github.io/acpype/)
12. [Repositorio oficial de ACPYPE](https://github.com/alanwilter/acpype)
13. [Sousa da Silva y Vranken, ACPYPE — AnteChamber PYthon Parser interfacE](https://doi.org/10.1186/1756-0500-5-367)
14. [Wang et al., Development and testing of a General Amber Force Field](https://doi.org/10.1002/jcc.20035)
15. [AmberTools](https://ambermd.org/AmberTools.php)
