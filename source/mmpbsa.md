## Energía de unión mediante `gmx_MMPBSA`

### 1. Qué calcula este método

**gmx_MMPBSA** es la implementación actual para realizar cálculos de energía libre de unión de estados finales usando trayectorias y topologías de GROMACS. Está basado en **MMPBSA.py** de AmberTools y reemplaza el flujo antiguo basado en **g_mmpbsa**, un archivo **pbsa.mdp**, APBS ejecutado externamente y el script **pbsa.py**.

MM/PBSA y MM/GBSA no son FEP. No contienen estados λ, no hacen desaparecer el ligando y no necesitan umbrella sampling para impedir que el ligando se aleje durante un desacoplamiento. Analizan configuraciones ya muestreadas de los estados unido y libre mediante un modelo de solvente implícito.

El esquema básico es:

$$
\Delta G_{\mathrm{bind}}
=
G_{\mathrm{complejo}}
-
G_{\mathrm{receptor}}
-
G_{\mathrm{ligando}}
$$

Para cada especie:

$$
G=
E_{\mathrm{MM}}
+
G_{\mathrm{solv}}
-
TS
$$

La energía de mecánica molecular puede escribirse:

$$
E_{\mathrm{MM}}
=
E_{\mathrm{bonded}}
+
E_{\mathrm{vdW}}
+
E_{\mathrm{elec}}
$$

y la contribución de solvatación:

$$
G_{\mathrm{solv}}
=
G_{\mathrm{polar}}
+
G_{\mathrm{nonpolar}}
$$

Por tanto:

$$
\Delta G_{\mathrm{bind}}
=
\Delta E_{\mathrm{MM}}
+
\Delta G_{\mathrm{polar}}
+
\Delta G_{\mathrm{nonpolar}}
-
T\Delta S
$$

Si no se calcula entropía, el resultado contiene solo:

$$
\Delta G_{\mathrm{bind}}^{*}
=
\Delta E_{\mathrm{MM}}
+
\Delta G_{\mathrm{solv}}
$$

El asterisco recuerda que no es una energía libre absoluta completa. Muchos informes la llaman “binding free energy”, pero físicamente es una estimación end-state sin el término entrópico explícito.

### 2. PB frente a GB

MM/PBSA calcula la contribución polar resolviendo numéricamente la ecuación de Poisson–Boltzmann. MM/GBSA utiliza una aproximación Generalized Born.

| Método  | Ventaja                                                      | Limitación                                                                    |
| ------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| MM/GBSA | Más rápido; útil para explorar protocolos y series.          | Mayor dependencia del modelo GB y del conjunto de radios.                     |
| MM/PBSA | Tratamiento continuo electrostático más explícito.           | Más costoso y sensible a malla, radios, dieléctricos y convergencia numérica. |
| 3D-RISM | Describe estructura promedio del solvente con mayor detalle. | Coste y preparación superiores; escalamiento paralelo limitado.               |

No existe una regla universal por la cual PB sea siempre más exacto que GB. La comparación debe validarse para la familia química y el objetivo.

### 3. Qué puede y qué no puede inferirse

Usos razonables:

- comparar poses del mismo ligando;
- ordenar ligandos estrechamente relacionados;
- comparar mutantes con un protocolo idéntico;
- detectar residuos que contribuyen de forma persistente;
- estudiar sensibilidad a parámetros del continuo;
- complementar estabilidad estructural y contactos.

No debe interpretarse automáticamente como:

- afinidad experimental absoluta;
- constante de disociación exacta;
- mecanismo de unión;
- tasa de asociación o disociación;
- sustituto de FEP para transformaciones pequeñas;
- prueba causal de que un residuo “produce” la unión;
- evidencia de convergencia de la dinámica.

La aproximación omite o simplifica agua explícita, reorganización del solvente, cambios de protonación, polarización, estados alternativos y, con frecuencia, entropía conformacional.

### 4. Protocolo de trayectoria única

En el protocolo de trayectoria única, **single trajectory, ST**, receptor y ligando se extraen de cada instantánea del complejo:

```text
trayectoria del complejo
        ├── complejo
        ├── receptor extraído
        └── ligando extraído
```

Esto mantiene correspondencia conformacional entre los tres términos y favorece la cancelación:

$$
\Delta E_{\mathrm{bonded}}\approx0
$$

