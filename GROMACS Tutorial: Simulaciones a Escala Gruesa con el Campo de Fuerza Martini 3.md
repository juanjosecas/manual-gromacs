# GROMACS Tutorial: Simulaciones a Escala Gruesa con el Campo de Fuerza Martini 3

**Palabras:** 1808 palabras  
**Duración Estimada de Lectura:** 11 minutos  

## Introducción

En este tutorial, exploraremos una técnica fascinante llamada simulaciones a escala gruesa (CG) y veremos cómo ejecutarlas utilizando GROMACS.

## Simulaciones a Escala Gruesa (CG)

Las simulaciones moleculares estándar, aunque son extremadamente valiosas, pueden ser computacionalmente intensivas y consumir mucho tiempo, lo que a menudo limita nuestra capacidad para estudiar procesos de larga escala en biología. Para superar estas limitaciones, han surgido las simulaciones a escala gruesa (CG) como una solución poderosa.

La idea principal detrás de las simulaciones CG es el mapeo de múltiples átomos en una única entidad representativa, a menudo llamada "bead" (cuentas, como las de un rosario). Esto ofrece dos ventajas clave sobre las simulaciones atomísticas:

1. **Reducción del Recuento de Átomos:** En las simulaciones CG, varios átomos se mapean en una única entidad representativa, lo que resulta en un número significativamente menor de átomos en el sistema. Esta reducción en el recuento de átomos permite cálculos más eficientes y simulaciones más rápidas.

2. **Mayores Pasos Temporales:** La simplificación del sistema en las simulaciones CG también permite el uso de pasos temporales más grandes en comparación con las simulaciones atomísticas. Con menos grados de libertad que considerar, las simulaciones CG pueden explorar eficazmente escalas de tiempo más largas, potencialmente hasta 20 fs o incluso más. Este mayor paso temporal contribuye aún más a la aceleración computacional de las simulaciones CG.

La reducción de grados de libertad acelera significativamente la simulación mientras sigue capturando la dinámica esencial del sistema. Esta eficiencia permite la investigación de fenómenos biológicamente relevantes que ocurren en escalas de tiempo más largas, lo que de otro modo sería difícil de simular utilizando modelos atomísticos.

## Flujo de Trabajo de las Simulaciones CG

El flujo de trabajo general de las simulaciones CG no difiere mucho de una simulación MD estándar. La única diferencia radica en el paso inicial, ya que la proteína debe convertirse de una estructura atomística a una estructura CG, pero el resto es bastante similar a una simulación MD estándar, con algunas modificaciones en el archivo mdp.

El flujo de trabajo consta de las siguientes etapas:

1. **Estructura Atomística**
2. **Estructura CG**
3. **Preparación del Sistema**
4. **Minimización**
5. **Equilibración**
6. **Ejecución de Producción**

## Convertir la Estructura a CG con Martinize

Para convertir una estructura atomística en una representación a escala gruesa (CG) utilizando la herramienta Martinize, debemos proporcionar varios indicadores y parámetros. Desglosemos el comando y expliquemos cada indicador en detalle:

```bash
martinize2 -f 1aki_clean.pdb -dssp /home/user/anaconda3/envs/martinize/bin/mkdssp -x 1aki_cg.pdb -o topol.top -ff martini3001 -scfix -cys auto -p backbone -elastic -ef 700.0 -el 0.5 -eu 0.9
```

- **martinize2:** Este es el ejecutable para la herramienta Martinize2.
- **-f 1aki_clean.pdb:** Indica el archivo de estructura atomística de entrada en formato PDB.
- **-dssp /home/user/anaconda3/envs/martinize/bin/mkdssp:** Especifica la estructura secundaria mediante el indicador -dssp (se debe proporcionar una ubicación válida para el ejecutable mkdssp).
- **-x 1aki_cg.pdb:** Establece el nombre del archivo de salida para la estructura CG convertida.
- **-o topol.top:** Define el nombre del archivo de topología que contendrá toda la información sobre el sistema.
- **-ff martini3001:** Selecciona el campo de fuerza Martini 3.
- **-scfix:** Aplica correcciones a las cadenas laterales.
- **-cys auto:** Permite al programa detectar automáticamente los enlaces disulfuro en la proteína y crear restricciones apropiadas.
- **-p backbone:** Define restricciones de posición en el esqueleto (backbone) de la proteína.
- **-elastic:** Activa el modelo de red elástica, que introduce restricciones armónicas entre pares de átomos dentro de una cierta distancia de corte, simulando la conectividad y flexibilidad de la proteína.
- **-ef 700.0, -el 0.5, -eu 0.9:** Controla los parámetros de la red elástica, incluida la constante de fuerza y los límites de corte inferior y superior.

