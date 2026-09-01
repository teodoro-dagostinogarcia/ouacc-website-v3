document.addEventListener("DOMContentLoaded", async function () {
  const form = document.getElementById("site-search-form");
  const input = document.getElementById("site-search");
  const results = document.getElementById("search-results");
  const status = document.getElementById("search-status");
  if (!form || !input || !results || !status) return;

  const indexUrl = document.body.dataset.siteRoot + "search-index.json";
  let index = [];
  try {
    const response = await fetch(indexUrl, { cache: "no-store" });
    index = await response.json();
  } catch (error) {
    status.textContent = "Search is temporarily unavailable.";
    return;
  }

  function render(raw) {
    const query = raw.trim().toLowerCase();
    results.innerHTML = "";
    if (!query) {
      status.textContent = "Enter a search term to begin.";
      return;
    }

    const terms = query.split(/\s+/).filter(Boolean);
    const ranked = index.map(function (item) {
      const title = item.title.toLowerCase();
      const text = item.text.toLowerCase();
      let score = 0;
      terms.forEach(function (term) {
        if (title.includes(term)) score += 12;
        if (text.includes(term)) score += 3;
      });
      if (title.includes(query)) score += 20;
      return { item, score };
    }).filter(function (entry) { return entry.score > 0; })
      .sort(function (a, b) { return b.score - a.score || a.item.title.localeCompare(b.item.title); });

    status.textContent = ranked.length + " result" + (ranked.length === 1 ? "" : "s");
    if (!ranked.length) {
      results.innerHTML = '<p class="no-results">No pages matched your search.</p>';
      return;
    }

    ranked.slice(0, 30).forEach(function (entry) {
      const card = document.createElement("article");
      const link = document.createElement("a");
      const excerpt = document.createElement("p");
      card.className = "search-result";
      link.className = "search-result-title";
      link.href = entry.item.url;
      link.textContent = entry.item.title;
      let snippet = entry.item.text;
      const pos = snippet.toLowerCase().indexOf(terms[0]);
      if (pos > 120) snippet = snippet.slice(pos - 90);
      snippet = snippet.slice(0, 240);
      excerpt.textContent = snippet + (snippet.length >= 240 ? "..." : "");
      card.append(link, excerpt);
      results.appendChild(card);
    });
  }

  const params = new URLSearchParams(location.search);
  const initial = params.get("q") || "";
  input.value = initial;
  render(initial);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const q = input.value.trim();
    history.replaceState({}, "", q ? "search.html?q=" + encodeURIComponent(q) : "search.html");
    render(q);
  });
});
