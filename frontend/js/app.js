const creatorGrid = document.querySelector("#creator-grid");
const analyticsPreview = document.querySelector("#analytics-preview");
const navToggle = document.querySelector(".nav-toggle");
const primaryNav = document.querySelector(".primary-nav");
const howModal = document.querySelector("[data-modal]");
const modalOpenButton = document.querySelector("[data-modal-open]");
const modalCloseButton = document.querySelector("[data-modal-close]");
let lastFocusedElement = null;

const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  "'": "&#39;",
  '"': "&quot;"
}[character]));

const formatCompactNumber = (value) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(number);
};

async function fetchJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
  return response.json();
}

function renderCreators(creators) {
  if (!creatorGrid) return;
  const featured = Array.isArray(creators) ? creators.slice(0, 3) : [];

  if (!featured.length) {
    throw new Error("No creator profiles are available yet.");
  }

  creatorGrid.innerHTML = featured.map((creator, index) => {
    const name = escapeHtml(creator.name || creator.username || "Creator");
    const niche = escapeHtml(creator.niche || "Beauty");
    const imageFile = /^creator_(0[1-9]|10)\.jpg$/.test(String(creator.image || ""))
      ? String(creator.image)
      : "";
    const followers = formatCompactNumber(creator.followers);
    const engagement = Number(creator.engagement_rate);
    const engagementLabel = Number.isFinite(engagement)
      ? `${engagement.toFixed(1)}% engagement`
      : "Engagement unavailable";

    return `
      <article class="creator-card">
        <div class="creator-portrait">
          ${imageFile
            ? `<img src="/assets/images/${escapeHtml(imageFile)}" alt="AI-generated fictional portrait of ${name}" loading="lazy" decoding="async">`
            : `<span class="portrait-missing" role="status">Portrait unavailable: ${name}</span>`}
        </div>
        <div class="creator-info">
          <div class="creator-meta"><span>${niche}</span><span>0${index + 1}</span></div>
          <h3 class="creator-name">${name}</h3>
          <p class="creator-stats">
            <span>${escapeHtml(engagementLabel)}</span>
            <span>${escapeHtml(followers)} followers</span>
          </p>
          <a class="profile-link" href="/creator/${escapeHtml(creator.creator_id)}">
            <span>View profile</span><span aria-hidden="true">→</span>
          </a>
        </div>
      </article>`;
  }).join("");

  creatorGrid.querySelectorAll(".creator-portrait img").forEach((image) => {
    image.addEventListener("error", () => {
      const portrait = image.closest(".creator-portrait");
      portrait.classList.add("image-error");
      portrait.innerHTML = `<span class="portrait-missing" role="status">Portrait unavailable: ${escapeHtml(image.alt.replace("AI-generated fictional portrait of ", ""))}</span>`;
    }, { once: true });
  });
  creatorGrid.setAttribute("aria-busy", "false");
}

function renderAnalytics(data) {
  if (!analyticsPreview) return;
  const categories = Object.entries(data?.top_categories || {})
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .slice(0, 4)
    .map(([category]) => `<li>${escapeHtml(category)}</li>`)
    .join("");

  analyticsPreview.innerHTML = `
    <div class="analytics-stat">
      <span class="analytics-stat-label">Creators studied</span>
      <strong class="analytics-stat-value">${escapeHtml(formatCompactNumber(data?.total_influencers))}</strong>
    </div>
    <div class="analytics-stat">
      <span class="analytics-stat-label">Average audience</span>
      <strong class="analytics-stat-value">${escapeHtml(formatCompactNumber(data?.average_followers))}</strong>
    </div>
    <div class="analytics-categories">
      <span class="analytics-categories-title">Leading creator categories</span>
      <ul class="category-list">${categories || "<li>Beauty</li>"}</ul>
    </div>`;
  analyticsPreview.setAttribute("aria-busy", "false");
}

function showCreatorError() {
  if (!creatorGrid) return;
  creatorGrid.innerHTML = `
    <div class="error-state">
      <span>Creator profiles are resting backstage.</span>
      <a class="text-link" href="/creators.html">Visit the directory <span aria-hidden="true">→</span></a>
    </div>`;
  creatorGrid.setAttribute("aria-busy", "false");
}

function showAnalyticsError() {
  if (!analyticsPreview) return;
  analyticsPreview.innerHTML = `
    <div class="analytics-loading">
      <span>Studio insights are temporarily unavailable.</span>
    </div>`;
  analyticsPreview.setAttribute("aria-busy", "false");
}

if (navToggle && primaryNav) {
  navToggle.addEventListener("click", () => {
    const isOpen = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!isOpen));
    primaryNav.classList.toggle("is-open", !isOpen);
  });

  primaryNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      navToggle.setAttribute("aria-expanded", "false");
      primaryNav.classList.remove("is-open");
    }
  });
}

function closeHowModal() {
  if (!howModal || howModal.hidden) return;
  howModal.hidden = true;
  document.body.classList.remove("modal-open");
  document.removeEventListener("keydown", handleModalKeydown);
  lastFocusedElement?.focus();
}

function handleModalKeydown(event) {
  if (event.key === "Escape") {
    event.preventDefault();
    closeHowModal();
    return;
  }

  if (event.key !== "Tab" || !howModal) return;
  const focusable = [...howModal.querySelectorAll("a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])")];
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function openHowModal() {
  if (!howModal) return;
  lastFocusedElement = document.activeElement;
  howModal.hidden = false;
  document.body.classList.add("modal-open");
  document.addEventListener("keydown", handleModalKeydown);
  modalCloseButton?.focus();
}

modalOpenButton?.addEventListener("click", openHowModal);
modalCloseButton?.addEventListener("click", closeHowModal);
howModal?.addEventListener("click", (event) => {
  if (event.target === howModal) closeHowModal();
});

document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = new Date().getFullYear();
});

Promise.allSettled([
  fetchJson("/api/creators").then(renderCreators),
  fetchJson("/api/analytics").then(renderAnalytics)
]).then(([creatorsResult, analyticsResult]) => {
  if (creatorsResult.status === "rejected") showCreatorError();
  if (analyticsResult.status === "rejected") showAnalyticsError();
});
