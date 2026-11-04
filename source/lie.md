# Interacción energética lineal (Linear Interaction Energy, LIE)

La **energía de interacción lineal** (LIE) es un método de estado final para estimar afinidades de unión. Requiere muestrear explícitamente dos estados mediante dinámica molecular:

1. el ligando unido al receptor y rodeado por solvente e iones;
2. el mismo ligando libre en solvente, con el mismo estado de protonación y un protocolo compatible.

LIE es más económico que una transformación alquímica completa porque no introduce estados intermedios de $\lambda$. A cambio, es un modelo semiempírico: no debe interpretarse como una energía libre rigurosa ni utilizarse con coeficientes tomados arbitrariamente de otros sistemas. Su utilidad principal es comparar ligandos relacionados para un mismo receptor y dentro del dominio químico e interaccional empleado para calibrar el modelo.

## Fundamento teórico

En la forma más habitual,

$$
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
$$

Aquí:

- $L$ es el ligando y $E$ es su entorno;
- en el estado unido, el entorno incluye receptor, agua, iones y cualquier cofactor que no forme parte del ligando;
- en el estado libre, el entorno incluye agua e iones;
- los corchetes $\langle\cdots\rangle$ representan promedios de conjunto, aproximados mediante promedios temporales sobre trayectorias equilibradas;
- $\alpha$ y $\beta$ son coeficientes adimensionales para las contribuciones de Lennard-Jones y electrostática;
- $\gamma$ es un intercepto opcional, expresado en kJ mol$^{-1}$.

La contribución electrostática procede de una aproximación de respuesta lineal. El valor histórico $\beta=0{,}5$ corresponde al caso ideal de respuesta lineal, pero no es universal. La documentación de GROMACS 2026.3 conserva como valores predeterminados $\alpha=0{,}181$ y $\beta=0{,}5$; deben considerarse valores iniciales o de referencia, no una validación del modelo para cualquier ligando.

LIE no calcula de manera explícita todos los términos entrópicos, reorganizaciones internas, cambios conformacionales o contribuciones de estado estándar. Se presupone que una parte de esos efectos queda representada de forma efectiva por los coeficientes y el intercepto. Por eso un resultado aislado obtenido con los valores predeterminados debe describirse como **estimación LIE no calibrada**.

## Unidades y comparación con datos experimentales

GROMACS informa las energías de interacción en **kJ mol$^{-1}$**. Como $\alpha$ y $\beta$ son adimensionales, $\Delta G_{\mathrm{bind}}^{\mathrm{LIE}}$ y $\gamma$ conservan esas unidades.

$$
1\ \mathrm{kcal\ mol^{-1}}=4{,}184\ \mathrm{kJ\ mol^{-1}}.
$$

Para transformar una constante experimental de disociación en una energía libre estándar,

$$
\Delta G^\circ_{\mathrm{bind}}
=
RT\ln\left(\frac{K_d}{C^\circ}\right)
=
-RT\ln\left(K_a C^\circ\right),
$$

donde $C^\circ=1\ \mathrm{mol\ L^{-1}}$. La razón dentro del logaritmo debe ser adimensional. Deben registrarse la temperatura, la fuerza iónica, el pH y el estado de protonación del ligando; comparar directamente valores obtenidos bajo condiciones experimentales distintas puede introducir un error mayor que el que se intenta modelar.

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

```bash
gmx select -s md_bound.tpr -on lie_bound.ndx \
  -select '"LIG" resname LIG; "Environment" not resname LIG'
```

Para el ligando libre:

```bash
gmx select -s md_free.tpr -on lie_free.ndx \
  -select '"LIG" resname LIG; "Environment" not resname LIG'
```

Se debe reemplazar **LIG** por el nombre real del residuo o por una selección inequívoca. Si existen varias moléculas con ese mismo nombre, hay que decidir si constituyen un único ligando termodinámico o si deben analizarse por separado. Verifique siempre los grupos:

```bash
gmx check -f md_bound.xtc
gmx make_ndx -f md_bound.tpr -n lie_bound.ndx
```

Dentro de una copia del MDP de producción, agregue:

```ini
; Grupos no superpuestos que cubren el sistema
energygrps = LIG Environment
```

El resto del MDP usado para recalcular energías debe conservar el campo de fuerzas, los cortes, las reglas de dispersión, el modificador de potencial y el tratamiento electrostático de la simulación de producción. Cambiar esos parámetros durante el análisis define otro descriptor y rompe la comparabilidad con un modelo calibrado previamente.

### Limitación importante de PME

Los términos que utiliza **gmx lie** son, entre otros, **Coul-SR** y **LJ-SR**. La parte recíproca de PME no se descompone en pares de grupos como una energía ligando–entorno independiente. Por tanto, una LIE basada en esos términos es dependiente del protocolo y no contiene una asignación completa de la electrostática de largo alcance al ligando.

Esto no significa que deba eliminarse PME de una simulación moderna. Significa que todos los ligandos, los dos estados y el conjunto de calibración deben tratarse de manera idéntica, y que la limitación debe documentarse. Recalcular con reacción de campo u otro modelo electrostático sólo es defendible si todo el modelo LIE fue calibrado y validado con ese mismo protocolo.

## Obtención de los archivos EDR para LIE

Incluir grupos de energía durante una producción puede limitar la aceleración por GPU. Una alternativa práctica es recalcular las energías sobre las trayectorias ya producidas. Genere TPR de análisis separados para el complejo y el ligando libre:

```bash
gmx grompp -f lie_bound.mdp -c md_bound.gro -t md_bound.cpt \
  -p topol_bound.top -n lie_bound.ndx -o lie_bound.tpr

gmx grompp -f lie_free.mdp -c md_free.gro -t md_free.cpt \
  -p topol_free.top -n lie_free.ndx -o lie_free.tpr
```

Luego efectúe el recálculo en CPU:

```bash
gmx mdrun -s lie_bound.tpr -rerun md_bound.xtc \
  -deffnm lie_bound -nb cpu -pme cpu

gmx mdrun -s lie_free.tpr -rerun md_free.xtc \
  -deffnm lie_free -nb cpu -pme cpu
```

**mdrun -rerun** evalúa la energía de cada marco de la trayectoria suministrada; no genera un nuevo muestreo. Los archivos TPR deben conservar la misma topología, orden de átomos y parámetros no enlazantes usados para producir cada trayectoria. Los valores cinéticos y de temperatura obtenidos en un recálculo de este tipo no son relevantes para LIE.

Antes de continuar, compruebe que existen los términos esperados:

```bash
gmx energy -f lie_free.edr -o /dev/null
gmx energy -f lie_bound.edr -o /dev/null
```

Deben aparecer nombres equivalentes a:

```text
Coul-SR:LIG-Environment
LJ-SR:LIG-Environment
```

Si no aparecen, el TPR no contenía una definición válida de **energygrps** o el cálculo se ejecutó con una ruta que no produjo la descomposición solicitada.

## Cálculo con gmx lie en GROMACS 2026

Primero obtenga los promedios del ligando libre en solvente. El inicio del intervalo productivo se expresa en picosegundos:

```bash
printf "Coul-SR:LIG-Environment\nLJ-SR:LIG-Environment\n0\n" | \
  gmx energy -f lie_free.edr -o free_interactions.xvg -b 20000
```

Tome de la salida los promedios **Average** y asígnelos, sin cambiar signos ni unidades:

```bash
FREE_COUL=-104.226
FREE_LJ=-183.449
```

Los números anteriores son únicamente ejemplos. No deben copiarse para otro ligando.

Calcule después la estimación sobre el estado unido:

```bash
gmx lie -f lie_bound.edr -o lie.xvg -b 20000 \
  -Elj "$FREE_LJ" -Eqq "$FREE_COUL" \
  -Clj 0.181 -Cqq 0.5 -ligand LIG
```

