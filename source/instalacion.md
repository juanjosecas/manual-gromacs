# Instalación de GROMACS

Esta sección corresponde a **GROMACS 2026.3**. Antes de instalar conviene decidir qué se necesita:

- **Paquete de la distribución:** instalación rápida para aprendizaje, análisis y pruebas. Puede no ser la versión más reciente ni estar optimizado para el hardware.
- **Compilación desde código fuente:** recomendada para producción, GPU, clústeres y control preciso de dependencias.
- **MPI externo:** necesario principalmente para ejecuciones que abarcan varios nodos. Para una sola estación de trabajo, la compilación normal con thread-MPI suele ser suficiente.
- **gmxapi:** interfaz de Python opcional. Requiere primero una instalación compatible de GROMACS.

La guía oficial vigente requiere CMake 3.28 o posterior, un compilador C99 y un compilador C++17. Para GROMACS 2026.3, las versiones mínimas indicadas son GCC 11, Clang 14 o MSVC 2019.

## Comprobación del sistema

Antes de instalar:

```bash
uname -a
cmake --version
gcc --version
g++ --version
python3 --version
```

Si se utilizará una GPU NVIDIA:

```bash
nvidia-smi
nvcc --version
```

**nvidia-smi** informa el controlador instalado y la versión máxima de CUDA admitida por ese controlador. **nvcc --version** informa la versión del toolkit usado para compilar. No son la misma cosa.

Según la compatibilidad menor publicada por NVIDIA:

| Familia del toolkit | Controlador mínimo |
| ------------------- | ------------------:|
| CUDA 13.x           | 580                |
| CUDA 12.x           | 525                |
| CUDA 11.x           | 450                |

Un controlador más nuevo puede ejecutar aplicaciones compiladas con una familia CUDA anterior mediante compatibilidad hacia atrás. La tabla es un requisito mínimo general; deben revisarse también las notas de la versión concreta del toolkit y la compatibilidad de la GPU.

## Instalación mediante el gestor de paquetes

### Ubuntu y Debian

```bash
sudo apt update
sudo apt install gromacs
```

Comprobación:

```bash
gmx --version
```

El paquete disponible depende de la versión de Ubuntu o Debian. Esta vía es adecuada si la versión empaquetada satisface el protocolo. Para simulaciones de producción conviene revisar en la salida de **gmx --version** el soporte SIMD, FFT, MPI y GPU.

### Fedora

```bash
sudo dnf install gromacs
```

Algunas variantes empaquetadas pueden instalar ejecutables o módulos separados para MPI. Compruebe los nombres proporcionados por la versión de Fedora:

```bash
rpm -ql gromacs | grep /bin/

gmx --version
```

### Arch Linux y Manjaro

```bash
sudo pacman -S gromacs

gmx --version
```

### macOS con Homebrew

```bash
brew update

brew install gromacs

gmx --version
```

La aceleración CUDA no está disponible en macOS. En equipos Apple Silicon, la compilación nativa puede aprovechar SIMD y la GPU solo mediante backends admitidos por la versión de GROMACS y las herramientas disponibles; no debe asumirse que una fórmula de Homebrew incluye aceleración por GPU.

## Windows y WSL2

La ruta más práctica para ejecutar GROMACS en Windows es WSL2 con una distribución Linux. Después de instalar WSL2 y Ubuntu, los comandos de instalación y compilación son los mismos que en Linux.

Desde PowerShell con privilegios de administrador:

```powershell
wsl --install -d Ubuntu
wsl --update
```

Dentro de Ubuntu:

```bash
sudo apt update

sudo apt install gromacs

gmx --version
```

Para usar una GPU NVIDIA dentro de WSL2 se necesita un controlador de Windows compatible con WSL; no debe instalarse un controlador Linux NVIDIA dentro de la distribución WSL. El toolkit CUDA de usuario puede instalarse dentro de WSL cuando sea necesario para compilar. Verifique desde WSL:

```bash
nvidia-smi
```

## Compilación desde código fuente

### Dependencias en Ubuntu o Debian

```bash
sudo apt update

sudo apt install build-essential cmake git python3 libfftw3-dev libhwloc-dev
```

Para una compilación MPI agregue:

```bash
sudo apt install openmpi-bin libopenmpi-dev
```

### Dependencias en Fedora

