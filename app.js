/* optical. — interactions: theme, progress, contents, search, geometry lab, KaTeX. */

// Shared between the boot IIFE and the post-KaTeX word count below.
let minutesEstimate = 30;

(() => {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const escapeHtml = (text) =>
    String(text).replace(
      /[&<>"']/g,
      (c) =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
          c
        ],
    );

  /* ---------------------------------------------------------------- theme */

  const root = document.documentElement;

  function applyTheme(theme) {
    const dark = theme === "dark";
    root.dataset.theme = dark ? "dark" : "light";
    try {
      localStorage.setItem("optical-theme", dark ? "dark" : "light");
    } catch {}
    const button = $(".theme-toggle");
    const label = dark ? "Switch to light theme" : "Switch to dark theme";
    button.setAttribute("aria-label", label);
    button.setAttribute("title", label);
    $('meta[name="theme-color"]')?.setAttribute(
      "content",
      dark ? "#2d2a2e" : "#f5f6f7",
    );
    drawLab();
  }

  $(".theme-toggle").addEventListener("click", () => {
    applyTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });

  /* ----------------------------------------------------------- geometry lab */

  const labSvg = $("#lab-canvas");
  const rhoSlider = $("#rho-slider");

  function drawLab() {
    const rho = parseFloat(rhoSlider.value) || 0;
    const css = getComputedStyle(root);
    const c = (name) => css.getPropertyValue(name).trim();
    const line = c("--line");
    const lineStrong = c("--line-strong");
    const ink = c("--ink");
    const muted = c("--muted");
    const accent = c("--accent");
    const accentBright = c("--accent-bright");

    const CX = 320;
    const CY = 190;
    const R = 150;
    const alpha = 0.2;
    const beta = 0.2;

    const rx = (p) => R * (1 + alpha * p * p);
    const rz = (p) => R * (1 - beta * p * p);

    const grid = [];
    for (let gx = CX - 240; gx <= CX + 240; gx += 60) {
      grid.push(
        `<line x1="${gx}" y1="30" x2="${gx}" y2="350" stroke="${line}" stroke-width="1"/>`,
      );
    }
    for (let gy = CY - 150; gy <= CY + 150; gy += 60) {
      grid.push(
        `<line x1="60" y1="${gy}" x2="580" y2="${gy}" stroke="${line}" stroke-width="1"/>`,
      );
    }

    const shells = [1, 0.66, 0.33]
      .map(
        (p) =>
          `<ellipse class="lab-shell" cx="${CX}" cy="${CY}" rx="${rx(p).toFixed(1)}" ry="${rz(p).toFixed(1)}"/>`,
      )
      .join("");

    const activeRx = rx(rho);
    const activeRz = rz(rho);

    const dxdr = 1 + 3 * alpha * rho * rho;
    const dzdr = 1 - 3 * beta * rho * rho;

    const xEnd = CX + activeRx;
    const zEnd = CY - activeRz;

    labSvg.innerHTML = `
      <g>${grid.join("")}</g>
      <line class="lab-axis" x1="40" y1="${CY}" x2="600" y2="${CY}"/>
      <line class="lab-axis" x1="${CX}" y1="20" x2="${CX}" y2="360"/>
      <g>${shells}</g>
      <ellipse class="lab-shell lab-shell--active" cx="${CX}" cy="${CY}" rx="${activeRx.toFixed(1)}" ry="${activeRz.toFixed(1)}"/>
      <line class="lab-arrow" x1="${CX}" y1="${CY}" x2="${xEnd.toFixed(1)}" y2="${CY}"/>
      <polygon class="lab-arrow-head" points="${xEnd.toFixed(1)},${CY} ${(xEnd - 8).toFixed(1)},${CY - 5} ${(xEnd - 8).toFixed(1)},${CY + 5}"/>
      <line class="lab-arrow" x1="${CX}" y1="${CY}" x2="${CX}" y2="${zEnd.toFixed(1)}"/>
      <polygon class="lab-arrow-head" points="${CX},${zEnd.toFixed(1)} ${CX - 5},${(zEnd + 8).toFixed(1)} ${CX + 5},${(zEnd + 8).toFixed(1)}"/>
      <circle class="lab-pt" cx="${xEnd.toFixed(1)}" cy="${CY}" r="4"/>
      <circle class="lab-pt" cx="${CX}" cy="${zEnd.toFixed(1)}" r="4"/>
      <circle class="lab-pt" cx="${CX}" cy="${CY}" r="4"/>
      <text class="lab-text lab-text--strong" x="${Math.min(xEnd + 14, 560)}" y="${CY + 22}">sₓ(ρ) = ${(1 + alpha * rho * rho).toFixed(3)}</text>
      <text class="lab-text lab-text--strong" x="${CX + 12}" y="${Math.max(zEnd - 12, 40)}">s_z(ρ) = ${(1 - beta * rho * rho).toFixed(3)}</text>
      <text class="lab-text lab-text--accent" x="${CX - 235}" y="${CY - 118}">dx/dρ = ${dxdr.toFixed(3)}</text>
      <text class="lab-text lab-text--accent" x="${CX - 235}" y="${CY - 103}">dz/dρ = ${dzdr.toFixed(3)}</text>
      <text class="lab-text" x="52" y="${CY - 132}">x</text>
      <text class="lab-text" x="${CX + 8}" y="30">z</text>`;

    $("#rho-val").textContent = rho.toFixed(2);
    $("#dxdr").textContent = dxdr.toFixed(3);
    $("#dzdr").textContent = dzdr.toFixed(3);
    $("#ratio").textContent = `${(dxdr / dzdr).toFixed(2)} : 1`;
    rhoSlider.setAttribute("aria-valuetext", rho.toFixed(2));
  }

  rhoSlider.addEventListener("input", drawLab);

  /* ------------------------------------------------------------- progress */

  const readingSection = $("#essay");
  const article = $("#article-content");
  const chapterLinks = $$(".chapter-link");

  function updateProgress() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const progress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    const bar = $(".reading-progress > div");
    if (bar) bar.style.width = `${progress * 100}%`;
    const side = $(".side-progress > span");
    if (side) side.style.width = `${progress * 100}%`;
    $("#reading-left").textContent =
      progress < 0.01
        ? "Reading progress"
        : `${Math.max(1, Math.ceil(minutesEstimate * (1 - progress)))} min remaining`;
    updateActiveChapter();
  }

  function updateActiveChapter() {
    const headings = $$("#article-content h2[id]");
    let active = null;
    // Headings land ~272px from the top (scroll-padding + scroll-margin),
    // so a section becomes active once its heading clears that band.
    for (const heading of headings) {
      if (heading.getBoundingClientRect().top <= 280) active = heading.id;
      else break;
    }
    if (readingSection.getBoundingClientRect().top > window.innerHeight * 0.6) {
      active = null;
    }
    for (const link of chapterLinks) {
      const current = Boolean(active) && link.hash === `#${active}`;
      link.classList.toggle("current", current);
      if (current) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
    // Keep the active row visible inside the scrolling list.
    const activeLink = $("#chapter-list .chapter-link.current");
    const list = $("#chapter-list");
    if (activeLink && list.clientHeight > 0) {
      const lr = list.getBoundingClientRect();
      const ar = activeLink.getBoundingClientRect();
      if (ar.top < lr.top || ar.bottom > lr.bottom) {
        list.scrollTop += ar.top - lr.top - 12;
      }
    }
  }

  let queued = false;
  window.addEventListener(
    "scroll",
    () => {
      if (!queued) {
        queued = true;
        requestAnimationFrame(() => {
          queued = false;
          updateProgress();
        });
      }
    },
    { passive: true },
  );

  /* ------------------------------------------------------------ mobile toc */

  const mobileMenu = $(".mobile-menu");

  function closeMobileToc() {
    document.body.classList.remove("mobile-toc-open");
    mobileMenu.setAttribute("aria-expanded", "false");
  }

  mobileMenu.addEventListener("click", () => {
    const open = document.body.classList.toggle("mobile-toc-open");
    mobileMenu.setAttribute("aria-expanded", String(open));
  });

  $(".rail-close")?.addEventListener("click", closeMobileToc);

  $("#chapter-list").addEventListener("click", (event) => {
    if (event.target.closest(".chapter-link")) closeMobileToc();
  });

  document.addEventListener("click", (event) => {
    if (!document.body.classList.contains("mobile-toc-open")) return;
    if (
      event.target.closest(".chapter-sidebar") ||
      event.target.closest(".mobile-menu")
    )
      return;
    closeMobileToc();
  });

  /* ------------------------------------------------------- reading controls */

  const toast = (message) => {
    const element = $("#toast");
    element.textContent = message;
    element.classList.add("visible");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => element.classList.remove("visible"), 2400);
  };

  const sizes = ["18.5px", "19.5px", "21.5px"];
  let sizeIndex = 1;
  try {
    const stored = Number(localStorage.getItem("optical-text-size"));
    if (Number.isInteger(stored) && sizes[stored]) sizeIndex = stored;
  } catch {}

  function applyTextSize() {
    readingSection.style.setProperty("--reading-size", sizes[sizeIndex]);
  }

  $(".text-size").addEventListener("click", () => {
    sizeIndex = (sizeIndex + 1) % sizes.length;
    try {
      localStorage.setItem("optical-text-size", String(sizeIndex));
    } catch {}
    applyTextSize();
    toast(`Reading text: ${["standard", "large", "extra large"][sizeIndex]}.`);
  });

  $(".focus-toggle").addEventListener("click", (event) => {
    const active = document.body.classList.toggle("focus-mode");
    event.currentTarget.setAttribute("aria-pressed", String(active));
    toast(active ? "Distraction-free reading." : "Contents restored.");
  });

  $("#back-to-top").addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  /* ------------------------------------------------------------------ search */

  const dialog = $("#search-dialog");
  const input = $("#search-input");
  const resultsBox = $("#search-results");

  const arrowIcon =
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>';

  let index = [];
  function buildIndex() {
    index = [];
    const nodes = $$(
      "#article-content h2, #article-content h3, #article-content p, #article-content li, #article-content figcaption, #article-content .theorem-title, #article-content .stat-label",
    );
    let anchor = "s1";
    for (const node of nodes) {
      if (node.matches("h2, h3")) {
        if (node.id) anchor = node.id;
        continue;
      }
      if (node.closest(".katex")) continue;
      const text = node.textContent.replace(/\s+/g, " ").trim();
      if (text.length < 8) continue;
      index.push({ anchor, label: labelFor(anchor), text });
    }
  }

  function labelFor(anchor) {
    const link = $(`.chapter-link[href="#${anchor}"]`);
    return link ? link.textContent.replace(/^\d+\s*/, "").trim() : "Essay";
  }

  function search() {
    const query = input.value.trim().toLowerCase();
    const results = [];
    if (query.length >= 2) {
      for (const entry of index) {
        const at = entry.text.toLowerCase().indexOf(query);
        if (at < 0) continue;
        results.push({
          ...entry,
          snippet: entry.text.slice(Math.max(0, at - 60), at + 160),
        });
        if (results.length >= 24) break;
      }
    }
    resultsBox.innerHTML = !query
      ? `<div class="search-empty"><span>Search the essay</span><p>Try “caustic”, “group delay”, or “calibration”.</p></div>`
      : query.length < 2
        ? '<div class="search-empty">Enter at least two characters.</div>'
        : !results.length
          ? `<div class="search-empty">No matches for “${escapeHtml(input.value)}”.</div>`
          : `<div class="results-count">${results.length} match${results.length === 1 ? "" : "es"}</div>${results
              .map(
                (result, i) =>
                  `<button class="search-result" type="button" data-i="${i}"><span>${escapeHtml(result.label)} ${arrowIcon}</span><p>${escapeHtml(result.snippet)}</p></button>`,
              )
              .join("")}`;

    $$(".search-result", resultsBox).forEach((button) => {
      button.addEventListener("click", () => {
        const result = results[Number(button.dataset.i)];
        dialog.close();
        requestAnimationFrame(() => {
          document
            .getElementById(result.anchor)
            ?.scrollIntoView({ behavior: "instant", block: "start" });
        });
      });
    });
  }

  function openSearch() {
    dialog.showModal();
    search();
    input.focus();
  }

  $(".search-trigger").addEventListener("click", openSearch);
  $(".close-search").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  input.addEventListener("input", search);
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      dialog.open ? dialog.close() : openSearch();
      return;
    }
    if (event.key === "Escape") {
      if (dialog.open) dialog.close();
      if (document.body.classList.contains("mobile-toc-open")) {
        closeMobileToc();
        mobileMenu.focus();
      }
    }
  });

  /* ---------------------------------------------------------------- print */

  window.addEventListener("beforeprint", () => {
    $$(".proof:not([open])").forEach((d) => (d.open = true));
  });
  window.addEventListener("afterprint", () => {
    $$(".proof[open]").forEach((d) => (d.open = false));
  });

  /* ------------------------------------------------------------------ init */

  applyTextSize();
  drawLab();
  buildIndex();
  updateProgress();
})();

