"""Gera os quadros do vídeo: um editor claro estilo VS Code com o código REAL de ../../codigo
e a saída REAL de `npm run` (capture/run/*.txt). Sem narração e sem legendas.

Cada quadro é um <template> com prefixo próprio (f1-, f2-, ...) em classes e ids.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT.parent.parent / "codigo"
RUN = ROOT / "capture" / "run"
OUT = ROOT / "compositions" / "frames"
FONT_BASE = "../../assets/fonts"

W, H = 1920, 1080
TITLE_H, TABS_H, STATUS_H, SIDE_W = 48, 50, 34, 400
FS, LH, GUT = 24, 38, 74          # editor: fonte, altura da linha, largura da calha
TFS, TLH = 21, 30                 # terminal
ED_TOP = TITLE_H + TABS_H         # topo do editor
ED_PAD = 18
TERM_TOP = 590                    # topo do terminal quando aberto
TERM_H = H - STATUS_H - TERM_TOP

# ── realce de sintaxe (mesmas cores do deck) ──────────────────────────────────
KW = set("import from export type interface class implements async await const let return new if else throw function try catch of in".split())
TY = set("string number Buffer Promise Record".split())
TOK = re.compile(r"(//.*)|(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_$][\w$]*\b)")


def hl(src, p):
    out, last = [], 0
    for m in TOK.finditer(src):
        out.append(html.escape(src[last:m.start()], quote=False))
        last = m.end()
        t = html.escape(m.group(0), quote=False)
        if m.group(1):
            cls = "c"
        elif m.group(2):
            cls = "s"
        elif m.group(3):
            cls = "n"
        elif m.group(0) in KW:
            cls = "k"
        elif m.group(0) in TY or m.group(0)[0].isupper():
            cls = "t"
        else:
            out.append(t)
            continue
        out.append(f'<span class="{p}-{cls}">{t}</span>')
    out.append(html.escape(src[last:], quote=False))
    return "".join(out)


def term_hl(line, p):
    """Cores parecidas com as do Node no terminal."""
    e = html.escape(line, quote=False)
    if line.startswith(">"):
        return f'<span class="{p}-dim">{e}</span>'
    if line.startswith("✓"):
        return f'<span class="{p}-ok">{e}</span>'
    if line.startswith("✗"):
        return f'<span class="{p}-err">{e}</span>'
    e = re.sub(r"(&#x27;|')(.*?)(&#x27;|')", lambda m: f'<span class="{p}-s">\'{m.group(2)}\'</span>', e)
    e = re.sub(r"(?<![\w-])(\d+)(?![\w-])", lambda m: f'<span class="{p}-n">{m.group(1)}</span>', e)
    return e


def read(rel):
    return (CODE / rel).read_text(encoding="utf-8").rstrip("\n").split("\n")


def run_out(name):
    lines = (RUN / name).read_text(encoding="utf-8").rstrip("\n").split("\n")
    return [l for l in lines][1:] if lines and lines[0] == "" else lines


# ── explorador ────────────────────────────────────────────────────────────────
TREE = [
    (0, "dir", "data"), (1, "file", "data/extrato.csv"), (1, "file", "data/extrato.ofx"), (1, "file", "data/extrato.xlsx"),
    (0, "dir", "src"), (1, "dir", "src/adapters"),
    (2, "file", "src/adapters/csv.adapter.ts"), (2, "file", "src/adapters/excel.adapter.ts"), (2, "file", "src/adapters/ofx.adapter.ts"),
    (1, "file", "src/adapter-resolver.ts"), (1, "file", "src/comparar.ts"), (1, "file", "src/import-file.ts"), (1, "file", "src/main.ts"),
    (1, "file", "src/transaction-file-adapter.ts"), (1, "file", "src/transaction-import-service.ts"), (1, "file", "src/transaction.ts"),
    (0, "file", "package.json"),
]
ROW_H = 36


def explorer(p, hide_csv, badges=None):
    badges = badges or {}
    rows, y = [], 0
    for depth, kind, path in TREE:
        name = path.split("/")[-1]
        rid = f"{p}-x-" + re.sub(r"[^a-z0-9]", "-", path.lower())
        hidden = hide_csv and path.endswith("csv.adapter.ts")
        icon = "▾" if kind == "dir" else ("TS" if name.endswith(".ts") else "{}" if name.endswith(".json") else "≡")
        icls = "d" if kind == "dir" else ("ts" if name.endswith(".ts") else "f")
        style = f"top:{y}px;padding-left:{22 + depth * 22}px" + (";opacity:0" if hidden else "")
        rows.append(f'<div class="{p}-xr" id="{rid}" style="{style}"><i class="{p}-xi {p}-xi-{icls}">{icon}</i>{name}' +
                    (f'<b class="{p}-bdg {badges[path].lower()}" id="{rid}-b" style="opacity:0">{badges[path]}</b>' if path in badges else '') + '</div>')
        if not hidden:
            y += ROW_H
        elif hide_csv:
            pass
    return (f'<aside class="{p}-side"><div class="{p}-sh">Explorador</div><div class="{p}-proj">▾ ADAPTER-IMPORTADOR-TRANSACOES</div>'
            f'<div class="{p}-tree" id="{p}-tree">{"".join(rows)}</div></aside>')


def xid(p, path):
    return f"#{p}-x-" + re.sub(r"[^a-z0-9]", "-", path.lower())


# ── abas, editor, terminal ────────────────────────────────────────────────────
def tabs(p, tid, names, active):
    t = "".join(f'<span class="{p}-tab{" on" if n == active else ""}"><i>TS</i>{n}</span>' for n in names)
    return f'<div class="{p}-tabs" id="{tid}">{t}</div>'


def editor(p, eid, lines, typed=False, adds=()):
    """Arquivo no editor. typed=True deixa as linhas para digitar; adds = índices de linhas inseridas (fundo verde)."""
    rows = []
    for i, src in enumerate(lines):
        n = len(src)
        add = f'<i class="{p}-add" id="{eid}-a{i}"></i>' if i in adds else ""
        rows.append(f'<div class="{p}-row" id="{eid}-r{i}">{add}<span class="{p}-no">{i + 1}</span>'
                    f'<span class="{p}-tx" id="{eid}-t{i}" style="--n:{n}">{hl(src, p)}</span></div>')
    return (f'<div class="{p}-ed" id="{eid}"><div class="{p}-scroll" id="{eid}-sc">'
            f'<i class="{p}-band" id="{eid}-band"></i>{"".join(rows)}</div></div>')


def terminal(p, blocks):
    """blocks: lista de (id, comando, linhas de saída)."""
    out = []
    for bid, cmd, lines in blocks:
        out.append(f'<div class="{p}-tl" id="{bid}-c"><span class="{p}-pr">~/codigo $ </span>'
                   f'<span class="{p}-ty" id="{bid}-ty" style="--n:{len(cmd)}">{html.escape(cmd)}</span></div>')
        for j, l in enumerate(lines):
            out.append(f'<div class="{p}-tl {bid}-o" id="{bid}-o{j}">{term_hl(l, p) or "&nbsp;"}</div>')
    return (f'<section class="{p}-term" id="{p}-term"><div class="{p}-th"><span class="on">Terminal</span><span>Problemas</span><span>Saída</span></div>'
            f'<div class="{p}-tb"><div class="{p}-tsc" id="{p}-tsc" data-layout-allow-overflow>{"".join(out)}</div></div></section>')


# ── CSS comum ──────────────────────────────────────────────────────────────────
def css(p):
    faces = "".join(
        f'@font-face{{font-family:"{fam}";src:url("{FONT_BASE}/{file}-{w}.woff2") format("woff2");font-weight:{w};font-style:normal}}\n'
        for fam, file, ws in (("Inter Tight", "InterTight", (400, 500, 600)), ("JetBrains Mono", "JetBrainsMono", (400, 500, 700)))
        for w in ws
    )
    ed_w = W - SIDE_W
    return faces + f"""