```bash
sudo dnf install gcc gcc-c++ cmake make git python3 fftw-devel hwloc-devel
```

Para MPI:

```bash
sudo dnf install openmpi openmpi-devel
```

En Fedora puede ser necesario cargar el entorno de OpenMPI según cómo esté empaquetado:

```bash
module load mpi/openmpi-x86_64
```

Si el comando **module** no existe o el módulo tiene otro nombre, examine los archivos instalados por el paquete OpenMPI.

### Descarga y compilación básica para CPU

Use una carpeta de compilación separada del código fuente. El prefijo bajo `$HOME/opt` evita requerir permisos de administrador durante la instalación.

Aclaración: un "\" al final de la línea indica que el comando continúa en la siguiente línea. Esto funciona en Linux, macOS y WSL2. En Windows PowerShell se puede escribir todo en una línea o usar el carácter de continuación de PowerShell. Es por una cuestión de visualización, si resulta molesto, se puede escribir todo en una sola línea.

```bash
wget https://ftp.gromacs.org/gromacs/gromacs-2026.3.tar.gz

tar xfz gromacs-2026.3.tar.gz

cd gromacs-2026.3

mkdir build

cd build

cmake .. -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3"

cmake --build . --parallel

ctest --output-on-failure

cmake --install .
```

Active la instalación:

```bash
source "$HOME/opt/gromacs-2026.3/bin/GMXRC"

gmx --version
```

Para cargarla automáticamente al iniciar Bash:

```bash
echo 'source "$HOME/opt/gromacs-2026.3/bin/GMXRC"' >> "$HOME/.bashrc"
```

**GMX_BUILD_OWN_FFTW=ON** descarga y compila FFTW. Si existe una instalación adecuada de FFTW puede omitirse. La FFTW suministrada por GROMACS es una elección simple y reproducible para una estación de trabajo.

## Compilación con GPU NVIDIA

Primero instale un controlador NVIDIA compatible y el toolkit CUDA siguiendo el método correspondiente a la distribución. No mezcle paquetes CUDA de repositorios incompatibles. Verifique:

```bash
nvidia-smi

nvcc --version
```

Configure GROMACS con el backend CUDA:

```bash
cd gromacs-2026.3

mkdir build-cuda

cd build-cuda

cmake .. -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DGMX_GPU=CUDA \
    -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3-cuda"

cmake --build . --parallel

ctest --output-on-failure

cmake --install .
```

Active y compruebe:

```bash
source "$HOME/opt/gromacs-2026.3-cuda/bin/GMXRC"
gmx --version
gmx mdrun -version
```

La salida debe indicar que GROMACS fue compilado con soporte CUDA. Que CUDA aparezca en **nvidia-smi** no demuestra que el ejecutable de GROMACS tenga soporte GPU.

Para comprobar el acceso real al dispositivo:

```bash
nvidia-smi -L
```

La aceleración efectiva depende del tamaño del sistema, el modelo de GPU, CPU, red, configuración PME y opciones de **gmx mdrun**. No se debe forzar la descarga de todas las tareas a GPU sin medir el rendimiento.

## Compilación con MPI para clústeres

La compilación MPI externa se usa para distribuir una simulación entre varios nodos. Puede coexistir con la instalación normal; el ejecutable suele llamarse **gmx_mpi**.

```bash
cd gromacs-2026.3
mkdir build-mpi
cd build-mpi

cmake .. -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DGMX_MPI=ON \
    -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3-mpi"

cmake --build . --parallel

ctest --output-on-failure

cmake --install .
```

Comprobación:

```bash
source "$HOME/opt/gromacs-2026.3-mpi/bin/GMXRC"

gmx_mpi --version

mpirun -np 2 gmx_mpi --version
```

Para combinar MPI y CUDA:

```bash
cmake .. -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DGMX_MPI=ON \
    -DGMX_GPU=CUDA \
    -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3-mpi-cuda"
```

En un clúster deben usarse el lanzador y las variables indicadas por el gestor de trabajos. Un comando local con **mpirun** no sustituye un script de SLURM, PBS u otro planificador.

## Opciones CMake relevantes

