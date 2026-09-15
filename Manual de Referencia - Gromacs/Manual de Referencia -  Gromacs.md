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

## Compilación reproducible dentro de Docker

Un contenedor permite fijar la distribución Linux, compiladores, bibliotecas, versión de CUDA de usuario y opciones de CMake. Esto mejora la reproducibilidad del entorno y evita contaminar el sistema anfitrión. No vuelve al ejecutable universal ni garantiza resultados idénticos bit a bit: el kernel, el controlador NVIDIA, la arquitectura CPU, la GPU y la asignación de hilos siguen perteneciendo al anfitrión.

La imagen debe construirse para una versión exacta de GROMACS. No conviene descargar “la última versión” durante cada compilación. Los ejemplos siguientes fijan **GROMACS 2026.3**, verifican el MD5 publicado para el archivo fuente y utilizan una construcción multietapa para que la imagen final no contenga compiladores ni archivos temporales.

### Requisitos del anfitrión

Para CPU sólo se necesitan Docker Engine o Docker Desktop y espacio suficiente para compilar:

~~~bash
docker version
docker info
~~~

En Linux con una GPU NVIDIA se necesitan además:

1. un controlador NVIDIA instalado en el anfitrión;
2. NVIDIA Container Toolkit;
3. el runtime de Docker configurado para exponer la GPU.

El controlador se instala únicamente en el anfitrión. La imagen contiene el toolkit y las bibliotecas CUDA de usuario, pero no reemplaza al controlador.

Después de instalar NVIDIA Container Toolkit:

~~~bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
~~~

Compruebe el acceso antes de compilar GROMACS:

~~~bash
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
~~~

Si este comando falla, el problema está en Docker, el runtime NVIDIA o el controlador del anfitrión; recompilar GROMACS no lo corrige.

### Imagen CPU portable para x86-64

Cree un archivo llamado **Dockerfile.cpu**:

~~~dockerfile
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
~~~

Construya la imagen:

~~~bash
docker build --pull --no-cache \
  -f Dockerfile.cpu \
  -t gromacs:2026.3-cpu .
~~~

El valor **SSE2** se eligió como mínimo común denominador razonable para x86-64. Aumenta la posibilidad de ejecutar la misma imagen en procesadores x86-64 distintos, pero reduce el rendimiento respecto de AVX2 o AVX-512. Para una imagen destinada a un único nodo o a máquinas homogéneas puede compilarse otra variante:

~~~bash
docker build --pull \
  --build-arg GMX_SIMD=AVX2_256 \
  -f Dockerfile.cpu \
  -t gromacs:2026.3-cpu-avx2 .
~~~

Esa imagen fallará o no será apropiada en CPU sin AVX2. Una imagen construida para **linux/amd64** tampoco se vuelve compatible automáticamente con ARM64. En ARM debe realizarse una compilación nativa con el SIMD correspondiente; la emulación mediante QEMU sirve para construir o probar, pero no para medir rendimiento de dinámica molecular.

### Imagen con CUDA para GPU NVIDIA

GROMACS 2026.3 requiere CUDA 12.1 o posterior y una GPU con capacidad de cómputo 5.0 o superior. El ejemplo utiliza CUDA 12.6 sobre Ubuntu 24.04, una combinación incluida entre las plataformas de prueba declaradas para esta versión.

Cree **Dockerfile.cuda**:

~~~dockerfile
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
~~~

Construya y verifique:

~~~bash
docker build --pull --no-cache \
  -f Dockerfile.cuda \
  -t gromacs:2026.3-cuda12.6 .

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 --version

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 mdrun -version
~~~

La lista de **CMAKE_CUDA_ARCHITECTURES** genera código para varias generaciones y aumenta el tiempo de compilación y el tamaño de la imagen. Puede reducirse para un parque homogéneo. Por ejemplo, una RTX 3060 utiliza SM 86 y una Tesla P100 utiliza SM 60:

~~~bash
docker build --pull \
  --build-arg CUDA_ARCHITECTURES="60;86" \
  -f Dockerfile.cuda \
  -t gromacs:2026.3-cuda12.6-sm60-sm86 .
~~~

No agregue una arquitectura que el toolkit seleccionado ya no admita. Si se busca máxima portabilidad entre GPU NVIDIA, es preferible conservar la lista predeterminada de arquitecturas generada por GROMACS o definir explícitamente todas las GPU reales que deberán ejecutar la imagen.

### Compatibilidad entre la imagen CUDA y el controlador

La versión mostrada por **nvidia-smi** como “CUDA Version” es la versión máxima admitida por el controlador, no el toolkit contenido en la imagen. Para ejecutar una imagen basada en CUDA 12.x, el controlador Linux debe cumplir como mínimo el requisito de esa familia; la tabla general de compatibilidad menor de NVIDIA indica controlador 525 o posterior para CUDA 12.x. Algunas características que combinan PTX, bibliotecas nuevas o hardware reciente pueden exigir un controlador más nuevo.

Verifique ambos lados:

~~~bash
nvidia-smi

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 mdrun -version
~~~

La primera orden caracteriza el anfitrión. La segunda confirma cómo fue compilado GROMACS y si el contenedor ve la GPU.

### Ejecutar una simulación conservando los archivos

Los datos no deben quedar únicamente dentro de la capa efímera del contenedor. Monte el directorio actual en **/work** y use el UID y GID del usuario para evitar archivos propiedad de root:

~~~bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cpu \
  grompp -f md.mdp -c npt.gro -t npt.cpt \
  -p topol.top -o md.tpr
~~~

Para producción con NVIDIA:

~~~bash
docker run --rm -it \
  --gpus all \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cuda12.6 \
  mdrun -deffnm md -ntmpi 1 -ntomp 8
~~~

Como el Dockerfile define **ENTRYPOINT ["gmx"]**, después del nombre de la imagen se escribe directamente la suborden, por ejemplo **grompp**, **mdrun** o **rms**. El directorio montado conserva TPR, trayectorias, energías, logs y checkpoints cuando se elimina el contenedor.

Si Docker tiene un límite de CPU o memoria, GROMACS sólo podrá usar los recursos asignados. Conviene declararlos de forma explícita cuando se comparan rendimientos:

~~~bash
docker run --rm \
  --gpus all \
  --cpuset-cpus 0-7 \
  --memory 24g \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cuda12.6 \
  mdrun -deffnm md -ntmpi 1 -ntomp 8
~~~

### Validación mínima de la imagen

La compilación ejecuta **ctest**, pero la imagen GPU se construye normalmente sin acceso a un dispositivo. Debe realizarse una prueba de ejecución en cada clase de hardware de destino.

Registre la configuración:

~~~bash
docker image inspect gromacs:2026.3-cuda12.6 > image-inspect.json

docker run --rm --gpus all \
  gromacs:2026.3-cuda12.6 mdrun -version
~~~

Después ejecute un sistema pequeño y examine el log:

~~~bash
docker run --rm --gpus all \
  --user "$(id -u):$(id -g)" \
  --volume "$PWD:/work" \
  --workdir /work \
  gromacs:2026.3-cuda12.6 \
  mdrun -s test.tpr -deffnm test -nsteps 1000
~~~

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

