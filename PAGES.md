# GitHub Pages: publicación y navegación

Este repositorio **ya dispone de un sitio Jekyll y publicación automática** mediante `.github/workflows/pages.yml`. Se mantienen ambas tecnologías: no es necesario migrar a MkDocs para tener un sitio navegable.

## Configuración en GitHub

1. Entrar en **Settings → Pages**.
2. En **Build and deployment → Source** elegir **GitHub Actions** (no `Deploy from a branch`). El workflow existente utiliza `actions/jekyll-build-pages`, `upload-pages-artifact` y `deploy-pages`.
3. Mantener HTTPS y el dominio predeterminado.
4. Fusionar el PR en `main`. Un push a `main` publica automáticamente; también puede ejecutarse manualmente desde **Actions → Publicar manual en GitHub Pages → Run workflow**.

URL prevista: https://juanjosecas.github.io/manual-gromacs/

El workflow existente ya se había ejecutado correctamente según el historial de GitHub Actions de septiembre de 2026. No se modificaron sus acciones ni permisos.

## Navegación

- **Manual completo:** carga íntegra de `manual.md`, con tabla de contenido automática a partir de encabezados.
- **Guía tutorial:** itinerarios de simulación según objetivo experimental.
- **Explorar temas:** tarjetas que llevan a secciones concretas del manual.
- **Buscar una sección:** filtro de encabezados de la página actual, no buscador de texto completo. Para texto completo, usar la búsqueda del navegador (`Ctrl+F`).

La edición de `manual.md` actualiza la web en el siguiente despliegue, sin generar índices manuales de capítulos. Las tarjetas temáticas son una selección curada: deben actualizarse cuando se agregan nuevos grandes temas o se renombran secciones.

## Alcance

Este PR modifica solo la navegación web, el índice lateral y los estilos. No altera la metodología científica ni los comandos del manual. Los fragmentos de código incrustados siguen siendo contenido documental, no se ejecutan durante el despliegue.

Los vínculos entre páginas se construyen con `relative_url` para respetar el prefijo `/manual-gromacs/`; el JavaScript preserva los IDs originales del generador Markdown antes de asignar identificadores faltantes.

La compilación y la publicación deben comprobarse en GitHub Actions después de fusionar el PR.
