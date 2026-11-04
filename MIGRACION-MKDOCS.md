# Migración a MkDocs Material

Este repositorio conserva **manual.md** y **guia.md** como fuentes originales. El script `scripts/build_docs.py` crea `docs/` y divide el manual en 10 capítulos a partir de encabezados existentes, sin modificar su contenido científico ni sus bloques de código.

## Previsualización

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-docs.txt
python scripts/build_docs.py
mkdocs serve
```

La web usa navegación por capítulos, búsqueda de texto completo, copia de código, tablas y ecuaciones MathJax.

## Publicación

En **Settings → Pages → Build and deployment → Source**, seleccionar **GitHub Actions**. El workflow `.github/workflows/pages.yml` compila cada cambio en `main` y publica automáticamente en https://juanjosecas.github.io/manual-gromacs/. Los pull requests solo construyen el sitio, sin publicarlo.

El workflow anterior de Jekyll se sustituye; los archivos `_config.yml`, `_layouts/`, `assets/` e `index.md` antiguos quedan en el repositorio como legado y no se usan para compilar MkDocs. El contenido publicado se genera exclusivamente desde `docs/`.

## Compatibilidad de enlaces

La guía se convierte automáticamente de enlaces Liquid/Jekyll a rutas Markdown relativas a capítulos, manteniendo identificadores de secciones. **Los enlaces externos antiguos al manual raíz con fragmentos `/#...` pueden dejar de funcionar**, porque los capítulos ahora tienen rutas propias. Esta migración no incluye redirecciones para todos los fragmentos heredados.

La división es por títulos de capítulos, no por números de línea. Si se renombra o elimina un título utilizado como punto de corte, el generador falla explícitamente en vez de publicar capítulos incompletos.

La generación de documentación no ejecuta GROMACS ni verifica los resultados de los protocolos.
