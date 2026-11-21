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


def route_card(entry: Entry, chain, number: int) -> str:
    metric = METRICS.get(chain.metric, chain.metric)
    language = "Language independent" if chain.language == "n/a" else chain.language.upper()
    steps = []
    for node in chain.nodes:
        stage = node.id.split("/", 1)[0]
        steps.append(
            f'<li class="step {escape(stage)}"><span class="step-dot"></span>'
            f'<span>{escape(node_label(node.id))}</span>'
            f'<small>{escape(node.version)}</small></li>'
        )
    steps.append('<li class="step output"><span class="step-dot"></span>'
                 '<span>report.json</span><small>output</small></li>')
    return f'''<section class="route-card" id="{route_anchor(entry, number)}" aria-label="{escape(task_label(chain.task))} route">
      <div class="route-heading"><div class="route-name"><span class="route-number">{number:02d}</span>
      <div><h4>{escape(TASK_NAMES.get(chain.task, task_label(chain.task)))}</h4>
      <p>{escape(task_label(chain.task))} <span>·</span> {escape(language)}</p></div></div>
      <span class="metric">{escape(metric)}</span></div>
      <ol class="pipeline" aria-label="Ordered evaluation steps">{''.join(steps)}</ol>
      <div class="pipeline-id"><div><span class="code-label">EXACT PIPELINE ID</span>
      <code>{escape(chain.pipeline_id)}</code></div>
      <button class="copy-button" type="button" data-copy="{escape(chain.pipeline_id, quote=True)}"
        aria-label="Copy {escape(task_label(chain.task))} pipeline ID"><svg width="12" height="12" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="5" y="5" width="9" height="9" rx="1.5" stroke="currentColor"/><path d="M10 3V2H2v8h1" stroke="currentColor"/></svg> Copy</button></div>
    </section>'''


def article(entry: Entry, superseded: bool) -> str:
    routes = "".join(route_card(entry, chain, i + 1) for i, chain in enumerate(entry.chain))
    docs = "".join(link(task_label(path.rsplit("/", 1)[-1][:-3]), source_link(entry, path), "resource-link")
                   for path in entry.links.docs)
    tests = "".join(link(path, source_link(entry, path)) for path in entry.links.tests)
    related = "".join(link(f"Related source {i + 1}", url)
                      for i, url in enumerate(entry.links.related_changes))
    revised = '<span class="revision-badge">Earlier revision</span>' if superseded else ""
    searchable = escape(" ".join([entry.title, entry.summary, *entry.support.tasks,
                                  *entry.support.metrics, *entry.support.pipeline_ids]), quote=True)
    return f'''<article class="release" id="{entry.id}" data-search="{searchable}"
      data-tasks="{escape(' '.join(entry.support.tasks), quote=True)}">
      <div class="release-date"><span class="timeline-dot"></span><time datetime="{entry.published_at}">
      <strong>{entry.published_at.strftime('%d %b')}</strong><span>{entry.published_at.year}</span></time>
      <span class="release-type">Capability update</span></div>
      <div class="release-content"><div class="release-kicker"><span class="status"><i></i> Supported</span>
      <span class="release-ref">{len(entry.chain):02d} evaluation routes</span>{revised}</div>
      <h2>{escape(entry.title)}</h2><p class="release-summary">{escape(entry.summary)}</p>
      <div class="routes">{routes}</div>
      <div class="run-note"><span class="note-icon" aria-hidden="true">i</span>
      <div><h3>Before you run</h3><p>{escape(entry.limitations)}</p></div></div>
      <div class="release-resources"><div class="resource-group"><span class="code-label">TASK GUIDES</span>{docs}</div>
      {link('Pipeline catalog', source_link(entry, entry.links.catalog), 'catalog-link')}</div>
      <details class="evidence"><summary><span><span class="evidence-icon" aria-hidden="true">✓</span>
      Source &amp; validation</span><span class="evidence-ref">{entry.evidence.source_commit[:7]} <b>+</b></span></summary>
      <div class="evidence-body"><p>{escape(entry.evidence.test_result)}</p>
      <div class="evidence-links">{link('Source commit', entry.links.source_change)}{related}{tests}</div></div></details>
      </div></article>'''


def render_page(entries: list[Entry]) -> str:
    superseded = {e.supersedes for e in entries if e.supersedes}
    active = [e for e in entries if e.id not in superseded]
    tasks = sorted({task for entry in active for task in entry.support.tasks})
    pipelines = {pid for entry in active for pid in entry.support.pipeline_ids}
    latest = active[0] if active else None
    repository = (latest.links.source_change.rsplit("/commit/", 1)[0]
                  if latest else "https://github.com/PigeonDan1/sure-evaluation")
    chips = "".join(f'<button type="button" class="filter" data-task="{escape(task)}">'
                    f'{escape(task_label(task))}</button>' for task in tasks)
    content = "".join(article(e, e.id in superseded) for e in entries)
    template = files("news_agent").joinpath("templates/news.html").read_text(encoding="utf-8")
    replacements = {
        "{{REPOSITORY}}": escape(repository, quote=True),
        "{{DATE}}": latest.published_at.strftime("%d %b %Y") if latest else "No updates yet",
        "{{COUNT}}": str(len(entries)), "{{ROUTES}}": str(len(pipelines)),
        "{{TASKS}}": str(len(tasks)), "{{FILTERS}}": chips, "{{CONTENT}}": content,
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
