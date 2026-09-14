# Normas y Ejemplo de Archivo de Topología en GROMACS

*Resumen:*
Este documento presenta las normas y directrices para la creación de archivos de topología en GROMACS, un software ampliamente utilizado en simulaciones de dinámica molecular. Además, se presenta un ejemplo concreto de un archivo de topología para la molécula de urea.

**Introducción:**
La simulación de dinámica molecular es una técnica esencial en la investigación biomolecular y química computacional. La generación precisa de archivos de topología es un paso crucial en la preparación de sistemas moleculares para la simulación. En este documento, se describen las normas y recomendaciones para la creación de archivos de topología en GROMACS, así como un ejemplo detallado de un archivo de topología para la molécula de urea.

**Normas para Archivos de Topología en GROMACS:**
1. *Comentarios y Separadores:* Los comentarios en los archivos de topología se indican mediante el uso del carácter de punto y coma (;). Los separadores de línea se utilizan para comentarios adicionales. Ejemplo:

   ```plaintext
   ; Este es un comentario
   ```

2. *Directivas y Jerarquía de Topología:* Las directivas se delimitan con corchetes [ ]. La topología se organiza en tres niveles: parámetros, moléculas y sistema. Ejemplo:

   ```plaintext
   [ moleculetype ]
   ```

3. *Formato de Items:* Los elementos en el archivo deben separarse mediante espacios o tabulaciones, no comas.

4. *Numeración de Átomos:* Los átomos en las moléculas deben numerarse de manera consecutiva, comenzando en 1.

5. *Grupos de Carga:* Los átomos en el mismo grupo de carga deben estar listados de forma consecutiva.

6. *Nombres de Tipos de Átomos Bondados:* Los nombres de tipos de átomos bondados deben contener al menos un carácter que no sea un dígito.

7. *Definición de Parámetros:* Los elementos deben definirse antes de que se utilicen; no se permiten referencias adelantadas.

8. *Generación de Exclusiones y Fuerzas Bondadas:* Las exclusiones pueden generarse a partir de los enlaces o anularse manualmente. Las fuerzas bondadas pueden generarse a partir de los tipos de átomos o anularse por enlace.

9. *Múltiples Interacciones Bondadas:* Es posible aplicar múltiples interacciones bondadas del mismo tipo en los mismos átomos.

10. *Comentarios y Líneas Vacías:* Se recomienda encarecidamente incluir líneas de comentario descriptivas y líneas vacías en el archivo.

11. *Directivas Múltiples:* A partir de GROMACS 3.1.3, las directivas en el nivel de parámetros pueden usarse varias veces sin restricciones de orden.

12. *Reiniciar con Valores Últimos:* Si se definen parámetros para la misma interacción con combinaciones de tipos de átomos diferentes, se utilizará la última definición.

13. *Uso Significativo de Directivas:* El uso de ciertas directivas sin haber utilizado otras previamente carece de significado y genera advertencias.

14. *Inclusión de Topología de Agua:* Es común incluir la topología de agua al sistema.

15. *Definición del Sistema:* Se debe especificar el nombre del sistema.

**Ejemplo de Archivo de Topología: urea.top**

```plaintext
; Example topology file
; The force-field files to be included
#include "amber99.ff/forcefield.itp"

[ moleculetype ]
; name nrexcl
Urea 3

[ atoms ]
1 C 1 URE C 1 0.880229 12.01000 ; Tipo de átomo C de Amber
2 O 1 URE O 2 -0.613359 16.00000 ; Tipo de átomo O de Amber
3 N 1 URE N1 3 -0.923545 14.01000 ; Tipo de átomo N de Amber
4 H 1 URE H11 4 0.395055 1.00800 ; Tipo de átomo H de Amber
5 H 1 URE H12 5 0.395055 1.00800 ; Tipo de átomo H de Amber
6 N 1 URE N2 6 -0.923545 14.01000 ; Tipo de átomo N de Amber
7 H 1 URE H21 7 0.395055 1.00800 ; Tipo de átomo H de Amber
8 H 1 URE H22 8 0.395055 1.00800 ; Tipo de átomo H de Amber

[ bonds ]
1 2
1 3
1 6
3 4
3 5
6 7
6 8

[ dihedrals ]
; ai aj ak al funct definition
2 1 3 4 9
2 1 3 5 9
2 1 6 7 9
2 1 6 8 9
3 1 6 7 9
3 1 6 8 9
6 1 3 4 9
6 1 3 5 9

[ dihedrals ]
3 6 1 2 4
1 4 3 5 4
1 7 6 8 4

[ position_restraints ]
; ai funct fc
1 1 1000 1000 1000
2 1 1000 0 1000
3 1 1000 0 0

[ dihedral_restraints ]
; ai aj ak al type phi dphi fc
3 6 1 2 1 180 0 10
1 4 3 5 1 180 0 10

[ system ]
Urea in Water

[ molecules ]
; molecule name nr.
Urea 1
SOL 1000
```

**Discusión:**
El ejemplo de archivo de topología `urea.top` sigue las normas y directrices previamente establecidas. Define la topología de la molécula de urea, incluyendo átomos, enlaces, dihedros y restricciones. También se incluye una cantidad de 1000 moléculas de agua (SOL) en el sistema.

**Conclusiones:**
La correcta creación de archivos de topología en GROMACS es esencial para realizar simulaciones de dinámica molecular precisas y confiables. El ejemplo proporcionado ilustra cómo seguir las normas y directrices para definir la topología de una molécula y su entorno en un sistema de simulación.

Este documento ofrece una guía sólida para aquellos que deseen trabajar con archivos de topología en GROMACS, asegurando la integridad y coherencia de las simulaciones moleculares.

Es importante señalar que las normas y directrices pueden evolucionar con las versiones de GROMACS, por lo que se recomienda consultar la documentación oficial para obtener información actualizada.