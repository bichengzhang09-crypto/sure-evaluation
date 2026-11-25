"""Serious, compact release cards for the repository README."""

from html import escape
from textwrap import wrap

from .contract import Entry
from .web import METRICS, pipeline_brief, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"
PR_NUMBERS = {
    "3853dab1db5d7d44691b25a6620932742a1c0a50": 49,
    "c1bc96cf865baef07e37f702a8286d3a6c68a5a2": 47,
    "549eb711483e7c4e515479864bca8e0abd558572": 44,
    "137fbcc8b89b8c96ca10e641d409808c22165435": 38,
    "abfdd68801cce39e28a27ccfb9335deee091a27f": 40,
    "204ffe814fa7b0797e8471d80916339d1dfd0690": 39,
}
CARD_SUMMARIES = {
    "ear-1": "Score EAR-1 submissions for speaker diarization with DER and Mandarin speaker-attributed ASR with cpCER.",
    "ear-1-scoring": "Score EAR-1 submissions for speaker diarization with DER and Mandarin speaker-attributed ASR with cpCER.",
    "fd-bench": "Evaluate full-duplex dialogue timing by measuring response start, early reply, and interruption behavior.",
    "slu-judge": "Score spoken-language understanding answers against a custom rubric with an API-based LLM judge.",
    "etc-bench": "Canonicalize equivalent transcript forms in 12 languages before CER or WER scoring.",
    "openbench-se": "Evaluate enhanced speech for intelligibility, spectral distortion, and predicted quality with optional metrics.",
}


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


def _pr_url(entry: Entry) -> str:
    repository = entry.links.source_change.rsplit("/commit/", 1)[0]
    number = PR_NUMBERS.get(entry.evidence.source_commit)
    if number is None:
        return entry.links.source_change
    return f"{repository}/pull/{number}"


def _card_summary(entry: Entry) -> str:
    return CARD_SUMMARIES.get(entry.id, entry.summary)


def _text_rows(values: list[str], x: int, y: int, size: int, fill: str,
               weight: int = 400, step: int = 18,
               family: str = "Arial,sans-serif") -> str:
    return "".join(
        f'<text x="{x}" y="{y + i * step}" fill="{fill}" font-family="{family}" '
        f'font-size="{size}" font-weight="{weight}">{escape(value)}</text>'
        for i, value in enumerate(values)
    )


def tile(entry: Entry) -> str:
    """Render a white, linked card with only the announcement essentials."""
    title = _lines(entry.title, 44, 2)
    summary = _lines(_card_summary(entry), 92, 2)
    brief = _lines(pipeline_brief(entry), 96, 2)
    metrics = _metric_labels(entry)
    tasks = " · ".join(task_label(task) for task in entry.support.tasks)
    pr_number = PR_NUMBERS.get(entry.evidence.source_commit)
    pr_label = f"PR #{pr_number} ↗" if pr_number else "SOURCE ↗"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="280" viewBox="0 0 760 280" role="img" aria-labelledby="title desc">
<title id="title">{escape(entry.title)}</title>
<desc id="desc">{escape(_card_summary(entry))}</desc>
<rect x="1" y="1" width="758" height="278" rx="14" fill="#ffffff" stroke="#d4d9df" stroke-width="2"/>
<rect x="24" y="0" width="72" height="4" rx="2" fill="#111827"/>
<g font-family="Arial, Helvetica, sans-serif">
  <text x="28" y="31" fill="#68717d" font-size="11" font-weight="700" letter-spacing="2">RECENT SUPPORT</text>
  <text x="732" y="31" text-anchor="end" fill="#68717d" font-size="11">{entry.published_at:%d %b %Y}</text>
  {_text_rows(title, 28, 77, 29, '#111827', 700, 31, 'Georgia,Times New Roman,serif')}
  {_text_rows(summary, 28, 126 if len(title) == 1 else 144, 14, '#3f4752', 400, 20)}
  <line x1="28" y1="168" x2="732" y2="168" stroke="#e1e5e9"/>
  <text x="28" y="193" fill="#68717d" font-size="10" font-weight="700" letter-spacing="1.4">METRICS</text>
  <text x="112" y="193" fill="#111827" font-size="13" font-weight="700">{escape(metrics)}</text>
  <text x="28" y="217" fill="#68717d" font-size="10" font-weight="700" letter-spacing="1.4">PIPELINE</text>
  {_text_rows(brief, 112, 217, 12, '#111827', 600, 17)}
  <text x="28" y="264" fill="#68717d" font-size="10">{escape(tasks)} · {len(entry.support.pipeline_ids):02d} route{'s' if len(entry.support.pipeline_ids) != 1 else ''}</text>
  <text x="732" y="264" text-anchor="end" fill="#111827" font-size="11" font-weight="700">{escape(pr_label)}</text>
</g>
</svg>'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    """Render newest-first cards inside a vertically scrollable README rail."""
    if not entries:
        return "No releases yet.\n", {}

    cards = []
    assets: dict[str, str] = {}
    for entry in entries:
        path = f"docs/news/cards/{entry.id}.svg"
        assets[path] = tile(entry)
        alt = escape(f"{entry.title} · {_card_summary(entry)} · {_metric_labels(entry)}", quote=True)
        cards.append(
            f'<p style="margin:0 0 16px"><a href="{escape(_pr_url(entry), quote=True)}">'
            f'<img src="./{path}" width="760" alt="{alt}"></a></p>'
        )

    rail = (
        '<div style="position:relative">'
        '<div style="height:460px;overflow-y:scroll;padding:16px 16px 34px;'
        'border:1px solid #d4d9df;border-radius:14px;background:#f7f8fa">\n'
        + "\n".join(cards)
        + '\n</div><div aria-hidden="true" style="position:absolute;right:1px;bottom:1px;left:1px;'
          'height:72px;border-radius:0 0 13px 13px;pointer-events:none;'
          'background:linear-gradient(to bottom,rgba(247,248,250,0),#f7f8fa 88%)"></div></div>'
    )
    board = f"## Recently supported\n\n{rail}\n\n[View announcement history ↗]({PAGES})\n"
    return board, assets
