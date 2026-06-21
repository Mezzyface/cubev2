const DIR = window.DIR || "pngs/";
const CARDS = window.CARDS || [];
const ORDER = window.COLOR_ORDER || ["yellow", "green", "red", "blue", "purple"];
const COLHEX = { yellow:"#e2b53c", green:"#4a9d3f", red:"#d8443f", blue:"#3a78c2", purple:"#8a5cc4", unknown:"#666" };
const grid = document.getElementById("grid");
const src = f => DIR + encodeURIComponent(f);
let sortMode = "name", activeColor = "all", view = [];

const ci = c => { const i = ORDER.indexOf(c); return i < 0 ? 99 : i; };
function sorted() {
  const list = CARDS.filter(c => activeColor === "all" || c.color === activeColor);
  const by = {
    name: (a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }),
    color: (a, b) => ci(a.color) - ci(b.color) || (a.level ?? 9) - (b.level ?? 9) || a.name.localeCompare(b.name),
    levelup: (a, b) => (a.level ?? 9) - (b.level ?? 9) || ci(a.color) - ci(b.color) || a.name.localeCompare(b.name),
    leveldown: (a, b) => (b.level ?? -1) - (a.level ?? -1) || ci(a.color) - ci(b.color) || a.name.localeCompare(b.name),
  };
  return list.sort(by[sortMode]);
}
function render() {
  view = sorted();
  grid.innerHTML = "";
  view.forEach((c, i) => {
    const el = document.createElement("div");
    el.className = "card";
    const lvl = c.level == null ? "" : '<span class="lvl">Lv ' + c.level + "</span>";
    el.innerHTML =
      '<div class="imgwrap"><img loading="lazy" src="' + src(c.file) + '" alt="' + c.name + '"></div>' +
      '<div class="cap"><span class="cdot" style="background:' + COLHEX[c.color] + '"></span>' + c.name + lvl + "</div>";
    el.addEventListener("click", () => openLb(i));
    grid.appendChild(el);
  });
  document.getElementById("count").textContent = view.length + " cards";
}
document.getElementById("sort").addEventListener("change", e => { sortMode = e.target.value; render(); });
document.getElementById("size").addEventListener("input", e => {
  document.documentElement.style.setProperty("--tile", e.target.value + "px");
});
document.querySelectorAll(".chip").forEach(ch => ch.addEventListener("click", () => {
  document.querySelectorAll(".chip").forEach(x => x.classList.remove("active"));
  ch.classList.add("active");
  activeColor = ch.dataset.color;
  render();
}));

const lb = document.getElementById("lb"), lbImg = document.getElementById("lbImg"), lbCap = document.getElementById("lbCap");
let cur = 0;
const openLb = i => { cur = i; show(); lb.classList.add("open"); };
const closeLb = () => lb.classList.remove("open");
const stepLb = d => { cur = (cur + d + view.length) % view.length; show(); };
function show() {
  const c = view[cur];
  lbImg.src = src(c.file);
  lbImg.alt = c.name;
  lbCap.textContent = c.name + (c.level == null ? "" : "  ·  Lv " + c.level);
}
document.getElementById("lbClose").addEventListener("click", closeLb);
document.getElementById("lbPrev").addEventListener("click", e => { e.stopPropagation(); stepLb(-1); });
document.getElementById("lbNext").addEventListener("click", e => { e.stopPropagation(); stepLb(1); });
lb.addEventListener("click", e => { if (e.target === lb) closeLb(); });
document.addEventListener("keydown", e => {
  if (!lb.classList.contains("open")) return;
  if (e.key === "Escape") closeLb();
  else if (e.key === "ArrowLeft") stepLb(-1);
  else if (e.key === "ArrowRight") stepLb(1);
});
render();
