"""Serious, compact release cards for the repository README."""

from html import escape
from textwrap import wrap

from .contract import Entry
from .web import METRICS, pipeline_brief, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"


def _lines(value: str, width: int, limit: int) -> list[str]:
    rows = [line for paragraph in value.splitlines() for line in wrap(paragraph, width)]
    if len(rows) > limit:
        rows = rows[:limit]
        rows[-1] = rows[-1].rstrip(".,") + "…"
    return rows


def _metric_labels(entry: Entry) -> str:
    labels = [METRICS.get(metric, metric.upper()) for metric in entry.support.metrics]
    if len(labels) <= 5:
        return " · ".join(labels)
    return " · ".join(labels[:4]) + f" · +{len(labels) - 4} more"


def _text_rows(values: list[str], x: int, y: int, size: int, fill: str,
               weight: int = 400, step: int = 18,
               family: str = "Arial,sans-serif") -> str:
    return "".join(
        f'<text x="{x}" y="{y + i * step}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}">{escape(value)}</text>'
        for i, value in enumerate(values)
    )


def tile(entry: Entry, number: int) -> str:
    """Render a white, linked card with only the announcement essentials."""
    title = _lines(entry.title, 44, 2)
    summary = _lines(entry.summary, 92, 2)
    brief = _lines(pipeline_brief(entry), 96, 2)
    metrics = _metric_labels(entry)
    tasks = " · ".join(task_label(task) for task in entry.support.tasks)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="258" viewBox="0 0 760 258" role="img" aria-labelledby="title desc">
<title id="title">{escape(entry.title)}</title>
<desc id="desc">{escape(entry.summary)}</desc>
<rect x="1" y="1" width="758" height="256" rx="14" fill="#ffffff" stroke="#d4d9df" stroke-width="2"/>
<rect x="24" y="0" width="72" height="4" rx="2" fill="#111827"/>
<g font-family="Arial, Helvetica, sans-serif">
  <text x="28" y="31" fill="#68717d" font-size="11" font-weight="700" letter-spacing="2">SURE / RECENT SUPPORT</text>
  <text x="732" y="31" text-anchor="end" fill="#68717d" font-size="11">{entry.published_at:%d %b %Y}</text>
  {_text_rows(title, 28, 75, 27, '#111827', 700, 29, 'Georgia,Times New Roman,serif')}
  {_text_rows(summary, 28, 124 if len(title) == 1 else 139, 14, '#3f4752', 400, 20)}
  <line x1="28" y1="164" x2="732" y2="164" stroke="#e1e5e9"/>
  <text x="28" y="188" fill="#68717d" font-size="10" font-weight="700" letter-spacing="1.4">METRICS</text>
  <text x="105" y="188" fill="#111827" font-size="12" font-weight="700">{escape(metrics)}</text>
  <text x="28" y="211" fill="#68717d" font-size="10" font-weight="700" letter-spacing="1.4">PIPELINE</text>
  {_text_rows(brief, 105, 211, 12, '#111827', 600, 17)}
  <text x="732" y="239" text-anchor="end" fill="#68717d" font-size="10">{escape(tasks)} · {len(entry.support.pipeline_ids):02d} route{'s' if len(entry.support.pipeline_ids) != 1 else ''} · DETAILS ↗</text>
</g>
</svg>'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    """Render newest-first cards inside a vertically scrollable README rail."""
    if not entries:
        return "No releases yet.\n", {}

    cards = []
    assets: dict[str, str] = {}
    for number, entry in enumerate(entries, 1):
        path = f"docs/news/cards/{entry.id}.svg"
        assets[path] = tile(entry, number)
        alt = escape(f"{entry.title} · {entry.summary} · {_metric_labels(entry)}", quote=True)
        cards.append(
            f'<p style="margin:0 0 16px"><a href="./docs/news/index.md#{escape(entry.id, quote=True)}">'
            f'<img src="./{path}" width="760" alt="{alt}"></a></p>'
        )

    rail = (
        '<div style="max-height:980px;overflow-y:auto;padding:16px;'
        'border:1px solid #d4d9df;border-radius:14px;background:#f7f8fa">\n'
        + "\n".join(cards)
        + "\n</div>"
    )
    board = f"## Recently supported\n\n{rail}\n\n[View announcement history ↗]({PAGES})\n"
    return board, assets