| Opción                          | Uso                                                                                                 |
| ------------------------------- | --------------------------------------------------------------------------------------------------- |
| **-DGMX_MPI=ON**                | Compila con MPI externo.                                                                            |
| **-DGMX_GPU=CUDA**              | Activa GPU NVIDIA mediante CUDA.                                                                    |
| **-DGMX_GPU=OpenCL**            | Activa el backend OpenCL.                                                                           |
| **-DGMX_GPU=SYCL**              | Activa el backend SYCL.                                                                             |
| **-DGMX_SIMD=valor**            | Selecciona explícitamente SIMD; normalmente conviene la autodetección.                              |
| **-DGMX_DOUBLE=ON**             | Compila en doble precisión; es más lento y rara vez necesario para dinámica molecular convencional. |
| **-DGMX_FFT_LIBRARY=fftw3**     | Selecciona la biblioteca FFT.                                                                       |
| **-DBUILD_SHARED_LIBS=ON**      | Genera bibliotecas compartidas; es necesario para ciertos clientes, incluido gmxapi.                |
| **-DCMAKE_INSTALL_PREFIX=ruta** | Define el directorio de instalación.                                                                |
| **-DCMAKE_BUILD_TYPE=Debug**    | Compilación de depuración; no es adecuada para producción.                                          |

Las opciones antiguas **-DGMX_GPU=ON** y **-DGMX_USE_OPENCL=ON** no deben usarse con GROMACS 2026. El backend se selecciona directamente mediante **-DGMX_GPU=CUDA**, **OpenCL** o **SYCL**.

## Compilación reproducible dentro de Docker

Un contenedor permite fijar la distribución Linux, compiladores, bibliotecas, versión de CUDA de usuario y opciones de CMake. Esto mejora la reproducibilidad del entorno y evita contaminar el sistema anfitrión. No vuelve al ejecutable universal ni garantiza resultados idénticos bit a bit: el kernel, el controlador NVIDIA, la arquitectura CPU, la GPU y la asignación de hilos siguen perteneciendo al anfitrión.

La imagen debe construirse para una versión exacta de GROMACS. No conviene descargar “la última versión” durante cada compilación. Los ejemplos siguientes fijan **GROMACS 2026.3**, verifican el MD5 publicado para el archivo fuente y utilizan una construcción multietapa para que la imagen final no contenga compiladores ni archivos temporales.

### Requisitos del anfitrión

Para CPU sólo se necesitan Docker Engine o Docker Desktop y espacio suficiente para compilar:

```bash

docker version

docker info
```

En Linux con una GPU NVIDIA se necesitan además:

1. un controlador NVIDIA instalado en el anfitrión;
2. NVIDIA Container Toolkit;
3. el runtime de Docker configurado para exponer la GPU.

El controlador se instala únicamente en el anfitrión. La imagen contiene el toolkit y las bibliotecas CUDA de usuario, pero no reemplaza al controlador.

Después de instalar NVIDIA Container Toolkit:

```bash
sudo nvidia-ctk runtime configure --runtime=docker

sudo systemctl restart docker
```

Compruebe el acceso antes de compilar GROMACS:

```bash
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

Si este comando falla, el problema está en Docker, el runtime NVIDIA o el controlador del anfitrión; recompilar GROMACS no lo corrige.

### Imagen CPU portable para x86-64

Cree un archivo llamado **Dockerfile.cpu**:

```dockerfile
FROM ubuntu:24.04 AS builder

ARG GROMACS_VERSION=2026.3
ARG GROMACS_MD5=7987af0c6ab939ab6e639f32d0dd260f
ARG GMX_SIMD=SSE2

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

RUN curl -fL \
    "https://ftp.gromacs.org/gromacs/gromacs-${GROMACS_VERSION}.tar.gz" \
    -o gromacs.tar.gz \
    && echo "${GROMACS_MD5}  gromacs.tar.gz" | md5sum -c - \
    && tar xzf gromacs.tar.gz \
    && cmake -S "gromacs-${GROMACS_VERSION}" -B gromacs-build \
        -DGMX_BUILD_OWN_FFTW=ON \
        -DREGRESSIONTEST_DOWNLOAD=ON \
        -DGMX_SIMD="${GMX_SIMD}" \
        -DGMX_GPU=OFF \
        -DGMX_MPI=OFF \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/gromacs \
    && cmake --build gromacs-build --parallel \
    && ctest --test-dir gromacs-build --output-on-failure \
    && cmake --install gromacs-build

FROM ubuntu:24.04 AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/gromacs /opt/gromacs

