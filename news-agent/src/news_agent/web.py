"""Self-contained visual release notes from the same validated announcement facts."""

from html import escape
from importlib.resources import files

from .contract import Entry

TASK_NAMES = {"sd": "Speaker diarization", "sa_asr": "Speaker-attributed ASR"}
METRICS = {"der": "DER", "cpcer": "cpCER"}


def task_label(task: str) -> str:
    return task.upper().replace("_", "-")


def node_label(node_id: str) -> str:
    stage, name = node_id.split("/", 1)
    if stage == "conversion":
        return "Submission conversion"
    if node_id == "normalization/ear1_norm":
        return "EAR-1 normalization"
    if node_id == "scoring/ear1_scorer":
        return "EAR-1 scorer"
    return name.replace("_", " ")


def source_link(entry: Entry, path: str) -> str:
    commit_url = entry.links.source_change
    repository_url = commit_url.rsplit("/commit/", 1)[0]
    return f"{repository_url}/blob/{entry.evidence.source_commit}/{path}"


def link(label: str, url: str, css: str = "") -> str:
    return f'<a class="{css}" href="{escape(url, quote=True)}">{escape(label)} ↗</a>'


def route_anchor(entry: Entry, number: int) -> str:
    return f"{entry.id}-route-{number}"


def pipeline_brief(entry: Entry) -> str:
    if entry.pipeline_brief:
        return entry.pipeline_brief
    paths = dict.fromkeys(" → ".join(node_label(n.id) for n in chain.nodes)
                          for chain in entry.chain)
    return "\n".join(paths)


def article(entry: Entry, previous: list[Entry]) -> str:
    aliases = "".join(f'<span id="{e.id}"></span>' for e in previous)
    rows = []
    for number, chain in enumerate(entry.chain, 1):
        old_anchors = "".join(f'<span id="{route_anchor(e, i)}"></span>' for e in previous
                              for i, c in enumerate(e.chain, 1) if c.pipeline_id == chain.pipeline_id)
        steps = " → ".join(f"{escape(n.id)} ({escape(n.version)})" for n in chain.nodes)
        pid = escape(chain.pipeline_id)
        rows.append(f'<li id="{route_anchor(entry, number)}">{old_anchors}'
                    f'<div><code>{pid}</code><small>{steps}</small></div>'
                    f'<button class="copy-button" data-copy="{pid}" aria-label="Copy pipeline ID">Copy</button></li>')
    docs = " ".join(link(task_label(p.rsplit("/", 1)[-1][:-3]), source_link(entry, p))
                    for p in entry.links.docs)
    tests = " ".join(link(p.rsplit("/", 1)[-1], source_link(entry, p)) for p in entry.links.tests)
    search = escape(" ".join([entry.title, entry.summary, pipeline_brief(entry), *entry.support.tasks,
                              *entry.support.metrics, *entry.support.pipeline_ids]))
    label = escape(" · ".join(task_label(t) for t in entry.support.tasks))
    count = len(rows)
    commit = entry.links.source_change
    return f'''<article class="release" id="{entry.id}" data-search="{search}"
      data-tasks="{escape(' '.join(entry.support.tasks))}">{aliases}
      <div class="release-date"><span class="timeline-dot"></span>
      <time datetime="{entry.published_at}"><a href="{escape(commit, quote=True)}"
      title="Open the source commit"><strong>{entry.published_at:%d %b}</strong><span>{entry.published_at.year}</span></a></time>
      <a class="release-type" href="{escape(commit, quote=True)}">Commit {entry.evidence.source_commit[:7]} ↗</a></div>
      <div class="release-content"><div class="release-kicker"><span class="status"><i></i> <span data-i18n="supported">Supported</span></span>
      <span class="release-ref">{label} · {count:02d} {'pipeline' if count == 1 else 'pipelines'}</span></div>
      <h2>{escape(entry.title)}</h2><p class="release-summary">{escape(entry.summary)}</p>
      <p class="flow">{escape(pipeline_brief(entry))}</p>
      <details><summary>{count} <span class="pipeline-word" data-en="{'pipeline' if count == 1 else 'pipelines'}" data-zh="{'条流水线' if count != 1 else '条流水线'}">{'pipeline' if count == 1 else 'pipelines'}</span></summary>
      <p class="release-summary"><strong data-i18n="beforeRun">Before you run</strong><br>{escape(entry.limitations)}</p><ul>{''.join(rows)}</ul>
      <p class="sources"><span data-i18n="taskDocumentation">Task documentation</span> &nbsp; {docs}</p>
      {f'<p class="sources"><span data-i18n="tests">Tests</span> &nbsp; {tests}</p>' if tests else ''}</details>
      </div></article>'''


def render_page(entries: list[Entry]) -> str:
    superseded = {e.supersedes for e in entries if e.supersedes}
    active = [e for e in entries if e.id not in superseded]
    by_id = {e.id: e for e in entries}
    tasks = sorted({task for entry in active for task in entry.support.tasks})
    chips = "".join(f'<button type="button" class="filter" data-task="{escape(t)}">{escape(task_label(t))}</button>'
                    for t in tasks)
    articles = []
    for entry in active:
        previous = []
        old = by_id.get(entry.supersedes)
        while old and old not in previous:
            previous.append(old)
            old = by_id.get(old.supersedes)
        articles.append(article(entry, previous))
    template = files("news_agent").joinpath("templates/news.html").read_text(encoding="utf-8")
    latest = active[0] if active else None
    repository = "https://github.com/bichengzhang09-crypto/sure-evaluation"
    replacements = {
        "{{REPOSITORY}}": repository,
        "{{DATE}}": latest.published_at.strftime("%d %b %Y") if latest else "No updates yet",
        "{{COUNT}}": str(len(active)),
        "{{ROUTES}}": str(len({p for e in active for p in e.support.pipeline_ids})),
        "{{TASKS}}": str(len({t for e in active for t in e.support.tasks})),
        "{{FILTERS}}": chips,
        "{{CONTENT}}": "".join(articles),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


def render_banner(entries: list[Entry]) -> str:
    count = len({p for entry in entries for p in entry.support.pipeline_ids})
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="184" viewBox="0 0 1120 184" role="img" aria-labelledby="title desc">
    <title id="title">SURE evaluation release notes</title>
    <desc id="desc">New evaluation capabilities with explicit pipelines and source evidence.</desc>
    <rect width="1120" height="184" rx="16" fill="#153f35"/>
    <g font-family="Arial, Helvetica, sans-serif">
      <text x="38" y="42" fill="#b6d5c7" font-size="12" font-weight="700" letter-spacing="3">SURE / RELEASE NOTES</text>
      <text x="36" y="98" fill="#f6f8ef" font-size="39" font-weight="700" letter-spacing="-1">New capabilities. Every step, explained.</text>
      <text x="38" y="140" fill="#c0d3c8" font-size="15">Exact pipelines · Reproducible evaluation · Source evidence</text>
      <rect x="946" y="34" width="136" height="116" rx="12" fill="#244d41"/>
      <text x="1014" y="88" text-anchor="middle" fill="#ddf1ac" font-size="40" font-weight="700">{count:02d}</text>
      <text x="1014" y="119" text-anchor="middle" fill="#c0d3c8" font-size="12">evaluation routes</text>
    </g></svg>'''