Esta conversión generará tres archivos:

- **La estructura CG (1aki_cg.pdb)**
- **La topología correspondiente (topol.top)**
- **El archivo de parámetros para la proteína (molecule_0.itp). Aquí también encontrarás el comando que usaste para generar los parámetros.**

Comparando la estructura inicial atomística (1aki_clean.pdb) y la estructura CG obtenida (1aki_cg.pdb), notarás fácilmente la diferencia. En la estructura atomística, cada átomo se representa individualmente, conservando el nivel de detalle atomístico. En contraste, la estructura a escala gruesa simplifica la representación agrupando átomos en "beads", reduciendo la complejidad del sistema y permitiendo simulaciones más rápidas.

## Preparación del Sistema con Insane

Una vez obtenida nuestra estructura a escala gruesa (CG), necesitamos preparar el sistema para la simulación. Este proceso típicamente involucra tres pasos esenciales: solvatación, adición de iones para la neutralización del sistema y, opcionalmente, incrustación de la proteína en un entorno de membrana.

Para simplificar este proceso, podemos utilizar la herramienta Insane para construir sistemas CG. Ofrece una variedad de funcionalidades, incluyendo la generación de un sistema solvatado e incrustación de la proteína en una membrana si es necesario. Puedes obtener el script insane.py desde [aquí](url_insane).

Una vez que tengas el script, puedes usarlo para solvatar el sistema con agua y agregar los iones necesarios para la neutralización. Veamos el siguiente comando en Python:

```bash
python2.7 insane.py -f monomer_6cm4_cg.gro -o monomer_6cm4_memb_cg.gro -p topol.top -x 14 -y 14 -z 14 -l POPC:36 -l CHOL:31 -l POPE:22 -l POPS:8 -l POPG:3 -u POPC:36 -u CHOL:31 -u POPE:22 -u POPS:8 -u POPG:3 -sol W:100 -salt 0.15 -sol W:100 -center
```

Explicación de los parámetros:

- **-f 1aki_cg.pdb:** Especifica el archivo de estructura CG de entrada en formato GRO.
- **-p topol.top:** Proporciona el archivo de topología.
- **-o system.gro:** Establece el nombre del archivo de salida para el sistema solvatado en formato GRO.
- **-d 7:** Construye la caja periódica de manera que la distancia entre dos imágenes periódicas sea mayor que 7 nm.
- **-sol W:** Indica el tipo de solvente a agregar al sistema. En este caso, "W" representa moléculas de agua.
- **-salt 0.15:** Agrega iones de sal al sistema. El valor 0.15 representa la concentración de sal deseada en moles por litro (M).

Ejecutando este comando, el script insane.py generará un sistema solvatado con la cantidad especificada de moléculas de agua e iones agregados para neutralizar el sistema. La estructura resultante se guardará como "monomer_6cm4_memb_cg.gro" y se puede utilizar en los pasos subsiguientes de la simulación.

## Modificar los Archivos de Topología (itp)

Los archivos itp para el campo de fuerza Martini 3 se pueden descargar [aquí](url_martini_itp). Por lo general, se almacenan en un directorio llamado "martini_itp". Aquí encontrarás los parámetros generales del campo de fuerza, así como los de agua e iones.

```bash
tar -xvf martini_itp.tar.gz
```

Luego, puedes mover el archivo itp generado previamente por Martinize al directorio mencionado:

```bash
mv molecule_0.itp martini_itp
```

Finalmente, necesitamos modificar el archivo de topología (topol.top) para incluir todos los parámetros necesarios. Aquí se muestra cómo debería ser el archivo:

```bash
#include "martini_itp/martini_v3.0.0.itp"
#include "martini_itp/martini_v3.0.0_solvents_v1.itp"
#include "martini_itp/martini_v3.0.0_ions_v1.itp"
#include "martini_itp/molecule_0.itp"

[ system ]
; name
Insanely solvated protein.

[ molecules ]
; name  number
molecule_0       1
W            10672
NA+            113
CL-            121
```