Significado de las opciones principales:

| Opción         | Significado                                        | Unidad                      |
| -------------- | -------------------------------------------------- | --------------------------- |
| **-Elj**       | Promedio LJ ligando–solvente del estado libre      | kJ mol$^{-1}$               |
| **-Eqq**       | Promedio Coulomb ligando–solvente del estado libre | kJ mol$^{-1}$               |
| **-Clj**       | Coeficiente $\alpha$                               | adimensional                |
| **-Cqq**       | Coeficiente $\beta$                                | adimensional                |
| **-ligand**    | Nombre del grupo de energía del ligando            | —                           |
| **-b**, **-e** | Inicio y final del intervalo analizado             | ps, de forma predeterminada |
| **-dt**        | Separación temporal entre marcos utilizados        | ps                          |

El archivo **lie.xvg** contiene la evolución de la estimación. No se debe elegir el comienzo del promedio sólo porque la curva “parece estable” a partir de un punto conveniente. El descarte debe establecerse antes de comparar ligandos o justificarse mediante diagnósticos de equilibrio y convergencia aplicados de manera uniforme.

También es recomendable extraer los cuatro promedios por separado y verificar manualmente la ecuación. Esto detecta con facilidad grupos invertidos, signos erróneos o valores libres copiados de otro sistema.

## Calibración de los coeficientes

Para predicción cuantitativa, construya una tabla con un conjunto de ligandos de afinidad experimental conocida:

| Ligando     | $\Delta V_{\mathrm{vdW}}$ | $\Delta V_{\mathrm{elec}}$ | $\Delta G^\circ_{\mathrm{exp}}$ |
| ----------- | -------------------------:| --------------------------:| -------------------------------:|
| compuesto 1 | unido − libre             | unido − libre              | kJ mol$^{-1}$                   |
| compuesto 2 | unido − libre             | unido − libre              | kJ mol$^{-1}$                   |

Ajuste entonces

$$
\Delta G^\circ_{\mathrm{exp}}
=
\alpha\Delta V_{\mathrm{vdW}}
+
\beta\Delta V_{\mathrm{elec}}
+
\gamma .
$$

No es correcto promediar valores de $\alpha$ o $\beta$ publicados para proteínas, campos de fuerzas o familias químicas diferentes. Con pocos compuestos, ajustar simultáneamente tres parámetros produce sobreajuste; en ese caso conviene fijar uno de los coeficientes con una justificación previa o ampliar el conjunto. Deben informarse, como mínimo, validación cruzada o conjunto externo, MAE, RMSE, correlación y dominio de aplicabilidad.

Una predicción nueva es más confiable cuando el ligando se parece al conjunto de calibración no sólo en estructura, sino también en sus patrones de interacción con el receptor. Un compuesto con carga, pose o química diferente puede estar fuera del dominio aunque su esqueleto molecular parezca similar.

## Convergencia e incertidumbre

Use series temporales y promedios por bloques para cada uno de los cuatro términos energéticos. Para réplicas independientes, informe la media entre réplicas y su incertidumbre; una trayectoria larga no sustituye necesariamente varias inicializaciones cuando existen poses o estados conformacionales separados.

Una aproximación útil para la propagación de la incertidumbre es

$$
\sigma^2_{\Delta G}
\approx
\alpha^2\sigma^2_{\Delta V_{\mathrm{vdW}}}
+
\beta^2\sigma^2_{\Delta V_{\mathrm{elec}}}
+
2\alpha\beta\operatorname{Cov}
\left(\Delta V_{\mathrm{vdW}},\Delta V_{\mathrm{elec}}\right).
$$

Esta expresión debe emplear errores de los promedios que tengan en cuenta la autocorrelación, no la desviación estándar de los marcos como si fueran observaciones independientes. Si $\alpha$, $\beta$ y $\gamma$ fueron ajustados, su incertidumbre también contribuye al error predictivo.

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
