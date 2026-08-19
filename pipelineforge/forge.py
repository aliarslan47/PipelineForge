"""PipelineForge — spec (YAML) → standart "Pipeline DAG" HTML üreticisi.

Forge ailesinin (RNAForge, VirusForge, BacForge, ...) tek-tornadan çıkmış pipeline
şemalarını üretir: elle-çizilmiş inline SVG node-graph, nokta-ızgara canvas, tiplenmiş
kartlar (kod çipi + ad + araç + portlar), eğri bezier oklar, karar düğümü, TR/EN toggle,
modül matrisi tablosu, izole ortam listesi. İskelet RNAForge referansından sabittir;
graf içeriği ve palet spec'ten gelir. Kenarlar projenin gerçek run() bağımlılıklarıdır.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# ---- sabit geometri (aile standardı) ----
NODE_W = 190
NODE_H = 56
CHIP_W = 40
CHIP_H = 18

# ---- sabit renk paleti: kategori ROLLERİ (mavi=ortak sabittir; yeşil/amber/mor dallar) ----
# Her rengin light/dark tonu + kart-arkaplanı. Kategori adları projeye özgü, renkler ortak.
COLORS = {
    "blue":   dict(light="#0d6b8f", dark="#4bb3d6", bg_light="#e7f0f5", bg_dark="#12303c"),
    "green":  dict(light="#2f8f5b", dark="#5cc08a", bg_light="#e4f1ea", bg_dark="#15321f"),
    "amber":  dict(light="#c07211", dark="#e0a24e", bg_light="#f7ecdb", bg_dark="#3a2c16"),
    "purple": dict(light="#7d6fae", dark="#a99bd0", bg_light="#eeeaf6", bg_dark="#221d33"),
}
DEC_LIGHT, DEC_DARK = "#8a5cd0", "#b28cf0"

# port normalleri (dışa doğru)
_NORMAL = {"top": (0, -1), "bottom": (0, 1), "left": (-1, 0), "right": (1, 0)}


@dataclass
class Node:
    code: str
    tr: str
    en: str
    tool: str
    cat: str
    lane: str
    y: float
    dep: str = "—"
    tag: str | None = None       # tabloda kategori yerine özel etiket (ör. HUB)

    x: float = 0.0               # layout'ta doldurulur (kart sol-x)
    cx: float = 0.0              # merkez-x

    def port(self, name: str) -> tuple[float, float]:
        if name == "top":
            return (self.cx, self.y)
        if name == "bottom":
            return (self.cx, self.y + NODE_H)
        if name == "left":
            return (self.x, self.y + NODE_H / 2)
        if name == "right":
            return (self.x + NODE_W, self.y + NODE_H / 2)
        raise ValueError(f"bilinmeyen port: {name}")


@dataclass
class Decision:
    at: tuple[float, float]       # merkez (cx, cy)
    tr_label: str
    tr_sub: str
    en_label: str
    en_sub: str
    hw: float = 46                # yarı-genişlik
    hh: float = 28                # yarı-yükseklik

    def port(self, name: str) -> tuple[float, float]:
        cx, cy = self.at
        return {
            "top": (cx, cy - self.hh),
            "bottom": (cx, cy + self.hh),
            "left": (cx - self.hw, cy),
            "right": (cx + self.hw, cy),
        }[name]


@dataclass
class Edge:
    src: str                      # düğüm kodu ya da "decision"
    dst: str
    cat: str                      # renk kategorisi
    from_port: str = "bottom"
    to_port: str = "top"
    d: str | None = None          # ham path override (zor yollar için)


@dataclass
class Spec:
    name: str
    title: str
    filename: str
    repo: str
    favicon: str
    subtitle_tr: str
    subtitle_en: str
    footer_tr: str
    footer_en: str
    lanes: dict                   # lane adı -> merkez x
    viewbox: tuple[int, int]
    categories: dict              # kat adı -> {color, tr, en, dashed}
    nodes: list                   # Node
    edges: list                   # Edge
    envs: list
    decision: Decision | None = None
    hub_label: dict | None = None # {at:[x,y], tr, en}
    aria_tr: str = ""
    aria_en: str = ""


# --------------------------------------------------------------------------- #
# bezier router
# --------------------------------------------------------------------------- #
def _bezier(p0, n0, p3, n3) -> str:
    (x0, y0), (x3, y3) = p0, p3
    dist = math.hypot(x3 - x0, y3 - y0)
    k = max(26.0, 0.42 * dist)
    c1 = (x0 + n0[0] * k, y0 + n0[1] * k)
    c2 = (x3 + n3[0] * k, y3 + n3[1] * k)
    return (f"M{x0:.0f} {y0:.0f} C{c1[0]:.0f} {c1[1]:.0f} "
            f"{c2[0]:.0f} {c2[1]:.0f} {x3:.0f} {y3:.0f}")


def _resolve(spec: Spec):
    """lane -> x, node index kur."""
    by_code = {}
    for n in spec.nodes:
        n.cx = spec.lanes[n.lane]
        n.x = n.cx - NODE_W / 2
        by_code[n.code] = n
    return by_code


def _edge_path(spec: Spec, by_code, e: Edge) -> str:
    if e.d:
        return e.d
    src = spec.decision if e.src == "decision" else by_code[e.src]
    dst = spec.decision if e.dst == "decision" else by_code[e.dst]
    p0, p3 = src.port(e.from_port), dst.port(e.to_port)
    return _bezier(p0, _NORMAL[e.from_port], p3, _NORMAL[e.to_port])


# --------------------------------------------------------------------------- #
# CSS
# --------------------------------------------------------------------------- #
def _css(spec: Spec) -> str:
    def cat_vars(theme):  # theme 'light'|'dark'
        out = []
        for key, c in spec.categories.items():
            col = COLORS[c["color"]]
            out.append(f"--{key}:{col[theme]}; --{key}-bg:{col['bg_'+theme]};")
        return " ".join(out)

    light = cat_vars("light")
    dark = cat_vars("dark")

    # kategori-türevli sınıflar
    cls = []
    for key, c in spec.categories.items():
        dash = "stroke-dasharray:5 4;stroke-width:1.6;" if c.get("dashed") else ""
        cls.append(f"""  .n-{key}{{stroke:var(--{key});stroke-width:1.6}}
  .chip-{key}{{fill:var(--{key})}}
  .port-{key}{{fill:var(--{key});stroke:var(--node);stroke-width:1.5}}
  .e-{key}{{stroke:var(--{key});{dash}}}
  .i-{key}{{background:var(--{key}-bg);border-color:var(--{key})}}
  .tag.{key}{{background:var(--{key}-bg);color:var(--{key})}}""")
    cls = "\n".join(cls)

    # ilk kategori rengini "vurgu" (toggle, badge) olarak kullan
    first = next(iter(spec.categories))

    return f""":root{{
    --bg:#eef1f4; --card:#ffffff; --node:#ffffff; --bd:#dfe4e9; --ink:#161b21; --mut:#69737d;
    --grid:#dbe1e7; --dec:{DEC_LIGHT}; --na-tx:#96a0a9;
    {light}
  }}
  @media (prefers-color-scheme: dark){{
    :root:not([data-theme="light"]){{
      --bg:#0c1014; --card:#141920; --node:#1b2129; --bd:#28303a; --ink:#e7ebef; --mut:#8a95a0;
      --grid:#20272f; --dec:{DEC_DARK}; --na-tx:#5c6771;
      {dark}
    }}
  }}
  :root[data-theme="dark"]{{
    --bg:#0c1014; --card:#141920; --node:#1b2129; --bd:#28303a; --ink:#e7ebef; --mut:#8a95a0;
    --grid:#20272f; --dec:{DEC_DARK}; --na-tx:#5c6771;
    {dark}
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);
    font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;padding:30px 22px 38px}}
  .wrap{{max-width:1180px;margin:0 auto}}
  .toggle{{display:flex;justify-content:flex-end;margin-bottom:14px}}
  .toggle .grp{{display:inline-flex;border:1px solid var(--bd);border-radius:999px;overflow:hidden;background:var(--card)}}
  .langbtn{{border:0;background:transparent;color:var(--mut);font:600 12.5px system-ui;
    padding:6px 16px;cursor:pointer;letter-spacing:.3px}}
  .langbtn.on{{background:var(--{first});color:#fff}}
  .langbtn:focus-visible{{outline:2px solid var(--{first});outline-offset:2px}}
  header{{margin-bottom:22px}}
  h1{{font-size:26px;margin:0 0 6px;letter-spacing:-.4px;text-wrap:balance}}
  .sub{{color:var(--mut);font-size:13.5px;margin:0;max-width:74ch}}
  .mono{{font-family:ui-monospace,"SF Mono",Menlo,monospace}}
  h2{{font-size:15.5px;margin:32px 0 12px;letter-spacing:-.2px}}
  .page[hidden]{{display:none}}
  .canvas{{position:relative;background:var(--card);border:1px solid var(--bd);border-radius:14px;
    box-shadow:0 1px 3px rgba(0,0,0,.05);overflow:auto;max-height:84vh}}
  .bar{{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:12px;
    padding:9px 14px;background:var(--card);border-bottom:1px solid var(--bd)}}
  .bar .fn{{font-family:ui-monospace,monospace;font-size:12px;color:var(--mut)}}
  .bar .dot{{width:9px;height:9px;border-radius:50%;display:inline-block}}
  .bar .sp{{flex:1}}
  .chips{{display:flex;gap:12px;font-size:11.5px;flex-wrap:wrap}}
  .chips span{{display:inline-flex;align-items:center;gap:6px;color:var(--mut)}}
  .chips i{{width:11px;height:11px;border-radius:3px;display:inline-block;border:1.4px solid}}
  .chips i.dash{{border-style:dashed}}
  svg.dag{{display:block;min-width:{spec.viewbox[0]}px}}
  .node{{fill:var(--node)}}
  .chip-t{{fill:#fff;font-family:ui-monospace,monospace;font-weight:700;font-size:11px}}
  .nname{{fill:var(--ink);font-size:12.5px;font-weight:600}}
  .ntool{{fill:var(--mut);font-size:9.5px;font-family:ui-monospace,monospace}}
  .edge{{fill:none;stroke-width:1.9}}
  .decision{{fill:var(--node);stroke:var(--dec);stroke-width:1.6}}
  .dec-t{{fill:var(--dec);font-size:11px;font-weight:700;font-family:ui-monospace,monospace}}
  .dec-s{{fill:var(--mut);font-size:9px}}
  .hublbl{{fill:var(--mut);font-size:9.5px;font-style:italic}}
{cls}
  .tbl-wrap{{overflow-x:auto;border:1px solid var(--bd);border-radius:12px;background:var(--card);margin-top:12px}}
  table{{width:100%;border-collapse:collapse;min-width:680px}}
  th,td{{text-align:left;padding:9px 13px;border-bottom:1px solid var(--bd);font-size:13px;vertical-align:top}}
  thead th{{background:var(--{first}-bg);color:var(--{first});font-size:11px;letter-spacing:.4px;text-transform:uppercase}}
  tbody tr:last-child td{{border-bottom:none}}
  td.code{{font-family:ui-monospace,monospace;font-weight:700;color:var(--{first});white-space:nowrap}}
  td.mod{{font-weight:600;white-space:nowrap}}
  td.dep{{font-family:ui-monospace,monospace;font-size:12px;color:var(--mut);white-space:nowrap}}
  .tag{{display:inline-block;font-size:10px;font-weight:700;padding:1px 7px;border-radius:999px;margin-left:6px}}
  .envs{{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}}
  .env{{font-family:ui-monospace,monospace;font-size:12px;background:var(--card);border:1px solid var(--bd);
    border-radius:7px;padding:4px 10px}}
  .env b{{color:var(--{first})}}
  footer{{margin-top:28px;padding-top:15px;border-top:1px solid var(--bd);color:var(--mut);font-size:12px}}"""


# --------------------------------------------------------------------------- #
# SVG
# --------------------------------------------------------------------------- #
def _svg(spec: Spec, by_code, lang: str, suffix: str) -> str:
    W, H = spec.viewbox
    aria = spec.aria_tr if lang == "tr" else spec.aria_en
    parts = [
        f'<svg class="dag" viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">',
        f'  <defs>',
        f'    <pattern id="grid-{suffix}" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.1" fill="var(--grid)"/></pattern>',
        f'    <marker id="ah-{suffix}" markerWidth="8" markerHeight="8" refX="5.5" refY="3" '
        f'orient="auto"><polygon points="0 0, 6 3, 0 6" fill="context-stroke"/></marker>',
        f'  </defs>',
        f'  <rect x="0" y="0" width="{W}" height="{H}" fill="url(#grid-{suffix})"/>',
    ]
    # kenarlar
    for e in spec.edges:
        d = _edge_path(spec, by_code, e)
        parts.append(f'  <path class="edge e-{e.cat}" marker-end="url(#ah-{suffix})" d="{d}"/>')
    # düğümler
    for n in spec.nodes:
        name = n.tr if lang == "tr" else n.en
        cx = n.cx
        parts.append(
            f'  <g><rect class="node n-{n.cat}" x="{n.x:.0f}" y="{n.y:.0f}" width="{NODE_W}" '
            f'height="{NODE_H}" rx="11"/>'
            f'<rect class="chip-{n.cat}" x="{n.x+10:.0f}" y="{n.y+10:.0f}" width="{CHIP_W}" '
            f'height="{CHIP_H}" rx="5"/>'
            f'<text class="chip-t" x="{n.x+30:.0f}" y="{n.y+23:.0f}" text-anchor="middle">{n.code}</text>'
            f'<text class="nname" x="{n.x+58:.0f}" y="{n.y+24:.0f}">{name}</text>'
            f'<text class="ntool" x="{n.x+12:.0f}" y="{n.y+45:.0f}">{n.tool}</text>'
            f'<circle class="port-{n.cat}" cx="{cx:.0f}" cy="{n.y:.0f}" r="4"/>'
            f'<circle class="port-{n.cat}" cx="{cx:.0f}" cy="{n.y+NODE_H:.0f}" r="4"/></g>'
        )
    # karar düğümü
    if spec.decision:
        d = spec.decision
        cx, cy = d.at
        label = d.tr_label if lang == "tr" else d.en_label
        sub = d.tr_sub if lang == "tr" else d.en_sub
        pts = f"{cx:.0f} {cy-d.hh:.0f} {cx+d.hw:.0f} {cy:.0f} {cx:.0f} {cy+d.hh:.0f} {cx-d.hw:.0f} {cy:.0f}"
        parts.append(
            f'  <g><path class="decision" d="M{cx:.0f} {cy-d.hh:.0f} L{cx+d.hw:.0f} {cy:.0f} '
            f'L{cx:.0f} {cy+d.hh:.0f} L{cx-d.hw:.0f} {cy:.0f} Z"/>'
            f'<text class="dec-t" x="{cx:.0f}" y="{cy-3:.0f}" text-anchor="middle">{label}</text>'
            f'<text class="dec-s" x="{cx:.0f}" y="{cy+11:.0f}" text-anchor="middle">{sub}</text></g>'
        )
    # hub etiketi
    if spec.hub_label:
        hl = spec.hub_label
        txt = hl["tr"] if lang == "tr" else hl["en"]
        parts.append(f'  <text class="hublbl" x="{hl["at"][0]}" y="{hl["at"][1]}" '
                     f'text-anchor="middle">{txt}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# tablo + lejant + sayfa
# --------------------------------------------------------------------------- #
def _legend(spec: Spec, lang: str) -> str:
    out = []
    for key, c in spec.categories.items():
        lbl = c["tr"] if lang == "tr" else c["en"]
        dash = " dash" if c.get("dashed") else ""
        out.append(f'          <span><i class="i-{key}{dash}"></i> {lbl}</span>')
    return "\n".join(out)


def _table(spec: Spec, lang: str) -> str:
    if lang == "tr":
        hdr = ["Kod", "Modül", "Bağımlılık", "Araç &amp; işlev"]
        h2 = "Modül matrisi — araçlar &amp; bağımlılık"
    else:
        hdr = ["Code", "Module", "Depends", "Tool &amp; function"]
        h2 = "Module matrix — tools &amp; dependency"
    rows = []
    for n in spec.nodes:
        name = n.tr if lang == "tr" else n.en
        cat = spec.categories[n.cat]
        tag_lbl = n.tag if n.tag else (cat["tr"] if lang == "tr" else cat["en"]).upper()
        rows.append(
            f'        <tr><td class="code">{n.code}</td>'
            f'<td class="mod">{name} <span class="tag {n.cat}">{tag_lbl}</span></td>'
            f'<td class="dep">{n.dep}</td><td>{n.tool}</td></tr>'
        )
    return (f'    <h2>{h2}</h2>\n    <div class="tbl-wrap"><table>\n'
            f'      <thead><tr><th style="width:52px">{hdr[0]}</th>'
            f'<th style="width:170px">{hdr[1]}</th><th style="width:110px">{hdr[2]}</th>'
            f'<th>{hdr[3]}</th></tr></thead>\n      <tbody>\n' + "\n".join(rows) +
            '\n      </tbody>\n    </table></div>')


def _page(spec: Spec, by_code, lang: str) -> str:
    hidden = "" if lang == "tr" else " hidden"
    suffix = lang
    subtitle = spec.subtitle_tr if lang == "tr" else spec.subtitle_en
    footer = spec.footer_tr if lang == "tr" else spec.footer_en
    envs_h2 = "İzole conda ortamları" if lang == "tr" else "Isolated conda environments"
    main_lbl = "ana" if lang == "tr" else "main"
    envs = ""
    for i, ev in enumerate(spec.envs):
        tail = f" · {main_lbl}" if i == 0 else ""
        envs += f'<span class="env"><b>{ev}</b>{tail}</span>'
    svg = _svg(spec, by_code, lang, suffix)
    return f"""  <div class="page" data-lang="{lang}"{hidden}>
    <header>
      <h1>{spec.title}</h1>
      <p class="sub">{subtitle}</p>
    </header>

    <figure style="margin:0">
    <div class="canvas">
      <div class="bar">
        <span class="dot" style="background:#e0605a"></span>
        <span class="dot" style="background:#e0b64e"></span>
        <span class="dot" style="background:#5bb87a"></span>
        <span class="fn">{spec.filename}</span>
        <span class="sp"></span>
        <span class="chips">
{_legend(spec, lang)}
        </span>
      </div>
      {svg}
    </div>
    </figure>

{_table(spec, lang)}

    <h2>{envs_h2}</h2>
    <div class="envs">
      {envs}
    </div>
    <footer>{footer}</footer>
  </div>"""


_SCRIPT = """<script>
  (function(){
    var btns = document.querySelectorAll('.langbtn');
    var pages = document.querySelectorAll('.page');
    btns.forEach(function(b){
      b.addEventListener('click', function(){
        var l = b.getAttribute('data-lang');
        btns.forEach(function(x){
          var on = x.getAttribute('data-lang') === l;
          x.classList.toggle('on', on);
          x.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        pages.forEach(function(p){ p.hidden = (p.getAttribute('data-lang') !== l); });
      });
    });
  })();
</script>"""


def render(spec: Spec) -> str:
    by_code = _resolve(spec)
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{spec.title}</title>
<style>
  {_css(spec)}
</style>
</head>
<body>

<div class="wrap">
  <div class="toggle">
    <div class="grp" role="group" aria-label="Language / Dil">
      <button class="langbtn on" data-lang="tr" aria-pressed="true">Türkçe</button>
      <button class="langbtn" data-lang="en" aria-pressed="false">English</button>
    </div>
  </div>

{_page(spec, by_code, 'tr')}

{_page(spec, by_code, 'en')}
</div>

{_SCRIPT}
</body>
</html>
"""


def validate(html: str) -> dict:
    """kaba yapısal doğrulama; sözlük döner, sorun varsa 'errors' dolu."""
    import re
    errors = []
    for tag in ["svg", "table", "figure", "div", "g"]:
        o = len(re.findall(rf"<{tag}[ >]", html))
        c = len(re.findall(rf"</{tag}>", html))
        if o != c:
            errors.append(f"{tag}: open={o} close={c}")
    if "�" in html:
        errors.append("bozuk karakter (U+FFFD) var")
    nodes = html.count('class="node n-') // 2
    edges = html.count('class="edge e-') // 2
    return dict(errors=errors, nodes_per_page=nodes, edges_per_page=edges)
