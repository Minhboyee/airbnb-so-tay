(() => {
  const $ = (s) => document.querySelector(s);
  const fmt = (n, d = 0) => n.toLocaleString("vi-VN", { minimumFractionDigits: d, maximumFractionDigits: d });

  /* ---------- sáng / tối ---------- */
  const root = document.documentElement;
  try { const t = localStorage.getItem("theme"); if (t) root.dataset.theme = t; } catch (e) {}
  $("#theme").addEventListener("click", () => {
    const cur = root.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
  });

  /* ---------- tab + link nội bộ ---------- */
  const views = [...document.querySelectorAll("[data-view]")];
  const tabs = [...document.querySelectorAll(".tabs a")];
  function openBlk(b, on) {
    const ex = b.querySelector(":scope > .expl");
    if (!ex) return;
    const open = on ?? ex.hidden;
    ex.hidden = !open;
    b.classList.toggle("open", open);
    b.querySelector(":scope > .lines").setAttribute("aria-expanded", open);
  }
  function go(id) {
    let t = id && document.getElementById(id);
    // link sinh động (#file-L85) có thể rơi giữa khối: lùi về dòng đầu khối chứa nó
    const m = !t && /^(.+)-L(\d+)$/.exec(id || "");
    if (m) for (let n = +m[2]; n > 0 && !t; n--) t = document.getElementById(`${m[1]}-L${n}`);
    t = t || views[0];
    const view = t.closest("[data-view]") || views[0];
    views.forEach((v) => (v.hidden = v !== view));
    tabs.forEach((a) => {
      const on = a.getAttribute("href") === "#" + view.id;
      a.setAttribute("aria-current", on ? "page" : "false");
      if (on) a.scrollIntoView({ block: "nearest", inline: "nearest" });
    });
    if (t.classList.contains("blk")) openBlk(t, true);
    if (t === view) scrollTo(0, 0);
    else t.scrollIntoView({ block: "start" });
    requestAnimationFrame(spy);
  }
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    e.preventDefault();
    const id = a.getAttribute("href").slice(1);
    if (location.hash !== "#" + id) history.pushState(null, "", "#" + id);
    go(id);
  });
  addEventListener("popstate", () => go(location.hash.slice(1)));
  addEventListener("hashchange", () => go(location.hash.slice(1)));

  /* ---------- bấm dòng mở giải thích ---------- */
  document.addEventListener("click", (e) => {
    const l = e.target.closest(".lines");
    if (!l || String(getSelection())) return;
    openBlk(l.parentElement);
  });
  document.addEventListener("keydown", (e) => {
    const l = e.target.closest?.(".lines");
    if (l && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openBlk(l.parentElement); }
  });
  document.querySelectorAll("[data-all]").forEach((b) =>
    b.addEventListener("click", () => {
      const open = b.dataset.all === "open";
      b.closest(".filesec").querySelectorAll(".blk").forEach((x) => openBlk(x, open));
    }));

  /* ---------- pane luồng: tô bước đang đọc (mỗi file một pane) ---------- */
  let spyQueued = false;
  function spy() {
    spyQueued = false;
    const view = views.find((v) => !v.hidden);
    if (!view) return;
    for (const pane of view.querySelectorAll(".flowpane")) {
      const split = pane.closest(".split");
      const sr = split.getBoundingClientRect();
      if (sr.bottom < 0 || sr.top > innerHeight) continue;
      const items = [...pane.querySelectorAll(".fp")];
      let cur = null, top = -Infinity;
      for (const a of items) {
        const t = document.getElementById(a.getAttribute("href").slice(1));
        const y = t && split.contains(t) ? t.getBoundingClientRect().top : Infinity;
        if (y <= innerHeight * 0.4 && y > top) { top = y; cur = a; }
      }
      items.forEach((a) => a.classList.toggle("on", a === cur));
      if (cur && getComputedStyle(pane).position === "sticky") {
        const r = cur.getBoundingClientRect(), pr = pane.getBoundingClientRect();
        if (r.top < pr.top || r.bottom > pr.bottom) pane.scrollTop += r.top - pr.top - pr.height / 3;
      }
    }
  }
  addEventListener("scroll", () => { if (!spyQueued) { spyQueued = true; requestAnimationFrame(spy); } }, { passive: true });
  document.addEventListener("click", () => requestAnimationFrame(spy));

  /* ---------- hỏi đáp: mở/đóng hết ---------- */
  document.querySelectorAll("[data-qa]").forEach((b) =>
    b.addEventListener("click", () => {
      const open = b.dataset.qa === "open";
      document.querySelectorAll("details.qa").forEach((d) => (d.open = open));
    }));

  /* ---------- máy phân nhóm: bản sao classify() trong src/segments/rules.py ---------- */
  const seg = $("#seg-form");
  if (seg) {
    const NAMES = {
      B_ghost: "Khoá lịch, không review", B_booked: "Kín lịch, vẫn có review", D_dormant: "Ngủ đông",
      D_never: "Chưa từng có review", N_new: "Mới / chưa đủ dữ liệu", L_low: "Mở nhiều, ít review", H_healthy: "Khoẻ mạnh",
    };
    const PHANTOM = new Set(["B_ghost", "D_dormant", "D_never"]);
    const LINE = { B_ghost: 85, B_booked: 86, D_dormant: 87, D_never: 88, N_new: 89, L_low: 90, H_healthy: 93 };
    const val = (id) => $(id).value.trim();
    function run() {
      const avail = Number(val("#sg-avail")) || 0;
      const nrev = Number(val("#sg-nrev")) || 0;
      const ltm = Number(val("#sg-ltm")) || 0;
      const daysRaw = val("#sg-days");
      const days = daysRaw === "" || nrev === 0 ? NaN : Number(daysRaw);
      const seen = $("#sg-seen").value;
      const hasRecent = days <= 365; // NaN <= 365 là false, đúng như pandas
      const blocked = avail <= 0;
      const isSeen = seen === "yes";
      const conds = [
        ["B_ghost", blocked && !hasRecent, `availability_365 = ${avail} ≤ 0 và không có review trong 365 ngày`],
        ["B_booked", blocked && hasRecent, `availability_365 = ${avail} ≤ 0 và có review trong 365 ngày`],
        ["D_dormant", nrev > 0 && !hasRecent, `number_of_reviews = ${nrev} > 0 nhưng review cuối cách ${isNaN(days) ? "?" : days} ngày (> 365)`],
        ["D_never", nrev === 0 && isSeen, "0 review và id đã có ở mốc cách ≥ 150 ngày"],
        ["N_new", nrev === 0, seen === "none" ? "0 review, và không có mốc nào đủ cũ để so (seen_before = None)" : "0 review, id chưa thấy ở mốc đủ cũ"],
        ["L_low", avail >= 180 && ltm >= 1 && ltm <= 3, `availability_365 = ${avail} ≥ 180 và ${ltm} review trong 12 tháng (1–3)`],
      ];
      const rows = [];
      let hit = null;
      for (const [k, ok, why] of conds) {
        if (hit) { rows.push(`<li class="skip"><code>${k}</code> không xét nữa</li>`); continue; }
        if (ok) { hit = [k, why]; rows.push(`<li class="hit"><code>${k}</code> đúng: ${why}</li>`); }
        else rows.push(`<li class="miss"><code>${k}</code> sai</li>`);
      }
      if (!hit) { hit = ["H_healthy", "không điều kiện nào ở trên đúng"]; rows.push(`<li class="hit"><code>H_healthy</code> mặc định</li>`); }
      const [k] = hit;
      $("#seg-out").innerHTML =
        `<p class="seg-res"><span class="segtag ${PHANTOM.has(k) ? "ph" : ""}">${k}</span> ${NAMES[k]}${PHANTOM.has(k) ? " · <b>căn ảo</b>" : ""}</p>` +
        `<ol class="seg-steps">${rows.join("")}</ol>` +
        `<p class="muted">Điều kiện tương ứng trong code: <a href="#seg_rules-L${LINE[k]}">rules.py dòng ${LINE[k]}</a>.</p>`;
      $("#sg-days").disabled = nrev === 0;
    }
    seg.addEventListener("input", run);
    seg.querySelectorAll("[data-preset]").forEach((b) => b.addEventListener("click", () => {
      const [a, n, l, d, s] = b.dataset.preset.split(",");
      $("#sg-avail").value = a; $("#sg-nrev").value = n; $("#sg-ltm").value = l; $("#sg-days").value = d; $("#sg-seen").value = s;
      run();
    }));
    run();
  }

  /* ---------- IQR: bản sao luật price_outlier ---------- */
  const iqr = $("#iqr-in");
  if (iqr) {
    const q = (s, p) => { // nội suy tuyến tính như pandas.quantile mặc định
      const pos = (s.length - 1) * p, lo = Math.floor(pos), hi = Math.ceil(pos);
      return s[lo] + (s[hi] - s[lo]) * (pos - lo);
    };
    function runIqr() {
      const xs = iqr.value.split(/[\s,;]+/).map(Number).filter((x) => Number.isFinite(x)).sort((a, b) => a - b);
      const k = Number($("#iqr-k").value) || 3;
      $("#iqr-k-v").textContent = fmt(k, 1);
      if (xs.length < 4) { $("#iqr-out").innerHTML = "<p>Cần ít nhất 4 giá.</p>"; return; }
      const q1 = q(xs, 0.25), q3 = q(xs, 0.75), r = q3 - q1, lo = q1 - k * r, hi = q3 + k * r;
      const out = xs.filter((x) => x < lo || x > hi);
      $("#iqr-out").innerHTML =
        `<div class="stats"><span>Q1 <b>${fmt(q1, 1)}</b></span><span>Q3 <b>${fmt(q3, 1)}</b></span><span>IQR <b>${fmt(r, 1)}</b></span>` +
        `<span>Khoảng hợp lệ <b>[${fmt(lo, 1)}; ${fmt(hi, 1)}]</b></span></div>` +
        `<p>${out.length ? `Gắn cờ cảnh báo <code>price_outlier</code>: <b>${out.map((x) => fmt(x)).join(", ")}</b>` : "Không giá nào bị gắn cờ."}</p>`;
    }
    iqr.addEventListener("input", runIqr);
    $("#iqr-k").addEventListener("input", runIqr);
    runIqr();
  }

  go(location.hash.slice(1) || "cau-chuyen");
})();
