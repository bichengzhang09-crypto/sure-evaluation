# SURE news-agent

## 公告的实际展示

同一份经过事实校验的 entry 会生成两种展示，均由 `render` 和轮询流程自动更新：

- `docs/news/index.md`、`latest.md` 和英文 README：兼容 GitHub 的 SVG 横幅、
  路线表格、折叠 pipeline ID、版本化节点和来源证据。
- `docs/news/index.html`：独立网页，内嵌 CSS、JavaScript 和 SVG，不请求外部字体
  或样式资源。支持深浅色、手机布局、按任务/关键词筛选、复制精确 pipeline ID
  和展开验证证据。保存该 HTML 后直接用浏览器打开即可。

GitHub 仓库页面可以展示 Markdown/SVG；独立 HTML 需要用浏览器打开或通过静态
服务访问，GitHub 文件查看器本身不运行此网页。目前没有发布 GitHub Pages。

当前本地可视预览服务为 `news-agent-preview.service`，仅监听服务器
`127.0.0.1:18765`。远程使用时先将服务器的 18765 端口转发到本机，再访问：

- `http://127.0.0.1:18765/`：统一预览入口，默认展示完整仓库 README，可切换
  “公告历史”和“独立网页”，支持桌面/手机宽度及“定位公告”。
- `http://127.0.0.1:18765/readme.html`：当前完整 README 的 GitHub 风格渲染。
- `http://127.0.0.1:18765/readme-news.html`：只查看 README 中的公告区。
- `http://127.0.0.1:18765/news-history.html`：仓库 `docs/news/index.md` 的渲染。
- `http://127.0.0.1:18765/announcement.html`：独立交互公告页。
- `http://127.0.0.1:18765/pr-47.html`：使用此前真实 Kimi 输出的旧 PR #47 公告。

README 与历史预览直接读取当前工作区的 Markdown，图片内嵌到页面，折叠区可以
直接展开，不需要在终端打开图片。预览排版模拟 GitHub；当前尚未提交主分支，
远端 GitHub 仓库没有因此更新。修改 Markdown 后，可在仓库根目录刷新预览：

```bash
conda run -n news-agent python news-agent/deploy/build_preview.py
```

该工具使用可选依赖 `news-agent[preview]` 中的 `markdown-it-py`，部署环境已安装。

真实 Chromium 截图和交互检查报告位于本仓库
`news-agent/state/visual-preview/`，包括桌面、手机、深色模式和 README 预览。
该目录已忽略，不进入 Git。停止预览服务可使用
`systemctl --user disable --now news-agent-preview.service`。

## 运行方式

独立的公告生成器，固定使用 Kimi Code `k3.1-pro`。默认只生成本地预览。
实现不导入其他 agent，不加载共享 `.env`，仅使用
`NEWS_AGENT_KIMI_API_KEY`；SQLite、锁、日志和 systemd 单元均独立。

本轮按用户授权，与 sure-maintainer 使用同一个 key；仅在部署时复制 key 值到
news-agent 自己的凭据文件，运行时不读取 sure-maintainer 的 `.env`。

## 本地使用

以下命令在 `sure-evaluation` 仓库根目录运行：

```bash
python -m venv news-agent/.venv
news-agent/.venv/bin/python -m pip install -e 'news-agent[dev]'
cp news-agent/config.yaml.example news-agent/config.yaml
news-agent/.venv/bin/sure-news-agent --config news-agent/config.yaml doctor
news-agent/.venv/bin/sure-news-agent --config news-agent/config.yaml check
news-agent/.venv/bin/python -m pytest news-agent/tests -q
```

不安装包也可在已具备 PyYAML、Pydantic 2 的环境中运行：

```bash
PYTHONPATH=news-agent/src python -m news_agent check
PYTHONPATH=news-agent/src python -m news_agent render --output /tmp/sure-news-preview
```

