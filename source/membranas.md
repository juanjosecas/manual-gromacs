## Proteína de membrana: construcción de una bicapa e inserción de una acuaporina

### Introducción

Las proteínas de membrana no deben simularse como proteínas solubles rodeadas únicamente por agua. La bicapa aporta un entorno anisotrópico, ejerce presión lateral, establece interfaces polares y apolares, modula la conformación de la proteína y puede ocupar sitios de unión específicos. La composición lipídica, la orientación, el ensamblado oligomérico y el protocolo de equilibración forman parte del modelo físico.

CHARMM-GUI Membrane Builder automatiza gran parte de esta preparación: lectura y reparación de la estructura, orientación, construcción de bicapas homogéneas o heterogéneas, agua en cavidades, solvatación, incorporación de iones y generación de archivos para GROMACS. La automatización reduce errores mecánicos, pero no decide qué unidad biológica, estado de protonación, composición de membrana o ensamble experimental son correctos.

Este tutorial usa una acuaporina como caso principal y contempla dos resoluciones:

- **all-atom:** proteína, lípidos, agua e iones representados átomo por átomo;
- **coarse-grained (CG):** varios átomos se agrupan en partículas efectivas.

Ambos modelos responden preguntas diferentes. No deben mezclarse archivos de fuerza, topologías ni pasos de integración entre CHARMM36 y Martini.

Flujo general:

```text
estructura y pregunta biológica
    ↓
unidad biológica y protonación
    ↓
orientación respecto de la membrana
    ↓
composición y tamaño de la bicapa
    ↓
construcción en CHARMM-GUI
    ↓
inspección de topología y coordenadas
    ↓
EM y equilibración con restricciones decrecientes
    ↓
producción
    ↓
control de proteína, bicapa, agua, iones y poro
```

### 1. Definir el objetivo antes de construir el sistema

Registre antes de usar Membrane Builder:

- especie, tejido y membrana de origen;
- isoforma y secuencia exacta;
- ensamblado oligomérico;
- estructura experimental o modelo utilizado;
- residuos faltantes, mutaciones y modificaciones;
- ligandos, cofactores, iones o lípidos estructurales;
- orientación y topología transmembrana;
- composición de cada monocapa;
- pH, temperatura, presión y fuerza iónica;
- variable principal que se analizará;
- número de réplicas y duración prevista.

Una bicapa de POPC puro puede ser un modelo controlado útil, pero no representa de forma universal una membrana plasmática, bacteriana, mitocondrial o del cristalino. La composición lipídica puede modificar estabilidad, inclinación, oligomerización y función de una proteína de membrana.

### 2. Particularidades de las acuaporinas

Las acuaporinas suelen organizarse como homotetrámeros. Cada monómero contiene su propio poro acuoso; el eje central del tetrámero no equivale necesariamente a un quinto canal de agua funcional. La simulación de un monómero aislado elimina contactos entre subunidades y expone superficies que en el ensamblado biológico contactan con otros monómeros.

Antes de construir el sistema:

- obtenga la unidad biológica, no solo la unidad asimétrica del PDB;
- compruebe que estén presentes los cuatro monómeros cuando el objetivo sea el tetrámero;
- revise los dos motivos NPA de cada monómero;
- revise el filtro ar/R y los residuos que determinan selectividad;
- identifique lípidos, metales u otras moléculas resueltas;
- verifique que las hélices transmembrana estén completas;
- decida si colas N- o C-terminales faltantes se modelarán o se dejarán truncadas.

CHARMM-GUI puede aplicar operaciones de simetría si la información está disponible, pero el resultado debe compararse con el ensamblado biológico informado por la fuente estructural.

### 3. Preparación de la estructura

Conserve el archivo original:

```bash
mkdir -p 00_entrada 01_charmmgui 02_em 03_equilibracion 04_md 05_analisis
cp aquaporin_input.pdb 00_entrada/aquaporin_original.pdb
```

Revise:

- cadenas y segmentos que se conservarán;
- conformaciones alternativas;
- residuos faltantes;
- enlaces disulfuro;
- terminales;
- histidinas y otros grupos titulables;
- aguas estructurales dentro del canal;
- moléculas de cristalización que deben eliminarse;
- ligandos o cofactores que necesitan parámetros.

No elimine automáticamente todas las aguas cristalográficas. Una cadena de agua bien resuelta dentro de una acuaporina puede aportar una configuración inicial razonable, aunque no debe conservarse si solapa con el procedimiento de generación de agua del poro.

CHARMM-GUI puede modelar segmentos faltantes cortos. Las regiones largas o poco determinadas requieren validación adicional; una geometría generada por el servidor no constituye evidencia estructural.

### 4. Orientación respecto de la bicapa

En Membrane Builder:

- el plano de la membrana es **xy**;
- la normal de la bicapa es el eje **z**;
- el centro hidrofóbico se sitúa aproximadamente en $z=0$.

Una estructura obtenida de OPM o PPM puede usarse como orientación inicial. Una estructura descargada directamente de RCSB no está necesariamente orientada respecto de una membrana.

Las opciones basadas en ejes principales o en un vector son aproximaciones geométricas. Pueden fallar cuando:

- existen dominios extramembrana grandes;
- la proteína es irregular;
- se cargó un oligómero incompleto;
- el eje principal no coincide con el poro;
- hay hélices anfipáticas o reentrantes;
- la proteína es un barril beta asimétrico.

La orientación debe validarse visualmente y estructuralmente. Compruebe que:

- la región hidrofóbica contacte con las colas;
- los residuos cargados no queden enterrados sin justificación;
- los dominios citosólicos y extracelulares estén del lado correcto;
- el poro atraviese la bicapa en la dirección esperada;
- no haya subunidades invertidas;
- el centro del filtro selectivo quede cerca de la región prevista.

Para una acuaporina, la orientación del tetrámero debe evaluarse como conjunto. Orientar una sola cadena y reconstruir después el tetrámero puede introducir una geometría inconsistente.

### 5. Agua del poro

Membrane Builder puede generar agua dentro de poros y cavidades. Este paso es particularmente relevante para acuaporinas, canales, porinas y transportadores.

Revise que:

- los cuatro poros monoméricos estén hidratados;
- no haya agua aislada dentro de la región hidrofóbica fuera del canal;
- no queden huecos extensos producidos por una mala construcción;
- las aguas no solapen con ligandos o residuos;
- la hidratación central del tetrámero no se confunda con permeación monomérica.

La ocupación inicial no debe interpretarse como un resultado. El patrón de agua debe reequilibrarse durante la dinámica.

### 6. Selección de la composición lipídica

Elija la composición a partir del organismo y del compartimiento celular. Si no existe información suficiente, declare explícitamente que se utiliza una membrana modelo.

Ejemplos de decisiones justificables:

| Objetivo                              | Modelo posible                                            | Limitación                                                |
| ------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------- |
| Estabilidad general de una acuaporina | POPC puro                                                 | No reproduce asimetría ni diversidad celular.             |
| Influencia del colesterol             | POPC/colesterol                                           | La proporción debe justificarse experimentalmente.        |
| Membrana bacteriana interna           | Mezcla PE/PG/cardiolipina                                 | Depende de especie y condición de crecimiento.            |
| Membrana externa Gram negativa        | Monocapa externa con LPS y monocapa interna fosfolipídica | Requiere parámetros, iones y equilibración más exigentes. |
| Comparación entre isoformas           | Misma bicapa controlada                                   | Aumenta comparabilidad, pero reduce realismo fisiológico. |

En mezclas asimétricas, las dos monocapas pueden contener números y áreas moleculares diferentes. CHARMM-GUI permite ajustar proporciones y luego refinar el número de cada especie. No fuerce la misma cantidad de lípidos en ambas monocapas si sus composiciones o áreas efectivas son diferentes.

### 7. Tamaño del sistema

La caja debe contener suficientes lípidos alrededor de la proteína para reducir la interacción con sus imágenes periódicas. La extensión lateral no debe calcularse solo como el rango máximo de coordenadas de la proteína.

Como criterio inicial:

$$
L_x \gtrsim d_x + 2b
$$

$$
L_y \gtrsim d_y + 2b
$$

donde $d_x$ y $d_y$ son las dimensiones proyectadas de la proteína y $b$ es el espesor del anillo lipídico deseado. Para una proteína que pueda inclinarse o cambiar de conformación, debe añadirse margen adicional.

La cantidad aproximada de lípidos de una monocapa homogénea puede estimarse como:

$$
N_{\mathrm{lip}} \approx
\frac{A_{xy}-A_{\mathrm{prot}}}
     {a_{\mathrm{lip}}}
$$

donde:

- $A_{xy}=L_xL_y$;
- $A_{\mathrm{prot}}$ es el área proyectada ocupada por la proteína;
- $a_{\mathrm{lip}}$ es el área por lípido esperada en esas condiciones.

La ecuación es orientativa. En una mezcla lipídica, alrededor de una proteína irregular o en una membrana asimétrica no existe una única área por lípido que resuelva el empaquetamiento.

La altura de agua debe evitar contactos periódicos entre dominios extramembrana. CHARMM-GUI expresa normalmente estas dimensiones en Å:

$$
10\ \text{Å}=1\ \text{nm}
$$

GROMACS utiliza nanómetros en coordenadas y parámetros espaciales.

### 8. Temperatura y estado de fase

La temperatura no debe elegirse solo por el valor predeterminado del servidor. Debe ser compatible con:

- la condición experimental;
- el estado de fase esperado de los lípidos;
- la parametrización;
- la estabilidad de la proteína;
- la pregunta biológica.

Conversión:

$$
T(\mathrm{K})=T(^{\circ}\mathrm{C})+273.15
$$

| °C  | K      |
| ---:| ------:|
| 20  | 293.15 |
| 25  | 298.15 |
| 30  | 303.15 |
| 37  | 310.15 |

Una bicapa destinada a representar una fase fluida debe simularse por encima de la transición pertinente de la mezcla. En mezclas complejas, la transición no puede inferirse únicamente a partir de un lípido aislado.

### 9. Iones y concentración

CHARMM-GUI puede neutralizar el sistema y agregar NaCl, KCl u otras sales. Distinga:

- **neutralización:** cantidad mínima de contraiones para carga neta cero;
- **concentración salina nominal:** pares iónicos adicionales según el volumen accesible;
- **fuerza iónica:** depende de carga y concentración de todas las especies.

$$
I=\frac{1}{2}\sum_i c_i z_i^2
$$

donde $c_i$ es la concentración molar y $z_i$ la carga del ion.

Una solución 0.15 M de NaCl se usa frecuentemente como aproximación fisiológica, pero “0.15 M” e “isotónica” no son sinónimos generales. MgCl₂ o CaCl₂ producen otra fuerza iónica y otra osmolaridad. Los iones divalentes también pueden interactuar fuertemente con lípidos aniónicos.

No sustituya un ion estructural o catalítico por un contraion difusible.

### 10. Construcción en CHARMM-GUI Membrane Builder

Secuencia conceptual de la interfaz:

1. Seleccionar **Input Generator → Membrane Builder**.
2. Elegir un sistema proteína/membrana.
3. Cargar un PDB propio o recuperar una estructura.
4. Seleccionar modelo, cadenas, ligandos y componentes.
5. Aplicar terminales, protonación, enlaces disulfuro y reparaciones justificadas.
6. Orientar la proteína.
7. Generar y revisar agua del poro.
8. Definir forma y dimensiones de caja.
9. Elegir composición de ambas monocapas.
10. Seleccionar agua, iones, concentración y método de colocación.
11. Ensamblar y revisar el sistema.
12. Generar entradas para GROMACS con el campo de fuerza seleccionado.
13. Descargar el archivo TGZ y conservar el identificador del trabajo.

La disponibilidad exacta de lípidos y opciones cambia con la versión del servidor. Registre la fecha, el identificador del trabajo, el campo de fuerza y las opciones elegidas.

### 11. Inspección del archivo descargado

Descomprima sin modificar el original:

```bash
mkdir -p 01_charmmgui
tar -xzf charmm-gui.tgz -C 01_charmmgui
cd 01_charmmgui
```

Localice la carpeta de GROMACS:

```bash
find . -maxdepth 3 -type f \
    \( -name 'topol.top' -o -name 'index.ndx' -o -name '*.mdp' -o -name 'README*' \) \
    -print
```

Los nombres pueden variar entre trabajos. Una salida típica contiene:

```text
topol.top
index.ndx
step5_input.gro o step5_charmm2gmx.pdb
step6.0_minimization.mdp
step6.1_equilibration.mdp
...
step6.6_equilibration.mdp
step7_production.mdp
archivos .itp
directorio del campo de fuerza
README o script de ejecución
```

No regenere la topología con **pdb2gmx**. CHARMM-GUI ya produjo una topología consistente con la proteína, los lípidos, el agua y los iones. Ejecutar **pdb2gmx** sobre el sistema ensamblado elimina esa coherencia.

Antes de correr:

```bash
gmx --version
head -n 80 topol.top
grep -R "^define\|^integrator\|^dt\|^nsteps\|^tcoupl\|^pcoupl\|^pcoupltype" ./*.mdp
```

Compruebe:

- campo de fuerza esperado;
- nombres y cantidades en `[ molecules ]`;
- existencia de todos los archivos incluidos;
- grupos de **index.ndx**;
- temperatura;
- paso de integración;
- duración de cada etapa;
- esquema de cortes;
- termostato y barostato;
- macros de restricciones;
- frecuencia de salida;
- tratamiento de dispersión y PME.

No reemplace parámetros del MDP por un archivo genérico. Los cortes y modificadores de Lennard-Jones deben ser compatibles con CHARMM36 y con la versión concreta usada por el servidor.

### 12. CSH no es un requisito

Los archivos generados pueden incluir un script C shell. GROMACS no depende de CSH: el script solo encadena llamadas a **gmx grompp** y **gmx mdrun**. Puede ejecutar cada etapa manualmente o usar Bash/POSIX shell.

No ejecute el script sin leerlo. Los nombres de archivos y el número de etapas pueden cambiar.

### 13. Minimización manual

Adapte **step5_input.gro** al nombre real del archivo descargado:

```bash
gmx grompp \
    -f step6.0_minimization.mdp \
    -c step5_input.gro \
    -r step5_input.gro \
    -n index.ndx \
    -p topol.top \
    -o step6.0_minimization.tpr \
    -pp step6.0_processed.top

gmx mdrun \
    -deffnm step6.0_minimization \
    -v
```

La opción **-r** proporciona las coordenadas de referencia para las restricciones posicionales. Si el MDP o la topología usan esas restricciones y **-r** se omite, **grompp** puede fallar o aplicar una referencia incorrecta.

Revise:

```bash
gmx check -f step6.0_minimization.gro

(echo Potential; echo 0) | \
gmx energy \
    -f step6.0_minimization.edr \
    -o ../05_analisis/em_potential.xvg
```

### 14. Equilibración escalonada sin CSH

CHARMM-GUI suele generar varias etapas que reducen gradualmente restricciones sobre proteína, lípidos, agua y componentes internos. No combine las seis etapas en una sola sin comparar sus MDP.

Script Bash, versión 4 o superior:

```bash
#!/usr/bin/env bash
set -euo pipefail

GMX_COMMAND="${GMX_COMMAND:-gmx}"
REFERENCE="step5_input.gro"
PREVIOUS="step6.0_minimization"

for STEP in 1 2 3 4 5 6
do
    NAME="step6.${STEP}_equilibration"
    MDP="${NAME}.mdp"

    if [[ ! -f "${MDP}" ]]; then
        printf 'Falta %s\n' "${MDP}" >&2
        exit 1
    fi

    COMMAND=(
        "${GMX_COMMAND}" grompp
        -f "${MDP}"
        -c "${PREVIOUS}.gro"
        -r "${REFERENCE}"
        -n index.ndx
        -p topol.top
        -o "${NAME}.tpr"
    )

    if [[ "${STEP}" -gt 1 && -f "${PREVIOUS}.cpt" ]]; then
        COMMAND+=(-t "${PREVIOUS}.cpt")
    fi

    "${COMMAND[@]}"

    "${GMX_COMMAND}" mdrun \
        -deffnm "${NAME}" \
        -v

    PREVIOUS="${NAME}"
done
```

Guárdelo como **run_equilibration.sh** y ejecute:

```bash
chmod +x run_equilibration.sh
./run_equilibration.sh
```

El script usa arreglos de Bash para preservar correctamente cada argumento. No es compatible con un intérprete POSIX mínimo como **dash**; debe ejecutarse con Bash.

Si el archivo inicial se llama **step5_charmm2gmx.pdb**, cambie **REFERENCE**. Si CHARMM-GUI genera más o menos etapas, modifique la lista.

Para revisar sin ejecutar:

```bash
bash -n run_equilibration.sh
```

### 15. Qué cambia entre las etapas de equilibración

Inspeccione las diferencias:

```bash
diff -u step6.1_equilibration.mdp step6.2_equilibration.mdp
diff -u step6.5_equilibration.mdp step6.6_equilibration.mdp
```

Normalmente cambian una o más de estas variables:

- constantes de restricciones;
- paso de integración;
- temperatura;
- acoplamiento de presión;
- duración;
- tratamiento de grupos;
- frecuencias de salida.

Una etapa corta puede ser suficiente para resolver contactos, pero no demuestra equilibrio de la bicapa. Extienda una etapa si persisten:

- huecos alrededor de la proteína;
- deformación fuerte de la bicapa;
- densidad no estacionaria;
- área xy con deriva;
- agua dentro del núcleo hidrofóbico fuera del poro;
- errores LINCS;
- proteína que se desplaza o inclina bruscamente;
- contactos periódicos.

### 16. Acoplamiento de presión en membranas

Para una bicapa en el plano xy se utiliza habitualmente acoplamiento semiisotrópico:

```ini
pcoupltype       = semiisotropic
ref-p            = 1.0 1.0
compressibility  = 4.5e-5 4.5e-5
```

El primer valor corresponde conjuntamente a x/y y el segundo a z. El acoplamiento isotrópico obliga a que todas las dimensiones respondan de la misma manera y no suele ser apropiado para una bicapa plana.

**C-rescale** es adecuado para equilibración. **Parrinello-Rahman** suele reservarse para producción una vez estabilizado el sistema. Mantenga inicialmente los valores generados por CHARMM-GUI y documente cualquier cambio.

No interprete fluctuaciones instantáneas de presión como fallo. Evalúe deriva, densidad, área, espesor y promedios por bloques.

