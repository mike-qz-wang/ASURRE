/* ASURRE browser.
 *
 * Two views, no more:
 *   Respondents — one person's own answers, each followed by every model's
 *     version of that same answer. Respondents join across generator files by
 *     position; the originals agree at every index, so position is the key.
 *     This matters for phd2019, whose response_id column is not an identifier.
 *   Persona agents — agents invent a whole respondent, so no model answer
 *     corresponds to any person's. Those are pooled per question instead.
 */

async function loadJson(name) {
  const inlined = window.__ASURRE_DATA__;
  if (inlined && Object.prototype.hasOwnProperty.call(inlined, name)) {
    return inlined[name];
  }
  const res = await fetch(`data/${name}.json`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

const state = {
  index: null,
  dataset: null,
  payload: null,
  cursor: 0,
  variant: null, // "<tag>|<mode>" — the one model version shown beside the human
};

const el = {
  datasetTabs: document.getElementById("datasetTabs"),
  viewTabs: document.getElementById("viewTabs"),
  introMeta: document.getElementById("introMeta"),
  introLede: document.getElementById("introLede"),
  stage: document.getElementById("stage"),
  licenceNote: document.getElementById("licenceNote"),
};

const words = (s) => (s ? (s.match(/\S+/g) || []).length : 0);

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

/* ---------- loading ---------- */

async function boot() {
  try {
    state.index = await loadJson("index");
  } catch (err) {
    el.stage.innerHTML =
      '<div class="empty"><strong>The data did not load.</strong>' +
      "Serve this folder over HTTP — <code>python -m http.server --directory docs</code> — " +
      "or open the single-file preview instead.</div>";
    return;
  }
  await selectDataset(state.index.datasets[0].id);
}

async function selectDataset(id) {
  try {
    state.payload = await loadJson(id);
  } catch (err) {
    el.stage.innerHTML = `<div class="empty"><strong>Could not load ${esc(id)}.</strong>${esc(err)}</div>`;
    return;
  }
  state.dataset = id;
  state.cursor = 0;

  // Keep the chosen comparison when switching datasets where it still exists,
  // so the reader does not lose their place.
  const keys = (state.payload.generators || []).map((g) => g.key);
  if (!keys.includes(state.variant)) state.variant = keys[0] || null;
  render();
}

/* ---------- chrome ---------- */

function renderTabs() {
  el.datasetTabs.innerHTML = "";
  state.index.datasets.forEach((d) => {
    const b = document.createElement("button");
    b.textContent = d.meta.short || d.id;
    b.title = d.meta.title || d.id;
    if (d.id === state.dataset) b.setAttribute("aria-current", "true");
    b.addEventListener("click", () => selectDataset(d.id));
    el.datasetTabs.appendChild(b);
  });

  const gens = state.payload.generators || [];
  el.viewTabs.innerHTML =
    `<span class="scope">${state.payload.respondents.length} respondents · ` +
    `${gens.length} comparisons</span>`;
}

function renderIntro() {
  const m = state.payload.meta || {};
  const c = state.payload.config || {};
  const bits = [m.title, m.year, m.attribution, m.licence].filter(Boolean).map(esc);
  let html = bits.join(" &middot; ");
  if (m.url) html += ` &middot; <a href="${esc(m.url)}">source</a>`;
  if (c.description) html = `${esc(c.description)}<br>${html}`;
  if (m.sensitive) {
    html +=
      '<span class="sensitive">These are real accounts of mental health at work, ' +
      "published by OSMI under CC BY-SA 4.0. Read them as you would any interview material.</span>";
  }
  el.introMeta.innerHTML = html;

  el.introLede.textContent =
    "One respondent, one model: their completed questionnaire beside the version a language model produced in their place.";

  el.licenceNote.textContent =
    "Source survey licences — " +
    state.index.datasets.map((d) => `${d.meta.short}: ${d.meta.licence}`).join(" · ") +
    ". Respect them when redistributing.";
}

/* ---------- respondents ---------- */

function renderRespondents() {
  const list = state.payload.respondents;
  if (!list.length) {
    el.stage.innerHTML = '<div class="empty"><strong>No respondents here.</strong></div>';
    return;
  }
  state.cursor = Math.max(0, Math.min(state.cursor, list.length - 1));

  const r = list[state.cursor];
  const questions = state.payload.questions || {};
  const order = state.payload.field_order || Object.keys(questions);
  const gens = state.payload.generators || [];
  const chosen = gens.find((g) => g.key === state.variant) || gens[0];

  const controls =
    `<div class="pager">` +
    `<button id="prev"${state.cursor === 0 ? " disabled" : ""} aria-label="Previous respondent">Previous</button>` +
    `<span class="pager-count">Respondent ${state.cursor + 1} of ${list.length}` +
    (state.payload.rid_usable && r.rid ? ` <span class="rid">${esc(r.rid)}</span>` : "") +
    `</span>` +
    `<button id="next"${state.cursor === list.length - 1 ? " disabled" : ""} aria-label="Next respondent">Next</button>` +
    `<span class="pager-spacer"></span>` +
    `<label class="pager-pick" for="variantPick">Compared with</label>` +
    `<select id="variantPick">` +
    variantOptions(gens, chosen) +
    `</select>` +
    `</div>`;

  const covered = chosen
    ? order.some((fid) =>
        ((r.answers[fid] || {}).variants || []).some((v) => `${v.tag}|${v.mode}` === chosen.key)
      )
    : false;

  const notice =
    chosen && !covered
      ? `<p class="notice">${esc(chosen.generator)} did not run on this respondent. ` +
        `Its phd2019 pass covers only part of the split — pick another comparison, or page on.</p>`
      : "";

  // Every question gets a row, answered or not, so the two columns stay in
  // step and a blank reads as "not answered" rather than going missing.
  const rows = order
    .map((fid) => {
      const a = r.answers[fid] || { human: "", variants: [] };
      const match = chosen
        ? a.variants.find((v) => `${v.tag}|${v.mode}` === chosen.key)
        : null;
      const blank = !a.human && !match;

      return (
        `<article class="qrow${blank ? " is-blank" : ""}">` +
        `<div class="qhead"><span class="qid">${esc(fid)}</span>` +
        `<h2 class="qtext">${esc(questions[fid] || fid)}</h2></div>` +
        `<div class="sides">` +
        side(a.human, "human", "Their answer", "Not answered") +
        side(
          match ? match.t : "",
          "machine",
          chosen
            ? `${esc(chosen.label || chosen.tag)} <span class="verb">${esc(chosen.verb)}</span>`
            : "Model",
          chosen && chosen.mode === "agent_fill" ? "Agent skipped it" : "No model version"
        ) +
        `</div></article>`
      );
    })
    .join("");

  el.stage.innerHTML = controls + notice + rows;

  const step = (delta) => {
    state.cursor += delta;
    render();
    window.scrollTo({ top: 0 });
  };
  const prev = document.getElementById("prev");
  const next = document.getElementById("next");
  if (prev) prev.addEventListener("click", () => step(-1));
  if (next) next.addEventListener("click", () => step(1));

  const pick = document.getElementById("variantPick");
  if (pick) {
    pick.addEventListener("change", (e) => {
      state.variant = e.target.value;
      render();
    });
  }
}

/* Runs are grouped by family, not just by strategy: the four Claude Sonnet
   persona runs are one ablation, other backbones are a different question, and
   the inject_* runs are a separate attack study. Several runs share a backbone
   (persona_sonnet, _terse and _controlled are all Claude Sonnet), so the tag
   leads — that is what distinguishes them and what the files are named after. */
function variantOptions(gens, chosen) {
  const families = state.payload.families || [];
  return families
    .map((fam) => {
      const group = gens.filter((g) => g.family === fam.key);
      if (!group.length) return "";
      const opts = group
        .map(
          (g) =>
            `<option value="${esc(g.key)}"${g.key === (chosen || {}).key ? " selected" : ""}` +
            ` title="${esc(g.tag)}">` +
            `${esc(g.label || g.tag)} · ${esc(g.generator)}</option>`
        )
        .join("");
      return `<optgroup label="${esc(fam.label)}">${opts}</optgroup>`;
    })
    .join("");
}

function side(text, cls, label, emptyLabel) {
  if (!text) {
    return (
      `<div class="answer ${cls} absent">` +
      `<div class="answer-by">${label}</div>` +
      `<p class="answer-text">${esc(emptyLabel)}</p>` +
      `</div>`
    );
  }
  return (
    `<div class="answer ${cls}">` +
    `<div class="answer-by">${label}</div>` +
    `<p class="answer-text">${esc(text)}</p>` +
    `<div class="answer-len">${words(text)} words</div>` +
    `</div>`
  );
}

function generatorName(tag) {
  const g = (state.payload.generators || []).find((x) => x.tag === tag);
  return g ? g.generator : tag;
}

function modeVerb(mode) {
  const g = (state.payload.generators || []).find((x) => x.mode === mode);
  return g ? g.verb : mode;
}

/* ---------- ---------- */

function render() {
  renderTabs();
  renderIntro();
  renderRespondents();
}

boot();
