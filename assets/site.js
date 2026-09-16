(() => {
  const article = document.querySelector("article");
  const toc = document.getElementById("toc");
  const search = document.getElementById("toc-search");
  const sidebar = document.getElementById("sidebar");
  const menu = document.getElementById("menu-button");
  const backdrop = document.getElementById("backdrop");
  const desktop = window.matchMedia("(min-width: 901px)");
  const sidebarKey = "manual-sidebar-collapsed";
  if (!article || !toc || !sidebar || !menu || !backdrop) return;

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
      item.hidden = Boolean(query) && !item.firstElementChild.dataset.search.includes(query);
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
      window.setTimeout(() => button.textContent = "Copiar", 1400);
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

  const setMobileMenu = (open) => {
    sidebar.classList.toggle("open", open);
    menu.setAttribute("aria-expanded", String(open));
    backdrop.hidden = !open;
  };

  const setDesktopSidebar = (collapsed) => {
    document.body.classList.toggle("sidebar-collapsed", collapsed);
    menu.setAttribute("aria-expanded", String(!collapsed));
    backdrop.hidden = true;
    try {
      localStorage.setItem(sidebarKey, collapsed ? "1" : "0");
    } catch {}
  };

  if (desktop.matches) {
    let collapsed = false;
    try {
      collapsed = localStorage.getItem(sidebarKey) === "1";
    } catch {}
    setDesktopSidebar(collapsed);
  } else {
    setMobileMenu(false);
  }

  menu.addEventListener("click", () => {
    if (desktop.matches) {
      setDesktopSidebar(!document.body.classList.contains("sidebar-collapsed"));
    } else {
      setMobileMenu(!sidebar.classList.contains("open"));
    }
  });

  backdrop.addEventListener("click", () => setMobileMenu(false));
  toc.addEventListener("click", () => {
    if (!desktop.matches) setMobileMenu(false);
  });

  desktop.addEventListener("change", (event) => {
    sidebar.classList.remove("open");
    backdrop.hidden = true;
    if (event.matches) {
      let collapsed = false;
      try {
        collapsed = localStorage.getItem(sidebarKey) === "1";
      } catch {}
      setDesktopSidebar(collapsed);
    } else {
      document.body.classList.remove("sidebar-collapsed");
      setMobileMenu(false);
    }
  });
})();
