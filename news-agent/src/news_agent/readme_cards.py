"""Linked feature cards for GitHub's horizontally scrollable README."""

from html import escape
from textwrap import wrap

from .contract import Entry
from .web import pipeline_brief, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"
PALETTES = (
    ("#eff9e7", "#d9f1e8", "#b7d9c5", "#22594a"),
    ("#edf8ff", "#dfe9fb", "#c1d6e9", "#345775"),
    ("#fff5e3", "#fae4de", "#e8cfc1", "#794d3d"),
    ("#f6f2ff", "#e8e5f9", "#d7cfea", "#584d78"),
    ("#edf8f6", "#d8edf1", "#bad8df", "#315e68"),
)


def lines(value: str, width: int, limit: int, y: int, leading: int) -> str:
    rows = [line for paragraph in value.splitlines() for line in wrap(paragraph, width)]
    if len(rows) > limit:
        rows = rows[:limit]
        rows[-1] = rows[-1].rstrip(".") + "…"
    return "".join(f'<tspan x="26" y="{y + i * leading}">{escape(row)}</tspan>'
                   for i, row in enumerate(rows))


def tile(entry: Entry, brief: str, palette) -> str:
    start, end, edge, ink = palette
    tasks = " · ".join(task_label(t) for t in entry.support.tasks)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="398" height="264" viewBox="0 0 398 264">
  <title>{escape(entry.title)}</title>
  <defs><linearGradient id="wash" x2="1" y2="1"><stop stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient></defs>
  <rect width="398" height="264" fill="#fff"/>
  <rect x="7" y="8" width="384" height="248" rx="22" fill="url(#wash)" stroke="{edge}"/>
  <g font-family="Arial, Helvetica, sans-serif" fill="{ink}">
    <text font-size="12" font-weight="700">{lines(tasks, 27, 1, 37, 0)}</text>
    <text x="369" y="37" text-anchor="end" font-size="12">{entry.published_at:%d %b %Y}</text>
    <text font-size="22" font-weight="700">{lines(entry.title, 29, 2, 71, 24)}</text>
    <text font-size="14">{lines(entry.summary, 47, 3, 119, 18)}</text>
    <path d="M26 169h346" stroke="{edge}"/>
    <text font-size="13" font-weight="600">{lines(brief, 45, 3, 189, 16)}</text>
    <text x="26" y="241" font-size="12" font-weight="700">View commit ↗</text>
    <text x="369" y="241" text-anchor="end" font-size="12" font-family="monospace">{entry.evidence.source_commit[:7]}</text>
  </g>
</svg>
'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    links = []
    assets = {}
    for i, entry in enumerate(entries):
        path = f"docs/news/cards/{entry.id}.svg"
        brief = pipeline_brief(entry)
        assets[path] = tile(entry, brief, PALETTES[i % len(PALETTES)])
        alt = escape(" · ".join((entry.title, entry.summary, " ".join(brief.splitlines()))))
        links.append(f'<a href="{escape(entry.links.source_change)}"><img src="./{path}" width="398" alt="{alt}"></a>')
    strip = "<pre>" + "".join(links) + "</pre>" if links else "No releases yet."
    return f"## Recently supported\n\n{strip}\n\n[Explore all updates on GitHub Pages ↗]({PAGES})\n", assets
