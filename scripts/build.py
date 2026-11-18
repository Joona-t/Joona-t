#!/usr/bin/env python3
"""Build the animated profile SVGs in assets/ (dark and light) from data/languages.json.

  python3 scripts/build.py            rebuild the SVGs from the saved counts
  python3 scripts/build.py --refresh  re-count languages with the `gh` CLI first

Only totals are saved (language -> number of repos); no repo names. The SVGs use CSS
animation only, no script and no outside requests, and stop moving under
prefers-reduced-motion. Every text has a fixed textLength, so the layout is the same
whatever monospace font the reader's system has.
"""
import datetime
import json
import random
import subprocess
import sys
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "languages.json"
W = 600
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
THEMES = {
    "dark": dict(bg="#1c0b16", line="#5a1f40", text="#ffe9f3", muted="#e7a9c8", track="#35122a",
                 a="#ff8fc2", b="#c79bff", chip="#2a1021"),
    "light": dict(bg="#fff3f8", line="#ffb6d5", text="#4a0827", muted="#6b2848", track="#ffd9e9",
                  a="#e91e8c", b="#9b5de5", chip="#ffffff"),
}
BARS = 9                                    # languages drawn as bars
ALSO = ["C", "C++", "Go", "GDScript", "TeX"]  # named under the bars
STACK = [
    ("browser extensions", ["Manifest V3", "vanilla JS", "WebExtensions"]),
    ("native apps", ["Swift", "SwiftUI", "Expo"]),
    ("agents / ai", ["Claude Code", "MCP", "LangGraph", "local models"]),
    ("creative", ["Manim", "Blender", "Godot", "p5.js"]),
]


def refresh():
    out = subprocess.run(["gh", "repo", "list", "--limit", "1000", "--source", "--json", "languages"],
                         check=True, capture_output=True, text=True).stdout
    repos = json.loads(out)
    n = Counter(l["node"]["name"] for r in repos for l in r["languages"])
    DATA.write_text(json.dumps({"date": datetime.date.today().isoformat(), "repos": len(repos),
                                "languages": dict(n.most_common())}, indent=1) + "\n")


def text(x, y, s, size, fill, weight=400, cls="", anchor="start"):
    """A label whose width is fixed at 0.6 em per character."""
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'textLength="{len(s) * size * 0.6:.1f}" lengthAdjust="spacingAndGlyphs"'
            f'{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{escape(s)}</text>')


def star(r):
    return f"M0,{-r} Q0,0 {r},0 Q0,0 0,{r} Q0,0 {-r},0 Q0,0 0,{-r}Z"


