"""Linked image tiles for GitHub's horizontally scrollable README."""

from html import escape
from textwrap import shorten, wrap

from .contract import Entry
from .web import METRICS, TASK_NAMES, route_anchor, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"
PALETTES = (
    ("#eff9e7", "#d9f1e8", "#b7d9c5", "#22594a"),
    ("#edf8ff", "#dfe9fb", "#c1d6e9", "#345775"),
    ("#fff5e3", "#fae4de", "#e8cfc1", "#794d3d"),
)


def tile(title, label, detail, action, date, palette):
    start, end, edge, ink = palette
    lines = wrap(title, width=23, max_lines=2, placeholder="…")
    heading = "".join(f'<tspan x="28" y="{85 + 28 * i}">{escape(line)}</tspan>'
                      for i, line in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="356" height="196" viewBox="0 0 356 196">
  <title>{escape(title)}</title>
  <defs><linearGradient id="wash" x2="1" y2="1" gradientUnits="objectBoundingBox">
    <stop stop-color="{start}"/><stop offset="1" stop-color="{end}"/>
  </linearGradient></defs>
  <rect width="356" height="196" fill="#fff"/>
  <rect x="7" y="9" width="342" height="178" rx="22" fill="url(#wash)" stroke="{edge}"/>
  <g font-family="Arial, Helvetica, sans-serif" fill="{ink}">
    <circle cx="32" cy="41" r="4" fill="{ink}"/>
    <text x="45" y="45" font-size="12" font-weight="700">{escape(shorten(label, 24, placeholder="…"))}</text>
    <text x="327" y="45" text-anchor="end" font-size="12">{date}</text>
    <text font-size="23" font-weight="700">{heading}</text>
    <text x="28" y="139" font-size="14">{escape(shorten(detail, 37, placeholder="…"))}</text>
    <text x="28" y="169" font-size="12" font-weight="700">{action}</text>
    <circle cx="317" cy="161" r="14" fill="#fff" fill-opacity=".8"/>
    <path d="M312 166l10-10m-9 0h9v9" fill="none" stroke="{ink}" stroke-width="1.7"
      stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>
'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    links = []
    assets = {}
    for entry in entries:
        metrics = " · ".join(METRICS.get(m, m) for m in entry.support.metrics)
        cards = [(entry.id, entry.title, "RELEASE", metrics, "View release")]
        for number, chain in enumerate(entry.chain, 1):
            metric = METRICS.get(chain.metric, chain.metric)
            language = {"zh": "Mandarin", "n/a": "Language independent"}.get(
                chain.language, chain.language.upper())
            cards.append((route_anchor(entry, number), TASK_NAMES.get(chain.task, task_label(chain.task)),
                          task_label(chain.task), f"{language} · {metric}", "View pipeline"))
        for i, (anchor, title, label, detail, action) in enumerate(cards):
            path = f"docs/news/cards/{anchor}.svg"
            assets[path] = tile(title, label, detail, action, entry.published_at.strftime("%d %b %Y"),
                                PALETTES[i % len(PALETTES)])
            alt = escape(f"{title} · {detail}", quote=True)
            links.append(f'<a href="{PAGES}#{anchor}"><img src="./{path}" width="356" alt="{alt}"></a>')
    # GitHub supplies native overflow scrolling for pre. Keep the image links
    # on one line so their white backgrounds form one continuous strip.
    strip = "<pre>" + "".join(links) + "</pre>" if links else "No releases yet."
    return f"## Recently supported\n\n{strip}\n\n[Explore all updates on GitHub Pages ↗]({PAGES})\n", assets