Ventajas:

- menor ruido;
- menor costo;
- correspondencia exacta entre marcos;
- buena reproducibilidad operativa.

Supuesto fuerte:

- receptor y ligando libres adoptan las mismas conformaciones que en el complejo.

ST no cuantifica adecuadamente una reorganización grande inducida por unión.

### 5. Protocolo de trayectorias múltiples

En el protocolo **multiple trajectory, MT**, complejo, receptor y ligando provienen de simulaciones separadas:

$$
\Delta G_{\mathrm{bind}}
=
\langle G_C\rangle_C
-
\langle G_R\rangle_R
-
\langle G_L\rangle_L
$$

Puede incorporar reorganización conformacional, pero aumenta mucho la varianza porque se pierde cancelación entre configuraciones correlacionadas.

Use MT solo cuando:

- existan trayectorias libres suficientemente muestreadas;
- la reorganización sea parte de la pregunta;
- se disponga de varias réplicas;
- se evalúe la convergencia de cada estado por separado.

Un resultado MT más “completo” puede ser menos preciso que ST si el muestreo es insuficiente.

### 6. Requisitos actuales

La documentación de desarrollo consultada en septiembre de 2026 recomienda rangos probados:

- Python 3.11 o 3.12;
- AmberTools desde 24.8 y menor que 27;
- GROMACS desde 2022 y menor que 2027;
- ParmEd 4.2.2 o posterior dentro de la serie 4;
- MPI opcional para paralelización.

GROMACS 2026 está dentro del rango probado. Esto no garantiza que cualquier topología se convierta correctamente.

Archivos necesarios para ST:

```text
md.tpr              estructura y masas del complejo
md_fit.xtc          trayectoria corregida
index.ndx           grupos receptor y ligando
topol.top           topología completa de GROMACS
reference.pdb       referencia con cadenas y numeración, recomendada
mmpbsa.in           opciones del cálculo
```

La topología del ligando debe estar incluida en **topol.top**. La ruta actual no reconstruye ligandos desde un PDB sin parámetros.

### 7. Instalación reproducible

Conda o Mamba, Python 3.12:

```bash
conda create -n gmxMMPBSA python=3.12 -y
conda activate gmxMMPBSA

conda install -c conda-forge \
    "mpi4py>=4.0.1,<5" \
    "ambertools>=24.8,<27" \
    -y

python -m pip install gmx_MMPBSA
python -m pip check
```

Si GROMACS 2026 ya está instalado en el sistema y disponible en **PATH**, no instale otra copia sin necesidad. Verifique:

```bash
gmx --version
gmx_MMPBSA --version
gmx_MMPBSA -h
python -m pip check
```

Para una instalación completamente aislada:

```bash
conda install -c conda-forge "gromacs>=2022,<2027" pocl -y
```

La interfaz gráfica requiere PyQt6:

```bash
conda install -c conda-forge pyqt6 -y
```

No es necesaria en un nodo HPC sin entorno gráfico.

### 8. Probar la instalación

```bash
gmx_MMPBSA_test -h
```

Ejecute primero una prueba pequeña proporcionada por el paquete. Esto permite separar problemas de instalación de problemas propios de la topología.

Compruebe además:

```bash
command -v gmx
command -v gmx_MMPBSA
command -v ante-MMPBSA.py
echo "${AMBERHOME:-AMBERHOME no definido}"
```

La instalación debe encontrar AmberTools y GROMACS dentro del entorno activo o mediante las opciones de configuración correspondientes.

### 9. Preparación de los grupos

Cree un índice que contenga grupos separados y sin solapamiento:

- receptor;
- ligando;
- complejo receptor–ligando.

Forma interactiva:

```bash
gmx make_ndx \
    -f md.tpr \
    -o index.ndx
```

Ejemplo dentro de **make_ndx**, si el ligando se llama LIG:

```text
r LIG
Protein | r LIG
name NOMBRE_GRUPO_RECEPTOR Receptor
name NOMBRE_GRUPO_LIGANDO Ligando
name NOMBRE_GRUPO_COMPLEJO Complejo
q
```

Los números reales dependen del índice creado. Verifique:

```bash
gmx make_ndx \
    -f md.tpr \
    -n index.ndx \
    -o index_check.ndx
```

