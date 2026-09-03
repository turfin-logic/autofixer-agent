"""Bounded exact-text patch validation; generated code is parsed, never run."""
from __future__ import annotations

import ast
from typing import Any


class PatchError(ValueError): pass

def validate_edits(proposal: dict[str, Any], source: str) -> list[dict[str, str]]:
    edits = proposal.get("edits") if isinstance(proposal, dict) else None
    if not isinstance(edits, list) or not 1 <= len(edits) <= 5: raise PatchError("edits must contain one to five changes")
    spans: list[tuple[int,int]] = []; clean: list[dict[str,str]] = []
    for edit in edits:
        if not isinstance(edit, dict) or not isinstance(edit.get("old"), str) or not isinstance(edit.get("new"), str): raise PatchError("each edit needs string old and new")
        old, new = edit["old"], edit["new"]
        if not old or len(old) > 20_000 or old not in source: raise PatchError("edit text is missing or too large")
        start = source.index(old); end = start + len(old)
        if source.count(old) != 1: raise PatchError("edit text must match exactly once")
        if any(start < other_end and other_start < end for other_start, other_end in spans): raise PatchError("edits overlap")
        spans.append((start,end)); clean.append({"old":old,"new":new})
    result = apply_edits(source, clean)
    try: ast.parse(result)
    except SyntaxError as exc: raise PatchError("edited source is not valid Python") from exc
    return clean

def apply_edits(source: str, edits: list[dict[str,str]]) -> str:
    spans = sorted(((source.index(e["old"]), source.index(e["old"])+len(e["old"]), e["new"]) for e in edits), reverse=True)
    for start,end,new in spans: source = source[:start] + new + source[end:]
    return source