#root{{position:absolute;inset:0;width:{W}px;height:{H}px;overflow:hidden;font-family:"Inter Tight",sans-serif;color:#17181b}}
.{p}-bg{{position:absolute;inset:0;background:#fbfbf9}}
.{p}-stage{{position:absolute;inset:0}}
.{p}-title{{position:absolute;left:0;top:0;width:{W}px;height:{TITLE_H}px;background:#e9e6e0;border-bottom:1px solid rgba(23,24,27,.08);display:flex;align-items:center;justify-content:center;font:500 19px "Inter Tight";color:#3d3b37}}
.{p}-dots{{position:absolute;left:22px;top:17px;display:flex;gap:9px}}
.{p}-dots i{{width:14px;height:14px;border-radius:50%;background:#d6d1ca}}
.{p}-step{{position:absolute;right:22px;top:9px;height:30px;padding:0 16px;border-radius:99px;background:#ff6a13;color:#17181b;display:flex;align-items:center;font:600 17px "Inter Tight"}}
.{p}-side{{position:absolute;left:0;top:{TITLE_H}px;width:{SIDE_W}px;height:{H - TITLE_H - STATUS_H}px;background:#f1efeb;border-right:1px solid rgba(23,24,27,.08)}}
.{p}-sh{{height:44px;padding:0 22px;display:flex;align-items:center;font:600 15px "Inter Tight";letter-spacing:.12em;text-transform:uppercase;color:#55534e}}
.{p}-proj{{height:34px;padding:0 14px;display:flex;align-items:center;font:600 15px "Inter Tight";letter-spacing:.04em;color:#3d3b37}}
.{p}-tree{{position:relative}}
.{p}-xr{{position:absolute;left:0;width:{SIDE_W}px;height:{ROW_H}px;display:flex;align-items:center;gap:10px;font:400 20px "Inter Tight";color:#2a2b2f;white-space:nowrap}}
.{p}-xr.on{{background:rgba(255,106,19,.14);box-shadow:inset 3px 0 0 #ff6a13}}
.{p}-xi{{font-style:normal;font:700 12px "JetBrains Mono";width:22px;text-align:center;color:#6b6964}}
.{p}-xi-ts{{color:#2556c9}}.{p}-xi-d{{font-size:16px;color:#55534e}}
.{p}-bdg{{margin-left:auto;margin-right:20px;font:700 17px "JetBrains Mono"}}
.{p}-bdg.u{{color:#157a3c}}.{p}-bdg.m{{color:#7a4800}}
.{p}-keep{{margin-left:auto;margin-right:16px;padding:2px 10px;border-radius:99px;background:rgba(21,122,60,.12);color:#157a3c;font:600 15px "Inter Tight"}}
.{p}-tabs{{position:absolute;left:{SIDE_W}px;top:{TITLE_H}px;width:{ed_w}px;height:{TABS_H}px;background:#f1efeb;border-bottom:1px solid rgba(23,24,27,.08);display:flex}}
.{p}-tab{{display:flex;align-items:center;gap:10px;padding:0 24px;font:400 19px "Inter Tight";color:#6b6964;border-right:1px solid rgba(23,24,27,.06);white-space:nowrap}}
.{p}-tab i{{font:700 12px "JetBrains Mono";font-style:normal;color:#2556c9}}
.{p}-tab.on{{background:#fbfbf9;color:#17181b;box-shadow:inset 0 2px 0 #ff6a13}}
.{p}-ed{{position:absolute;left:{SIDE_W}px;top:{ED_TOP}px;width:{ed_w}px;height:{H - ED_TOP - STATUS_H}px;overflow:hidden;background:#fbfbf9}}
.{p}-scroll{{position:absolute;left:0;top:0;width:100%;padding-top:{ED_PAD}px}}
.{p}-row{{position:relative;height:{LH}px;display:flex;align-items:center;font:400 {FS}px/{LH}px "JetBrains Mono";white-space:pre;color:#1d1f23}}
.{p}-no{{flex:none;width:{GUT}px;padding-right:22px;text-align:right;color:#66625c;font-size:{FS - 4}px;position:relative;z-index:1}}
.{p}-tx{{position:relative;z-index:1;display:inline-block;overflow:hidden;white-space:pre;vertical-align:top}}
.{p}-band{{position:absolute;left:0;width:100%;height:{LH}px;background:rgba(255,106,19,.15);box-shadow:inset 4px 0 0 #ff6a13;transform-origin:left center;opacity:0;z-index:0}}
.{p}-add{{position:absolute;left:0;top:0;width:100%;height:{LH}px;background:rgba(21,122,60,.12);box-shadow:inset 4px 0 0 #157a3c;transform-origin:left center;z-index:0}}
.{p}-k{{color:#c2410c}}.{p}-t{{color:#2556c9}}.{p}-s{{color:#157a3c}}.{p}-n{{color:#9a5b00}}.{p}-c{{color:#8b8d92;font-style:italic}}
.{p}-term{{position:absolute;left:{SIDE_W}px;top:{TERM_TOP}px;width:{ed_w}px;height:{TERM_H}px;background:#f3f2ee;border-top:1px solid rgba(23,24,27,.12);box-shadow:0 -18px 40px -30px rgba(60,40,20,.4);overflow:hidden;z-index:5}}
.{p}-th{{height:44px;display:flex;align-items:center;gap:30px;padding:0 26px;font:600 15px "Inter Tight";letter-spacing:.1em;text-transform:uppercase;color:#66625c;border-bottom:1px solid rgba(23,24,27,.07)}}
.{p}-th .on{{color:#17181b;box-shadow:0 13px 0 -11px #ff6a13}}
.{p}-tb{{position:absolute;left:0;top:44px;right:0;bottom:0;overflow:hidden}}
.{p}-tsc{{position:absolute;left:0;top:0;width:100%;padding:12px 28px}}
.{p}-tl{{height:{TLH}px;font:400 {TFS}px/{TLH}px "JetBrains Mono";white-space:pre;color:#1d1f23}}
.{p}-pr{{color:#157a3c;font-weight:500}}
.{p}-ty{{display:inline-block;overflow:hidden;vertical-align:top;white-space:pre}}
.{p}-dim{{color:#66625c}}.{p}-ok{{color:#157a3c;font-weight:700}}.{p}-err{{color:#b42318;font-weight:700}}
.{p}-status{{position:absolute;left:0;top:{H - STATUS_H}px;width:{W}px;height:{STATUS_H}px;background:#e9e6e0;border-top:1px solid rgba(23,24,27,.08);z-index:6;display:flex;align-items:center;gap:28px;padding:0 22px;font:500 16px "Inter Tight";color:#55534e}}
.{p}-status b{{margin-left:auto;font-weight:600;color:#17181b}}
"""


def shell(p, step, side, tab_html, body, status_right=""):
    return f"""
  <div class="{p}-title"><span class="{p}-dots"><i></i><i></i><i></i></span>adapter-importador-transacoes<span class="{p}-step">{step}</span></div>
  {side}
  {tab_html}
  {body}
  <div class="{p}-status"><span>⎇ main</span><span>TypeScript</span><span>UTF-8</span><b id="{p}-sr">{status_right}</b></div>"""


def frame(n, fid, dur, step, inner, js):
    p = f"f{n}"
    return f"""<template>
<style>
{css(p)}
</style>
<div id="root" data-composition-id="{fid}" data-width="{W}" data-height="{H}">
  <div class="{p}-bg clip" id="{p}-bg" data-start="0" data-duration="{dur}" data-track-index="0"></div>
  <div class="{p}-stage clip" id="{p}-stage" data-start="0" data-duration="{dur}" data-track-index="1">
{inner}
  </div>
</div>
<script>
(function () {{
  window.__timelines = window.__timelines || {{}};
  const tl = gsap.timeline({{ paused: true }});
  const E = "power3.out";
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  // digita: largura em ch, em degraus (determinístico)
  const type = (id, at, dur, row) => {{
    const el = $(id);
    if (row) {{ gsap.set(el.parentNode, {{ opacity: 0 }}); tl.set(el.parentNode, {{ opacity: 1 }}, at); }}
    const n = Math.max(1, +getComputedStyle(el).getPropertyValue("--n"));
    tl.fromTo(el, {{ width: "0ch" }}, {{ width: n + "ch", duration: dur, ease: "steps(" + n + ")" }}, at);
  }};
  // mostra um arquivo inteiro de uma vez, linha a linha (como ao abrir)
  const open = (eid, at) => tl.fromTo($$(eid + " ." + "{p}-row"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.18, stagger: 0.025, ease: "power1.out" }}, at);
  // faixa de destaque na linha i (0-based) do editor eid
  const band = (eid, i, at, n = 1) => {{
    tl.set(eid + "-band", {{ top: {ED_PAD} + i * {LH}, height: n * {LH} }}, at);
    tl.fromTo(eid + "-band", {{ opacity: 0, scaleX: 0 }}, {{ opacity: 1, scaleX: 1, duration: 0.4, ease: "power2.inOut" }}, at);
  }};
  const termUp = (at) => tl.fromTo("#{p}-term", {{ y: {TERM_H + 60} }}, {{ y: 0, duration: 0.6, ease: E }}, at);
  const termDown = (at) => tl.to("#{p}-term", {{ y: {TERM_H + 60}, duration: 0.5, ease: "power2.in" }}, at);
  const scroll = (eid, lines, at) => tl.to(eid + "-sc", {{ y: -lines * {LH}, duration: 0.6, ease: E }}, at);
  const output = (bid, at) => tl.fromTo("." + bid + "-o", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.05, stagger: 0.035 }}, at);
  const cut = (hide, show, at) => {{ if (hide) tl.set(hide, {{ opacity: 0 }}, at); tl.set(show, {{ opacity: 1 }}, at); }};
{js}
  tl.set({{}}, {{}}, {dur});
  window.__timelines["{fid}"] = tl;
}})();
</script>
</template>
"""


def find(lines, needle, start=0):
    return next(i for i, l in enumerate(lines) if i >= start and needle in l)


# ── Quadro 1 · o contrato ─────────────────────────────────────────────────────
def f1():
    p, fid, dur = "f1", "01-contrato", 9
    model = read("src/transaction.ts")
    target = read("src/transaction-file-adapter.ts")
    side = explorer(p, hide_csv=True)
    t1 = tabs(p, f"{p}-tabA", ["transaction.ts"], "transaction.ts")
    t2 = tabs(p, f"{p}-tabB", ["transaction.ts", "transaction-file-adapter.ts"], "transaction-file-adapter.ts")
    body = editor(p, f"{p}-m", model) + editor(p, f"{p}-g", target, typed=True)
    inner = shell(p, "O contrato (Target)", side, t1 + t2, body, "modelo e interface")
    pm, pg = xid(p, "src/transaction.ts"), xid(p, "src/transaction-file-adapter.ts")
    i_iface = find(model, "export interface")
    i_parse = find(target, "parse(")
    js = f"""
  gsap.set("{pm}", {{ className: "{p}-xr on" }});
  gsap.set(["#{p}-tabB", "#{p}-g"], {{ opacity: 0 }});
  open("#{p}-m", 0.3);
  band("#{p}-m", {i_iface}, 1.4, {len(model) - i_iface});
  cut("#{p}-tabA", "#{p}-tabB", 3.4); cut("#{p}-m", "#{p}-g", 3.4);
  tl.set("{pm}", {{ className: "{p}-xr" }}, 3.4); tl.set("{pg}", {{ className: "{p}-xr on" }}, 3.4);
  {" ".join(f'type("#{p}-g-t{i}", {3.6 + sum(len(x) for x in target[:i]) * 0.022:.3f}, {max(0.05, len(l) * 0.022):.3f}, true);' for i, l in enumerate(target))}
  band("#{p}-g", {i_parse}, 6.4);
"""
    return fid, frame(1, fid, dur, "", inner, js)


# ── Quadros 2 e 3 · um adaptador + execução ───────────────────────────────────
def adapter_frame(n, fid, dur, step, rel, tabs_list, cmd, outfile, marks, t_marks):
    p = f"f{n}"
    src = read(rel)
    out = run_out(outfile)
    side = explorer(p, hide_csv=True)
    name = rel.split("/")[-1]
    tb = tabs(p, f"{p}-tab", tabs_list, name)
    body = editor(p, f"{p}-e", src) + terminal(p, [(f"{p}b", cmd, out)])
    inner = shell(p, step, side, tb, body, name)
    i_class = find(src, "export class")
    idx = [find(src, m) for m in marks]
    scroll_lines = max(0, idx[-1] - ((TERM_TOP - ED_TOP - ED_PAD) // LH) + 3)
    t_up = t_marks[-1] + 1.3
    js = f"""
  gsap.set("{xid(p, rel)}", {{ className: "{p}-xr on" }});
  gsap.set("#{p}-term", {{ y: {TERM_H + 60} }});
  open("#{p}-e", 0.2);
  band("#{p}-e", {i_class}, 1.3);
  {" ".join(f'band("#{p}-e", {i}, {t});' for i, t in zip(idx, t_marks))}
  termUp({t_up});
  scroll("#{p}-e", {scroll_lines}, {t_up});
  type("#{p}b-ty", {t_up + 0.7}, {len(cmd) * 0.03:.2f});
  output("{p}b", {t_up + 0.9 + len(cmd) * 0.03 + 0.5:.2f});
"""
    return fid, frame(n, fid, dur, step, inner, js)


def f2():
    return adapter_frame(2, "02-ofx", 14, "Passo 1 · OFX", "src/adapters/ofx.adapter.ts",
                         ["transaction-file-adapter.ts", "ofx.adapter.ts"], "npm run importar data/extrato.ofx", "ofx.txt",
                         ["date:", "description:", "amount:", "type:"], (3.2, 4.0, 4.8, 5.6))


def f3():
    return adapter_frame(3, "03-excel", 12, "Passo 2 · Excel", "src/adapters/excel.adapter.ts",
                         ["ofx.adapter.ts", "excel.adapter.ts"], "npm run importar data/extrato.xlsx", "xlsx.txt",
                         ['"Extrato"', "date:", "description:", "amount:", "type:"], (2.4, 3.1, 3.7, 4.3, 4.9))


# ── Quadro 4 · comparar ───────────────────────────────────────────────────────
def f4():
    p, fid, dur = "f4", "04-comparar", 10
    rel = "src/transaction-import-service.ts"
    src = read(rel)
    out = run_out("comparar.txt")
    side = explorer(p, hide_csv=True)
    tb = tabs(p, f"{p}-tab", ["excel.adapter.ts", "transaction-import-service.ts"], "transaction-import-service.ts")
    cmd = "npm run comparar"
    body = editor(p, f"{p}-e", src) + terminal(p, [(f"{p}b", cmd, out)])
    inner = shell(p, "Passo 3 · Comparar", side, tb, body, "Client: só conhece a interface")
    i_client = find(src, "// Client")
    i_parse = find(src, "adapter.parse")
    i_ok = len(out) - 1
    js = f"""
  gsap.set("{xid(p, rel)}", {{ className: "{p}-xr on" }});
  gsap.set("#{p}-term", {{ y: {TERM_H + 60} }});
  open("#{p}-e", 0.2);
  band("#{p}-e", {i_client}, 1.0);
  band("#{p}-e", {i_parse}, 2.2);
  termUp(3.8);
  type("#{p}b-ty", 4.4, {len(cmd) * 0.03:.2f});
  output("{p}b", 5.4);
  tl.to("#{p}-tsc", {{ y: -{max(0, len(out) + 1 - (TERM_H - 56) // TLH) * TLH}, duration: 0.5, ease: E }}, 6.4);
  tl.fromTo("#{p}b-o{i_ok}", {{ backgroundColor: "rgba(21,122,60,0)" }}, {{ backgroundColor: "rgba(21,122,60,.14)", duration: 0.4 }}, 6.8);
"""
    return fid, frame(4, fid, dur, "", inner, js)


# ── Quadro 5 · formato novo (CSV) ─────────────────────────────────────────────
def f5():
    p, fid, dur = "f5", "05-csv", 21
    csv_src = read("src/adapters/csv.adapter.ts")
    res = read("src/adapter-resolver.ts")
    add_idx = (find(res, "import { CsvAdapter"), find(res, "csv: new CsvAdapter"))
    err, ok = run_out("csv-erro.txt"), run_out("csv.txt")
    cmd = "npm run importar data/extrato.csv"
    side = explorer(p, hide_csv=True, badges={"src/adapters/csv.adapter.ts": "U", "src/adapter-resolver.ts": "M"})
    ta = tabs(p, f"{p}-tabA", ["comparar.ts", "transaction-import-service.ts"], "transaction-import-service.ts")
    tbb = tabs(p, f"{p}-tabB", ["transaction-import-service.ts", "csv.adapter.ts"], "csv.adapter.ts")
    tc = tabs(p, f"{p}-tabC", ["transaction-import-service.ts", "csv.adapter.ts", "adapter-resolver.ts"], "adapter-resolver.ts")
    svc = read("src/transaction-import-service.ts")
    body = (editor(p, f"{p}-s", svc) + editor(p, f"{p}-c", csv_src, typed=True) + editor(p, f"{p}-r", res, adds=add_idx)
            + terminal(p, [(f"{p}a", cmd, err), (f"{p}b", cmd, ok)]))
    inner = shell(p, "Passo 4 · Formato novo", side, ta + tbb + tc, body, "1 arquivo novo · 2 linhas no mapa · TransactionImportService sem alterações")
    # tempos
    t_err, t_new = 1.9, 3.6
    per = 0.016
    starts, t = [], t_new + 0.5
    for l in csv_src:
        starts.append(round(t, 3))
        t += max(0.06, len(l) * per)
    t_res = round(t + 0.6, 2)
    total_lines = 1 + len(err) + 1 + len(ok)
    visible = (TERM_H - 56) // TLH
    rows_csv = xid(p, "src/adapters/csv.adapter.ts")
    rows_after = [xid(p, path) for _, _, path in TREE[TREE.index((2, "file", "src/adapters/csv.adapter.ts")) + 1:]]
    js = f"""
  gsap.set("{xid(p, 'src/transaction-import-service.ts')}", {{ className: "{p}-xr on" }});
  gsap.set(["#{p}-tabB", "#{p}-tabC", "#{p}-c", "#{p}-r", "#{p}b-c", ".{p}b-o"], {{ opacity: 0 }});
  gsap.set(["#{p}-r-t{add_idx[0]}", "#{p}-r-t{add_idx[1]}"], {{ width: "0ch" }});
  gsap.set(["#{p}-r-a{add_idx[0]}", "#{p}-r-a{add_idx[1]}"], {{ scaleX: 0 }});
  gsap.set("#{p}-sr", {{ opacity: 0 }});
  gsap.set("#{p}-keep", {{ opacity: 0 }});
  open("#{p}-s", 0);
  termUp(0.3);
  type("#{p}a-ty", 0.9, {len(cmd) * 0.025:.2f});
  output("{p}a", {t_err});
  // novo arquivo: aparece no explorador (U) e abre vazio
  termDown({t_new - 0.4});
  tl.to([{", ".join(f'"{r}"' for r in rows_after)}], {{ y: {ROW_H}, duration: 0.35, ease: E }}, {t_new});
  tl.fromTo("{rows_csv}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {t_new + 0.15});
  tl.set("{rows_csv}", {{ className: "{p}-xr on" }}, {t_new + 0.15});
  tl.set("{xid(p, 'src/transaction-import-service.ts')}", {{ className: "{p}-xr" }}, {t_new + 0.15});
  tl.set("{rows_csv}-b", {{ opacity: 1 }}, {t_new + 0.15});
  cut(["#{p}-tabA", "#{p}-s"], ["#{p}-tabB", "#{p}-c"], {t_new + 0.3});
  {" ".join(f'type("#{p}-c-t{i}", {s}, {max(0.05, len(l) * per):.3f}, true);' for i, (l, s) in enumerate(zip(csv_src, starts)))}
  // registra no mapa de adaptadores (M)
  cut(["#{p}-tabB", "#{p}-c"], ["#{p}-tabC", "#{p}-r"], {t_res});
  tl.set("{rows_csv}", {{ className: "{p}-xr" }}, {t_res});
  tl.set("{xid(p, 'src/adapter-resolver.ts')}", {{ className: "{p}-xr on" }}, {t_res});
  tl.fromTo("#{p}-r-a{add_idx[0]}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.35, ease: "power2.inOut" }}, {t_res + 0.5});
  type("#{p}-r-t{add_idx[0]}", {t_res + 0.55}, 0.7);
  tl.fromTo("#{p}-r-a{add_idx[1]}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.35, ease: "power2.inOut" }}, {t_res + 1.5});
  type("#{p}-r-t{add_idx[1]}", {t_res + 1.55}, 0.5);
  tl.set("{xid(p, 'src/adapter-resolver.ts')}-b", {{ opacity: 1 }}, {t_res + 0.6});
  // roda de novo
  termUp({t_res + 2.4});
  tl.set("#{p}b-c", {{ opacity: 1 }}, {t_res + 2.9});
  tl.to("#{p}-tsc", {{ y: -{max(0, total_lines - visible) * TLH}, duration: 0.4, ease: E }}, {t_res + 2.9});
  type("#{p}b-ty", {t_res + 3.0}, {len(cmd) * 0.025:.2f});
  output("{p}b", {t_res + 3.0 + len(cmd) * 0.025 + 0.4:.2f});
  // o serviço não mudou
  tl.fromTo("#{p}-sr", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_res + 4.6});
  tl.fromTo("#{p}-keep", {{ opacity: 0, x: -10 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: E }}, {t_res + 4.6});
"""
    # selo "sem alterações" na linha do serviço no explorador
    keep = f'<span class="{p}-keep" id="{p}-keep">intacto</span>'
    inner = inner.replace('transaction-import-service.ts</div>', f'transaction-import-service.ts{keep}</div>', 1)
    return fid, frame(5, fid, dur, "", inner, js), round(t_res + 7.0, 1)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (f1, f2, f3, f4):
        fid, doc = fn()
        (OUT / f"{fid}.html").write_text(doc, encoding="utf-8")
        print("ok", fid)
    fid, doc, need = f5()
    (OUT / f"{fid}.html").write_text(doc, encoding="utf-8")
    print("ok", fid, "precisa de", need, "s")
