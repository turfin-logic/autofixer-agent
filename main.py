"""Explicit one-shot entry point; repository writes require --publish."""
from __future__ import annotations

import argparse
from pathlib import Path

from agent import AutoFixAgent
from github_bot import GitHubBot


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draft review proposal from an error log")
    parser.add_argument("--log", default="error.log"); parser.add_argument("--publish", action="store_true")
    args = parser.parse_args(); analysis = AutoFixAgent().analyze_error(Path(args.log).read_text(encoding="utf-8"))
    if not args.publish:
        print(f"Analysis complete for {analysis['file']} (dry run; no repository write)"); return 0
    bot = GitHubBot(); source_obj = bot.repo.get_contents(analysis["file"], ref="main")
    proposal = AutoFixAgent().generate_patch(analysis, source_obj.decoded_content.decode("utf-8"))
    print(bot.create_pull_request(analysis, proposal)); return 0

if __name__ == "__main__": raise SystemExit(main())
