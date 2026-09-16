(() => {
  const article = document.querySelector(".manual article");
  const toc = document.getElementById("table-of-contents");
  const search = document.getElementById("toc-search");
  const sidebar = document.getElementById("sidebar");
  const menuButton = document.querySelector(".menu-button");
  const backdrop = document.querySelector(".sidebar-backdrop");

  if (!article || !toc) return;

  const normalize = (value) =>
    value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  const uniqueId = (heading, used) => {
    const original = heading.id || heading.textContent;
    let base = normalize(original)
      .trim()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-") || "seccion";
    let id = base;
    let counter = 2;
    while (used.has(id)) id = base + "-" + counter++;
    used.add(id);
    return id;
  };

  const headings = Array.from(article.querySelectorAll("h2, h3"));
  const usedIds = new Set();
  const list = document.createElement("ul");

  headings.forEach((heading) => {
    heading.id = uniqueId(heading, usedIds);
    const label = heading.textContent.trim();
    const item = document.createElement("li");
    item.className = "toc-" + heading.tagName.toLowerCase();
    const link = document.createElement("a");
    link.href = "#" + heading.id;
    link.textContent = label;
    link.dataset.search = normalize(label);
    item.appendChild(link);
    list.appendChild(item);

    const anchor = document.createElement("a");
    anchor.className = "heading-anchor";
    anchor.href = "#" + heading.id;
    anchor.setAttribute("aria-label", "Enlace permanente a " + label);
    anchor.textContent = "#";
    heading.appendChild(anchor);
  });

  toc.replaceChildren(list);

  search?.addEventListener("input", () => {
    const query = normalize(search.value.trim());
    let visible = 0;
    list.querySelectorAll("li").forEach((item) => {
      const match = !query || item.firstElementChild.dataset.search.includes(query);
      item.hidden = !match;
      if (match) visible++;
    });

    toc.querySelector(".toc-empty")?.remove();
    if (!visible) {
      const empty = document.createElement("p");
      empty.className = "toc-empty";
      empty.textContent = "No se encontraron secciones.";
      toc.appendChild(empty);
    }
  });

  document.querySelectorAll(".manual table").forEach((table) => {
    if (table.parentElement?.classList.contains("table-wrapper")) return;
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrapper";
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", "Tabla desplazable");
    wrapper.tabIndex = 0;
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  document.querySelectorAll(".manual pre").forEach((pre) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.textContent = "Copiar";
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(pre.textContent);
        button.textContent = "Copiado";
      } catch {
        button.textContent = "No se pudo copiar";
      }
      window.setTimeout(() => {
        button.textContent = "Copiar";
      }, 1600);
    });
    pre.appendChild(button);
  });

  if ("IntersectionObserver" in window) {
    const links = new Map(
      headings.map((heading) => [
        heading.id,
        toc.querySelector('a[href="#' + CSS.escape(heading.id) + '"]')
      ])
    );
    const observer = new IntersectionObserver(
      (entries) => {
        const current = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (!current) return;
        links.forEach((link) => link?.classList.remove("active"));
        links.get(current.target.id)?.classList.add("active");
      },
      { rootMargin: "-15% 0px -75% 0px" }
    );
    headings.forEach((heading) => observer.observe(heading));
  }

  const setMenu = (open) => {
    sidebar?.classList.toggle("open", open);
    menuButton?.setAttribute("aria-expanded", String(open));
    if (backdrop) backdrop.hidden = !open;
  };

  menuButton?.addEventListener("click", () => {
    setMenu(!sidebar.classList.contains("open"));
  });
  backdrop?.addEventListener("click", () => setMenu(false));
  toc.addEventListener("click", (event) => {
    if (event.target.closest("a") && window.matchMedia("(max-width: 900px)").matches) {
      setMenu(false);
    }
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenu(false);
  });
})();
