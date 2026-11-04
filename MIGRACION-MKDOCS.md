# Migración a MkDocs Material

El contenido del manual está separado en **11 archivos editables** bajo `source/` (introducción y diez capítulos). `manual.md` permanece como copia histórica y **ya no se utiliza para generar la web**. `guia.md` sigue siendo la fuente de la guía práctica. `scripts/build_docs.py` construye `docs/` a partir de `source/` sin alterar el contenido científico ni los bloques de código.

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

Los archivos de `source/` se procesan en un orden explícito. Los límites de capítulo siguen identificándose por encabezados; si se renombra o elimina un encabezado utilizado como punto de corte, el generador falla en vez de publicar capítulos incompletos. Editar `source/<capitulo>.md` para cambiar el manual; **no editar `manual.md` esperando cambios en Pages**.

La generación de documentación no ejecuta GROMACS ni verifica los resultados de los protocolos.
