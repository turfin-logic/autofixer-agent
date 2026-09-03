# AutoFixer review agent

AutoFixer turns a bounded error-log excerpt into a draft code proposal for
human review. It is a review aid, not an autonomous production deployment
system.

## Setup

Use Python 3.11 or newer, then run `python -m pip install -r requirements.txt`.
Set `GEMINI_API_KEY` and an explicit approved `GEMINI_MODEL` in a local `.env`.
Set `GITHUB_TOKEN` and `GITHUB_REPO` only when you intend to create a draft PR.
Those values are never printed and `.env` is ignored.

## Workflow

`python main.py --log error.log` performs analysis only. Add `--publish` to
create a draft PR after the model returns one to five exact `old`/`new` edits.
The publisher permits only relative `.py` paths, requires each old fragment to
match exactly once, parses the resulting source with `ast`, and uses GitHub’s
blob SHA when updating the branch. It does not execute generated code, merge
PRs, or clear the input log.

The optional `watcher.py` handles truncation and retries a failed callback, but
it does not implement production backoff, sandboxing or test execution. Run
the target project’s tests and review every draft manually.

## Checks

`python -m pytest -q`, `ruff check .`, `python -m compileall -q .`, and
`python -m pip_audit -r requirements.txt` are the intended local checks.
Generated proposals are unverified until the target project’s test suite is
run by a reviewer.