### 17. Repartición de masa de hidrógeno (HMR)

La **repartición de masa de hidrógeno** (*hydrogen mass repartitioning*, HMR) transfiere parte de la masa del átomo pesado a sus hidrógenos enlazados sin cambiar la masa total de la molécula. Su objetivo es disminuir las frecuencias más altas del sistema y permitir, después de validarlo, un paso de integración mayor.

Para una vibración aproximadamente armónica:

$$
\omega=\sqrt{\frac{k}{\mu}},
\qquad
\mu=\frac{m_1m_2}{m_1+m_2}
$$

donde $k$ es la constante de fuerza y $\mu$ la masa reducida. Al aumentar la masa del hidrógeno aumenta $\mu$ y disminuye $\omega$. Para un factor de repartición $f$:

$$
m'_{H}=f\,m_H,
\qquad
m'_X=m_X-\sum_H\left(m'_H-m_H\right)
$$

El segundo término se suma sobre los hidrógenos unidos al átomo pesado $X$. Con $f=3$, un hidrógeno de aproximadamente $1.008\ \mathrm{u}$ pasa a aproximadamente $3.024\ \mathrm{u}$. La masa total se conserva. HMR no cambia las cargas, los parámetros de Lennard-Jones ni la función de energía potencial; sí cambia la matriz de masas y, por lo tanto, puede modificar propiedades dinámicas.

#### Qué permite y qué no permite HMR

En sistemas atomísticos convencionales, GROMACS indica que combinar un factor 3 con enlaces a hidrógeno restringidos permite **habitualmente** usar $\Delta t=0.004\ \mathrm{ps}=4\ \mathrm{fs}$. No es una garantía de estabilidad para cualquier topología. HMR:

- reduce aproximadamente a la mitad el número de pasos necesario para simular el mismo tiempo físico;
- puede acercarse a una aceleración de dos veces, aunque el rendimiento real depende de GPU, CPU, PME, restricciones y comunicaciones;
- no mejora el campo de fuerza ni genera más muestreo por nanosegundo simulado;
- conserva, en principio, las distribuciones configuracionales de equilibrio;
- altera escalas dinámicas: difusión, correlaciones temporales, cinética y tasas de transporte pueden resultar algo más lentas.

Por este último motivo, HMR es especialmente atractivo para propiedades estructurales y termodinámicas de membranas, pero exige cautela si el resultado principal es difusión lipídica, flujo de agua, permeabilidad de una acuaporina, tiempos de residencia o cinética de apertura.

#### Método nativo en GROMACS 2026.3

Desde GROMACS 2024, **gmx grompp** puede efectuar HMR a partir de una topología ordinaria mediante una sola opción del MDP. Para GROMACS 2026.3, el bloque mínimo es:

```ini
integrator              = md
dt                      = 0.004
constraints             = h-bonds
constraint-algorithm    = lincs
mass-repartition-factor = 3
```

**No combine este método con `define = -DHEAVY_H`, con masas ya modificadas por CHARMM-GUI ni con una edición manual de los ITP.** La opción nativa debe aplicarse al sistema completo. Reparticionar solo lípidos o solo proteína deja otros hidrógenos con movimientos rápidos y elimina la justificación física del paso de 4 fs.

**grompp** eleva al umbral correspondiente las masas de los átomos ligeros y resta la diferencia al átomo enlazado. Emite una advertencia si un átomo ligero no tiene vecino enlazado y un error si tiene más de uno o si la resta haría que el vecino quedara por debajo de la masa mínima. Esto obliga a revisar con especial cuidado moléculas no estándar, modelos polarizables, sitios virtuales y topologías con conectividad inusual.

#### Integración con los archivos de CHARMM-GUI

Duplique el MDP de producción para conservar un control de 2 fs:

```bash
cp step7_production.mdp step7_production_hmr.mdp
```

En **step7_production_hmr.mdp**, mantenga los parámetros de CHARMM-GUI para electrostática, van der Waals, temperatura y presión, y cambie únicamente lo necesario para la comparación:

```ini
dt                      = 0.004
constraints             = h-bonds
mass-repartition-factor = 3
```

No aproveche el cambio a HMR para acortar cortes, cambiar el barostato o sustituir los parámetros no enlazados. El estudio de membranas que evaluó HMR encontró resultados razonables con el protocolo validado, pero no respaldó el corte de $9\ \text{Å}=0.9\ \mathrm{nm}$ que también ensayó. En CHARMM36 deben conservarse los cortes y el esquema de conmutación recomendados para esa versión del campo de fuerza.

El tiempo simulado es:

$$
t_{\mathrm{total}}=n_{\mathrm{steps}}\,\Delta t
$$

Para 10 ns:

| Paso            | `nsteps`  | Tiempo |
| --------------- | ---------:| ------:|
| 0.002 ps (2 fs) | 5 000 000 | 10 ns  |
| 0.004 ps (4 fs) | 2 500 000 | 10 ns  |

Los intervalos de salida también dependen de $\Delta t$:

$$
\Delta t_{\mathrm{salida}}=\mathrm{nst}\times\Delta t
$$

Si se desea guardar cada 10 ps con 4 fs, use por ejemplo:

```ini
nstlog              = 2500
nstenergy           = 2500
nstxout-compressed  = 2500
```

#### Generación y comprobación del TPR

Ejemplo para producción después de una equilibración que ya empleó HMR:

```bash
gmx grompp \
    -f step7_production_hmr.mdp \
    -c step6.6_equilibration.gro \
    -t step6.6_equilibration.cpt \
    -r step5_input.gro \
    -n index.ndx \
    -p topol.top \
    -pp processed_hmr.top \
    -po mdout_hmr.mdp \
    -o step7_1_hmr.tpr
```

Revise los parámetros efectivamente procesados:

```bash
grep -E '^(dt|nsteps|constraints|mass-repartition-factor)' mdout_hmr.mdp
gmx dump -s step7_1_hmr.tpr > step7_1_hmr.dump
```

El archivo **processed_hmr.top** permite auditar la topología preprocesada, mientras que **gmx dump** permite inspeccionar el TPR. No edite ninguno para ejecutar la simulación; corrija siempre el MDP o la topología fuente y vuelva a ejecutar **grompp**.