Ahora estamos listos para continuar con la simulación.

## Simulación

Una vez que hemos preparado el sistema solvatado, podemos proceder con la simulación, que sigue un protocolo similar a una simulación de dinámica molecular (MD) estándar. Los pasos clave incluyen la minimización, la equilibración y la ejecución de producción.

Las únicas diferencias que encontrarás son los archivos mdp para las ejecuciones y la diferencia en el rendimiento en comparación con una simulación atómica.

## Minimización

Comencemos creando un directorio dedicado a la fase de minimización y navegamos a él:

```bash
mkdir minim
cd minim
```

A continuación, deberás descargar el archivo mdp para la ejecución de minimización y copiarlo en este directorio.

Para generar el archivo binario de entrada (tpr) necesario para la ejecución de minimización, ejecuta el siguiente comando:

```bash
gmx_mpi grompp -f minim.mdp -c ../system.gro -r ../system.gro -p ../topol.top -o em.tpr
```

Una vez generado el archivo em.tpr, podemos proceder a ejecutar la simulación de minimización utilizando el siguiente comando:

```bash
gmx_mpi mdrun -v -deffnm em
```

## Equilibración

Después del paso de minimización, podemos proceder con la fase de equilibración de nuestra simulación a escala gruesa (CG). Debido a la mayor estabilidad de los modelos CG, generalmente es suficiente realizar una equilibración aproximada. En este caso, nos enfocaremos en una simulación NPT (número constante de partículas,

 presión y temperatura).

Primero, creamos un directorio para la equilibración y navegamos a él:

```bash
mkdir equil
cd equil
```

Luego, necesitas descargar el archivo mdp para la ejecución de equilibración y copiarlo en este directorio.

Generamos el archivo binario de entrada (tpr) necesario para la ejecución de equilibración con el siguiente comando:

```bash
gmx_mpi grompp -f npt.mdp -c ../em.gro -t ../em.trr -p ../topol.top -o npt.tpr
```

Finalmente, ejecutamos la simulación de equilibración:

```bash
gmx_mpi mdrun -v -deffnm npt
```

## Ejecución de Producción

Una vez que hemos completado la equilibración, estamos listos para llevar a cabo la ejecución de producción de nuestra simulación CG. Esto nos permitirá obtener datos valiosos sobre la dinámica del sistema a escala gruesa.

Primero, creamos un directorio para la producción y navegamos a él:

```bash
mkdir prod
cd prod
```

Descarga el archivo mdp para la ejecución de producción y colócalo en este directorio.

Generamos el archivo binario de entrada (tpr) para la ejecución de producción con el siguiente comando:

```bash
gmx_mpi grompp -f md.mdp -c ../npt.gro -t ../npt.trr -p ../topol.top -o md.tpr
```

Por último, ejecutamos la simulación de producción:

```bash
gmx_mpi mdrun -v -deffnm md
```

## Análisis de Resultados

Después de completar la ejecución de producción, tendrás un archivo de trayectoria (trr) con toda la información de la simulación. Ahora, puedes utilizar herramientas de análisis de GROMACS y scripts personalizados para extraer información relevante, como la dinámica de la proteína, la difusión de lípidos o cualquier otra propiedad de interés.

Recuerda que las simulaciones a escala gruesa (CG) son una herramienta poderosa para estudiar sistemas biomoleculares en escalas de tiempo más largas. Sin embargo, es importante comprender las simplificaciones inherentes en este enfoque y validar los resultados según sea necesario.

## Conclusiones

En este tutorial, hemos explorado el emocionante mundo de las simulaciones a escala gruesa (CG) y cómo llevar a cabo estas simulaciones utilizando GROMACS y el campo de fuerza Martini 3. Estas simulaciones permiten estudiar sistemas biomoleculares en escalas de tiempo más largas y con una reducción significativa en el número de átomos, lo que las hace ideales para investigar procesos biológicamente relevantes.

Hemos cubierto todo el flujo de trabajo, desde la conversión de una estructura atomística en una estructura CG hasta la preparación del sistema, la simulación y el análisis de resultados. Si bien este tutorial proporciona una introducción sólida, te alentamos a explorar más y personalizar tu enfoque según tus necesidades de investigación específicas.
