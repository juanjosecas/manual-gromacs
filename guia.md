---
layout: default
title: "Guía práctica de GROMACS"
description: "Entrada tutorial y orientada a tareas para el Manual de referencia de GROMACS."
permalink: /guia/
---

# Guía práctica de GROMACS

Esta página propone una forma alternativa de recorrer el manual: en lugar de avanzar capítulo por capítulo, parte de una pregunta experimental y conduce hasta un resultado verificable. El [manual completo]({{ '/' | relative_url }}) conserva la teoría, las opciones, los comandos y los casos especiales; esta guía funciona como mapa de trabajo.

> **Principio de uso:** no continúe una simulación porque el comando terminó sin errores. Continúe cuando la salida de la etapa anterior cumpla un criterio físico y técnico explícito.

## Elegir la ruta adecuada

| Objetivo | Ruta recomendada | Decisión crítica |
| --- | --- | --- |
| Aprender el flujo básico | [Proteína monomérica en agua]({{ '/' | relative_url }}#dinamica-de-una-proteina-en-agua) | Campo de fuerza, protonación y calidad estructural |
| Simular un complejo | [Una proteína y un ligando]({{ '/' | relative_url }}#caso-1-proteina-1-ligando) | Parametrización coherente del ligando |
| Trabajar con varias cadenas o ligandos | [Sistemas multimoleculares]({{ '/' | relative_url }}#multiples-moleculas-de-ligandos-y-de-proteinas) | Orden de moléculas, índices y restricciones |
| Construir una interfaz líquida | [Sistema 1-octanol–agua]({{ '/' | relative_url }}#sistema-bifasico) | Densidad, dimensiones y equilibrio de fases |
| Simular una proteína de membrana | [Bicapa y acuaporina]({{ '/' | relative_url }}#proteina-de-membrana-construccion-de-una-bicapa-e-insercion-de-una-acuaporina) | Composición lipídica, orientación y presión |
| Calcular energía libre de solvatación | [FEP, BAR y ventanas λ]({{ '/' | relative_url }}#energia-libre-de-perturbacion-energia-libre-de-solvatacion) | Ciclo termodinámico y solapamiento entre estados |
| Estimar energía de unión por estado final | [gmx_MMPBSA]({{ '/' | relative_url }}#energia-de-union-mediante-gmx_mmpbsa) | Muestreo, dieléctricos y alcance del método |
| Aplicar un modelo LIE | [Interacción energética lineal]({{ '/' | relative_url }}#interaccion-energetica-lineal-linear-interaction-energy-lie) | Calibración de coeficientes y estados de referencia |

Si es la primera vez que se utiliza GROMACS, conviene completar primero el caso de una proteína en agua. Ese sistema permite aprender el flujo común sin introducir simultáneamente la parametrización de una molécula no estándar.

## El flujo común

Casi todos los tutoriales del manual pueden leerse mediante la misma secuencia:

1. **Definir la pregunta.** Especificar qué observable responderá la pregunta y qué escala temporal puede ser necesaria.
2. **Preparar el modelo.** Resolver protonación, residuos faltantes, moléculas no estándar, cofactores, orientación y composición.
3. **Construir la topología.** Mantener un único campo de fuerza compatible para todas las especies o documentar rigurosamente cualquier conversión.
4. **Construir el entorno.** Definir caja, solvente, membrana, iones y concentración.
5. **Minimizar.** Eliminar contactos desfavorables sin interpretar esta etapa como equilibrio.
6. **Equilibrar.** Relajar temperatura, presión, densidad y restricciones de forma gradual.
7. **Producir.** Ejecutar segmentos recuperables, conservar puntos de control y registrar la versión y el comando.
8. **Preparar la trayectoria.** Corregir condiciones periódicas antes de medir movimientos globales o contactos.
9. **Analizar.** Usar observables relacionados con la hipótesis, réplicas e incertidumbre.
10. **Decidir.** Aceptar, extender o repetir la simulación según criterios definidos antes del análisis.

## Tutorial mínimo: proteína en agua

### Resultado esperado

Al terminar se debe disponer de una topología reproducible, una trayectoria sin artefactos periódicos evidentes y un conjunto mínimo de controles estructurales y termodinámicos.

### Recorrido

1. Compruebe la instalación con la [verificación final]({{ '/' | relative_url }}#verificacion-final).
2. Defina la entidad biológica y revise la estructura según [qué estructura se simulará]({{ '/' | relative_url }}#1-definir-que-estructura-se-simulara).
3. Elija conjuntamente [campo de fuerza y modelo de agua]({{ '/' | relative_url }}#2-campo-de-fuerza-y-modelo-de-agua).
4. Genere la topología, la caja, el solvente y los iones.
5. Realice minimización, NVT y NPT. No use la producción para corregir una equilibración deficiente.
6. Inicie la producción únicamente después de aplicar el [criterio para continuar]({{ '/' | relative_url }}#27-criterio-para-continuar).
7. Ejecute los [controles estructurales mínimos]({{ '/' | relative_url }}#14-controles-estructurales-minimos).
8. Si la pregunta requiere movimientos colectivos, continúe con [PCA o dinámica esencial]({{ '/' | relative_url }}#18-fundamento-de-pca-o-dinamica-esencial).

### Puntos de control

| Etapa | Comprobar antes de avanzar |
| --- | --- |
| Estructura | Identidad biológica, residuos faltantes, estados de protonación, enlaces especiales y cofactores |
| Topología | Carga total, número y orden de moléculas, campo de fuerza y modelo de agua |
| Minimización | Ausencia de fallos, fuerza máxima razonable y geometría sin contactos anómalos |
| NVT | Temperatura estable después del transitorio |
| NPT | Densidad y volumen estabilizados; caja físicamente razonable |
| Producción | Archivo de punto de control, energía sin discontinuidades y rendimiento documentado |
| Análisis | Trayectoria corregida, selección de átomos explícita, intervalo de descarte e incertidumbre |

## Tutorial central: proteína–ligando

### La decisión que organiza todo el protocolo

La topología del ligando debe pertenecer a la misma familia del campo de fuerza usada para la proteína. No es seguro mezclar parámetros sólo porque GROMACS pueda leer los archivos.

| Estrategia | Familia prevista | Cuándo usarla |
| --- | --- | --- |
| [ACPYPE]({{ '/' | relative_url }}#parametrizacion-del-ligando-con-acpype) | AMBER/GAFF o GAFF2 | Flujo basado en una familia AMBER y moléculas compatibles con el dominio de parametrización |
| [SwissParam]({{ '/' | relative_url }}#alternativa-parametrizacion-con-swissparam-para-charmm36) | CHARMM36/CGenFF aproximado | Prototipado dentro de un flujo CHARMM36, con validación de penalizaciones y parámetros |
| Parametrización específica validada | Familia correspondiente | Producción cuando existen parámetros oficiales, experimentales o de mayor calidad |

### Recorrido

1. Defina forma química, tautómero, protonación, estereoquímica y carga del ligando.
2. Prepare la proteína por separado y documente las decisiones químicas.
3. Parametrice el ligando y examine carga total, tipos atómicos, términos ausentes y geometría.
4. Construya el complejo sin alterar el orden de átomos esperado por las topologías.
5. Añada caja, solvente e iones; verifique la sección `[ molecules ]`.
6. Aplique restricciones de posición sólo durante las etapas que las requieran.
7. Complete minimización, NVT, NPT y producción con criterios de avance.
8. Corrija las condiciones periódicas antes del análisis.
9. Combine estabilidad global con observables locales: RMSD, contactos, distancias funcionales, puentes de hidrógeno y agua estructural.
10. Trate MM/PBSA, LIE o FEP como protocolos adicionales, no como sustitutos de una trayectoria bien equilibrada.

## Tutorial especializado: proteína de membrana

Una membrana introduce más decisiones que una proteína soluble: orientación, composición, hidratación, iones, estado de fase, acoplamiento de presión y relajación de los lípidos.

### Recorrido recomendado

1. Defina el fenómeno: estabilidad, permeación, selectividad, unión lipídica o respuesta a voltaje.
2. Prepare y oriente la proteína respecto del eje normal de la membrana.
3. Elija una composición lipídica que represente el sistema experimental.
4. Construya el sistema mediante el flujo de [CHARMM-GUI Membrane Builder]({{ '/' | relative_url }}#10-construccion-en-charmm-gui-membrane-builder).
5. Inspeccione todos los archivos antes de ejecutar scripts.
6. Use la [equilibración escalonada]({{ '/' | relative_url }}#14-equilibracion-escalonada-sin-csh) y mantenga el acoplamiento de presión apropiado para bicapas.
7. Considere [HMR]({{ '/' | relative_url }}#17-reparticion-de-masa-de-hidrogeno-hmr) sólo después de validar el sistema convencional; el paso de integración mayor no es gratuito.
8. Analice proteína y bicapa: área por lípido, espesor, orden, difusión, inclinación, hidratación y propiedades del poro.
9. Use réplicas y evalúe convergencia antes de extraer mecanismos.

## Núcleo de análisis reutilizable

Los mismos principios se aplican a proteínas solubles, complejos y membranas:

- Elimine saltos periódicos y centre el sistema con una selección reproducible.
- Separe estabilidad de convergencia: un RMSD estable no demuestra muestreo suficiente.
- Use RMSF, estructura secundaria, radio de giro y SASA para describir cambios complementarios.
- Defina contactos mediante umbrales explícitos y analice su ocupación, no sólo una imagen representativa.
- Compare bloques temporales y réplicas independientes.
- Informe promedio, dispersión, tamaño de muestra efectivo cuando corresponda y período descartado.
- Relacione cada gráfico con una pregunta; no acumule observables sin interpretación.

Para el procedimiento detallado, consulte [diseñar el análisis antes de calcular observables]({{ '/' | relative_url }}#15-disenar-el-analisis-antes-de-calcular-observables) y [preparación de la trayectoria]({{ '/' | relative_url }}#preparacion-de-la-trayectoria).

## Estructura de carpetas sugerida

```text
proyecto/
├── 00_entrada/
├── 01_parametros/
├── 02_construccion/
├── 03_minimizacion/
├── 04_equilibracion/
├── 05_produccion/
├── 06_analisis/
└── registro/
```

No es obligatorio usar estos nombres. Lo importante es separar entradas originales, archivos generados, etapas de simulación y resultados de análisis. En `registro/` conviene conservar versión de GROMACS, comandos, archivos MDP, semillas, advertencias aceptadas y procedencia de los parámetros.

## Cómo leer el manual según la experiencia

### Primera simulación

Empiece por instalación, proteína monomérica en agua y controles mínimos. Después repita el flujo con un ligando sencillo.

### Uso habitual

Use esta guía como lista de decisiones y el índice lateral del manual como referencia de comandos, ecuaciones y errores frecuentes.

### Desarrollo de protocolos

Trabaje desde la pregunta científica hacia atrás: observable, muestreo necesario, modelo físico, construcción y validación. Añada pruebas pequeñas antes de comprometer recursos de producción.

## Lista de salida reproducible

Antes de considerar terminado un trabajo, conserve al menos:

- estructura inicial y procedencia;
- topologías e inclusiones exactamente utilizadas;
- archivos MDP;
- versión completa de GROMACS y plataforma;
- comandos de preprocesamiento y ejecución;
- advertencias y justificación de las aceptadas;
- puntos de control;
- trayectoria o instrucciones para reconstruirla;
- selección de grupos usada en cada análisis;
- scripts, intervalos temporales y unidades;
- réplicas, semillas y criterio de convergencia.

Esta organización no reemplaza el manual original. Lo convierte en una referencia consultable y ofrece, en paralelo, una ruta tutorial con metas y controles de avance.
