const page = document.documentElement.dataset.page;
const shortlistKey = "bb-studio-shortlist";
let creatorCache = null;
let extractedRecords = [];

const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
}[character]));

const formatNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number)
    ? new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(number)
    : "—";
};

async function fetchJson(url, options) {
  const response = await fetch(url, { headers: { Accept: "application/json", "Content-Type": "application/json" }, ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

async function getCreators() {
  if (!creatorCache) creatorCache = await fetchJson("/api/creators");
  return creatorCache;
}

function creatorImage(creator, className = "") {
  const image = /^creator_(0[1-9]|10)\.jpg$/.test(String(creator.image || "")) ? creator.image : "";
  return image
    ? `<img class="${className}" src="/assets/images/${escapeHtml(image)}" alt="AI-generated fictional portrait of ${escapeHtml(creator.name)}" loading="lazy" decoding="async">`
    : `<span class="asset-missing">Portrait unavailable: ${escapeHtml(creator.name)}</span>`;
}

function getShortlist() {
  try { return JSON.parse(localStorage.getItem(shortlistKey) || "[]").map(Number).filter(Number.isFinite); }
  catch { return []; }
}

function setShortlist(ids) {
  localStorage.setItem(shortlistKey, JSON.stringify([...new Set(ids)]));
  updateShortlistUI();
}

function toggleShortlist(id) {
  const ids = getShortlist();
  setShortlist(ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id]);
}

async function updateShortlistUI() {
  const ids = getShortlist();
  document.querySelectorAll("[data-shortlist-count]").forEach((node) => { node.textContent = ids.length; });
  document.querySelectorAll("[data-shortlist-id]").forEach((button) => {
    const saved = ids.includes(Number(button.dataset.shortlistId));
    button.classList.toggle("is-saved", saved);
    button.setAttribute("aria-pressed", String(saved));
    button.textContent = saved ? "Remove from shortlist" : "Add to shortlist";
  });

  const container = document.querySelector("[data-shortlist-items]");
  if (!container) return;
  if (!ids.length) {
    container.innerHTML = `<div class="drawer-empty"><p>Your shortlist is ready for a few exceptional voices.</p><a class="text-link" href="/creators.html">Discover creators →</a></div>`;
    return;
  }
  try {
    const creators = await getCreators();
    const saved = ids.map((id) => creators.find((creator) => Number(creator.creator_id) === id)).filter(Boolean);
    container.innerHTML = saved.map((creator) => `<article class="shortlist-item">${creatorImage(creator)}<div><span>${escapeHtml(creator.niche)}</span><h3>${escapeHtml(creator.name)}</h3><a href="/creator/${creator.creator_id}">View profile →</a><button type="button" data-shortlist-id="${creator.creator_id}">Remove</button></div></article>`).join("");
  } catch {
    container.innerHTML = `<div class="drawer-empty"><p>The shortlist could not be loaded.</p></div>`;
  }
}

function closeDrawer() {
  const drawer = document.querySelector("[data-shortlist-drawer]");
  const scrim = document.querySelector("[data-shortlist-scrim]");
  if (!drawer) return;
  drawer.classList.remove("is-open"); drawer.setAttribute("aria-hidden", "true");
  if (scrim) scrim.hidden = true;
}

document.addEventListener("click", (event) => {
  const shortlistButton = event.target.closest("[data-shortlist-id]");
  if (shortlistButton) toggleShortlist(Number(shortlistButton.dataset.shortlistId));
  if (event.target.closest("[data-shortlist-open]")) {
    const drawer = document.querySelector("[data-shortlist-drawer]");
    const scrim = document.querySelector("[data-shortlist-scrim]");
    drawer?.classList.add("is-open"); drawer?.setAttribute("aria-hidden", "false");
    if (scrim) scrim.hidden = false;
    document.querySelector("[data-shortlist-close]")?.focus();
  }
  if (event.target.closest("[data-shortlist-close]") || event.target.matches("[data-shortlist-scrim]")) closeDrawer();
});

document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeDrawer(); });

function directoryCard(creator) {
  return `<article class="directory-card">
    <a class="directory-portrait" href="/creator/${creator.creator_id}">${creatorImage(creator)}</a>
    <div class="directory-card-body"><div class="creator-meta"><span>${escapeHtml(creator.niche)}</span><span>${String(creator.creator_id).padStart(2, "0")}</span></div>
      <h3>${escapeHtml(creator.name)}</h3><p>${formatNumber(creator.followers)} followers · ${Number(creator.engagement_rate).toFixed(1)}% engagement</p>
      <div class="card-actions"><a class="text-link" href="/creator/${creator.creator_id}">View profile →</a><button class="shortlist-button" type="button" data-shortlist-id="${creator.creator_id}">Add to shortlist</button></div>
    </div></article>`;
}