`render` 读取工作区已审核的 entry，校验其指定提交中的历史事实，再生成预览。
只有显式 `render --write` 才更新当前工作区文档，所有校验在写入前完成。
`check` 验证 schema、节点顺序/版本、证据摘要、英文 entry ID、链接和页面新鲜度。
schema 来自 `contract.Entry.model_json_schema()`，测试会检查静态 JSON 与运行时
契约一致。提示词随 Python 包安装在 `src/news_agent/prompts/news_v1.md`。

## 轮询与模型

`config.yaml` 的路径相对于配置文件位置解析。默认 `ref` 为
`refs/remotes/origin/main`；`fetch: false` 便于离线使用。生产轮询设为
`fetch: true`，读取主分支但不切换、不修改当前工作区。应保留足够 Git 历史，
使 cursor 和 entry 的来源提交始终可读。

在公告模板尚未合并时，可在独立验证 checkout 中显式设置
`preview_from_working_tree: true`。它使用该 checkout 的本地 README 标记和
已审核 entry 生成预览，pipeline 事实仍从目标提交读取。该选项默认关闭，
仅限 `dry-run`；`pr` 和 `docs-commit` 模式会拒绝运行。

```bash
# 通过安全的环境变量管理方式提供独立的 NEWS_AGENT_KIMI_API_KEY。
PYTHONPATH=news-agent/src python -m news_agent --config news-agent/config.yaml doctor --smoke
PYTHONPATH=news-agent/src python -m news_agent --config news-agent/config.yaml run
PYTHONPATH=news-agent/src python -m news_agent --config news-agent/config.yaml status
```

首次 `run` 仅将 cursor 初始化到当前主分支，不自动为历史能力发公告。
需要回填时显式传 `run --since <base-commit>`。没有新增 atomic pipeline 的变更
只推进 cursor，不调用模型；已存在于公告中的 pipeline 也不会重复公告。
仅新增独立 node、格式/测试调整或同 ID 内部实现变更不算新增可用评测能力。

检测到新增 pipeline 后，程序交叉验证 catalog、route 和 manifest，并冻结
提交、文件、摘要、受限 diff、catalog 行和提示词。模型只提供英文标题、摘要
和限制文案；事实、日期、链接和发布范围由程序确定。完整 catalog 留在独立
状态库，发给模型的 catalog 内容仅包含候选行。

每个候选以 repository、base branch、head SHA、catalog digest、prompt version
和固定模型组成幂等键。成功文案被缓存；发布重试不重新请求模型。
网络超时和 429/5xx 有有限重试；模型截断、错误模型、无效 JSON、事实不一致
或链接错误均终止本轮，不写 README，保留失败任务并保持成功 cursor。
下次 `run` 会重试。进程锁避免定时器与手动运行重叠；`status` 展示错误原因。

## 离线端到端验证

```bash
PYTHONPATH=news-agent/src python -m news_agent --config news-agent/config.yaml run \
  --since <引入新能力之前的提交> --copy-file news-agent/tests/fixtures/copy.json
```

这只适用于已提交公告标记的新能力 fixture/测试 checkout。模型文案 fixture
仅可用于 dry-run，标记为人工来源，缓存后也不能直接提升为远端发布。
真实仓库中的首条 `ear-1.yaml` 已覆盖两条 EAR-1 路线，所以不会为同一能力
生成第二条公告。初始 EAR-1 公告是人工整理的，不代表已调用真实模型。

预览位于 `state/previews/<job-key>/`，包含完整候选文件和 `preview.diff`。
dry-run 不修改源工作区、不创建 commit/PR、不调用 GitHub 写接口。
已有 entry 的事实变更必须使用新 ID、新 `revision` 和 `supersedes`，保留旧文件；
README 仅展示未被替代的最近三条，英文历史保留全部修订。

## 发布

远端 publisher 代码已实现，生产接入前应先完成真实模型 smoke 和一段时间的
dry-run，再在测试仓库验证。需要 Git、GitHub CLI `gh` 以及该仓库的推送/PR
权限。`repository` 和 `remote` 应指向同一个 GitHub 仓库。

