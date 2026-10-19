# CLAUDE.md — Claude Code project context for financial-scraper

> **Single source of truth**: [`AGENTS.md`](AGENTS.md). This file is a
> pointer for Claude Code. It does not duplicate rules.

## What Claude Code should do on session start

1. Read [`AGENTS.md`](AGENTS.md) in full before touching any code.
2. Treat its "Hard rules", "What NOT to do", and "After making changes"
   sections as normative.
3. Use the `.claude/agents/python-expert.md` sub-agent for Python-style
   review questions (it also points back at `AGENTS.md`).

## Project identity (one-liner)

Python library that scrapes Brazilian-market financial sites into CSVs.
Python 3.10+, Poetry, pytest. Six `*Provider` classes under
`financial_scraper/providers/`.

## Tool affordances

None configured today. Add Claude-Code-specific things here only when
they apply to Claude Code and only — e.g., permission rules under
`settings.json`, hooks, slash commands. Do not move repo-wide rules
here; those belong in `AGENTS.md`.