async function initDirectory() {
  const grid = document.querySelector("[data-creator-directory]");
  const form = document.querySelector("[data-creator-filters]");
  if (!grid || !form) return;
  try {
    const creators = await getCreators();
    const nicheSelect = form.elements.niche;
    [...new Set(creators.map((creator) => creator.niche))].sort().forEach((niche) => nicheSelect.add(new Option(niche, niche)));
    const render = () => {
      const search = form.elements.search.value.trim().toLowerCase();
      const niche = form.elements.niche.value;
      const sort = form.elements.sort.value;
      let results = creators.filter((creator) => (!search || creator.name.toLowerCase().includes(search)) && (!niche || creator.niche === niche));
      if (sort === "followers-desc") results.sort((a, b) => b.followers - a.followers);
      if (sort === "followers-asc") results.sort((a, b) => a.followers - b.followers);
      if (sort === "engagement-desc") results.sort((a, b) => b.engagement_rate - a.engagement_rate);
      grid.innerHTML = results.length ? results.map(directoryCard).join("") : `<div class="empty-state"><h3>No creators found.</h3><p>Try a different name or category.</p><button type="button" data-clear-filters>Clear filters</button></div>`;
      grid.setAttribute("aria-busy", "false"); updateShortlistUI();
    };
    form.addEventListener("input", render); form.addEventListener("change", render);
    grid.addEventListener("click", (event) => { if (event.target.matches("[data-clear-filters]")) { form.reset(); render(); } });
    render();
  } catch (error) { grid.innerHTML = `<div class="empty-state"><h3>Directory unavailable.</h3><p>${escapeHtml(error.message)}</p></div>`; }
}

async function initProfile() {
  const shell = document.querySelector("[data-profile]");
  if (!shell) return;
  const id = location.pathname.match(/\/creator\/(\d+)/)?.[1];
  if (!id) { shell.innerHTML = `<div class="empty-state"><h2>Creator not found.</h2><a href="/creators.html">Back to creators</a></div>`; return; }
  try {
    const creator = await fetchJson(`/api/creators/${id}`);
    document.title = `${creator.name} | B&B Studio`;
    shell.innerHTML = `<div class="profile-image">${creatorImage(creator)}</div><div class="profile-copy"><a class="back-link" href="/creators.html">← Back to creators</a><p class="eyebrow">${escapeHtml(creator.niche)}</p><h1>${escapeHtml(creator.name)}</h1><p class="profile-lede">A fictional ${escapeHtml(creator.niche.toLowerCase())} creator based in ${escapeHtml(creator.location)}, presented as demonstration portfolio data.</p><dl class="profile-facts"><div><dt>Followers</dt><dd>${formatNumber(creator.followers)}</dd></div><div><dt>Engagement</dt><dd>${Number(creator.engagement_rate).toFixed(1)}%</dd></div><div><dt>Audience</dt><dd>${escapeHtml(creator.audience)}</dd></div><div><dt>Location</dt><dd>${escapeHtml(creator.location)}</dd></div><div><dt>Indicative fee</dt><dd>₹${Number(creator.estimated_fee).toLocaleString("en-IN")}</dd></div></dl><button class="button button-primary" type="button" data-shortlist-id="${creator.creator_id}">Add to shortlist</button><p class="data-disclosure">Fictional persona and demonstration metrics.</p></div>`;
    shell.setAttribute("aria-busy", "false"); updateShortlistUI();
  } catch (error) { shell.innerHTML = `<div class="empty-state"><h2>Creator not found.</h2><p>${escapeHtml(error.message)}</p><a href="/creators.html">Back to creators</a></div>`; }
}

function matchCard(creator) {
  return `<article class="match-card"><div class="match-card-image">${creatorImage(creator)}</div><div><div class="match-score"><strong>${Number(creator.match_score).toFixed(0)}%</strong><span>match score</span></div><p class="eyebrow">${escapeHtml(creator.niche)}</p><h3>${escapeHtml(creator.name)}</h3><p>${formatNumber(creator.followers)} followers · ${Number(creator.engagement_rate).toFixed(1)}% engagement</p><ul>${creator.reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}</ul><div class="card-actions"><a class="text-link" href="/creator/${creator.creator_id}">View profile →</a><button class="shortlist-button" type="button" data-shortlist-id="${creator.creator_id}">Add to shortlist</button></div></div></article>`;
}

function initMatchmaker() {
  const form = document.querySelector("[data-match-form]"); const results = document.querySelector("[data-match-results]");
  if (!form || !results) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault(); results.innerHTML = `<div class="page-state">Considering the strongest alignments…</div>`;
    const payload = Object.fromEntries(new FormData(form));
    try {
      const matches = await fetchJson("/api/match", { method: "POST", body: JSON.stringify(payload) });
      results.innerHTML = matches.length ? `<div class="match-list">${matches.slice(0, 5).map(matchCard).join("")}</div>` : `<div class="empty-state"><h3>No creators fit this budget.</h3><p>Try increasing the budget or broadening the brief.</p></div>`;
      updateShortlistUI();
    } catch (error) { results.innerHTML = `<div class="empty-state"><h3>Matching unavailable.</h3><p>${escapeHtml(error.message)}</p></div>`; }
  });
}