ENV PATH="/opt/gromacs/bin:${PATH}"
ENV LD_LIBRARY_PATH="/opt/gromacs/lib:${LD_LIBRARY_PATH}"

WORKDIR /work

ENTRYPOINT ["gmx"]
CMD ["--version"]
```

Construya la imagen:

```bash
docker build --pull --no-cache \
  -f Dockerfile.cpu \
  -t gromacs:2026.3-cpu .
```

El valor **SSE2** se eligió como mínimo común denominador razonable para x86-64. Aumenta la posibilidad de ejecutar la misma imagen en procesadores x86-64 distintos, pero reduce el rendimiento respecto de AVX2 o AVX-512. Para una imagen destinada a un único nodo o a máquinas homogéneas puede compilarse otra variante:

```bash
docker build --pull \
  --build-arg GMX_SIMD=AVX2_256 \
  -f Dockerfile.cpu \
  -t gromacs:2026.3-cpu-avx2 .
```

Esa imagen fallará o no será apropiada en CPU sin AVX2. Una imagen construida para **linux/amd64** tampoco se vuelve compatible automáticamente con ARM64. En ARM debe realizarse una compilación nativa con el SIMD correspondiente; la emulación mediante QEMU sirve para construir o probar, pero no para medir rendimiento de dinámica molecular.

### Imagen con CUDA para GPU NVIDIA

GROMACS 2026.3 requiere CUDA 12.1 o posterior y una GPU con capacidad de cómputo 5.0 o superior. El ejemplo utiliza CUDA 12.6 sobre Ubuntu 24.04, una combinación incluida entre las plataformas de prueba declaradas para esta versión.

Cree **Dockerfile.cuda**:

```dockerfile
FROM nvidia/cuda:12.6.3-devel-ubuntu24.04 AS builder

ARG GROMACS_VERSION=2026.3
ARG GROMACS_MD5=7987af0c6ab939ab6e639f32d0dd260f
ARG CUDA_ARCHITECTURES="52;60;61;70;75;80;86;89;90"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

RUN curl -fL \
    "https://ftp.gromacs.org/gromacs/gromacs-${GROMACS_VERSION}.tar.gz" \
    -o gromacs.tar.gz \
    && echo "${GROMACS_MD5}  gromacs.tar.gz" | md5sum -c - \
    && tar xzf gromacs.tar.gz \
    && cmake -S "gromacs-${GROMACS_VERSION}" -B gromacs-build \
        -DGMX_BUILD_OWN_FFTW=ON \
        -DREGRESSIONTEST_DOWNLOAD=ON \
        -DGMX_GPU=CUDA \
        -DCUDAToolkit_ROOT=/usr/local/cuda \
        -DCMAKE_CUDA_ARCHITECTURES="${CUDA_ARCHITECTURES}" \
        -DGMX_MPI=OFF \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/opt/gromacs \
    && cmake --build gromacs-build --parallel \
    && ctest --test-dir gromacs-build --output-on-failure \
    && cmake --install gromacs-build

FROM nvidia/cuda:12.6.3-runtime-ubuntu24.04 AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/gromacs /opt/gromacs

ENV PATH="/opt/gromacs/bin:${PATH}"
ENV LD_LIBRARY_PATH="/opt/gromacs/lib:${LD_LIBRARY_PATH}"

WORKDIR /work

ENTRYPOINT ["gmx"]
CMD ["--version"]
```

Construya y verifique:

```bash
docker build --pull --no-cache \
  -f Dockerfile.cuda \
  -t gromacs:2026.3-cuda12.6 .

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 --version

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 mdrun -version
```

La lista de **CMAKE_CUDA_ARCHITECTURES** genera código para varias generaciones y aumenta el tiempo de compilación y el tamaño de la imagen. Puede reducirse para un parque homogéneo. Por ejemplo, una RTX 3060 utiliza SM 86 y una Tesla P100 utiliza SM 60:

```bash
docker build --pull \
  --build-arg CUDA_ARCHITECTURES="60;86" \
  -f Dockerfile.cuda \
  -t gromacs:2026.3-cuda12.6-sm60-sm86 .
