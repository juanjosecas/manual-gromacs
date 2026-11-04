---
layout: default
title: "Explorar temas · Manual de GROMACS"
description: "Accesos directos a protocolos de dinámica molecular, instalación, membranas y cálculos de energía libre."
permalink: /temas/
---

# Explorar el manual por temas

El manual incluye procedimientos de GROMACS 2026.3, preparación de sistemas y análisis de trayectorias. Elegí un bloque para ir directamente al capítulo correspondiente.

La [guía práctica]({{ '/guia/' | relative_url }}) organiza los protocolos como recorridos experimentales. El [manual íntegro]({{ '/' | relative_url }}) conserva los procedimientos y explicaciones originales.

<div class="topic-grid">
  <a class="topic-card" href="{{ '/' | relative_url }}#instalacion-de-gromacs"><strong>Instalación y entorno</strong><span>Linux, GPU, MPI, Docker, gmxapi y verificación.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#caso-1-proteina---1-ligando"><strong>Proteína–ligando</strong><span>Parámetros, topologías, minimización, NVT, NPT y producción.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#dinamica-de-una-proteina-en-agua"><strong>Proteína en solución</strong><span>Preparación del sistema, trayectoria, calidad y PCA.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#multiples-moleculas-de-ligandos-y-de-proteinas"><strong>Sistemas multimoleculares</strong><span>Varias cadenas, múltiples ligandos e índices.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#sistema-bifasico"><strong>Interfaz octanol–agua</strong><span>Dos fases, equilibración y propiedades.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#proteina-de-membrana-construccion-de-una-bicapa-e-insercion-de-una-acuaporina"><strong>Proteínas de membrana</strong><span>Bicapas, acuaporinas, presión y análisis lipídico.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#energia-libre-de-perturbacion-energia-libre-de-solvatacion"><strong>FEP y energía libre</strong><span>Ventanas λ, BAR y solvatación.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#energia-de-union-mediante-gmx_mmpbsa"><strong>MM/PBSA</strong><span>gmx_MMPBSA, selección de frames e incertidumbre.</span></a>
  <a class="topic-card" href="{{ '/' | relative_url }}#interaccion-energetica-lineal-linear-interaction-energy-lie"><strong>LIE</strong><span>Interacciones energéticas y calibración.</span></a>
</div>

## Buscar por palabras

Usá el buscador de la barra lateral del **manual completo** para filtrar los títulos de capítulos y secciones. El filtro no busca dentro de los párrafos ni equivale a un índice de texto completo; para eso podés usar la búsqueda del navegador (`Ctrl+F`).

## Cómo se actualiza

Esta página enlaza las secciones existentes de `manual.md`. Cuando agregues nuevos capítulos al manual se publicarán automáticamente mediante GitHub Actions, pero las tarjetas de temas requieren incorporar el nuevo vínculo. La navegación lateral dentro del manual se construye automáticamente desde sus encabezados.