function plotLayout(title) {
  return { title: { text: title, font: { family: "DM Sans", size: 12, color: "#560B18" } }, paper_bgcolor: "#F2E5C6", plot_bgcolor: "#F2E5C6", font: { family: "DM Sans", color: "#3B010B", size: 11 }, margin: { l: 55, r: 18, t: 45, b: 65 }, autosize: true };
}

async function initAnalytics() {
  const studio = document.querySelector("[data-analytics-studio]"); if (!studio) return;
  try {
    const data = await fetchJson("/api/analytics");
    studio.querySelector(".kpi-grid").innerHTML = `<article><span>Records</span><strong>${Number(data.total_influencers).toLocaleString()}</strong></article><article><span>Average followers</span><strong>${formatNumber(data.average_followers)}</strong></article><article><span>Average engagement</span><strong>${Number(data.average_engagement_rate).toFixed(2)}%</strong></article><article><span>Leading category</span><strong>${escapeHtml(data.most_represented_category)}</strong></article>`;
    if (!window.Plotly) throw new Error("The chart library could not load.");
    const config = { responsive: true, displayModeBar: false };
    Plotly.newPlot(document.querySelector('[data-chart="categories"]'), [{ type: "bar", x: data.category_distribution.labels, y: data.category_distribution.values, marker: { color: "#75162D" } }], plotLayout("Influencer records by category"), config);
    Plotly.newPlot(document.querySelector('[data-chart="engagement"]'), [{ type: "bar", orientation: "h", y: data.engagement_by_category.labels, x: data.engagement_by_category.values, marker: { color: "#560B18" } }], plotLayout("Average engagement rate (%)"), config);
    Plotly.newPlot(document.querySelector('[data-chart="scatter"]'), [{ mode: "markers", x: data.followers_vs_engagement.followers, y: data.followers_vs_engagement.engagement_rate, text: data.followers_vs_engagement.categories, marker: { color: "#75162D", opacity: .58, size: 7 } }], { ...plotLayout("Followers vs engagement rate"), xaxis: { title: "Followers", type: "log" }, yaxis: { title: "Engagement rate (%)" } }, config);
    studio.setAttribute("aria-busy", "false");
  } catch (error) { studio.innerHTML = `<div class="empty-state"><h2>Insights unavailable.</h2><p>${escapeHtml(error.message)}</p></div>`; }
}

function toCsv(records) {
  const fields = ["quote", "author", "tags"];
  const cell = (value) => `"${String(value ?? "").replace(/"/g, '""')}"`;
  return [fields.join(","), ...records.map((record) => fields.map((field) => cell(record[field])).join(","))].join("\r\n");
}

function initAtelier() {
  const run = document.querySelector("[data-run-extraction]"); const table = document.querySelector("[data-extraction-table]");
  const message = document.querySelector("[data-extraction-message]"); const count = document.querySelector("[data-record-count]"); const download = document.querySelector("[data-download-csv]");
  if (!run || !table) return;
  run.addEventListener("click", async () => {
    run.disabled = true; run.textContent = "Extracting…"; message.textContent = "Retrieving and parsing the public practice page…";
    try {
      const data = await fetchJson("/api/scrape", { method: "POST", body: "{}" }); extractedRecords = data.records || data.preview || [];
      count.textContent = data.count; document.querySelector("[data-extraction-heading]").textContent = "Extraction complete.";
      message.textContent = `${data.count} live records were parsed into structured fields.`;
      table.innerHTML = extractedRecords.slice(0, 8).map((record) => `<tr><td>${escapeHtml(record.quote)}</td><td>${escapeHtml(record.author)}</td><td>${escapeHtml(record.tags)}</td></tr>`).join("");
      download.disabled = !extractedRecords.length;
    } catch (error) { message.textContent = `Extraction failed: ${error.message}`; document.querySelector("[data-extraction-heading]").textContent = "The source could not be reached."; }
    finally { run.disabled = false; run.innerHTML = 'Run extraction <span aria-hidden="true">→</span>'; }
  });
  download?.addEventListener("click", () => {
    if (!extractedRecords.length) return;
    const url = URL.createObjectURL(new Blob([toCsv(extractedRecords)], { type: "text/csv;charset=utf-8" }));
    const link = document.createElement("a"); link.href = url; link.download = "bb-studio-extracted-quotes.csv"; link.click(); URL.revokeObjectURL(url);
  });
}

const navToggle = document.querySelector(".nav-toggle"); const primaryNav = document.querySelector(".primary-nav");
navToggle?.addEventListener("click", () => { const open = navToggle.getAttribute("aria-expanded") === "true"; navToggle.setAttribute("aria-expanded", String(!open)); primaryNav?.classList.toggle("is-open", !open); });
document.querySelectorAll("[data-year]").forEach((node) => { node.textContent = new Date().getFullYear(); });

updateShortlistUI();
if (page === "creators") initDirectory();
if (page === "profile") initProfile();
if (page === "match") initMatchmaker();
if (page === "analytics") initAnalytics();
if (page === "atelier") initAtelier();