Lo más limpio es usar HMR de manera consistente desde la primera etapa de dinámica de la equilibración. Si el sistema fue equilibrado a 2 fs con masas normales y se decide cambiar después, no trate la primera ejecución HMR como una continuación bit a bit de la dinámica anterior. Genere velocidades compatibles en una etapa NVT corta, vuelva a equilibrar a NPT y recién después produzca. Mantenga separados los nombres de archivos y no anexe un tramo HMR a un log o trayectoria de masas normales.

#### Prueba escalonada de estabilidad

Antes de una producción larga:

1. demuestre que el mismo sistema es estable con masas normales y 2 fs;
2. prepare HMR sin cambiar simultáneamente otros parámetros;
3. ejecute una prueba corta de 100 ps a 1 ns;
4. revise advertencias LINCS, NaN, temperatura, energía, volumen, área xy y espesor;
5. amplíe la prueba antes de lanzar réplicas largas.

Una prueba de 1 ns a 4 fs contiene 250 000 pasos:

```bash
gmx mdrun \
    -s step7_1_hmr.tpr \
    -deffnm hmr_test \
    -nsteps 250000 \
    -v
```

Busque problemas evidentes:

```bash
grep -Ei 'LINCS|constraint|nan|fatal|warning' hmr_test.log
gmx energy -f hmr_test.edr -o hmr_test_control.xvg
```

Seleccione al menos temperatura, energía potencial, presión, volumen y dimensiones de caja. Si 4 fs falla, no oculte el problema aumentando indiscriminadamente el orden de LINCS. Revise estructura, contactos, topología, restricciones y equilibración. Un paso de 3 fs puede ser una alternativa; si tampoco es estable o la topología no es compatible, use 2 fs.

#### Validación específica para una membrana

Compare al menos una réplica de referencia a 2 fs y masas normales con una réplica HMR a 4 fs, usando el mismo sistema y el mismo tiempo físico. Evalúe por bloques:

- área por lípido o área xy;
- espesor y perfiles de densidad;
- parámetro de orden $S_{CD}$;
- compresibilidad areal;
- RMSD, RMSF e inclinación de la proteína;
- contactos lípido–proteína;
- hidratación y radio del poro;
- difusión lateral, indicando que HMR altera la dinámica;
- estabilidad de temperatura, energía y presión;
- rendimiento en ns/día sobre el mismo hardware.

Para una acuaporina, la recomendación práctica es usar HMR con confianza solo después de demostrar que la estructura de la membrana y del canal coincide con el control. Si el objetivo es una **permeabilidad absoluta**, flujo de agua o una constante cinética, conserve producción de 2 fs con masas normales como referencia principal o cuantifique explícitamente el sesgo de HMR. Una ocupación o un perfil de densidad es configuracional; una tasa de cruce depende del tiempo dinámico y no debe asumirse invariante.

#### Decisión práctica

HMR es recomendable cuando se busca aumentar el muestreo de equilibrio de estructura, contactos y termodinámica, siempre que el sistema pase una validación apareada. No lo use de forma automática cuando:

- existen hidrógenos flexibles sin restringir;
- la topología contiene conectividades o partículas no estándar que **grompp** rechaza;
- se mezclan componentes con y sin HMR;
- se pretende comparar directamente cinética con trayectorias de masas normales;
- no hay un control estable a 2 fs;
- se cambia al mismo tiempo HMR, cortes, termostato, barostato y grupos de acoplamiento.

La discusión histórica del foro incluye métodos dependientes del campo de fuerza y casos de inestabilidad anteriores a la opción nativa. Son útiles para entender los errores frecuentes, pero para GROMACS 2026.3 debe prevalecer el método documentado con **mass-repartition-factor**.

### 18. Producción segmentada sin CSH

Dividir una producción en segmentos no cambia por sí mismo la física. Facilita checkpoints, colas HPC, copias de seguridad y reanudación. El tiempo total es:

$$
t_{\mathrm{total}} =
N_{\mathrm{segmentos}}\,
n_{\mathrm{steps}}\,
\Delta t
$$

Si cada segmento contiene 5000000 pasos con $\Delta t=0.002\ \mathrm{ps}$:

$$
t_{\mathrm{segmento}}=10\ \mathrm{ns}
$$

Diez segmentos suman 100 ns.

Script Bash:

```bash
#!/usr/bin/env bash
set -euo pipefail

GMX_COMMAND="${GMX_COMMAND:-gmx}"
FIRST_SEGMENT="${FIRST_SEGMENT:-1}"
LAST_SEGMENT="${LAST_SEGMENT:-10}"
REFERENCE="step5_input.gro"

for SEGMENT in $(seq "${FIRST_SEGMENT}" "${LAST_SEGMENT}")
do
    NAME="step7_${SEGMENT}"

    if [[ "${SEGMENT}" -eq 1 ]]; then
        PREVIOUS="step6.6_equilibration"
    else
        PREVIOUS="step7_$((SEGMENT - 1))"
    fi

    if [[ ! -f "${NAME}.tpr" ]]; then
        "${GMX_COMMAND}" grompp \
            -f step7_production.mdp \
            -c "${PREVIOUS}.gro" \
            -t "${PREVIOUS}.cpt" \
            -r "${REFERENCE}" \
            -n index.ndx \
            -p topol.top \
            -o "${NAME}.tpr"
    fi

    if [[ -f "${NAME}.cpt" ]]; then
        "${GMX_COMMAND}" mdrun \
            -deffnm "${NAME}" \
            -cpi "${NAME}.cpt" \
            -append \
            -v
    else
        "${GMX_COMMAND}" mdrun \
            -deffnm "${NAME}" \
            -v
    fi
done
```

Guárdelo como **run_production.sh**:

```bash
chmod +x run_production.sh
bash -n run_production.sh
./run_production.sh
```

Para ejecutar solo los segmentos 4 a 7:

```bash
FIRST_SEGMENT=4 LAST_SEGMENT=7 ./run_production.sh
```

Si la producción no usa restricciones, **-r** puede ser innecesario, pero conservarlo no reemplaza la revisión del MDP y de las macros activas.

En un clúster, el script debe ejecutarse dentro del sistema de colas. No lance múltiples segmentos dependientes al mismo tiempo: cada uno necesita el checkpoint final del anterior.