def svg(uid, h, t, css, body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" id="{uid}" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{escape(label)}" font-family="{FONT}">
<title>{escape(label)}</title>
<defs><linearGradient id="{uid}-g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{t['a']}"/><stop offset="1" stop-color="{t['b']}"/></linearGradient></defs>
<style>
{css}
@media (prefers-reduced-motion: reduce) {{ #{uid} * {{ animation: none !important; }} }}
</style>
<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="14" fill="{t['bg']}" stroke="{t['line']}" stroke-width="2"/>
{body}
</svg>
'''


def header(theme, t):
    uid, h = f"header-{theme}", 190
    line = "building things to understand them."
    size, x, y = 17, 32, 118
    tw = len(line) * size * 0.6
    css = f'''#{uid} .cover {{ animation: {uid}-type 12s steps({len(line)}) infinite; }}
#{uid} .cur {{ animation: {uid}-cur 12s steps({len(line)}) infinite, {uid}-blink 1s steps(1) infinite; }}
#{uid} .sub {{ animation: {uid}-in 12s ease-out infinite; }}
#{uid} .tw {{ animation: {uid}-tw 3.2s ease-in-out infinite; }}
#{uid} .orbit {{ animation: {uid}-spin 14s linear infinite; }}
#{uid} .pulse {{ animation: {uid}-pulse 3.2s ease-in-out infinite; }}
@keyframes {uid}-type {{ 0% {{ transform: scaleX(1); }} 25%, 100% {{ transform: scaleX(0); }} }}
@keyframes {uid}-cur {{ 0% {{ transform: translateX({-tw:.1f}px); }} 25%, 100% {{ transform: translateX(0); }} }}
@keyframes {uid}-blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
@keyframes {uid}-in {{ 0%, 26% {{ opacity: 0; }} 34%, 100% {{ opacity: 1; }} }}
@keyframes {uid}-tw {{ 0%, 100% {{ opacity: .25; transform: scale(.6); }} 50% {{ opacity: 1; transform: scale(1); }} }}
@keyframes {uid}-spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes {uid}-pulse {{ 0%, 100% {{ transform: scale(.92); }} 50% {{ transform: scale(1.06); }} }}'''
    rnd = random.Random(7)
    spots = [(rnd.uniform(24, 400), rnd.choice([rnd.uniform(16, 34), rnd.uniform(160, 176)])) for _ in range(9)]
    spots += [(rnd.uniform(420, 576), rnd.uniform(16, 36)) for _ in range(2)] + [(rnd.uniform(420, 576), rnd.uniform(156, 176)) for _ in range(2)]
    body = [f'<g transform="translate({sx:.0f},{sy:.0f})"><path class="tw" style="animation-delay:{-rnd.uniform(0, 3.2):.2f}s" '
            f'd="{star(rnd.choice([4, 5, 7]))}" fill="{rnd.choice([t["a"], t["b"]])}"/></g>' for sx, sy in spots]
    body += [
        text(32, 78, "Joona Tyrninoksa", 34, f"url(#{uid}-g)", 700),
        text(x, y, line, size, t["text"]),
        f'<g transform="translate({x + tw + 1:.1f},{y - 16})"><rect class="cover" x="{-tw - 2:.1f}" width="{tw + 2:.1f}" height="24" fill="{t["bg"]}"/></g>',
        f'<g transform="translate({x + tw + 3:.1f},{y - 14})"><rect class="cur" width="9" height="18" fill="{t["a"]}"/></g>',
        text(32, 150, "human curiosity × machine intelligence", 16, t["muted"], cls="sub"),
        f'<g transform="translate(500,96)"><g class="orbit"><circle cx="46" r="4" fill="{t["b"]}"/><circle cx="-46" r="3" fill="{t["a"]}"/>'
        f'<circle r="46" fill="none" stroke="{t["line"]}" stroke-width="1.5" stroke-dasharray="3 7"/></g>'
        f'<path class="pulse" d="{star(30)}" fill="url(#{uid}-g)"/></g>',
    ]
    return svg(uid, h, t, css, "\n".join(body), "Joona Tyrninoksa. building things to understand them. human curiosity × machine intelligence")


def languages(theme, t, d):
    uid = f"languages-{theme}"
    rows = list(d["languages"].items())[:BARS]
    top, x0, tw, step = rows[0][1], 140, 370, 30
    h = 100 + step * len(rows) + 44
    css = f'''#{uid} .bar {{ animation: {uid}-grow 1.4s cubic-bezier(.2,.8,.2,1) both; }}
#{uid} .n {{ animation: {uid}-in .6s ease-out both; }}
@keyframes {uid}-grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes {uid}-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}'''
    body = [text(32, 46, "languages", 20, t["text"], 700),
            text(32, 72, f"how many of my {d['repos']} repos use each", 16, t["muted"])]
    for i, (name, n) in enumerate(rows):
        y = 104 + i * step
        body += [
            text(32, y + 5, name, 16, t["text"]),
            f'<rect x="{x0}" y="{y - 6}" width="{tw}" height="12" rx="6" fill="{t["track"]}"/>',
            f'<g transform="translate({x0},{y - 6})"><rect class="bar" style="animation-delay:{i * .12:.2f}s" width="{max(12, tw * n / top):.1f}" height="12" rx="6" fill="url(#{uid}-g)"/></g>',
            text(568, y + 5, str(n), 16, t["muted"], cls="n", anchor="end").replace("<text ", f'<text style="animation-delay:{.6 + i * .12:.2f}s" '),
        ]
    body.append(text(32, h - 26, "also  " + " · ".join(ALSO), 16, t["muted"]))
    label = "Languages by number of repos: " + ", ".join(f"{k} {v}" for k, v in rows) + ". Also " + ", ".join(ALSO) + "."
    return svg(uid, h, t, css, "\n".join(body), label)


def stack(theme, t):
    uid, step = f"stack-{theme}", 78
    h = 70 + step * len(STACK) + 6
    css = f'''#{uid} .chip {{ animation: {uid}-pop .7s cubic-bezier(.2,.8,.2,1) both; }}
@keyframes {uid}-pop {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}'''
    body, k = [text(32, 46, "stack", 20, t["text"], 700)], 0
    for gi, (group, chips) in enumerate(STACK):
        y = 82 + gi * step
        body.append(text(32, y, group, 16, t["muted"]))
        x = 32
        for c in chips:
            cw = len(c) * 9.6 + 24
            body.append(f'<g class="chip" style="animation-delay:{k * .09:.2f}s"><rect class="box" x="{x:.1f}" y="{y + 12}" width="{cw:.1f}" height="32" rx="16" '
                        f'fill="{t["chip"]}" stroke="{t["line"]}" stroke-width="1.5"/>{text(round(x + 12, 1), y + 33, c, 16, t["text"])}</g>')
            x += cw + 8
            k += 1
    label = "Stack. " + ". ".join(f"{g}: {', '.join(c)}" for g, c in STACK) + "."
    return svg(uid, h, t, css, "\n".join(body), label)


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh()
    d = json.loads(DATA.read_text())
    for theme, t in THEMES.items():
        for name, s in (("header", header(theme, t)), ("languages", languages(theme, t, d)), ("stack", stack(theme, t))):
            (ROOT / "assets" / f"{name}-{theme}.svg").write_text(s)
    print("built", len(THEMES) * 3, "svgs from", DATA.name, d["date"], d["repos"], "repos")


def preview(out):
    """Write the pages the checks run on: check.html (every SVG inline, for check_svg_diagrams.py)
    and readme-<theme>.html (the SVGs as images in a GitHub-width column, for screenshots)."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    names = ("header", "languages", "stack")
    page = "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><style>body{{margin:0;padding:16px;background:{bg}}}main{{max-width:846px;margin:auto}}svg,img{{display:block;width:100%;height:auto;margin:0 0 16px}}</style><main>{body}</main>"
    inline = "".join((ROOT / "assets" / f"{n}-{th}.svg").read_text() for th in THEMES for n in names)
    (out / "check.html").write_text(page.format(bg="#888", body=inline))
    for th, bg in (("dark", "#0d1117"), ("light", "#ffffff")):
        imgs = "".join(f'<img src="{(ROOT / "assets" / f"{n}-{th}.svg").as_uri()}">' for n in names)
        (out / f"readme-{th}.html").write_text(page.format(bg=bg, body=imgs))


if "--preview" in sys.argv:
    preview(sys.argv[sys.argv.index("--preview") + 1])