~~~dockerfile
FROM ubuntu:24.04@sha256:DIGEST_VERIFICADO AS builder
~~~

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
5. [Descarga y suma de comprobación de GROMACS 2026.3](https://manual.gromacs.org/documentation/2026.3/download.html)
6. [Instalación de NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
7. [Prueba de acceso a GPU desde un contenedor](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html)
8. [Buenas prácticas para construir imágenes Docker](https://docs.docker.com/build/building/best-practices/)

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

## Múltiples moléculas de ligandos y de proteínas

Los sistemas con varias cadenas proteicas y varios ligandos requieren distinguir tres conceptos:

1. **Copia molecular:** instancia concreta con coordenadas propias.
2. **Tipo molecular:** definición de la molécula en una sección **[ moleculetype ]**.
3. **Nombre de residuo:** etiqueta empleada en las coordenadas y en las selecciones.

Dos ligandos químicamente idénticos, con los mismos átomos, orden atómico, enlaces, cargas y parámetros, pueden ser dos copias del mismo tipo molecular. Sus posiciones y conformaciones iniciales pueden ser diferentes. En cambio, ligandos distintos o copias que deban recibir topologías diferentes necesitan tipos moleculares separados.

### Caso 1: varias copias de un ligando idéntico

La estructura PDB 1OKE contiene dos cadenas proteicas y varias moléculas no proteicas, entre ellas dos moléculas BOG. Si ambas copias de BOG tienen la misma composición y parametrización, se necesita una sola topología molecular para BOG.

Antes de parametrizar:

- extraiga una copia completa del ligando;
- revise protonación, carga formal, estereoquímica y orden de enlaces;
- confirme que ambas copias tienen los mismos átomos;
- conserve las coordenadas originales de cada copia;
- use el mismo orden atómico en las coordenadas y en la topología.

Puede asignarse **BOG** como nombre de residuo y como nombre del tipo molecular. Las dos copias se distinguen mediante su número de residuo y, si el formato lo permite, su cadena.

Ejemplo simplificado de coordenadas:

~~~text
HETATM    1  C1  BOG C   1     -14.258  79.953  45.302  1.00  0.00           C
HETATM    2  O1  BOG C   1     -13.074  79.344  45.814  1.00  0.00           O
...
TER
HETATM   49  C1  BOG D   2     -17.418  58.852   3.720  1.00  0.00           C
HETATM   50  O1  BOG D   2     -16.140  59.295   3.262  1.00  0.00           O
...
~~~

Los números de átomo deben ser únicos dentro del PDB. Los números de residuo o identificadores de cadena diferentes facilitan el análisis, aunque GROMACS asigna la topología principalmente según el orden de las moléculas.

Topología molecular:

~~~ini
[ moleculetype ]
; nombre   nrexcl
BOG        3

[ atoms ]
; nr  tipo  resnr  residuo  átomo  cgnr  carga  masa
1     ...   1      BOG      C1     1     ...    12.011
2     ...   1      BOG      O1     2     ...    15.999
; ...
~~~

En **topol.top** se incluye una sola vez:

~~~ini
; Parámetros generales
#include "charmm36-jul2022.ff/forcefield.itp"

; Parámetros adicionales del ligando, si corresponden
#include "bog_atomtypes.itp"

; Definición del tipo molecular BOG
#include "bog.itp"

; Cadenas proteicas generadas por pdb2gmx
#include "topol_Protein_chain_A.itp"
#include "topol_Protein_chain_B.itp"
~~~

Al final del archivo:

~~~ini
[ system ]
Proteína 1OKE con dos moléculas BOG

[ molecules ]
; tipo molecular       cantidad
Protein_chain_A         1
Protein_chain_B         1
BOG                     2
~~~

La sección **[ molecules ]** indica que existen dos instancias de BOG. No deben incluirse dos copias idénticas de **bog.itp** porque se redefinirían los mismos tipos o el mismo **[ moleculetype ]**.

El orden de las coordenadas debe ser:

~~~text
Protein_chain_A
Protein_chain_B
BOG, copia 1
BOG, copia 2
~~~

Este orden debe coincidir exactamente con **[ molecules ]**.

### Cuándo son necesarias topologías separadas

Use tipos moleculares diferentes, por ejemplo **LIGA** y **LIGB**, cuando:

- los ligandos son químicamente distintos;
- tienen diferente protonación o carga;
- una copia contiene átomos o enlaces diferentes;
- se parametrizaron con términos diferentes;
- se aplicarán restricciones posicionales distintas;
- se realizarán transformaciones alquí­micas o cálculos de energía libre diferentes por copia.

En ese caso:

~~~ini
#include "ligand_A.itp"
#include "ligand_B.itp"

[ molecules ]
Protein_chain_A    1
Protein_chain_B    1
LIGA               1
LIGB               1
~~~

Duplicar una topología solo para cambiar el nombre del residuo suele ser innecesario. Si se crean **LIGA** y **LIGB**, ambos archivos deben tener nombres de **[ moleculetype ]** diferentes y todos sus índices deben seguir siendo locales a cada molécula.

### Sistemas con muchas cadenas: ejemplo 6BKK

La estructura 6BKK corresponde al dominio transmembrana M2 de influenza A unido a amantadina. El sistema biológico y la unidad cristalográfica deben revisarse antes de simular: no debe suponerse que todas las cadenas del PDB forman la unidad funcional.

Prepare la proteína sin eliminar ligandos o cofactores hasta haber registrado su identidad y posición. Luego genere la topología de las cadenas:

~~~bash
gmx pdb2gmx     -f protein_only.pdb     -o protein_processed.gro     -p topol.top     -i posre_protein.itp     -water tip3p
~~~

Seleccione un campo de fuerza compatible con la topología de amantadina. No use automáticamente CHARMM27 por aparecer en protocolos antiguos; registre el campo de fuerza concreto disponible en la instalación.

Si **pdb2gmx** separa las cadenas en archivos ITP, **topol.top** puede contener:

~~~ini
#include "topol_Protein_chain_A.itp"
#include "topol_Protein_chain_B.itp"
#include "topol_Protein_chain_C.itp"
#include "topol_Protein_chain_D.itp"
#include "topol_Protein_chain_E.itp"
#include "topol_Protein_chain_F.itp"
#include "topol_Protein_chain_G.itp"
#include "topol_Protein_chain_H.itp"
~~~

La cantidad y el orden deben verificarse en la salida real. No copie esta lista a otro sistema.

Si existen dos amantadinas idénticas:

~~~ini
[ molecules ]
Protein_chain_A    1
Protein_chain_B    1
Protein_chain_C    1
Protein_chain_D    1
Protein_chain_E    1
Protein_chain_F    1
Protein_chain_G    1
Protein_chain_H    1
AMA                2
~~~

Cada copia debe tener coordenadas propias, números de átomo válidos y el mismo orden interno que **ama.itp**.

### Construcción y validación de las coordenadas

Después de combinar proteína y ligandos:

~~~bash
gmx editconf     -f protein_ligands.pdb     -o complex.gro
~~~

Revise el archivo:

~~~bash
gmx check -f complex.gro
~~~

Genere un TPR de validación antes de solvatar. Puede usarse un MDP mínimo:

~~~ini
integrator      = steep
nsteps          = 0
cutoff-scheme   = Verlet
coulombtype     = PME
rcoulomb        = 1.0
rvdw            = 1.0
pbc             = xyz
~~~

~~~bash
gmx grompp     -f validate.mdp     -c complex.gro     -p topol.top     -o validate.tpr     -pp processed.top
~~~

La opción **-pp processed.top** guarda la topología ya expandida por el preprocesador. Resulta útil para comprobar el orden de las inclusiones, macros y restricciones activadas.

No continúe si aparece alguno de estos problemas:

- número de coordenadas distinto del número de átomos de la topología;
- tipos atómicos desconocidos;
- parámetros enlazados ausentes;
- carga total inesperada;
- redefiniciones de **[ atomtypes ]**;
- nombres distintos entre **[ molecules ]** y **[ moleculetype ]**.

No use **-maxwarn** para forzar el TPR sin comprender cada advertencia.

### Caja, solvatación e iones

Para una proteína soluble:

~~~bash
gmx editconf     -f complex.gro     -o complex_box.gro     -c     -d 1.0     -bt dodecahedron
~~~

Para un sistema de membrana no debe construirse una caja acuosa genérica alrededor de la proteína. Primero debe definirse la membrana, su orientación, composición y espesor mediante un protocolo específico.

Solvatación:

~~~bash
gmx solvate     -cp complex_box.gro     -cs spc216.gro     -o complex_solv.gro     -p topol.top
~~~

Preprocesamiento para iones:

~~~bash
gmx grompp     -f ions.mdp     -c complex_solv.gro     -p topol.top     -o ions.tpr
~~~

Neutralización y NaCl 0.15 mol L⁻¹:

~~~bash
gmx genion     -s ions.tpr     -o complex_solv_ions.gro     -p topol.top     -pname NA     -nname CL     -neutral     -conc 0.15
~~~

Seleccione el grupo de solvente, normalmente **SOL**. El número del grupo depende del sistema.

### Restricciones de posición

#### Múltiples copias del mismo tipo molecular

Si dos ligandos son instancias del mismo **[ moleculetype ]**, un único archivo de restricciones incluido dentro de esa topología se aplica a todas las copias:

~~~bash
gmx genrestr     -f bog_only.gro     -o posre_bog.itp     -fc 1000 1000 1000
~~~

Incluya las restricciones inmediatamente después de la definición de BOG:

~~~ini
#include "bog.itp"

#ifdef POSRES_BOG
#include "posre_bog.itp"
#endif
~~~

Active la macro durante la equilibración:

~~~ini
define = -DPOSRES -DPOSRES_BOG
~~~

No genere **posre_BOG1.itp** y **posre_BOG2.itp** para incluirlos sobre un único tipo molecular. Los índices de las restricciones son locales al tipo molecular, por lo que ambas copias usarán la misma selección local.

#### Restricciones diferentes para cada copia

Si BOG1 y BOG2 deben tener restricciones diferentes, defina dos tipos moleculares:

~~~ini
#include "bog1.itp"
#ifdef POSRES_BOG1
#include "posre_bog1.itp"
#endif

#include "bog2.itp"
#ifdef POSRES_BOG2
#include "posre_bog2.itp"
#endif
~~~

~~~ini
[ molecules ]
Protein_chain_A    1
Protein_chain_B    1
BOG1               1
BOG2               1
~~~

Esta duplicación aumenta el mantenimiento y solo se justifica si las copias requieren un tratamiento realmente diferente.

#### Cadenas proteicas

Las restricciones de cada cadena deben estar dentro del ámbito del **[ moleculetype ]** correspondiente. Los ITP generados por **pdb2gmx** suelen incluir su propio archivo de restricciones mediante la macro **POSRES**. Revise cada archivo antes de añadir nuevas inclusiones.

Ejemplo dentro de **topol_Protein_chain_A.itp**:

~~~ini
[ moleculetype ]
Protein_chain_A    3

; átomos, enlaces y otros términos
; ...

#ifdef POSRES
#include "posre_Protein_chain_A.itp"
#endif
~~~

No reúna al final de **topol.top** restricciones de varias moléculas como si utilizaran índices globales.

### Grupos de índice para varias cadenas y ligandos

Cree grupos explícitos:

~~~bash
gmx make_ndx     -f complex_solv_ions.gro     -o index.ndx
~~~

Ejemplo interactivo para dos ligandos con residuo BOG:

~~~text
r BOG
name 18 BOG_all
"Protein" | 18
name 19 Protein_BOG
q
~~~

Los números 18 y 19 son ejemplos. Use los asignados en su sesión.

Las dos copias pueden seleccionarse por número de residuo, cadena o índice atómico. La sintaxis exacta depende de la información conservada en el archivo:

~~~bash
gmx select     -s complex_solv_ions.gro     -n index.ndx     -select 'resname BOG'
~~~

Para separar las copias por número de residuo:

~~~bash
gmx select     -s complex_solv_ions.gro     -select 'resname BOG and resid 1'     -on bog_1.ndx

gmx select     -s complex_solv_ions.gro     -select 'resname BOG and resid 2'     -on bog_2.ndx
~~~

Si los números de residuo no son únicos entre cadenas, seleccione además por identificador de cadena cuando esté disponible o utilice rangos de índices verificados.

### Minimización y equilibración

La minimización sigue el flujo general:

~~~bash
gmx grompp     -f em.mdp     -c complex_solv_ions.gro     -p topol.top     -n index.ndx     -o em.tpr

gmx mdrun -deffnm em -v
~~~

NVT con restricciones:

~~~bash
gmx grompp     -f nvt.mdp     -c em.gro     -r em.gro     -p topol.top     -n index.ndx     -o nvt.tpr

gmx mdrun -deffnm nvt -v
~~~

NPT continuando coordenadas y velocidades:

~~~bash
gmx grompp     -f npt.mdp     -c nvt.gro     -r nvt.gro     -t nvt.cpt     -p topol.top     -n index.ndx     -o npt.tpr

gmx mdrun -deffnm npt -v
~~~

No use el barostato Berendsen para obtener un ensamble de producción. Para equilibración, **C-rescale** permite controlar la presión y genera el ensamble correcto. Para producción suele utilizarse **Parrinello-Rahman**, según el sistema y el protocolo.

Ejemplo de acoplamiento durante NPT:

~~~ini
tcoupl           = V-rescale
tc-grps          = Protein_LIG Water_and_ions
tau-t            = 1.0 1.0
ref-t            = 300 300

pcoupl           = C-rescale
pcoupltype       = isotropic
tau-p            = 5.0
ref-p            = 1.0
compressibility  = 4.5e-5
~~~

**tau-t** y **tau-p** se expresan en ps; **ref-t**, en K; **ref-p**, en bar; la compresibilidad, en bar⁻¹.

El tiempo de simulación se calcula como:

~~~
tiempo = dt × nsteps
~~~

Con **dt = 0.002 ps** y **nsteps = 500000**, el tiempo es 1000 ps, equivalente a 1 ns. En el texto anterior, **nsteps = 20000** se interpretaba erróneamente como 60 ns: en realidad corresponde a 40 ps con un paso de 2 fs.

### Producción

Genere el TPR sin las macros de restricciones, salvo que formen parte deliberada del experimento:

~~~bash
gmx grompp     -f md.mdp     -c npt.gro     -t npt.cpt     -p topol.top     -n index.ndx     -o md.tpr

gmx mdrun -deffnm md -v
~~~

Compruebe que **md.mdp** contiene **continuation = yes** y **gen-vel = no**. La producción debe continuar las velocidades de NPT.

Para revisar métodos y parámetros contenidos en el TPR:

~~~bash
gmx dump -s md.tpr > md_tpr_dump.txt
gmx report-methods -s md.tpr -o methods.tex
~~~

**gmx report-methods** genera una descripción de métodos a partir del TPR. Debe revisarse antes de incorporarla a un manuscrito.

### Preparación de la trayectoria

Haga las moléculas completas:

~~~bash
echo System |
gmx trjconv     -s md.tpr     -f md.xtc     -o md_whole.xtc     -pbc whole
~~~

Centre el complejo completo:

~~~bash
(echo Protein_LIG; echo System) |
gmx trjconv     -s md.tpr     -f md_whole.xtc     -o md_center.xtc     -center     -pbc mol     -ur compact     -n index.ndx
~~~

Ajuste rotación y traslación respecto del backbone de todas las cadenas:

~~~bash
(echo Backbone; echo System) |
gmx trjconv     -s md.tpr     -f md_center.xtc     -o md_fit.xtc     -fit rot+trans     -n index.ndx
~~~

Para oligómeros, inspeccione que el grupo usado para centrar contiene todas las cadenas funcionales y todos los ligandos relevantes.

### RMSD de cada ligando

Si ambas copias están en un mismo grupo, **gmx rms** calcula un único RMSD sobre el conjunto completo; no produce automáticamente una curva independiente por molécula.

Cree grupos separados para BOG1 y BOG2 y calcule cada curva después de ajustar sobre la proteína:

~~~bash
(echo Backbone; echo BOG1) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_bog1.xvg     -tu ns

(echo Backbone; echo BOG2) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_bog2.xvg     -tu ns
~~~

El primer grupo selecciona los átomos usados para el ajuste; el segundo, los átomos cuyo RMSD se calcula. Para ligandos simétricos, el RMSD convencional puede mostrar saltos por permutaciones de átomos equivalentes y debe interpretarse con cuidado.

Comando extra para medir la distancia mínima de cada ligando a la proteína:

~~~bash
gmx pairdist     -s md.tpr     -f md_fit.xtc     -n index.ndx     -ref 'group "Protein"'     -sel 'group "BOG1"' 'group "BOG2"'     -type min     -o ligand_protein_mindist.xvg
~~~

### RMSD de cadenas individuales

Cree grupos para cada cadena y use el oligómero completo como grupo de ajuste si desea comparar movimientos internos bajo una referencia común:

~~~bash
(echo Backbone; echo Chain_A) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_chain_A.xvg     -tu ns

(echo Backbone; echo Chain_B) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o rmsd_chain_B.xvg     -tu ns
~~~

Si cada cadena se ajusta sobre sí misma, se elimina su movimiento relativo respecto del oligómero. Ambas estrategias responden preguntas diferentes y no deben mezclarse en una misma comparación.

### RMSD de la proteína, todas las cadenas juntas

Después de corregir PBC y ajustar la trayectoria:

~~~bash
(echo Backbone; echo Backbone) |
gmx rms     -s md.tpr     -f md_fit.xtc     -n index.ndx     -o md_rmsd_protein_all_chains.xvg     -tu ns
~~~

Este RMSD describe el cambio del backbone del conjunto de cadenas respecto de la referencia seleccionada. Puede aumentar por reorganización cuaternaria aunque cada cadena conserve su estructura interna. Por eso conviene compararlo con los RMSD por cadena y con distancias entre centros de masa:

~~~bash
gmx distance     -s md.tpr     -f md_fit.xtc     -n index.ndx     -select 'com of group "Chain_A" plus com of group "Chain_B"'     -oall chain_A_chain_B_distance.xvg
~~~

## Dinámica de una proteína en agua

### Caso: proteína monomérica

Este sistema contiene una proteína formada por aminoácidos estándar, agua e iones. Es útil para estudiar estabilidad conformacional, flexibilidad, compactación, estructura secundaria, exposición al solvente y movimientos colectivos. También sirve para relajar una estructura modelada, pero una dinámica molecular breve no corrige automáticamente errores de secuencia, plegamiento, protonación o ensamblaje.

El flujo general es:

~~~text
estructura inicial
    ↓
revisión y preparación
    ↓
topología con pdb2gmx
    ↓
caja periódica
    ↓
solvatación e iones
    ↓
minimización de energía
    ↓
equilibración NVT
    ↓
equilibración NPT
    ↓
dinámica de producción
    ↓
corrección de PBC y análisis
~~~

### 1. Definir qué estructura se simulará

Antes de ejecutar GROMACS, determine si la estructura representa realmente un monómero biológico. Una cadena aislada de un PDB puede ser:

- una proteína monomérica funcional;
- una subunidad extraída de un oligómero;
- una construcción truncada;
- una estructura con mutaciones o etiquetas;
- un modelo incompleto;
- una cadena estabilizada por contactos cristalográficos.

Simular una única cadena de una proteína oligomérica puede producir exposición artificial de superficies hidrofóbicas, pérdida de estructura o movimientos que no ocurren en la unidad biológica.

Revise como mínimo:

- residuos y segmentos faltantes;
- átomos con ocupación alternativa;
- residuos no estándar;
- terminales reales de la construcción;
- enlaces disulfuro;
- histidinas y otros grupos titulables;
- metales, cofactores, ligandos y aguas estructurales;
- mutaciones y modificaciones postraduccionales;
- orientación y entorno experimental de la proteína.

Conserve el archivo original y trabaje sobre una copia:

~~~bash
mkdir -p 00_entrada 01_preparacion 02_em 03_nvt 04_npt 05_md 06_analisis
cp protein.pdb 00_entrada/protein_original.pdb
~~~

### 2. Campo de fuerza y modelo de agua

No existe un campo de fuerza universalmente superior para todas las proteínas y propiedades. La elección debe justificarse por:

- tipo de proteína y entorno;
- propiedad que se medirá;
- calidad de la parametrización disponible;
- compatibilidad con cofactores o ligandos;
- antecedentes metodológicos comparables;
- modelo de agua utilizado durante el desarrollo o la validación del campo de fuerza.

No seleccione OPLS-AA, CHARMM, AMBER o GROMOS solo por el número que ocupa en el menú de **pdb2gmx**. Los números y campos instalados pueden cambiar entre equipos.

Liste las opciones disponibles:

~~~bash
gmx pdb2gmx -h
~~~

También puede iniciar **pdb2gmx** sin **-ff** para seleccionar el campo de fuerza interactivamente.

### 3. Limpieza de la estructura

Elimine únicamente componentes cuya ausencia esté justificada. Las aguas cristalográficas alejadas suelen descartarse, pero una molécula de agua conservada en un sitio catalítico o en una red de puentes de hidrógeno puede ser relevante.

Las conformaciones alternativas deben resolverse antes de **pdb2gmx**. No deben quedar dos posiciones incompatibles para el mismo átomo.

Verificación inicial:

~~~bash
grep '^ATOM\|^HETATM\|^TER\|^SSBOND' 00_entrada/protein_original.pdb     > 01_preparacion/structure_records.txt
~~~

Este comando solo extrae registros para inspección; no genera por sí mismo un PDB listo para simular.

### 4. Generación de la topología

Ejemplo interactivo:

~~~bash
cd 01_preparacion

gmx pdb2gmx     -f ../00_entrada/protein_original.pdb     -o protein_processed.gro     -p topol.top     -i posre_protein.itp
~~~

Ejemplo con campo de fuerza y agua indicados explícitamente:

~~~bash
gmx pdb2gmx     -f ../00_entrada/protein_original.pdb     -o protein_processed.gro     -p topol.top     -i posre_protein.itp     -ff charmm36-jul2022     -water tip3p
~~~

El identificador **charmm36-jul2022** es un ejemplo. Debe coincidir con un campo instalado y con el protocolo elegido.

Opciones útiles:

| Opción | Uso |
|---|---|
| **-ff** | Selecciona el campo de fuerza. |
| **-water** | Selecciona el modelo de agua. |
| **-ter** | Permite elegir estados de los terminales. |
| **-his** | Permite seleccionar estados de protonación de histidinas. |
| **-ss** | Permite elegir interactivamente enlaces disulfuro. |
| **-ignh** | Ignora hidrógenos de entrada y los reconstruye. Debe usarse deliberadamente. |
| **-chainsep** | Controla cuándo separar cadenas en tipos moleculares. |
| **-merge** | Controla la fusión de cadenas en un único tipo molecular. |

Consulte las opciones exactas de la instalación:

~~~bash
gmx pdb2gmx -h
~~~

**pdb2gmx** no asigna estados de protonación mediante una simulación de pH constante. Aplica plantillas y decisiones del usuario. Para histidina deben evaluarse las formas protonadas en Nδ, Nε o en ambos nitrógenos según su entorno.

Revise cuidadosamente la salida. Debe comprobar:

- residuos reconocidos;
- terminales asignados;
- carga total;
- enlaces disulfuro;
- átomos añadidos o eliminados;
- advertencias;
- nombre del tipo molecular generado.

Compruebe el archivo:

~~~bash
gmx check -f protein_processed.gro
~~~

### 5. Contenido esperado de la topología

Un **topol.top** típico incluye:

~~~ini
; Campo de fuerza
#include "charmm36-jul2022.ff/forcefield.itp"

; Topología de la proteína
#include "topol_Protein.itp"

; Agua
#include "charmm36-jul2022.ff/tip3p.itp"

; Iones
#include "charmm36-jul2022.ff/ions.itp"

[ system ]
Proteína monomérica en agua

[ molecules ]
Protein    1
~~~

La estructura exacta depende de la salida de **pdb2gmx**. No reescriba manualmente nombres sin cambiar también la definición **[ moleculetype ]** correspondiente.

El archivo de restricciones suele estar incluido dentro del ITP de la proteína:

~~~ini
#ifdef POSRES
#include "posre_protein.itp"
#endif
~~~

La inclusión debe permanecer dentro del ámbito del tipo molecular al que pertenecen sus índices.

### 6. Caja periódica

Para una proteína soluble aproximadamente globular:

~~~bash
gmx editconf     -f protein_processed.gro     -o protein_box.gro     -c     -d 1.0     -bt dodecahedron
~~~

**-d 1.0** establece una distancia mínima de 1.0 nm, equivalente a 10 Å, entre el soluto y la caja. Debe ser compatible con los radios de corte y con el tamaño y movimiento esperados de la proteína.

Una caja dodecaédrica suele contener menos agua que una cúbica. Una caja cúbica puede ser más simple de visualizar, pero normalmente aumenta el número de átomos:

~~~bash
gmx editconf     -f protein_processed.gro     -o protein_box_cubic.gro     -c     -d 1.0     -bt cubic
~~~

No use este protocolo de caja acuosa para una proteína transmembrana: necesita una bicapa, orientación y composición lipídica apropiadas.

### 7. Solvatación

~~~bash
gmx solvate     -cp protein_box.gro     -cs spc216.gro     -o protein_solv.gro     -p topol.top
~~~

**gmx solvate** actualiza la cantidad de solvente en **[ molecules ]**. Revise el final de **topol.top** y confirme que el agua utilizada es compatible con la topología elegida.

Compruebe que la proteína no cruza de forma problemática la caja y que no existen cavidades o solapamientos extraños mediante una inspección visual.

### 8. Neutralización y fuerza iónica

Archivo mínimo **ions.mdp**:

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

Genere el TPR:

~~~bash
gmx grompp     -f ions.mdp     -c protein_solv.gro     -p topol.top     -o ions.tpr
~~~

Neutralización con NaCl y concentración nominal de 0.15 mol L⁻¹:

~~~bash
gmx genion     -s ions.tpr     -o protein_solv_ions.gro     -p topol.top     -pname NA     -nname CL     -neutral     -conc 0.15
~~~

Seleccione el grupo de agua, normalmente **SOL**. No memorice su número: depende del sistema.

La opción **-neutral** incorpora los contraiones necesarios para que la carga total sea cero. **-conc 0.15** agrega sal hasta aproximar la concentración solicitada. Debido al volumen finito de la caja, la concentración efectiva puede diferir ligeramente.

Si el experimento requiere otra sal, deben existir parámetros compatibles para cada especie. Un ion metálico coordinado en un sitio activo no debe tratarse como un contraion difusible común.

### 9. Validación antes de minimizar

Genere una topología expandida:

~~~bash
gmx grompp     -f em.mdp     -c protein_solv_ions.gro     -p topol.top     -o em_test.tpr     -pp processed.top
~~~

**processed.top** permite revisar las inclusiones y macros después del preprocesamiento.

No continúe si existen:

- diferencias entre el número de átomos y coordenadas;
- carga total inesperada;
- residuos sin parametrizar;
- parámetros faltantes;
- nombres moleculares inconsistentes;
- advertencias no comprendidas.

No use **-maxwarn** para forzar la creación del TPR.

### 10. Minimización de energía

Archivo **em.mdp**:

~~~ini
title            = Minimización de proteína en agua
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

Ejecución:

~~~bash
mkdir -p ../02_em
cd ../02_em

gmx grompp     -f ../01_preparacion/em.mdp     -c ../01_preparacion/protein_solv_ions.gro     -p ../01_preparacion/topol.top     -o em.tpr

gmx mdrun -deffnm em -v
~~~

Extraiga la energía potencial:

~~~bash
(echo Potential; echo 0) |
gmx energy     -f em.edr     -o ../06_analisis/em_potential.xvg
~~~

La minimización elimina contactos desfavorables; no equilibra temperatura, presión ni distribución conformacional. Revise energía potencial, fuerza máxima, átomo asociado a esa fuerza y posibles valores NaN.

### 11. Equilibración NVT

NVT estabiliza la temperatura con volumen fijo. Use restricciones posicionales inicialmente si necesita evitar una relajación brusca del soluto mientras se reorganizan agua e iones.

Parámetros principales:

~~~ini
title         = Equilibración NVT
define        = -DPOSRES

integrator    = md
dt            = 0.002
nsteps        = 50000
continuation  = no

gen-vel       = yes
gen-temp      = 300
gen-seed      = -1

constraints   = h-bonds

tcoupl        = V-rescale
tc-grps       = Protein Water_and_ions
tau-t         = 1.0 1.0
ref-t         = 300 300

pcoupl        = no
pbc           = xyz
~~~

Con **dt = 0.002 ps** y **nsteps = 50000**, la duración es 100 ps. El paso de 0.002 ps equivale a 2 fs.

~~~bash
mkdir -p ../03_nvt
cd ../03_nvt

gmx grompp     -f ../01_preparacion/nvt.mdp     -c ../02_em/em.gro     -r ../02_em/em.gro     -p ../01_preparacion/topol.top     -o nvt.tpr

gmx mdrun -deffnm nvt -v
~~~

Analice la temperatura:

~~~bash
(echo Temperature; echo 0) |
gmx energy     -f nvt.edr     -o ../06_analisis/nvt_temperature.xvg
~~~

### 12. Equilibración NPT

NPT ajusta presión, densidad y volumen. Continúe desde el checkpoint de NVT y no regenere velocidades:

~~~ini
title            = Equilibración NPT
define           = -DPOSRES

integrator       = md
dt               = 0.002
nsteps           = 250000
continuation     = yes
gen-vel          = no

constraints      = h-bonds

tcoupl           = V-rescale
tc-grps          = Protein Water_and_ions
tau-t            = 1.0 1.0
ref-t            = 300 300

pcoupl           = C-rescale
pcoupltype       = isotropic
tau-p            = 5.0
ref-p            = 1.0
compressibility  = 4.5e-5

pbc              = xyz
~~~

Aquí se simulan 500 ps. **ref-p** se expresa en bar y la compresibilidad en bar⁻¹. El valor 4.5 × 10⁻⁵ bar⁻¹ es habitual para agua líquida cerca de condiciones ambientales.

~~~bash
mkdir -p ../04_npt
cd ../04_npt

gmx grompp     -f ../01_preparacion/npt.mdp     -c ../03_nvt/nvt.gro     -r ../03_nvt/nvt.gro     -t ../03_nvt/nvt.cpt     -p ../01_preparacion/topol.top     -o npt.tpr

gmx mdrun -deffnm npt -v
~~~

Analice temperatura, presión, densidad y volumen:

~~~bash
(echo Temperature; echo Pressure; echo Density; echo Volume; echo 0) |
gmx energy     -f npt.edr     -o ../06_analisis/npt_thermodynamics.xvg
~~~

La presión instantánea fluctúa intensamente. Evalúe promedios por bloques, densidad y deriva temporal.

### 13. Dinámica de producción

Retire **define = -DPOSRES** salvo que mantener restricciones forme parte explícita del experimento.

Parámetros principales:

~~~ini
title            = Producción de proteína en agua

integrator       = md
dt               = 0.002
nsteps           = 50000000
continuation     = yes
gen-vel          = no

constraints      = h-bonds

tcoupl           = V-rescale
tc-grps          = Protein Water_and_ions
tau-t            = 1.0 1.0
ref-t            = 300 300

pcoupl           = Parrinello-Rahman
pcoupltype       = isotropic
tau-p            = 5.0
ref-p            = 1.0
compressibility  = 4.5e-5

pbc              = xyz
~~~

Con 50000000 pasos de 0.002 ps se simulan 100 ns. Agregue los parámetros de PME, Verlet y control de salida validados en el tutorial principal; no mezcle MDP de campos de fuerza diferentes sin revisar cortes y modificadores.

~~~bash
mkdir -p ../05_md
cd ../05_md

gmx grompp     -f ../01_preparacion/md.mdp     -c ../04_npt/npt.gro     -t ../04_npt/npt.cpt     -p ../01_preparacion/topol.top     -o md.tpr

gmx mdrun -deffnm md -v
~~~

Compruebe en el registro:

- ausencia de errores LINCS;
- temperatura, presión y densidad estables;
- rendimiento y uso esperado de CPU/GPU;
- frecuencia y tamaño de los archivos de salida;
- escritura periódica del checkpoint.

### 14. Controles estructurales mínimos

Corrija PBC antes de analizar:

~~~bash
echo Protein |
gmx trjconv     -s md.tpr     -f md.xtc     -o md_protein_center.gro     -center     -pbc mol     -ur compact
~~~

Para conservar una trayectoria XTC:

~~~bash
(echo Protein; echo Protein) |
gmx trjconv     -s md.tpr     -f md.xtc     -o md_protein_center.xtc     -center     -pbc mol     -ur compact
~~~

Ajuste rotación y traslación:

~~~bash
(echo Backbone; echo Protein) |
gmx trjconv     -s md.tpr     -f md_protein_center.xtc     -o md_protein_fit.xtc     -fit rot+trans
~~~

RMSD del backbone:

~~~bash
(echo Backbone; echo Backbone) |
gmx rms     -s md.tpr     -f md_protein_fit.xtc     -o ../06_analisis/rmsd_backbone.xvg     -tu ns
~~~

RMSF por residuo:

~~~bash
echo C-alpha |
gmx rmsf     -s md.tpr     -f md_protein_fit.xtc     -o ../06_analisis/rmsf_calpha.xvg     -res
~~~

Radio de giro:

~~~bash
gmx gyrate     -s md.tpr     -f md_protein_fit.xtc     -sel 'group "Protein"'     -o ../06_analisis/gyrate_protein.xvg
~~~

Estructura secundaria:

~~~bash
gmx dssp     -s md.tpr     -f md_protein_fit.xtc     -sel 'group "Protein"'     -o ../06_analisis/secondary_structure.dat
~~~

La disponibilidad y las opciones de **gmx dssp** deben comprobarse con:

~~~bash
gmx dssp -h
~~~

Una meseta de RMSD no demuestra convergencia. Compare bloques temporales, réplicas independientes y observables complementarios.

### 15. Proteínas modeladas o inicialmente inestables

Si la estructura proviene de homología, predicción o modelado de bucles:

- revise regiones de baja confianza;
- minimice contactos locales antes de interpretar movimientos;
- use calentamiento gradual si el sistema presenta inestabilidad inicial;
- considere un paso de integración menor, por ejemplo 1 fs, durante las primeras etapas;
- reduzca las restricciones por etapas en vez de retirarlas abruptamente;
- no interprete la relajación del modelo como un cambio biológico.

Ejemplo de liberación gradual:

~~~ini
; Etapa inicial
define = -DPOSRES
~~~

Puede generar archivos de restricciones con constantes decrecientes, por ejemplo 1000, 500, 100 y 0 kJ mol⁻¹ nm⁻², manteniendo la duración y los criterios documentados. Cada etapa debe continuar desde las coordenadas y velocidades de la anterior.

### 16. Cofactores, metales y residuos no estándar

Una proteína que contiene solo residuos reconocidos por el campo de fuerza puede procesarse directamente mediante **pdb2gmx**. Un cofactor orgánico, grupo prostético o residuo modificado requiere parámetros compatibles.

No todos los cofactores deben tratarse como ligandos independientes. Existen varios casos:

- **cofactor no covalente:** puede definirse como otro **[ moleculetype ]**;
- **grupo covalente:** requiere enlaces y parámetros entre proteína y cofactor;
- **residuo modificado:** puede necesitar una entrada RTP y reglas de enlace;
- **metal estructural o catalítico:** exige un modelo específico de coordinación;
- **ion difusible:** puede usar la topología iónica del campo de fuerza.

Un metal coordinado no debe reemplazarse por un ion genérico sin evaluar geometría, estado de oxidación, coordinación y transferencia de carga.

Valide siempre que el orden de las coordenadas coincida con **[ molecules ]** y que la carga total sea la esperada.

### 17. Monómeros, oligómeros y estabilidad artificial

Cambiar el identificador de cadena o agrupar átomos en **index.ndx** no crea enlaces ni estabiliza físicamente un oligómero. Los grupos sirven para selecciones, acoplamiento, salida o análisis.

Si una estructura polimérica se desarma durante la simulación, investigue primero:

- si se simuló la unidad biológica correcta;
- si faltan cadenas, lípidos, ligandos o cofactores;
- si las interfaces dependen del pH o fuerza iónica;
- si se perdieron enlaces covalentes o disulfuro;
- si la orientación inicial es correcta;
- si existen errores de PBC o visualización;
- si la escala temporal observada es compatible con el fenómeno.

Las restricciones de posición pueden mantener una geometría, pero también impedir la dinámica que se pretende estudiar. Para conservar contactos específicos pueden emplearse restricciones de distancia, siempre que exista una justificación física o experimental. Congelar grupos completos altera más drásticamente la dinámica y debe evitarse salvo casos técnicos muy controlados.

Las restricciones aplicadas durante producción deben informarse porque modifican el ensamble y limitan la interpretación de fluctuaciones, RMSD, RMSF y transiciones conformacionales.

### 18. Criterio para continuar

Proceda a EM, NVT, NPT y producción únicamente cuando:

- la estructura inicial represente la especie biológica correcta;
- todos los componentes estén parametrizados;
- la topología y las coordenadas tengan el mismo número de átomos;
- la carga total sea razonable;
- las advertencias de **grompp** estén resueltas;
- caja, solvente e iones sean apropiados;
- se haya definido de antemano qué propiedades se analizarán.

Para una proteína monomérica formada exclusivamente por aminoácidos estándar, el flujo EM → NVT → NPT → MD suele ser suficiente. La presencia de cofactores, modificaciones, metales, membranas o interfaces oligoméricas requiere un protocolo específico; no debe resolverse mediante restricciones genéricas sin modelar antes la química faltante.

### Fuentes

1. [Preparación de sistemas en GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/system-preparation.html)
2. [Referencia de gmx pdb2gmx](https://manual.gromacs.org/current/onlinehelp/gmx-pdb2gmx.html)
3. [Campos de fuerza en GROMACS](https://manual.gromacs.org/current/user-guide/force-fields.html)
4. [Referencia de gmx solvate](https://manual.gromacs.org/current/onlinehelp/gmx-solvate.html)
5. [Opciones de archivos MDP](https://manual.gromacs.org/current/user-guide/mdp-options.html)

## Sistema bifásico

### Modelo de dos solventes: 1-octanol–agua

Un sistema bifásico permite estudiar la distribución de moléculas entre dos medios líquidos, la estructura de la interfaz, la penetración mutua de los solventes y, con un protocolo específico, propiedades como el coeficiente de partición. El sistema no debe tratarse como una caja acuosa convencional: contiene dos fases condensadas, dos interfaces por las condiciones periódicas de contorno y una composición que cambia durante la equilibración.

Este ejemplo describe la construcción de una capa de 1-octanol en contacto con agua. Los nombres de archivos, residuos y tipos atómicos son ejemplos; deben coincidir exactamente con la parametrización utilizada.

El flujo recomendado es:

~~~text
parametrización del 1-octanol
    ↓
validación de una molécula aislada
    ↓
construcción del líquido de 1-octanol
    ↓
EM y equilibración del líquido puro
    ↓
ampliación de la caja en z
    ↓
incorporación del agua
    ↓
EM → NVT → NPT o NVT de interfaz
    ↓
producción y perfiles a lo largo de z
~~~

### 1. Decidir qué sistema físico se quiere representar

Antes de construir la caja, defina:

- temperatura y presión;
- campo de fuerza y modelo de agua;
- dimensiones laterales de la interfaz;
- espesor mínimo de cada fase;
- composición inicial;
- presencia de solutos, iones o contraiones;
- duración de la equilibración;
- observable que se calculará.

El sistema inicial puede contener 1-octanol puro y agua pura, pero las fases de equilibrio no serán químicamente puras: parte del agua ingresará en la región rica en octanol y parte del octanol ingresará en la región acuosa. Para estudios de partición conviene considerar fases previamente saturadas o equilibrar el sistema durante un tiempo suficiente. Una configuración visualmente separada no demuestra que se haya alcanzado el equilibrio composicional.

Debido a la periodicidad, una lámina de octanol rodeada por agua genera normalmente dos interfaces aproximadamente paralelas al plano xy. El tamaño de la caja en z debe evitar que ambas interfaces interactúen de manera artificial.

### 2. Parametrización del 1-octanol

El 1-octanol no es un residuo proteico estándar y no debe procesarse con **gmx pdb2gmx** como si fuera un aminoácido. Se necesitan:

- coordenadas tridimensionales;
- topología molecular;
- tipos atómicos;
- cargas parciales;
- parámetros enlazados;
- parámetros de Lennard-Jones compatibles con el campo de fuerza;
- reglas de combinación coherentes con el resto del sistema.

SMILES del 1-octanol:

~~~text
CCCCCCCCO
~~~

La fórmula **CCCCCCCCOH** puede ser interpretada por algunos programas, pero el SMILES convencional es **CCCCCCCCO**; el hidrógeno del grupo hidroxilo se agrega según la valencia.

SwissParam genera parámetros compatibles con la familia CHARMM y puede ser útil para una prueba inicial. No convierte automáticamente esos parámetros en una parametrización validada para propiedades de partición o de interfaz. Para un trabajo cuantitativo deben comprobarse, al menos:

- carga total igual a cero;
- geometría y conformaciones;
- densidad del líquido;
- entalpía de vaporización, si corresponde;
- solubilidad mutua con agua;
- distribución de cargas;
- compatibilidad exacta con la versión del campo de fuerza.

No mezcle una topología generada para CHARMM con un campo AMBER, GROMOS u OPLS. Tampoco copie bloques **[ atomtypes ]** sin comprobar si los nombres ya existen: dos tipos con el mismo nombre y parámetros diferentes invalidan la topología.

Una organización sencilla es:

~~~text
00_parametros/
    octanol.gro
    octanol.itp
    octanol_atomtypes.itp
01_octanol_liquido/
02_interfaz/
03_em/
04_nvt/
05_npt/
06_md/
07_analisis/
topol.top
~~~

### 3. Revisar la topología molecular

El archivo **octanol.itp** debe contener un único **[ moleculetype ]** y las secciones moleculares correspondientes:

~~~ini
[ moleculetype ]
; nombre    nrexcl
OCT         3

[ atoms ]
; nr  tipo  resnr  residuo  átomo  cgnr  carga  masa
; ...

[ bonds ]
; ...

[ pairs ]
; ...

[ angles ]
; ...

[ dihedrals ]
; ...
~~~

Si el generador entrega tipos atómicos nuevos, colóquelos en un archivo separado que se incluya inmediatamente después del campo de fuerza y antes de **octanol.itp**:

~~~ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/octanol_atomtypes.itp"
#include "00_parametros/octanol.itp"
~~~

No coloque **[ atomtypes ]** después de haber comenzado una definición **[ moleculetype ]**. El preprocesador de topologías exige un orden específico de directivas.

Compruebe que la coordenada de una molécula aislada tenga exactamente los mismos átomos, nombres y orden que la sección **[ atoms ]**:

~~~bash
gmx check -f 00_parametros/octanol.gro
~~~

Para inspeccionar la topología expandida:

~~~bash
gmx grompp \
    -f em_single.mdp \
    -c 00_parametros/octanol.gro \
    -p topol_single.top \
    -o octanol_single.tpr \
    -pp octanol_single_processed.top
~~~

No use **-maxwarn** para ocultar incompatibilidades.

### 4. Calcular el número inicial de moléculas

El número de moléculas no debe elegirse de manera arbitraria. A partir de una densidad objetivo:

\[
N = \frac{\rho V N_\mathrm{A}}{M}
\]

donde:

- \(N\) es el número de moléculas;
- \(\rho\) es la densidad;
- \(V\) es el volumen;
- \(N_\mathrm{A}\) es la constante de Avogadro;
- \(M\) es la masa molar.

Para usar \(\rho\) en g·cm⁻³, \(V\) en nm³ y \(M\) en g·mol⁻¹:

\[
N = \frac{\rho\,V\,10^{-21}\,N_\mathrm{A}}{M}
\]

porque:

\[
1\ \mathrm{nm^3}=10^{-21}\ \mathrm{cm^3}
\]

Para 1-octanol, \(M = 130.23\ \mathrm{g\,mol^{-1}}\). Usando como ejemplo \(\rho \approx 0.827\ \mathrm{g\,cm^{-3}}\) y una caja de 5 × 5 × 5 nm:

\[
V=125\ \mathrm{nm^3}
\]

\[
N \approx 478\ \text{moléculas}
\]

Por lo tanto, 500 moléculas son razonables como punto de partida para una caja cercana a 5 nm por lado. En cambio, 500 moléculas en 10 × 10 × 10 nm corresponden aproximadamente a:

\[
\rho \approx 0.108\ \mathrm{g\,cm^{-3}}
\]

Ese sistema está muy subdensificado y contiene grandes huecos. La presión NPT inicial puede ser extrema y la caja tendría que contraerse de manera drástica.

La densidad experimental utilizada debe corresponder a la temperatura del protocolo. El valor inicial solo aproxima el volumen; la caja debe equilibrarse con el modelo molecular elegido.

### 5. Construir el líquido de 1-octanol

Centre una molécula y asegúrese de que las coordenadas estén expresadas en nanómetros:

~~~bash
gmx editconf \
    -f 00_parametros/octanol.gro \
    -o 00_parametros/octanol_centered.gro \
    -center 0 0 0
~~~

Inserte las moléculas en una caja inicial de 5 × 5 × 5 nm:

~~~bash
mkdir -p 01_octanol_liquido

gmx insert-molecules \
    -ci 00_parametros/octanol_centered.gro \
    -nmol 500 \
    -box 5 5 5 \
    -try 500 \
    -seed 2026 \
    -o 01_octanol_liquido/octanol_box.gro
~~~

**gmx insert-molecules** evita solapamientos mediante radios atómicos, pero no garantiza que el número solicitado pueda insertarse. Revise la línea final y use el número realmente añadido en **[ molecules ]**.

Si no logra insertar todas las moléculas:

- aumente moderadamente la caja;
- incremente **-try**;
- revise radios y nombres atómicos;
- inserte una cantidad menor y comprima durante una equilibración controlada;
- no reduzca agresivamente **-scale** sin inspeccionar los contactos creados.

No use una semilla aleatoria indefinida si desea reproducibilidad.

Topología inicial:

~~~ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/octanol_atomtypes.itp"
#include "00_parametros/octanol.itp"

[ system ]
1-octanol líquido

[ molecules ]
; molécula    cantidad
OCT           500
~~~

El nombre **OCT** debe ser idéntico al definido en **[ moleculetype ]**.

### 6. Minimizar el líquido de 1-octanol

Archivo **em_octanol.mdp**:

~~~ini
title           = Minimización del líquido de 1-octanol
integrator      = steep
nsteps          = 50000
emtol           = 1000.0
emstep          = 0.01

cutoff-scheme   = Verlet
nstlist         = 20
rlist           = 1.2
coulombtype     = PME
rcoulomb        = 1.2
vdwtype         = Cut-off
rvdw            = 1.2
pbc             = xyz
~~~

Los cortes son ejemplos. Deben reemplazarse por los valores recomendados para el campo de fuerza seleccionado.

~~~bash
mkdir -p 03_em

gmx grompp \
    -f em_octanol.mdp \
    -c 01_octanol_liquido/octanol_box.gro \
    -p topol.top \
    -o 03_em/octanol_em.tpr \
    -pp 03_em/octanol_processed.top

gmx mdrun \
    -deffnm 03_em/octanol_em \
    -v
~~~

Revise energía potencial, fuerza máxima, contactos anómalos y valores NaN. La convergencia numérica de la minimización no demuestra que la densidad o la estructura del líquido sean correctas.

### 7. Equilibrar primero la fase de 1-octanol

Una trayectoria de 1 ps es insuficiente para equilibrar un líquido construido por inserción aleatoria. Use primero NVT para estabilizar la temperatura y luego NPT para ajustar densidad y volumen.

Ejemplo NVT:

~~~ini
title           = NVT del 1-octanol
integrator      = md
dt              = 0.002
nsteps          = 250000
continuation    = no
gen-vel         = yes
gen-temp        = 300
gen-seed        = 2026

constraints     = h-bonds
tcoupl          = V-rescale
tc-grps         = System
tau-t           = 1.0
ref-t           = 300

pcoupl          = no
pbc             = xyz
~~~

Con 250000 pasos de 0.002 ps se simulan 500 ps.

~~~bash
mkdir -p 04_nvt

gmx grompp \
    -f nvt_octanol.mdp \
    -c 03_em/octanol_em.gro \
    -p topol.top \
    -o 04_nvt/octanol_nvt.tpr

gmx mdrun \
    -deffnm 04_nvt/octanol_nvt \
    -v
~~~

Ejemplo NPT isotrópico:

~~~ini
title            = NPT del 1-octanol
integrator       = md
dt               = 0.002
nsteps           = 2500000
continuation     = yes
gen-vel          = no

constraints      = h-bonds
tcoupl           = V-rescale
tc-grps          = System
tau-t            = 1.0
ref-t            = 300

pcoupl            = C-rescale
pcoupltype        = isotropic
tau-p             = 5.0
ref-p             = 1.0
compressibility   = 8.0e-5

pbc              = xyz
~~~

Aquí se simulan 5 ns. La compresibilidad es un valor inicial ilustrativo y debe reemplazarse por un valor justificado para el líquido y las condiciones elegidas.

~~~bash
mkdir -p 05_npt

gmx grompp \
    -f npt_octanol.mdp \
    -c 04_nvt/octanol_nvt.gro \
    -t 04_nvt/octanol_nvt.cpt \
    -p topol.top \
    -o 05_npt/octanol_npt.tpr

gmx mdrun \
    -deffnm 05_npt/octanol_npt \
    -v
~~~

Controle densidad, volumen, presión y energía:

~~~bash
(echo Density; echo Volume; echo Pressure; echo Potential; echo 0) | \
gmx energy \
    -f 05_npt/octanol_npt.edr \
    -o 07_analisis/octanol_bulk_properties.xvg
~~~

La presión instantánea tiene fluctuaciones grandes. Compare promedios por bloques y compruebe que densidad y volumen hayan alcanzado una región estacionaria.

### 8. Preparar la lámina de 1-octanol

Use la última configuración equilibrada, no un PDB extraído arbitrariamente de una trayectoria. El formato GRO conserva la caja con precisión suficiente y evita pérdidas innecesarias de información.

Primero consulte las dimensiones finales:

~~~bash
gmx check -f 05_npt/octanol_npt.gro
~~~

Supóngase, solo como ejemplo, que la caja equilibrada mide aproximadamente 5 × 5 × 5 nm. Amplíe únicamente z para crear espacio para el agua:

~~~bash
mkdir -p 02_interfaz

gmx editconf \
    -f 05_npt/octanol_npt.gro \
    -o 02_interfaz/octanol_slab_box.gro \
    -box 5 5 12 \
    -center 2.5 2.5 6.0
~~~

Use los valores reales de \(L_x\) y \(L_y\) de la fase equilibrada. Cambiarlos en este paso impone una deformación lateral. La región vacía debe quedar distribuida a ambos lados de la lámina para generar dos interfaces equivalentes.

Compruebe visualmente:

- que el octanol forme una única lámina continua;
- que no quede dividido por una representación incorrecta de PBC;
- que exista espacio suficiente para el agua;
- que los grupos hidroxilo no hayan sido orientados artificialmente de forma uniforme.

### 9. Incorporar el agua

Incluya la topología de agua compatible con el campo de fuerza antes de la sección **[ system ]**:

~~~ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/octanol_atomtypes.itp"
#include "00_parametros/octanol.itp"
#include "campo_de_fuerza.ff/modelo_de_agua.itp"

[ system ]
Interfaz 1-octanol–agua

[ molecules ]
; molécula    cantidad
OCT           500
~~~

Solvate usando explícitamente una caja de agua:

~~~bash
gmx solvate \
    -cp 02_interfaz/octanol_slab_box.gro \
    -cs spc216.gro \
    -o 02_interfaz/octanol_water.gro \
    -p topol.top
~~~

**spc216.gro** aporta una configuración geométrica de agua de tres sitios; la interacción efectiva queda definida por la topología incluida. Verifique que el modelo de agua sea el recomendado para el campo de fuerza.

**gmx solvate** elimina moléculas que solapan con el octanol y actualiza el número de agua en **[ molecules ]**. La salida final debe quedar, por ejemplo:

~~~ini
[ molecules ]
; molécula    cantidad
OCT           500
SOL           4442
~~~

El valor 4442 no es universal. Depende de las dimensiones finales, la densidad de la lámina y los criterios geométricos de solvatación. Use el número informado por su propia ejecución.

Revise el orden: las coordenadas contienen primero OCT y después SOL, por lo que **[ molecules ]** debe seguir el mismo orden.

Compruebe el sistema:

~~~bash
gmx check -f 02_interfaz/octanol_water.gro
~~~

### 10. Minimización y equilibración de la interfaz

La interfaz recién construida contiene contactos y una distribución no equilibrada de ambos líquidos. Ejecute nuevamente EM, NVT y una equilibración apropiada de volumen o área.

~~~bash
gmx grompp \
    -f em_interface.mdp \
    -c 02_interfaz/octanol_water.gro \
    -p topol.top \
    -o 03_em/interface_em.tpr \
    -pp 03_em/interface_processed.top

gmx mdrun \
    -deffnm 03_em/interface_em \
    -v
~~~

NVT:

~~~bash
gmx grompp \
    -f nvt_interface.mdp \
    -c 03_em/interface_em.gro \
    -p topol.top \
    -o 04_nvt/interface_nvt.tpr

gmx mdrun \
    -deffnm 04_nvt/interface_nvt \
    -v
~~~

Para una interfaz plana existen dos estrategias principales:

| Estrategia | Ventaja | Limitación |
|---|---|---|
| NPT semiisotrópico | Permite ajustar por separado el plano xy y el eje z. | Las fluctuaciones del área pueden modificar la interfaz. |
| NVT con caja previamente equilibrada | Mantiene fija el área interfacial. | Requiere haber determinado antes dimensiones y densidades adecuadas. |

Ejemplo NPT semiisotrópico:

~~~ini
pcoupl            = C-rescale
pcoupltype        = semiisotropic
tau-p             = 5.0
ref-p             = 1.0 1.0
compressibility   = 4.5e-5 4.5e-5
~~~

Los dos valores corresponden al plano xy y al eje z. No copie automáticamente la compresibilidad del agua para todo el sistema: debe justificarse según el protocolo y comprobarse que la caja no derive o colapse.

El acoplamiento por tensión superficial también existe, pero no debe utilizarse solo porque el sistema tenga una interfaz. Requiere una tensión objetivo y una interpretación consistente del ensamble.

Para producción, continúe desde el checkpoint:

~~~bash
gmx grompp \
    -f md_interface.mdp \
    -c 05_npt/interface_npt.gro \
    -t 05_npt/interface_npt.cpt \
    -p topol.top \
    -o 06_md/interface_md.tpr

gmx mdrun \
    -deffnm 06_md/interface_md \
    -v
~~~

### 11. Controles mínimos de la trayectoria

Corrija únicamente la representación periódica necesaria para visualizar. No centre el sistema de una manera que desplace la interfaz entre fotogramas sin documentarlo.

Extraiga una configuración:

~~~bash
echo System | \
gmx trjconv \
    -s 06_md/interface_md.tpr \
    -f 06_md/interface_md.xtc \
    -o 07_analisis/interface_last.gro \
    -dump 100000
~~~

El tiempo de **-dump** se expresa en ps. En este ejemplo, 100000 ps equivalen a 100 ns.

Perfil de densidad de masa a lo largo de z:

~~~bash
gmx density \
    -s 06_md/interface_md.tpr \
    -f 06_md/interface_md.xtc \
    -n index.ndx \
    -d Z \
    -sl 200 \
    -dens mass \
    -o 07_analisis/density_z.xvg
~~~

Cree grupos separados para OCT y SOL y analice ambos perfiles. Un sistema bifásico equilibrado debe mostrar:

- una región rica en agua;
- una región rica en octanol;
- dos zonas interfaciales;
- densidades aproximadamente constantes en el centro de cada fase, si el espesor es suficiente;
- ausencia de deriva sistemática del espesor o de la posición de la lámina.

La anchura de la interfaz depende del binning. Repita el cálculo con distintos valores de **-sl** para verificar que la conclusión no sea un artefacto de discretización.

### 12. Propiedades y análisis adicionales

#### Penetración mutua de los solventes

Los perfiles de densidad de OCT y SOL permiten estimar la presencia de agua en la fase rica en octanol y de octanol en la fase acuosa. Descarte la etapa transitoria y compare bloques temporales independientes.

#### Orientación del 1-octanol

Puede analizarse el ángulo entre el vector C1–O del 1-octanol y el eje z:

~~~bash
gmx gangle \
    -s 06_md/interface_md.tpr \
    -f 06_md/interface_md.xtc \
    -n index.ndx \
    -g1 vector \
    -group1 'vector connecting atomnr START END' \
    -g2 z \
    -oav 07_analisis/octanol_orientation.xvg
~~~

La selección debe adaptarse a los índices reales. Para obtener una distribución molecular completa puede ser necesario definir pares equivalentes para todas las moléculas.

#### Tensión interfacial

Para una lámina con dos interfaces planas normales a z:

\[
\gamma =
\frac{L_z}{2}
\left[
P_{zz}-
\frac{P_{xx}+P_{yy}}{2}
\right]
\]

El factor 1/2 aparece porque la caja periódica contiene dos interfaces. \(P_{xx}\), \(P_{yy}\) y \(P_{zz}\) son los componentes diagonales del tensor de presión.

Extraiga los componentes con **gmx energy**:

~~~bash
(echo Pres-XX; echo Pres-YY; echo Pres-ZZ; echo Box-Z; echo 0) | \
gmx energy \
    -f 06_md/interface_md.edr \
    -o 07_analisis/pressure_tensor.xvg
~~~

La tensión interfacial converge lentamente porque el tensor de presión es ruidoso. Deben usarse trayectorias suficientemente largas, promedios por bloques y unidades consistentes. En GROMACS, presión se informa en bar y longitud en nm; el resultado no queda automáticamente en mN·m⁻¹ sin conversión.

La equivalencia útil es:

\[
1\ \mathrm{bar\,nm}=0.1\ \mathrm{mN\,m^{-1}}
\]

#### Coeficiente de partición

Contar espontáneamente un soluto en cada fase puede servir si ocurren muchas transiciones reversibles. Para moléculas con barreras altas, una única trayectoria suele quedar atrapada en una fase y no permite estimar un coeficiente de partición confiable. En esos casos se requieren métodos de energía libre y réplicas, no solo una caja bifásica más larga.

### 13. Errores frecuentes

- Usar 500 moléculas en una caja de 10 nm por lado sin calcular la densidad.
- Parametrizar octanol con un campo de fuerza y combinarlo con otro.
- Duplicar tipos atómicos con nombres iguales.
- Confundir el solvente de coordenadas **spc216.gro** con el modelo definido en la topología.
- Conservar el número de moléculas solicitado cuando **insert-molecules** insertó menos.
- Escribir **[ molecules ]** en un orden distinto al archivo de coordenadas.
- Extraer un PDB intermedio y perder precisión de caja o velocidades sin necesidad.
- Equilibrar solo 1 ps.
- Interpretar separación visual como equilibrio termodinámico.
- Calcular promedios incluyendo la construcción y relajación inicial.
- Aplicar un barostato isotrópico a una interfaz sin evaluar la deformación del área.
- Interpretar ausencia de cruces del soluto como evidencia de partición estable.

### 14. Criterios para iniciar la producción

Continúe únicamente cuando:

- la carga y los tipos atómicos sean correctos;
- la topología expandida no contenga conflictos;
- el número y orden de moléculas coincidan con las coordenadas;
- no existan huecos ni solapamientos graves;
- el octanol puro reproduzca razonablemente la densidad objetivo;
- temperatura, energía y dimensiones de caja sean estacionarias;
- se hayan formado dos regiones de densidad definidas;
- la fase rica en cada solvente tenga espesor suficiente;
- las advertencias de **gmx grompp** estén comprendidas y resueltas;
- el protocolo de producción y los análisis se hayan definido de antemano.

### Fuentes

1. [Preparación de sistemas en GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/system-preparation.html)
2. [Referencia de gmx insert-molecules](https://manual.gromacs.org/current/onlinehelp/gmx-insert-molecules.html)
3. [Referencia de gmx solvate](https://manual.gromacs.org/current/onlinehelp/gmx-solvate.html)
4. [Referencia de gmx editconf](https://manual.gromacs.org/current/onlinehelp/gmx-editconf.html)
5. [Referencia de gmx trjconv](https://manual.gromacs.org/current/onlinehelp/gmx-trjconv.html)
6. [Unidades de GROMACS](https://manual.gromacs.org/current/reference-manual/definitions.html)
7. [Opciones de archivos MDP](https://manual.gromacs.org/current/user-guide/mdp-options.html)



## Proteína de membrana: construcción de una bicapa e inserción de una acuaporina

### Introducción

Las proteínas de membrana no deben simularse como proteínas solubles rodeadas únicamente por agua. La bicapa aporta un entorno anisotrópico, ejerce presión lateral, establece interfaces polares y apolares, modula la conformación de la proteína y puede ocupar sitios de unión específicos. La composición lipídica, la orientación, el ensamblado oligomérico y el protocolo de equilibración forman parte del modelo físico.

CHARMM-GUI Membrane Builder automatiza gran parte de esta preparación: lectura y reparación de la estructura, orientación, construcción de bicapas homogéneas o heterogéneas, agua en cavidades, solvatación, incorporación de iones y generación de archivos para GROMACS. La automatización reduce errores mecánicos, pero no decide qué unidad biológica, estado de protonación, composición de membrana o ensamble experimental son correctos.

Este tutorial usa una acuaporina como caso principal y contempla dos resoluciones:

- **all-atom:** proteína, lípidos, agua e iones representados átomo por átomo;
- **coarse-grained (CG):** varios átomos se agrupan en partículas efectivas.

Ambos modelos responden preguntas diferentes. No deben mezclarse archivos de fuerza, topologías ni pasos de integración entre CHARMM36 y Martini.

Flujo general:

~~~text
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
~~~

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

~~~bash
mkdir -p 00_entrada 01_charmmgui 02_em 03_equilibracion 04_md 05_analisis
cp aquaporin_input.pdb 00_entrada/aquaporin_original.pdb
~~~

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
- el centro hidrofóbico se sitúa aproximadamente en \(z=0\).

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

| Objetivo | Modelo posible | Limitación |
|---|---|---|
| Estabilidad general de una acuaporina | POPC puro | No reproduce asimetría ni diversidad celular. |
| Influencia del colesterol | POPC/colesterol | La proporción debe justificarse experimentalmente. |
| Membrana bacteriana interna | Mezcla PE/PG/cardiolipina | Depende de especie y condición de crecimiento. |
| Membrana externa Gram negativa | Monocapa externa con LPS y monocapa interna fosfolipídica | Requiere parámetros, iones y equilibración más exigentes. |
| Comparación entre isoformas | Misma bicapa controlada | Aumenta comparabilidad, pero reduce realismo fisiológico. |

En mezclas asimétricas, las dos monocapas pueden contener números y áreas moleculares diferentes. CHARMM-GUI permite ajustar proporciones y luego refinar el número de cada especie. No fuerce la misma cantidad de lípidos en ambas monocapas si sus composiciones o áreas efectivas son diferentes.

### 7. Tamaño del sistema

La caja debe contener suficientes lípidos alrededor de la proteína para reducir la interacción con sus imágenes periódicas. La extensión lateral no debe calcularse solo como el rango máximo de coordenadas de la proteína.

Como criterio inicial:

\[
L_x \gtrsim d_x + 2b
\]

\[
L_y \gtrsim d_y + 2b
\]

donde \(d_x\) y \(d_y\) son las dimensiones proyectadas de la proteína y \(b\) es el espesor del anillo lipídico deseado. Para una proteína que pueda inclinarse o cambiar de conformación, debe añadirse margen adicional.

La cantidad aproximada de lípidos de una monocapa homogénea puede estimarse como:

\[
N_{\mathrm{lip}} \approx
\frac{A_{xy}-A_{\mathrm{prot}}}
     {a_{\mathrm{lip}}}
\]

donde:

- \(A_{xy}=L_xL_y\);
- \(A_{\mathrm{prot}}\) es el área proyectada ocupada por la proteína;
- \(a_{\mathrm{lip}}\) es el área por lípido esperada en esas condiciones.

La ecuación es orientativa. En una mezcla lipídica, alrededor de una proteína irregular o en una membrana asimétrica no existe una única área por lípido que resuelva el empaquetamiento.

La altura de agua debe evitar contactos periódicos entre dominios extramembrana. CHARMM-GUI expresa normalmente estas dimensiones en Å:

\[
10\ \text{Å}=1\ \text{nm}
\]

GROMACS utiliza nanómetros en coordenadas y parámetros espaciales.

### 8. Temperatura y estado de fase

La temperatura no debe elegirse solo por el valor predeterminado del servidor. Debe ser compatible con:

- la condición experimental;
- el estado de fase esperado de los lípidos;
- la parametrización;
- la estabilidad de la proteína;
- la pregunta biológica.

Conversión:

\[
T(\mathrm{K})=T(^{\circ}\mathrm{C})+273.15
\]

| °C | K |
|---:|---:|
| 20 | 293.15 |
| 25 | 298.15 |
| 30 | 303.15 |
| 37 | 310.15 |

Una bicapa destinada a representar una fase fluida debe simularse por encima de la transición pertinente de la mezcla. En mezclas complejas, la transición no puede inferirse únicamente a partir de un lípido aislado.

### 9. Iones y concentración

CHARMM-GUI puede neutralizar el sistema y agregar NaCl, KCl u otras sales. Distinga:

- **neutralización:** cantidad mínima de contraiones para carga neta cero;
- **concentración salina nominal:** pares iónicos adicionales según el volumen accesible;
- **fuerza iónica:** depende de carga y concentración de todas las especies.

\[
I=\frac{1}{2}\sum_i c_i z_i^2
\]

donde \(c_i\) es la concentración molar y \(z_i\) la carga del ion.

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

~~~bash
mkdir -p 01_charmmgui
tar -xzf charmm-gui.tgz -C 01_charmmgui
cd 01_charmmgui
~~~

Localice la carpeta de GROMACS:

~~~bash
find . -maxdepth 3 -type f \
    \( -name 'topol.top' -o -name 'index.ndx' -o -name '*.mdp' -o -name 'README*' \) \
    -print
~~~

Los nombres pueden variar entre trabajos. Una salida típica contiene:

~~~text
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
~~~

No regenere la topología con **pdb2gmx**. CHARMM-GUI ya produjo una topología consistente con la proteína, los lípidos, el agua y los iones. Ejecutar **pdb2gmx** sobre el sistema ensamblado elimina esa coherencia.

Antes de correr:

~~~bash
gmx --version
head -n 80 topol.top
grep -R "^define\|^integrator\|^dt\|^nsteps\|^tcoupl\|^pcoupl\|^pcoupltype" ./*.mdp
~~~

Compruebe:

- campo de fuerza esperado;
- nombres y cantidades en **[ molecules ]**;
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

~~~bash
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
~~~

La opción **-r** proporciona las coordenadas de referencia para las restricciones posicionales. Si el MDP o la topología usan esas restricciones y **-r** se omite, **grompp** puede fallar o aplicar una referencia incorrecta.

Revise:

~~~bash
gmx check -f step6.0_minimization.gro

(echo Potential; echo 0) | \
gmx energy \
    -f step6.0_minimization.edr \
    -o ../05_analisis/em_potential.xvg
~~~

### 14. Equilibración escalonada sin CSH

CHARMM-GUI suele generar varias etapas que reducen gradualmente restricciones sobre proteína, lípidos, agua y componentes internos. No combine las seis etapas en una sola sin comparar sus MDP.

Script Bash, versión 4 o superior:

~~~bash
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
~~~

Guárdelo como **run_equilibration.sh** y ejecute:

~~~bash
chmod +x run_equilibration.sh
./run_equilibration.sh
~~~

El script usa arreglos de Bash para preservar correctamente cada argumento. No es compatible con un intérprete POSIX mínimo como **dash**; debe ejecutarse con Bash.

Si el archivo inicial se llama **step5_charmm2gmx.pdb**, cambie **REFERENCE**. Si CHARMM-GUI genera más o menos etapas, modifique la lista.

Para revisar sin ejecutar:

~~~bash
bash -n run_equilibration.sh
~~~

### 15. Qué cambia entre las etapas de equilibración

Inspeccione las diferencias:

~~~bash
diff -u step6.1_equilibration.mdp step6.2_equilibration.mdp
diff -u step6.5_equilibration.mdp step6.6_equilibration.mdp
~~~

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

~~~ini
pcoupltype       = semiisotropic
ref-p            = 1.0 1.0
compressibility  = 4.5e-5 4.5e-5
~~~

El primer valor corresponde conjuntamente a x/y y el segundo a z. El acoplamiento isotrópico obliga a que todas las dimensiones respondan de la misma manera y no suele ser apropiado para una bicapa plana.

**C-rescale** es adecuado para equilibración. **Parrinello-Rahman** suele reservarse para producción una vez estabilizado el sistema. Mantenga inicialmente los valores generados por CHARMM-GUI y documente cualquier cambio.

No interprete fluctuaciones instantáneas de presión como fallo. Evalúe deriva, densidad, área, espesor y promedios por bloques.

### 17. Producción segmentada sin CSH

Dividir una producción en segmentos no cambia por sí mismo la física. Facilita checkpoints, colas HPC, copias de seguridad y reanudación. El tiempo total es:

\[
t_{\mathrm{total}} =
N_{\mathrm{segmentos}}\,
n_{\mathrm{steps}}\,
\Delta t
\]

Si cada segmento contiene 5000000 pasos con \(\Delta t=0.002\ \mathrm{ps}\):

\[
t_{\mathrm{segmento}}=10\ \mathrm{ns}
\]

Diez segmentos suman 100 ns.

Script Bash:

~~~bash
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
~~~

Guárdelo como **run_production.sh**:

~~~bash
chmod +x run_production.sh
bash -n run_production.sh
./run_production.sh
~~~

Para ejecutar solo los segmentos 4 a 7:

~~~bash
FIRST_SEGMENT=4 LAST_SEGMENT=7 ./run_production.sh
~~~

Si la producción no usa restricciones, **-r** puede ser innecesario, pero conservarlo no reemplaza la revisión del MDP y de las macros activas.

En un clúster, el script debe ejecutarse dentro del sistema de colas. No lance múltiples segmentos dependientes al mismo tiempo: cada uno necesita el checkpoint final del anterior.

### 18. Reanudar una ejecución interrumpida

Si existe un checkpoint del mismo segmento:

~~~bash
gmx mdrun \
    -deffnm step7_4 \
    -cpi step7_4.cpt \
    -append \
    -v
~~~

No vuelva a ejecutar **grompp** desde la última estructura si el objetivo es continuar exactamente el mismo segmento. El checkpoint conserva estado del integrador, velocidades y otra información necesaria para una continuación reproducible.

### 19. Preparación de la trayectoria para análisis

Conserve siempre la trayectoria original. Genere derivados para visualización y análisis.

Primero haga moléculas enteras y centre la proteína:

~~~bash
(echo Protein; echo System) | \
gmx trjconv \
    -s step7_1.tpr \
    -f md_all.xtc \
    -o 05_analisis/md_center.xtc \
    -pbc mol \
    -center \
    -ur compact
~~~

Luego ajuste la proteína si el análisis requiere eliminar traslación y rotación:

~~~bash
(echo Backbone; echo System) | \
gmx trjconv \
    -s step7_1.tpr \
    -f 05_analisis/md_center.xtc \
    -o 05_analisis/md_fit.xtc \
    -fit rot+trans
~~~

No use una trayectoria ajustada para difusión lateral de lípidos ni para fluctuaciones de caja. El ajuste cambia las coordenadas colectivas que esos análisis necesitan.

Si la producción está segmentada:

~~~bash
gmx trjcat \
    -f step7_1.xtc step7_2.xtc step7_3.xtc step7_4.xtc \
    -o md_all.xtc \
    -cat
~~~

Compruebe continuidad temporal y descarte marcos duplicados si los segmentos se solapan.

### 20. Controles estructurales de la proteína

RMSD del backbone:

~~~bash
(echo Backbone; echo Backbone) | \
gmx rms \
    -s step7_1.tpr \
    -f 05_analisis/md_fit.xtc \
    -o 05_analisis/rmsd_backbone.xvg \
    -tu ns
~~~

RMSF por residuo:

~~~bash
echo C-alpha | \
gmx rmsf \
    -s step7_1.tpr \
    -f 05_analisis/md_fit.xtc \
    -o 05_analisis/rmsf_calpha.xvg \
    -res
~~~

Para una acuaporina tetramérica, calcule además:

- RMSD de cada monómero;
- RMSD del tetrámero completo;
- distancias entre centros de masa de subunidades;
- contactos interfaciales entre monómeros;
- inclinación del eje de cada poro respecto de z;
- estabilidad de los motivos NPA;
- geometría del filtro ar/R.

Un RMSD estable del tetrámero puede ocultar que un monómero se deforma; cuatro RMSD monoméricos estables pueden ocultar una reorganización cuaternaria.

### 21. Área de la membrana

El área instantánea proyectada es:

\[
A_{xy}(t)=L_x(t)L_y(t)
\]

Extraiga las dimensiones:

~~~bash
(echo Box-X; echo Box-Y; echo Box-Z; echo Volume; echo 0) | \
gmx energy \
    -f step7_1.edr \
    -o 05_analisis/box_dimensions.xvg
~~~

Para una bicapa homogénea, simétrica y sin proteína:

\[
APL(t)=\frac{A_{xy}(t)}{N_{\mathrm{lip,leaflet}}}
\]

Con una proteína:

\[
APL_{\mathrm{aprox}}(t)=
\frac{A_{xy}(t)-A_{\mathrm{prot}}(t)}
     {N_{\mathrm{lip,leaflet}}}
\]

La corrección depende de cómo se defina el área proyectada de la proteína. En bicapas mixtas no existe una única APL rigurosa para todas las especies. Para análisis local conviene usar una partición de Voronoi u otra herramienta específica.

No divida por el número total de lípidos de las dos monocapas: el denominador es el número de una monocapa.

### 22. Compresibilidad areal

En un ensamble apropiado puede estimarse:

\[
K_A=
\frac{k_\mathrm{B}T\langle A\rangle}
     {\langle A^2\rangle-\langle A\rangle^2}
\]

donde \(A=L_xL_y\). La estimación es sensible a:

- duración de la trayectoria;
- barostato;
- correlación temporal;
- tamaño del sistema;
- presencia de proteína;
- mezcla y asimetría de lípidos.

Use promedios por bloques y no compare directamente valores obtenidos con ensambles diferentes.

### 23. Espesor y perfiles de densidad

Calcule perfiles a lo largo de z:

~~~bash
gmx density \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -d Z \
    -sl 200 \
    -dens number \
    -o 05_analisis/density_z.xvg
~~~

Cree grupos para:

- fósforos o grupos cabeza;
- colas lipídicas;
- agua;
- proteína;
- iones;
- cada especie lipídica relevante.

Una definición simple del espesor entre cabezas es la distancia entre los máximos de densidad de fósforo de ambas monocapas:

\[
d_{PP}=z_{P,\mathrm{sup}}-z_{P,\mathrm{inf}}
\]

Es una definición global. Una membrana deformada alrededor de la proteína requiere mapas locales de espesor.

### 24. Orden de las cadenas lipídicas

El parámetro de orden deuterio se expresa como:

\[
S_{CD}=
\frac{1}{2}
\left\langle 3\cos^2\theta-1 \right\rangle
\]

donde \(\theta\) es el ángulo entre un enlace de la cadena y la normal de la membrana.

Consulte primero la sintaxis disponible:

~~~bash
gmx order -h
~~~

Ejemplo general:

~~~bash
gmx order \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n lipid_chains.ndx \
    -d z \
    -od 05_analisis/order_parameter.xvg
~~~

El archivo de índice debe definir los átomos de cadena en el orden requerido. No mezcle carbonos de especies lipídicas diferentes en una misma curva sin justificarlo.

### 25. Difusión lateral de lípidos

Para difusión bidimensional:

\[
MSD_{xy}(t)=
\left\langle
[x(t)-x(0)]^2+[y(t)-y(0)]^2
\right\rangle
\]

En el régimen difusivo:

\[
MSD_{xy}(t)=4D_{xy}t
\]

Comando:

~~~bash
gmx msd \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -sel 'res_com of group "POPC"' \
    -lateral z \
    -o 05_analisis/msd_popc_xy.xvg
~~~

Compruebe la sintaxis con **gmx msd -h**, porque cambió respecto de versiones antiguas. El ajuste no debe incluir el régimen balístico inicial ni una región donde el MSD todavía sea subdifusivo. La difusión lipídica converge lentamente y depende del tamaño del sistema.

### 26. Inclinación de la proteína y del canal

Defina un vector entre centros de masa de dos grupos situados en extremos opuestos del poro y calcule su ángulo con z:

~~~bash
gmx gangle \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -g1 vector \
    -group1 'com of group "Pore_lower" plus com of group "Pore_upper"' \
    -g2 z \
    -oav 05_analisis/pore_tilt.xvg
~~~

La selección debe adaptarse a residuos conservados de la acuaporina. Para el tetrámero, genere una curva por monómero.

### 27. Radio y continuidad del poro

GROMACS no proporciona por sí solo un perfil completo de radio de poro equivalente a herramientas especializadas. Puede:

- medir distancias entre residuos del filtro;
- calcular densidad de agua a lo largo del eje;
- usar herramientas externas como HOLE o CHAP;
- comparar perfiles por monómero y por bloque temporal.

Una disminución local del radio no implica cierre funcional si el agua mantiene una cadena continua. Tampoco una cavidad geométricamente abierta demuestra permeabilidad.

### 28. Puentes de hidrógeno y orientación del agua

Puentes de hidrógeno proteína–agua:

~~~bash
gmx hbond \
    -s step7_1.tpr \
    -f 05_analisis/md_fit.xtc \
    -n index.ndx \
    -r 'group "Protein"' \
    -t 'group "Water"' \
    -num 05_analisis/protein_water_hbonds.xvg
~~~

Verifique la sintaxis exacta con:

~~~bash
gmx hbond -h
~~~

En acuaporinas importa no solo la ocupación, sino la orientación de las moléculas de agua cerca de los motivos NPA. El cambio de orientación contribuye al mecanismo de exclusión de protones. Este análisis requiere vectores dipolares o enlaces O–H y una coordenada axial referida al poro.

### 29. Conteo de eventos de permeación

Contar moléculas dentro de un cilindro en cada fotograma no equivale a contar permeaciones. Un evento debe exigir una trayectoria completa desde un reservorio hasta el opuesto.

Defina tres estados respecto del centro del canal:

~~~text
A: z < -z0
P: -z0 ≤ z ≤ z0 y dentro del radio del poro
B: z > z0
~~~

Una permeación A→B requiere la secuencia A→P→B para la misma molécula, sin reiniciar el conteo por fluctuaciones en el límite. Use coordenadas relativas al centro de cada monómero y corrija PBC.

El flujo neto bajo un gradiente puede expresarse como:

\[
J=\frac{N_{A\rightarrow B}-N_{B\rightarrow A}}{t}
\]

Una estimación directa de permeabilidad osmótica necesita además el gradiente de concentración:

\[
P_f=\frac{J}{\Delta c}
\]

Las unidades dependen de si \(J\) se expresa como moléculas por tiempo, moles por tiempo o volumen por tiempo. En equilibrio, donde no hay flujo neto sostenido, se utilizan formulaciones basadas en fluctuaciones colectivas; no debe aplicarse la ecuación anterior con \(\Delta c=0\).

### 30. Permeabilidad colectiva en equilibrio

Para una coordenada colectiva \(n(t)\) que registra el desplazamiento neto de agua a través del canal:

\[
\left\langle
[n(t)-n(0)]^2
\right\rangle
\xrightarrow[t\ \mathrm{grande}]{}
2D_n t
\]

La permeabilidad osmótica de canal único puede relacionarse con:

\[
p_f=v_wD_n
\]

donde \(v_w\) es el volumen molecular del agua y \(D_n\) es el coeficiente de difusión de la coordenada colectiva. La definición exacta de \(n(t)\), el tratamiento de PBC y el intervalo de ajuste deben mantenerse constantes al comparar sistemas.

No calcule una permeabilidad confiable a partir de unos pocos cruces. Use réplicas, intervalos de confianza y análisis por bloques.

### 31. Contactos lípido–proteína

Los contactos persistentes pueden revelar sitios anulares o específicos. Un contacto simple puede definirse por una distancia máxima:

~~~bash
gmx select \
    -s step7_1.tpr \
    -f md_all.xtc \
    -n index.ndx \
    -select 'resname POPC and within 0.45 of group "Protein"' \
    -os 05_analisis/lipid_contacts_size.xvg
~~~

Este resultado informa cuántos átomos o posiciones cumplen la selección, según la salida elegida; no es automáticamente un número de lípidos únicos. Para residencia lipídica deben seguirse identidades moleculares y tolerar interrupciones cortas.

En una mezcla, analice enriquecimiento relativo:

\[
E_i=
\frac{x_i^{\mathrm{contacto}}}
     {x_i^{\mathrm{membrana}}}
\]

donde \(E_i>1\) sugiere enriquecimiento de la especie \(i\) alrededor de la proteína. El resultado depende del corte, del área considerada y del muestreo.

### 32. Potencial electrostático y sistemas con voltaje

El potencial promedio a lo largo de z puede calcularse con **gmx potential** a partir de grupos de carga apropiados. Una sola bicapa periódica no crea automáticamente dos reservorios independientes.

Para estudiar flujo iónico bajo potencial sostenido puede utilizarse el protocolo de electrofisiología computacional de GROMACS, que emplea típicamente dos bicapas, dos compartimientos y un desequilibrio de carga:

\[
\Delta U=\frac{\Delta q}{C_{\mathrm{membrana}}}
\]

Este montaje no es necesario para permeación de agua en equilibrio y no debe añadirse sin una pregunta electrofisiológica explícita.

### 33. Réplicas, descarte y convergencia

Una trayectoria larga no reemplaza réplicas independientes. Para comparar acuaporinas, mutantes o composiciones:

- use varias semillas de velocidad;
- mantenga idénticos los parámetros comunes;
- descarte la etapa transitoria según observables;
- compare bloques temporales;
- informe incertidumbre entre réplicas;
- evite seleccionar la trayectoria “más estable”.

La estabilización del RMSD no demuestra que APL, espesor, difusión lipídica o permeación hayan convergido.

### 34. Simulación coarse-grained

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

### 35. Redes elásticas en proteínas CG

Una red elástica ayuda a conservar estructura terciaria o cuaternaria, pero puede suprimir:

- apertura del canal;
- inclinación helicoidal;
- movimientos entre dominios;
- respiración del poro;
- reorganización oligomérica.

No use una red “porque es el valor predeterminado” si la variable de interés depende del movimiento restringido. Realice análisis de sensibilidad cambiando el corte o la constante, o compare con un modelo sin red cuando sea estable.

La red elástica no reemplaza enlaces covalentes, disulfuros ni una unidad biológica correcta.

### 36. Paso de integración en CG

Los pasos CG suelen ser mayores que en all-atom, pero el máximo estable depende del modelo, el agua, las restricciones y la geometría inicial. Comience con el protocolo recomendado para la versión concreta y revise:

- energía;
- errores de restricciones;
- temperatura y presión;
- estabilidad del poro;
- comportamiento de los lípidos;
- sensibilidad al paso de integración.

La aceleración aparente del tiempo en CG no debe interpretarse como una correspondencia universal y exacta con tiempo experimental.

### 37. Visualización CG

VMD y otros visores pueden no inferir correctamente enlaces entre partículas CG porque usan reglas pensadas para geometrías atomísticas. La ausencia visual de enlaces no significa que falten en la topología.

Las representaciones deben basarse en nombres reales de partículas y residuos. Ejemplos habituales en Martini incluyen:

~~~text
name BB
resname POPC
resname W
resname NA CL
~~~

Los nombres dependen de la versión y del constructor. Compruébelos en la coordenada y en los ITP.

Para reducir memoria, genere una trayectoria de visualización:

~~~bash
gmx trjconv \
    -s cg_md.tpr \
    -f cg_md.xtc \
    -o cg_visualization.xtc \
    -n cg_visualization.ndx \
    -dt 1000
~~~

No use la trayectoria reducida para análisis que requieran resolución temporal mayor.

La representación secundaria atomística no puede reconstruirse exactamente a partir de unas pocas partículas por residuo. Una caricatura CG es una interpretación gráfica apoyada en la asignación secundaria, no una observación directa de todos los enlaces y ángulos del esqueleto.

### 38. Errores conceptuales frecuentes

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

### 39. Criterios para producción

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



## Energía libre de perturbación: energía libre de solvatación

### Caso de estudio: formaldehído en agua

La energía libre de solvatación describe el cambio de energía libre asociado con transferir una especie química desde una fase de referencia —habitualmente gas ideal— hasta una solución a dilución infinita:

\[
\Delta G_{\mathrm{solv}} =
G_{\mathrm{soluto,solución}}-
G_{\mathrm{soluto,gas}}
\]

Una \(\Delta G_{\mathrm{solv}}<0\) indica que la transferencia al solvente es favorable bajo la convención y los estados estándar especificados. La magnitud depende de la identidad química, el estado de protonación, el solvente, la temperatura, el campo de fuerza, los estados estándar, el tratamiento electrostático, el tamaño de caja y el muestreo.

Este tutorial muestra un cálculo alquímico de una molécula neutra. El formaldehído sirve para ilustrar la mecánica de GROMACS, pero presenta una limitación química crítica: en agua reacciona para formar metanodiol. El resultado obtenido con una topología no reactiva corresponde al formaldehído molecular \(\mathrm{H_2CO}\), no al equilibrio químico completo de una solución de formaldehído.

### 1. Fundamento del método

Los estados físicos A y B pueden tener distribuciones configuracionales con poca superposición. Se construye entonces un camino alquímico mediante \(\lambda\):

\[
H(\mathbf{x};\lambda)
\]

Una interpolación conceptual sencilla es:

\[
H(\lambda)=(1-\lambda)H_A+\lambda H_B
\]

Los estados intermedios no necesitan ser físicamente realizables. Solo deben conectar los extremos mediante una ruta reversible con superposición estadística suficiente.

Para un desacoplamiento en solución:

~~~text
λ = 0                         λ = 1
soluto completamente          soluto sin interacciones
acoplado al agua              no enlazadas con el agua
~~~

Las interacciones internas del soluto se mantienen. La molécula desacoplada sigue presente en las coordenadas, pero no ejerce interacciones de Coulomb ni Lennard-Jones sobre el solvente.

### 2. FEP, TI, BAR y MBAR

La ecuación de Zwanzig es:

\[
\Delta G_{A\rightarrow B}
=
-k_\mathrm{B}T
\ln
\left\langle
\exp[-\beta(U_B-U_A)]
\right\rangle_A
\]

con \(\beta=1/(k_\mathrm{B}T)\), o \(\beta=1/(RT)\) para cantidades molares. Es exacta en el límite de muestreo infinito, pero ineficiente cuando A y B tienen poca superposición.

En integración termodinámica:

\[
\Delta G_{A\rightarrow B}
=
\int_0^1
\left\langle
\frac{\partial H}{\partial\lambda}
\right\rangle_\lambda
d\lambda
\]

TI requiere una grilla que resuelva la curvatura del integrando y una integración numérica apropiada.

BAR combina información en ambas direcciones entre dos estados vecinos. MBAR analiza todos los estados conjuntamente. Ninguno corrige una ruta alquímico mal diseñada ni grados de libertad sin muestrear.

Este tutorial utiliza **gmx bar**, incluido en GROMACS.

### 3. Convención de signo

Definamos:

- estado 0: formaldehído acoplado al agua;
- estado 1: formaldehído desacoplado del agua.

La simulación calcula:

\[
\Delta G_{0\rightarrow1}
=
G_{\mathrm{desacoplado}}-
G_{\mathrm{acoplado}}
=
\Delta G_{\mathrm{desacoplamiento}}
\]

Por lo tanto:

\[
\boxed{
\Delta G_{\mathrm{solv}}
=
-\Delta G_{0\rightarrow1}
}
\]

Si se invierten **couple-lambda0** y **couple-lambda1**, también se invierte el signo. Antes de interpretar un número, escriba qué representa cada extremo.

### 4. Separar Coulomb y Lennard-Jones

Apagar simultáneamente cargas y Lennard-Jones puede servir en un ejercicio corto, pero no es la ruta preferida para un resultado cuantitativo.

Una secuencia habitual es:

1. apagar electrostática mientras el volumen excluido permanece;
2. apagar Lennard-Jones mediante potenciales soft-core.

Si desaparece primero el volumen excluido, el solvente puede ocupar la posición del soluto mientras todavía existen cargas puntuales.

\[
\Delta G_{\mathrm{desacoplamiento}}
=
\Delta G_{\mathrm{Coulomb}}
+
\Delta G_{\mathrm{LJ}}
\]

Esta separación permite identificar qué componente necesita mayor densidad de estados λ.

### 5. Potenciales soft-core

La interpolación lineal de Lennard-Jones puede producir divergencias cuando dos partículas se superponen. Los potenciales soft-core mantienen finita la energía en estados intermedios.

~~~ini
sc-alpha       = 0.5
sc-power       = 1
sc-sigma       = 0.3
sc-coul        = no
~~~

Son valores iniciales, no constantes universales. **sc-power** requiere un entero y **sc-sigma** se expresa en nm. Como Coulomb se elimina antes que Lennard-Jones, no se activa soft-core electrostático.

### 6. Selección de estados λ

Agregar estados uniformemente no garantiza precisión. Conviene aumentar su densidad donde disminuye la superposición, crece la varianza, entra solvente en una cavidad o cambia rápidamente el potencial soft-core.

Grilla inicial de 19 estados:

~~~ini
coul-lambdas = 0.00 0.25 0.50 0.75 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00

vdw-lambdas  = 0.00 0.00 0.00 0.00 0.00 0.05 0.10 0.15 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.85 0.90 0.95 1.00
~~~

Los índices 0–4 descargan el soluto y los índices 4–18 eliminan Lennard-Jones. El estado 4 es común a ambas etapas. La grilla debe reajustarse después de analizar solapamiento y errores por intervalo.

### 7. Parametrización del formaldehído

La topología debe ser compatible con el campo de fuerza y el modelo de agua. No use automáticamente parámetros antiguos de CHARMM27 ni copie tipos de SwissParam sin validación.

Compruebe:

- fórmula \(\mathrm{CH_2O}\);
- geometría trigonal plana;
- carga neta cero;
- nombres y orden de átomos;
- cargas parciales;
- parámetros enlazados;
- interacción del carbonilo;
- compatibilidad con el campo de fuerza;
- ausencia de tipos atómicos duplicados.

Organización sugerida:

~~~text
00_parametros/
    formaldehyde.gro
    formaldehyde.itp
    formaldehyde_atomtypes.itp
01_preparacion/
02_equilibracion/
03_fep/
04_analisis/
topol.top
~~~

Topología general:

~~~ini
#include "campo_de_fuerza.ff/forcefield.itp"
#include "00_parametros/formaldehyde_atomtypes.itp"
#include "00_parametros/formaldehyde.itp"
#include "campo_de_fuerza.ff/modelo_de_agua.itp"

[ system ]
Formaldehído molecular en agua

[ molecules ]
FOR    1
SOL    NUMERO_DE_AGUAS
~~~

**FOR** debe coincidir con **[ moleculetype ]**. Si existen varias moléculas FOR, **couple-moltype = FOR** perturbará todas. Para desacoplar una sola copia se necesita un tipo molecular exclusivo.

### 8. Construcción de la caja

~~~bash
gmx editconf \
    -f 00_parametros/formaldehyde.gro \
    -o 01_preparacion/formaldehyde_box.gro \
    -c \
    -d 1.2 \
    -bt dodecahedron
~~~

La distancia de 1.2 nm es inicial. Debe reducir interacciones con imágenes periódicas y ser coherente con los cortes.

~~~bash
gmx solvate \
    -cp 01_preparacion/formaldehyde_box.gro \
    -cs spc216.gro \
    -o 01_preparacion/formaldehyde_water.gro \
    -p topol.top
~~~

**spc216.gro** aporta coordenadas de agua de tres sitios. El modelo físico queda determinado por la topología incluida.

Para una sola molécula no hace falta insertarla en una caja vacía y luego redefinir otra caja: **editconf** seguido de **solvate** es suficiente.

### 9. Minimización

~~~ini
title           = EM de formaldehído en agua
integrator      = steep
nsteps          = 50000
emtol           = 1000.0
emstep          = 0.01

cutoff-scheme   = Verlet
nstlist         = 20
rlist           = 1.2
coulombtype     = PME
rcoulomb        = 1.2
vdwtype         = Cut-off
rvdw            = 1.2
pbc             = xyz
~~~

Los cortes deben adaptarse al campo de fuerza.

~~~bash
mkdir -p 02_equilibracion

gmx grompp \
    -f em.mdp \
    -c 01_preparacion/formaldehyde_water.gro \
    -p topol.top \
    -o 02_equilibracion/em.tpr \
    -pp 02_equilibracion/processed.top

gmx mdrun \
    -deffnm 02_equilibracion/em \
    -v
~~~

Terminar por alcanzar **nsteps** sin cumplir **emtol** no significa convergencia. Una fuerza máxima de miles de kJ·mol⁻¹·nm⁻¹ debe investigarse.

### 10. Equilibración física previa

NVT:

~~~ini
title         = NVT previa a FEP
integrator    = md
dt            = 0.002
nsteps        = 250000
continuation  = no
gen-vel       = yes
gen-temp      = 298.15
gen-seed      = 2026

constraints   = h-bonds
tcoupl        = V-rescale
tc-grps       = System
tau-t         = 1.0
ref-t         = 298.15
pcoupl        = no
pbc           = xyz
~~~

~~~bash
gmx grompp \
    -f nvt.mdp \
    -c 02_equilibracion/em.gro \
    -p topol.top \
    -o 02_equilibracion/nvt.tpr

gmx mdrun -deffnm 02_equilibracion/nvt -v
~~~

NPT:

~~~ini
title            = NPT previa a FEP
integrator       = md
dt               = 0.002
nsteps           = 1000000
continuation     = yes
gen-vel          = no

constraints      = h-bonds
tcoupl           = V-rescale
tc-grps          = System
tau-t            = 1.0
ref-t            = 298.15

pcoupl            = C-rescale
pcoupltype        = isotropic
tau-p             = 5.0
ref-p             = 1.0
compressibility   = 4.5e-5
pbc               = xyz
~~~

~~~bash
gmx grompp \
    -f npt.mdp \
    -c 02_equilibracion/nvt.gro \
    -t 02_equilibracion/nvt.cpt \
    -p topol.top \
    -o 02_equilibracion/npt.tpr

gmx mdrun -deffnm 02_equilibracion/npt -v
~~~

Cuarenta picosegundos no constituyen una duración universal de equilibración. Evalúe densidad, volumen, energía y relajación del solvente.

### 11. Bloque MDP para desacoplamiento

Mantenga los parámetros no enlazados del protocolo validado y añada:

~~~ini
free-energy            = yes
couple-moltype         = FOR

; λ=0 acoplado; λ=1 desacoplado
couple-lambda0         = vdw-q
couple-lambda1         = none
couple-intramol        = no

coul-lambdas = 0.00 0.25 0.50 0.75 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00 1.00
vdw-lambdas  = 0.00 0.00 0.00 0.00 0.00 0.05 0.10 0.15 0.20 0.30 0.40 0.50 0.60 0.70 0.80 0.85 0.90 0.95 1.00

init-lambda-state      = LAMBDA_STATE
calc-lambda-neighbors  = 1

sc-alpha               = 0.5
sc-power               = 1
sc-sigma               = 0.3
sc-coul                = no

nstdhdl                = 100
dhdl-derivatives       = yes
separate-dhdl-file     = yes
~~~

**calc-lambda-neighbors = 1** calcula diferencias con estados vecinos para BAR. **nstdhdl** debe ser múltiplo de **nstcalcenergy**.

**init-lambda-state** es el índice entero de las listas, no el valor de λ. No use simultáneamente **fep-lambdas** y **coul-lambdas/vdw-lambdas** para describir la misma ruta sin controlar cómo se forma el vector λ.

### 12. Equilibrar cada estado

Prepare:

- **fep_equilibration.template.mdp** para relajar cada Hamiltoniano;
- **fep_production.template.mdp** para acumular datos.

Ambos contienen **LAMBDA_STATE**.

Equilibración por ventana:

~~~ini
nsteps       = 250000
nstdhdl      = 0
gen-vel      = yes
gen-temp     = 298.15
gen-seed     = -1
~~~

Producción por ventana:

~~~ini
nsteps       = 2500000
nstdhdl      = 100
gen-vel      = no
continuation = yes
~~~

Con \(dt=0.002\ \mathrm{ps}\), corresponden a 0.5 ns y 5 ns. Son puntos de partida, no garantías de convergencia.

### 13. Crear y ejecutar las ventanas

Script para Bash 4 o superior:

~~~bash
#!/usr/bin/env bash
set -euo pipefail

GMX_COMMAND="${GMX_COMMAND:-gmx}"
START_STRUCTURE="02_equilibracion/npt.gro"
TOPOLOGY="topol.top"

for STATE in $(seq 0 18)
do
    DIRECTORY=$(printf "03_fep/lambda_%02d" "${STATE}")
    mkdir -p "${DIRECTORY}"

    sed "s/LAMBDA_STATE/${STATE}/g" \
        fep_equilibration.template.mdp \
        > "${DIRECTORY}/equilibration.mdp"

    sed "s/LAMBDA_STATE/${STATE}/g" \
        fep_production.template.mdp \
        > "${DIRECTORY}/production.mdp"

    "${GMX_COMMAND}" grompp \
        -f "${DIRECTORY}/equilibration.mdp" \
        -c "${START_STRUCTURE}" \
        -p "${TOPOLOGY}" \
        -o "${DIRECTORY}/equilibration.tpr"

    "${GMX_COMMAND}" mdrun \
        -deffnm "${DIRECTORY}/equilibration" \
        -v

    "${GMX_COMMAND}" grompp \
        -f "${DIRECTORY}/production.mdp" \
        -c "${DIRECTORY}/equilibration.gro" \
        -t "${DIRECTORY}/equilibration.cpt" \
        -p "${TOPOLOGY}" \
        -o "${DIRECTORY}/production.tpr"

    "${GMX_COMMAND}" mdrun \
        -deffnm "${DIRECTORY}/production" \
        -dhdl "${DIRECTORY}/dhdl.xvg" \
        -v
done
~~~

~~~bash
chmod +x run_fep.sh
bash -n run_fep.sh
./run_fep.sh
~~~

Las ventanas son independientes después de generar sus TPR y pueden ejecutarse como un array de trabajos. No use el mismo directorio o nombre de salida para ventanas diferentes.

### 14. Ejecución en un array HPC

Ejemplo mínimo basado en **SLURM_ARRAY_TASK_ID**:

~~~bash
STATE="${SLURM_ARRAY_TASK_ID}"
DIRECTORY=$(printf "03_fep/lambda_%02d" "${STATE}")

gmx mdrun \
    -deffnm "${DIRECTORY}/production" \
    -dhdl "${DIRECTORY}/dhdl.xvg" \
    -v
~~~

Los TPR deben haberse generado previamente. Los recursos, GPU, partición y tiempo dependen del clúster.

Registre:

~~~text
estado | coul-lambda | vdw-lambda | semilla | duración | estado del trabajo
~~~

### 15. Continuar una ventana

~~~bash
gmx mdrun \
    -deffnm 03_fep/lambda_07/production \
    -cpi 03_fep/lambda_07/production.cpt \
    -append \
    -dhdl 03_fep/lambda_07/dhdl.xvg \
    -v
~~~

No regenere el TPR si solo continúa el mismo Hamiltoniano. Si cambia MDP, duración o λ, documente el nuevo segmento.

### 16. Análisis con BAR

Los directorios llevan ceros iniciales para que el glob preserve el orden:

~~~bash
mkdir -p 04_analisis

gmx bar \
    -b 500 \
    -f 03_fep/lambda_*/dhdl.xvg \
    -o 04_analisis/bar_deltaG.xvg \
    -oi 04_analisis/bar_integral.xvg \
    -oh 04_analisis/bar_histograms.xvg \
    -prec 3
~~~

**-b 500** descarta 500 ps de cada archivo. Determine el descarte mediante la relajación real de las ventanas, no por copia del ejemplo.

Con la convención usada:

\[
\Delta G_{\mathrm{solv}}
=
-\Delta G_{\mathrm{BAR}}
\]

### 17. Diagnóstico de BAR

Revise por cada par:

- \(\Delta G\) parcial;
- incertidumbre;
- entropías relativas **s_A** y **s_B**;
- desviación esperada por muestra;
- histogramas;
- consistencia entre ventanas.

Las entropías relativas son indicadores de distancia entre distribuciones; valores grandes sugieren peor superposición.

El error de BAR no incluye automáticamente error del campo de fuerza, modelo de agua, especie química, estado estándar, tamaño finito o muestreo conformacional ausente. Precisión estadística no implica exactitud química.

### 18. Convergencia temporal y réplicas

Repita BAR con distintos descartes:

~~~bash
gmx bar -b 250  -f 03_fep/lambda_*/dhdl.xvg
gmx bar -b 500  -f 03_fep/lambda_*/dhdl.xvg
gmx bar -b 1000 -f 03_fep/lambda_*/dhdl.xvg
~~~

Una estimación defendible debe mostrar:

- ausencia de deriva;
- superposición bilateral;
- contribuciones sin saltos dominantes;
- compatibilidad entre mitades temporales;
- compatibilidad entre réplicas;
- menor incertidumbre al aumentar datos efectivos.

Las filas consecutivas están correlacionadas. El número de filas no es el número de muestras independientes.

Use semillas distintas y vuelva a equilibrar las ventanas para cada réplica. Trayectorias con el mismo checkpoint y velocidades no son independientes.

### 19. Refinar la grilla

Agregue estados entre \(\lambda_i\) y \(\lambda_{i+1}\) si los histogramas apenas se superponen, el error parcial domina, **s_A/s_B** aumentan abruptamente o el solvente entra y sale de forma discontinua.

No agregue ventanas donde el solapamiento ya es alto si el cuello de botella está en otra región. Redistribuya el cálculo.

### 20. Unidades de energía

GROMACS informa energías molares en kJ·mol⁻¹.

\[
1\ \mathrm{kcal\,mol^{-1}}
=
4.184\ \mathrm{kJ\,mol^{-1}}
\]

\[
1\ \mathrm{eV\ por\ molécula}
=
96.485332\ \mathrm{kJ\,mol^{-1}}
\]

\[
1\ E_h
=
2625.50\ \mathrm{kJ\,mol^{-1}}
\]

Por tanto:

\[
-0.151256\ \mathrm{eV}
\times
96.485332
=
-14.59399\ \mathrm{kJ\,mol^{-1}}
\]

El valor anterior, −14.5934028 kJ·mol⁻¹, difiere ligeramente por el factor de conversión empleado. Esa diferencia es despreciable frente a la incertidumbre física, pero debe usarse una constante consistente.

### 21. Energía térmica

A 298.15 K:

\[
RT=
(8.314462618\times10^{-3})
(298.15)
=
2.47896\ \mathrm{kJ\,mol^{-1}}
\]

Una unidad \(k_\mathrm{B}T\) por partícula equivale numéricamente a una unidad \(RT\) por mol.

\[
-14.594\ \mathrm{kJ\,mol^{-1}}
\approx
-5.89\ k_\mathrm{B}T
\]

No multiplique por el número de Avogadro una energía ya expresada por mol.

### 22. Tiempo y λ

\[
1000\ \mathrm{ps}=1\ \mathrm{ns}
\]

Con:

~~~ini
dt     = 0.002
nsteps = 2500000
~~~

\[
t=0.002\ \mathrm{ps}\times2500000
=5000\ \mathrm{ps}
=5\ \mathrm{ns}
\]

λ es adimensional; **init-lambda-state** es un índice entero.

### 23. Estados estándar

Una referencia experimental puede usar gas ideal a 1 atm o 1 bar, solución a 1 mol·L⁻¹, dilución infinita o una convención de ley de Henry.

La conversión gas–solución contiene:

\[
\Delta G^\circ_{\mathrm{corr}}
=
RT\ln
\left(
\frac{C^\circ RT}{p^\circ}
\right)
\]

A 298.15 K, la magnitud entre 1 atm y 1 mol·L⁻¹ es aproximadamente 7.9 kJ·mol⁻¹. El signo depende de la dirección y de la definición original.

No aplique esta corrección sin identificar las convenciones experimental y computacional.

### 24. Tamaño finito y carga

Para solutos con carga neta, PME y una caja periódica con fondo neutralizante introducen correcciones dependientes de la carga, la caja, la constante dieléctrica y la convención electrostática.

El formaldehído aquí es neutro y no requiere la corrección principal de carga neta. Persisten posibles efectos de tamaño y dipolo.

No compare transformaciones que cambian la carga neta sin un protocolo específico.

### 25. Limitación química del formaldehído

En agua:

\[
\mathrm{H_2CO + H_2O
\rightleftharpoons
CH_2(OH)_2}
\]

El producto es metanodiol o metilenglicol. Según la concentración también pueden existir oligómeros.

Un campo de fuerza clásico de topología fija no rompe el enlace C=O, no forma enlaces C–O, no transfiere protones y no convierte formaldehído en metanodiol.

Este cálculo estima:

\[
\mathrm{H_2CO(g)}
\rightarrow
\mathrm{H_2CO(aq)}
\]

para formaldehído mantenido artificialmente como tal. No estima directamente:

\[
\mathrm{H_2CO(g)+H_2O(l)}
\rightarrow
\mathrm{CH_2(OH)_2(aq)}
\]

ni la solubilidad total de formaldehído.

### 26. Ciclo químico correcto

El proceso efectivo puede descomponerse:

\[
\Delta G^\circ_{\mathrm{global}}
=
\Delta G^\circ_{\mathrm{solv}}(\mathrm{H_2CO})
+
\Delta G^\circ_{\mathrm{hidratación,aq}}
\]

Alternativas:

- calcular solo solvatación física de \(\mathrm{H_2CO}\) y declararlo;
- parametrizar metanodiol como especie diferente;
- calcular la hidratación covalente mediante QM/MM o estructura electrónica;
- combinar solvatación y reacción en un ciclo termodinámico;
- usar etanol o metanol como ejemplo pedagógico no reactivo.

El tutorial oficial de GROMACS usa etanol, una elección más clara para enseñar el procedimiento general. El formaldehído resulta útil para mostrar que la especie química debe definirse antes del cálculo.

### 27. Comparación con el valor atribuido a NIST

El texto anterior cita:

\[
-0.151256\ \mathrm{eV}
=
-14.59399\ \mathrm{kJ\,mol^{-1}}
\]

Antes de compararlo con BAR deben coincidir:

- especie;
- sentido solvatación/desolvatación;
- temperatura;
- estado estándar;
- solvente;
- definición de dilución;
- inclusión de hidratación covalente;
- convención de la base.

La página general del proyecto NIST no reemplaza el registro específico con sus metadatos. Un acuerdo numérico accidental puede ocultar signos opuestos o procesos químicos distintos.

### 28. Interpretación de resultados

Un resultado como:

\[
-22.94\pm1.04\ \mathrm{kJ\,mol^{-1}}
\]

solo es interpretable si se informa:

- extremos de λ;
- signo aplicado a BAR;
- tiempo descartado;
- duración por ventana;
- grilla;
- réplicas;
- método de incertidumbre;
- campo de fuerza;
- agua;
- temperatura;
- correcciones;
- especie química.

El ± suele representar incertidumbre estadística condicionada al muestreo. No incluye errores de parametrización o química ausente.

### 29. Controles adicionales

~~~bash
gmx trjconv \
    -s 03_fep/lambda_00/production.tpr \
    -f 03_fep/lambda_00/production.xtc \
    -o 04_analisis/lambda_00_snapshot.gro \
    -dump 5000

gmx trjconv \
    -s 03_fep/lambda_18/production.tpr \
    -f 03_fep/lambda_18/production.xtc \
    -o 04_analisis/lambda_18_snapshot.gro \
    -dump 5000
~~~

Controle temperatura, volumen, errores LINCS, integridad del soluto, respuesta del solvente, ausencia de singularidades, producción de archivos de diferencias de energía y estado λ informado en el log.

En el extremo desacoplado el solvente puede ocupar el espacio del soluto. Es un comportamiento esperado con soft-core.

### 30. Errores frecuentes

- No definir los estados extremos.
- Confundir solvatación con desolvatación.
- Usar **vdwq** en vez de la sintaxis actual **vdw-q**.
- Eliminar Lennard-Jones antes que las cargas.
- Usar cinco λ uniformes y asumir convergencia.
- Desacoplar Coulomb y Lennard-Jones simultáneamente sin validación.
- No equilibrar cada ventana.
- Copiar arbitrariamente el descarte **-b**.
- Reutilizar un directorio para varias ventanas.
- Usar archivos sin orden definido.
- Tratar muestras correlacionadas como independientes.
- Informar solamente el error de BAR.
- Confundir eV por molécula con kJ·mol⁻¹.
- Multiplicar otra vez por \(N_A\).
- Ignorar el estado estándar.
- Perturbar varias copias del mismo **moleculetype**.
- Cambiar carga neta sin correcciones.
- Comparar formaldehído molecular con formaldehído total acuoso.
- Aceptar una minimización que no alcanzó su criterio.
- Usar **-maxwarn** para producir el TPR.

### 31. Reproducibilidad mínima

Informe:

- versión exacta de GROMACS;
- origen y versión de parámetros;
- modelo de agua;
- topología molecular;
- caja y número de aguas;
- temperatura y presión;
- integrador y paso;
- lista completa de λ;
- parámetros soft-core;
- equilibración y producción;
- frecuencia de diferencias de energía;
- método de análisis y descarte;
- réplicas y semillas;
- correcciones;
- signo de \(\Delta G\);
- especie química calculada.

### 32. Criterios de aceptación

El cálculo es técnicamente defendible cuando:

- los extremos están definidos;
- la topología es químicamente correcta;
- todas las ventanas terminaron;
- existe superposición entre vecinos;
- las contribuciones parciales son estables;
- el resultado converge temporalmente;
- las réplicas son compatibles;
- unidades y signo son inequívocos;
- se aplicaron las correcciones necesarias;
- el dato experimental usa una convención comparable;
- la especie simulada coincide con la experimental.

Para formaldehído acuoso en equilibrio, el último criterio no se cumple si solo se modela \(\mathrm{H_2CO}\) mediante una topología clásica fija.

### Fuentes

1. [Tutorial oficial de energía libre de solvatación de GROMACS](https://tutorials.gromacs.org/docs/free-energy-of-solvation.html)
2. [Opciones MDP de energía libre en GROMACS 2026.3](https://manual.gromacs.org/current/user-guide/mdp-options.html)
3. [Referencia de gmx bar](https://manual.gromacs.org/current/onlinehelp/gmx-bar.html)
4. [Perturbation Free-Energy Toolkit](https://pmc.ncbi.nlm.nih.gov/articles/PMC8479811/)
5. [Guidelines for the analysis of free energy calculations](https://link.springer.com/article/10.1007/s10822-015-9840-9)
6. [Python tool for relative free-energy calculations in GROMACS](https://link.springer.com/article/10.1007/s10822-015-9873-0)
7. [Tutorial histórico de FEP con GROMACS](http://www.mdtutorials.com/gmx/2018/free_energy/index.html)
8. [Revisión adicional proporcionada](https://pmc.ncbi.nlm.nih.gov/articles/PMC12163693/)
9. [Proyecto NIST sobre energías libres de solvatación](https://www.nist.gov/programs-projects/solvation-free-energies)



## Energía de unión mediante gmx_MMPBSA

### 1. Qué calcula este método

**gmx_MMPBSA** es la implementación actual para realizar cálculos de energía libre de unión de estados finales usando trayectorias y topologías de GROMACS. Está basado en **MMPBSA.py** de AmberTools y reemplaza el flujo antiguo basado en **g_mmpbsa**, un archivo **pbsa.mdp**, APBS ejecutado externamente y el script **pbsa.py**.

MM/PBSA y MM/GBSA no son FEP. No contienen estados λ, no hacen desaparecer el ligando y no necesitan umbrella sampling para impedir que el ligando se aleje durante un desacoplamiento. Analizan configuraciones ya muestreadas de los estados unido y libre mediante un modelo de solvente implícito.

El esquema básico es:

\[
\Delta G_{\mathrm{bind}}
=
G_{\mathrm{complejo}}
-
G_{\mathrm{receptor}}
-
G_{\mathrm{ligando}}
\]

Para cada especie:

\[
G=
E_{\mathrm{MM}}
+
G_{\mathrm{solv}}
-
TS
\]

La energía de mecánica molecular puede escribirse:

\[
E_{\mathrm{MM}}
=
E_{\mathrm{bonded}}
+
E_{\mathrm{vdW}}
+
E_{\mathrm{elec}}
\]

y la contribución de solvatación:

\[
G_{\mathrm{solv}}
=
G_{\mathrm{polar}}
+
G_{\mathrm{nonpolar}}
\]

Por tanto:

\[
\Delta G_{\mathrm{bind}}
=
\Delta E_{\mathrm{MM}}
+
\Delta G_{\mathrm{polar}}
+
\Delta G_{\mathrm{nonpolar}}
-
T\Delta S
\]

Si no se calcula entropía, el resultado contiene solo:

\[
\Delta G_{\mathrm{bind}}^{*}
=
\Delta E_{\mathrm{MM}}
+
\Delta G_{\mathrm{solv}}
\]

El asterisco recuerda que no es una energía libre absoluta completa. Muchos informes la llaman “binding free energy”, pero físicamente es una estimación end-state sin el término entrópico explícito.

### 2. PB frente a GB

MM/PBSA calcula la contribución polar resolviendo numéricamente la ecuación de Poisson–Boltzmann. MM/GBSA utiliza una aproximación Generalized Born.

| Método | Ventaja | Limitación |
|---|---|---|
| MM/GBSA | Más rápido; útil para explorar protocolos y series. | Mayor dependencia del modelo GB y del conjunto de radios. |
| MM/PBSA | Tratamiento continuo electrostático más explícito. | Más costoso y sensible a malla, radios, dieléctricos y convergencia numérica. |
| 3D-RISM | Describe estructura promedio del solvente con mayor detalle. | Coste y preparación superiores; escalamiento paralelo limitado. |

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

~~~text
trayectoria del complejo
        ├── complejo
        ├── receptor extraído
        └── ligando extraído
~~~

Esto mantiene correspondencia conformacional entre los tres términos y favorece la cancelación:

\[
\Delta E_{\mathrm{bonded}}\approx0
\]

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

\[
\Delta G_{\mathrm{bind}}
=
\langle G_C\rangle_C
-
\langle G_R\rangle_R
-
\langle G_L\rangle_L
\]

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

~~~text
md.tpr              estructura y masas del complejo
md_fit.xtc          trayectoria corregida
index.ndx           grupos receptor y ligando
topol.top           topología completa de GROMACS
reference.pdb       referencia con cadenas y numeración, recomendada
mmpbsa.in           opciones del cálculo
~~~

La topología del ligando debe estar incluida en **topol.top**. La ruta actual no reconstruye ligandos desde un PDB sin parámetros.

### 7. Instalación reproducible

Conda o Mamba, Python 3.12:

~~~bash
conda create -n gmxMMPBSA python=3.12 -y
conda activate gmxMMPBSA

conda install -c conda-forge \
    "mpi4py>=4.0.1,<5" \
    "ambertools>=24.8,<27" \
    -y

python -m pip install gmx_MMPBSA
python -m pip check
~~~

Si GROMACS 2026 ya está instalado en el sistema y disponible en **PATH**, no instale otra copia sin necesidad. Verifique:

~~~bash
gmx --version
gmx_MMPBSA --version
gmx_MMPBSA -h
python -m pip check
~~~

Para una instalación completamente aislada:

~~~bash
conda install -c conda-forge "gromacs>=2022,<2027" pocl -y
~~~

La interfaz gráfica requiere PyQt6:

~~~bash
conda install -c conda-forge pyqt6 -y
~~~

No es necesaria en un nodo HPC sin entorno gráfico.

### 8. Probar la instalación

~~~bash
gmx_MMPBSA_test -h
~~~

Ejecute primero una prueba pequeña proporcionada por el paquete. Esto permite separar problemas de instalación de problemas propios de la topología.

Compruebe además:

~~~bash
command -v gmx
command -v gmx_MMPBSA
command -v ante-MMPBSA.py
echo "${AMBERHOME:-AMBERHOME no definido}"
~~~

La instalación debe encontrar AmberTools y GROMACS dentro del entorno activo o mediante las opciones de configuración correspondientes.

### 9. Preparación de los grupos

Cree un índice que contenga grupos separados y sin solapamiento:

- receptor;
- ligando;
- complejo receptor–ligando.

Forma interactiva:

~~~bash
gmx make_ndx \
    -f md.tpr \
    -o index.ndx
~~~

Ejemplo dentro de **make_ndx**, si el ligando se llama LIG:

~~~text
r LIG
Protein | r LIG
name NOMBRE_GRUPO_RECEPTOR Receptor
name NOMBRE_GRUPO_LIGANDO Ligando
name NOMBRE_GRUPO_COMPLEJO Complejo
q
~~~

Los números reales dependen del índice creado. Verifique:

~~~bash
gmx make_ndx \
    -f md.tpr \
    -n index.ndx \
    -o index_check.ndx
~~~

No use números copiados de otro sistema. La opción actual **-cg** acepta números de grupo basados en cero o nombres.

### 10. Corregir la trayectoria

La documentación requiere una trayectoria sin problemas de PBC y ajustada. El ligando debe permanecer junto al receptor.

Primero centre el complejo:

~~~bash
(echo Complejo; echo System) | \
gmx trjconv \
    -s md.tpr \
    -f md.xtc \
    -n index.ndx \
    -o md_center.xtc \
    -pbc mol \
    -center \
    -ur compact
~~~

Luego elimine rotación y traslación:

~~~bash
(echo Backbone; echo System) | \
gmx trjconv \
    -s md.tpr \
    -f md_center.xtc \
    -n index.ndx \
    -o md_fit.xtc \
    -fit rot+trans
~~~

Compruebe visualmente que:

- la proteína esté entera;
- el ligando no salte por PBC;
- el orden atómico no cambie;
- no se hayan descartado componentes necesarios;
- los tiempos sean correctos.

Para MM/PBSA se elimina el solvente durante la preparación interna. No genere una trayectoria manualmente desolvatada si todavía no verificó que la selección mantiene todos los componentes del complejo.

### 11. Estructura de referencia

Genere un PDB de referencia con el complejo completo:

~~~bash
echo Complejo | \
gmx trjconv \
    -s md.tpr \
    -f md_fit.xtc \
    -n index.ndx \
    -o reference.pdb \
    -dump 0
~~~

Revise cadenas, numeración, nombres de residuos y átomos. La opción **-cr reference.pdb** es recomendada porque evita asignaciones automáticas incorrectas, especialmente en complejos con varias cadenas.

### 12. Generar un archivo de entrada

La versión actual puede generar plantillas:

~~~bash
gmx_MMPBSA --create_input gb
gmx_MMPBSA --create_input pb
gmx_MMPBSA --create_input gb decomp
gmx_MMPBSA --create_input gb nmode
~~~

Revise siempre la plantilla generada por la versión instalada:

~~~bash
gmx_MMPBSA --input-file-help
~~~

No reutilice el archivo **pbsa.mdp** de **g_mmpbsa**. La sintaxis actual usa bloques namelist como **&general**, **&gb**, **&pb** y **&decomp**.

### 13. Entrada mínima MM/GBSA

Archivo **mmpbsa_gb.in**:

~~~text
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
~~~

Con **igb=8**, la documentación recomienda **PBRadii=4**, correspondiente a mbondi3.

**startframe**, **endframe** e **interval** se refieren a índices de marcos procesados, no necesariamente a ps. El número analizado es aproximadamente:

\[
N_{\mathrm{frames}}
=
\left\lfloor
\frac{f_{\mathrm{final}}-f_{\mathrm{inicial}}}
     {\mathrm{interval}}
\right\rfloor+1
\]

No elija 500 marcos consecutivos y los trate como 500 observaciones independientes.

### 14. Ejecutar MM/GBSA

~~~bash
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
~~~

Significado de las opciones principales:

| Opción | Función |
|---|---|
| **-O** | Permite sobrescribir resultados existentes. Úsela deliberadamente. |
| **-i** | Archivo de parámetros. |
| **-cs** | TPR o PDB del complejo; se recomienda el TPR de producción. |
| **-ct** | Una o más trayectorias del complejo. |
| **-ci** | Índice del complejo. |
| **-cg** | Grupos receptor y ligando. |
| **-cp** | Topología completa de GROMACS, obligatoria. |
| **-cr** | PDB de referencia recomendado. |
| **-o** | Resumen estadístico. |
| **-eo** | Energías por marco en CSV. |
| **-nogui** | No abre el analizador gráfico al terminar. |

### 15. Entrada mínima MM/PBSA

Genere primero la plantilla de su versión:

~~~bash
gmx_MMPBSA --create_input pb
~~~

Ejemplo inicial **mmpbsa_pb.in**:

~~~text
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
~~~

Ejecución:

~~~bash
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
~~~

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

\[
I=\frac{1}{2}\sum_i c_i z_i^2
\]

Para NaCl ideal 1:1, 0.15 M produce \(I=0.15\ \mathrm{M}\). Para una sal divalente la concentración molar y la fuerza iónica no son iguales.

### 17. Radios atómicos

Los radios influyen en la frontera dieléctrica y en el término polar. No son una opción cosmética.

Correspondencias documentadas:

| PBRadii | Conjunto | Uso típico |
|---:|---|---|
| 1 | bondi | Asociado habitualmente con igb=7. |
| 2 | mbondi | Asociado habitualmente con igb=1. |
| 3 | mbondi2 | Asociado con igb=2 o 5. |
| 4 | mbondi3 | Asociado con igb=8. |
| 7 | charmm_radii | Solo PB y topologías preparadas con CHARMM. |

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

~~~text
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
~~~

Es un esquema orientativo. Debe adaptarse a la orientación de la bicapa, nombres de átomos, espesor, presencia de poro y modelo experimental. Una membrana implícita mal centrada puede producir un resultado peor que un modelo acuoso simplificado claramente declarado.

### 20. Entropía

Sin entropía:

\[
\Delta G_{\mathrm{estimada}}
=
\Delta E_{\mathrm{MM}}
+
\Delta G_{\mathrm{solv}}
\]

Con entropía:

\[
\Delta G_{\mathrm{bind}}
=
\Delta H_{\mathrm{aprox}}
-
T\Delta S
\]

Métodos disponibles:

- Interaction Entropy;
- C2 Entropy;
- modos normales, NMODE.

NMODE es costoso y sensible a minimización. El consumo total de memoria crece aproximadamente como:

\[
RAM_{\mathrm{total}}
=
RAM_{\mathrm{por\ marco}}
\times
N_{\mathrm{procesos}}
\]

No paralelice NMODE hasta agotar memoria.

### 21. Interaction Entropy

La aproximación IE usa fluctuaciones de la energía de interacción:

\[
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
\]

con:

\[
\Delta E_{\mathrm{int}}
=
E_{\mathrm{int}}
-
\left\langle E_{\mathrm{int}}\right\rangle
\]

Entrada:

~~~text
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
~~~

Debe informarse \(\sigma_{IE}\), la desviación de la energía de interacción. La documentación desaconseja IE cuando:

\[
\sigma_{IE}\gtrsim3.6\ \mathrm{kcal\,mol^{-1}}
\]

porque el promedio exponencial se vuelve difícil de converger. Esto equivale aproximadamente a:

\[
3.6\ \mathrm{kcal\,mol^{-1}}
=
15.1\ \mathrm{kJ\,mol^{-1}}
\]

**ie_segment** es un diagnóstico de la cola de la curva acumulativa; no reemplaza el resultado calculado sobre todo el conjunto seleccionado.

### 22. Descomposición por residuos

Genere una plantilla:

~~~bash
gmx_MMPBSA --create_input gb decomp
~~~

Ejemplo:

~~~text
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
~~~

Ejecución:

~~~bash
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
~~~

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

\[
\Delta\Delta G_{\mathrm{bind}}
=
\Delta G_{\mathrm{bind}}^{\mathrm{mutante}}
-
\Delta G_{\mathrm{bind}}^{\mathrm{WT}}
\]

Interpretación:

- \(\Delta\Delta G>0\): la mutación debilita la unión en esta convención;
- \(\Delta\Delta G<0\): la mutación la favorece.

Es una mutación end-state sobre estructuras existentes. No reemplaza una dinámica completa del mutante si este reorganiza la proteína.

### 24. Paralelización

Ejecución serial:

~~~bash
gmx_MMPBSA -O \
    -i mmpbsa_gb.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -nogui
~~~

Con MPI:

~~~bash
mpirun -np 4 gmx_MMPBSA -O \
    -i mmpbsa_gb.in \
    -cs md.tpr \
    -ct md_fit.xtc \
    -ci index.ndx \
    -cg Receptor Ligando \
    -cp topol.top \
    -cr reference.pdb \
    -nogui
~~~

No use **gmx_mpi** dentro de esta ejecución MPI. La documentación indica usar **gmx**, porque las herramientas auxiliares de GROMACS no se benefician del MPI de **mdrun** y pueden entrar en conflicto con **mpirun**.

El escalamiento deja de mejorar cuando el número de procesos se aproxima al número de marcos o domina la carga de topologías.

### 25. Análisis gráfico

~~~bash
gmx_MMPBSA_ana \
    -f FINAL_RESULTS_MMPBSA.dat
~~~

El analizador permite revisar términos, evolución temporal, descomposición y exportar gráficos. En HPC use los archivos DAT y CSV, y abra el analizador en una estación con entorno gráfico.

Conserve:

~~~text
FINAL_RESULTS_MMPBSA.dat
FINAL_RESULTS_MMPBSA.csv
FINAL_DECOMP_MMPBSA.dat
FINAL_DECOMP_MMPBSA.csv
gmx_MMPBSA.log
mmpbsa.in
~~~

No conserve únicamente una captura del valor final.

### 26. Unidades

Las salidas heredadas de AmberTools suelen expresarse en kcal·mol⁻¹. Verifique siempre el encabezado del archivo.

\[
1\ \mathrm{kcal\,mol^{-1}}
=
4.184\ \mathrm{kJ\,mol^{-1}}
\]

Ejemplo:

\[
-28.6\ \mathrm{kcal\,mol^{-1}}
=
-119.7\ \mathrm{kJ\,mol^{-1}}
\]

No mezcle resultados antiguos de **g_mmpbsa**, que normalmente se informaban en kJ·mol⁻¹, con resultados de **gmx_MMPBSA** sin convertir unidades.

En parámetros PB y GB aparecen además:

- concentración y fuerza iónica en mol·L⁻¹;
- radios y distancias en Å;
- tensión superficial en kcal·mol⁻¹·Å⁻².

### 27. Relación con afinidad experimental

Bajo estados estándar compatibles:

\[
\Delta G^\circ_{\mathrm{bind}}
=
RT\ln K_d
=
-RT\ln K_a
\]

A 298.15 K:

\[
RT=2.47896\ \mathrm{kJ\,mol^{-1}}
=0.59248\ \mathrm{kcal\,mol^{-1}}
\]

Entonces:

\[
K_d=
\exp
\left(
\frac{\Delta G^\circ_{\mathrm{bind}}}{RT}
\right)
\]

Esta conversión solo es válida para una energía libre estándar completa. No convierta directamente un MM/GBSA sin entropía ni correcciones en un \(K_d\) “predicho”.

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

~~~text
0–20 ns
20–40 ns
40–60 ns
60–80 ns
80–100 ns
~~~

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

\[
\Delta\Delta G_i
=
\Delta G_i-
\Delta G_{\mathrm{referencia}}
\]

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
- Convertir un resultado sin entropía directamente en \(K_d\).
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


# Interacción energética lineal (Linear Interaction Energy, LIE)

La **energía de interacción lineal** (LIE) es un método de estado final para estimar afinidades de unión. Requiere muestrear explícitamente dos estados mediante dinámica molecular:

1. el ligando unido al receptor y rodeado por solvente e iones;
2. el mismo ligando libre en solvente, con el mismo estado de protonación y un protocolo compatible.

LIE es más económico que una transformación alquímica completa porque no introduce estados intermedios de \(\lambda\). A cambio, es un modelo semiempírico: no debe interpretarse como una energía libre rigurosa ni utilizarse con coeficientes tomados arbitrariamente de otros sistemas. Su utilidad principal es comparar ligandos relacionados para un mismo receptor y dentro del dominio químico e interaccional empleado para calibrar el modelo.

## Fundamento teórico

En la forma más habitual,

\[
\Delta G_{\mathrm{bind}}^{\mathrm{LIE}}
=
\alpha\left(
\left\langle V_{\mathrm{vdW}}^{L-E}\right\rangle_{\mathrm{bound}}
-
\left\langle V_{\mathrm{vdW}}^{L-E}\right\rangle_{\mathrm{free}}
\right)
+
\beta\left(
\left\langle V_{\mathrm{elec}}^{L-E}\right\rangle_{\mathrm{bound}}
-
\left\langle V_{\mathrm{elec}}^{L-E}\right\rangle_{\mathrm{free}}
\right)
+
\gamma .
\]

Aquí:

- \(L\) es el ligando y \(E\) es su entorno;
- en el estado unido, el entorno incluye receptor, agua, iones y cualquier cofactor que no forme parte del ligando;
- en el estado libre, el entorno incluye agua e iones;
- los corchetes \(\langle\cdots\rangle\) representan promedios de conjunto, aproximados mediante promedios temporales sobre trayectorias equilibradas;
- \(\alpha\) y \(\beta\) son coeficientes adimensionales para las contribuciones de Lennard-Jones y electrostática;
- \(\gamma\) es un intercepto opcional, expresado en kJ mol\(^{-1}\).

La contribución electrostática procede de una aproximación de respuesta lineal. El valor histórico \(\beta=0{,}5\) corresponde al caso ideal de respuesta lineal, pero no es universal. La documentación de GROMACS 2026.3 conserva como valores predeterminados \(\alpha=0{,}181\) y \(\beta=0{,}5\); deben considerarse valores iniciales o de referencia, no una validación del modelo para cualquier ligando.

LIE no calcula de manera explícita todos los términos entrópicos, reorganizaciones internas, cambios conformacionales o contribuciones de estado estándar. Se presupone que una parte de esos efectos queda representada de forma efectiva por los coeficientes y el intercepto. Por eso un resultado aislado obtenido con los valores predeterminados debe describirse como **estimación LIE no calibrada**.

## Unidades y comparación con datos experimentales

GROMACS informa las energías de interacción en **kJ mol\(^{-1}\)**. Como \(\alpha\) y \(\beta\) son adimensionales, \(\Delta G_{\mathrm{bind}}^{\mathrm{LIE}}\) y \(\gamma\) conservan esas unidades.

\[
1\ \mathrm{kcal\ mol^{-1}}=4{,}184\ \mathrm{kJ\ mol^{-1}}.
\]

Para transformar una constante experimental de disociación en una energía libre estándar,

\[
\Delta G^\circ_{mathrm{bind}}
=
RT\ln\left(\frac{K_d}{C^\circ}\right)
=
-RT\ln\left(K_a C^\circ\right),
\]

donde \(C^\circ=1\ \mathrm{mol\ L^{-1}}\). La razón dentro del logaritmo debe ser adimensional. Deben registrarse la temperatura, la fuerza iónica, el pH y el estado de protonación del ligando; comparar directamente valores obtenidos bajo condiciones experimentales distintas puede introducir un error mayor que el que se intenta modelar.

## Diseño de las simulaciones

Los estados unido y libre deben usar, en lo posible:

- el mismo campo de fuerzas para el ligando;
- el mismo modelo de agua, concentración salina y temperatura;
- idéntico tratamiento de interacciones no enlazantes;
- el mismo estado de protonación, tautomería y carga;
- longitudes de producción y criterios de descarte comparables;
- varias réplicas independientes cuando el coste lo permita.

No debe extraerse el ligando de la caja del complejo y analizarse sin una simulación libre propia: la relajación y la reorganización del solvente son parte esencial del estado libre. Para sistemas flexibles o con poses alternativas conviene iniciar réplicas desde conformaciones distintas. Si el ligando abandona el sitio, cambia de pose de forma irreversible o el receptor experimenta una transición grande, esa trayectoria no debe promediarse ciegamente con las demás.

## Preparación de grupos de energía

La orden **gmx lie** necesita términos de interacción no enlazante entre el ligando y el resto del sistema en el archivo EDR. La separación más clara es usar dos grupos no superpuestos que cubran todo el sistema: **LIG** y **Environment**.

Para crear un índice estático a partir del TPR del complejo:

~~~bash
gmx select -s md_bound.tpr -on lie_bound.ndx \
  -select '"LIG" resname LIG; "Environment" not resname LIG'
~~~

Para el ligando libre:

~~~bash
gmx select -s md_free.tpr -on lie_free.ndx \
  -select '"LIG" resname LIG; "Environment" not resname LIG'
~~~

Se debe reemplazar **LIG** por el nombre real del residuo o por una selección inequívoca. Si existen varias moléculas con ese mismo nombre, hay que decidir si constituyen un único ligando termodinámico o si deben analizarse por separado. Verifique siempre los grupos:

~~~bash
gmx check -f md_bound.xtc
gmx make_ndx -f md_bound.tpr -n lie_bound.ndx
~~~

Dentro de una copia del MDP de producción, agregue:

~~~ini
; Grupos no superpuestos que cubren el sistema
energygrps = LIG Environment
~~~

El resto del MDP usado para recalcular energías debe conservar el campo de fuerzas, los cortes, las reglas de dispersión, el modificador de potencial y el tratamiento electrostático de la simulación de producción. Cambiar esos parámetros durante el análisis define otro descriptor y rompe la comparabilidad con un modelo calibrado previamente.

### Limitación importante de PME

Los términos que utiliza **gmx lie** son, entre otros, **Coul-SR** y **LJ-SR**. La parte recíproca de PME no se descompone en pares de grupos como una energía ligando–entorno independiente. Por tanto, una LIE basada en esos términos es dependiente del protocolo y no contiene una asignación completa de la electrostática de largo alcance al ligando.

Esto no significa que deba eliminarse PME de una simulación moderna. Significa que todos los ligandos, los dos estados y el conjunto de calibración deben tratarse de manera idéntica, y que la limitación debe documentarse. Recalcular con reacción de campo u otro modelo electrostático sólo es defendible si todo el modelo LIE fue calibrado y validado con ese mismo protocolo.

## Obtención de los archivos EDR para LIE

Incluir grupos de energía durante una producción puede limitar la aceleración por GPU. Una alternativa práctica es recalcular las energías sobre las trayectorias ya producidas. Genere TPR de análisis separados para el complejo y el ligando libre:

~~~bash
gmx grompp -f lie_bound.mdp -c md_bound.gro -t md_bound.cpt \
  -p topol_bound.top -n lie_bound.ndx -o lie_bound.tpr

gmx grompp -f lie_free.mdp -c md_free.gro -t md_free.cpt \
  -p topol_free.top -n lie_free.ndx -o lie_free.tpr
~~~

Luego efectúe el recálculo en CPU:

~~~bash
gmx mdrun -s lie_bound.tpr -rerun md_bound.xtc \
  -deffnm lie_bound -nb cpu -pme cpu

gmx mdrun -s lie_free.tpr -rerun md_free.xtc \
  -deffnm lie_free -nb cpu -pme cpu
~~~

**mdrun -rerun** evalúa la energía de cada marco de la trayectoria suministrada; no genera un nuevo muestreo. Los archivos TPR deben conservar la misma topología, orden de átomos y parámetros no enlazantes usados para producir cada trayectoria. Los valores cinéticos y de temperatura obtenidos en un recálculo de este tipo no son relevantes para LIE.

Antes de continuar, compruebe que existen los términos esperados:

~~~bash
gmx energy -f lie_free.edr -o /dev/null
gmx energy -f lie_bound.edr -o /dev/null
~~~

Deben aparecer nombres equivalentes a:

~~~text
Coul-SR:LIG-Environment
LJ-SR:LIG-Environment
~~~

Si no aparecen, el TPR no contenía una definición válida de **energygrps** o el cálculo se ejecutó con una ruta que no produjo la descomposición solicitada.

## Cálculo con gmx lie en GROMACS 2026

Primero obtenga los promedios del ligando libre en solvente. El inicio del intervalo productivo se expresa en picosegundos:

~~~bash
printf "Coul-SR:LIG-Environment\nLJ-SR:LIG-Environment\n0\n" | \
  gmx energy -f lie_free.edr -o free_interactions.xvg -b 20000
~~~

Tome de la salida los promedios **Average** y asígnelos, sin cambiar signos ni unidades:

~~~bash
FREE_COUL=-104.226
FREE_LJ=-183.449
~~~

Los números anteriores son únicamente ejemplos. No deben copiarse para otro ligando.

Calcule después la estimación sobre el estado unido:

~~~bash
gmx lie -f lie_bound.edr -o lie.xvg -b 20000 \
  -Elj "$FREE_LJ" -Eqq "$FREE_COUL" \
  -Clj 0.181 -Cqq 0.5 -ligand LIG
~~~

Significado de las opciones principales:

| Opción | Significado | Unidad |
| --- | --- | --- |
| **-Elj** | Promedio LJ ligando–solvente del estado libre | kJ mol\(^{-1}\) |
| **-Eqq** | Promedio Coulomb ligando–solvente del estado libre | kJ mol\(^{-1}\) |
| **-Clj** | Coeficiente \(\alpha\) | adimensional |
| **-Cqq** | Coeficiente \(\beta\) | adimensional |
| **-ligand** | Nombre del grupo de energía del ligando | — |
| **-b**, **-e** | Inicio y final del intervalo analizado | ps, de forma predeterminada |
| **-dt** | Separación temporal entre marcos utilizados | ps |

El archivo **lie.xvg** contiene la evolución de la estimación. No se debe elegir el comienzo del promedio sólo porque la curva “parece estable” a partir de un punto conveniente. El descarte debe establecerse antes de comparar ligandos o justificarse mediante diagnósticos de equilibrio y convergencia aplicados de manera uniforme.

También es recomendable extraer los cuatro promedios por separado y verificar manualmente la ecuación. Esto detecta con facilidad grupos invertidos, signos erróneos o valores libres copiados de otro sistema.

## Calibración de los coeficientes

Para predicción cuantitativa, construya una tabla con un conjunto de ligandos de afinidad experimental conocida:

| Ligando | \(\Delta V_{\mathrm{vdW}}\) | \(\Delta V_{\mathrm{elec}}\) | \(\Delta G^\circ_{\mathrm{exp}}\) |
| --- | ---: | ---: | ---: |
| compuesto 1 | unido − libre | unido − libre | kJ mol\(^{-1}\) |
| compuesto 2 | unido − libre | unido − libre | kJ mol\(^{-1}\) |

Ajuste entonces

\[
\Delta G^\circ_{\mathrm{exp}}
=
\alpha\Delta V_{\mathrm{vdW}}
+
\beta\Delta V_{\mathrm{elec}}
+
\gamma .
\]

No es correcto promediar valores de \(\alpha\) o \(\beta\) publicados para proteínas, campos de fuerzas o familias químicas diferentes. Con pocos compuestos, ajustar simultáneamente tres parámetros produce sobreajuste; en ese caso conviene fijar uno de los coeficientes con una justificación previa o ampliar el conjunto. Deben informarse, como mínimo, validación cruzada o conjunto externo, MAE, RMSE, correlación y dominio de aplicabilidad.

Una predicción nueva es más confiable cuando el ligando se parece al conjunto de calibración no sólo en estructura, sino también en sus patrones de interacción con el receptor. Un compuesto con carga, pose o química diferente puede estar fuera del dominio aunque su esqueleto molecular parezca similar.

## Convergencia e incertidumbre

Use series temporales y promedios por bloques para cada uno de los cuatro términos energéticos. Para réplicas independientes, informe la media entre réplicas y su incertidumbre; una trayectoria larga no sustituye necesariamente varias inicializaciones cuando existen poses o estados conformacionales separados.

Una aproximación útil para la propagación de la incertidumbre es

\[
\sigma^2_{\Delta G}
\approx
\alpha^2\sigma^2_{\Delta V_{\mathrm{vdW}}}
+
\beta^2\sigma^2_{\Delta V_{\mathrm{elec}}}
+
2\alpha\beta\operatorname{Cov}
\left(\Delta V_{\mathrm{vdW}},\Delta V_{\mathrm{elec}}\right).
\]

Esta expresión debe emplear errores de los promedios que tengan en cuenta la autocorrelación, no la desviación estándar de los marcos como si fueran observaciones independientes. Si \(\alpha\), \(\beta\) y \(\gamma\) fueron ajustados, su incertidumbre también contribuye al error predictivo.

Como diagnóstico mínimo:

- grafique promedios acumulativos y por bloques;
- compare mitades de la región productiva;
- examine por separado los estados libre y unido;
- compruebe la estabilidad de la pose, contactos, hidratación y estado conformacional;
- repita el cálculo con varias réplicas y documente cualquier exclusión.

## Múltiples poses y métodos híbridos

Cuando varias poses o conformaciones del receptor sean plausibles, no deben concatenarse y promediarse sin criterio. Los esquemas LIE iterativos pueden combinar estados mediante pesos de tipo Boltzmann, pero esos pesos dependen de los parámetros del modelo y exigen calibración iterativa.

También se han propuesto métodos híbridos que combinan LIE con energías de solvatación alquímicas. Pueden mejorar la representación del estado libre o permitir estrategias de anclaje, pero no convierten automáticamente un cálculo LIE convencional en una energía libre rigurosa. Cada término adicional, coeficiente y protocolo debe calibrarse como parte del mismo modelo y validarse fuera del conjunto de entrenamiento.

## Errores frecuentes

- Usar una sola simulación del complejo y omitir el ligando libre.
- Copiar **-Elj** y **-Eqq** de otro ligando.
- Promediar coeficientes tomados de artículos incompatibles.
- Mezclar estados de protonación o parámetros no enlazantes entre los dos estados.
- Confundir **Coul-SR** con la energía electrostática total bajo PME.
- Usar grupos superpuestos o dejar átomos fuera de **LIG + Environment**.
- Interpretar cada marco de una trayectoria como una muestra independiente.
- Seleccionar retrospectivamente el intervalo que produce el resultado esperado.
- Reportar demasiadas cifras significativas sin incertidumbre.
- Presentar una estimación con coeficientes predeterminados como afinidad absoluta validada.

## Qué debe informarse

Un resultado LIE reproducible debe incluir: versión de GROMACS, campo de fuerzas, modelo de agua, estados de protonación, parámetros electrostáticos y de dispersión, composición de los grupos, duración descartada y analizada, número de réplicas, promedios libre y unido, coeficientes e intercepto, procedimiento de calibración, métricas de validación, incertidumbre y dominio de aplicabilidad.

### Fuentes

1. [gmx lie — documentación de GROMACS 2026.3](https://manual.gromacs.org/current/onlinehelp/gmx-lie.html)
2. [Interacciones de energía libre — manual de referencia de GROMACS](https://manual.gromacs.org/current/reference-manual/functions/free-energy-interactions.html)
3. [Recent Developments in Linear Interaction Energy Based Binding Free Energy Calculations](https://www.frontiersin.org/journals/molecular-biosciences/articles/10.3389/fmolb.2020.00114/full)
4. [Combined Linear Interaction Energy and Alchemical Solvation Free-Energy Approach](https://pubs.acs.org/jctcce/article/16/2/1300/606208/Combined-Linear-Interaction-Energy-and-Alchemical)
5. [A Comparative Linear Interaction Energy and MM/PBSA Study](https://pubs.acs.org/jcisd8/article/59/9/4018/987937/A-Comparative-Linear-Interaction-Energy-and-MM)


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
