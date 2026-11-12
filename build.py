#!/usr/bin/env python3
"""Build the Free Stack site.

Guide content lives in _src/<slug>.html. Each file starts with a JSON meta
block in an HTML comment, followed by the article body. This script wraps
every page in the shared shell (sidebar, search, on-this-page, prev/next)
and writes <slug>.html to the repo root, plus assets/search-index.js.

Usage:  python3 build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_src"

# Sidebar order. (group, slug, label)
NAV = [
    ("Start here", "index", "Overview"),
    ("Hosting", "vercel-guide", "Vercel"),
    ("Hosting", "render-guide", "Render"),
    ("Hosting", "cloudflare-guide", "Cloudflare"),
    ("Data", "supabase-guide", "Supabase"),
    ("Workflow", "git-guide", "Git"),
    ("Workflow", "github-guide", "GitHub"),
    ("Workflow", "keepalive-guide", "Keep-alive"),
    ("Build", "telegram-bot-guide", "Telegram bots"),
]

UPDATED = "November 2026"

ICON_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
ICON_THEME = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'


def read_src(slug):
    raw = (SRC / f"{slug}.html").read_text(encoding="utf-8")
    m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->\s*", raw, re.S)
    if not m:
        raise SystemExit(f"{slug}: missing meta block")
    return json.loads(m.group(1)), raw[m.end():]


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def transform_body(body):
    """Expand shorthand into full components."""

    def code(m):
        attrs, content = m.group(1), m.group(2)
        lang = re.search(r'data-lang="([^"]*)"', attrs)
        file = re.search(r'data-file="([^"]*)"', attrs)
        lang = lang.group(1) if lang else ""
        label = file.group(1) if file else {"sh": "Terminal", "sql": "SQL", "yaml": "YAML", "json": "JSON", "py": "Python", "js": "JavaScript", "ts": "TypeScript"}.get(lang, "Code")
        content = content.strip("\n")
        # dedent
        lines = content.split("\n")
        indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
        cut = min(indents) if indents else 0
        content = "\n".join(l[cut:] for l in lines)
        lang_attr = f' data-lang="{lang}"' if lang else ""
        return (
            f'<div class="codeblock"><div class="codebar"><span class="file">{html.escape(label)}</span>'
            f'<button class="copy" type="button">Copy</button></div>'
            f"<pre{lang_attr}>{html.escape(content, quote=False)}</pre></div>"
        )

    body = re.sub(r"<pre([^>]*)>(.*?)</pre>", code, body, flags=re.S)
    def table(m):
        inner = m.group(1)
        heads = [strip_tags(h) for h in re.findall(r"<th>(.*?)</th>", inner, re.S)]

        def row(r):
            cells = iter(heads)
            return re.sub(r"<td>", lambda _: f'<td data-label="{html.escape(next(cells, ""))}">', r.group(0))

        inner = re.sub(r"<tr>(?:(?!</tr>).)*<td>.*?</tr>", row, inner, flags=re.S)
        return f'<div class="table-wrap"><table>{inner}</table></div>'

    body = re.sub(r"<table>(.*?)</table>", table, body, flags=re.S)
    return body


def sections(body):
    """Return [(id, title, keywords)] for each h2, adding ids where missing."""
    out = []
    parts = re.split(r"(<h2[^>]*>.*?</h2>)", body, flags=re.S)
    rebuilt = []
    for i, part in enumerate(parts):
        m = re.match(r"<h2([^>]*)>(.*?)</h2>", part, re.S)
        if m:
            idm = re.search(r'id="([^"]+)"', m.group(1))
            sid = idm.group(1) if idm else slugify(m.group(2))
            title = strip_tags(m.group(2))
            nxt = parts[i + 1] if i + 1 < len(parts) else ""
            h3s = [strip_tags(h) for h in re.findall(r"<h3[^>]*>(.*?)</h3>", nxt, re.S)]
            sums = [strip_tags(s) for s in re.findall(r"<summary>(.*?)</summary>", nxt, re.S)]
            out.append((sid, title, " ".join(h3s + sums)))
            rebuilt.append(f'<h2 id="{sid}">{m.group(2)}</h2>')
        else:
            rebuilt.append(part)
    return out, "".join(rebuilt)


def sidebar(current, guides_meta):
    groups, order = {}, []
    for g, slug, label in NAV:
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append((slug, label))
    parts = []
    for g in order:
        links = []
        for slug, label in groups[g]:
            href = "./" if slug == "index" else f"{slug}.html"
            cur = ' aria-current="page"' if slug == current else ""
            mins = guides_meta.get(slug, {}).get("minutes")
            small = f"<small>{mins} min</small>" if mins else ""
            links.append(f'<a href="{href}"{cur}><span>{label}</span>{small}</a>')
        parts.append(f'<div class="nav-group"><h4>{g}</h4>{"".join(links)}</div>')
    return f"""
