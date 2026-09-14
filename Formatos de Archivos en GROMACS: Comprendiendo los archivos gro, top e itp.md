# Formatos de Archivos en GROMACS: Comprendiendo los archivos gro, top e itp

En la simulación de dinámica molecular con GROMACS, un software ampliamente utilizado, se emplean formatos de archivo específicos para comunicarse con el usuario y definir las propiedades de las moléculas. Comprender estos formatos es esencial para configurar y analizar simulaciones de manera precisa.

En esta entrada de blog, exploraremos tres formatos de archivo esenciales en GROMACS y proporcionaremos consejos prácticos para trabajar con ellos.

---

## Formato de Archivo gro

El formato de archivo gro es un archivo de texto plano que almacena las coordenadas espaciales y las velocidades (si están disponibles) de los átomos durante una simulación de dinámica molecular. Sigue un formato específico que es crucial para comprender si planeas trabajar con GROMACS.

Un archivo típico comienza con dos líneas como estas:

```plaintext
1
2
```

La primera línea es una entrada simple de Título, que se genera automáticamente cuando se crea el archivo utilizando el comando `gmx trjconv` de GROMACS. Si ese es el caso, la línea contiene información sobre el tiempo y el paso de la simulación. La entrada `t=` especifica el tiempo en picosegundos (ps), mientras que `step=` especifica el número de paso.

La segunda línea especifica el número de átomos en el sistema, lo cual es un parámetro crucial para realizar varios cálculos y tareas de análisis. El número de átomos es un valor entero y debe coincidir con el número de átomos en el sistema.

El resto del archivo funciona de manera similar a un archivo PDB; cada línea en el archivo gro corresponde a un átomo en el sistema y contiene varias columnas con información diferente.

Aquí tienes un ejemplo de cómo podría verse el aminoácido más simple (Glicina) escrito en un archivo gro:

```plaintext
1
2
3
4
5
6
7
243GLY      N 3982   5.064   4.383   7.880 -0.1954  0.1966  0.0028
243GLY      H 3983   5.071   4.375   7.780 -0.6142  2.7367 -0.2744
243GLY     CA 3984   5.106   4.514   7.926  0.4334 -0.0836  0.2363
243GLY    HA2 3985   5.172   4.511   8.013 -3.5828 -1.5010  3.3792
243GLY    HA3 3986   5.160   4.566   7.847  2.4291 -0.7782  1.0870
243GLY      C 3987   4.991   4.608   7.959  0.4018 -0.1763  0.3836
243GLY      O 3988   5.019   4.699   8.036  0.2410  0.2285 -0.0364
```

Tomemos la primera fila y desglosemos lo que significa cada componente:

- **Número de Residuo (5 posiciones, entero):** Especifica el número de residuo (243) al que pertenece el átomo. Es un valor entero con 5 posiciones, indicando el orden secuencial del residuo en la molécula.

- **Nombre de Residuo (5 posiciones, caracteres):** Esta columna contiene el nombre del residuo al que pertenece el átomo. Es una cadena de 5 caracteres que representa el tipo de residuo, "GLY" en nuestro ejemplo.

- **Nombre del Átomo (5 posiciones, caracteres):** Esta columna contiene el nombre del átomo. Es una cadena de 5 caracteres que representa el tipo de átomo, como "CA" para el carbono alfa, "N" para el nitrógeno, entre otros.

- **Número de Átomo (5 posiciones, entero):** Esta columna especifica el número de átomo, que es un identificador único para cada átomo en el sistema. Es un valor entero con 5 posiciones, indicando el orden secuencial del átomo en la molécula.

- **Posición (en nm, x y z en 3 columnas, cada 8 posiciones con 3 decimales):** Esta columna contiene las coordenadas x, y, y z del átomo en nanómetros (nm). Las coordenadas se enumeran en tres columnas, y cada columna tiene 8 posiciones con 3 decimales, lo que permite una alta precisión.