### 19. Reanudar una ejecución interrumpida

Si existe un checkpoint del mismo segmento:

```bash
gmx mdrun \
    -deffnm step7_4 \
    -cpi step7_4.cpt \
    -append \
    -v
```

No vuelva a ejecutar **grompp** desde la última estructura si el objetivo es continuar exactamente el mismo segmento. El checkpoint conserva estado del integrador, velocidades y otra información necesaria para una continuación reproducible.

### 20. Preparación de la trayectoria para análisis

Conserve siempre la trayectoria original. Genere derivados para visualización y análisis.

Primero haga moléculas enteras y centre la proteína:

```bash
(echo Protein; echo System) | \
gmx trjconv \
    -s step7_1.tpr \
    -f md_all.xtc \
    -o 05_analisis/md_center.xtc \
    -pbc mol \
    -center \
    -ur compact
```

Luego ajuste la proteína si el análisis requiere eliminar traslación y rotación:

```bash
(echo Backbone; echo System) | \
gmx trjconv \
    -s step7_1.tpr \
    -f 05_analisis/md_center.xtc \
    -o 05_analisis/md_fit.xtc \
    -fit rot+trans
```

No use una trayectoria ajustada para difusión lateral de lípidos ni para fluctuaciones de caja. El ajuste cambia las coordenadas colectivas que esos análisis necesitan.

Si la producción está segmentada:

```bash
gmx trjcat \
    -f step7_1.xtc step7_2.xtc step7_3.xtc step7_4.xtc \
    -o md_all.xtc \
    -cat
```

Compruebe continuidad temporal y descarte marcos duplicados si los segmentos se solapan.

### 21. Controles estructurales de la proteína

RMSD del backbone:

```bash
(echo Backbone; echo Backbone) | \
gmx rms \
    -s step7_1.tpr \
    -f 05_analisis/md_fit.xtc \
    -o 05_analisis/rmsd_backbone.xvg \
    -tu ns
```

RMSF por residuo:

```bash
echo C-alpha | \
gmx rmsf \
    -s step7_1.tpr \
    -f 05_analisis/md_fit.xtc \
    -o 05_analisis/rmsf_calpha.xvg \
    -res
```

Para una acuaporina tetramérica, calcule además:

- RMSD de cada monómero;
- RMSD del tetrámero completo;
- distancias entre centros de masa de subunidades;
- contactos interfaciales entre monómeros;
- inclinación del eje de cada poro respecto de z;
- estabilidad de los motivos NPA;
- geometría del filtro ar/R.

Un RMSD estable del tetrámero puede ocultar que un monómero se deforma; cuatro RMSD monoméricos estables pueden ocultar una reorganización cuaternaria.

### 22. Área de la membrana

El área instantánea proyectada es:

$$
A_{xy}(t)=L_x(t)L_y(t)
$$

Extraiga las dimensiones:

```bash
(echo Box-X; echo Box-Y; echo Box-Z; echo Volume; echo 0) | \
gmx energy \
    -f step7_1.edr \
    -o 05_analisis/box_dimensions.xvg
```

Para una bicapa homogénea, simétrica y sin proteína:

$$
APL(t)=\frac{A_{xy}(t)}{N_{\mathrm{lip,leaflet}}}
$$

Con una proteína:

$$
APL_{\mathrm{aprox}}(t)=
\frac{A_{xy}(t)-A_{\mathrm{prot}}(t)}
     {N_{\mathrm{lip,leaflet}}}
$$

La corrección depende de cómo se defina el área proyectada de la proteína. En bicapas mixtas no existe una única APL rigurosa para todas las especies. Para análisis local conviene usar una partición de Voronoi u otra herramienta específica.

No divida por el número total de lípidos de las dos monocapas: el denominador es el número de una monocapa.

### 23. Compresibilidad areal

En un ensamble apropiado puede estimarse:

$$
K_A=
\frac{k_\mathrm{B}T\langle A\rangle}
     {\langle A^2\rangle-\langle A\rangle^2}
$$

donde $A=L_xL_y$. La estimación es sensible a:

- duración de la trayectoria;
- barostato;
- correlación temporal;
- tamaño del sistema;
- presencia de proteína;
- mezcla y asimetría de lípidos.

Use promedios por bloques y no compare directamente valores obtenidos con ensambles diferentes.

### 24. Espesor y perfiles de densidad

Calcule perfiles a lo largo de z:

```bash
gmx density \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -d Z \
    -sl 200 \
    -dens number \
    -o 05_analisis/density_z.xvg
```

Cree grupos para:

- fósforos o grupos cabeza;
- colas lipídicas;
- agua;
- proteína;
- iones;
- cada especie lipídica relevante.

Una definición simple del espesor entre cabezas es la distancia entre los máximos de densidad de fósforo de ambas monocapas:

$$
d_{PP}=z_{P,\mathrm{sup}}-z_{P,\mathrm{inf}}
$$

Es una definición global. Una membrana deformada alrededor de la proteína requiere mapas locales de espesor.

### 25. Orden de las cadenas lipídicas

El parámetro de orden deuterio se expresa como:

$$
S_{CD}=
\frac{1}{2}
\left\langle 3\cos^2\theta-1 \right\rangle
$$

donde $\theta$ es el ángulo entre un enlace de la cadena y la normal de la membrana.

Consulte primero la sintaxis disponible:

```bash
gmx order -h
```

Ejemplo general:

```bash
gmx order \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n lipid_chains.ndx \
    -d z \
    -od 05_analisis/order_parameter.xvg
```

El archivo de índice debe definir los átomos de cadena en el orden requerido. No mezcle carbonos de especies lipídicas diferentes en una misma curva sin justificarlo.

### 26. Difusión lateral de lípidos

Para difusión bidimensional:

$$
MSD_{xy}(t)=
\left\langle
[x(t)-x(0)]^2+[y(t)-y(0)]^2
\right\rangle
$$

En el régimen difusivo:

$$
MSD_{xy}(t)=4D_{xy}t
$$

Comando:

```bash
gmx msd \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -sel 'res_com of group "POPC"' \
    -lateral z \
    -o 05_analisis/msd_popc_xy.xvg
```

