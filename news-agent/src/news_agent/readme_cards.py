"""Small linked release cards for GitHub's horizontally scrollable README."""

from html import escape
from textwrap import wrap

from .contract import Entry
from .web import METRICS, PR_NUMBERS, pipeline_brief, pr_url, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"
PALETTES = (
    ("#eff9e7", "#d9f1e8", "#b7d9c5", "#22594a"),
    ("#edf8ff", "#dfe9fb", "#c1d6e9", "#345775"),
    ("#fff5e3", "#fae4de", "#e8cfc1", "#794d3d"),
    ("#f6f2ff", "#e8e5f9", "#d7cfea", "#584d78"),
    ("#edf8f6", "#d8edf1", "#bad8df", "#315e68"),
)
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
    """Render the wide card used by the announcement page."""
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


def readme_tile(entry: Entry, palette: tuple[str, str, str, str]) -> str:
    """Render a compact card sized for the README's horizontal strip."""
    start, end, edge, ink = palette
    title = _lines(entry.title, 27, 2)
    summary = _lines(_card_summary(entry), 47, 2)
    brief = _lines(pipeline_brief(entry), 45, 2)
    metrics = _lines(_metric_labels(entry), 38, 1)
    tasks = " · ".join(task_label(task) for task in entry.support.tasks)
    pr_number = PR_NUMBERS.get(entry.evidence.source_commit)
    pr_label = f"PR #{pr_number} ↗" if pr_number else "SOURCE ↗"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="398" height="264" viewBox="0 0 398 264" role="img" aria-labelledby="title desc">
<title id="title">{escape(entry.title)}</title>
<desc id="desc">{escape(_card_summary(entry))}</desc>
<defs><linearGradient id="wash" x2="1" y2="1"><stop stop-color="{start}"/><stop offset="1" stop-color="{end}"/></linearGradient></defs>
<rect width="398" height="264" fill="#ffffff"/>
<rect x="7" y="8" width="384" height="248" rx="22" fill="url(#wash)" stroke="{edge}"/>
<g font-family="Arial, Helvetica, sans-serif" fill="{ink}">
  <text x="26" y="37" font-size="11" font-weight="700">RECENT SUPPORT · {escape(tasks)}</text>
  <text x="369" y="37" text-anchor="end" font-size="12">{entry.published_at:%d %b %Y}</text>
  {_text_rows(title, 26, 71, 22, ink, 700, 24)}
  {_text_rows(summary, 26, 119 if len(title) == 1 else 143, 13, ink, 400, 18)}
  <path d="M26 169h346" stroke="{edge}"/>
  <text x="26" y="189" font-size="10" font-weight="700" letter-spacing="1.2">METRICS</text>
  {_text_rows(metrics, 105, 189, 12, ink, 700, 16)}
  <text x="26" y="211" font-size="10" font-weight="700" letter-spacing="1.2">PIPELINE</text>
  {_text_rows(brief, 105, 211, 11, ink, 600, 15)}
  <text x="26" y="241" font-size="12" font-weight="700">{escape(pr_label)}</text>
  <text x="369" y="241" text-anchor="end" font-size="10" font-family="monospace">{len(entry.support.pipeline_ids):02d} route{'s' if len(entry.support.pipeline_ids) != 1 else ''}</text>
</g>
</svg>'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    """Render linked cards on one line so GitHub provides horizontal scrolling."""
    if not entries:
        return "No releases yet.\n", {}

    links = []
    assets: dict[str, str] = {}
    for index, entry in enumerate(entries):
        page_path = f"docs/news/cards/{entry.id}.svg"
        readme_path = f"docs/news/readme-cards/{entry.id}.svg"
        assets[page_path] = tile(entry)
        assets[readme_path] = readme_tile(entry, PALETTES[index % len(PALETTES)])
        alt = escape(f"{entry.title} · {_card_summary(entry)} · {_metric_labels(entry)}", quote=True)
        links.append(
            f'<a href="{escape(pr_url(entry), quote=True)}">'
            f'<img src="./{readme_path}" width="398" alt="{alt}"></a>'
        )
    strip = "<pre>" + "".join(links) + "</pre>"
    board = f"## Recently supported\n\n{strip}\n\n[View announcement history ↗]({PAGES})\n"
    return board, assets
