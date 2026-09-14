# PROTOCOLOS DE TRABAJO CON GROMACS 5.X-2021

*Dr. JJ Casal, PhD*

Versión 2023.21.10.9.44

> The greatest obstacle to discovery is not ignorance -- it is the illusion of knowledge.
>
> Never tell people how to do things. Tell them what to do and they will surprise you with their ingenuity.
>
> General George S. Patton
>
> Desordené
> átomos tuyos
> para hacerte aparecer.
>
> Puente - Gustavo Cerati
>
> Jerry, just remember, it's not a lie if you believe it.
>
> George Costanza
>
> Sometimes
> Only sometimes
> I question everything
>
> Sometimes - Depeche Mode
>
> The laughter penetrates my silence
> As drunken men find flaws in science
>
> Set The Fire To The Third Bar - Snow Patrol
>
# Estrategia para la simulación


# Instalación de GROMACS

Esta sección corresponde a **GROMACS 2026.3**. Antes de instalar conviene decidir qué se necesita:

- **Paquete de la distribución:** instalación rápida para aprendizaje, análisis y pruebas. Puede no ser la versión más reciente ni estar optimizado para el hardware.
- **Compilación desde código fuente:** recomendada para producción, GPU, clústeres y control preciso de dependencias.
- **MPI externo:** necesario principalmente para ejecuciones que abarcan varios nodos. Para una sola estación de trabajo, la compilación normal con thread-MPI suele ser suficiente.
- **gmxapi:** interfaz de Python opcional. Requiere primero una instalación compatible de GROMACS.

La guía oficial vigente requiere CMake 3.28 o posterior, un compilador C99 y un compilador C++17. Para GROMACS 2026.3, las versiones mínimas indicadas son GCC 11, Clang 14 o MSVC 2019.

## Comprobación del sistema

Antes de instalar:

~~~bash
uname -a
cmake --version
gcc --version
g++ --version
python3 --version
~~~

Si se utilizará una GPU NVIDIA:

~~~bash
nvidia-smi
nvcc --version
~~~

**nvidia-smi** informa el controlador instalado y la versión máxima de CUDA admitida por ese controlador. **nvcc --version** informa la versión del toolkit usado para compilar. No son la misma cosa.

Según la compatibilidad menor publicada por NVIDIA:

| Familia del toolkit | Controlador mínimo |
|---|---:|
| CUDA 13.x | 580 |
| CUDA 12.x | 525 |
| CUDA 11.x | 450 |

Un controlador más nuevo puede ejecutar aplicaciones compiladas con una familia CUDA anterior mediante compatibilidad hacia atrás. La tabla es un requisito mínimo general; deben revisarse también las notas de la versión concreta del toolkit y la compatibilidad de la GPU.

## Instalación mediante el gestor de paquetes

### Ubuntu y Debian

~~~bash
sudo apt update
sudo apt install gromacs
~~~

Comprobación:

~~~bash
gmx --version
~~~

El paquete disponible depende de la versión de Ubuntu o Debian. Esta vía es adecuada si la versión empaquetada satisface el protocolo. Para simulaciones de producción conviene revisar en la salida de **gmx --version** el soporte SIMD, FFT, MPI y GPU.

### Fedora

~~~bash
sudo dnf install gromacs
~~~

Algunas variantes empaquetadas pueden instalar ejecutables o módulos separados para MPI. Compruebe los nombres proporcionados por la versión de Fedora:

~~~bash
rpm -ql gromacs | grep /bin/
gmx --version
~~~

### Arch Linux y Manjaro

~~~bash
sudo pacman -S gromacs
gmx --version
~~~

### macOS con Homebrew

~~~bash
brew update
brew install gromacs
gmx --version
~~~

La aceleración CUDA no está disponible en macOS. En equipos Apple Silicon, la compilación nativa puede aprovechar SIMD y la GPU solo mediante backends admitidos por la versión de GROMACS y las herramientas disponibles; no debe asumirse que una fórmula de Homebrew incluye aceleración por GPU.

## Windows y WSL2

La ruta más práctica para ejecutar GROMACS en Windows es WSL2 con una distribución Linux. Después de instalar WSL2 y Ubuntu, los comandos de instalación y compilación son los mismos que en Linux.

Desde PowerShell con privilegios de administrador:

~~~powershell
wsl --install -d Ubuntu
wsl --update
~~~

Dentro de Ubuntu:

~~~bash
sudo apt update
sudo apt install gromacs
gmx --version
~~~

Para usar una GPU NVIDIA dentro de WSL2 se necesita un controlador de Windows compatible con WSL; no debe instalarse un controlador Linux NVIDIA dentro de la distribución WSL. El toolkit CUDA de usuario puede instalarse dentro de WSL cuando sea necesario para compilar. Verifique desde WSL:

~~~bash
nvidia-smi
~~~

## Compilación desde código fuente

### Dependencias en Ubuntu o Debian

~~~bash
sudo apt update
sudo apt install build-essential cmake git python3     libfftw3-dev libhwloc-dev
~~~

Para una compilación MPI agregue:

~~~bash
sudo apt install openmpi-bin libopenmpi-dev
~~~

### Dependencias en Fedora

~~~bash
sudo dnf install gcc gcc-c++ cmake make git python3     fftw-devel hwloc-devel
~~~

Para MPI:

~~~bash
sudo dnf install openmpi openmpi-devel
~~~

En Fedora puede ser necesario cargar el entorno de OpenMPI según cómo esté empaquetado:

~~~bash
module load mpi/openmpi-x86_64
~~~

Si el comando **module** no existe o el módulo tiene otro nombre, examine los archivos instalados por el paquete OpenMPI.

### Descarga y compilación básica para CPU

Use una carpeta de compilación separada del código fuente. El prefijo bajo **$HOME/opt** evita requerir permisos de administrador durante la instalación.

~~~bash
wget https://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz
tar xfz gromacs-2026.3.tar.gz
cd gromacs-2026.3

mkdir build
cd build

cmake ..     -DGMX_BUILD_OWN_FFTW=ON     -DREGRESSIONTEST_DOWNLOAD=ON     -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3"

cmake --build . --parallel
ctest --output-on-failure
cmake --install .
~~~

Active la instalación:

~~~bash
source "$HOME/opt/gromacs-2026.3/bin/GMXRC"
gmx --version
~~~

Para cargarla automáticamente al iniciar Bash:

~~~bash
echo 'source "$HOME/opt/gromacs-2026.3/bin/GMXRC"' >> "$HOME/.bashrc"
~~~

**GMX_BUILD_OWN_FFTW=ON** descarga y compila FFTW. Si existe una instalación adecuada de FFTW puede omitirse. La FFTW suministrada por GROMACS es una elección simple y reproducible para una estación de trabajo.

## Compilación con GPU NVIDIA

Primero instale un controlador NVIDIA compatible y el toolkit CUDA siguiendo el método correspondiente a la distribución. No mezcle paquetes CUDA de repositorios incompatibles. Verifique:

~~~bash
nvidia-smi
nvcc --version
~~~

Configure GROMACS con el backend CUDA:

~~~bash
cd gromacs-2026.3
mkdir build-cuda
cd build-cuda

cmake ..     -DGMX_BUILD_OWN_FFTW=ON     -DREGRESSIONTEST_DOWNLOAD=ON     -DGMX_GPU=CUDA     -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3-cuda"

cmake --build . --parallel
ctest --output-on-failure
cmake --install .
~~~

Active y compruebe:

~~~bash
source "$HOME/opt/gromacs-2026.3-cuda/bin/GMXRC"
gmx --version
gmx mdrun -version
~~~

La salida debe indicar que GROMACS fue compilado con soporte CUDA. Que CUDA aparezca en **nvidia-smi** no demuestra que el ejecutable de GROMACS tenga soporte GPU.

Para comprobar el acceso real al dispositivo:

~~~bash
nvidia-smi -L
~~~

La aceleración efectiva depende del tamaño del sistema, el modelo de GPU, CPU, red, configuración PME y opciones de **gmx mdrun**. No se debe forzar la descarga de todas las tareas a GPU sin medir el rendimiento.

## Compilación con MPI para clústeres

La compilación MPI externa se usa para distribuir una simulación entre varios nodos. Puede coexistir con la instalación normal; el ejecutable suele llamarse **gmx_mpi**.

~~~bash
cd gromacs-2026.3
mkdir build-mpi
cd build-mpi

cmake ..     -DGMX_BUILD_OWN_FFTW=ON     -DREGRESSIONTEST_DOWNLOAD=ON     -DGMX_MPI=ON     -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3-mpi"

cmake --build . --parallel
ctest --output-on-failure
cmake --install .
~~~

Comprobación:

~~~bash
source "$HOME/opt/gromacs-2026.3-mpi/bin/GMXRC"
gmx_mpi --version
mpirun -np 2 gmx_mpi --version
~~~

Para combinar MPI y CUDA:

~~~bash
cmake ..     -DGMX_BUILD_OWN_FFTW=ON     -DREGRESSIONTEST_DOWNLOAD=ON     -DGMX_MPI=ON     -DGMX_GPU=CUDA     -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3-mpi-cuda"
~~~

En un clúster deben usarse el lanzador y las variables indicadas por el gestor de trabajos. Un comando local con **mpirun** no sustituye un script de SLURM, PBS u otro planificador.

## Opciones CMake relevantes

| Opción | Uso |
|---|---|
| **-DGMX_MPI=ON** | Compila con MPI externo. |
| **-DGMX_GPU=CUDA** | Activa GPU NVIDIA mediante CUDA. |
| **-DGMX_GPU=OpenCL** | Activa el backend OpenCL. |
| **-DGMX_GPU=SYCL** | Activa el backend SYCL. |
| **-DGMX_SIMD=valor** | Selecciona explícitamente SIMD; normalmente conviene la autodetección. |
| **-DGMX_DOUBLE=ON** | Compila en doble precisión; es más lento y rara vez necesario para dinámica molecular convencional. |
| **-DGMX_FFT_LIBRARY=fftw3** | Selecciona la biblioteca FFT. |
| **-DBUILD_SHARED_LIBS=ON** | Genera bibliotecas compartidas; es necesario para ciertos clientes, incluido gmxapi. |
| **-DCMAKE_INSTALL_PREFIX=ruta** | Define el directorio de instalación. |
| **-DCMAKE_BUILD_TYPE=Debug** | Compilación de depuración; no es adecuada para producción. |

Las opciones antiguas **-DGMX_GPU=ON** y **-DGMX_USE_OPENCL=ON** no deben usarse con GROMACS 2026. El backend se selecciona directamente mediante **-DGMX_GPU=CUDA**, **OpenCL** o **SYCL**.

## Instalación de gmxapi para Python

gmxapi requiere una instalación previa de GROMACS compilada con **GMXAPI=ON** y **BUILD_SHARED_LIBS=ON**. Ambas opciones suelen estar activadas por defecto, pero conviene declararlas cuando se prepara una instalación destinada a Python:

~~~bash
cmake ..     -DGMX_BUILD_OWN_FFTW=ON     -DREGRESSIONTEST_DOWNLOAD=ON     -DGMXAPI=ON     -DBUILD_SHARED_LIBS=ON     -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3"
~~~

Después de instalar GROMACS, cree un entorno virtual. gmxapi admite Python 3.9 o posterior.

~~~bash
python3 -m venv "$HOME/venvs/gmxapi-2026"
source "$HOME/venvs/gmxapi-2026/bin/activate"

python -m pip install --upgrade pip setuptools wheel cmake pybind11
source "$HOME/opt/gromacs-2026.3/bin/GMXRC"
python -m pip install --no-cache-dir gmxapi
~~~

Si el instalador no encuentra GROMACS:

~~~bash
gmxapi_ROOT="$HOME/opt/gromacs-2026.3" python -m pip install --no-cache-dir gmxapi
~~~

Comprobación:

~~~bash
python -c "import gmxapi; print(gmxapi.__version__)"
~~~

Después de actualizar o recompilar GROMACS con otro compilador, MPI o precisión, reinstale gmxapi sin usar la caché. Una rueda compilada contra otra instalación puede importar incorrectamente o fallar por símbolos incompatibles.

## Verificación final

~~~bash
which gmx
gmx --version
gmx mdrun -version
~~~

Compruebe al menos:

- versión exacta de GROMACS;
- compilador y precisión;
- SIMD;
- biblioteca FFT;
- soporte MPI o thread-MPI;
- backend GPU;
- ruta del archivo de datos.

Una prueba mínima del ejecutable no reemplaza los tests:

~~~bash
gmx help
gmx check -h
~~~

Para diagnosticar qué ejecutable se está usando cuando existen varias instalaciones:

~~~bash
type -a gmx
echo "$PATH"
~~~

Si se activa otro entorno, módulo o instalación, ejecute nuevamente el **GMXRC** correspondiente antes de continuar.

## Fuentes

