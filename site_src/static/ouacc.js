document.addEventListener("DOMContentLoaded", () => {
  const nav = document.getElementById("main-nav");
  const toggle = document.querySelector(".nav-toggle");
  const groups = document.querySelectorAll(".nav-group");

  const closeGroups = () => groups.forEach(group => {
    group.classList.remove("is-open");
    const button = group.querySelector(".nav-caret");
    if (button) button.setAttribute("aria-expanded", "false");
  });

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });
  }

  groups.forEach(group => {
    const caret = group.querySelector(".nav-caret");
    if (!caret) return;
    caret.addEventListener("click", event => {
      event.preventDefault();
      const open = group.classList.contains("is-open");
      closeGroups();
      group.classList.toggle("is-open", !open);
      caret.setAttribute("aria-expanded", String(!open));
    });
  });

  document.addEventListener("click", event => {
    if (!event.target.closest(".main-nav")) closeGroups();
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      closeGroups();
      if (toggle && nav) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    }
  });

  const form = document.getElementById("site-search-form");
  const results = document.getElementById("search-results");
  const input = document.getElementById("site-search");
  if (form && results && input) {
    const runSearch = async () => {
      const query = input.value.trim().toLowerCase();
      if (!query) { results.innerHTML = "<p>Enter a search term.</p>"; return; }
      const response = await fetch("search-index.json");
      const pages = await response.json();
      const terms = query.split(/\s+/).filter(Boolean);
      const scored = pages.map(page => {
        const title = page.title.toLowerCase();
        const text = page.text.toLowerCase();
        let score = 0;
        terms.forEach(term => {
          if (title.includes(term)) score += 12;
          if (page.section.toLowerCase().includes(term)) score += 3;
          score += Math.min(text.split(term).length - 1, 8);
        });
        return {...page, score};
      }).filter(page => page.score > 0).sort((a,b) => b.score-a.score).slice(0, 12);
      if (!scored.length) { results.innerHTML = "<p>No pages matched your search.</p>"; return; }
      const esc = value => value.replace(/[&<>\"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[ch]));
      results.innerHTML = scored.map(page => `<article class="search-result"><div class="search-meta">${esc(page.section)}</div><h2><a href="${page.path}">${esc(page.title)}</a></h2><p>${esc(page.text.slice(0, 260))}${page.text.length > 260 ? "…" : ""}</p></article>`).join("");
    };
    form.addEventListener("submit", event => {
      event.preventDefault();
      runSearch();
      history.replaceState(null, "", "search.html?q=" + encodeURIComponent(input.value));
    });
    const params = new URLSearchParams(window.location.search);
    const q = params.get("q");
    if (q) { input.value=q; runSearch(); }
  }
});
