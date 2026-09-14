# Tutorial: Crear un archivo .gro para GROMACS utilizando Python

## Introducción

En este tutorial, aprenderemos a crear un archivo .gro que se utiliza en GROMACS, un software de simulación molecular ampliamente utilizado. El archivo .gro contiene información sobre las posiciones iniciales de los átomos en una simulación, así como el tamaño de la caja de simulación. Utilizaremos Python para automatizar este proceso.

## Paso 1: ¿Qué es un archivo .gro?

Un archivo .gro es esencial en GROMACS, ya que contiene información crucial sobre la configuración inicial de la simulación. Su estructura básica es la siguiente:

```textile
Nombre del sistema
número-de-átomos
número-de-residuo nombre-del-residuo nombre-del-átomo número-del-átomo posiciones-del-átomo (x3) # primer átomo
número-de-residuo nombre-del-residuo nombre-del-átomo número-del-átomo posiciones-del-átomo (x3) # segundo átomo
...
número-de-residuo nombre-del-residuo nombre-del-átomo número-del-átomo posiciones-del-átomo (x3) # último átomo
tamaño-de-la-caja (x3)
```

Cada columna debe estar en una posición fija, como se indica en el manual de GROMACS.

## Paso 2: Definición de Residuos

Comenzaremos definiendo los residuos que queremos incluir en nuestro sistema. En este tutorial, utilizamos tres tipos de residuos: SO4_ion (ion sulfato), Na_ion (ion sodio) y H20_molecule (molécula de agua).

Para cada tipo de residuo, definiremos las posiciones de los átomos, los tipos de átomos, los nombres de los átomos y el nombre del residuo.

A continuación, se muestra un ejemplo de cómo se define un residuo (SO4_ion) en Python:

```python
import numpy as np

def SO4_ion():
    Position = np.array([[0.1238,  0.0587,   0.1119], \
        [0.0778,   0.1501,  -0.1263], \
        [-0.0962,   0.1866,   0.0623], \
        [-0.0592,  -0.0506,  -0.0358],\
        [0.0115,   0.0862,   0.0030]])
    Type = ['OS', 'OS', 'OS', 'OS', 'SO']
    Name = ['O1', 'O2', 'O3', 'O4', 'S1']
    Resname = 'SO4'
    return Position, Type, Resname, Name
```

Repetiremos este proceso para los otros dos residuos.

## Paso 3: Definición de Parámetros Básicos

Ahora, definiremos algunos parámetros básicos para nuestra simulación. Esto incluye el tamaño de la caja de simulación (Lx, Ly, Lz), la masa molar del agua (Mh2o), el número total de residuos (ntotal) y la concentración deseada de sal (c).

```python
import numpy as np

# Definir el tamaño de la caja
Lx, Ly, Lz = [3.36]*3
box = np.array([Lx, Ly, Lz])

# Masa molar del agua
Mh2o = 0.018053 # kg/mol - agua

# Número total de residuos
ntotal = 720

# Concentración deseada de sal en mol/L
c = 1.5
```

## Paso 4: Generación de Posiciones para Iones

A continuación, generaremos posiciones aleatorias para los iones (SO4 y Na), asegurándonos de que no haya superposiciones entre ellos ni con otros átomos en el sistema.

```python
import numpy as np
from molecules import SO4_ion, Na_ion

# Agregar SO4 aleatoriamente
atpositions, attypes, resname, atnames = SO4_ion()
while cpt_SO4 < np.int32(nion):
    x_com, y_com, z_com = generate_random_location(box)
    d = search_closest_neighbor(np.array(all_positions), atpositions + np.array([x_com, y_com, z_com]), box)
    if d < dSO4:
        add_residue = False
    else:
        add_residue = True
    if add_residue == True:
        cpt_SO4 += 1
        cpt_residue += 1
        for atposition, attype, atname in zip(atpositions, attypes, atnames):
            cpt_atoms += 1
            x_at, y_at, z_at = atposition
            all_positions.append([x_com+x_at, y_com+y_at, z_com+z_at])
            all_resnum.append(cpt_residue)
            all_resname.append(resname)
            all_atname.append(atname)
            all_attype.append(attype)
```

Este proceso se repite para los iones Na.

## Paso 5: Generación de Posiciones para Moléculas de Agua

Luego, colocaremos las moléculas de agua en una cuadrícula 3D con un espaciado específico, evitando superposiciones.

```python
# Agregar agua en una cuadrícula 3D
atpositions, attypes, resname, atnames = H20_molecule()
for x_com in np.arange(dSol/2, Lx, dSol):
    for y_com in np.arange(dSol/2, Ly, dSol):
        for z_com in np.arange(dSol/2, Lz, dSol):
            d = search_closest_neighbor(np.array(all_positions), atpositions + np.array([x_com, y_com, z_com]), box)
            if d < dSol:
                add_residue = False
            else:
                add_residue = True
            if (add_residue == True) & (cpt_Sol < np.int32(nwater)):
                cpt_Sol += 1
                cpt_residue += 1
                for atposition, attype, atname in zip(atpositions, attypes, atnames):
                    cpt_atoms += 1
                    x_at, y_at, z_at = atposition
                    all_positions.append([x_com+x_at, y_com+y_at, z_com+z_at])
                    all_resnum.append(cpt_residue)
                    all_resname.append(resname)
                    all_atname.append(atname)
                    all_attype.append(attype)
            if cpt_Sol >= np.int32(nwater):
                break
```

## Paso 6: Escritura del Archivo .gro

Finalmente, escribimos todas las posiciones y nombres de los átomos en el archivo .gro, junto con el tamaño de la caja.

```python
# Escribir el archivo .gro
f = open('conf.gro', 'w')
f.write('Solución de Na2SO4\n')
f.write(str(cpt_atoms)+'\n')
cpt = 0
for resnum, resname, atname, position  in zip(all_resnum, all_resname, all_atname, all_positions):
    x, y, z = position
    cpt += 1
    f.write("{: >5}".format(str(resnum))) # número de residuo (5 posiciones, entero)
    f.write("{: >5}".format(resname)) # nombre del residuo (5 caracteres)
    f.write("{: >5}".format(atname)) # nombre del átomo (5 caracteres)
    f.write("{: >5}".format(str(cpt))) # número del átomo (5 posiciones, entero)
    f.write("{: >8}".format(str("{:.3f}".format(x)))) # posición (en nm, x y z en 3 columnas, cada una con 8 posiciones y 3 decimales)
    f.write("{: >8}".format(str("{:.3f}".format(y)))) # posición (en nm, x y z en 3 columnas, cada una con 8 posiciones y 3 decimales)
    f.write("{: >8}".format(str("{:.3f}".format(z)))) # posición (en nm, x y z en 3 columnas, cada una con 8 posiciones y 3 decimales)
    f.write("\n")
f.write("{: >10}".format(str("{:.5f}".format(Lx)))) # tamaño de la caja
f.write("{: >10}".format(str("{:.5f}".format(Ly)))) # tamaño de la caja
f.write("{: >10}".format(str("{:.5f}".format(Lz)))) # tamaño de la caja
f.write("\n")
f.close()
```

## Conclusión

Con este tutorial, hemos creado con éxito un archivo .gro para GROMACS utilizando Python. Este archivo contiene información esencial para nuestras simulaciones moleculares. Puedes usar programas como VMD para visualizar el sistema generado.