<nav class="side" aria-label="Guides">
  <a class="brand" href="./"><span class="brand-mark" aria-hidden="true"></span>Free Stack</a>
  <div class="search" role="search">
    <input type="search" placeholder="Search guides" aria-label="Search guides" autocomplete="off">
    <kbd>/</kbd>
    <div class="results" role="listbox"></div>
  </div>
  <div class="nav">{"".join(parts)}</div>
  <div class="side-foot">
    <a href="https://github.com/devtint/free-stack">Source</a>
    <button class="btn" type="button" data-theme-toggle>{ICON_THEME}<span data-theme-label>Dark mode</span></button>
  </div>
</nav>"""


def shell(slug, title, description, main_html, guides_meta):
    page_title = "Free Stack" if slug == "index" else f"{title} guide | Free Stack"
    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(page_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta name="theme-color" content="#faf9f5">
<script>try{{var t=localStorage.getItem('fs-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%23c2603f'/%3E%3Crect x='10' y='10' width='12' height='12' rx='3' fill='%23faf9f5'/%3E%3C/svg%3E">
</head>
<body>
<div class="mobile-bar">
  <a class="brand" href="./"><span class="brand-mark" aria-hidden="true"></span>Free Stack</a>
  <button class="btn" type="button" data-nav-open aria-label="Open menu">{ICON_MENU}Menu</button>
</div>
<div class="scrim" data-nav-close></div>
<div class="app">
{sidebar(slug, guides_meta)}
{main_html}
</div>
<script src="assets/search-index.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
"""


FOOT = """<footer class="page-foot">
  An independent, educational reference. Not affiliated with any service mentioned. Limits change, so always confirm on the official pricing page before you rely on a number.<br>
  Made by <a href="https://github.com/devtint">devtint</a> &middot; <a href="https://t.me/BadCodeWriter">Telegram</a> &middot; <a href="https://github.com/devtint/free-stack">Source</a> &middot; MIT license
</footer>"""


def build():
    guides = [slug for _, slug, _ in NAV if slug != "index"]
    metas, bodies = {}, {}
    for slug in guides + ["index"]:
        metas[slug], bodies[slug] = read_src(slug)

    search = []
    for slug in guides + ["index"]:
        meta, body = metas[slug], bodies[slug]
        body = transform_body(body)
        secs, body = sections(body)

        if slug == "index":
            main = f'<main class="main wide" id="main"><div>{body}{FOOT}</div></main>'
            for sid, t, k in secs:
                search.append({"t": t, "g": "Overview", "u": f"./#{sid}", "k": k})
        else:
            i = guides.index(slug)
            prev_s = guides[i - 1] if i > 0 else None
            next_s = guides[i + 1] if i + 1 < len(guides) else None
            label = {s: l for _, s, l in NAV}
            pager = '<nav class="pager" aria-label="More guides">'
            if prev_s:
                pager += f'<a href="{prev_s}.html"><span>Previous</span><b>{label[prev_s]}</b></a>'
            if next_s:
                pager += f'<a class="next" href="{next_s}.html"><span>Next</span><b>{label[next_s]}</b></a>'
            pager += "</nav>"

            chips = "".join(f'<span class="chip"><b>{v}</b> {k}</span>' for v, k in meta.get("chips", []))
            docs = "".join(
                f'<a href="{u}">{html.escape(n)}</a>' for n, u in meta.get("docs", [])
            )
            toc = "".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t, _ in secs)
            main = f"""<main class="main" id="main">
<div>
  <p class="crumb"><a href="./">Guides</a> / {html.escape(meta["group"])}</p>
  <h1>{html.escape(meta["title"])}</h1>
  <p class="lede">{meta["lede"]}</p>
  <div class="meta-row"><span>Checked against official docs, {UPDATED}</span><span>{meta["minutes"]} min read</span>{docs}</div>
  <div class="chips">{chips}</div>
  <article class="prose">{body}</article>
  {pager}
  {FOOT}
</div>
<aside class="toc" aria-label="On this page"><h4>On this page</h4><ol>{toc}</ol></aside>
</main>"""
            search.append({"t": meta["title"], "g": meta["group"] + " guide", "u": f"{slug}.html", "k": meta.get("keywords", "")})
            for sid, t, k in secs:
                search.append({"t": t, "g": meta["title"], "u": f"{slug}.html#{sid}", "k": k})

        out = shell(slug, meta["title"], meta["description"], main, metas)
        (ROOT / f"{slug}.html").write_text(out, encoding="utf-8")
        print("wrote", f"{slug}.html")

    (ROOT / "assets" / "search-index.js").write_text(
        "window.FS_SEARCH=" + json.dumps(search, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print("wrote assets/search-index.js")


if __name__ == "__main__":
    build()
