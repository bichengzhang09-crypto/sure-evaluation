"""Serious, compact release cards for the repository README."""

from html import escape
from textwrap import wrap

from .contract import Entry
from .web import METRICS, PR_NUMBERS, pipeline_brief, pr_url, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"
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


def rail_tile(entries: list[Entry]) -> str:
    """Render a fixed README preview of the live scroll rail."""
    elements = []
    for index, entry in enumerate(entries):
        card = tile(entry)
        body = card[card.index("<rect "):card.rindex("</svg>")]
        elements.append(f'<g transform="translate(18 {18 + index * 296})">{body}</g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="460" viewBox="0 0 820 460" role="img" aria-labelledby="title desc">
<title id="title">Latest SURE evaluation support</title>
<desc id="desc">A fixed preview of the latest announcement cards. Open the live announcement rail for independent scrolling.</desc>
<defs><clipPath id="window"><rect x="10" y="10" width="778" height="440" rx="12"/></clipPath><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7f8fa" stop-opacity="0"/><stop offset="0.88" stop-color="#f7f8fa" stop-opacity="0.96"/><stop offset="1" stop-color="#f7f8fa"/></linearGradient></defs>
<rect width="820" height="460" rx="14" fill="#f7f8fa" stroke="#d4d9df" stroke-width="2"/>
<g clip-path="url(#window)">{''.join(elements)}<rect x="10" y="372" width="778" height="78" fill="url(#fade)"/></g>
<rect x="798" y="24" width="4" height="412" rx="2" fill="#e1e5e9"/><rect x="798" y="24" width="4" height="142" rx="2" fill="#68717d"/>
</svg>'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    """Render a GitHub-compatible preview and link to the live scroll rail."""
    if not entries:
        return "No releases yet.\n", {}

    assets: dict[str, str] = {}
    for entry in entries:
        path = f"docs/news/cards/{entry.id}.svg"
        assets[path] = tile(entry)
    assets["docs/news/readme-rail.svg"] = rail_tile(entries)
    board = (
        "## Recently supported\n\n"
        '<p><a href="' + escape(PAGES + "#latest-support", quote=True) + '">'
        '<img src="./docs/news/readme-rail.svg" width="820" '
        'alt="Latest evaluation support. Open the live announcement rail for independent scrolling."></a></p>\n\n'
        '<details><summary>Open source PRs for these releases</summary>\n\n<ul>\n'
        + "\n".join(
            f'<li><a href="{escape(pr_url(entry), quote=True)}">'
            f'{escape(entry.title)} · PR ↗</a></li>' for entry in entries
        )
        + "\n</ul>\n</details>\n\n"
        f"[Open the live announcement rail ↗]({PAGES}#latest-support)\n"
    )
    return board, assets
