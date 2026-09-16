(() => {
  const article = document.querySelector("article");
  const toc = document.getElementById("toc");
  const search = document.getElementById("toc-search");
  const sidebar = document.getElementById("sidebar");
  const menu = document.getElementById("menu-button");
  const backdrop = document.getElementById("backdrop");
  if (!article || !toc) return;

  const normalize = (text) =>
    text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  const used = new Set();
  const slug = (text) => {
    const base = normalize(text).trim()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-") || "seccion";
    let id = base;
    let n = 2;
    while (used.has(id)) id = base + "-" + n++;
    used.add(id);
    return id;
  };

  const headings = [...article.querySelectorAll("h2, h3")];
  const list = document.createElement("ul");
  headings.forEach((heading) => {
    heading.id = slug(heading.textContent);
    const item = document.createElement("li");
    item.className = heading.tagName.toLowerCase();
    const link = document.createElement("a");
    link.href = "#" + heading.id;
    link.textContent = heading.textContent.trim();
    link.dataset.search = normalize(link.textContent);
    item.appendChild(link);
    list.appendChild(item);
  });
  toc.appendChild(list);

  search?.addEventListener("input", () => {
    const query = normalize(search.value.trim());
    list.querySelectorAll("li").forEach((item) => {
      item.hidden = query && !item.firstElementChild.dataset.search.includes(query);
    });
  });

  article.querySelectorAll("table").forEach((table) => {
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrap";
    wrapper.tabIndex = 0;
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  article.querySelectorAll("pre").forEach((pre) => {
    const button = document.createElement("button");
    button.className = "copy";
    button.type = "button";
    button.textContent = "Copiar";
    button.addEventListener("click", async () => {
      const code = pre.querySelector("code")?.textContent || pre.textContent;
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = "Copiado";
      } catch {
        button.textContent = "Error";
      }
      setTimeout(() => button.textContent = "Copiar", 1400);
    });
    pre.appendChild(button);
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const current = entries.find((entry) => entry.isIntersecting);
      if (!current) return;
      toc.querySelectorAll("a").forEach((link) => link.classList.remove("active"));
      toc.querySelector('a[href="#' + CSS.escape(current.target.id) + '"]')?.classList.add("active");
    }, { rootMargin: "-15% 0px -75% 0px" });
    headings.forEach((heading) => observer.observe(heading));
  }

  const openMenu = (open) => {
    sidebar.classList.toggle("open", open);
    menu.setAttribute("aria-expanded", String(open));
    backdrop.hidden = !open;
  };
  menu?.addEventListener("click", () => openMenu(!sidebar.classList.contains("open")));
  backdrop?.addEventListener("click", () => openMenu(false));
  toc.addEventListener("click", () => openMenu(false));
})();
