# Conversor de Topología Molecular para GROMACS

Este script de Python facilita la conversión de topologías moleculares desde el formato CHARMM a formatos compatibles con GROMACS. Permite la generación de archivos `.itp`, `.prm`, `.pdb` y `.top` necesarios para tus simulaciones.

## Requisitos

Asegúrate de tener los siguientes requisitos antes de usar este script:

- Python 2.7.3 o una versión compatible.
- Archivo de topología RTP CHARMM (`rtp_name`).
- Archivo `.mol2` de la molécula de interés (`mol2_name`).
- Directorio que contiene los archivos de fuerza CHARMM36 (`ffdir`).
- Archivo `atomtypes.atp` en el directorio de fuerza CHARMM36 (`ffdir`).

## Uso

Ejecuta el script con los siguientes comandos:

```bash
python script_conversor.py RESNAME drug.mol2 drug.str charmm36.ff
```

Donde:

- `RESNAME`: El nombre de la molécula de interés.
- `drug.mol2`: El archivo `.mol2` de la molécula.
- `drug.str`: El archivo `.str` CHARMM de la molécula.
- `charmm36.ff`: Directorio que contiene los archivos de fuerza CHARMM36.

## Tutorial: Conversión de Topología Molecular

### Paso 1: Preparación de Archivos

Asegúrate de tener los siguientes archivos en el directorio de trabajo:

- El archivo `.mol2` de la molécula de interés (por ejemplo, `drug.mol2`).
- El archivo `.str` CHARMM de la molécula (por ejemplo, `drug.str`).
- Un directorio que contenga los archivos de fuerza CHARMM36 (por ejemplo, `charmm36.ff`).
- Asegúrate de que el archivo `atomtypes.atp` esté presente en el directorio `charmm36.ff`.

### Paso 2: Ejecución del Script

Ejecuta el script de conversión con el siguiente comando, reemplazando los valores entre paréntesis con tus nombres de archivos y directorios:

```bash
python script_conversor.py (RESNAME) (drug.mol2) (drug.str) (charmm36.ff)
```

- `(RESNAME)`: Sustituye con el nombre de la molécula de interés.
- `(drug.mol2)`: Sustituye con el nombre de tu archivo `.mol2`.
- `(drug.str)`: Sustituye con el nombre de tu archivo `.str` CHARMM.
- `(charmm36.ff)`: Sustituye con el nombre del directorio que contiene los archivos de fuerza CHARMM36.

### Paso 3: Resultados

El script generará varios archivos de salida:

- Un archivo `.itp` con la topología molecular de la molécula.
- Un archivo `.prm` con los parámetros adicionales necesarios para la molécula.
- Un archivo `.pdb` inicial de la molécula.
- Un archivo `.top` que debe incluirse en el sistema `.top` de GROMACS.

Puedes utilizar estos archivos en tus simulaciones de GROMACS.

¡La conversión de topología molecular ha sido completada!

## Licencia

Este script se proporciona bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.