1. [Guía de instalación de GROMACS 2026.3](https://manual.gromacs.org/current/install-guide/index.html)
2. [Instalación de gmxapi](https://manual.gromacs.org/current/gmxapi/userguide/install.html)
3. [Compatibilidad entre CUDA Toolkit y controladores NVIDIA](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)
4. [Guía de instalación de CUDA para Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)

# Caso: 1 proteína - 1 ligando

Este tutorial describe la preparación, simulación y análisis de un complejo proteína–ligando con **GROMACS 2026.3**. Se supone que el ligando ya está colocado en la pose inicial que se desea estudiar.

Los nombres de archivos son ejemplos. Conviene mantener nombres explícitos y una carpeta por etapa:

~~~bash
mkdir -p 00_entrada 01_preparacion 02_em 03_nvt 04_npt 05_md 06_analisis
~~~

## Requisitos básicos

Archivos iniciales:

- **protein.pdb:** estructura de la proteína.
- **ligand.pdb** o **ligand.mol2:** ligando con geometría, estereoquímica, protonación y carga formal revisadas.
- **ligand.itp:** topología del ligando compatible con el campo de fuerza de la proteína.
- **ions.mdp**, **em.mdp**, **nvt.mdp**, **npt.mdp** y **md.mdp:** parámetros de cada etapa.

Antes de procesar la proteína deben revisarse residuos faltantes, conformaciones alternativas, enlaces disulfuro, metales, cofactores, aguas estructurales y estados de protonación. Eliminar automáticamente todos los heteroátomos puede destruir información necesaria.

El ligando debe conservar la pose obtenida por cristalografía, docking u otro procedimiento. Un archivo MOL2 puede contener tipos atómicos y cargas, pero eso no demuestra que sean compatibles con el campo de fuerza seleccionado.

## Unidades utilizadas por GROMACS

| Magnitud | Unidad habitual |
|---|---|
| Distancia | nm |
| Tiempo | ps |
| Temperatura | K |
| Presión | bar |
| Energía | kJ mol⁻¹ |
| Fuerza | kJ mol⁻¹ nm⁻¹ |
| Velocidad | nm ps⁻¹ |
| Constante de fuerza de restricción posicional | kJ mol⁻¹ nm⁻² |

Equivalencias útiles:

$
1\ \mathrm{nm}=10\ \text{Å}
$

$
1\ \mathrm{ps}=10^{-12}\ \mathrm{s},\qquad
1\ \mathrm{ns}=1000\ \mathrm{ps}
$

$
1\ \mathrm{kcal\ mol^{-1}}=4.184\ \mathrm{kJ\ mol^{-1}}
$

No convierta distancias de Å a nm de forma implícita. Una distancia de corte de 1.0 en un archivo MDP significa 1.0 nm, es decir, 10 Å.

## Preparación del ligando

La protonación debe corresponder al pH y al microentorno que se pretende simular. Añadir hidrógenos con una herramienta de conversión no sustituye esta decisión química.

Conversión básica con Open Babel:

~~~bash
obabel -ipdb ligand.pdb -omol2 -O ligand.mol2 -h
~~~

Protonación aproximada a pH 7.4:

~~~bash
obabel -ipdb ligand.pdb -omol2 -O ligand_pH7.4.mol2 -p 7.4
~~~

La opción **-p 7.4** predice una forma de protonación. Para moléculas con tautomería, centros ionizables acoplados o metales, el resultado debe verificarse. También deben revisarse carga formal, orden de enlaces y estereoquímica.

GROMACS no parametriza automáticamente moléculas orgánicas arbitrarias. La topología debe obtenerse con una herramienta apropiada para la familia del campo de fuerza:

- CHARMM: parámetros compatibles con CGenFF/CHARMM.
- AMBER: parámetros compatibles con GAFF u otra metodología AMBER.
- OPLS-AA: tipos y cargas consistentes con OPLS.
- GROMOS: parámetros desarrollados bajo las convenciones GROMOS.

No deben mezclarse tipos atómicos, reglas de combinación, cargas o términos de CHARMM y AMBER sin una transformación validada.

Ejemplo mínimo de un archivo ITP:

~~~ini
[ moleculetype ]
; nombre   nrexcl
LIG        3

[ atoms ]
; nr  type  resnr  residuo  átomo  cgnr  carga  masa
1     CG2R61  1     LIG      C1     1     0.12   12.011
2     NG2R50  1     LIG      N1     2    -0.32   14.007
; ...
~~~

Las líneas iniciadas por punto y coma son comentarios. El nombre definido en **[ moleculetype ]** debe coincidir exactamente con el utilizado en **[ molecules ]**. La suma de las cargas parciales debe reproducir la carga formal esperada dentro de la precisión numérica del modelo.

El valor de **nrexcl** depende de la convención del campo de fuerza. No debe cambiarse solo para eliminar errores de preprocesamiento.

## Preparación de la proteína

Ejecute **pdb2gmx** sobre una copia de la estructura original:

~~~bash
cd 01_preparacion

gmx pdb2gmx     -f ../00_entrada/protein.pdb     -o protein_processed.gro     -p topol.top     -i posre_protein.itp     -water tip3p
~~~

Seleccione el campo de fuerza de manera interactiva o especifíquelo mediante **-ff** si el identificador instalado está documentado:

~~~bash
gmx pdb2gmx     -f ../00_entrada/protein.pdb     -o protein_processed.gro     -p topol.top     -i posre_protein.itp     -ff charmm36-jul2022     -water tip3p
~~~

El nombre disponible puede diferir según los campos de fuerza instalados. Consulte:

~~~bash
gmx pdb2gmx -h
~~~

Evite **-ignh** como opción automática: descarta los hidrógenos presentes y los regenera según las plantillas del campo de fuerza. Puede ser útil, pero también elimina estados de protonación definidos previamente.

Compruebe la estructura:

~~~bash
gmx check -f protein_processed.gro
~~~

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

~~~ini
; Parámetros generales
#include "charmm36-jul2022.ff/forcefield.itp"

; Tipos o parámetros adicionales del ligando, si existen
#include "ligand_atomtypes.itp"

; Topología molecular del ligando
#include "ligand.itp"

; Topología de la proteína generada por pdb2gmx
#include "topol_Protein_chain_A.itp"
~~~

Una sección **[ atomtypes ]** debe aparecer antes de cualquier **[ moleculetype ]** que utilice esos tipos. No incluya el mismo bloque de tipos atómicos más de una vez.

Al final de **topol.top**:

~~~ini
[ system ]
Complejo proteína–ligando

[ molecules ]
; molécula          cantidad
Protein_chain_A     1
LIG                 1
~~~

El orden en **[ molecules ]** debe coincidir con el orden de las moléculas en el archivo de coordenadas. La cantidad representa moléculas, no átomos ni residuos.

## Caja periódica

Para una proteína soluble aproximadamente globular, una caja dodecaédrica reduce el número de moléculas de agua respecto de una caja cúbica:

~~~bash
gmx editconf     -f complex.gro     -o complex_box.gro     -c     -d 1.0     -bt dodecahedron
~~~

**-d 1.0** establece una distancia mínima de 1.0 nm entre el soluto y el límite de la caja. No es una constante universal. Debe ser compatible con los radios de corte y con los movimientos esperados del sistema.

Compruebe el volumen y los vectores de caja:

~~~bash
gmx editconf -f complex_box.gro
~~~

## Solvatación

~~~bash
gmx solvate     -cp complex_box.gro     -cs spc216.gro     -o complex_solv.gro     -p topol.top
~~~

El nombre **spc216.gro** identifica una configuración preequilibrada distribuida con GROMACS. La topología final del agua está determinada por el modelo elegido en **pdb2gmx**, por lo que debe mantenerse la compatibilidad entre campo de fuerza, archivo de agua y topología.

**gmx solvate** actualiza automáticamente el número de moléculas de solvente en **topol.top**. Revise la sección **[ molecules ]** después del comando.

## Neutralización y concentración salina

Archivo **ions.mdp** mínimo:

~~~ini
integrator      = steep
nsteps          = 0
emtol           = 1000.0

cutoff-scheme   = Verlet
coulombtype     = PME
rcoulomb        = 1.0
rvdw            = 1.0
pbc             = xyz
~~~

Genere un TPR temporal:

~~~bash
gmx grompp     -f ions.mdp     -c complex_solv.gro     -p topol.top     -o ions.tpr
~~~

Añada NaCl, neutralice la carga neta y solicite una concentración nominal de 0.15 mol L⁻¹:

~~~bash
gmx genion     -s ions.tpr     -o complex_solv_ions.gro     -p topol.top     -pname NA     -nname CL     -neutral     -conc 0.15
~~~

Seleccione el grupo de solvente, normalmente **SOL**, cuando el programa pregunte qué moléculas reemplazar. No use un número de grupo copiado de otro sistema.

La concentración se relaciona con el número de pares iónicos mediante:

$
N_{\mathrm{pares}} \approx c\,N_A\,V
$

donde **c** es la concentración en mol L⁻¹, (N_A) es la constante de Avogadro y **V** es el volumen en litros. Debido a que el número de iones debe ser entero y la caja es pequeña, la concentración efectiva puede diferir del valor solicitado.

La opción **-neutral** agrega los contraiones necesarios para llevar la carga neta a cero. **-conc 0.15** agrega además la sal correspondiente a la concentración solicitada. Revise la cantidad final de NA y CL en **topol.top**.

## Grupos de índice

Los números de grupo cambian con la composición del sistema. Cree los grupos necesarios y documente las selecciones:

~~~bash
gmx make_ndx -f complex_solv_ions.gro -o index.ndx
~~~

Ejemplo interactivo:

~~~text
r LIG
"Protein" | "LIG"
name 18 Protein_LIG
q
~~~

El número 18 es ilustrativo: debe reemplazarse por el número asignado durante esa sesión. El grupo **Protein_LIG** resulta útil para centrar y visualizar el complejo, pero no crea una única molécula física.

Puede examinar selecciones modernas con:

~~~bash
gmx select     -s complex_solv_ions.gro     -select 'group "Protein" or resname LIG'
~~~

## Restricciones de posición del ligando

Genere las restricciones usando una estructura que contenga solamente el ligando y cuyo orden atómico coincida con **ligand.itp**:

~~~bash
gmx genrestr     -f ligand.gro     -o posre_ligand.itp     -fc 1000 1000 1000
~~~

Seleccione **LIG**. Los índices del archivo de restricciones son locales al **[ moleculetype ]**. Si se usa la estructura completa y se generan índices globales, las restricciones pueden apuntar a átomos incorrectos.

Incluya el archivo inmediatamente después de la topología del ligando:

~~~ini
#include "ligand.itp"

#ifdef POSRES_LIG
#include "posre_ligand.itp"
#endif
~~~

El valor 1000 corresponde a 1000 kJ mol⁻¹ nm⁻² en cada eje. La energía armónica de una restricción unidimensional es:

$
V(x)=\frac{1}{2}k(x-x_0)^2
$

donde **k** es la constante de fuerza y (x_0) la posición de referencia.

Active las restricciones desde el MDP:

~~~ini
define = -DPOSRES -DPOSRES_LIG
~~~

El archivo indicado mediante **gmx grompp -r** proporciona las coordenadas de referencia. Las restricciones se usan normalmente durante la equilibración y se eliminan en producción.

## Minimización de energía

Archivo **em.mdp**:

~~~ini
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
~~~

Preprocese y ejecute:

~~~bash
mkdir -p ../02_em
cd ../02_em

gmx grompp     -f ../01_preparacion/em.mdp     -c ../01_preparacion/complex_solv_ions.gro     -p ../01_preparacion/topol.top     -o em.tpr

gmx mdrun -deffnm em -v
~~~

El criterio **emtol = 1000** significa que la minimización puede finalizar cuando la fuerza máxima sea menor que 1000 kJ mol⁻¹ nm⁻¹. Este valor es habitual antes de equilibrar, pero no garantiza que la estructura represente un mínimo profundo.

Extraiga la energía potencial:

~~~bash
(echo Potential; echo 0) |
gmx energy -f em.edr -o ../06_analisis/em_potential.xvg
~~~

Compruebe:

- descenso de la energía potencial;
- ausencia de valores NaN;
- fuerza máxima final;
- átomo sobre el cual actúa la fuerza máxima;
- advertencias de LINCS o contactos anómalos.

No use **-maxwarn** para ocultar advertencias de **grompp**. Debe entenderse la causa antes de continuar.

## Equilibración NVT

En NVT se estabiliza la temperatura manteniendo fijo el volumen. Ejemplo a 300 K durante 100 ps:

~~~ini
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
~~~

El tiempo simulado es:

$
t_{\mathrm{total}}=\mathrm{dt}\times\mathrm{nsteps}
$

En este ejemplo:

$
0.002\ \mathrm{ps}\times 50000=100\ \mathrm{ps}
$

Con restricciones sobre enlaces con hidrógeno, un paso de 0.002 ps equivale a 2 fs.

Ejecución:

~~~bash
mkdir -p ../03_nvt
cd ../03_nvt

gmx grompp     -f ../01_preparacion/nvt.mdp     -c ../02_em/em.gro     -r ../02_em/em.gro     -p ../01_preparacion/topol.top     -n ../01_preparacion/index.ndx     -o nvt.tpr

gmx mdrun -deffnm nvt -v
~~~

Las velocidades se generan una sola vez. Para las etapas posteriores se conserva el estado mediante el checkpoint.

Análisis de temperatura:

~~~bash
(echo Temperature; echo 0) |
gmx energy -f nvt.edr -o ../06_analisis/nvt_temperature.xvg
~~~

La temperatura debe evaluarse como serie temporal y promedio, no por un único valor final.

## Equilibración NPT

En NPT se ajustan presión, volumen y densidad. Ejemplo de 500 ps con barostato C-rescale:

~~~ini
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
~~~

**ref-p = 1.0** significa 1 bar. **compressibility = 4.5e-5 bar⁻¹** es un valor habitual para agua líquida cerca de condiciones ambientales; debe adaptarse si el medio no es agua.

Ejecución:

~~~bash
mkdir -p ../04_npt
cd ../04_npt

gmx grompp     -f ../01_preparacion/npt.mdp     -c ../03_nvt/nvt.gro     -r ../03_nvt/nvt.gro     -t ../03_nvt/nvt.cpt     -p ../01_preparacion/topol.top     -n ../01_preparacion/index.ndx     -o npt.tpr

gmx mdrun -deffnm npt -v
~~~

Extraiga presión y densidad:

~~~bash
(echo Pressure; echo Density; echo 0) |
gmx energy -f npt.edr -o ../06_analisis/npt_pressure_density.xvg
~~~

La presión instantánea fluctúa mucho en sistemas pequeños. Evalúe promedios por bloques, densidad y volumen. Si existe una deriva sistemática, prolongue la equilibración desde el checkpoint.

## Dinámica molecular de producción

Durante producción se retiran las restricciones posicionales, salvo que formen parte explícita del protocolo. El siguiente MDP describe 100 ns:

~~~ini
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
~~~

Con 2 fs por paso:

$
50000000\times 0.002\ \mathrm{ps}
=100000\ \mathrm{ps}
=100\ \mathrm{ns}
$

Ejecución:

~~~bash
mkdir -p ../05_md
cd ../05_md

gmx grompp     -f ../01_preparacion/md.mdp     -c ../04_npt/npt.gro     -t ../04_npt/npt.cpt     -p ../01_preparacion/topol.top     -n ../01_preparacion/index.ndx     -o md.tpr

gmx mdrun -deffnm md -v
~~~

Archivos principales:

| Archivo | Contenido |
|---|---|
| **md.tpr** | Topología, parámetros, coordenadas y estado de entrada. |
| **md.xtc** | Coordenadas comprimidas. |
| **md.edr** | Energías y variables termodinámicas. |
| **md.log** | Registro detallado de la ejecución. |
| **md.cpt** | Checkpoint para continuar. |
| **md.gro** | Coordenadas finales. |
| **md.trr** | Coordenadas, velocidades o fuerzas en precisión completa, si se solicitaron. |

No es necesario generar TRR si el análisis no requiere velocidades, fuerzas o coordenadas de precisión completa.

## Continuación y extensión

Para reanudar una ejecución interrumpida:

~~~bash
gmx mdrun -deffnm md -cpi md.cpt -append
~~~

**-append** verifica y continúa los archivos existentes. Use **-noappend** solo cuando necesite segmentos separados.

Si el TPR agotó el número de pasos, extiéndalo. **-extend** se expresa en picosegundos:

~~~bash
gmx convert-tpr     -s md.tpr     -extend 50000     -o md_extended.tpr

gmx mdrun     -s md_extended.tpr     -deffnm md     -cpi md.cpt     -append
~~~

Aquí se agregan 50000 ps, equivalentes a 50 ns.

Concatenación de segmentos XTC:

~~~bash
gmx trjcat     -f md.part0001.xtc md.part0002.xtc     -o md_complete.xtc
~~~

Revise el orden y los tiempos. La concatenación no corrige superposiciones temporales ni discontinuidades físicas.

## Corrección de condiciones periódicas

Las condiciones periódicas pueden separar visualmente moléculas que continúan próximas. No existe una única secuencia válida para todos los sistemas. Para un complejo soluble:

~~~bash
echo System |
gmx trjconv     -s md.tpr     -f md.xtc     -o md_whole.xtc     -pbc whole
~~~

Trayectoria sin saltos, útil para difusión:

~~~bash
echo System |
gmx trjconv     -s md.tpr     -f md_whole.xtc     -o md_nojump.xtc     -pbc nojump
~~~

Centre el complejo y lleve las moléculas a una caja compacta:

~~~bash
(echo Protein_LIG; echo System) |
gmx trjconv     -s md.tpr     -f md_whole.xtc     -o md_center.xtc     -center     -pbc mol     -ur compact     -n index.ndx
~~~

Elimine rotación y traslación ajustando el backbone:

~~~bash
(echo Backbone; echo System) |
gmx trjconv     -s md.tpr     -f md_center.xtc     -o md_fit.xtc     -fit rot+trans     -n index.ndx
~~~

El orden importa: no aplique **-pbc nojump** después de centrar. Inspeccione visualmente la trayectoria final.

Extracción de una estructura a 50 ns:

~~~bash
echo Protein_LIG |
gmx trjconv     -s md.tpr     -f md_fit.xtc     -o frame_50ns.pdb     -dump 50     -tu ns     -n index.ndx
~~~

## Análisis de resultados

Use el mismo intervalo de producción, tratamiento de PBC y selección en todas las réplicas. Los archivos XVG son texto y pueden analizarse con Grace, Python, R u otro programa.

### RMSD

El RMSD mide la desviación respecto de una referencia después del ajuste:

$
\mathrm{RMSD}(t)=
\sqrt{\frac{1}{M}\sum_i m_i
\left\|\mathbf r_i(t)-\mathbf r_i^{\mathrm{ref}}\right\|^2}
$

donde **M** es la masa total de los átomos seleccionados. Una meseta indica estabilidad relativa frente a esa referencia, no convergencia termodinámica.

~~~bash
mkdir -p ../06_analisis/rmsd

(echo Backbone; echo Backbone) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o ../06_analisis/rmsd/rmsd_backbone.xvg     -tu ns
~~~

RMSD del ligando después de ajustar la proteína:

~~~bash
(echo Backbone; echo LIG) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o ../06_analisis/rmsd/rmsd_ligand_fit_protein.xvg     -tu ns
~~~

### Radio de giro

~~~bash
gmx gyrate     -s md.tpr     -f md_fit.xtc     -n index.ndx     -sel 'group "Protein"'     -o ../06_analisis/gyrate_protein.xvg
~~~

El radio de giro informa sobre la compacidad global. Debe interpretarse junto con RMSD, estructura secundaria y contactos internos.

### Distancias y contactos proteína–ligando

Distancia entre el centro geométrico del ligando y un átomo de referencia:

~~~bash
gmx distance     -s md.tpr     -f md_fit.xtc     -n index.ndx     -select 'com of group "LIG" plus com of resid 123 and name CA'     -oall ../06_analisis/dist_lig_res123.xvg
~~~

El residuo 123 es un ejemplo y debe reemplazarse. Para distancia mínima y número de contactos:

~~~bash
(echo Protein; echo LIG) |
gmx mindist     -s md.tpr     -f md_fit.xtc     -n index.ndx     -od ../06_analisis/mindist_protein_lig.xvg     -on ../06_analisis/contacts_protein_lig.xvg     -d 0.4
~~~

**-d 0.4** establece un umbral de contacto de 0.4 nm, equivalente a 4 Å. Debe informarse el umbral utilizado.

### Puentes de hidrógeno

GROMACS 2026 incluye la implementación moderna de **gmx hbond**, incorporada inicialmente en GROMACS 2024:

~~~bash
gmx hbond     -s md.tpr     -f md_fit.xtc     -n index.ndx     -r 'group "Protein"'     -t 'group "LIG"'     -num ../06_analisis/hbonds_protein_lig.xvg
~~~

Las selecciones de referencia y objetivo deben ser idénticas o no solaparse. Los valores recomendados por la herramienta son 0.35 nm para distancia y 30 grados para el criterio angular. Si se modifican, deben reportarse.

### Contactos iónicos

Un contacto corto entre grupos cargados puede estudiarse mediante selecciones explícitas:

~~~bash
gmx pairdist     -s md.tpr     -f md_fit.xtc     -n index.ndx     -ref 'group "Protein_charged"'     -sel 'group "LIG_charged"'     -type min     -o ../06_analisis/ion_pairs.xvg
~~~

Los grupos **Protein_charged** y **LIG_charged** deben construirse previamente según los átomos efectivamente cargados. Una distancia corta no demuestra por sí sola una interacción energéticamente favorable.

### Área accesible al solvente

~~~bash
gmx sasa     -s md.tpr     -f md_fit.xtc     -n index.ndx     -surface 'group "Protein_LIG"'     -output 'group "Protein_LIG"'     -o ../06_analisis/sasa_complex.xvg     -or ../06_analisis/sasa_per_residue.xvg
~~~

SASA depende de la selección, los radios atómicos y la sonda. Una disminución del área expuesta del ligando puede acompañar su enterramiento, pero no equivale a energía de unión.

### Variables termodinámicas

~~~bash
(echo Temperature; echo Pressure; echo Density; echo Volume; echo Potential; echo 0) |
gmx energy     -f md.edr     -o ../06_analisis/thermodynamics.xvg
~~~

Los nombres disponibles dependen del contenido de EDR. Evalúe promedios por bloques y deriva temporal. La presión instantánea suele presentar fluctuaciones grandes.

### Desplazamiento cuadrático medio

**gmx msd** usa selecciones modernas:

~~~bash
gmx msd     -s md.tpr     -f md_nojump.xtc     -n index.ndx     -sel 'group "LIG"'     -o ../06_analisis/msd_ligand.xvg
~~~

Difusión lateral en el plano XY:

~~~bash
gmx msd     -s md.tpr     -f md_nojump.xtc     -n index.ndx     -sel 'group "LIG"'     -lateral z     -o ../06_analisis/msd_ligand_xy.xvg
~~~

La estimación del coeficiente de difusión se basa en la región lineal de la relación de Einstein:

$
\left\langle |\mathbf r(t)-\mathbf r(0)|^2\right\rangle=2dDt
$

donde **d** es la dimensionalidad: 3 para difusión tridimensional y 2 para difusión lateral. Debe elegirse un intervalo de ajuste en el régimen difusivo; el tramo inicial balístico y las regiones con muestreo insuficiente sesgan el resultado.

### Mapas de densidad

~~~bash
echo LIG |
gmx densmap     -s md.tpr     -f md_fit.xtc     -n index.ndx     -od ../06_analisis/density_ligand.xpm     -aver z
~~~

El sistema debe estar alineado previamente. Informe el eje promediado, la resolución de la grilla y la selección.

### Fluctuación de los residuos

La RMSF mide la fluctuación de cada átomo alrededor de su posición promedio:

$
\mathrm{RMSF}_i=
\sqrt{
\left\langle
\left\|\mathbf r_i(t)-\langle\mathbf r_i\rangle\right\|^2
\right\rangle}
$

Primero ajuste la trayectoria sobre una región estructuralmente estable:

~~~bash
mkdir -p ../06_analisis/rmsf

echo Backbone |
gmx trjconv     -s md.tpr     -f md_center.xtc     -o ../06_analisis/rmsf/md_fit_backbone.xtc     -fit rot+trans     -n index.ndx
~~~

Calcule RMSF por residuo usando C-alpha:

~~~bash
echo C-alpha |
gmx rmsf     -s md.tpr     -f ../06_analisis/rmsf/md_fit_backbone.xtc     -n index.ndx     -o ../06_analisis/rmsf/rmsf_calpha.xvg     -res     -oq ../06_analisis/rmsf/rmsf_calpha_bfactor.pdb
~~~

**-oq** escribe los valores convertidos al campo B del PDB. La relación isotrópica es:

$
B_i=\frac{8\pi^2}{3}\mathrm{RMSF}_i^2
$

Para evaluar estabilidad temporal, compare bloques de igual duración:

~~~bash
echo C-alpha |
gmx rmsf     -s md.tpr     -f ../06_analisis/rmsf/md_fit_backbone.xtc     -n index.ndx     -b 20     -e 40     -tu ns     -res     -o ../06_analisis/rmsf/rmsf_20_40ns.xvg

echo C-alpha |
gmx rmsf     -s md.tpr     -f ../06_analisis/rmsf/md_fit_backbone.xtc     -n index.ndx     -b 40     -e 60     -tu ns     -res     -o ../06_analisis/rmsf/rmsf_40_60ns.xvg
~~~

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

# Simulación de una caja de agua

Vamos a simular un sistema compuesto por agua. Puede ser que nos sirva para simular sistemas sencillos y así testear la instalación de GROMACS o estudiar variables.

Múltiples moléculas de ligandos y de proteínas

Caso: 1OKE y BOG

Es necesario, en ocasiones, calcular la dinámica de múltiples ligandos o tomar en cuenta cofactores que no son metales. El problema escala en dificultad y en tener más cuidado con qué se hace cada paso.

NOTA: un caso más complejo se explica más adelante. Tal vez convenga leer las notas de este y luego usar el otro como ejercicio real.

Consideremos a la proteína 1OKE que consiste en dos cadenas, A y B, que están acompañadas por ocho moléculas, de las cuales dos son BOG unidas al sitio correspondiente a cada cadena. Ambas moléculas son idénticas, esto es, los BOG poseen los mismos tipos de átomos pero diferente conformación y posición.


Esto nos plante la pregunta: ¿las moléculas son idénticas? Sí. Son las mismas clases de átomos en ambas, sólo varían dónde están. Para generar la topología de ambas moléculas, puedo usar el MOL2 de cualquiera de ellas y emplear SwissParam para obtener el ITP y el PDB. Sin embargo, el ITP va a contener los mismos parámetros. Esto es clave[^39].

Si extraigo ambos BOG, uno llamado BOGA.mol2 y otro BOGB.mol2, obtendré BOGA.pdb y BOGB.pdb con los correspondientes ITP con el SwissParam. Edito cada PDB

BOGA.pdb:

ATOM      1  C1  LIG     1     -14.258  79.953  45.302  1.00  0.00      LIG

ATOM      2  O1  LIG     1     -13.074  79.344  45.814  1.00  0.00      LIG

ATOM      3  C2  LIG     1     -15.153  78.753  44.866  1.00  0.00      LIG

Cambiar LIG a BOA

BOGA.itp:

[ moleculetype ]

; Name nrexcl

BOGA 3

[ atoms ]

; nr type resnr resid atom cgnr charge mass

`   `1 CR   1  LIG C1      1  0.5600  12.0110

Cambiar LIG a BOA y BOGA a BOA

BOGB.pdb

ATOM      1  C1  LIG     1     -17.418  58.852   3.720  1.00  0.00      LIG

ATOM      2  O1  LIG     1     -16.140  59.295   3.262  1.00  0.00      LIG

ATOM      3  C2  LIG     1     -18.015  60.210   4.211  1.00  0.00      LIG

ATOM      4  O2  LIG     1     -17.189  60.761   5.241  1.00  0.00      LIG

Cambiar LIG a BOB

El BOGB.itp no lo usaremos.¿Por qué?

Generamos la topología de la proteína sin residuos protein.pdb y obtenemos protein-complex.pdb. En topol.top haré los siguientes cambios

; Include forcefield parameters

#include "charmm27.ff/forcefield.itp"

; topologia del ligando

#include "BOGA.itp"

; Include chain topologies

#include "topol\_Protein\_chain\_A.itp"

#include "topol\_Protein\_chain\_B.itp”

Sólo necesito indicar el ITP de un BOG, ya que ambos son idénticos. En la sección de las moléculas edito

[ molecules ]

; Compound        #mols

Protein\_chain\_A     1

Protein\_chain\_B     1

BOA                 2

Si bien tengo BOA y BOB, ambas tienen la misma topología. Entonces tengo DOS moléculas, aunque estén en lugares distintos. Ahora debemos editar el archivo protein-complex.pdb. Pondremos, luego del aminoácido TER de la cadena B, las coordenadas ATOM de los PDB de BOGA.pdb y BOGB.pdb que ya editamos.

TER

ATOM      1  C1  BOA     1     -14.258  79.953  45.302  1.00  0.00      BOA

ATOM      2  O1  BOA     1     -13.074  79.344  45.814  1.00  0.00      BOA

ATOM      3  C2  BOA     1     -15.153  78.753  44.866  1.00  0.00      BOA

...

...

...

ATOM     47 H8'3 BOA     1      -4.590  80.022  47.691  1.00  0.00      BOA

ATOM     48  HO2 BOA     1     -15.053  77.315  43.523  1.00  0.00      BOA

TER      49      BOA      1

ATOM      1  C1  BOB     1     -17.418  58.852   3.720  1.00  0.00      BOB

ATOM      2  O1  BOB     1     -16.140  59.295   3.262  1.00  0.00      BOB

ATOM      3  C2  BOB     1     -18.015  60.210   4.211  1.00  0.00      BOB

...

...

...

ATOM     46 H8'2 BOB     1      -7.367  57.375   2.492  1.00  0.00      BOB

ATOM     47 H8'3 BOB     1      -8.123  56.758   1.004  1.00  0.00      BOB

ATOM     48  HO2 BOB     1     -17.524  61.625   5.492  1.00  0.00      BOB

TER      49      BOB      1

ENDMDL

Solvatación y neutralización se hacen como en los casos normales. Lo mismo para la minimización energética. Una vez hecha la EM, debemos generar las restraints para los dos ligandos y la proteína. Antes era automático en el sentido que había sólo dos moléculas, pero ahora hay que ser explícito, porque hay DOS cadenas y DOS ligandos.

Para BOGB.pdb:

| gmx genrestr -f BOGB.pdb -o posre\_BOGB.itp -fc 1000 1000 1000 |
| -------------------------------------------------------------- |

Reading structure file

Select group to position restrain

Group     0 (         System) has    48 elements

Group     1 (          Other) has    48 elements

Group     2 (            BOB) has    48 elements

Select a group: 2

Selected 2: 'BOB'

y

para BOGA.pdb

| gmx genrestr -f BOGA.pdb -o posre\_BOGA.itp -fc 1000 1000 1000 |
| -------------------------------------------------------------- |

Reading structure file

Select group to position restrain

Group     0 (         System) has    48 elements

Group     1 (          Other) has    48 elements

Group     2 (            BOA) has    48 elements

Select a group: 2

Selected 2: 'BOA'

Editamos topol.top

; Include chain topologies

#include "topol\_Protein\_chain\_A.itp"

#include "topol\_Protein\_chain\_B.itp"

; Include Position restraint file proteina

#ifdef POSRES

#include "posre\_Protein\_chain\_A.itp"

#endif

; Include Position restraint file proteina

#ifdef POSRES

#include "posre\_Protein\_chain\_B.itp"

#endif

; Ligand position restraints BOGA

#ifdef POSRES

#include "posre\_BOGA.itp"

#endif

; Ligand position restraints BOGA

#ifdef POSRES

#include "posre\_BOGB.itp"

#endif

; Include water topology

#include "charmm27.ff/tip3p.itp

Edito el nvt.mdp

define      = -DPOSRES

…

energygrps  = Protein BOA

Proceder en forma usual.

Deberá tenerse en cuenta si trabajaremos con grupos o no y si usaremos las restraints. En el caso anterior, ya tomé en cuenta las restraints ya que forcé a tomarlas en cuenta al definir el POSRES. El trabajo con múltiples moléculas refuerza la necesidad de usar el archivo de definición de grupos index.ndx.

A continuación, un ejemplo con múltiples cadenas y dos moléculas del ligando

Influenza A M2 transmembrane domain bound to amantadine

6BKK.

DOI: 10.2210/pdb6BKK/pdb

Classification: MEMBRANE PROTEIN

Organism(s): Influenza A virus (strain A/Udorn/1972 H3N2)


La molécula cristalizada posee un catión y dos moléculas idénticas de amadantina.


La estructura en 3D de cada cadena y ligando es,


Extraigo ambas moléculas, las salvo en formato PDB desde Chimera. Separo las moléculas con un editor de texto y las transformo en MOL2 a través de Openbabel. Se obtienen los PDB e ITP correspondientes a ambas moléculas. Los ITP para ambas deberán contener la misma información, ya que son moléculas idénticas.

Topología de la proteína

| gmx pdb2gmx -f protein.pdb -ff charmm27 -water tip3p -ignh -o protein-complex.pdb |
| --------------------------------------------------------------------------------- |

Creación del complejo ligandos-proteína

Luego, agrego un sólo ITP ya que ambos tienen la misma información

;    Force field was read from the standard GROMACS share directory.

;

; Include forcefield parameters

#include "charmm27.ff/forcefield.itp"

;ligandos, le dejé este nombre porque me confundí, pero no cambia nada

#include "ligand1.itp"

; Include chain topologies

#include "topol\_Protein\_chain\_A.itp"

#include "topol\_Protein\_chain\_B.itp"

#include "topol\_Protein\_chain\_C.itp"

#include "topol\_Protein\_chain\_D.itp"

#include "topol\_Protein\_chain\_E.itp"

#include "topol\_Protein\_chain\_F.itp"

#include "topol\_Protein\_chain\_G.itp"

#include "topol\_Protein\_chain\_H.itp"

; Include water topology

#include "charmm27.ff/tip3p.itp"

...

...

Agregar DOS moléculas de LIG

...

...

[ molecules ]

; Compound        #mols

Protein\_chain\_A     1

Protein\_chain\_B     1

Protein\_chain\_C     1

Protein\_chain\_D     1

Protein\_chain\_E     1

Protein\_chain\_F     1

Protein\_chain\_G     1

Protein\_chain\_H     1

LIG                 2

Agregado de las coordenadas de cada ligando al archivo protein-complex.pdb. Deberíamos cambiar la numeración de cada ligando.

ATOM   3255  OT1 LEU H  46      58.573  24.017  55.778  1.00  0.00           O

ATOM   3256  OT2 LEU H  46      58.474  24.287  55.844  1.00  0.00

TER

ATOM      1  N1  LIG     1      68.571  10.462  72.970  1.00  0.00      LIG

ATOM      2  C10 LIG     1      69.949  10.240  73.367  1.00  0.00      LIG

ATOM      3  C7  LIG     1      70.850  11.256  72.670  1.00  0.00      LIG

ATOM      4  C1  LIG     1      72.300  11.024  73.090  1.00  0.00      LIG

ATOM      5  C8  LIG     1      70.073  10.402  74.880  1.00  0.00      LIG

...

...

TOM     27  H15 LIG     1      73.741   9.451  72.990  1.00  0.00      LIG

ATOM     28  H16 LIG     1      72.641   9.499  71.633  1.00  0.00      LIG

TER      29      LIG      1

ATOM      1  N1  LIG     2      68.780  10.283  47.255  2.00  0.00      LIG

ATOM      2  C10 LIG     2      67.420  10.497  46.797  2.00  0.00      LIG

ATOM      3  C7  LIG     2      67.131   9.577  45.613  2.00  0.00      LIG

...

...

ATOM     27  H15 LIG     2      64.538  11.418  44.352  2.00  0.00      LIG

ATOM     28  H16 LIG     2      66.226  11.473  43.904  2.00  0.00      LIG

TER      29      LIG      2

ENDMDL

Creación de la caja, solvatación y neutralización

| gmx editconf -f protein-complex.pdb -o protein-complex-box.pdb -c -d 1 -bt dodecahedron<br><br>gmx solvate -cs -cp protein-complex-box.pdb -o protein-complex-solv.pdb -p topol.top<br><br>gmx grompp -f em.mdp -c protein-complex-solv.pdb -p topol.top -o ions.tpr -maxwarn 2<br><br>gmx genion -s ions.tpr -o protein-complex-neutral.pdb -p topol.top -pname NA -nname CL -neutral |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

Minimización energética

| gmx grompp -f em.mdp -c protein-complex-neutral.pdb -p topol.top -o em.tpr<br><br>gmx mdrun -v -deffnm em |
| --------------------------------------------------------------------------------------------------------- |

Salida,

...

...

Step= 5019, Dmax= 1.8e-03 nm, Epot= -5.09176e+05 Fmax= 1.42654e+03, atom= 1523

Step= 5021, Dmax= 1.1e-03 nm, Epot= -5.09179e+05 Fmax= 7.74061e+01, atom= 1523

writing lowest energy coordinates.

Steepest Descents converged to Fmax < 100 in 5022 steps

Potential Energy  = -5.0917916e+05

Maximum force     =  7.7406082e+01 on atom 1523

Norm of force     =  5.6013878e+00

...

Generación de las restraints para ambos ligandos

| gmx genrestr -f ligand1.pdb -o posre\_LIG1.itp -fc 1000 1000 1000<br><br>gmx genrestr -f ligand2.pdb -o posre\_LIG2.itp -fc 1000 1000 1000 |
| ------------------------------------------------------------------------------------------------------------------------------------------ |

Editamos topol.top, y debemos agregar las restraints de cada cadena. Esto lo hacía automáticamente GMX en otros pasos, pero parece que no lo hace en el caso de múltiples cadenas. Por lo tanto, debemos crear la siguiente entrada

; Include Position restraint file proteina

#ifdef POSRES

#include "posre\_Protein\_chain\_A.itp"

#endif

El problema es que se deberá hacer para cada cadena. Este ejemplo tiene cadenas de la A a la H. Una vez logrado esto,

; Include chain topologies

#include "topol\_Protein\_chain\_A.itp"

#include "topol\_Protein\_chain\_B.itp"

...

...

; Include Position restraint file proteina

#ifdef POSRES

#include "posre\_Protein\_chain\_A.itp"

#endif

...

...

; Include Position restraint file proteina

#ifdef POSRES

#include "posre\_Protein\_chain\_H.itp"

#endif

; Ligand position restraints LIG 1

#ifdef POSRES

#include "posre\_LIG1.itp"

#endif

; Ligand position restraints LIG 2

#ifdef POSRES

#include "posre\_LIG2.itp"

#endif

; Include water topology

#include "charmm27.ff/tip3p.itp

...

Crearemos el grupo Protein\_LIG, que tiene la ventaja de YA incluir ambos ligandos,

| gmx make\_ndx -f em.tpr -o index.ndx |
| ------------------------------------ |

Equilibrado NVT

Edito el nvt.mdp

...

...

; Run parameters

integrator  = md        ; leap-frog integrator

nsteps      = 10000     ; dt\*nsteps = tiempo --> Ejemplo si 0.002 ps \* 50000 stp = 100ps

dt          = 0.002     ; en ps, cuidado con ser >0.002 ps. fs

; Output control

nstxout     = 500       ; save coordinates every (dt\*nsteps)

nstvout     = 500      ; save velocities

nstenergy   = 500       ; save energies

nstlog      = 500       ; update log file

energygrps  = Protein LIG ; recordar que acá los nombres deben ser correctos

...

...

tc\_grps = Protein\_LIG Water\_and\_ions

...

...

Ejecutamos

| gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -n index.ndx |
| -------------------------------------------------------------------- |

En GROMACS 2018-2019 hay un cambio particular en las restraints y se debe agregar el parámetro -r en.gro para lograr que funcione

| gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -r em.gro -n index.ndx |
| ------------------------------------------------------------------------------ |

Y ejecutamos,

| gmx mdrun -v -deffnm nvt |
| ------------------------ |

Equilibrado NPT

Edito npt.mdp

...

...

tcoupl      = V-rescale                     ; modified Berendsen thermostat

tc-grps     = Protein\_LIG Water\_and\_ions    ; two coupling groups - more accurate

tau-t       = 0.1   0.1                     ; time constant, in ps

ref-t       = 300   300                     ; reference temperature, one for each group, in K

; Pressure coupling

pcoupl      = berendsen             ; pressure coupling is on for NPT

pcoupltype  = isotropic                     ; uniform scaling of box vectors

tau-p       = 2.0                           ; time constant, in ps

ref-p       = 1.0                           ; reference pressure, in bar

compressibility = 4.5e-5                    ; isothermal compressibility of water,

...

...

Empleo el Berendsen coupling ya que lo sugirió el programa

Ejecuto

| gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -r nvt.gro -n index.ndx<br><br>gmx mdrun -v -deffnm npt |
| ---------------------------------------------------------------------------------------------------------------- |

Corrida MD

Edito md.mdp

...

...

integrator  = md        ; leap-frog integrator

nsteps      = 20000   ; pasos = 60 ns

dt          = 0.002     ; ps / paso

; Output control

nstxout             = 0         ; suppress .trr output

nstvout             = 0         ; suppress .trr output

nstenergy           = 100      ; save energies every 10.0 ps

nstlog              = 100      ; update log file every 10.0 ps

nstxout-compressed  = 100      ; write .xtc trajectory every 10.0 ps

...

...

Ejecutamos

| gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr -n index.ndx<br><br>gmx mdrun -v -deffnm md |
| ------------------------------------------------------------------------------------------------------------- |

El resultado

...

...

starting mdrun 'MATRIX PROTEIN 2 in water'

20000 steps,     40.0 ps.

step 19900, remaining wall clock time:     4 s

Writing final coordinates.

step 20000, remaining wall clock time:     0 s

`               `Core t (s)   Wall t (s)        (%)

`       `Time:     3519.181      879.795      400.0

`                 `(ns/day)    (hour/ns)

Performance:        3.928        6.109

...

...

Análisis numérico de la dinámica

RMSD del LIG

Van a figurar ambos en el mismo gráfico

| gmx rms -s md.tpr -f md.xtc -o md\_rmsd.xvg |
| ------------------------------------------- |


RMSD de la proteína, todas las cadenas juntas

| gmx rms -s md.tpr -f md.xtc -o md\_rmsd-prot.xvg |
| ------------------------------------------------ |


Dinámica de una proteína en agua

Caso: proteína monómero

Este caso es el más sencillo. Esta estrategia se suele emplear cuando se necesita mejorar el modelado de una proteína mediante MD.

Topología

| gmx pdb2gmx -f protein.pdb -o protein\_proc.pdb -water spce |
| ----------------------------------------------------------- |

Select the Force Field:

From '/usr/local/gromacs/share/gromacs/top':

` `1: AMBER03 protein, nucleic AMBER94 (Duan et al., J. Comp. Chem. 24, 1999-2012, 2003)

` `2: AMBER94 force field (Cornell et al., JACS 117, 5179-5197, 1995)

...

...

14: GROMOS96 54a7 force field (Eur. Biophys. J. (2011), 40,, 843-856, DOI: 10.1007/s00249-011-0700-9)

15: OPLS-AA/L all-atom force field (2001 aminoacid dihedrals)

Elegir 15, para simulaciones de proteínas (solas) está recomendado el OPLS-AA. A menos que deba comparar la misma proteína unida a otros ligandos, para ello debemos seleccionar el mismo campo de fuerza que empleamos en el caso de complejos no covalentes. También, deberán respetarse las mismas condiciones que se emplearon en el caso de la simulación con proteína-ligando.

En topol.top

#include "oplsaa.ff/forcefield.itp"

; Name       nrexcl

Protein\_A    3

[ atoms ]

;   nr       type  resnr residue  atom   cgnr     charge       mass  typeB    chargeB      massB

; residue   1 LYS rtp LYSH q +2.0

`     `1   opls\_287      1   LYS       N      1       -0.3    14.0067   ; qtot -0.3

...

...

...

; Include Position restraint file

#ifdef POSRES

#include "posre.itp"

#endif

; Include water topology

#include "oplsaa.ff/spce.itp"

#ifdef POSRES\_WATER

; Position restraint for each water oxygen

[ position\_restraints ]

;  i funct       fcx        fcy        fcz

`   `1    1       1000       1000       1000

#endif

; Include generic topology for ions

#include "oplsaa.ff/ions.itp"

[ system ]

; Name

Proteina

[ molecules ]

; Compound        #mols

Protein\_A           1

| #Creación de la caja (en este caso, puse un cubo)<br><br>gmx editconf -f protein\_proc.pdb -o protein\_newbox.pdb -c -d 1.0 -bt cubic<br><br>#Solvatar<br><br>gmx solvate -cp protein\_newbox.pdb -cs spc216.gro -o protein\_solv.pdb -p topol.top<br><br>#Neutralización<br><br>gmx grompp -f em.mdp -c protein\_solv.pdb -p topol.top -o ions.tpr<br><br>gmx genion -s ions.tpr -o protein\_neutral.pdb -p topol.top -pname NA -nname CL -neutral |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

![ref3]Proceder en la forma usual.

En teoría, para una proteína compuesta sólo de aminoácidos, no debería necesitar nada más que EM, NVT, NPT y MD, pero si tiene cofactores entonces se deberán tratar como ligandos. También se puede forzar la estabilidad de una estructura polimérica para evitar inestabilidad durante la simulación. Se pueden usar varias estrategias, el uso de grupos y el cambio de la identidad de la cadena son algunos. También se pueden aplicar restraints a partes de los grupos creados.

Sistema bifásico

Modelo de dos solventes: octanol-agua

El empleo de moléculas que no están hechas de residuos estándar hace que debamos crear los archivos de topología a mano.

Diseño de la molécula de 1-octanol en Chimera con SMILES CCCCCCCCOH.


Creación del MOL2 y parametrización con SwissParam. Nos deja los siguientes archivos.

octanol.pdb

MODEL        1

ATOM      1  C1  OCT     1       1.781   6.660   7.966  1.00  0.00      OCT

ATOM      2  C2  OCT     1       2.415   6.424   6.605  1.00  0.00      OCT

ATOM      3  C3  OCT     1       2.320   4.955   6.192  1.00  0.00      OCT

...

...

...

ATOM     26  H17 OCT     1       3.589   1.893   0.514  1.00  0.00      OCT

ATOM     27  H18 OCT     1       3.960   0.225   1.009  1.00  0.00      OCT

TER      28      OCT      1

ENDMDL

octanol.itp:

; ----

; Built itp for octanol.mol2

;    by user vzoete

; ----

;

[ atomtypes ]

; name at.num  mass   charge  ptype    sigma            epsilon

CR      6   12.0110  0.0  A         0.387541    0.230120

…

…

…

[ moleculetype ]

; Name nrexcl

OCT 3

[ atoms ]

; nr type resnr resid atom cgnr charge mass

`   `1 CR   1  OCT C1      1  0.0000  12.0110

…

topol.top (creado a mano):

; Include forcefield parameters

#include "charmm27.ff/forcefield.itp"

[ atomtypes ]

; name at.num  mass   charge  ptype    sigma            epsilon

CR      6   12.0110  0.0  A         0.387541    0.230120

…

`   `9 1 1000 1000 1000

#endif

; Include water topology

#include "charmm27.ff/tip3p.itp"

[ system ]

; Name

Octanol en agua

[ molecules ]

; Compound        #mols

OCT                500

Insertar 500 moléculas en un box de 10x10x10 nm (Esto fue adrede!!!). Verificar que realmente estén insertadas.

| gmx insert-molecules -ci octanol.pdb -nmol 500 -box 10 10 10 -o octanol\_box.pdb |
| -------------------------------------------------------------------------------- |

Try 692 success (now 13500 atoms)!

Added 500 molecules (out of 500 requested)

Writing generated configuration to octanol\_box.pdb

Back Off! I just backed up octanol\_box.pdb to ./#octanol\_box.pdb.1#

Output configuration contains 13500 atoms in 500 residues

Minimización

| gmx grompp -f em.mdp -c octanol\_box.pdb -p topol.top -o em.tpr<br><br>gmx mdrun -v -deffnm em |
| ---------------------------------------------------------------------------------------------- |

Da

Step=  454, Dmax= 9.7e-04 nm, Epot= -2.81080e+04 Fmax= 5.22059e+02, atom= 90

Step=  456, Dmax= 5.8e-04 nm, Epot= -2.81090e+04 Fmax= 8.10068e+01, atom= 90

writing lowest energy coordinates.

Steepest Descents converged to Fmax < 100 in 457 steps

Potential Energy  = -2.8108963e+04

Maximum force     =  8.1006821e+01 on atom 90

Norm of force     =  4.3152623e+00

Equilibrado NVT

| gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr |
| ------------------------------------------------------- |

Calculating fourier grid dimensions for X Y Z

Using a fourier grid of 84x84x84, spacing 0.119 0.119 0.119

Estimate for the relative computational load of the PME mesh part: 0.46

This run will generate roughly 4 Mb of data

Y

| gmx mdrun -v -deffnm nvt |
| ------------------------ |

500 steps,      1.0 ps.

step 400, remaining wall clock time:     1 s

Writing final coordinates.

step 500, remaining wall clock time:     0 s

`               `Core t (s)   Wall t (s)        (%)

`       `Time:       34.562        9.782      353.3

`                 `(ns/day)    (hour/ns)

Performance:        8.850        2.712

Equilibrado NPT

| gmx grompp -f npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -o npt.tpr<br><br>gmx mdrun -v -deffnm npt |
| --------------------------------------------------------------------------------------------------- |

da

500 steps,      1.0 ps.

step 400, remaining wall clock time:     2 s

Writing final coordinates.

step 500, remaining wall clock time:     0 s

`               `Core t (s)   Wall t (s)        (%)

`       `Time:       39.250       11.431      343.4

`                 `(ns/day)    (hour/ns)

Performance:        7.573        3.169

Corrida MD

| gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr<br><br>gmx mdrun -v -deffnm md |
| ------------------------------------------------------------------------------------------------ |

Da

step 0

Writing final coordinates.

step 100, remaining wall clock time:     0 s

`               `Core t (s)   Wall t (s)        (%)

`       `Time:       10.625        3.623      293.3

`                 `(ns/day)    (hour/ns)

Performance:        4.817        4.982

Extraigo el PDB de la MD

| gmx trjconv -s md.tpr -f md.xtc -o OCT\_md.pdb -pbc whole -sep |
| -------------------------------------------------------------- |

Con esto logramos crear la fase de octanol y estabilizarla en “la conformación más natural”, ahora hay que poner el agua.

Solvatar

Incremento el volumen en el eje z y coloco el centro en la mitad de la capa.

| gmx editconf -f OCT\_md.pdb -o OCT\_newbox.pdb -box 10 10 20 -center 5 5 5 |
| -------------------------------------------------------------------------- |

Da

Read 13500 atoms

Volume: 1006.16 nm^3, corresponds to roughly 452700 electrons

No velocities found

`    `system size : 11.314 11.315 11.702 (nm)

`    `center      :  5.177  5.077  5.076 (nm)

`    `box vectors : 10.021 10.021 10.021 (nm)

`    `box angles  :  90.00  90.00  90.00 (degrees)

`    `box volume  :1006.16               (nm^3)

`    `shift       : -2.677 -2.577 -2.576 (nm)

new center      :  2.500  2.500  2.500 (nm)

new box vectors :  5.000  5.000 10.000 (nm)

new box angles  :  90.00  90.00  90.00 (degrees)

new box volume  : 250.00               (nm^3)

Y

| gmx solvate -cp OCT\_newbox.pdb -p topol.top -o OCT\_solv.pdb |
| ------------------------------------------------------------- |

Found 1 molecule type:

`    `SOL (   3 atoms):  4442 residues

Generated solvent containing 13326 atoms in 4442 residues

Writing generated configuration to OCT\_solv.pdb

Back Off! I just backed up OCT\_solv.pdb to ./#OCT\_solv.pdb.1#

Output configuration contains 26826 atoms in 4942 residues

Volume                 :         250 (nm^3)

Density                :      964.03 (g/l)

Number of SOL molecules:   4442

Processing topology

Back Off! I just backed up temp.topIzLXjf to ./#temp.topIzLXjf.1#

Removing line #448 'SOL             28275' from topology file (topol.top)

Adding line for 4442 solvent molecules to topology file (topol.top)

![ref4]Proceder en forma usual

Proteína de membrana. Construcción de una bicapa e inserción de una acuaporina

Introducción

Las membranas biológicas son entidades complicadas que contienen mezclas autoensambladas de diferentes lípidos y proteínas. Entre todos estos lípidos, el colesterol juega un papel muy especial debido a su papel en la creación de balsas de membrana. Las cuestiones relacionadas con la naturaleza y organización de las balsas en membranas naturales están lejos de estar aclaradas y consensuadas, aunque existe una definición de lo que es una balsa. Según el Simposio Keystone sobre balsas lipídicas y función celular en 2006, “las balsas de membrana son dominios pequeños (10-200 nm) heterogéneos, altamente dinámicos, enriquecidos con esterol y esfingolípidos que compartimentan los procesos celulares”. Para comprender por qué el enriquecimiento de colesterol está presente en los dominios de la balsa, debemos comprender en detalle el carácter de las interacciones específicas entre el colesterol y los lípidos y esta es la razón por la que se estudia tan intensamente.

Dado que las membranas biológicas son mezclas complicadas que son muy difíciles de analizar, muchas investigaciones se realizan en membranas modelo que contienen componentes puros o mezclas bien controladas de dos o tres componentes. Especialmente interesantes son las membranas sintéticas que contienen tres componentes: fosfolípidos saturados , fosfolípidos insaturados y colesterol. En estas membranas modelo se pueden observar dominios en forma de balsa mejorados con colesterol y fosfolípidos saturados, dominios que varían en tamaño desde nanoescala a microescala. El estudio de las interacciones entre el colesterol y los lípidos en estas membranas modelo también puede arrojar luz sobre la naturaleza de las balsas lipídicas en las biomembranas.

Las bicapas lipídicas son bloques de construcción esenciales para las membranas biológicas . Ha habido un gran interés en sondear las membranas celulares ya que forman la estructura de los orgánulos celulares y sirven como una barrera para el transporte de materiales biológicos al citoplasma. Para las membranas lipídicas sin colesterol (o esteroles en general), existen tres fases principales que pueden existir: fluida (o líquido-cristalina) (Lα), ondulación (Pβ) y gel (Lβ). Líquido o líquido desordenado (con mezclas que contienen esteroles) es la fase más común en biología en la que las cadenas de ácidos grasos están completamente desordenadas. Esta fase se puede ver a altas temperaturas dependiendo del lípido en la membrana y las características de esta fase son la alta movilidad de los lípidos y la flexibilidad de la cadena. La fase L α ha sido ampliamente estudiada utilizando diversas técnicas experimentales y computacionales. Sin embargo, el enfoque de este artículo son las fases condensadas de una bicapa lipídica, es decir, P β y L β . El Lβ La fase se ve a temperaturas más bajas definidas por una temperatura de transición del gel. Las cadenas de acilo están más ordenadas y se componen de casi todas en la configuración trans.


Entre la fase L α y L β puede existir una fase de pre transición que se cree que consiste en una configuración ondulada denominada fase P β , que no existe para todos los lípidos, como los que tienen colas insaturadas [ 7 ]. . Entre todos los lípidos, que tienen fase P β , 1,2-dimiristoil- sn -glicero-3-fosfocolina (DMPC) y 1,2-dipalmitoil- sn -glicero-fosfocolina (DPPC) son los lípidos más comunes, en los que P Se ha estudiado la β [ [8] , [9] , [10] ]. La formación de P β se puede obtener calentando la L βfase con cadenas inclinadas o enfriamiento de la fase L α [ 11 ]. Para la fase P β , se puede encontrar una región gruesa y delgada, que se definen principalmente en la literatura como un brazo mayor y menor ( Fig. 1 ), respectivamente [ 8 ]. La región de torcedura con cadenas de ácidos grasos interdigitadas podría existir entre los dominios del brazo mayor y del brazo menor. Se conoce la existencia de estos dos brazos, pero los detalles sobre la configuración precisa de los grupos de cabezas de lípidos y las colas de lípidos y cómo se diferencian entre las regiones se desconocen o se están debatiendo. Se ha investigado y sugerido la coexistencia tanto de L α como de L β en P β [ 12], es decir, el brazo mayor representa principalmente el L β y hay una pequeña región desordenada en la membrana que presenta la fase L α (brazo menor).

| Lípidos PC  | Rango de temperatura (K) |
| ----------- | ------------------------ |
| di-18: 0    | 321,65 a 330,15          |
| 18: 0,16: 0 | 306,25 a 319,75          |
| 16: 0,18: 0 | 311,25 al 321,55         |
| 18: 0,14: 0 | 290,85 a 305,35          |
| di-14: 0    | 287\.15 a 297.15         |
| di-16: 0    | 308,45 a 314,55          |


Desde su primer lanzamiento en 2007, CHARMM-GUI Membrane Builder, una herramienta basada en la web disponible públicamente ( <http://www.charmm-gui.org/input/membrane> ), ha facilitado enormemente la generación de sistemas de membranas complejos. Su primera implementación permitió a los usuarios construir un sistema complejo de proteína-membrana con tres tipos de lípidos. Después de un desarrollo y actualización continuos, Membrane Builder ahora admite bicapas heterogéneas, con o sin proteínas, utilizando más de 400 tipos de lípidos, incluidos fosfolípidos, fosfoinosítidos, cardiolipina, esfingolípidos, lípidos bacterianos, esteroles, ácidos grasos y detergentes, lo que permite a los usuarios construir biológicamente sistemas de membranas realistas y experimentalmente comparables. Es importante destacar que Membrane Builder también proporciona entradas de simulación bien validadas para varios programas de MD, como CHARMM, NAMD, GROMACS y AMBER permitiendo a los usuarios realizar una simulación de MD con su herramienta familiar.

Ir a <https://www.charmm-gui.org/>


Por supuesto, podremos acceder a los tutoriales y papers que describen el funcionamiento. En realidad, recomiendo eso antes que este tutorial. Por qué? Tratan el funcionamiento completo del software, sus aplicaciones y sus limitaciones.

Nuestro objetivo será crear un sistema compuesto por una proteína y una bicapa lipídica. Luego, ese sistema lo usaremos para correr una simulación de dinámica molecular. El mismo sistema será creado para dos tipos de simulaciones: all-atom y coarse grain.

All-Atom

A la izquierda vamos a Input Generator


Inmediatamente, nos aparece una ventana de login. Se requiere un registro gratuito en el servidor.


El registro requiere una cuenta de mail académica. Parece que cualquier cosa .edu funciona. Después del registro entramos en el servidor.


Vamos a Membrane Builder. Obviamente, podríamos ir a Solution Builder y construir un sistema en solventes pero queremos algo más complejo.


En Bilayer Builder encontraremos


Es importante leer la descripción que figura acá. Despeja bastantes dudas. Abajo del texto vemos,


Podemos subir un archivo propio o usar el PDB ID que queramos. Voy a usar una proteína pequeña. Un barril β


Entonces,


Cambiamos a source RCSB porque el código es del Protein Data Bank. Lo siguiente es


Cada vez que apretamos Next Step, puede aparecer una ventana superpuesta que nos muestra qué es lo que está haciendo el servidor. Cuanto más complejo es, más tiempo va a tardar.


Bilayer Builder


Hay datos importantes. JOB ID nos permite recuperar el trabajo si pasa algo malo con el servidor o nuestra conexión de internet (lo segundo es más probable por cuestiones obvias, tales como vivir en Argentina). Se puede leer uno o más modelos. Esto dependerá de cómo están hechos los PDB. Después figura la información de cuáles son las moléculas que existen. En este caso, tenemos moléculas de sulfatos, el agua y dos cadenas. Figura la extensión de cada cadena. El nombre va a depender de cómo están en el archivo original. A veces nos conviene editar el PDB antes, así que tendríamos que usar el cargador del archivo y no el código PDB.


Sólo nos interesa la proteína. Podemos ignorar el resto. Si tiene residuos modificados y los necesitamos, hay que seleccionarlos. Siguiente,


Esta sección nos permite manipular el archivo, por ejemplo, con fosforilaciones o glicosilaciones. Una cuestión que tal vez sea relevante es el estado de protonación del aminoácido N y C terminal. Para cosas “comunes” podría decir que estas opciones serían las mejores.


Siguiente,


Es la parte que nos permite orientar la proteína. Puede que esto lo quiera o no. Por ejemplo, si quiero estudiar la forma en la cual se puede orientar la molécula (en simulaciones largas que estudien plegamiento) me daría igual e ignoraría esta parte. Sin embargo, las proteínas de membrana TIENEN una orientación predecible y está dado por las alfa hélices o las beta plegadas en forma de barril. Si ya está previamente orientada, está perfecto. Si no, hay varias estrategias que se usan. Para proteínas de membrana “sencillas” podemos usar ciegamente alguna de las opciones,


Usar orientación PDB Esta opción se sugiere para una estructura orientada de <http://opm.phar.umich.edu>

Alinear el primer eje principal a lo largo de Z Esta opción se sugiere para paquetes helicoidales pequeños u homo-oligómeros.

Alinear un vector (dos átomos) a lo largo de Z Esta opción se sugiere para un heterooligómero irregular.

Usar servidor PPM Esta opción envía una estructura de entrada en <http://opm.phar.umich.edu/ppm_server> Puede llevar algunos minutos dependiendo del tamaño de la proteína.

Voy a usar la última opción, porque no tengo idea cómo viene la proteína ni la conozco bien.


También podemos hacer otras cosas, como rotarla.


Siguiente,

Acá veremos algo así:


Este gráfico nos sirve para ver cómo se ubicó la molécula según el servidor. Se ve algo raro. Muy raro. Si la proteína es un canal, y debe estar paralelo a los lípidos de membrana, debería cruzar de lado a lado. Sin embargo, eso no pasa. Vamos a mirar qué pudo haber pasado,


Y encontramos que,


No tiene el mínimo sentido. En qué nos equivocamos? El canal es sólo una molécula, enviamos DOS moléculas mal orientadas al servidor. Soluciones? Hay que editar bien lo que pasó antes. Voy a aprovechar el JOB ID


 y

Y así,


Es el paso 3 en el cual orientamos, pero es el paso 1 en el cual editamos el PDB. Vamos a elegir la Cadena A, porque quiero. Pero para elegir bien deberíamos CONOCER MUY BIEN la estructura de la proteína a simular.


Así repetimos los pasos anteriores pero con esta cadena solamente.


Bueno, esto tampoco funcionó. Un desastre.

Voy a cambiar de proteína y usar una clásica que tiene α hélices. La AQP0, 2B6P


Así que, (JOB ID 1945476414)


Ven? CUIDADO con lo que pasó acá‼! Las AQP son homotetrámeros, así que sólo vemos una cadena, pero son 4 en el ensamblado biológico. Con esto en cuenta, queda como,


Ahora sí, con las otras opciones,


Opciones


La altura del agua sobre y debajo de la membrana. Influye si tenemos proteínas que se insertan en el solvente.


La parte de la longitud en la extensión XY. Es simétrico, dando origen a un cuadrado. Abajo figuran los lípidos con que se pueden construir la bicapa. Se pueden cambiar las proporciones


Vamos a elegir el POPC


1 y 1 significa: 100% de moléculas de lípido son POPC en la capa superior y en la capa inferior. Elijo una extensión XY de 50 y luego


Al apretar Show the system info,


Puedo empezar a adivinar cuál es el número XY que necesito o me fijo en las propiedades de la proteína,


Si X va de -20 a 34 e Y va de -21 a 29, entonces X = 54 e Y = 50. La dimensión más grande es 54. Así que cualquier valor será mayor a esto. Si uso 90,


Y no hay error. Depende qué quiero estudiar, debemos elegir la extensión adecuada.

Siguiente,


Si visualizamos, queda algo más lindo


Los límites del sistema están marcados por los cuadrados de colores. Las esferas representan las cabezas de los lípidos. La otra parte que podemos/debemos editar es el equilibrado electrostático. Para esto se emplea una solución de NaCl, KCl, CaCl2 o MgCl2,


0\.15 M es una solución isotónica. Si sólo quiero neutralizar, usaremos la opción de Add neutralizing ions. Es muy probable que los siguientes pasos tarden mucho en correrse.


Entonces,


Siguiente,


Podemos ver las estructuras finales,


Siguiente,


Se pueden armar los archivos para correr con el software que usemos. Nosotros empleamos GROMACS y el FF CHARMM36m. Si mi sistema tiene problemas luego, entonces conviene poner más pasos de minimización.

El equilibrado es otra parte importante. En general, una simulación implicará un NPT (pero podemos agregar o quitar pasos si el sistema es complicado o colapsa en la producción).


La temperatura se puede dejar como está, predeterminada en 303.15 K o cambiarla a la que deseemos. Una tabla con valores comunes es:

| Temperatura (ºC) | Temperatura (K) |
| ---------------- | --------------- |
| 0                | 273\.15         |
| 10               | 283\.15         |
| 15               | 288\.15         |
| 20               | 293\.15         |
| 25               | 298\.15         |
| 30               | 303\.15         |
| 37               | 310\.15         |
| 50               | 323\.15         |
| 100              | 373\.15         |

De nuevo, después de este paso va a tardar bastante. Así, el sistema queda


Esto debe descargarse en forma de archivo comprimido. No es un ZIP sino un archivo caracterísitco de Linux TGZ, pero se puede abrir en Windows de ser necesario (por ejemplo con 7zip),


El tamaño va a depender de la estructura y la cantidad de moléculas. Unas vez descargado podemos descomprimirlo y veremos,


Esta carpeta contiene muchos archivos pero, en nuestro caso, nos interesa otra carpeta interna, “gromacs”


Adentro están todos los archivos que necesitamos para lanzar la simulación


Resumen (traducción LITERAL, perdón por tan poco)

Una breve explicación de cada paso:

PASO 1: Leer las coordenadas de las proteínas

El usuario puede descargar las coordenadas desde RCSB (sitio web PDB) o OPM (http://opm.phar.umich.edu). OPM proporciona proteínas preorientadas coordiantes con respecto a la membrana normal. El usuario puede cargar las coordenadas del formato PDB (o CHARMM) desde la máquina local del usuario, una vez que oriente correctamente la proteína en las membranas.

PASO 2: Oriente la proteína

Si las coordenadas PDB son de RCSB, es necesario orientar adecuadamente la proteína con respecto a las membranas. Hay dos opciones para hacer esto. Es el paso en el que se calcula y se muestra el área de la sección transversal de la proteína a lo largo del eje Z. Las áreas máxima superior (10 <Z <20) e inferior (-20 <Z <-10) se utilizan para determinar el tamaño del sistema en XY.

Para ver un ejemplo detallado que muestra cómo orientar su estructura, vea esta demostración en video, particularmente la parte que comienza a las 2:00.

PASO 3: Determine el tamaño del sistema

Para determinar el tamaño del sistema en XY, hay tres opciones, en el caso de la generación de bicapas homogéneas, basadas en (1) el número de capas de lípidos alrededor de la proteína, (2) el número específico de moléculas de lípidos en la parte superior e inferior y (3) ) tamaño específico del sistema a lo largo de X e Y. El tamaño del sistema a lo largo de Z está determinado por la extensión del agua desde la parte superior e inferior de la proteína. Por ahora, están disponibles dos tipos de formas de sistema en XY (rectangular y hexagonal).

En el caso de la generación de bicapas heterogéneas, hay dos opciones para determinar el tamaño del sistema: (1) la proporción de tipos de lípidos que se utilizarán y el tamaño inicial (conjetura) del sistema a lo largo de X e Y (2) número específico de moléculas de lípidos y Relación del tamaño del sistema a lo largo de X e Y El tamaño del sistema a lo largo de Z está determinado por la extensión del agua desde la parte superior e inferior de la proteína. Si se desea, el número de hidratación (número de moléculas de agua por molécula de lípido) se puede utilizar para este propósito.

PASO 4: Construya los componentes

Basado en el tamaño del sistema determinado en el paso anterior, este paso construye piezas individuales como (1) la bicapa lipídica alrededor de la proteína, (2) moléculas de agua adicionales para solvatar completamente la proteína y (3) iones (con muestreo de Monte Carlo o algoritmo basado en la distancia) para una concentración determinada.

PASO 5: Ensamble los componentes

Todas las piezas (proteína, bicapa lipídica, agua adicional e iones) se ensamblan en este paso.

PASO 6: Equilibre el sistema

Debido a su tiempo de cálculo, solo se proporcionan los archivos de entrada para seis pasos de equilibrio "sugeridos". Sin embargo, el usuario puede encontrar coordenadas equilibradas para algunas proteínas de membranas del archivo.

Ahí están todos los archivos que necesitamos para correr el programa. Existe uno muy importante que se llama README. Básicamente, README es un script de CSH[^40] que tiene los pasos a ejecutar con Gromacs en nuestra PC.

El problema que aparece, normalmente, es que no está instalado CSH en nuestro sistema. Se deberá, por lo tanto, instalar usando el método específico de la distribución. Otro problema es que no conviene ejecutar ciegamente el script, sino abrirlo y analizarlo. Así sabremos qué está haciendo o, también, podremos anticiparnos a los posibles errores que surjan. A esta altura del manual, podremos ver el script y predecir qué es lo que va a fallar. La ejecución es idéntica a la de un .SH, siendo el comando a usar,

csh script.csh

Minimización energética del sistema

| gmx grompp -f step6.0\_minimization.mdp -o step6.0\_minimization.tpr -c step5\_charmm2gmx.pdb -r step5\_charmm2gmx.pdb -p topol.top<br><br>gmx mdrun -v -deffnm step6.0\_minimization |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

Equilibrado

Es un proceso que se repite unas 6 veces, así que lo pondremos en un script (también de CSH) pero más pequeño, así sabremos qué pasa. En un editor,

| <p>#!/bin/csh</p><p></p><p># Equilibration</p><p>set cnt    = 1</p><p>set cntmax = 6</p><p></p><p>while ( ${cnt} <= ${cntmax} )</p><p>`    `@ pcnt = ${cnt} - 1</p><p>`    `if ( ${cnt} == 1 ) then</p><p>`        `gmx grompp -f step6.{$cnt}\_equilibration.mdp -o step6.{$cnt}\_equilibration.tpr -c step6.{$pcnt}\_minimization.gro -r step5\_charmm2gmx.pdb -n index.ndx -p topol.top</p><p>`        `gmx mdrun -v -deffnm step6.{$cnt}\_equilibration</p><p>`    `else</p><p>`        `gmx grompp -f step6.{$cnt}\_equilibration.mdp -o step6.{$cnt}\_equilibration.tpr -c step6.{$pcnt}\_equilibration.gro -r step5\_charmm2gmx.pdb -n index.ndx -p topol.top</p><p>`        `gmx mdrun -v -deffnm step6.{$cnt}\_equilibration</p><p>`    `endif</p><p>`    `@ cnt += 1</p><p>end</p><p></p> |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

Corrida de producción

Se repite 10 veces (no sé por qué[^41], ya viene así configurado. Debería estudiar el manual[^42])

| <p>#!/bin/csh</p><p></p><p># Production</p><p>set cnt    = 1</p><p>set cntmax = 10</p><p></p><p></p><p>while ( ${cnt} <= ${cntmax} )</p><p>`    `if ( ${cnt} == 1 ) then</p><p>`        `gmx grompp -f step7\_production.mdp -o step7\_${cnt}.tpr -c step6.6\_equilibration.gro -n index.ndx -p topol.top</p><p>`        `gmx mdrun -v -deffnm step7\_${cnt}</p><p>`    `else</p><p>`        `@ pcnt = ${cnt} - 1</p><p>`        `gmx grompp -f step7\_production.mdp -o step7\_${cnt}.tpr -c step7\_${pcnt}.gro -t step7\_${pcnt}.cpt -n index.ndx -p topol.top</p><p>`        `gmx mdrun -v -deffnm step7\_${cnt}</p><p>`    `endif</p><p>`    `@ cnt += 1</p><p>end</p><p></p> |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

Análisis del comportamiento de las moléculas en una membrana

Hay diferentes tipos de análisis, en membranas se puede encontrar la fluidez y el empaquetamiento.

Para las bicapas que consisten en un único componente lipídico, el área promedio por molécula a es una cantidad central porque es la medida más simple de organización lateral. Dada una simulación de una bicapa que consiste en un solo lípido, el área promedio por lípido es obviamente solo el área simulada total dividida por el número de lípidos en cada monocapa, aunque cualquier lípido en particular puede tener más o menos que el área promedio, especialmente en fases fluidas desordenadas y fluctuantes. El grosor de la membrana es una medida de la organización transversal, pero se pueden definir muchos grosores (p. Ej., Hidrófobos, estéricos, del grupo de cabeza o de la superficie de Luzzati / Gibbs). El área A, por supuesto, está relacionada con el grosor como dos factores del volumen V, por lo que A también es una medida relevante para la información transversal, y tiene la ventaja de ser única. Sin embargo, la simplicidad inherente del área A para las bicapas homogéneas se cuestiona cuando las bicapas consisten en mezclas heterogéneas de lípidos y / o proteínas.

Área por lípido El área por lípido, APL, es un parámetro esencial para describir el estado del empaquetamiento molecular dentro de una bicapa lipídica. En una simulación de MD, se calcula dividiendo el área total de la caja de simulación en el plano x-y por el número total de moléculas de lípidos en un prospecto de la bicapa.


Mean Square Displacement

Este desplazamiento cuadrado medio y DADA son calculados por el programa gmx msd. Normalmente se usa un archivo de índice que contiene números de átomos y el MSD se promedia sobre estos átomos. Para las moléculas que consisten en más de un átomo, el riri puede tomarse como el centro de las posiciones de masa de las moléculas. En ese caso, debe usar un archivo de índice con números de moléculas. Sin embargo, los resultados serán casi idénticos al promedio de los átomos. El programa gmx msd también se puede usar para calcular la difusión en una o dos dimensiones. Esto es útil para estudiar la difusión lateral en las interfaces.


| gmx msd -f run.xtc -s topol.tpr  -beginfit 1000 -endfit 10000 -trestart 10000 -lateral z |
| ---------------------------------------------------------------------------------------- |

Algunos fundamentos

VMD adoptó una filosofía de representación: para cualquier conjunto de átomos / moléculas / cadenas de proteínas que queramos mostrar o analizar, debemos seleccionar este conjunto a través de una "representación" definida por palabras clave relacionadas con este conjunto (algo similar a make\_ndx ). VMD viene con palabras clave implementadas para sistemas de todos los átomos ("proteína", "cadena", "hidrógeno", "disolvente", etc.). Se implementan palabras clave más generales para poder mostrar sistemas no clásicos (los sistemas CG son parte de esta segunda categoría); puede encontrarlos en el manual VMD:

http://www.ks.uiuc.edu/Research/vmd/current/ug/

A continuación se enumeran algunos ejemplos:

`    `Para seleccionar solo lípidos: renombrar POPC, o solo parte de cada lípido: renombrar POPC y nombrar "C. \*. A" "C. \*. \*. B" "D. \*. A" "D. \*. B" para colas de lípidos (C1A, C1B, etc.) y renombrar POPC y nombrar NC3 PO4 "GL. \*" para cabezas.

`    `Para seleccionar sólo perlas de la columna vertebral de una proteína: nombre BB (use "BB. \*" O BAS para versiones antiguas de scripts de FG a CG).

`    `Para eliminar el disolvente (agua / perlas de iones): no cambie el nombre de W WF ION o WP en caso de agua polarizable.

`    `Para mostrar solo residuos cargados positivamente (en Martini): resname LYS ARG.

`    `Para mostrar la capa de agua alrededor de residuos específicos: dentro de 7.0 de (índice 531 a 538).

`    `Para mostrar todos los lípidos (excluyendo DPPC) cuyas cabezas interactúan con los mismos residuos específicos: mismo residuo que ((dentro de 7.0 de (índice 531 a 538)) y nombre NC3 PO4 "GL. \*") Y no renombrar DPPC.

Como puede ver en los ejemplos, todas estas palabras clave se pueden mezclar con los enlaces lógicos: y, o, no, etc. para producir cualquier representación. ¡Inténtalo tú mismo! VMD es realmente exigente en términos de memoria; Un truco fácil para disminuir la cantidad que necesita VMD es cargar estructuras / trayectorias que contengan solo perlas necesarias para su análisis; esto se puede hacer fácilmente procesando previamente la trayectoria usando trjconv . Y como estamos simulando sistemas cada vez más grandes en los que se involucran más y más cuentas, el truco anterior se puede adaptar para aumentar la velocidad de visualización / búsqueda de las trayectorias escribiendo representaciones que muestren solo las cuentas necesarias para la visualización (grupos de cabezas de una bicapa para ejemplo). Tenga en cuenta que puede guardar el estado de visualización de su sistema cuando lo desee guardando un state.vmd archivo . Este archivo contiene los comandos Tcl necesarios para obtener la pantalla actual; las listas de enlaces y dibujos (cilindros) no se guardan, pero puede abrir este .vmd archivo y agregar manualmente las líneas que escribió para generarlas en la parte inferior.

Enlaces / restricciones CG y redes elásticas

Cuando se abre una estructura / trayectoria CG con VMD, el programa construye una red de enlaces usando un criterio de distancia y una biblioteca atomística de posibles longitudes de enlace (de nido por el campo de fuerza namd, desarrollado por el mismo grupo); Las perlas CG, unidas con enlaces con una longitud media de 0,35 nm, no se definen mediante este algoritmo automático. VMD inevitablemente termina mostrando una nube de puntos, que son difíciles (¿imposibles?) De visualizar correctamente con ojos humanos no biónicos. Un script Tcl que lee los enlaces y restricciones de los CG archivos .itp / .tpr y reescribe la red de enlaces CG está disponible en el sitio web de Martini.

Primero, asegúrese de que su sistema sepa dónde encontrar el script:

source /wherever/cg\_bonds.tcl

Este script ahora se puede usar desde la ventana de línea de comandos de VMD de la siguiente manera:

cg\_bonds -top system.top -topoltype "elastic"

en caso de que tenga un .top disponible, pero no gromacs. Alternativamente, si gromacs está instalado en la máquina que está utilizando, puede usar un .tpr su en lugar:

cg\_bonds -gmx /wherever/gmxdump -tpr dyn.tpr -net "elastic" -cutoff
` `12.0 -color "orange"

-mat "AOChalky" -res 12 -rad 0.1

La última línea dibujará la red ElNeDyn con las opciones (cuto? Ff, color, material, resolución y radio) especificadas extrayendo los enlaces del dyn.tpr archivo (ahí es donde el entra gmxdump ). Tenga en cuenta que debe especificar una versión de my gromacs compatible con el dyn.tpr archivo .

Visualización de estructura secundaria

Después de poder dibujar enlaces y restricciones definidas por el campo de fuerza CG, el siguiente paso es ver la estructura secundaria de la proteína. Actualmente estamos desarrollando un guión gráfico que dibuja una representación similar a una caricatura en vmd. Este conjunto de rutinas aún está en desarrollo y debe mejorarse. . . por sus comentarios?

El proporciona dos rutinas principales cg\_secondary\_structure.tcl script : cg\_helix y cg\_sheet.

Utilice estos dos comandos de la misma manera:

cg\_whatever {list of terminig} [-graphical options]

O, en un ejemplo:

cg\_helix {{5 48} {120 146}} -hlxmethod "cylinder" -hlxcolor "red" -hlxrad 2.5

que dibujará dos hélices, del residuo etiquetado como 5 al residuo etiquetado como 48 y del residuo etiquetado como 120 al residuo etiquetado como 146, como un cilindro rojo de radio de 0.25 nm. Consulte la ayuda que se muestra cuando se obtiene el script o el sitio web para obtener una lista exhaustiva de opciones y valores predeterminados. Para definir la lista de termini, se implementan dos opciones: i) proporcionar la lista usted mismo (como en el ejemplo que se muestra arriba), ii) leer / analizar un archivo generado por do\_dssp . En el segundo caso, no necesita proporcionar ningún término, pero la lista de términos aún debe escribirse en la línea de comando como una lista vacía: {}.

Tenga en cuenta que, debido a la cantidad restringida de información estructural contenida en una estructura CG, la belleza y exactitud de estas representaciones gráficas son limitadas. . .

Energía libre de perturbación (Free Energy Perturbation, FEP)

Modelo: energía de desolvatación del formaldehído

La energía de desolvatación se puede ver como la energía libre de la molécula cuando pasa del vacío a rodearse con agua. ¿Por qué quiero calcular esta energía?[^43],[^44]


Este problema se resuelve tomando en cuenta que puede haber estados intermedios en los cuales la molécula va apareciendo en el agua y se evalúa la perturbación que eso le crea al sistema. El parámetro que controla el avance de los cálculos de “no existe la molécula” a “está la molécula” es λ[^45] que lo podríamos entender como:


Donde la energía libre de solvatación dependerá de la evolución de en los diferentes estados λ. El truco será elegir la mayor cantidad de estados intermedios para hacer los cálculos.

Tengo formaldehído en MOL2. Pasa a SwissParam y tenemos for.pdb y for.itp. Generamos a mano el topol.top:

; Include forcefield parameters

#include "charmm27.ff/forcefield.itp"

; FORMALDEHIDO topologia segun charmm27

[ atomtypes ]

; name at.num  mass   charge  ptype    sigma            epsilon

C=O     6   12.0110  0.0  A         0.356359    0.460240

O=C     8   15.9994  0.0  A         0.302905    0.502080

HCMM    1    1.0079  0.0  A         0.235197    0.092048

[ pairtypes ]

;  i     j    func     sigma1-4       epsilon1-4 ; THESE ARE 1-4 INTERACTIONS

O=C      C=O    1      0.302905    0.480705

O=C      O=C    1      0.249452    0.502080

O=C      HCMM   1      0.242324    0.214978

[ moleculetype ]

; Name nrexcl

FOR 3

[ atoms ]

; nr type resnr resid atom cgnr charge mass

`   `1 C=O  1  FOR C1      1  0.4500  12.0110

`   `2 O=C  1  FOR O1      2 -0.5700  15.9994

`   `3 HCMM 1  FOR H1      3  0.0600   1.0079

`   `4 HCMM 1  FOR H2      4  0.0600   1.0079

[ bonds ]

; ai aj fu b0 kb, b0 kb

`  `1   2 1 0.12220  779866.6  0.12220  779866.6

`  `1   3 1 0.11010  280029.3  0.11010  280029.3

`  `1   4 1 0.11010  280029.3  0.11010  280029.3

[ pairs ]

; ai aj fu

[ angles ]

; ai aj ak fu th0 kth ub0 kub th0 kth ub0 kub

`  `2   1   3 1  123.4390  403.48    123.4390  403.48

`  `2   1   4 1  123.4390  403.48    123.4390  403.48

`  `3   1   4 1  116.6990  357.72    116.6990  357.72

[ dihedrals ]

; ai aj ak al fu phi0 kphi mult phi0 kphi mult

[ dihedrals ]

; ai aj ak al fu xi0 kxi xi0 kxi

`  `1   3   2   4 2   0.00  62.0236     0.00  62.0236

…

…

…

#ifdef POSRES\_LIGAND

[ position\_restraints ]

; atom  type      fx      fy      fz

`   `1 1 1000 1000 1000

`   `2 1 1000 1000 1000

#endif

; Include water topology

#include "charmm27.ff/tip3p.itp"

[ system ]

; Name

Formaldehido en agua

[ molecules ]

; Compound        #mols

FOR                1

Insertar una molécula de formaldehído en una caja de 2x2x2 nm[^46]

| gmx insert-molecules -ci for.pdb -nmol 1 -box 2 2 2 -o for\_box.pdb |
| ------------------------------------------------------------------- |

Crear la caja cúbica y solvatar

| gmx editconf -f for\_box.pdb -o for\_box1.pdb -c -d 1 -bt cubic<br><br>y<br><br>gmx solvate -cp for\_box1.pdb -p topol.top -o for\_solv.pdb |
| ------------------------------------------------------------------------------------------------------------------------------------------- |

Minimizar

Primero con em.mdp

integrator               = steep

nsteps                   = 500

coulombtype              = pme

vdw-type                 = pme

| gmx grompp -f em.mdp -c for\_solv.pdb -p topol.top -o em.tpr<br><br>gmx mdrun -v -deffnm em |
| ------------------------------------------------------------------------------------------- |

Da:

Step=  500, Dmax= 1.6e-03 nm, Epot= -1.55554e+04 Fmax= 2.06453e+03, atom= 1

Energy minimization reached the maximum number of steps before the forces

reached the requested precision Fmax < 10.

writing lowest energy coordinates.

Steepest Descents did not converge to Fmax < 10 in 501 steps.

Potential Energy  = -1.5555411e+04

Maximum force     =  2.0645303e+03 on atom 1

Norm of force     =  8.9395714e+01

NOTE: 11 % of the run time was spent in pair search,

`      `you might want to increase nstlist (this has no effect on accuracy)

Segundo con equil.mdp

integrator               = md

nsteps                   = 20000

dt                  = 0.002

nstenergy                = 100

rlist                    = 1.0

nstlist                  = 10

vdw-type                 = pme

rvdw                     = 1.0

coulombtype              = pme

rcoulomb                 = 1.0

fourierspacing           = 0.12

constraints              = all-bonds

tcoupl                   = v-rescale

tc-grps                  = system

tau-t                    = 0.2

ref-t                    = 300

pcoupl                  = berendsen

ref-p                  = 1

compressibility        = 4.5e-5

tau-p                  = 5

gen-vel                  = yes

gen-temp                 = 300

| gmx grompp -f equil.mdp -c em.gro -o equil.tpr<br><br>gmx mdrun -v -deffnm equil |
| -------------------------------------------------------------------------------- |

Using 1 MPI thread

Using 4 OpenMP threads

starting mdrun 'Formaldehido en agua

20000 steps,     40.0 ps.

step 19900, remaining wall clock time:     0 s

Writing final coordinates.

step 20000, remaining wall clock time:     0 s

`               `Core t (s)   Wall t (s)        (%)

`       `Time:      136.750       35.782      382.2

`                 `(ns/day)    (hour/ns)

Performance:       96.590        0.248

Creo un run.mdp

; cambiamos el típico md por sd

integrator               = sd

nsteps                   = 100000

dt                 = 0.002

nstenergy                = 1000

nstlog                   = 5000

; cut-offs at 1.0nm

rlist                    = 1.0

dispcorr                 = EnerPres

vdw-type                 = pme

rvdw                     = 1.0

; Coulomb interactions

coulombtype              = pme

rcoulomb                 = 1.0

fourierspacing           = 0.12

; Constraints

constraints              = all-bonds

; set temperature to 300K

tcoupl                   = v-rescale

tc-grps                  = system

tau-t                    = 0.2

ref-t                    = 300

; set pressure to 1 bar with a thermostat that gives a correct

; thermodynamic ensemble

pcoupl             = parrinello-rahman

ref-p             = 1

compressibility     = 4.5e-5

tau-p             = 5

; and set the free energy parameters

free-energy              = yes

couple-moltype           = FOR ;el nombre de la molécula

; these 'soft-core' parameters make sure we never get overlapping

; charges as lambda goes to 0

sc-power                 = 1    ; número entero. Siempre. Ni siquiera con 1.0

sc-sigma                 = 0.3

sc-alpha                 = 1.0

; we still want the molecule to interact with itself at lambda=0

couple-intramol          = no

couple-lambda1           = vdwq

couple-lambda0           = none

init-lambda-state        = $LAMBDA$ ; este valor lo va a cambiar el script

; los lambda para usar, en este caso son 5

fep-lambdas              = 0.0 0.2 0.5 0.8 1.0

Crear las λ uso un script de bash:

|#!/bin/bash<br><br>if [ $#  -lt 3 ]; then<br>`    `echo "Usage: ./lambdas.sh run.mdp topol.top equil.gro"<br>`    `echo<br>`    `echo "Va a crear la carpeta correspondiente a la corrida"<br>`    `echo "Cambia \$LAMBDA\$ del MDP con el lambda actual"<br>`    `exit 1<br>fi<br><br>Nlambdas=$(cat $1 | grep fep-lambdas | wc -w)<br>Nlambdas2=$(expr $Nlambdas - 2)<br><br>i="0"<br><br>while [ $i -lt $Nlambdas ]<br>do<br>`    `newdir=$(printf "lambda\_%02d" $i)<br>`    `echo "Carpeta $newdir "<br>`    `mkdir -p $newdir<br>`    `sed "s/\\\$LAMBDA\\\$/${i}/" $1 > $newdir/grompp.mdp<br>`    `cp $2 $newdir/topol.top<br>`    `cp $3 $newdir/conf.gro<br>`    `i=$(expr $i + 1)<br>done|
| - |

Al ejecutar:

| bash lambdas.sh run.mdp topol.top equil.gro |
| ------------------------------------------- |

Da algo como:

Carpeta lambda\_00

Carpeta lambda\_01

...

...

Corrida

cd a cada carpeta lambda\_NN

| gmx grompp -f grompp.mdp -c conf.gro -p topol.top -o run.tpr<br><br>Y<br><br>gmx mdrun -v -deffnm run |
| ----------------------------------------------------------------------------------------------------- |

Da

`               `Core t (s)   Wall t (s)        (%)

`       `Time:     1148.562      312.880      367.1

`                 `(ns/day)    (hour/ns)

Performance:       55.229        0.435

Se generará un archivo XVG llamado run.xvg. Si lo abrimos veremos algo como


Lo mismo en cada directorio de lambda\_NN. En el directorio superior a estos, ejecutamos el comando que recupera información de los archivos XVG que se generan.

| gmx bar -b 100 -f lambda\_\*/run.xvg |
| ------------------------------------ |

Da

lambda\_00/run.xvg: Ignoring set 'pV (kJ/mol)'.

lambda\_00/run.xvg: 0.0 - 200.0; lambda = 0

`    `dH/dl & foreign lambdas:

`        `dH/dl (fep-lambda) (2001 pts)

`        `delta H to 0 (2001 pts)

`        `delta H to 0.2 (2001 pts)

lambda\_01/run.xvg: Ignoring set 'pV (kJ/mol)'.

…

…

lambda\_04/run.xvg: 0.0 - 200.0; lambda = 1

`    `dH/dl & foreign lambdas:

`        `dH/dl (fep-lambda) (2001 pts)

`        `delta H to 0.8 (2001 pts)

`        `delta H to 1 (2001 pts)

`   `Samples in time interval: 0.000 - 200.000

Removing samples outside of: 100.000 - 200.000

Temperature: 300 K

Detailed results in kT (see help for explanation):

` `lam\_A  lam\_B      DG   +/-     s\_A   +/-     s\_B   +/-   stdev   +/-

`     `0      1    3.69  0.05    0.21  0.04    0.22  0.04    0.76  0.02

`     `1      2    3.60  0.19    2.31  0.08    2.39  0.08    2.59  0.07

`     `2      3   -2.98  0.24   13.73  0.86    3.20  0.31    4.09  0.36

`     `3      4  -13.50  0.18    9.51  0.19   10.17  0.29    8.93  0.48

Final results in kJ/mol:

point      0 -      1,   DG  9.19 +/-  0.14

point      1 -      2,   DG  8.97 +/-  0.46

point      2 -      3,   DG -7.43 +/-  0.60

point      3 -      4,   DG -33.68 +/-  0.44

total      0 -      4,   DG -22.94 +/-  1.04

El ultimo valor la energía libre de solvatación del formaldehído en agua: -22.94±1.04 kJ/mol

Opciones de bar

gmx bar calculates free energy difference estimates through Bennett's acceptance ratio method (BAR). It also automatically adds series of individual free energies obtained with BAR into a combined free energy estimate.

Every individual BAR free energy difference relies on two simulations at different states: say state A and state B, as controlled by a parameter, λ (see the .mdp parameter init\_lambda). The BAR method calculates a ratio of weighted average of the Hamiltonian difference of state B given state A and vice versa. The energy differences to the other state must be calculated explicitly during the simulation. This can be done with the .mdp option foreign\_lambda.

Input option -f expects multiple dhdl.xvg files. Two types of input files are supported:

\* Files with more than one y-value. The files should have columns with dH/dλ and Δλ. The λ values are inferred from the legends: λ of the simulation from the legend of dH/dλ and the foreign λ values from the legends of Delta H

\* Files with only one y-value. Using the -extp option for these files, it is assumed that the y-value is dH/dλ and that the Hamiltonian depends linearly on λ. The λ value of the simulation is inferred from the subtitle (if present), otherwise from a number in the subdirectory in the file name.

The λ of the simulation is parsed from dhdl.xvg file's legend containing the string 'dH', the foreign λ values from the legend containing the capitalized letters 'D' and 'H'. The temperature is parsed from the legend line containing 'T ='.

The input option -g expects multiple .edr files. These can contain either lists of energy differences (see the .mdp option separate\_dhdl\_file), or a series of histograms (see the .mdp options dh\_hist\_size and dh\_hist\_spacing). The temperature and λ values are automatically deduced from the ener.edr file.

In addition to the .mdp option foreign\_lambda, the energy difference can also be extrapolated from the dH/dλ values. This is done with the -extp option, which assumes that the system's Hamiltonian depends linearly on λ, which is not normally the case.

The free energy estimates are determined using BAR with bisection, with the precision of the output set with -prec. An error estimate considering time correlations is made by splitting the data into blocks and determining the free energy differences over those blocks and assuming the blocks are independent. The final error estimate is determined from the average variance over 5 blocks. A range of block numbers for error estimation can be provided with the options -nbmin and -nbmax.

gmx bar tries to aggregate samples with the same 'native' and 'foreign' λ values, but always assumes independent samples. Note that when aggregating energy differences/derivatives with different sampling intervals, this is almost certainly not correct. Usually subsequent energies are correlated and different time intervals mean different degrees of correlation between samples.

The results are split in two parts: the last part contains the final results in kJ/mol, together with the error estimate for each part and the total. The first part contains detailed free energy difference estimates and phase space overlap measures in units of kT (together with their computed error estimate). The printed values are:

\* lam\_A: the λ values for point A.

\* lam\_B: the λ values for point B.

\* DG: the free energy estimate.

\* s\_A: an estimate of the relative entropy of B in A.

\* s\_B: an estimate of the relative entropy of A in B.

\* stdev: an estimate expected per-sample standard deviation.

NIST online (<https://www.nist.gov/programs-projects/solvation-free-energies>): -0.151256 eV = -14.5934028 kJ/mol

NOTA: el formaldehído forma un hidrato covalente en agua, eso significa que… no existe en la forma en la que está modelada.

Energía de unión

Modelo genérico

La determinación del ΔGbinding con GROMACS se puede hacer con el método anterior de FEP. El problema que se presenta es el siguiente: si se tiene que generar los λ de cada especie, proteína ligando solvente complejo puede ocurrir que exista una superposición de los λ intermedios del ligando con la proteína. Esto no puede ocurrir ya que estaríamos con resultados sin sentido. La solución para ello es realizar un umbrela sampling, que básicamente considera al ligando fijo en el sitio de unión y luego lo va haciendo desaparecer con el tiempo.

La alternativa a este método implica el uso de las capacidades del programa APBS que me permite calcular las propiedades electrónicas de complejos. Si bien puede realizarse el estudio a través de la generación de estructuras intermedias, derivadas de la MD del complejo, el proceso llega a ser tedioso. Existe otro software que combina los programas GROMACS y APBS para lograr esto: g\_mmpbsa[^47].

Se descarga de <http://rashmikumari.github.io/g_mmpbsa/Download-and-Installation.html>


La descarga nos da un archivo comprimido con los ejecutables para Linux. Esos los vamos a usar en la carpeta con los archivos de las simulaciones. Hay alternativas más útiles para correr los programas sin necesidad de copiar los ejecutables. Recordar el concepto y utilidad de la variable PATH.

Necesitamos crear un archivo MDP ligeramente diferente al resto pbsa.mdp

;Polar calculation: "yes" or "no"

polar        = yes

;=============

;PSIZE options

;=============

;Factor by which to expand molecular dimensions to get coarsegrid dimensions.

cfac         = 1.5

;The desired fine mesh spacing (in A)

gridspace     = 0.5

:Amount (in A) to add to molecular dimensions to get fine grid dimensions.

fadd         = 5

;Maximum memory (in MB) available per-processor for a calculation.

gmemceil     = 4000

;=============================================

;APBS kwywords for polar solvation calculation

;=============================================

;Charge of positive ions

pcharge     = 1

;Radius of positive charged ions

prad        = 0.95

;Concentration of positive charged ions

pconc           = 0.150

;Charge of negative ions

ncharge     = -1

;Radius of negative charged ions

nrad        = 1.81

;Concentration of negative charged ions

nconc         = 0.150

;Solute dielectric constant

pdie         = 2

;Solvent dielectric constant

sdie         = 80

;Reference or vacuum dielectric constant

vdie         = 1

;Solvent probe radius

srad         = 1.4

;Method used to map biomolecular charges on grid. chgm = spl0 or spl2 or spl4

chgm            = spl4

;Model used to construct dielectric and ionic boundary. srfm = smol or spl2 or spl4

srfm            = smol

;Value for cubic spline window. Only used in case of srfm = spl2 or spl4.

swin         = 0.30

;Numebr of grid point per A^2. Not used when (srad = 0.0) or (srfm = spl2 or spl4)

sdens         = 10

;Temperature in K

temp         = 300

;Type of boundary condition to solve PB equation. bcfl = zero or sdh or mdh or focus or map

bcfl         = mdh

;Non-linear (npbe) or linear (lpbe) PB equation to solve

PBsolver     = lpbe

;========================================================

;APBS kwywords for Apolar/Non-polar solvation calculation

;========================================================

;Non-polar solvation calculation: "yes" or "no"

apolar        = yes

;Repulsive contribution to Non-polar

;===SASA model ====

;Gamma (Surface Tension) kJ/(mol A^2)

gamma           = 0.0226778

;Probe radius for SASA (A)

sasrad          = 1.4

;Offset (c) kJ/mol

sasaconst       = 3.84982

;===SAV model===

;Pressure kJ/(mol A^3)

press           = 0

;Probe radius for SAV (A)

savrad          = 0

;Offset (c) kJ/mol

savconst        = 0

;Attractive contribution to Non-polar

;===WCA model ====

;using WCA method: "yes" or "no"

WCA             = no

;Probe radius for WCA

wcarad          = 1.20

;bulk solvent density in A^3

bconc        = 0.033428

;displacment in A for surface area derivative calculation

dpos        = 0.05

;Quadrature grid points per A for molecular surface or solvent accessible surface

APsdens        = 20

;Quadrature grid spacing in A for volume integral calculations

grid            = 0.45 0.45 0.45

;Parameter to construct solvent related surface or volume

APsrfm          = sacc

;Cubic spline window in A for spline based surface definitions

APswin          = 0.3

;Temperature in K

APtemp          = 300

` `El programa se ejecuta con:

| ` `g\_mmpbsa -f md.xtc -s md.tpr -i pbsa.mdp -pdie 2 -pbsa -decomp |
| ------------------------------------------------------------------ |

![ref2]Opciones de g\_mmpbsa

Option     Filename  Type         Description

\------------------------------------------------------------

`  `-f       traj.xtc  Input        Trajectory: xtc trr trj gro g96 pdb cpt

`  `-s      topol.tpr  Input        Run input file: tpr tpb tpa

`  `-i     grompp.mdp  Input, Opt.  grompp input file with MD parameters

`  `-n      index.ndx  Input, Opt.  Index file

` `-mm  energy\_MM.xvg  Output, Opt. xvgr/xmgr file

-pol      polar.xvg  Output, Opt. xvgr/xmgr file

-apol    apolar.xvg  Output, Opt. xvgr/xmgr file

-mmcon contrib\_MM.dat  Output, Opt. Generic data file

-pcon contrib\_pol.dat  Output, Opt. Generic data file

-apcon contrib\_apol.dat  Output, Opt. Generic data file

Option       Type   Value   Description

\------------------------------------------------------

-[no]h       bool   yes     Print help info and quit

-[no]version bool   no      Print version info and quit

-nice        int    19      Set the nicelevel

-b           time   0       First frame (ps) to read from trajectory

-e           time   0       Last frame (ps) to read from trajectory

-dt          time   0       Only use frame when t MOD dt = first time (ps)

-tu          enum   ps      Time unit: fs, ps, ns, us, ms or s

-[no]w       bool   no      View output .xvg, .xpm, .eps and .pdb files

-xvg         enum   xmgrace  xvg plot formatting: xmgrace, xmgr or none

-[no]silent  bool   no      Display messages, output and errors from external

`                            `APBS program. Only works with external APBS

`                            `program

-rad         enum   bondi   van der Waal radius type: bondi, mbondi, mbondi2

`                            `or amber

-rvdw        real   1       Default van der Waal radius (in nm) if not found

-[no]mme     bool   yes     To calculate vacuum molecular mechanics energy

-pdie        real   1       Dielectric constant of solute. Should be same as

`                            `of polar solvation

-[no]incl\_14 bool   no      Include 1-4 atom-pairs, exclude 1-2 and 1-3 atom

`                            `pairs during MM calculation. Should be "yes" when

`                            `groups are bonded with each other.

-[no]focus   bool   no      To enable focusing on the specfic region of

`                            `molecule, group of atoms must be provided in

`                            `index file

-[no]pbsa    bool   no      To calculate polar and/or non-polar solvation

`                            `energy

-ndots       int    24      Number of dots per sphere in the calculation of

`                            `SASA, more dots means more accuracy

-[no]diff    bool   yes     Calculate the energy difference between two group

`                            `otherwise only calculates for one group

-[no]decomp  bool   no      Decomposition of energy for each residue

File Options

Se nos pedirá elegir dos grupos, si necesitamos estudiar grupos especiales, entonces debemos especificar eso a través del archivo index.ndx. Tenemos que usar la misma forma para declarar la existencia del index.ndx

| g\_mmpbsa -f md\_mol.xtc -s md.tpr -i pbsa.mdp -pdie 2 -pbsa -decomp -n index.ndx |
| --------------------------------------------------------------------------------- |

La pantalla que aparecerá, luego de la selección de grupos,


A medida que pasa el tiempo se realizan cálculos en diferentes instancias, las cuales se pueden controlar a través del archivo pbsa.mdp.


El cálculo numérico de la energía de interacción se realiza con el script pbsa.py en forma automática o a través de la lectura de los archivos de salida anterior.

| python pbsa.py -m energy\_MM.xvg -p polar.xvg -a apolar.xvg -bs -nbs 500 -of full\_energy.dat -os summary\_energy.dat -om meta\_energy.dat |
| ------------------------------------------------------------------------------------------------------------------------------------------ |

Y

| cat summary\_energy.dat |
| ----------------------- |

Da

#Complex Number:    1

\===============

`   `SUMMARY

\===============

` `van der Waal energy      =        -223.672   +/-    5.494 kJ/mol

` `Electrostattic energy    =         -64.061   +/-    2.452 kJ/mol

` `Polar solvation energy   =         201.300   +/-    6.884 kJ/mol

` `SASA energy              =         -33.450   +/-    0.417 kJ/mol

` `SAV energy               =           0.000   +/-    0.000 kJ/mol

` `WCA energy               =           0.000   +/-    0.000 kJ/mol

` `Binding energy           =        -119.594   +/-   11.074 kJ/mol

\===============

`    `END

\===============

En kcal/mol es: -28.6±2.6 kcal/mol

El código de pbsa.py es,

|#!/usr/bin/python<br>#<br># This file is part of g\_mmpbsa.<br><br>from \_\_future\_\_ import absolute\_import, division, print\_function<br>from builtins import range<br>from builtins import object<br><br>import re<br>import sys<br>import numpy as np<br>import argparse<br>import os<br>import math<br><br>def main():<br>`    `args = ParseOptions()<br>`    `#File => Frame wise component energy<br>`    `try:<br>`        `frame\_wise = open(args.outfr, 'w')<br>`    `except:<br>`        `raise IOError ('Could not open file {0} for writing. \n' .format(args.outfr))<br><br>`    `frame\_wise.write('#Time E\_VdW\_mm(Protein)\tE\_Elec\_mm(Protein)\tE\_Pol(Protein)\tE\_Apol(Protein)\tE\_VdW\_mm(Ligand)\tE\_Elec\_mm(Ligand)\tE\_Pol(Ligand)\tE\_Apol(Ligand)\tE\_VdW\_mm(Complex)\tE\_Elec\_mm(Complex)\tE\_Pol(Complex)\tE\_Apol(Complex)\tDelta\_E\_mm\tDelta\_E\_Pol\tDelta\_E\_Apol\tDelta\_E\_binding\n')<br>`    `#Complex Energy<br>`    `c = []<br>`    `if args.multiple:<br>`        `MmFile, PolFile, APolFile = ReadMetafile(args.metafile)<br>`        `for i in range(len(MmFile)):<br>`            `cTmp = Complex(MmFile[i],PolFile[i],APolFile[i])<br>`            `cTmp.CalcEnergy(args,frame\_wise,i)<br>`            `c.append(cTmp)<br>`    `else:<br>`        `cTmp = Complex(args.molmech,args.polar,args.apolar)<br>`        `cTmp.CalcEnergy(args,frame\_wise,0)<br>`        `c.append(cTmp)<br>`    `#Summary in output files => "--outsum" and "--outmeta" file options<br>`    `Summary\_Output\_File(c, args)<br><br>class Complex(object):<br>`    `def \_\_init\_\_(self,MmFile,PolFile,APolFile):<br>`        `self.TotalEn = []<br>`        `self.Vdw, self.Elec, self.Pol, self.Sas, self.Sav, self.Wca =[], [], [], [], [], []<br>`        `self.MmFile = MmFile<br>`        `self.PolFile = PolFile<br>`        `self.APolFile = APolFile<br>`        `self.AvgEnBS = []<br>`        `self.CI = []<br>`        `self.FinalAvgEnergy = 0<br>`        `self.StdErr = 0<br><br>`    `def CalcEnergy(self,args,frame\_wise,idx):<br>`        `mmEn = ReadData(self.MmFile,n=7)<br>`        `polEn = ReadData(self.PolFile,n=4)<br>`        `apolEn = ReadData(self.APolFile,n=10)<br>`        `CheckEnData(mmEn,polEn,apolEn)<br><br>`        `time, MM, Vdw, Elec, Pol, Apol, Sas, Sav, Wca = [], [], [], [], [], [], [], [], []<br>`        `for i in range(len(mmEn[0])):<br>`            `#Vacuum MM<br>`            `Energy = mmEn[5][i] + mmEn[6][i] - (mmEn[1][i] + mmEn[2][i] + mmEn[3][i] + mmEn[4][i])<br>`            `MM.append(Energy)<br>`            `Energy = mmEn[5][i] - (mmEn[1][i] + mmEn[3][i])<br>`            `Vdw.append(Energy)<br>`            `Energy = mmEn[6][i] - (mmEn[2][i] + mmEn[4][i])<br>`            `Elec.append(Energy)<br>`            `# Polar<br>`            `Energy = polEn[3][i] - (polEn[1][i] + polEn[2][i])<br>`            `Pol.append(Energy)<br>`            `#Non-polar<br>`            `Energy = apolEn[3][i] + apolEn[6][i] + apolEn[9][i] - (apolEn[1][i] + apolEn[2][i] + apolEn[4][i] + apolEn[5][i] + apolEn[7][i] + apolEn[8][i])<br>`            `Apol.append(Energy)<br>`            `Energy = apolEn[3][i] - (apolEn[1][i] + apolEn[2][i])<br>`            `Sas.append(Energy)<br>`            `Energy = apolEn[6][i] - (apolEn[4][i] + apolEn[5][i])<br>`            `Sav.append(Energy)<br>`            `Energy = apolEn[9][i] - (apolEn[7][i] + apolEn[8][i])<br>`            `Wca.append(Energy)<br>`            `#Final Energy<br>`            `time.append(mmEn[0][i])<br>`            `Energy = MM[i] + Pol[i] + Apol[i]<br>`            `self.TotalEn.append(Energy)<br><br>`        `# Writing frame wise component energy to file<br>`        `frame\_wise.write('\n#Complex %d\n' % ( (idx+1)))<br>`        `for i in range(len(time)):<br>`            `frame\_wise.write('%15.3lf %15.3lf %15.3lf %15.3lf %15.3lf' % (time[i], mmEn[1][i], mmEn[2][i], polEn[1][i], (apolEn[1][i] + apolEn[4][i] + apolEn[7][i])))<br>`            `frame\_wise.write('%15.3lf %15.3lf %15.3lf %15.3lf'         %          (mmEn[3][i], mmEn[4][i], polEn[2][i], (apolEn[2][i] + apolEn[5][i] + apolEn[8][i])))<br>`            `frame\_wise.write('%15.3lf %15.3lf %15.3lf %15.3lf'         %          (mmEn[5][i], mmEn[6][i], polEn[3][i], (apolEn[3][i] + apolEn[6][i] + apolEn[9][i])))<br>`            `frame\_wise.write('%15.3lf %15.3lf %15.3lf %15.3lf\n'         % (MM[i], Pol[i], Apol[i], self.TotalEn[i]))<br><br>`        `#Bootstrap analysis energy components<br>`        `if(args.bootstrap):<br>`            `bsteps = args.nbstep<br>`            `avg\_energy, error = BootStrap(Vdw,bsteps)<br>`            `self.Vdw.append(avg\_energy)<br>`            `self.Vdw.append(error)<br>`            `avg\_energy, error = BootStrap(Elec,bsteps)<br>`            `self.Elec.append(avg\_energy)<br>`            `self.Elec.append(error)<br>`            `avg\_energy, error = BootStrap(Pol,bsteps)<br>`            `self.Pol.append(avg\_energy)<br>`            `self.Pol.append(error)<br>`            `avg\_energy, error = BootStrap(Sas,bsteps)<br>`            `self.Sas.append(avg\_energy)<br>`            `self.Sas.append(error)<br>`            `avg\_energy, error = BootStrap(Sav,bsteps)<br>`            `self.Sav.append(avg\_energy)<br>`            `self.Sav.append(error)<br>`            `avg\_energy, error = BootStrap(Wca,bsteps)<br>`            `self.Wca.append(avg\_energy)<br>`            `self.Wca.append(error)<br>`            `#Bootstrap => Final Average Energy<br>`            `self.AvgEnBS, AvgEn, EnErr, CI = ComplexBootStrap(self.TotalEn,bsteps)<br>`            `self.FinalAvgEnergy = AvgEn<br>`            `self.StdErr = EnErr<br>`            `self.CI = CI<br>`        `#If not bootstrap then average and standard deviation<br>`        `else:<br>`            `self.Vdw.append(np.mean(Vdw))<br>`            `self.Vdw.append(np.std(Vdw))<br>`            `self.Elec.append(np.mean(Elec))<br>`            `self.Elec.append(np.std(Elec))<br>`            `self.Pol.append(np.mean(Pol))<br>`            `self.Pol.append(np.std(Pol))<br>`            `self.Sas.append(np.mean(Sas))<br>`            `self.Sas.append(np.std(Sas))<br>`            `self.Sav.append(np.mean(Sav))<br>`            `self.Sav.append(np.std(Sav))<br>`            `self.Wca.append(np.mean(Wca))<br>`            `self.Wca.append(np.std(Wca))<br>`            `self.FinalAvgEnergy = np.mean(self.TotalEn)<br>`            `self.StdErr = np.std(self.TotalEn)<br><br><br>def Summary\_Output\_File(AllComplex,args):<br>`    `try:<br>`        `fs = open(args.outsum,'w')<br>`    `except:<br>`        `raise IOError ('Could not open file {0} for writing. \n' .format(args.outsum))<br><br>`    `if args.multiple:<br>`        `try:<br>`            `fm = open(args.outmeta,'w')<br>`        `except:<br>`            `raise IOError ('Could not open file {0} for writing. \n' .format(args.outmeta))<br>`        `fm.write('# Complex\_Number\t\tTotal\_Binding\_Energy\t\tError\n')<br><br>`    `for n in range(len(AllComplex)):<br>`        `fs.write('\n\n#Complex Number: %4d\n' % (n+1))<br>`        `fs.write('===============\n   SUMMARY   \n===============\n\n')<br>`        `fs.write('\n van der Waal energy      = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].Vdw[0], AllComplex[n].Vdw[1]))<br>`        `fs.write('\n Electrostattic energy    = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].Elec[0],AllComplex[n].Elec[1]))<br>`        `fs.write('\n Polar solvation energy   = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].Pol[0], AllComplex[n].Pol[1]))<br>`        `fs.write('\n SASA energy              = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].Sas[0], AllComplex[n].Sas[1]))<br>`        `fs.write('\n SAV energy               = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].Sav[0], AllComplex[n].Sav[1]))<br>`        `fs.write('\n WCA energy               = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].Wca[0], AllComplex[n].Wca[1]))<br>`        `fs.write('\n Binding energy           = %15.3lf   +/-  %7.3lf kJ/mol\n' % (AllComplex[n].FinalAvgEnergy, AllComplex[n].StdErr))<br>`        `fs.write('\n===============\n    END     \n===============\n\n')<br><br>`        `if args.multiple:<br>`            `fm.write('%5d %15.3lf %7.3lf\n' % (n+1 , AllComplex[n].FinalAvgEnergy, AllComplex[n].StdErr))<br><br>def CheckEnData(mmEn,polEn,apolEn):<br>`    `frame = len(mmEn[0])<br>`    `for i in range(len(mmEn)):<br>`        `if(len(mmEn[i]) != frame):<br>`            `raise ValueError("In MM file, size of columns are not equal.")<br><br>`    `for i in range(len(polEn)):<br>`        `if(len(polEn[i]) != frame):<br>`            `raise ValueError("In Polar file, size of columns are not equal.")<br><br>`    `for i in range(len(apolEn)):<br>`        `if(len(apolEn[i]) != frame):<br>`            `raise ValueError("In APolar file, size of columns are not equal.")<br><br><br>def ParseOptions():<br>`    `parser = argparse.ArgumentParser()<br>`    `parser.add\_argument("-mt", "--multiple", help='If given, calculate for multiple complexes. Need Metafile containing path of energy files', action="store\_true")<br>`    `parser.add\_argument("-mf", "--metafile", help='Metafile containing path to energy files of each complex in a row obtained from g\_mmpbsa in following order: \<br>`                                                       `[MM file] [Polar file] [ Non-polar file] ',action="store", default='metafile.dat', metavar='metafile.dat')<br>`    `parser.add\_argument("-m", "--molmech", help='Vacuum Molecular Mechanics energy file obtained from g\_mmpbsa',action="store", default='energy\_MM.xvg', metavar='energy\_MM.xvg')<br>`    `parser.add\_argument("-p", "--polar", help='Polar solvation energy file obtained from g\_mmpbsa',action="store",default='polar.xvg', metavar='polar.xvg')<br>`    `parser.add\_argument("-a", "--apolar", help='Non-Polar solvation energy file obtained from g\_mmpbsa',action="store",default='apolar.xvg',metavar='apolar.xvg')<br>`    `parser.add\_argument("-bs", "--bootstrap", help='If given, Enable Boot Strap analysis',action="store\_true")<br>`    `parser.add\_argument("-nbs", "--nbstep", help='Number of boot strap steps for average energy calculation',action="store", type=int, default=500, metavar=500)<br>`    `parser.add\_argument("-of", "--outfr", help='Energy File: All energy components frame wise',action="store",default='full\_energy.dat', metavar='full\_energy.dat')<br>`    `parser.add\_argument("-os",<br>` `"--outsum", help='Final Energy File: Full Summary of energy components',action="store",default='summary\_energy.dat', metavar='summary\_energy.dat')<br>`    `parser.add\_argument("-om", "--outmeta", help='Final Energy File for Multiple Complexes: Complex wise final binding nergy',action="store",default='meta\_energy.dat',metavar='meta\_energy.dat')<br><br>`    `if len(sys.argv) < 2:<br>`        `print('ERROR: No input files. Need help!!!')<br>`        `parser.print\_help()<br>`        `sys.exit(1)<br><br>`    `args = parser.parse\_args()<br><br>`    `if args.multiple:<br>`        `if not os.path.exists(args.metafile):<br>`            `print('\nERROR: {0} not found....\n' .format(args.metafile))<br>`            `parser.print\_help()<br>`            `sys.exit(1)<br>`    `else:<br>`        `if not os.path.exists(args.molmech):<br>`            `print('\nERROR: {0} not found....\n' .format(args.molmech))<br>`            `parser.print\_help()<br>`            `sys.exit(1)<br>`        `if not os.path.exists(args.polar):<br>`            `print('\nERROR: {0} not found....\n' .format(args.polar))<br>`            `parser.print\_help()<br>`            `sys.exit(1)<br>`        `if not os.path.exists(args.apolar):<br>`            `print('\nERROR: {0} not found....\n' .format(args.apolar))<br>`            `parser.print\_help()<br>`            `sys.exit(1)<br><br>`    `return args<br><br>def ReadData(FileName,n=2):<br>`    `try:<br>`        `infile = open(FileName,'r')<br>`    `except:<br>`        `raise IOError('Could not open file {0} for reading. \n' .format(FileName))<br><br>`    `x, data = [],[]<br>`    `for line in infile:<br>`        `line = line.rstrip('\n')<br>`        `if not line.strip():<br>`            `continue<br>`        `if(re.match('#|@',line)==None):<br>`            `temp = line.split()<br>`            `data.append(np.array(temp))<br>`    `for j in range(0,n):<br>`        `x\_temp =[]<br>`        `for i in range(len(data)):<br>`            `try:<br>`                `value = float(data[i][j])<br>`            `except:<br>`                `raise FloatingPointError('\nCould not convert {0} to floating point number.. Something is wrong in {1}..\n' .format(data[i][j], FileName))<br><br>`            `x\_temp.append(value)<br>`        `x.append(x\_temp)<br>`    `return x<br><br>def ComplexBootStrap(x,step=1000):<br>`    `avg =[]<br>`    `x = np.array(x)<br>`    `n = len(x)<br>`    `idx = np.random.randint(0,n,(step,n))<br>`    `sample\_x = x[idx]<br>`    `avg = np.sort(np.mean(sample\_x,1))<br>`    `CI\_min = avg[int(0.005\*step)]<br>`    `CI\_max = avg[int(0.995\*step)]<br>`    `#print('Energy = %13.3f; Confidance Interval = (-%-5.3f / +%-5.3f)\n' % (np.mean(avg), (np.mean(avg)-CI\_min), (CI\_max-np.mean(avg))))<br>`    `return avg, np.mean(avg), np.std(avg), [(np.mean(avg)-CI\_min), (CI\_max-np.mean(avg))]<br><br>def BootStrap (x,step=1000):<br>`    `if(np.mean(x)) == 0:<br>`        `return 0.000, 0.000<br>`    `else:<br>`        `avg =[]<br>`        `x = np.array(x)<br>`        `n = len(x)<br>`        `idx = np.random.randint(0,n,(step,n))<br>`        `sample\_x = x[idx]<br>`        `avg = np.sort(np.mean(sample\_x,1))<br>`        `return np.mean(avg),np.std(avg)<br><br>def find\_nearest\_index(array,value):<br>`    `idx = (np.abs(array-value)).argmin()<br>`    `return idx<br><br>def ReadMetafile(metafile):<br>`    `MmFile,PolFile, APolFile = [], [], []<br>`    `FileList = open(metafile,'r')<br>`    `for line in FileList:<br>`        `line = line.rstrip('\n')<br>`        `if not line.strip():<br>`            `continue<br>`        `temp = line.split()<br>`        `MmFile.append(temp[0])<br>`        `PolFile.append(temp[1])<br>`        `APolFile.append(temp[2])<br><br>`        `if not os.path.exists(temp[0]):<br>`            `raise IOError('Could not open file {0} for reading. \n' .format(temp[0]))<br><br>`        `if not os.path.exists(temp[1]):<br>`            `raise IOError('Could not open file {0} for reading. \n' .format(temp[1]))<br><br>`        `if not os.path.exists(temp[2]):<br>`            `raise IOError('Could not open file {0} for reading. \n' .format(temp[2]))<br><br>`    `return MmFile, PolFile, APolFile<br><br>if \_\_name\_\_=="\_\_main\_\_":<br>`    `main()|
| - |

Interacción energética lineal (Linear Interaction Energy)

Otra forma de aproximar la energía de unión, es aprovechando la información de los archivos EDR, los mismos que usamos para estudiar la variación de energía en el tiempo. LIE utiliza la información de la MD del complejo y del ligando por separado.

La energía libre de unión según el método LIE es la diferencia de las energías libres de solvatación del ligando libre, ΔGsol(libre), y el ligando unido a la proteína, ΔGsol(proteína). Los cálculos de estas dos energías libres de solvatación para una pose dada, i , se pueden calcular de acuerdo con,


Según el manual de  Gromacs,

gmx lie [-f [<.edr>]] [-o [<.xvg>]] [-b <time>] [-e <time>] [-dt <time>]

`                  `[-[no]w] [-xvg <enum>] [-Elj <real>] [-Eqq <real>]

`                  `[-Clj <real>] [-Cqq <real>] [-ligand <string>]

gmx  lie  computes  a  free  energy  estimate  based  on an energy analysis from nonbonded energies. One needs an energy file with the following components: Coul-(A-B)  LJ-SR  (A-B) etc.

Para utilizar gmx lie correctamente, se requieren dos simulaciones: una con la molécula de interés unida a su receptor y otra con la molécula en agua. Ambos necesitan utilizar energygrps de manera que los términos Coul-SR (A-B), LJ-SR (A-B), etc. se escriban en el archivo .edr. Los valores de la simulación de molécula en agua son necesarios para proporcionar valores adecuados para -Elj y -Eqq.

` `Options to specify input files:

`       `-f [<.edr>] (ener.edr)

`              `Energy file

`       `Options to specify output files:

`       `-o [<.xvg>] (lie.xvg)

`              `xvgr/xmgr file

`       `Other options:

`       `-b <time> (0)

`              `Time of first frame to read from trajectory (default unit ps)

`       `-e <time> (0)

`              `Time of last frame to read from trajectory (default unit ps)

`       `-dt <time> (0)

`              `Only use frame when t MOD dt = first time (default unit ps)

`       `-[no]w (no)

`              `View output .xvg, .xpm, .eps and .pdb files

`       `-xvg <enum> (xmgrace)

`              `xvg plot formatting: xmgrace, xmgr, none

`       `-Elj <real> (0)

`              `Lennard-Jones interaction between ligand and solvent

`       `-Eqq <real> (0)

`              `Coulomb interaction between ligand and solvent

`       `-Clj <real> (0.181)

`              `Factor in the LIE equation for Lennard-Jones component of energy

`       `-Cqq <real> (0.5)

`              `Factor in the LIE equation for Coulomb component of energy

`       `-ligand <string> (none)

`              `Name of the ligand in the energy file

El cálculo de una energía de interacción se realiza mediante la palabra clave energygrps en el archivo .mdp. A pesar de ser una palabra clave .mdp, los cálculos de energía de interacción no deben considerarse parte de una simulación normal.

La descomposición de las energías de corto alcance es incompatible con la ejecución en una GPU y también ralentiza el cálculo innecesariamente.

El módulo mdrun no necesita realizar este trabajo adicional para realizar una simulación válida. Como tal, solo calcule las energías de interacción como parte de su análisis, no su dinámica.

Cree un nuevo archivo .tpr a partir de un archivo .mdp que tenga energygrps = Protein LIG definido, como este:

| gmx grompp -f ie.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o ie.tpr |
| ------------------------------------------------------------------------------ |

Luego, invoque mdrun con la opción -rerun para recalcular energías de la trayectoria de simulación existente:

| gmx mdrun -deffnm ie -rerun md\_0\_10.xtc -nb cpu |
| ------------------------------------------------- |

Note el uso de -deffnm para leer ie.tpr y escribir todo archivos de salida a ie. \* como sus nombres de archivo. La opción -rerun toma el nombre de la trayectoria para la que desea volver a calcular las energías, y -nb cpu le dice a mdrun que solo intente ejecutarse en el hardware de la CPU e ignore cualquier GPU que pueda estar disponible. Como se indicó anteriormente, este tipo de cálculo no se puede realizar en una GPU. La repetición debe ser muy rápida, y se completará en solo unos minutos. Extraiga los términos de energía de interés a través del módulo de energía.

Los términos que nos interesan son Coul-SR: Protein-LIG y LJ-SR: Protein-LIG.

| gmx energy -f ie.edr -o integration\_energy.xvg |
| ----------------------------------------------- |

Tomemos la siguiente molécula ya estudiada,


Al haber sido estudiada como ligando, se tiene preparado el ITP y el PDB ya formateado con la estructura necesaria. Asi, se creará un sistema nuevo a través del protocolo empleado en el caso de la simulación de una molécula en agua. La secuencia de cálculos para la molécula del ligando es:

| #Caja y solvatación<br><br>gmx insert-molecules -ci ligand.pdb -nmol 1 -box 1 1 1 -o ligand\_box.pdb<br><br>gmx editconf -f ligand\_box.pdb -o ligand\_box\_pre.pdb -c -d 1 -bt dodecahedron<br><br>gmx solvate -cp ligand\_box\_pre.pdb -p ligand.top -o ligand\_solv.pdb<br><br>#Minimización<br><br>gmx grompp -f ligand\_em.mdp -c ligand\_solv.pdb -p ligand.top -o ligand\_em.tpr<br><br>gmx mdrun -v -deffnm ligand\_em<br><br>#Equilibrado isotérmico  NVT<br><br>gmx grompp -f ligand\_nvt.mdp -c ligand\_em.gro -p ligand.top -o ligand\_nvt.tpr<br><br>gmx mdrun -v -deffnm ligand\_nvt<br><br>#Equilibrado isobárico NPT<br><br>gmx grompp -f ligand\_npt.mdp -c ligand\_nvt.gro -t ligand\_nvt.cpt -p ligand.top -o ligand\_npt.tpr<br><br>gmx mdrun -v -deffnm ligand\_npt<br><br>#Corrida MD<br><br>gmx grompp -f ligand\_md.mdp -c ligand\_npt.gro -t ligand\_npt.cpt -p ligand.top -o ligand\_md.tpr<br><br>gmx mdrun -v -deffnm ligand\_md |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

Cálculo LIE propiamente dicho

Extracción de las energías de interacción entre ligando y agua

| gmx energy -s ligand\_md.tpr -f ligand\_md.edr |
| ---------------------------------------------- |

End your selection with an empty line or a zero.

\-------------------------------------------------------------------

1  Angle            2  Proper-Dih.      3  Improper-Dih.    4  LJ-14

5  Coulomb-14       6  LJ-(SR)          7  Disper.-corr.    8  Coulomb-(SR)

9  Coul.-recip.    10  Potential       11  Kinetic-En.     12  Total-Energy

13  Conserved-En.   14  Temperature     15  Pres.-DC        16  Pressure

17  Constr.-rmsd    18  Box-X           19  Box-Y           20  Box-Z

21  Volume          22  Density         23  pV              24  Enthalpy

25  Vir-XX          26  Vir-XY          27  Vir-XZ          28  Vir-YX

29  Vir-YY          30  Vir-YZ          31  Vir-ZX          32  Vir-ZY

33  Vir-ZZ          34  Pres-XX         35  Pres-XY         36  Pres-XZ

37  Pres-YX         38  Pres-YY         39  Pres-YZ         40  Pres-ZX

41  Pres-ZY         42  Pres-ZZ         43  #Surf\*SurfTen   44  Box-Vel-XX

45  Box-Vel-YY                          46  Box-Vel-ZZ

47  Coul-SR:LIG-LIG                     48  LJ-SR:LIG-LIG

49  Coul-14:LIG-LIG                     50  LJ-14:LIG-LIG

51  Coul-SR:LIG-rest                    52  LJ-SR:LIG-res

53  Coul-14:LIG-rest                    54  LJ-14:LIG-res

55  Coul-SR:rest-rest                   56  LJ-SR:rest-rest
` `57  Coul-14:rest-rest                   58  LJ-14:rest-rest
` `59  T-LIG           60  T-SOL           61  Lamb-LIG        62  Lamb-SOL

-Elj: Lennard-Jones interaction between ligand and solvent (51)
-Eqq: Coulomb interaction between ligand and solvent (52)

Salida,

Last energy frame read 1 time   60.000

Statistics over 30001 steps [ 0.0000 through 60.0000 ps ], 2 data sets

All statistics are over 301 points

Energy                      Average   Err.Est.       RMSD  Tot-Drift

\-------------------------------------------------------------------------------

Coul-SR:LIG-rest           -104.226         --    17.7147   -35.7738  (kJ/mol)

LJ-SR:LIG-rest             -183.449         --    13.2216     12.912  (kJ/mol)

Con esta información,

| gmx lie -f md.edr -o lie.xvg -b 20000 -Elj -183.449 -Eqq -104.226 -ligand LIG |
| ----------------------------------------------------------------------------- |

Salida,

Opened md.edr as single precision energy file

Using the following energy terms:

LJ:    LJ-SR:Protein-LIG  LJ-14:Protein-LIG  LJ-SR:LIG-rest  LJ-14:LIG-rest

Coul:  Coul-SR:Protein-LIG  Coul-14:Protein-LIG  Coul-SR:LIG-rest  Coul-14:LIG-rest

Last energy frame read 300 time 60000.000

DGbind = -10.330 (9.163)

La energía será de -10.330 kJ/mol. El gráfico obtenido,


Vemos que la energía se estabiliza a partir de los 45 ns, entonces podríamos recalcular,

| gmx lie -f md.edr -o lie.xvg -b 45000 -Elj -183.449 -Eqq -104.226 -ligand LIG |
| ----------------------------------------------------------------------------- |

Salida,

Last energy frame read 300 time 60000.000

DGbind = -13.148 (7.997)

Se hizo un cálculo de la energía de unión a través del método MM-PBSA y arrojó un resultado final de -130.541 (4.617) kJ/mol, así que se deberá tomar en cuenta estos factores de corrección así como el empleo de EXACTAMENTE las mismas condiciones de cálculo de la MD para Protein-LIG-SOL como para LIG-SOL. Por ejemplo, no debería emplearse PME en los métodos de cálculo (acá se usó por cuestiones de practicidad, pero fundamentalmente por ignorancia[^48]). Otros factores que pueden ser cambiados para acercarse a valores coincidentes con la evidencia experimental con los parámetros

-Clj (default 0.181) Factor in the LIE equation for Lennard-Jones component of energy

-Cqq (default 0.5) Factor in the LIE equation for Coulomb component of energy

Los valores de bibliografía que encontré fueron:

Cytochrome P450s (CYPs):

Cqq: 0.442

Clj: 0.087[^49]

Clj: 0.18

| Cqq   | Tipo de estructura                                                                                                                                                                                                                       |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0\.5  | Charged compounds                                                                                                                                                                                                                        |
| 0\.43 | Neutral compounds                                                                                                                                                                                                                        |
| 0\.37 | Neutral compounds bearing a single hydroxyl group                                                                                                                                                                                        |
| 0\.33 | <p>Hansson, T., Marelius, J., and Åqvist, J. (1998) Ligand binding affinity prediction by linear interaction energy methods. J Comput Aided Mol Des 12, 27-35.-27-35.</p><p>Neutral compounds bearing 2 or more hydroxyl groups[^50]</p> |

Cqq: 0.45

Clj: 0.21[^51]

Hice un promedio para estudiar variantes, hay que ver si funciona. Es más o menos así.

|     | Promedio | Desvio estandar | +2 SD   | -2 SD   |         |
| --- | -------- | --------------- | ------- | ------- |:------- |
|     | Cqq      | 0\.420          | 0\.0608 | 0\.5416 | 0\.2984 |
|     | Clj      | 0\.159          | 0\.0641 | 0\.2872 | 0\.0308 |

EM.MDP

| title        = Minimization    ; Title of run<br><br>; Parameters describing what to do, when to stop and what to save<br>integrator    = steep        ; Algorithm (steep = steepest descent minimization)<br>emtol        = 1000.0      ; Stop minimization when the maximum<br>; force < (10.0) [kJ mol-1 nm-1]<br>emstep      = 0.01      ; Energy step size en nanometros<br>nsteps        = 50000          ; Maximum number of (minimization) steps to perform<br>energygrps    = system    ; que grupos se escribiran, "system" es todo el sistema<br><br>; Parameters describing how to find the neighbors of each atom and how to calculate the interactions<br>nstlist            = 20            ; Frequency to update the neighbor<br>; list and long range forces, With parallel simulations and/or<br>; non-bonded force calculation on the GPU, a value of 20 or 40 often gives the best performance<br><br>cutoff-scheme   = Verlet<br><br>; The buffer size is automatically set based on verlet-buffer-tolerance,<br>; unless this is set to -1, in which case rlist will be used. This option has an explicit,<br>; exact cut-off at rvdw=rcoulomb. Currently only cut-off, reaction-field,<br>; PME electrostatics and plain LJ are supported.<br><br>ns-type            = grid        ; Method to determine neighbor list (simple, grid)<br><br>; grid = Make a grid in the box and only check atoms in neighboring grid cells<br>; when constructing a new neighbor list every nstlist<br>; steps. In large systems grid search is much faster than simple search.<br><br>; simple = Check every atom in the box when constructing a new neighbor<br>; list every nstlist steps (only with cutoff-scheme=group).<br><br>rlist            = 1.0        ; Cut-off for making neighbor list<br>; (short range forces) en nm<br><br>; Cut-off distance for the short-range neighbor list.<br>; With cutoff-scheme=Verlet, this is by default set by the<br>; verlet-buffer-tolerance option and the value of rlist is ignored.<br><br>coulombtype        = PME        ; Treatment of long range electrostatic interactions<br><br>; Fast smooth Particle-Mesh Ewald (SPME) electrostatics.<br>; Direct space is similar to the Ewald sum, while the<br>; reciprocal part is performed with FFTs. Grid dimensions are controlled<br>; with fourierspacing and the interpolation order with pme-order<br><br>rcoulomb        = 1.0        ; long range electrostatic cut-off distance for the Coulomb cut-off en nm<br>rvdw            = 1.0        ; long range Van der Waals cut-off distance<br>; for the LJ or Buckingham cut-off en nm<br>pbc             = xyz         ; Periodic Boundary Conditions |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

NVT.MDP

| title       = Protein-ligand complex NVT equilibration<br>define      = -DPOSRES  ; position restrain the protein and ligand,<br>; depende que incluye POSRES<br><br>; Run parameters<br>integrator  = md        ; leap-frog integrator<br>nsteps      = 50000     ; dt\*nsteps = tiempo --> Ejemplo si 0.002 ps \* 50000 stp = 100ps<br>dt          = 0.002     ; en ps, cuidado con ser >0.002 ps. fs<br><br>; Output control<br>nstxout     = 5000       ; save coordinates every (dt\*nsteps)<br>nstvout     = 5000      ; save velocities<br>nstenergy   = 5000       ; save energies<br>nstlog      = 5000       ; update log file<br>; energygrps  = Protein LIG ; recorder que acá los nombres deben ser correctos SOLO USAR SI ES NECESARIO Y NUNCA PARA CORRER LA DINAMICA<br><br>; Bond parameters<br>continuation    = no            ; first dynamics run<br>constraint-algorithm = lincs    ; holonomic constraints<br>constraints     = all-bonds     ; all bonds (even heavy atom-H bonds) constrained<br>lincs-iter      = 1             ; accuracy of LINCS<br>lincs-order     = 1             ; also related to accuracy<br><br>; Neighborsearching<br>cutoff-scheme   = Verlet<br>ns-type         = grid      ; search neighboring grid cells<br>nstlist         = 10        ; 20 fs, largely irrelevant with Verlet<br>rcoulomb        = 1.0       ; short-range electrostatic cutoff (in nm) para GROMOS<br>; es 1.4 y para CHARMM27 es 1.0<br>rvdw            = 1.0       ; short-range van der Waals cutoff (in nm) debe ser = rcoulomb<br><br>; Electrostatics<br>coulombtype     = PME       ; Particle Mesh Ewald for long-range electrostatics<br>pme-order       = 4         ; cubic interpolation<br>fourierspacing  = 0.12      ; grid spacing for FFT<br><br>; Temperature coupling<br>tcoupl      = V-rescale                     ; modified Berendsen thermostat<br>tc-grps     = Protein Non-Protein     ; two coupling groups - more accurate<br>tau-t       = 0.1   0.1                     ; time constant, in ps time constant<br>; for coupling (one for each group in tc-grps), -1 means no temperature coupling<br><br>ref-t       = 310   310                     ; reference temperature, one for each<br>; group, in K = T(C)+273<br><br>; Pressure coupling<br>pcoupl      = no        ; no pressure coupling in NVT<br><br>; Periodic boundary conditions<br>pbc         = xyz       ; 3-D PBC<br><br>; Dispersion correction<br>DispCorr    = EnerPres  ; account for cut-off vdW scheme<br><br>; no = don't apply any correction<br>; EnerPres = apply long range dispersion corrections for Energy and Pressure<br>; Ener = apply long range dispersion corrections for Energy only<br><br>; Velocity generation<br>gen-vel     = yes       ; assign velocities from Maxwell distribution<br>; no = Do not generate velocities. The velocities are set to zero when there are<br>; no velocities in the input structure file.<br>; yes = Generate velocities in grompp according to a Maxwell distribution at<br>; temperature gen-temp [K], with random seed gen-seed. This is only meaningful with integrator md.<br><br>gen-temp    = 310       ; temperature for Maxwell distribution<br>gen-seed    = -1        ; generate a random seed para comparar métodos<br>;  fijar con un valor diferente a (-1) |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

NPT.MDP

| title       = Protein-ligand complex NPT equilibration<br>define      = -DPOSRES  ; position restrain the protein and ligand<br>; Run parameters<br>integrator  = md        ; leap-frog integrator<br>nsteps      = 15000     ; numero de pasos<br>dt          = 0.002     ; en ps, 1 fs = 0.001 ps<br><br>; Output control<br>nstxout     = 500       ; save coordinates every 1.0 ps<br>nstvout     = 500       ; save velocities every 1.0 ps<br>nstenergy   = 500       ; save energies every 1.0 ps<br>nstlog      = 500       ; update log file every 1.0 ps<br>; energygrps  = Protein LIG ; recorder que acá los nombres deben ser correctos SOLO USAR SI ES NECESARIO Y NUNCA PARA CORRER LA DINAMICA<br><br><br>; Bond parameters<br>continuation    = yes           ; first dynamics run<br>constraint\_algorithm = lincs    ; holonomic constraints<br>constraints     = all-bonds     ; all bonds (even heavy atom-H bonds) constrained<br>lincs-iter      = 1             ; accuracy of LINCS<br>lincs-order     = 2             ; also related to accuracy<br><br>; Neighborsearching<br>cutoff-scheme   = Verlet<br>ns-type         = grid      ; search neighboring grid cells<br>nstlist         = 20        ; fs, largely irrelevant with Verlet<br>rcoulomb        = 1.0       ; short-range electrostatic cutoff (in nm)<br>rvdw            = 1.0       ; short-range van der Waals cutoff (in nm)<br><br>; Electrostatics<br>coulombtype     = PME       ; Particle Mesh Ewald for long-range electrostatics<br>pme-order       = 4         ; cubic interpolation<br>; Interpolation order for PME. 4 equals cubic interpolation.<br>; You might try 6/8/10 when running in parallel and simultaneously decrease grid dimension.<br><br>fourierspacing  = 0.12      ; grid spacing for FFT<br><br>; Temperature coupling<br>tcoupl      = V-rescale                     ; modified Berendsen thermostat<br>tc-grps     = Protein Non-Protein    ; two coupling groups - more accurate<br>tau-t       = 0.1   0.1                     ; time constant, in ps<br>ref-t       = 310   310                     ; reference temperature, one for each group, in K<br><br>; Pressure coupling<br>pcoupl      = Parrinello-Rahman             ; pressure coupling is on for NPT<br>pcoupltype  = isotropic                     ; uniform scaling of box vectors<br>tau-p       = 2.0                           ; time constant, in ps<br>ref-p       = 1.0                           ; reference pressure, in bar<br>compressibility = 4.5e-5                    ; isothermal compressibility of water,<br>; bar^-1 For water at 1 atm and 300 K constant a las temperaturas usuales<br>refcoord-scaling    = com<br><br>; Periodic boundary conditions<br>pbc         = xyz       ; 3-D PBC<br><br>; Dispersion correction<br>DispCorr    = EnerPres  ; account for cut-off vdW scheme<br><br>; Velocity generation<br>gen-vel     = no        ; velocity generation off after NVT |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

MD.MDP

| title       = Protein-ligand complex MD simulation<br>; Run parameters<br>integrator  = md        ; leap-frog integrator<br>nsteps      = 20000000   ; pasos<br>dt          = 0.002     ; ps / paso<br><br>; Output control<br>nstxout             = 0         ; suppress .trr output<br>nstvout             = 0         ; suppress .trr output<br>nstenergy           = 10000      ; save energies every 10.0 ps<br>nstlog              = 10000      ; update log file every 10.0 ps<br>nstxout-compressed  = 50000      ; write .xtc trajectory every 10.0 ps<br>compressed-x-grps   = System<br>; energygrps  = Protein LIG ; recorder que acá los nombres deben ser correctos SOLO USAR SI ES NECESARIO Y NUNCA PARA CORRER LA DINAMICA<br><br><br>; Bond parameters<br>continuation    = yes           ; first dynamics run<br>constraint\_algorithm = lincs    ; holonomic constraints<br>constraints     = all-bonds     ; all bonds (even heavy atom-H bonds) constrained<br>lincs-iter      = 1             ; accuracy of LINCS<br>lincs-order     = 2             ; also related to accuracy<br><br>; Neighborsearching<br>cutoff-scheme   = Verlet<br>ns-type         = grid      ; search neighboring grid cells<br>nstlist         = 25        ; 20 fs, largely irrelevant with Verlet<br>rcoulomb        = 1.0       ; short-range electrostatic cutoff (in nm)<br>rvdw            = 1.0       ; short-range van der Waals cutoff (in nm)<br><br>; Electrostatics<br>coulombtype     = PME       ; Particle Mesh Ewald for long-range electrostatics<br>pme-order       = 4         ; cubic interpolation<br>fourierspacing  = 0.12      ; grid spacing for FFT<br><br>; Temperature coupling<br>tcoupl      = V-rescale                     ; modified Berendsen thermostat<br>tc-grps     = Protein Non-Protein    ; two coupling groups - more accurate<br>tau-t       = 0.1   0.1                     ; time constant, in ps<br>ref-t       = 310   310                     ; reference temperature, one for each group, in K<br><br>; Pressure coupling<br>pcoupl      = Parrinello-Rahman             ; pressure coupling is on for NPT<br>pcoupltype  = isotropic                     ; uniform scaling of box vectors<br>tau-p       = 2.0                           ; time constant, in ps<br>ref-p       = 1.0                           ; reference pressure, in bar<br>compressibility = 4.5e-5                    ; isothermal compressibility of water, bar^-1<br><br>; Periodic boundary conditions<br>pbc         = xyz       ; 3-D PBC<br><br>; Dispersion correction<br>DispCorr    = EnerPres  ; account for cut-off vdW scheme<br><br>; Velocity generation<br>gen-vel     = no        ; assign velocities from Maxwell distribution |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

TOPOL.TOP

;

;    Example topology file

;

[ defaults ]

; nbfunc        comb-rule       gen-pairs       fudgeLJ fudgeQQ

`  `1             1               no              1.0     1.0

; The force field files to be included

#include "rt41c5.itp"

[ moleculetype ]

; name  nrexcl

Urea         3

[ atoms ]

;   nr    type   resnr  residu    atom    cgnr  charge

`     `1       C       1    UREA      C1       1     0.683

`     `2       O       1    UREA      O2       1    -0.683

`     `3      NT       1    UREA      N3       2    -0.622

`     `4       H       1    UREA      H4       2     0.346

`     `5       H       1    UREA      H5       2     0.276

`     `6      NT       1    UREA      N6       3    -0.622

`     `7       H       1    UREA      H7       3   0.346

`     `8       H       1    UREA      H8       3     0.276

[ bonds ]

;  ai    aj funct           c0           c1

`    `3     4     1 1.000000e-01 3.744680e+05

`    `3     5     1 1.000000e-01 3.744680e+05

`    `6     7     1 1.000000e-01 3.744680e+05

`    `6     8     1 1.000000e-01 3.744680e+05

`    `1     2     1 1.230000e-01 5.020800e+05

`    `1     3     1 1.330000e-01 3.765600e+05

`    `1     6     1 1.330000e-01 3.765600e+05

[ pairs ]

;  ai    aj funct           c0           c1

`    `2     4     1 0.000000e+00 0.000000e+00

`    `2     5     1 0.000000e+00 0.000000e+00

`    `2     7     1 0.000000e+00 0.000000e+00

`    `2     8     1 0.000000e+00 0.000000e+00

`    `3     7     1 0.000000e+00 0.000000e+00

`    `3     8     1 0.000000e+00 0.000000e+00

`    `4     6     1 0.000000e+00 0.000000e+00

`    `5     6     1 0.000000e+00 0.000000e+00

[ angles ]

;  ai    aj    ak funct           c0           c1

`    `1     3     4     1 1.200000e+02 2.928800e+02

`    `1     3     5     1 1.200000e+02 2.928800e+02

`    `4     3     5     1 1.200000e+02 3.347200e+02

`    `1     6     7     1 1.200000e+02 2.928800e+02

`    `1     6     8     1 1.200000e+02 2.928800e+02

`    `7     6     8     1 1.200000e+02 3.347200e+02

`    `2     1     3     1 1.215000e+02 5.020800e+02

`    `2     1     6     1 1.215000e+02 5.020800e+02

`    `3     1     6     1 1.170000e+02 5.020800e+02

[ dihedrals ]

;  ai    aj    ak    al funct           c0           c1           c2

`    `2     1     3     4     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `6     1     3     4     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `2     1     3     5     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `6     1     3     5     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `2     1     6     7     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `3     1     6     7     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `2     1     6     8     1 1.800000e+02 3.347200e+01 2.000000e+00

`    `3     1     6     8     1 1.800000e+02 3.347200e+01 2.000000e+00

[ dihedrals ]

;  ai    aj    ak    al funct           c0           c1

`    `3     4     5     1     2 0.000000e+00 1.673600e+02

`    `6     7     8     1     2 0.000000e+00 1.673600e+02

`    `1     3     6     2     2 0.000000e+00 1.673600e+02

; Include SPC water topology

#include "spc.itp"

[ system ]

Urea in Water

[ molecules ]

Urea    1

SOL    1000

Manual de trabajo con el cluster TUPAC


Ene. 2020

Acceso al cluster

El acceso al cluster se realiza a través de una conexión SSH. Esta conexión implica la creación de una sesión de usuario remota. SSH es un protocolo que se usa en  servidores UNIX/Linux. Este tipo de conexiones son extremadamente seguras y pueden estar encriptadas.

Considerando que el servidor es UNIX-like, el acceso se hará sin problemas desde cualquier otro OS UNIX-like tales como Linux o macOS. El cliente de SSH se encuentra instalado en todas las distros modernas así que no debería requerirse su instalación desde los repos o compilando. Windows, por el otro lado, no incluye en su soporte las herramientas de cliente de SSH. Esto significa que debemos instalar un cliente, deben existir muchos, pero se recomienda uno denominado PuTTY (http://www.putty.org) y es gratuito.

Tanto en UNIX como en Windows el cliente más básico se ejecuta desde la  línea de comandos. Esencialmente la conexión al servidor remoto, en este caso, el cluster será en general:

ssh usuario@direccion.del.servidor

Luego de esto aparecerá la orden de poner el password del usuario. Si el ingreso es por primera vez, se pedirá que cambie la contraseña inicial por otra más segura. El concepto de “contraseña segura” es para el servidor muy diferente que para nosotros. Es probable que cualquier contraseña que se nos haya ocurrido o usado en la vida no sirvan. Deberá consistir en 10 caracteres con mayúsculas, minúsculas y números. No deberá contener el nombre de usuario ni poseer una palabra del “diccionario”, esto es, no deberá contener palabras que el servidor pueda reconocer. La dirección del cluster es:

h2.tupac.gov.ar

Por lo tanto el comando para usar desde el cliente de SSH será:

ssh jcasal@h2.tupac.gov.ar

Donde jcasal es el nombre de usuario asignado. Una vez dentro de la sesión remota, lo único que aparecerá es el siguiente texto:

Last login: Fri Dec 2 12:54:53 2016 from

168\.96.251.133

Centro de Simulación Computacional para Aplicaciones Tecnológicas Consejo Nacional de Investigaciones Científicas y Técnicas

Le recordamos leer el contenido del archivo LEEME dentro de su home.  Ante cualquier duda registrar su consulta en  http://tupac.conicet.gov.ar/redmine

Sólo en caso de no poder utilizar el sistema de pedidos

escribir un correo a tupac@dc.uba.ar

Si aparece el siguiente mensaje:

ssh jcasal@h2.tupac.conicet.gov.ar

Este headnode se encuentra momentariamente fuera de servicio por mantenimiento.

Solo los administradores del sistema pueden conectarse.

Por favor utilizar h2.tupac.conicet.gov.ar para conectarse a TUPAC.

Cambiar a h2.tupac.conicet.gov.ar


Como todo será dentro de la consola, no tendremos interfaz gráfica.

Una aclaración muy importante es que no estarán disponibles las herramientas que usamos en nuestra distro. ¿Qué significa esto? Si tenemos un software específico XX instalado en nuestra computadora, y no está instalado en el cluster no podremos usarla.

Si quiero ver el contenido de la carpeta personal, empleo el comando ls -l


El ejecutable de GROMACS se deberá compilar especialmente para el cluster.

Para desconectarnos del cluster se usa el comando exit.

Transferencia de archivos al cluster

La transferencia de archivos no es tan sencilla como copiar y pegar (no tenemos interfaz gráfica) o usar comandos como cp y mv ya que trabajamos del lado del servidor, así que nuestros archivos locales NO están disponibles en forma sencilla. Por supuesto, desde la línea de comandos hay una forma de solucionarlo, pero prefiero hacerlo desde una interfaz gráfica. El programa que usaremos es Filezilla. Filezilla es un software libre que se puede instalar en cualquier computadora y presenta una interfaz gráfica que nos permita copiar de una carpeta a otra (<https://filezilla-project.org/download.php?type=client>). En nuestro caso, la otra carpeta será el cluster. Esto también se puede hacer al revés y descargar toda la información desde el cluster.

![https://lh6.googleusercontent.com/HaMZ5ayUVUDFJ39TTrxsN_v5vSGq3DIhGO4d8dv9gUR9F5KJnVqwDk2lEw-kIjfBQnuRIfxCJyta8UEDg_DTE_OKGITqVsXtC4M3UPENU3x1ajC85AxYYj6wo5AuTyfyat5-wLVx]

El protocolo de trabajo que emplearemos es el SFTP, que implica una transferencia segura de archivos. Las credenciales del servidor son las mismas que para ingresar desde la consola. El ingreso de la dirección del cluster y del nombre de usuario la haremos apretando el botón que parecen tres PCs pegaditas:

![https://lh5.googleusercontent.com/iN9z2m0u4T89lW-XaQn7ScOXlPr1IXmc4CLblBW5CYg5_ywJE98730Ld2N7oOs19IPlf0zIN8Dn2j-U6murJU7UYOvxIJeBZC33q-EfOsW4GuZfNkUHYkB-iVemHvJU9IQfByrLo]

Allí agregaremos un nuevo servidor “Nuevo sitio”, que yo lo llamé TUPAC


El protocolo deberá ser SFTP y el resto de las opciones se pueden dejar como están.

Una vez hecho esto se puede apretar “Conectar” y del lado derecho de la ventana de Filezilla nos aparecerán las carpetas del servidor.


Acá se pueden hacer todas las cosas que haríamos con el navegador de archivos de cualquier sistema operativo:

copiar

mover

cambiar nombre

borrar

crear carpetas

editar archivos, con ciertas limitaciones

O sea, todo lo que no implica la ejecución del software. Todos estos procesos llevan más tiempo del que estamos acostumbrados, ya que implican la transferencia de las órdenes a través de la red.


| <p>NOTA: Un mensaje del tipo</p><p></p><p>Respuesta:    fzSftp started, protocol\_version=8</p><p>Comando:    open "jcasal@h1.tupac.conicet.gov.ar" 22</p><p>Error:    Connection timed out after 20 seconds of inactivity</p><p>Error:    No se pudo conectar al servidor</p><p>Estado:    Desconectado del servidor</p><p></p><p>Significa que el cluster no está disponible.</p> |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

Cuando se hacen modificaciones y procesos, la información aparece en la sección inferior.


Manejo de las colas del cluster

Los procesos de paralelización implica la separación de la ejecución de un código en diferentes procesos. Una vez terminado, se juntan y se obtienen los resultados. Esto puede tener la ventaja de acelerar la velocidad de cálculo. En nuestro caso, GROMACS utiliza la librería OpenMPI y MPI para aprovechar este sistema.

El cluster se divide en nodos y estos en procesadores. Los nodos están conectados a través de interfaces de red física, o sea, cables y placas de red. Una cola es la forma en que se manejan los pedidos de cálculos. Por ejemplo, si hay un proceso corriendo en el mismo nodo que estamos usando, el cálculo se reenvía a otro proceso o nodo dependiendo de la carga del servidor. Si, en cambio, están todos los procesos ocupados o dados de baja, el servidor mantendrá “en vilo” al proceso hasta que se libere. Si el tiempo de espera es muy extenso, o no encuentra rápidamente los procesadores necesarios, el cálculo se detiene antes de empezar. El manejo de las colas se realiza con un sistema que se denomina SLURM.

Una vez dentro de los nodos de cabecera deberá hacer uso del SLURM, el sistema de colas de trabajos (PBS) para encolar trabajos paralelos, es decir, no deberá hacer uso directo de ningún de los nodos.

TUPAC cuenta de tres particiones, cada una con su respectivo tiempo límite (walltime)

\* batch: ya no se usa

\* fast: 1 hora

\* free-rider: tres días

Si no se especifica ninguna partición, tomará batch como partición por defecto y el tiempo máximo de dicha partición.

Está prohibido utilizar los headnode o cualquier equipo para realizar tareas por fuera del sistema de colas (incluido el post-procesamiento). Para tal fin puede solicitar un trabajo interactivo[^52]:

srun --pty bash

Mantenimiento Mensual

Los segundos sábados de cada mes, el edificio realiza una prueba en los grupos electrógenos que alimentan a todo el edificio. Se efectúa un corte de luz, generalmente programado en el horario de la mañana, que afecta a parte del equipamiento de cómputo de TUPAC. Todos los trabajos encolados antes de la fecha estimada se podrán encolar, pero solamente cambiarán de estado, para pasar a ejecución, aquellos trabajos que al momento de asignarle recursos la duración total o walltime de dicho trabajo sea anterior a la fecha. Los trabajos que se encuentren en ejecución al momento del corte son CANCELADOS y si no se cuenta con información de recuperación o reinicio, se pueden perder los resultados intermedios.

Un script de SLURM típico para nuestro trabajo sería el siguiente:

| <p>#!/bin/bash</p><p></p><p>#SBATCH --partition=free-rider   #particion a usar</p><p>#SBATCH --mail-user=juan.5ht@gmail.com</p><p>#SBATCH --mail-type=ALL          #informacion a dar por mail</p><p>#SBATCH --job-name="MD"          #nombre de la corrida</p><p>#SBATCH --time=2:00:00           #Tiempo en horas</p><p>#SBATCH --ntasks=16              #OpenMPI</p><p>#SBATCH --cpus-per-task=4        #MPI</p><p>#SBATCH -e %N.%j.err             #Logs de errores</p><p></p><p># El PATH “/home/jcasal/gromacs.bin/bin/gmx\_one” es el que ubica al</p><p># ejecutable de GROMACS, en MI home</p><p># Guardar este archivo como texto tipo “nombre-de-script.sh”</p><p></p><p>mpirun /home/jcasal/gromacs.bin/bin/gmx\_one mdrun -v -deffnm md</p><p></p><p># el mdrun es la ejecución de las MD de gromacs</p> |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

¿Qué significa cada parámetro?

#SBATCH --partition=free-rider

Es la partición.

#SBATCH --mail-user=juan.5ht@gmail.com
#SBATCH --mail-type=ALL

Estas opciones son para que el servidor nos envíe mails para avisarnos de todo (ALL) los que pasa en el cluster

#SBATCH --job-name="234R"
Es el nombre del trabajo. Sin espacios y fácil de recordar (otras opciones?)

#SBATCH --time=70:00:00
Es el tiempo de corrida en HH:MM:SS, recordar que el máximo es 72 horas.

#SBATCH --ntasks=700
En cuántos procesos se va a separar

#SBATCH --cpus-per-task=2
Cuántas CPU van a usar

#SBATCH --cpu-freq=Performance
#SBATCH --propagate
Opciones que modifican el manejo de los procesos.

#SBATCH -o slurm.%N.%j.out # STDOUT
#SBATCH -e slurm.%N.%j.err # STDERR
Los archivos de salida de información de la corrida.

Lo que sigue son los comandos por ejecutar. Cuidado, no debemos poner comandos que no soporten MPI a través de mpirun o mpiexec.

Otro script que encontré útil es

#!/bin/bash

#SBATCH --nodes=2

#SBATCH --ntasks-per-node=8

#SBATCH --partition=free-rider   #particion a usar

<a name="_1ksv4uv"></a>#SBATCH --cpu-freq=Performance
#SBATCH --propagate

#SBATCH --mail-user=juan.5ht@gmail.com

#SBATCH --mail-type=ALL          #informacion a dar por mail

#SBATCH --job-name="MD"          #nombre de la corrida

#SBATCH --time=2:00:00           #Tiempo en horas

#SBATCH -e %N.%j.err             #Logs de errores

module load gcc/6.4.0

export PATH=$PATH:/nfs/soft/r6/gcc-6.4.0/gromacs/2019.3/bin/

source /nfs/soft/r6/gcc-6.4.0/gromacs/2019.3/bin/GMXRC.bash

mpirun <COMANDOS>

Cálculo del tiempo de corrida

El tiempo a usar para una simulación dependerá de la simulación en sí, pero el límite está dado por las horas asignadas a nuestro usuario. Si tenemos 9600 horas en la partición batch. Estas horas corresponden a cada procesador y no al tiempo total. Si usamos un tiempo de 24 horas y empleamos 16 procesadores (16 CPUs), el tiempo real de uso será de: 24x16=384 horas. Por lo tanto debemos tener en cuenta la siguiente fórmula:

Tiempo real= (ntasks)⋅(cpus-per-task)⋅(time, en HH)

Las horas de corrida que quedan por mes serán:

Tiempo remanente= 9600 horas - Tiempo real

Iniciar un trabajo y verificar cómo evoluciona

sbatch nombre-del-script.sh

Submitted batch job 91487

Chequear el status

squeue -u [nombre de usuario]

` `JOBID PARTITION     NAME     USER  ST       TIME  NODES NODELIST(REASON)
` `88915 general-c GPU\_test      jcasal  PD       0:00      1 (Priority)
` `91487 general-c hello\_te      jcasal  PD       0:00      2 (Priority)

squeue -j 91487

` `JOBID PARTITION     NAME     USER  ST       TIME  NODES NODELIST(REASON)
` `91487 general-c hello\_te      jcasal  PD       0:00      2 (Priority)

Cancelar un trabajo

scancel [ID del trabajo]

Manejo básico de una terminal de UNIX


De “Linux Command-Line Cheat Sheet” By Benjamin Mako Hill and Jono Bacon
Computerworld | AUG 14, 2007

Moving Around the Filesystem

Commands for moving around the filesystem include the following.

pwd: The pwd command allows you to know the directory in which you're located (pwd stands for "print working directory"). For example, pwd in the desktop directory will show ~/Desktop. Note that the GNOME terminal also displays this information in the title bar of its window.

cd: The cd command allows you to change directories. When you open a terminal, you will be in your home directory. To move around the filesystem, use cd.

`  `•  To navigate to your desktop directory, use cd ~/Desktop

`  `•  To navigate into the root directory, use cd /

`  `•  To navigate to your home directory, use cd

`  `•  To navigate up one directory level, usecd ..

`  `•  To navigate to the previous directory (or back), use cd -

` `• To navigate through multiple levels of directories at once, use cd /var/www, for example, which will take you directly to the /www subdirectory of /var.

Manipulating Files and Folders

You can manipulate files and folders by using the following commands.

cp: The cp command makes a copy of a file for you. For example, cp file foo makes an exact copy of the file whose name you entered and names the copy foo, but the first file will still exist with its original name. After you use mv, the original file no longer exists, but after you use cp, that file stays and a new copy is made.

mv: The mv command moves a file to a different location or renames a file. Examples are as follows: mv file foo renames the original file to foo. mv foo ~/Desktop moves the file foo to your desktop directory but does not rename it. You must specify a new filename to rename a file. To save on typing, you can substitute ~ in place of the home directory. Note: If you are using mv with sudo, you will not be able to use the ~ shortcut. Instead, you will have to use the full pathnames to your files.

rm: Use this command to remove or delete a file in your directory. It does not work on directories that contain files.

ls: The ls command shows you the files in your current directory. Used with certain options, it lets you see file sizes, when files where created, and file permissions. For example, ls ~ shows you the files that are in your home directory.

mkdir: The mkdir command allows you to create directories. For example, mkdir music creates a music directory.

chmod: The chmod command changes the permissions on the files listed. Permissions are based on a fairly simple model. You can set permissions for user, group, and world, and you can set whether each can read, write, and/or execute the file. For example, if a file had permission to allow everybody to read but only the user could write, the permissions would read rwxr--r--. To add or remove a permission, you append a + or a - in front of the specific permission. For example, to add the capability for the group to edit in the previous example, you could type chmod g+x file.

chown: The chown command allows the user to change the user and group ownerships of a file. For example, chown jim file changes the ownership of the file to Jim.

System Information Commands

System information commands include the following.

df: The df command displays filesystem disk space usage for all partitions. The command df-h is probably the most useful. It uses megabytes (M) and gigabytes (G) instead of blocks to report. (-h means "human-readable.")

free: The free command displays the amount of free and used memory in the system. For example, free -m gives the information using megabytes, which is probably most useful for current computers.

top: The top command displays information on your Linux system, running processes, and system resources, including the CPU, RAM, swap usage, and total number of tasks being run. To exit top, press Q.

uname -a: The uname command with the -a option prints all system information, including machine name, kernel name, version, and a few other details. This command is most useful for checking which kernel you're using.

lsb\_release -a: The lsb\_release command with the -a option prints version information for the Linux release you're running. For example:

user@computer:~$ lsb\_release -a

LSB Version: n/a

Distributor ID: Ubuntu

Description: Ubuntu (The Breezy Badger Release)

Release:

Codename: breezy

ifconfig: This reports on your system's network interfaces.

iwconfig: The iwconfig command shows you any wireless network adapters and the wireless-specific information from them, such as speed and network connected.

ps: The ps command allows you to view all the processes running on the machine.

The following commands list the hardware on your computer, either of a specific type or with a specific method. They are most useful for debugging when a piece of hardware does not function correctly.

lspci: The lspci command lists all PCI buses and devices connected to them. This commonly includes network cards and sound cards.

lsusb: The lsusb command lists all USB buses and any connected USB devices, such as printers and thumb drives.

lshal: The lshal command lists all devices the hardware abstraction layer (HAL) knows about, which should be most hardware on your system.

lshw: The lshw command lists hardware on your system, including maker, type, and where it is connected.

Searching and Editing Text Files

Search and edit text files by using the following commands.

grep: The grep command allows you to search inside a number of files for a particular search pattern and then print matching lines. For example, grep blah file will search for the text "blah" in the file and then print any matching lines.

sed: The sed (or Stream EDitor) command allows search and replace of a particular string in a file. For example, if you want to find the string "cat" and replace it with "dog" in a file named pets, type sed s/cat/dog/g pets

Three other commands are useful for dealing with text.

cat: The cat command, short for concatenate, is useful for viewing and adding to text files. The simple command cat FILENAME displays the contents of the file. Using cat FILENAME file adds the contents of the first file to the second.

nano: Nano is a simple text editor for the command line. To open a file, use nano filename. Commands listed at the bottom of the screen are accessed via pressing Ctrl followed by the letter.

less: The less command is used for viewing text files as well as standard output. A common usage is to pipe another command through less to be able to see all the output, such as ls | less.

Dealing with Users and Groups

You can use the following commands to administer users and groups.

adduser: The adduser command creates a new user. To create a new user, simply type sudo adduser $loginname. This creates the user's home directory and default group. It prompts for a user password and then further details about the user.

passwd: The passwd command changes the user's password. If run by a regular user, it will change his or her password. If run using sudo, it can change any user's password. For example, sudo passwd joe changes Joe's password.

who: The who command tells you who is currently logged into the machine.

addgroup: The addgroup command adds a new group. To create a new group, type sudo addgroup $groupname.

deluser: The deluser command removes a user from the system. To remove the user's files and home directory, you need to add the -remove-home option.

delgroup: The delgroup command removes a group from the system. You cannot remove a group that is the primary group of any users.

Getting Help on the Command Line

This section provides you with some tips for getting help on the command line. The commands --help and man are the two most important tools at the command line.

Virtually all commands understand the -h (or --help) option, which produces a short usage description of the command and its options, then exits back to the command prompt. Try man -h or man --help to see this in action.

Every command and nearly every application in Linux has a man (manual) file, so finding such a file is as simple as typing man command to bring up a longer manual entry for the specified command. For example, man mv brings up the mv(move) manual.

Some helpful tips for using the man command include the following.

Arrow keys: Move up and down the man file by using the arrow keys.

q: Quit back to the command prompt by typing q.

man man: man man brings up the manual entry for the man command, which is a good place to start!

man intro: man intro is especially useful. It displays the Introduction to User Commands, which is a well-written, fairly brief introduction to the Linux command line.

There are also info pages, which are generally more in-depth than man pages. Try info info for the introduction to info pages.

Searching for Man Files

If you aren't sure which command or application you need to use, you can try searching the man files.

man -k foo: This searches the man files for "foo". Try man -k nautilus to see how this works. Note: man -k foo is the same as the apropos command.

man -f foo: This searches only the titles of your system's man files. Try man -f gnome, for example. Note: man -f foo is the same as the whatis command.

Using Wildcards

Sometimes you need to look at or use multiple files at the same time. For instance, you might want to delete all .rar files or move all .odt files to another directory. Thankfully, you can use a series of wildcards to accomplish such tasks.

\* matches any number of characters. For example, \*.rar matches any file with the ending .rar.

? matches any single character. For example, ?.rar matches a.rar but not ab.rar.

[characters] matches any of the characters within the brackets. For example, [ab].rar matches a.rar and b.rar but not c.rar.

[!characters] matches any characters that are not listed. For example, [!ab].rar matches c.rar but not a.rar or b.rar.

Executing Multiple Commands

Often you may want to execute several commands together, either by running one after another or by passing output from one to another.

Running Sequentially

If you need to execute multiple commands in sequence but don't need to pass output between them, there are two options based on whether or not you want the subsequent commands to run only if the previous commands succeed or not. If you want the commands to run one after the other regardless of whether or not preceding commands succeed, place a ; between the commands. For example, if you want to get information about your hardware, you could run lspci ; lsusb, which would output information on your PCI buses and USB devices in sequence.

However, if you need to conditionally run the commands based on whether the previous command has succeeded, insert && between commands. An example of this is building a program from source, which is traditionally done with ./configure, make, and make install. The commands make and make install require that the previous commands have completed successfully, so you would use ./configure && make && make install.

Passing Output

If you need to pass the output of one command so that it goes to the input of the next, after the character used between the commands, you need something called a pipe, which looks like a vertical bar or pipe (|). To use the pipe, insert the | between each command. For example, using the |in the command ls | less allows you to view the contents of the ls more easily.

2

[^1]:
    <a name="_44sinio"></a><https://www.cgl.ucsf.edu/chimera/>
    <https://www.cgl.ucsf.edu/chimera/current/docs/UsersGuide/framecore.html>
    http://www.swissparam.ch/SwissParam\_mol2\_file.html
    https://avogadro.cc/
    Gutman I., Polansky O.E. (1986) Molecular Topology. In: Mathematical Concepts in Organic Chemistry. Springer, Berlin, Heidelberg
    V. Zoete, M. A. Cuendet, A. Grosdidier, O. Michielin, SwissParam, a Fast Force Field Generation Tool For Small Organic Molecules, J. Comput. Chem, 2011, 32(11), 2359-68. PMID: 21541964, DOI: 10.1002/jcc.21816.
    <http://www.wwpdb.org/data/ccd>
    [    http://www.troubleshooters.com/linux/prepostpath.htm](http://www.troubleshooters.com/linux/prepostpath.htm)
    <https://www.geeksforgeeks.org/absolute-relative-pathnames-unix/>
    Buck M, Bouguet-Bonnet S, Pastor RW, MacKerell AD. Importance of the CMAP Correction to the CHARMM22 Protein Force Field: Dynamics of Hen Lysozyme. Biophysical Journal. 2006;90(4):L36-L38. doi:10.1529/biophysj.105.078154.
    Mark, Pekka, and Lennart Nilsson. "Structure and Dynamics of the TIP3P, SPC, and SPC/E Water Models at 298 K." The Journal of Physical Chemistry A 105.43 (2001): 9954-960. Web.
    [    http://manual.gromacs.org/online/top.html](http://manual.gromacs.org/online/top.html)
    https://spdbv.vital-it.ch/TheMolecularLevel/0Help/PDBContent.html
    Dependiendo de las conversiones que hicimos en el medio
    [    https://es.wikipedia.org/wiki/Dodecaedro](https://es.wikipedia.org/wiki/Dodecaedro)
    [    http://manual.gromacs.org/programs/gmx-genion.html](http://manual.gromacs.org/programs/gmx-genion.html)
    http://www.softsimu.net/downloads.shtml
    `   `http://www.st-abel.com/index\_htm\_files/Poster\_Biophysical\_2012\_final.pdf
    [    https://en.wikipedia.org/wiki/Energy_minimization](https://en.wikipedia.org/wiki/Energy_minimization)
    [    https://en.wikipedia.org/wiki/Constraint_algorithm](https://en.wikipedia.org/wiki/Constraint_algorithm)
    http://manual.gromacs.org/online/ndx.html
    http://www.elcodigoascii.com.ar/codigos-ascii/barra-linea-vertical-pleca-codigo-ascii-124.html
    Berendsen, H. J., Postma, J. V., van Gunsteren, W. F., DiNola, A. R. H. J., & Haak, J. R. (1984). Molecular dynamics with coupling to an external bath. The Journal of chemical physics, 81(8), 3684-3690.
    http://www.gromacs.org/Documentation/Terminology/Blowing\_Up
    En realidad, parece que lo hace en programas que no entienden qué pasó con los enlaces y con todo lo que tenga que ver con longitudes y ángulos, como el RMSD
    [    https://en.wikipedia.org/wiki/Frame_rate](https://en.wikipedia.org/wiki/Frame_rate)
    <https://en.wikipedia.org/wiki/Periodic_boundary_conditions>
    http://manual.gromacs.org/programs/gmx-view.html
    [    https://en.wikipedia.org/wiki/X_Window_System](https://en.wikipedia.org/wiki/X_Window_System)
    Kufareva, Irina, and Ruben Abagyan. “Methods of Protein Structure Comparison.” Methods in molecular biology (Clifton, N.J.) 857 (2012): 231–257. PMC. Web. 14 Feb. 2017.
    <http://plasma-gate.weizmann.ac.il/Grace/>
    [    http://manual.gromacs.org/programs/gmx-hbond.html](http://manual.gromacs.org/programs/gmx-hbond.html)
    Donald, J. E., Kulp, D. W. and DeGrado, W. F. (2011), Salt bridges: Geometrically specific, designable interactions. Proteins, 79: 898–915. doi:10.1002/prot.22927
    Richmond, T. (1984). Solvent accessible surface area and excluded volume in proteins. Journal of Molecular Biology, 178(1), pp.63-89.
    http://chemed.chem.purdue.edu/genchem/topicreview/bp/ch21/chemical.php
    Básicamente luché con ese tema por días.
    https://es.wikipedia.org/wiki/C\_Shell
    Van cambiando las restraints, los steps, los intervalos de tiempo. Falta que cambie la temperatura y cartón lleno.
    Ayuda a mejorar la simulación porque continúa a partir de la anterior
    Zafar, Ayesha, and Jóhannes Reynisson. “Hydration Free Energy as a Molecular Descriptor in Drug Design: A Feasibility Study.” Molecular Informatics 35, no. 5 (May 2016): 207–14. doi:10.1002/minf.201501035.
    Laboratory Journal – Business Web for Users in Science and Industry

    Wiley-VCH Verlag GmbH & Co. KGaA - http://www.laboratory-journal.com/science/pharma-drug-discovery/computational-drug-discovery-hydration-behavior-de-novo-designed-pharm
    Klimovich, Pavel V., Michael R. Shirts, and David L. Mobley. “Guidelines for the Analysis of Free Energy Calculations.” Journal of Computer-Aided Molecular Design 29, no. 5 (May 2015): 397–411. doi:10.1007/s10822-015-9840-9.
    No sé si es necesario hacerlo así
    g\_mmpbsa—A GROMACS Tool for High-Throughput MM-PBSA Calculations

    Rashmi Kumari-Rajendra Kumar-Andrew Lynn- - Journal of Chemical Information and Modeling - 2014
    Primer intento, papu
    Vosmeer CR, Kooi DP, Capoferri L, Terpstra MM, Vermeulen NPE, Geerke DP. Improving the iterative Linear Interaction Energy approach using automated recognition of configurational transitions. Journal of Molecular Modeling. 2016;22:31. doi:10.1007/s00894-015-2883-y.
    Linear Interaction Energy (LIE) Models for Ligand Binding in Implicit Solvent: Theory and Application to the Binding of NNRTIs to HIV-1 Reverse Transcriptase. Yang Su, Emilio Gallicchio, Kalyan Das, Eddy Arnold, and Ronald M. Levy. J. Chem. Theory Comput. 2007, 3, 256-277.
    La verdad, no funcionó.
    [ref1]: Aspose.Words.28bd518c-a9c3-4b19-847e-48d6b51a7f0d.004.png
    [ref2]: Aspose.Words.28bd518c-a9c3-4b19-847e-48d6b51a7f0d.012.png
    [ref3]: Aspose.Words.28bd518c-a9c3-4b19-847e-48d6b51a7f0d.028.png
    [ref4]: Aspose.Words.28bd518c-a9c3-4b19-847e-48d6b51a7f0d.030.png
    [https://lh6.googleusercontent.com/HaMZ5ayUVUDFJ39TTrxsN_v5vSGq3DIhGO4d8dv9gUR9F5KJnVqwDk2lEw-kIjfBQnuRIfxCJyta8UEDg_DTE_OKGITqVsXtC4M3UPENU3x1ajC85AxYYj6wo5AuTyfyat5-wLVx]: Aspose.Words.28bd518c-a9c3-4b19-847e-48d6b51a7f0d.108.png
    [https://lh5.googleusercontent.com/iN9z2m0u4T89lW-XaQn7ScOXlPr1IXmc4CLblBW5CYg5_ywJE98730Ld2N7oOs19IPlf0zIN8Dn2j-U6murJU7UYOvxIJeBZC33q-EfOsW4GuZfNkUHYkB-iVemHvJU9IQfByrLo]: Aspose.Words.28bd518c-a9c3-4b19-847e-48d6b51a7f0d.109.png
