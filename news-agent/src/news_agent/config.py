from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field

from .contract import Strict


class Config(Strict):
    repository: str = Field(default="PigeonDan1/sure-evaluation",
                            pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    checkout: Path = Path("..")
    base_branch: str = Field(default="main", pattern=r"^[A-Za-z0-9_./-]+$")
    remote: str = Field(default="origin", pattern=r"^[A-Za-z0-9_-]+$")
    ref: str = "refs/remotes/origin/main"
    fetch: bool = False
    mode: Literal["dry-run", "pr", "docs-commit"] = "dry-run"
    preview_from_working_tree: bool = False
    state_dir: Path = Path("state")
    log_dir: Path = Path("logs")
    endpoint: str = "https://api.kimi.com/coding/v1"
    timeout_seconds: int = Field(default=300, ge=1, le=600)
    attempts: int = Field(default=3, ge=1, le=5)
    max_output_tokens: int = Field(default=4000, ge=512, le=16000)


def load_config(path: Path) -> Config:
    config = Config.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    parent = path.resolve().parent
    for key in ("checkout", "state_dir", "log_dir"):
        value = getattr(config, key)
        setattr(config, key, (parent / value).resolve())
    # No implicit .env loading, fallback key or shared runtime directories.
    for value in (config.state_dir, config.log_dir):
        if "sure-maintainer" in value.parts:
            raise ValueError("news-agent requires independent runtime directories")
    return config