Compruebe la sintaxis con **gmx msd -h**, porque cambió respecto de versiones antiguas. El ajuste no debe incluir el régimen balístico inicial ni una región donde el MSD todavía sea subdifusivo. La difusión lipídica converge lentamente y depende del tamaño del sistema.

### 27. Inclinación de la proteína y del canal

Defina un vector entre centros de masa de dos grupos situados en extremos opuestos del poro y calcule su ángulo con z:

```bash
gmx gangle \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -g1 vector \
    -group1 'com of group "Pore_lower" plus com of group "Pore_upper"' \
    -g2 z \
    -oav 05_analisis/pore_tilt.xvg
```

La selección debe adaptarse a residuos conservados de la acuaporina. Para el tetrámero, genere una curva por monómero.

### 28. Radio y continuidad del poro

GROMACS no proporciona por sí solo un perfil completo de radio de poro equivalente a herramientas especializadas. Puede:

- medir distancias entre residuos del filtro;
- calcular densidad de agua a lo largo del eje;
- usar herramientas externas como HOLE o CHAP;
- comparar perfiles por monómero y por bloque temporal.

Una disminución local del radio no implica cierre funcional si el agua mantiene una cadena continua. Tampoco una cavidad geométricamente abierta demuestra permeabilidad.

### 29. Puentes de hidrógeno y orientación del agua

Puentes de hidrógeno proteína–agua:

```bash
gmx hbond \
    -s step7_1.tpr \
    -f 05_analisis/md_fit.xtc \
    -n index.ndx \
    -r 'group "Protein"' \
    -t 'group "Water"' \
    -num 05_analisis/protein_water_hbonds.xvg
```

Verifique la sintaxis exacta con:

```bash
gmx hbond -h
```

En acuaporinas importa no solo la ocupación, sino la orientación de las moléculas de agua cerca de los motivos NPA. El cambio de orientación contribuye al mecanismo de exclusión de protones. Este análisis requiere vectores dipolares o enlaces O–H y una coordenada axial referida al poro.

### 30. Conteo de eventos de permeación

Contar moléculas dentro de un cilindro en cada fotograma no equivale a contar permeaciones. Un evento debe exigir una trayectoria completa desde un reservorio hasta el opuesto.

Defina tres estados respecto del centro del canal:

```text
A: z < -z0
P: -z0 ≤ z ≤ z0 y dentro del radio del poro
B: z > z0
```

Una permeación A→B requiere la secuencia A→P→B para la misma molécula, sin reiniciar el conteo por fluctuaciones en el límite. Use coordenadas relativas al centro de cada monómero y corrija PBC.

El flujo neto bajo un gradiente puede expresarse como:

$$
J=\frac{N_{A\rightarrow B}-N_{B\rightarrow A}}{t}
$$

Una estimación directa de permeabilidad osmótica necesita además el gradiente de concentración:

$$
P_f=\frac{J}{\Delta c}
$$

Las unidades dependen de si $J$ se expresa como moléculas por tiempo, moles por tiempo o volumen por tiempo. En equilibrio, donde no hay flujo neto sostenido, se utilizan formulaciones basadas en fluctuaciones colectivas; no debe aplicarse la ecuación anterior con $\Delta c=0$.

### 31. Permeabilidad colectiva en equilibrio

Para una coordenada colectiva $n(t)$ que registra el desplazamiento neto de agua a través del canal:

$$
\left\langle
[n(t)-n(0)]^2
\right\rangle
\xrightarrow[t\ \mathrm{grande}]{}
2D_n t
$$

La permeabilidad osmótica de canal único puede relacionarse con:

$$
p_f=v_wD_n
$$

donde $v_w$ es el volumen molecular del agua y $D_n$ es el coeficiente de difusión de la coordenada colectiva. La definición exacta de $n(t)$, el tratamiento de PBC y el intervalo de ajuste deben mantenerse constantes al comparar sistemas.

No calcule una permeabilidad confiable a partir de unos pocos cruces. Use réplicas, intervalos de confianza y análisis por bloques.

### 32. Contactos lípido–proteína

Los contactos persistentes pueden revelar sitios anulares o específicos. Un contacto simple puede definirse por una distancia máxima:

```bash
gmx select \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -select 'resname POPC and within 0.45 of group "Protein"' \
    -os 05_analisis/lipid_contacts_size.xvg
```

Este resultado informa cuántos átomos o posiciones cumplen la selección, según la salida elegida; no es automáticamente un número de lípidos únicos. Para residencia lipídica deben seguirse identidades moleculares y tolerar interrupciones cortas.

En una mezcla, analice enriquecimiento relativo:

$$
E_i=
\frac{x_i^{\mathrm{contacto}}}
     {x_i^{\mathrm{membrana}}}
$$

donde $E_i>1$ sugiere enriquecimiento de la especie $i$ alrededor de la proteína. El resultado depende del corte, del área considerada y del muestreo.

### 33. Potencial electrostático y sistemas con voltaje

El potencial promedio a lo largo de z puede calcularse con **gmx potential** a partir de grupos de carga apropiados. Una sola bicapa periódica no crea automáticamente dos reservorios independientes.

Para estudiar flujo iónico bajo potencial sostenido puede utilizarse el protocolo de electrofisiología computacional de GROMACS, que emplea típicamente dos bicapas, dos compartimientos y un desequilibrio de carga:

$$
\Delta U=\frac{\Delta q}{C_{\mathrm{membrana}}}
$$

Este montaje no es necesario para permeación de agua en equilibrio y no debe añadirse sin una pregunta electrofisiológica explícita.

### 34. Réplicas, descarte y convergencia

Una trayectoria larga no reemplaza réplicas independientes. Para comparar acuaporinas, mutantes o composiciones:

- use varias semillas de velocidad;
- mantenga idénticos los parámetros comunes;
- descarte la etapa transitoria según observables;
- compare bloques temporales;
- informe incertidumbre entre réplicas;
- evite seleccionar la trayectoria “más estable”.

La estabilización del RMSD no demuestra que APL, espesor, difusión lipídica o permeación hayan convergido.

### 35. Simulación coarse-grained

Un modelo CG reduce grados de libertad y permite escalas espaciales o temporales mayores. A cambio, pierde detalle atomístico, modifica la cinética efectiva y puede requerir restricciones estructurales adicionales.

Use un constructor y una versión de Martini compatibles. No convierta simplemente las coordenadas all-atom y reutilice:

- **topol.top** de CHARMM36;
- archivos ITP atomísticos;
- modelo de agua atomístico;
- cortes atomísticos;
- paso de integración atomístico;
- parámetros de restricciones atomísticas.

Registre:

- versión de Martini;
- método de mapeo;
- modelo de agua;
- tratamiento electrostático;
- red elástica;
- radio y constante de la red;
- lípidos CG;
- paso de integración;
- método de backmapping, si se utiliza.

### 36. Redes elásticas en proteínas CG

Una red elástica ayuda a conservar estructura terciaria o cuaternaria, pero puede suprimir:

- apertura del canal;
- inclinación helicoidal;
- movimientos entre dominios;
- respiración del poro;
- reorganización oligomérica.

No use una red “porque es el valor predeterminado” si la variable de interés depende del movimiento restringido. Realice análisis de sensibilidad cambiando el corte o la constante, o compare con un modelo sin red cuando sea estable.

La red elástica no reemplaza enlaces covalentes, disulfuros ni una unidad biológica correcta.

### 37. Paso de integración en CG

Los pasos CG suelen ser mayores que en all-atom, pero el máximo estable depende del modelo, el agua, las restricciones y la geometría inicial. Comience con el protocolo recomendado para la versión concreta y revise:

- energía;
- errores de restricciones;
- temperatura y presión;
- estabilidad del poro;
- comportamiento de los lípidos;
- sensibilidad al paso de integración.

La aceleración aparente del tiempo en CG no debe interpretarse como una correspondencia universal y exacta con tiempo experimental.

### 38. Visualización CG

VMD y otros visores pueden no inferir correctamente enlaces entre partículas CG porque usan reglas pensadas para geometrías atomísticas. La ausencia visual de enlaces no significa que falten en la topología.

Las representaciones deben basarse en nombres reales de partículas y residuos. Ejemplos habituales en Martini incluyen:

```text
name BB
resname POPC
resname W
resname NA CL
```

Los nombres dependen de la versión y del constructor. Compruébelos en la coordenada y en los ITP.

Para reducir memoria, genere una trayectoria de visualización:

```bash
gmx trjconv \
    -s cg_md.tpr \
    -f cg_md.xtc \
    -o cg_visualization.xtc \
    -n cg_visualization.ndx \
    -dt 1000
```

No use la trayectoria reducida para análisis que requieran resolución temporal mayor.

La representación secundaria atomística no puede reconstruirse exactamente a partir de unas pocas partículas por residuo. Una caricatura CG es una interpretación gráfica apoyada en la asignación secundaria, no una observación directa de todos los enlaces y ángulos del esqueleto.

### 39. Errores conceptuales frecuentes

- Simular una sola cadena de una acuaporina tetramérica sin justificarlo.
- Interpretar el centro del tetrámero como el poro de cada monómero.
- Orientar por eje principal sin revisar el cinturón hidrofóbico.
- Usar POPC puro y describirlo como membrana fisiológica.
- Considerar 0.15 M sinónimo universal de isotonicidad.
- Regenerar con **pdb2gmx** una topología de CHARMM-GUI.
- Sustituir los MDP generados por parámetros genéricos.
- Usar presión isotrópica en una bicapa plana sin validación.
- Retirar todas las restricciones en una sola etapa.
- Ejecutar 1 ps y declarar la membrana equilibrada.
- Ajustar rotación y traslación antes de calcular difusión lipídica.
- Calcular APL dividiendo por todos los lípidos de ambas monocapas.
- Contar ocupaciones del poro como eventos completos de permeación.
- Interpretar una sola trayectoria como estimación convergida de permeabilidad.
- Usar una red elástica CG que impide el movimiento que se quiere medir.
- Suponer que CSH es necesario para ejecutar los archivos de CHARMM-GUI.

### 40. Criterios para producción

Inicie la producción cuando:

- el ensamblado oligomérico sea correcto;
- la proteína esté orientada y centrada de forma razonable;
- no existan residuos o componentes sin parametrizar;
- las monocapas tengan la composición y asimetría previstas;
- topología, coordenadas e índice sean coherentes;
- los poros estén hidratados sin agua espuria en el núcleo;
- no existan contactos graves ni errores LINCS;
- temperatura, volumen, área xy y espesor sean estacionarios;
- no haya deriva sistemática de la proteína;
- las restricciones hayan alcanzado la etapa planificada;
- el intervalo descartado y los análisis se hayan definido;
- se hayan planificado réplicas independientes.

### Fuentes

1. [Tutorial de CHARMM-GUI para complejos proteína–membrana heterogéneos](https://charmm-gui.org/?doc=tutorial&project=membrane&chapter=membrane_vdac_hetero)
2. [Preparación de proteínas de membrana con CHARMM-GUI](https://pmc.ncbi.nlm.nih.gov/articles/PMC8158057/)
3. [Documentación de uso de CHARMM](https://www.charmm-gui.org/charmmdoc/usage.html)
4. [Opciones MDP de GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/mdp-options.html)
5. [Referencia de gmx msd](https://manual.gromacs.org/current/onlinehelp/gmx-msd.html)
6. [Referencia de gmx order](https://manual.gromacs.org/current/onlinehelp/gmx-order.html)
7. [Electrofisiología computacional en GROMACS](https://manual.gromacs.org/current/reference-manual/special/comp-electrophys.html)
8. [Balusek et al., *Accelerating Membrane Simulations with Hydrogen Mass Repartitioning*](https://pmc.ncbi.nlm.nih.gov/articles/PMC7271963/)
9. [Discusión técnica de HMR en el foro de GROMACS](https://gromacs.bioexcel.eu/t/hydrogen-mass-repartitioning/1171)
10. [Seguimiento de la documentación de HMR en GROMACS, work item 5007](https://gitlab.com/gromacs/gromacs/-/work_items/5007)
11. [HMR flexible mediante grompp: notas de rendimiento de GROMACS 2026.3](https://manual.gromacs.org/2026.3/release-notes/2024/major/performance.html#flexible-hydrogen-mass-repartitioning-using-grompp)
12. [Opciones MDP de GROMACS 2026.3: mass-repartition-factor](https://manual.gromacs.org/2026.3/user-guide/mdp-options.html#mdp-value-mass-repartition-factor)