```

No agregue una arquitectura que el toolkit seleccionado ya no admita. Si se busca máxima portabilidad entre GPU NVIDIA, es preferible conservar la lista predeterminada de arquitecturas generada por GROMACS o definir explícitamente todas las GPU reales que deberán ejecutar la imagen.

### Compatibilidad entre la imagen CUDA y el controlador

La versión mostrada por **nvidia-smi** como “CUDA Version” es la versión máxima admitida por el controlador, no el toolkit contenido en la imagen. Para ejecutar una imagen basada en CUDA 12.x, el controlador Linux debe cumplir como mínimo el requisito de esa familia; la tabla general de compatibilidad menor de NVIDIA indica controlador 525 o posterior para CUDA 12.x. Algunas características que combinan PTX, bibliotecas nuevas o hardware reciente pueden exigir un controlador más nuevo.

Verifique ambos lados:

```bash
nvidia-smi

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 mdrun -version
```

La primera orden caracteriza el anfitrión. La segunda confirma cómo fue compilado GROMACS y si el contenedor ve la GPU.

### Ejecutar una simulación conservando los archivos

Los datos no deben quedar únicamente dentro de la capa efímera del contenedor. Monte el directorio actual en **/work** y use el UID y GID del usuario para evitar archivos propiedad de root:

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cpu \
  grompp -f md.mdp -c npt.gro -t npt.cpt \
  -p topol.top -o md.tpr
```

Para producción con NVIDIA:

```bash
docker run --rm -it \
  --gpus all \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cuda12.6 \
  mdrun -deffnm md -ntmpi 1 -ntomp 8
```

Como el Dockerfile define **ENTRYPOINT ["gmx"]**, después del nombre de la imagen se escribe directamente la suborden, por ejemplo **grompp**, **mdrun** o **rms**. El directorio montado conserva TPR, trayectorias, energías, logs y checkpoints cuando se elimina el contenedor.

Si Docker tiene un límite de CPU o memoria, GROMACS sólo podrá usar los recursos asignados. Conviene declararlos de forma explícita cuando se comparan rendimientos:

```bash
docker run --rm \
  --gpus all \
  --cpuset-cpus 0-7 \
  --memory 24g \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cuda12.6 \
  mdrun -deffnm md -ntmpi 1 -ntomp 8
```

### Validación mínima de la imagen

La compilación ejecuta **ctest**, pero la imagen GPU se construye normalmente sin acceso a un dispositivo. Debe realizarse una prueba de ejecución en cada clase de hardware de destino.

Registre la configuración:

```bash
docker image inspect gromacs:2026.3-cuda12.6 > image-inspect.json

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 mdrun -version
```

Después ejecute un sistema pequeño y examine el log:

```bash
docker run --rm --gpus all \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cuda12.6 \
  mdrun -s test.tpr -deffnm test -nsteps 1000
```

Compruebe en **test.log**:

- versión y precisión de GROMACS;
- SIMD detectado;
- backend CUDA;
- GPU seleccionada;
- número de rangos y de hilos;
- ausencia de errores LINCS, NaN o fallos del dispositivo;
- rendimiento coherente con una ejecución nativa equivalente.

Una diferencia numérica pequeña entre hardware, número de hilos o backends no implica por sí sola un error: la dinámica molecular es caótica y las reducciones en coma flotante no son asociativas. La validación debe comparar conservación, distribuciones y propiedades estadísticas, no exigir trayectorias idénticas marco a marco.

### Reproducibilidad de la imagen

Una etiqueta como **ubuntu:24.04** o **nvidia/cuda:12.6.3-runtime-ubuntu24.04** puede apuntar posteriormente a una imagen base reconstruida. Para congelar una imagen publicada se debe registrar y usar su digest:

```dockerfile
FROM ubuntu:24.04@sha256:DIGEST_VERIFICADO AS builder
```

El digest se obtiene del registro utilizado y debe conservarse junto con:

- Dockerfile;
- versión y suma de comprobación de GROMACS;
- digest de cada imagen base;
- salida de **docker version**;
- salida de **gmx mdrun -version**;
- controlador y modelo de GPU;
- comando exacto de construcción y ejecución.

**--no-cache** fuerza una reconstrucción limpia, pero no garantiza reproducibilidad si los repositorios APT cambiaron. Para reconstrucciones archivables se necesitan además repositorios con instantáneas o una imagen ya construida identificada por digest.

### MPI, clústeres y límites prácticos