No use números copiados de otro sistema. La opción actual **-cg** acepta números de grupo basados en cero o nombres.

### 10. Corregir la trayectoria

La documentación requiere una trayectoria sin problemas de PBC y ajustada. El ligando debe permanecer junto al receptor.

Primero centre el complejo:

```bash
(echo Complejo; echo System) | \
gmx trjconv \
    -s md.tpr \
    -f md.xtc \
    -n index.ndx \
    -o md_center.xtc \
    -pbc mol \
    -center \
    -ur compact
```

Luego elimine rotación y traslación:

```bash
(echo Backbone; echo System) | \
gmx trjconv \
    -s md.tpr \
    -f md_center.xtc \
    -n index.ndx \
    -o md_fit.xtc \
    -fit rot+trans
```

Compruebe visualmente que:

- la proteína esté entera;
- el ligando no salte por PBC;
- el orden atómico no cambie;
- no se hayan descartado componentes necesarios;
- los tiempos sean correctos.

Para MM/PBSA se elimina el solvente durante la preparación interna. No genere una trayectoria manualmente desolvatada si todavía no verificó que la selección mantiene todos los componentes del complejo.

### 11. Estructura de referencia

Genere un PDB de referencia con el complejo completo:

```bash
echo Complejo | \
gmx trjconv \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -o reference.pdb \
    -dump 0
```

Revise cadenas, numeración, nombres de residuos y átomos. La opción **-cr reference.pdb** es recomendada porque evita asignaciones automáticas incorrectas, especialmente en complejos con varias cadenas.

### 12. Generar un archivo de entrada

La versión actual puede generar plantillas:

```bash
gmx_MMPBSA --create_input gb
gmx_MMPBSA --create_input pb
gmx_MMPBSA --create_input gb decomp
gmx_MMPBSA --create_input gb nmode
```

Revise siempre la plantilla generada por la versión instalada:

```bash
gmx_MMPBSA --input-file-help
```

No reutilice el archivo **pbsa.mdp** de **g_mmpbsa**. La sintaxis actual usa bloques namelist como **&general**, **&gb**, **&pb** y **&decomp**.

### 13. Entrada mínima MM/GBSA

Archivo **mmpbsa_gb.in**:

```text
&general
  sys_name="Complejo_proteina_ligando",
  startframe=1,
  endframe=5000,
  interval=10,
  PBRadii=4,
  temperature=300.0,
/

&gb
  igb=8,
  saltcon=0.150,
/
```

Con **igb=8**, la documentación recomienda **PBRadii=4**, correspondiente a mbondi3.

**startframe**, **endframe** e **interval** se refieren a índices de marcos procesados, no necesariamente a ps. El número analizado es aproximadamente:

$$
N_{\mathrm{frames}}
=
\left\lfloor
\frac{f_{\mathrm{final}}-f_{\mathrm{inicial}}}
     {\mathrm{interval}}
\right\rfloor+1
$$

No elija 500 marcos consecutivos y los trate como 500 observaciones independientes.

### 14. Ejecutar MM/GBSA

```bash
gmx_MMPBSA -O \
    -i mmpbsa_gb.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -o FINAL_RESULTS_MMGBSA.dat \
    -eo FINAL_RESULTS_MMGBSA.csv \
    -nogui
```

Significado de las opciones principales:

| Opción     | Función                                                            |
| ---------- | ------------------------------------------------------------------ |
| **-O**     | Permite sobrescribir resultados existentes. Úsela deliberadamente. |
| **-i**     | Archivo de parámetros.                                             |
| **-cs**    | TPR o PDB del complejo; se recomienda el TPR de producción.        |
| **-ct**    | Una o más trayectorias del complejo.                               |
| **-ci**    | Índice del complejo.                                               |
| **-cg**    | Grupos receptor y ligando.                                         |
| **-cp**    | Topología completa de GROMACS, obligatoria.                        |
| **-cr**    | PDB de referencia recomendado.                                     |
| **-o**     | Resumen estadístico.                                               |
| **-eo**    | Energías por marco en CSV.                                         |
| **-nogui** | No abre el analizador gráfico al terminar.                         |

### 15. Entrada mínima MM/PBSA

Genere primero la plantilla de su versión:

```bash
gmx_MMPBSA --create_input pb
```

Ejemplo inicial **mmpbsa_pb.in**:

