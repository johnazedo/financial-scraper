# Changelog

All notable changes to the Financial Scraper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation site with MkDocs
- `AGENTS.md` as the single source of truth for AI coding assistants
  (Claude Code, OpenCode, Aider, Continue, Cursor, Copilot, etc.).
- `CLAUDE.md`, `.cursorrules`, and `.github/copilot-instructions.md` as
  thin harness-specific pointers to `AGENTS.md` — no duplicated rules.
- `agents/python-expert.md` — generic Python review agent role
  description, harness-neutral.
- `.claude/agents/python-expert.md` — Claude Code wrapper that points at
  `agents/python-expert.md` (frontmatter only).
- `docs/architecture.md` — single-page map of the provider pipeline and
  template, linked from the MkDocs navigation.
- `tests/conftest.py` and `examples/usage.py` now include a short banner
  pointing AI assistants at `AGENTS.md`.

### Changed
- Python style, Selenium-specific guidance, and security rules moved
  into `AGENTS.md` so all tools share one source of truth.
- Python-expert agent moved from `.claude/agents/` (Claude-Code-only) to
  `agents/` (generic) so other harnesses can reuse the role.

## [1.0.0] - 2023-10-01

### Added
- Initial release of Financial Scraper
- Support for scraping from FundsExplorer
- Support for scraping from StatusInvest
- Support for scraping from TradingView
- Support for scraping from Investidor 10
- Support for scraping from Dados de Mercado
- Command-line interface for data collection tasks
- CSV export functionality