/* KaTeX — render all \( … \) and \[ … \] after the DOM is ready. */
document.addEventListener("DOMContentLoaded", () => {
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true },
      ],
      throwOnError: false,
      strict: false,
    });
  }
  // Word count after KaTeX, excluding rendered math entirely (it is not
  // prose, and its hidden MathML annotations would inflate the estimate).
  const article = document.querySelector("#article-content");
  if (article) {
    const clone = article.cloneNode(true);
    clone.querySelectorAll(".katex").forEach((node) => node.remove());
    const wordCount = (clone.textContent.match(/\S+/g) || []).length;
    minutesEstimate = Math.max(4, Math.round(wordCount / 215));
    const meta = document.querySelector(".reading-identity-meta");
    if (meta && !meta.dataset.timed) {
      meta.dataset.timed = "1";
      meta.textContent += ` · ~${minutesEstimate} MIN READ`;
    }
  }
});

/* Deep links: anchor jumps happen before fonts and KaTeX settle, so the
   target drifts. Re-apply the hash once fonts are ready and on hashchange. */
function settleHash() {
  const hash = location.hash;
  if (!hash) return;
  requestAnimationFrame(() => {
    const target = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (target) {
      target.scrollIntoView({ behavior: "instant", block: "start" });
    }
  });
}
window.addEventListener("hashchange", settleHash);
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(() => setTimeout(settleHash, 0));
} else {
  window.addEventListener("load", settleHash);
}