```text
&general
  sys_name="Complejo_proteina_ligando_PB",
  startframe=1,
  endframe=1000,
  interval=10,
  temperature=300.0,
/

&pb
  istrng=0.150,
  fillratio=4.0,
/
```

Ejecución:

```bash
gmx_MMPBSA -O \
    -i mmpbsa_pb.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -o FINAL_RESULTS_MMPBSA.dat \
    -eo FINAL_RESULTS_MMPBSA.csv \
    -nogui
```

PB suele ser más costoso. Pruebe primero pocos marcos y revise convergencia numérica antes de lanzar el conjunto completo.

### 16. Dieléctricos y fuerza iónica

En PB aparecen:

- **indi**: dieléctrico interno;
- **exdi**: dieléctrico externo;
- **istrng**: fuerza iónica molar.

En GB:

- **intdiel**: dieléctrico interno;
- **extdiel**: dieléctrico externo;
- **saltcon**: concentración salina molar.

No ajuste el dieléctrico interno solo para acercar el resultado a un dato experimental. Puede hacerse un análisis de sensibilidad, por ejemplo con 1, 2 y 4, manteniendo el resto constante.

La fuerza iónica se define:

$$
I=\frac{1}{2}\sum_i c_i z_i^2
$$

Para NaCl ideal 1:1, 0.15 M produce $I=0.15\ \mathrm{M}$. Para una sal divalente la concentración molar y la fuerza iónica no son iguales.

### 17. Radios atómicos

Los radios influyen en la frontera dieléctrica y en el término polar. No son una opción cosmética.

Correspondencias documentadas:

| PBRadii | Conjunto     | Uso típico                                  |
| -------:| ------------ | ------------------------------------------- |
| 1       | bondi        | Asociado habitualmente con igb=7.           |
| 2       | mbondi       | Asociado habitualmente con igb=1.           |
| 3       | mbondi2      | Asociado con igb=2 o 5.                     |
| 4       | mbondi3      | Asociado con igb=8.                         |
| 7       | charmm_radii | Solo PB y topologías preparadas con CHARMM. |

El campo de fuerza de la dinámica y el conjunto de radios del solvente implícito son conceptos distintos. **PBRadii** no cambia los parámetros enlazados ni Lennard-Jones de la topología original.

Para topologías CHARMM, consulte las limitaciones de conversión y valore **charmm_radii** en PB. La documentación advierte que no toda topología producida por CHARMM-GUI queda validada automáticamente.

### 18. Compatibilidad de topologías

**gmx_MMPBSA** convierte la topología GROMACS usando ParmEd. Compruebe cuidadosamente sistemas con:

- parámetros CHARMM y CMAP;
- átomos virtuales;
- dummy atoms;
- puntos de carga extra;
- metales coordinados;
- enlaces covalentes proteína–ligando;
- topologías híbridas;
- lípidos;
- residuos modificados;
- restricciones no convencionales.

La versión actual documenta rutas probadas para topologías representativas Amber, OPLS y CHARMM, pero esto no implica compatibilidad universal.

Siempre inspeccione el log y las topologías intermedias creadas.

### 19. Sistemas de membrana

No elimine la membrana conceptualmente y aplique un modelo acuoso homogéneo sin evaluar el efecto. La versión actual incluye opciones PB para membranas:

```text
&pb
  memopt=1,
  emem=7.0,
  indi=4.0,
  mctrdz=automatic,
  mthick=automatic,
  membrane_atoms="P",
  poretype=1,
  radiopt=0,
  istrng=0.150,
/
```

Es un esquema orientativo. Debe adaptarse a la orientación de la bicapa, nombres de átomos, espesor, presencia de poro y modelo experimental. Una membrana implícita mal centrada puede producir un resultado peor que un modelo acuoso simplificado claramente declarado.

### 20. Entropía

Sin entropía:

$$
\Delta G_{\mathrm{estimada}}
=
\Delta E_{\mathrm{MM}}
+
\Delta G_{\mathrm{solv}}
$$

Con entropía:

$$
\Delta G_{\mathrm{bind}}
=
\Delta H_{\mathrm{aprox}}
-
T\Delta S
$$

Métodos disponibles:

- Interaction Entropy;
- C2 Entropy;
- modos normales, NMODE.

NMODE es costoso y sensible a minimización. El consumo total de memoria crece aproximadamente como:

$$
RAM_{\mathrm{total}}
=
RAM_{\mathrm{por\ marco}}
\times
N_{\mathrm{procesos}}
$$

No paralelice NMODE hasta agotar memoria.

### 21. Interaction Entropy

La aproximación IE usa fluctuaciones de la energía de interacción:

$$
-T\Delta S_{\mathrm{IE}}
=
k_\mathrm{B}T
\ln
\left\langle
\exp
\left[
\beta\,
\Delta E_{\mathrm{int}}
\right]
\right\rangle
$$

con:

$$
\Delta E_{\mathrm{int}}
=
E_{\mathrm{int}}
-
\left\langle E_{\mathrm{int}}\right\rangle
$$

Entrada:

```text
&general
  sys_name="Complejo_IE",
  startframe=1,
  endframe=5000,
  interval=1,
  temperature=300.0,
  PBRadii=4,
  interaction_entropy=1,
  ie_segment=25,
/

&gb
  igb=8,
  saltcon=0.150,
/
```

Debe informarse $\sigma_{IE}$, la desviación de la energía de interacción. La documentación desaconseja IE cuando:

$$
\sigma_{IE}\gtrsim3.6\ \mathrm{kcal\,mol^{-1}}
$$

porque el promedio exponencial se vuelve difícil de converger. Esto equivale aproximadamente a:

$$
3.6\ \mathrm{kcal\,mol^{-1}}
=
15.1\ \mathrm{kJ\,mol^{-1}}
$$

**ie_segment** es un diagnóstico de la cola de la curva acumulativa; no reemplaza el resultado calculado sobre todo el conjunto seleccionado.

### 22. Descomposición por residuos

Genere una plantilla:

```bash
gmx_MMPBSA --create_input gb decomp
```

Ejemplo:

```text
&general
  sys_name="Descomposicion",
  startframe=1,
  endframe=5000,
  interval=10,
  PBRadii=4,
/

&gb
  igb=8,
  saltcon=0.150,
/

&decomp
  idecomp=2,
  dec_verbose=1,
  print_res="within 4",
/
```

Ejecución:

```bash
gmx_MMPBSA -O \
    -i mmpbsa_decomp.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -o FINAL_RESULTS_DECOMP.dat \
    -do FINAL_DECOMP_MMPBSA.dat \
    -eo FINAL_RESULTS_DECOMP.csv \
    -deo FINAL_DECOMP_MMPBSA.csv \
    -nogui
```

**print_res="within 4"** selecciona residuos próximos dentro de 4 Å en la sintaxis del programa. El conjunto impreso debe contener al menos un residuo del receptor y uno del ligando.

La descomposición:

- depende del esquema elegido;
- no es estrictamente única;
- reparte términos colectivos;
- no equivale a una mutación experimental;
- no demuestra causalidad;
- puede variar con radios y dieléctricos.

Úsela para priorizar residuos y formular hipótesis.

### 23. Alanine scanning

El alanine scanning computacional estima el cambio al mutar un residuo:

$$
\Delta\Delta G_{\mathrm{bind}}
=
\Delta G_{\mathrm{bind}}^{\mathrm{mutante}}
-
\Delta G_{\mathrm{bind}}^{\mathrm{WT}}
$$

Interpretación:

- $\Delta\Delta G>0$: la mutación debilita la unión en esta convención;
- $\Delta\Delta G<0$: la mutación la favorece.

Es una mutación end-state sobre estructuras existentes. No reemplaza una dinámica completa del mutante si este reorganiza la proteína.

### 24. Paralelización

Ejecución serial:

```bash
gmx_MMPBSA -O \
    -i mmpbsa_gb.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -nogui
```

Con MPI:

```bash
mpirun -np 4 gmx_MMPBSA -O \
    -i mmpbsa_gb.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -nogui
```

No use **gmx_mpi** dentro de esta ejecución MPI. La documentación indica usar **gmx**, porque las herramientas auxiliares de GROMACS no se benefician del MPI de **mdrun** y pueden entrar en conflicto con **mpirun**.

El escalamiento deja de mejorar cuando el número de procesos se aproxima al número de marcos o domina la carga de topologías.

### 25. Análisis gráfico

```bash
gmx_MMPBSA_ana \
    -f FINAL_RESULTS_MMPBSA.dat
```

