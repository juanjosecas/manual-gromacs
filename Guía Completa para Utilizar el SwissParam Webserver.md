# Guía Completa para Utilizar el SwissParam Webserver

¡Bienvenidos a esta guía completa sobre cómo utilizar el SwissParam Webserver para llevar a cabo la parametrización de moléculas! Ya sea que seas un farmacéutico experto o simplemente estés interesado en el campo de la farmacia y la química computacional, esta herramienta te será de gran utilidad.

**Nota Importante**: Asegúrate de tener `curl` instalado en tu sistema antes de comenzar.

Instalar `curl` en las distribuciones GNU/Linux más comunes es bastante sencillo. Aquí te proporciono los comandos específicos para algunas de las distribuciones más populares:

### Debian y Ubuntu:

```bash
sudo apt-get update
sudo apt-get install curl
```

### Fedora:

```bash
sudo dnf install curl
```

### CentOS:

```bash
sudo yum install curl
```

### Arch Linux:

```bash
sudo pacman -S curl
```

### openSUSE:

```bash
sudo zypper install curl
```

### Nota Importante:

1. Asegúrate de tener privilegios de superusuario (root) o usar el comando `sudo` según sea necesario.
2. Dependiendo de la distribución y la configuración de tu sistema, es posible que necesites ejecutar estos comandos como superusuario (root) o usando `sudo`.

Después de ejecutar el comando correspondiente a tu distribución, `curl` debería estar instalado y listo para su uso en tu sistema GNU/Linux. Puedes verificar si `curl` se instaló correctamente ejecutando el siguiente comando:

```bash
curl --version
```

Esto mostrará la versión de `curl` instalada en tu sistema.

### Paso 1: Verificar que el Servidor Esté en Funcionamiento

Antes de comenzar, es importante asegurarse de que el servidor esté en funcionamiento. Para hacerlo, sigue estos pasos:

1. Abre tu terminal y ejecuta el siguiente comando:

```bash
curl -s dev.swissparam.ch:5678/
```

**Nota**: Si el servidor está funcionando, recibirás un mensaje "Hello World!". Si no, asegúrate de contactar al equipo de SwissParam.

### Paso 2: Iniciar una Parametrización

#### a. Molécula Pequeña No Covalente

Si deseas parametrizar una molécula pequeña no covalente, sigue estos pasos:

1. Asegúrate de tener el archivo Mol2 de tu molécula listo. Puede tener cualquier nombre.

2. Ejecuta el siguiente comando para iniciar la parametrización (reemplaza `molecule.mol2` con el nombre de tu archivo Mol2):

```bash
curl -s -F "myMol2=@molecule.mol2" "dev.swissparam.ch:5678/startparam?approach=both"
```

**Nota**: Si tu archivo Mol2 no contiene hidrógenos y deseas protonar la molécula a pH 7.4, agrega la opción `addH` al comando.

3. Si prefieres usar SMILES en lugar de un archivo Mol2, puedes hacerlo de esta manera:

```bash
curl -s -g "dev.swissparam.ch:5678/startparam?mySMILES=NC(=N)NC1=CC=CC=C1&approach=both"
```

Recibirás un número de sesión que te permitirá verificar el estado de la parametrización más adelante.

#### b. Molécula Pequeña Covalente

Si necesitas parametrizar una molécula pequeña covalente, sigue estos pasos:

1. Asegúrate de tener el archivo Mol2 de tu molécula listo. Puede tener cualquier nombre.

2. Ejecuta el siguiente comando, reemplazando los argumentos según corresponda:

```bash
curl -s -F "myMol2=@molecule.mol2" "dev.swissparam.ch:5678/startparam?ligsite=l&reaction=r&protes=p&topology=t"
```

**Nota**: Puedes especificar el enfoque CHARMM22/27 agregando "&c22" o "&c27" al comando.

### Paso 3: Verificar el Estado de una Parametrización

Puedes verificar el estado de la parametrización utilizando el número de sesión que recibiste al enviar la parametrización. Ejecuta el siguiente comando:

```bash
curl -s "dev.swissparam.ch:5678/checksession?sessionNumber=TU_NUMERO_DE_SESION"
```

Este comando te proporcionará información sobre si la parametrización está en cola, en ejecución o finalizada.

### Paso 4: Cancelar una Parametrización

Si necesitas cancelar una parametrización en curso o en cola, puedes hacerlo con el siguiente comando:

```bash
curl -s -F "myMol2=@molecule.mol2" "dev.swissparam.ch:5678/startparam"
```

Luego, verifica el estado de la sesión y, si está en curso, puedes cancelarla utilizando el comando correspondiente.

### Paso 5: Obtener los Resultados de una Parametrización

Una vez que hayas confirmado que tu trabajo está finalizado, puedes obtener los resultados con el siguiente comando:

```bash
curl -s "dev.swissparam.ch:5678/retrievesession?sessionNumber=TU_NUMERO_DE_SESION"
```

Este comando te permitirá descargar un archivo gzip con los resultados.
