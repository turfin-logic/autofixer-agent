"""Review-only GitHub publisher with strict source and edit checks."""
from __future__ import annotations

import os
import re
import uuid
from typing import Any

from patching import apply_edits, validate_edits


class GitHubBotError(RuntimeError): pass

def safe_path(path: str) -> bool:
    p = path.replace("\\", "/")
    return bool(p.endswith(".py") and not p.startswith("/") and not p.startswith((".git/", ".env")) and ".." not in p.split("/"))

class GitHubBot:
    def __init__(self, *, repo: Any | None = None, token: str | None = None, repo_name: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN"); self.repo_name = repo_name or os.getenv("GITHUB_REPO")
        if not self.token or not self.repo_name: raise GitHubBotError("GITHUB_TOKEN and GITHUB_REPO are required; publishing is never mocked")
        self.repo = repo
        if self.repo is None:
            from github import Github
            self.repo = Github(self.token).get_repo(self.repo_name)

    def create_pull_request(self, analysis: dict[str, Any], proposal: dict[str, Any]) -> str:
        path = str(analysis.get("file", ""))
        if not safe_path(path): raise GitHubBotError("analysis points outside the Python source allowlist")
        base = self.repo.get_branch("main").commit.sha
        content = self.repo.get_contents(path, ref=base)
        if isinstance(content, list) or not getattr(content, "decoded_content", None): raise GitHubBotError("target is not readable text")
        source = content.decoded_content.decode("utf-8")
        edits = validate_edits(proposal, source); updated = apply_edits(source, edits)
        if updated == source: raise GitHubBotError("proposal makes no change")
        branch = f"autofix-{re.sub(r'[^a-z0-9]+', '-', str(analysis.get('error','error')).lower()).strip('-')}-{uuid.uuid4().hex[:8]}"
        self.repo.create_git_ref(ref=f"refs/heads/{branch}", sha=base)
        self.repo.update_file(path=path, message=f"AutoFixer: propose {analysis.get('error', 'error')} fix", content=updated, sha=content.sha, branch=branch)
        pr = self.repo.create_pull(title=f"Review proposed fix for {path}", base="main", head=branch, draft=True, body=(
            "## AutoFixer review proposal\n\nGenerated code was not executed. This draft contains bounded exact-text edits.\n\n"
            f"**File:** `{path}`  \n**Reported line:** `{analysis.get('line', '?')}`\n\nRun the project tests and review the diff before merging."))
        return pr.html_url