El analizador permite revisar términos, evolución temporal, descomposición y exportar gráficos. En HPC use los archivos DAT y CSV, y abra el analizador en una estación con entorno gráfico.

Conserve:

```text
FINAL_RESULTS_MMPBSA.dat
FINAL_RESULTS_MMPBSA.csv
FINAL_DECOMP_MMPBSA.dat
FINAL_DECOMP_MMPBSA.csv
gmx_MMPBSA.log
mmpbsa.in
```

No conserve únicamente una captura del valor final.

### 26. Unidades

Las salidas heredadas de AmberTools suelen expresarse en kcal·mol⁻¹. Verifique siempre el encabezado del archivo.

$$
1\ \mathrm{kcal\,mol^{-1}}
=
4.184\ \mathrm{kJ\,mol^{-1}}
$$

Ejemplo:

$$
-28.6\ \mathrm{kcal\,mol^{-1}}
=
-119.7\ \mathrm{kJ\,mol^{-1}}
$$

No mezcle resultados antiguos de **g_mmpbsa**, que normalmente se informaban en kJ·mol⁻¹, con resultados de **gmx_MMPBSA** sin convertir unidades.

En parámetros PB y GB aparecen además:

- concentración y fuerza iónica en mol·L⁻¹;
- radios y distancias en Å;
- tensión superficial en kcal·mol⁻¹·Å⁻².

### 27. Relación con afinidad experimental

Bajo estados estándar compatibles:

$$
\Delta G^\circ_{\mathrm{bind}}
=
RT\ln K_d
=
-RT\ln K_a
$$

A 298.15 K:

$$
RT=2.47896\ \mathrm{kJ\,mol^{-1}}
=0.59248\ \mathrm{kcal\,mol^{-1}}
$$

Entonces:

$$
K_d=
\exp
\left(
\frac{\Delta G^\circ_{\mathrm{bind}}}{RT}
\right)
$$

Esta conversión solo es válida para una energía libre estándar completa. No convierta directamente un MM/GBSA sin entropía ni correcciones en un $K_d$ “predicho”.

Para rankings, compare correlación y error frente a datos experimentales usando la misma serie química y protocolo.

### 28. Muestreo de marcos

Más marcos muy correlacionados aportan menos información que marcos separados por encima del tiempo de autocorrelación.

Evalúe:

- distancia temporal entre marcos;
- estabilidad del ligando;
- cambios de pose;
- RMSD del sitio;
- bloques tempranos y tardíos;
- réplicas independientes.

Ejemplo conceptual:

```text
0–20 ns
20–40 ns
40–60 ns
60–80 ns
80–100 ns
```

Calcule MM/PBSA por bloque. Una media estable con bloques discrepantes no implica convergencia.

La incertidumbre entre réplicas suele ser más informativa que el error interno calculado sobre marcos correlacionados.

### 29. Sensibilidad del protocolo

Repita una fracción representativa cambiando una variable por vez:

- PB frente a GB;
- conjunto de radios;
- dieléctrico interno;
- fuerza iónica;
- inclusión de agua explícita estructural;
- selección temporal;
- intervalo entre marcos;
- estado de protonación.

Si el ranking cambia completamente ante modificaciones pequeñas y razonables, el resultado no es robusto.

No elija retrospectivamente los parámetros que maximizan correlación sin validación externa: eso equivale a ajustar el método al conjunto.

### 30. Agua estructural

El protocolo estándar elimina agua explícita antes de evaluar el solvente implícito. Algunas aguas del sitio pueden mediar la unión y formar parte del receptor efectivo.

La versión actual incluye ejemplos de ST MM/GBSA con aguas explícitas del receptor. Si se conservan:

- seleccione aguas con criterios reproducibles;
- mantenga identidades o sitios coherentes;
- compruebe ocupación;
- evite incluir aguas transitorias arbitrarias;
- documente si pertenecen al receptor o al solvente.

Una selección fija basada solo en una instantánea puede sesgar el resultado.

### 31. Interpretación de componentes

Una salida típica contiene:

- **VDWAALS**: Lennard-Jones;
- **EEL**: electrostática molecular;
- **EGB** o **EPB**: solvatación polar;
- **ESURF/ENPOLAR/EDISPER**: términos no polares según el modelo;
- **GGAS**: contribución molecular;
- **GSOLV**: contribución de solvatación;
- **TOTAL**: suma reportada.