```bash
PYTHONPATH=news-agent/src python -m news_agent --config news-agent/config.yaml run --mode pr
```

`pr` 使用独立 worktree，从当前主分支生成仅修改公告的 commit，推送到
`news-agent/<job-key-prefix>` 并创建文档 PR；不会自动合并。
推送后失败可恢复，已有 PR 不会重复创建。`docs-commit` 同样只推送到独立
news 分支，但不创建 PR，不直接提交到主分支。两种模式只允许
`docs/news/**/*.md`、`docs/news/**/*.yaml`、固定的 `docs/news/index.html` 和
`docs/news/banner.svg`、英文 `README.md` 和可选 `NEWS.md`；
README 内容只能改变 `SURE-NEWS` 标记区。首次在 README 插入标记是本实现
的一次性人工变更，后续生成器不会自行创建或修补缺失的标记。

## systemd 用户定时器

`deploy/` 提供独立 service/timer 模板，本实现不会安装或启动它们。
模板使用 `%h/sure-news-checkout` 中的独立 checkout 和该 checkout 内
`news-agent/.venv` 的安装。使用其他位置时通过 systemd drop-in 修改路径。

1. 在独立 checkout 中安装 `news-agent`，创建
   `~/.config/sure-news-agent/config.yaml`，将 `checkout` 改为真实绝对路径，
   `state_dir` 改为用户目录下 `.local/state/sure-news-agent/state` 的绝对路径，
   `log_dir` 改为同级 `logs` 的绝对路径。创建这些目录，先保留 `mode: dry-run`。
2. 在 `~/.config/sure-news-agent/credentials.env` 中配置独立变量
   `NEWS_AGENT_KIMI_API_KEY`，权限设为 `0600`，不要把凭据放入仓库。
3. 在启用 fetch 前，先手动验证 checkout 的 origin、目标分支和仓库权限。
4. 审核模板后复制到 `~/.config/systemd/user/`，执行
   `systemctl --user daemon-reload`，再执行
   `systemctl --user enable --now sure-news-agent.timer`。

每 30 分钟轮询一次，另有随机延迟。用
`journalctl --user -u sure-news-agent.service` 和独立 `logs/news-agent.log`
诊断。停用时执行 `systemctl --user disable --now sure-news-agent.timer`。
远端发布和长期运行观察仍需后续验收。

## 当前已部署实例

已创建 Conda 环境 `news-agent`（Python 3.12），并安装本包、pytest 和 Ruff。
运行实例使用独立 checkout 和包副本；工作区实现仍保留本地未提交状态。

| 内容 | 位置或状态 |
| --- | --- |
| 配置 | `~/.config/news-agent/config.yaml` |
| 凭据 | `~/.config/news-agent/credentials.env`，权限 `0600` |
| 部署目录 | `~/.local/share/news-agent/` |
| 状态和日志 | `~/.local/state/news-agent/` |
| 用户定时器 | `news-agent.timer`，已启用，每 30 分钟运行并带随机延迟 |
| 退出登录后运行 | 用户 `linger` 已开启 |
| 发布模式 | 配置和 service 均显式指定 `dry-run` |
| 真实回放报告 | `~/.local/state/news-agent/validation/old-pr-validation.json` |

可直接使用命令（wrapper 自动加载独立凭据和配置）：

```bash
news-agent doctor
news-agent status
news-agent check
systemctl --user status news-agent.timer
journalctl --user -u news-agent.service
systemctl --user disable --now news-agent.timer
```

旧 PR #47 的真实回放成功检出两条 EAR-1 pipeline，调用一次 `k3.1-pro` 后
生成完整本地预览与 diff；重复轮询和旧 PR #49 都未再次调用模型。
没有创建或修改 GitHub PR，也没有提交主分支。
整个仓库 Ruff 检查通过，专项测试在 `news-agent` 环境中 `54 passed`。