- **Velocidad (en nm/ps, x y z en 3 columnas, cada 8 posiciones con 4 decimales):** Esta columna contiene la velocidad del átomo en nanómetros por picosegundo (nm/ps) o kilómetros por segundo (km/s). También incluye las componentes x, y y z de la velocidad, que se enumeran en tres columnas, y cada columna tiene 8 posiciones con 4 decimales, lo que permite una alta precisión. Si las velocidades no están disponibles, esta columna se puede omitir del archivo.

La última línea de un archivo gro contiene información sobre el tamaño de la caja de simulación. La línea contiene tres números que representan el tamaño de la caja en nanómetros (nm) en las direcciones x, y y z, respectivamente.

Por ejemplo, una línea que se ve así:

```plaintext
  10.37454  10.37454  15.63914
```

especifica una caja de simulación con una longitud de 10.37454 nm en las direcciones x e y y una altura de 15.63914 nm en la dirección z.

Finalmente, recuerda que

, dado que un archivo gro es un archivo de texto que almacena las coordenadas de los átomos, siempre puedes utilizar software de visualización molecular como PyMOL para visualizar la estructura.

## Archivo de Topología en GROMACS (top)

Si tienes experiencia previa en simulación molecular, seguramente habrás oído hablar de la topología de un sistema. Pero, ¿qué es exactamente?

Puedes pensar en el archivo de topología como el equivalente molecular de un currículum. Contiene toda la información importante sobre el sistema que estás estudiando.

Explicado en términos más rigurosos, el archivo de topología es donde defines los parámetros sobre cómo interactúan los átomos de tu molécula entre sí. Esto incluye interacciones enlazadas y no enlazadas, pero también restricciones o exclusiones.

Por lo tanto, puedes ver que es un componente esencial de cualquier simulación molecular, ya que define las interacciones entre átomos, que en última instancia dictan el movimiento del sistema bajo estudio.

En GROMACS, el archivo de topología es un archivo de texto simple caracterizado por la extensión .top (generalmente topol.top) que se puede crear con el comando `gmx pdb2gmx`.

La siguiente pregunta lógica que surge es de dónde provienen estos parámetros.

Si revisaste detenidamente mi blog, la respuesta debería ser bastante clara. Provienen del campo de fuerza. Por eso, después de ejecutar el comando `pdb2gmx`, se te pedirá que selecciones uno, para que GROMACS pueda recuperar los parámetros correspondientes que se utilizarán en tu simulación.

Ahora, veamos cómo podría verse un archivo topol.top típico. Para inspeccionar el contenido del archivo, simplemente puedes abrirlo con un editor de texto plano (vi, nano, etc.). Puedes abrir el código a continuación para ver un ejemplo de archivo de topología.

```plaintext
;   El archivo 'topol.top' fue generado
;   Por usuario: usuario
;   En host: XXX
;   En fecha: 
;
;   Este es un archivo de topología independiente
;
;   Creado por:
;                   :-) GROMACS - gmx pdb2gmx, 2020.5-MODIFICADO (-:
;
;   Ejecutable:   /usr/local/bin/gromacs-2020.5+plumed-2.7.1+PyTorch/bin/gmx
;   Prefijo de datos:  /usr/local/bin/gromacs-2020.5+plumed-2.7.1+PyTorch
;   Directorio de trabajo:  /home/usuario/
;   Línea de comando:
;     gmx pdb2gmx -f ...
;   El campo de fuerza fue leído desde el directorio compartido estándar de GROMACS.
;

; Incluir parámetros del campo de fuerza
#include "amber99sb.ff/forcefield.itp"

[ moleculetype ]
; nombre  nrexcl
Proteína         3

[ átomos ]
; nr    tipo    resnr   residuo  átomo    cgnr    carga  masa
; residuo   1 GLY rtp GLY  q  0.0
1          N      1    GLY      N     61    -0.4157      14.01
2          H      1    GLY      H     62     0.2719      1.008
3         CT      1    GLY     CA     63    -0.0252      12.01
4         H1      1    GLY    HA1     64     0.0698      1.008
5         H1      1    GLY    HA2     65     0.0698      1.008
6          C      1    GLY      C     66     0.5973      12.01
7          O      1    GLY      O     67    -0.5679         16   ; qtot 2

[ enlaces ]
.
.
.

[ pares ]
.
.
.

[ ángulos ]
.
.
.

[ dihedros ]
.
.
.


; Incluir archivo de restricción de posición
#ifdef POSRES
#include "posre.itp"
#endif


; Incluir topología del agua
#include "amber99sb.ff/tip3p.itp"

#ifdef POSRES_WATER
; Restricción de posición para cada oxígeno del agua
[ restricciones_de_posición ]
;  i funct       fcx        fcy        fcz
   1    1       1000       1000       1000
#endif

; Incluir topología de iones
#include "amber99sb.ff/ions.itp"

[ sistema ]
; Nombre
Proteína

[ moléculas ]
; Compuesto        #mols
Proteína             1
```

