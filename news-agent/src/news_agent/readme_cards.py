"""Compact release announcements for the repository README."""

from html import escape
import re

from .contract import Entry
from .web import METRICS, task_label

PAGES = "https://bichengzhang09-crypto.github.io/sure-evaluation/"
def short_summary(value: str) -> str:
    return re.split(r"(?<=[.!?])\s+", value.strip(), maxsplit=1)[0]


def metric_labels(entry: Entry) -> str:
    labels = [METRICS.get(metric, metric.upper()) for metric in entry.support.metrics]
    if len(labels) <= 5:
        return " · ".join(labels)
    return " · ".join(labels[:4]) + f" · +{len(labels) - 4} more"


def announcement(entry: Entry) -> str:
    metrics = metric_labels(entry)
    tasks = " · ".join(task_label(task) for task in entry.support.tasks)
    routes = len(entry.support.pipeline_ids)
    full = f"./docs/news/index.md#{escape(entry.id, quote=True)}"
    return f'''<table border="1" bordercolor="#d0d7de" cellpadding="20" cellspacing="0" width="100%" bgcolor="#ffffff">
<tr><td>
<p><sub><strong>SURE / RECENT SUPPORT</strong> &nbsp;·&nbsp; {entry.published_at.strftime('%d %b %Y')}</sub></p>
<h2>{escape(entry.title)}</h2>
<p>{escape(short_summary(entry.summary))}</p>
<table border="0" cellpadding="5" cellspacing="0" width="100%">
<tr><td width="25%"><sub><strong>METRICS</strong></sub></td><td><strong>{escape(metrics)}</strong></td></tr>
<tr><td><sub><strong>PIPELINES</strong></sub></td><td><strong>{routes} exact route{'s' if routes != 1 else ''}</strong></td></tr>
<tr><td><sub><strong>TASKS</strong></sub></td><td><strong>{escape(tasks)}</strong></td></tr>
</table>
<p><a href="{full}"><strong>Read full announcement →</strong></a></p>
</td></tr>
</table>'''


def readme_board(entries: list[Entry]) -> tuple[str, dict[str, str]]:
    if not entries:
        return "No releases yet.\n", {}
    updates = "\n\n".join(announcement(entry) for entry in entries)
    return f"{updates}\n\n<p><sub><a href=\"{PAGES}\">View announcement history ↗</a></sub></p>\n", {}
