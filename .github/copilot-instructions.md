# GitHub Copilot instructions for financial-scraper

> **Single source of truth**: [`AGENTS.md`](../AGENTS.md). This file is a
> pointer for GitHub Copilot. It does not duplicate rules.

## What Copilot should do

1. Treat [`AGENTS.md`](../AGENTS.md) as the authoritative guide for this
   repository.
2. Follow its "Hard rules", "What NOT to do", and "After making changes"
   sections as normative.
3. For Python style questions, defer to the "Style" and "Python style
   (canonical)" sections in `AGENTS.md`.

## Project identity (one-liner)

Python library that scrapes Brazilian-market financial sites into CSVs.
Python 3.10+, Poetry, pytest. Six `*Provider` classes under
`financial_scraper/providers/`.

Do not add Copilot-only rules here that contradict `AGENTS.md`. Add
Copilot-only affordances here only when they cannot live in `AGENTS.md`.