El archivo generalmente comienza con varias líneas precedidas por un punto y coma `;`, que son comentarios generales.

Después de los comentarios, verás la línea que llama a los parámetros dentro del campo de fuerza que seleccionaste (amber99sb). Esta línea indica que todos los parámetros posteriores se derivan de este campo de fuerza.

```plaintext
#include "amber99sb.ff/forcefield.itp"
```

La siguiente línea importante es [ moleculetype ], que define el nombre y las exclusiones de las moléculas. En el ejemplo dado, la molécula se llama "Proteína" y tiene un valor de nrexcl de 3, lo que significa que excluye las interacciones no enlazadas entre átomos que están a más de 3 enlaces de distancia.

```plaintext
[ moleculetype ]
; nombre  nrexcl
Proteína         3
```

La sección [ átomos ] enumera todos los átomos en la prote

ína, con la información presentada en columnas. Cada fila corresponde a un átomo diferente en la proteína, con detalles como el número de átomo, el tipo, el número de residuo, el nombre del residuo, el nombre del átomo y la carga. En el ejemplo, se informa de un residuo de glicina.

```plaintext
[ átomos ]
; nr    tipo    resnr   residuo  átomo    cgnr    carga  masa
; residuo   1 GLY rtp GLY  q  0.0
1          N      1    GLY      N     61    -0.4157      14.01
2          H      1    GLY      H     62     0.2719      1.008
3         CT      1    GLY     CA     63    -0.0252      12.01
4         H1      1    GLY    HA1     64     0.0698      1.008
5         H1      1    GLY    HA2     65     0.0698      1.008
6          C      1    GLY      C     66     0.5973      12.01
7          O      1    GLY      O     67    -0.5679         16   ; qtot 2
```

Luego tienes otras secciones que especifican otras interacciones como parámetros de [ enlaces ], [ pares ], [ ángulos ] y [ dihedros ].

Las secciones restantes de topol.top definen otras topologías útiles/necesarias. Por ejemplo, el archivo posre.itp define una constante de fuerza utilizada para mantener los átomos en su lugar durante la fase de equilibración.

```plaintext
; Incluir archivo de restricción de posición
#ifdef POSRES
#include "posre.itp"
#endif
```

Finalmente, la directiva [ sistema ] da el nombre del sistema que se escribirá en los archivos de salida durante la simulación, mientras que la directiva [ moléculas ] lista todas las moléculas en el sistema.

```plaintext
[ sistema ]
; Nombre
Proteína

[ moléculas ]
; Compuesto        #mols
Proteína             1
```

Nota:

Es crucial asegurarse de que el orden y los nombres de las moléculas listadas en la directiva [ moléculas ] coincidan exactamente con los del archivo de coordenadas (es decir, el archivo gro).

Por ejemplo, si tu archivo gro contiene una proteína (Proteína), seguida de un ligando (LIG) y una membrana de colesterol (CHL) compuesta por X moléculas, entonces la directiva [ moléculas ] debería ser la siguiente:

```plaintext
[ moléculas ]
; Compuesto        #mols
Proteína             1
LIG                 1
CHL                 X
```

Incluso una pequeña discrepancia en el orden o los nombres de las moléculas entre la directiva [ moléculas ] y el archivo gro resultará en un error.

Además, asegúrate de que los nombres listados coincidan con los nombres de [ moleculetype ], de lo contrario, recibirás errores relacionados con tipos de átomos que no coinciden.

## Archivo ITP en GROMACS

Si observaste detenidamente los archivos anteriores, es posible que te estés preguntando, ¿por qué exactamente se pasan los archivos itp mediante la declaración `#include`?

En las simulaciones de dinámica molecular, los sistemas complejos a menudo involucran un gran número de moléculas con diversas propiedades e interacciones.

Especificar todos los parámetros necesarios para tales sistemas en un solo archivo puede convertirse rápidamente en algo difícil de gestionar. Por esta razón, se considera más práctico utilizar el mecanismo de inclusión para agregar parámetros/moleculetypes utilizando archivos itp.

Por lo tanto, un archivo itp (que significa Include Topology) es simplemente otro archivo de texto que contiene información de topología molecular, como longitudes de enlace, ángulos de enlace, ángulos dihedros y constantes de fuerza, para una molécula específica o un grupo de moléculas. Estos archivos luego se pueden incluir en el archivo de topología principal mediante la directiva `#include`.

Supongamos que tienes un sistema complejo con una proteína, ligandos y varios lípidos que componen tu membrana. Se vuelve evidente que si intentas incorporar todos los parámetros que mostramos anteriormente en un solo archivo, rápidamente se volverá desorganizado.

Por lo tanto, es posible que te encuentres con una topología donde los parámetros para diferentes componentes se agrupan en diferentes archivos itp:

```plaintext
; Incluir parámetros del campo de fuerza
#include "toppar/forcefield.itp"
#include "toppar/PROA.itp"
#include "toppar/LIG.itp"
#include "toppar/CHL.itp"
#include "toppar/DOPC.itp"
#include "toppar/POPE.itp"
#include "toppar/Na+.itp"
#include "toppar/Cl-.itp"
#include "toppar/TP3.itp"

[ sistema ]
; Nombre
Título

[ moléculas ]
; Compuesto  #mols
PROA               1
LIG                1
CHL1              85
DOPC             144
POPE              32
Na+              106
Cl-               72
TP3            26449
```

De inmediato puedes ver que el uso de declaraciones `#include` es útil para hacer que la topología sea más compacta, en lugar de escribir todos los parámetros explícitamente. Como resultado, obtendrás un archivo de topología mucho más limpio.

## Otros archivos en GROMACS

En conclusión, comprender los archivos de topología, itp y gro es crucial para configurar y ejecutar simulaciones de dinámica molecular con GROMACS. Sin embargo, existen otros formatos de archivo con los que debes estar cómodo para diversos propósitos.

Te enlazo a una serie de publicaciones donde los discuto con más detalle:

- Archivo de índice (ndx): se utiliza para agrupar átomos para su uso en diversos análisis.
- Archivo de parámetros mdp: para configurar los parámetros de tu simulación.
- Archivo xvg: GROMACS te proporciona este formato como salida de muchos análisis.
- Formato de archivo pdb
- Archivos xtc y trr: archivos

 de trayectoria que almacenan información sobre la dinámica del sistema a lo largo del tiempo.
- Archivo de energía edr: almacena información sobre las energías del sistema a lo largo de la simulación.
- Archivo de coordenadas compactas (gro g96, etc.): formatos alternativos de archivo de coordenadas.
- Archivo de trayectoria (tpr): el archivo de entrada principal para las simulaciones con GROMACS.

Ten en cuenta que el uso de estos archivos variará según tus necesidades y el tipo de simulación que estés realizando. Sin embargo, comprender la función y el formato de cada uno de ellos te ayudará a aprovechar al máximo las capacidades de GROMACS y a analizar tus resultados de manera efectiva.