La imagen propuesta usa thread-MPI, apropiado para una estación de trabajo o un solo nodo. Construir con **GMX_MPI=ON** dentro del contenedor es posible, pero ejecutar eficientemente entre nodos requiere compatibilidad con el MPI, la red de alta velocidad, UCX/OFED y el lanzador del clúster. Encapsular una biblioteca MPI arbitraria puede anular RDMA o generar incompatibilidades con SLURM.

En HPC suele ser más simple construir una imagen OCI validada y ejecutarla mediante Apptainer/Singularity, o compilar GROMACS contra la pila MPI suministrada por el centro. Para multinodo, la portabilidad del contenedor debe validarse con el administrador y con una prueba de escalamiento; que **mpirun** funcione dentro de una computadora no demuestra compatibilidad multinodo.

### Fallos frecuentes

- Instalar el controlador NVIDIA dentro de la imagen.
- Confundir el toolkit CUDA de la imagen con el controlador del anfitrión.
- Compilar con AVX2 o AVX-512 y asumir que la imagen funcionará en cualquier CPU.
- Usar una etiqueta **latest** para GROMACS, Ubuntu o CUDA.
- No montar el directorio de trabajo y perder los resultados al eliminar el contenedor.
- Ejecutar como root y dejar archivos sin permisos para el usuario.
- Omitir **--gpus all** y concluir que GROMACS fue compilado sin CUDA.
- Probar sólo **gmx --version** sin ejecutar un sistema pequeño.
- Suponer que Docker elimina las diferencias numéricas entre GPU y CPU.
- Copiar una imagen CUDA a un nodo cuyo controlador es demasiado antiguo.

## Instalación de gmxapi para Python

gmxapi requiere una instalación previa de GROMACS compilada con **GMXAPI=ON** y **BUILD_SHARED_LIBS=ON**. Ambas opciones suelen estar activadas por defecto, pero conviene declararlas cuando se prepara una instalación destinada a Python:

```bash
cmake .. -DGMX_BUILD_OWN_FFTW=ON \
    -DREGRESSIONTEST_DOWNLOAD=ON \
    -DGMXAPI=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_PREFIX="$HOME/opt/gromacs-2026.3"
```

Después de instalar GROMACS, cree un entorno virtual. gmxapi admite Python 3.9 o posterior.

```bash
python3 -m venv "$HOME/venvs/gmxapi-2026"
source "$HOME/venvs/gmxapi-2026/bin/activate"

python -m pip install --upgrade pip setuptools wheel cmake pybind11
source "$HOME/opt/gromacs-2026.3/bin/GMXRC"

python -m pip install --no-cache-dir gmxapi
```

Si el instalador no encuentra GROMACS:

```bash
gmxapi_ROOT="$HOME/opt/gromacs-2026.3" python -m pip install --no-cache-dir gmxapi
```

Comprobación:

```bash
python -c "import gmxapi; print(gmxapi.__version__)"
```

Después de actualizar o recompilar GROMACS con otro compilador, MPI o precisión, reinstale gmxapi sin usar la caché. Una rueda compilada contra otra instalación puede importar incorrectamente o fallar por símbolos incompatibles.

## Verificación final

```bash
which gmx

gmx --version

gmx mdrun -version
```

Compruebe al menos:

- versión exacta de GROMACS;
- compilador y precisión;
- SIMD;
- biblioteca FFT;
- soporte MPI o thread-MPI;
- backend GPU;
- ruta del archivo de datos.

Una prueba mínima del ejecutable no reemplaza los tests:

```bash
gmx help

gmx check -h
```

Para diagnosticar qué ejecutable se está usando cuando existen varias instalaciones:

```bash
type -a gmx
echo "$PATH"
```

Si se activa otro entorno, módulo o instalación, ejecute nuevamente el **GMXRC** correspondiente antes de continuar.

## Fuentes

1. [Guía de instalación de GROMACS 2026.3](https://manual.gromacs.org/current/install-guide/index.html)
2. [Instalación de gmxapi](https://manual.gromacs.org/current/gmxapi/userguide/install.html)
3. [Compatibilidad entre CUDA Toolkit y controladores NVIDIA](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)
4. [Guía de instalación de CUDA para Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
5. [Descarga y suma de comprobación de GROMACS 2026.3](https://manual.gromacs.org/documentation/2026.3/download.html)
6. [Instalación de NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
7. [Prueba de acceso a GPU desde un contenedor](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html)
8. [Buenas prácticas para construir imágenes Docker](https://docs.docker.com/build/building/best-practices/)