No interprete cada componente como una magnitud experimental separable. Electrostatica molecular y solvatación polar suelen compensarse fuertemente.

En algunos modos PB, la documentación advierte que la partición entre **GGAS** y **GSOLV** no conserva la interpretación habitual aunque **TOTAL** siga siendo válido. Lea el log antes de interpretar columnas.

### 32. Comparación entre ligandos

Para comparar una serie:

- mismo receptor y estado de protonación;
- mismo campo de fuerza;
- mismo modelo PB/GB;
- mismas opciones y radios;
- temperatura equivalente;
- ventanas temporales comparables;
- número de réplicas similar;
- mismo tratamiento de aguas;
- misma definición del receptor.

Reporte:

$$
\Delta\Delta G_i
=
\Delta G_i-
\Delta G_{\mathrm{referencia}}
$$

Las diferencias relativas suelen ser más útiles que valores absolutos, pero no eliminan sesgos específicos de cada grupo funcional.

### 33. Errores frecuentes

- Confundir g_mmpbsa con gmx_MMPBSA.
- Descargar ejecutables antiguos y copiar **pbsa.py**.
- Usar **pbsa.mdp** con la interfaz nueva.
- Describir MM/PBSA como FEP con λ.
- Afirmar que umbrella sampling es obligatorio.
- Omitir **-cp topol.top** en la versión actual.
- Usar un PDB sin parámetros para el ligando.
- Seleccionar grupos solapados o equivocados.
- Copiar números de grupo de otro sistema.
- Analizar una trayectoria rota por PBC.
- Permitir que el ligando quede lejos del receptor.
- Mezclar topología y TPR con distinto orden atómico.
- Suponer compatibilidad automática de cualquier topología CHARMM.
- Tratar concentración de sal como fuerza iónica para sales multivalentes.
- Elegir dieléctricos para reproducir un resultado esperado.
- Interpretar TOTAL sin conocer sus unidades.
- Convertir un resultado sin entropía directamente en $K_d$.
- Tratar marcos correlacionados como réplicas.
- Usar descomposición como prueba causal.
- Paralelizar NMODE hasta agotar memoria.
- Usar **gmx_mpi** bajo **mpirun** con gmx_MMPBSA.
- Informar muchos decimales sin incertidumbre entre réplicas.

### 34. Controles mínimos

Antes de aceptar el resultado:

- instalación verificada;
- topología convertida sin errores;
- ligando parametrizado;
- grupos comprobados;
- referencia con cadenas correctas;
- trayectoria entera y ajustada;
- marcos posteriores a la equilibración;
- resultado estable por bloques;
- réplicas compatibles;
- sensibilidad a PB/GB o dieléctricos evaluada;
- entropía incluida o ausencia declarada;
- unidades confirmadas;
- componentes interpretados con cautela.

### 35. Información mínima para reproducibilidad

Informe:

- versión de gmx_MMPBSA;
- versiones de GROMACS, AmberTools y ParmEd;
- sistema operativo o entorno;
- campo de fuerza y modelo de agua;
- parametrización del ligando;
- archivos y grupos usados;
- protocolo ST o MT;
- cantidad y separación temporal de marcos;
- bloques namelist completos;
- radios, dieléctricos y fuerza iónica;
- método entrópico;
- número de procesos;
- réplicas;
- unidades;
- criterio de incertidumbre;
- tratamiento de aguas y membranas.

### Fuentes

1. [Inicio y requisitos de gmx_MMPBSA](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/getting-started/)
2. [Instalación actual](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/installation/)
3. [Funcionamiento y preparación de topologías](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/howworks/)
4. [Interfaz de línea de comandos](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/gmx_MMPBSA_command-line/)
5. [Ejemplos oficiales](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/examples/)
6. [Ejemplo proteína–ligando ST](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/examples/Protein_ligand/ST/)
7. [Ejemplo de descomposición](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/examples/Decomposition_analysis/)
8. [Ejemplo de Interaction Entropy](https://valdes-tresanco-ms.github.io/gmx_MMPBSA/dev/examples/Entropy_calculations/Interaction_Entropy/)
9. [Artículo original de gmx_MMPBSA](https://pubs.acs.org/doi/10.1021/acs.jctc.1c00645)
