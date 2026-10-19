# AGENTS.md — Guide for AI coding agents

This file is read automatically by AI coding assistants (Claude Code, OpenCode,
Aider, Continue, Cursor, Copilot, etc.) when working on this repository. If
you are an AI assistant, **read this file in full before touching any code**.

Human contributors: the human-facing equivalent of this document is
[`CONTRIBUTING.md`](CONTRIBUTING.md). The guidelines below are normative for
AI-generated contributions.

## What this repo is

A Python library that scrapes Brazilian-market financial websites
(StatusInvest, Fundamentus, Investidor10, TradingView, DadosDeMercado,
FundsExplorer) and saves the results as CSV files. Each data source is a
`Provider` class under `financial_scraper/providers/`.

- **Runtime dependencies**: `beautifulsoup4`, `requests`, `selenium`, `lxml`.
  There is no `requests-html` runtime use — ignore any mention of it.
- **Dev dependencies**: `pytest`, `pytest-cov`, `pytest-mock`, `responses`,
  `freezegun`, `mkdocs`, `mkdocstrings`, `mkdocs-material`.
- **Python**: 3.10+.
- **Public API surface** (do not break without a deprecation cycle):
  - `StatusInvestProvider`, `FundamentusProvider`, `InvestorTenProvider`,
    `TradingViewProvider`, `MarketDataProvider`, `FundsExplorerProvider`.
  - Each provider exposes a `run(...)` method.
  - All providers accept `(download_path: str, filename: str | None = None, ...)`.

## Repository layout

```
financial_scraper/
  __init__.py             # re-exports all 6 providers
  config/
    selenium.py           # Selenium Options builder used by 3 providers
    utils.py              # Log helpers + check_if_file_was_downloaded
  providers/
    fundamentus.py        # requests + BeautifulSoup
    funds_explorer.py     # Selenium
    investor_ten.py       # requests + BeautifulSoup
    market_data.py        # Selenium
    status_invest.py      # Selenium
    trading_view.py       # requests + BeautifulSoup
examples/
  usage.py                # canonical end-to-end examples
tests/
  conftest.py             # `download_path`, `html`, `csv_text` fixtures
  fixtures/{html,csv}/    # captured real-site snapshots (commit them!)
  scripts/capture_fixtures.py  # one-shot helper to refresh snapshots
  unit/                   # fast, hermetic, no I/O outside tmp_path
  integration/            # reserved for network-touching tests
docs/                     # MkDocs site (Material theme + mkdocstrings)
```

## The provider contract

Every provider in `financial_scraper/providers/` follows the same template.
**Any new provider must follow it. Any edit to an existing provider must
preserve it.**

```python
class XProvider:
    # Class-level constants (URLs, default filenames, magic strings)
    _URL = "..."
    _DEFAULT_FILENAME = "..."

    def __init__(self, download_path: str, filename: str | None = None, **opts):
        self.download_path = download_path
        self.filename = filename if filename else self._DEFAULT_FILENAME
        # store other opts here

    def _config_step(self) -> None: ...        # Selenium providers only
    def _make_request(self) -> None: ...
    def _read_page_and_get_data(self) -> None: ...
    def _transform_data_into_csv(self) -> None: ...
    def run(self, **kwargs) -> None:          # public entry point
        self._config_step()      # if Selenium
        self._make_request()
        self._read_page_and_get_data()
        self._transform_data_into_csv()
```

The four step methods are the contract. They run in order, mutate `self`,
and ultimately produce a CSV in `self.download_path`.

## How to add a new provider

1. Create `financial_scraper/providers/x_provider.py` with the class above.
2. Re-export it from `financial_scraper/__init__.py` (alphabetical order).
3. Add a Poetry script in `pyproject.toml` under `[tool.poetry.scripts]`:
   `example_x_provider = "examples.usage:x_provider_example"`.
4. Add an example function in `examples/usage.py` (don't auto-run it from
   `__main__` if it hits the network — gate it behind a flag).
5. Write unit tests in `tests/unit/test_x_provider.py` using the
   `download_path`, `html`, and `csv_text` fixtures. **Never** write to the
   user's working directory.
6. If you scrape a requests-based site, add a capture function in
   `tests/scripts/capture_fixtures.py` so fixtures can be refreshed.
7. Update `README.md` and `docs/modules/financial_scraper/overview.md`.

## How to fix a broken selector (the common case)

Sites change. When a provider's `_make_request` or `_read_page_and_get_data`
stops working because of an HTML/CSS change:

1. Run the targeted test:
   `poetry run pytest tests/unit/test_<provider>.py -x`.
2. Read the failing assertion — it usually names the missing element.
3. For requests-based providers: capture a fresh HTML snapshot with
   `python tests/scripts/capture_fixtures.py` and commit it under
   `tests/fixtures/html/<provider>.html`.
4. Update the selector in the provider file.
5. If the CSV layout changed, regenerate `tests/fixtures/csv/<provider>.csv`
   the same way.
6. Re-run the full unit suite: `poetry run pytest -m "not selenium"`.

Do **not** rewrite the whole provider. Small, surgical edits keep the diff
reviewable and the public API stable.

## Testing rules

- All filesystem writes go to pytest's `tmp_path`. Use the `download_path`
  fixture, not `os.getcwd()`.
- Mock HTTP with `responses`; mock datetime with `freezegun`; mock the
  WebDriver with `pytest-mock` (see `tests/unit/test_funds_explorer.py` for
  the WebDriver mocking recipe).
- Use the markers defined in `pyproject.toml`: `unit`, `integration`,
  `selenium`, `slow`. Default is unit; only mark selenium tests if they
  actually need a browser.
- New providers MUST have at least one happy-path test and one
  table-missing / network-failure test.

## Style

- PEP 8, 120-column line length (see `setup.cfg`).
- Type hints on all public method signatures. Prefer modern union syntax
  (`str | None`) over `Optional[str]`. `from __future__ import annotations`
  is fine and welcome.
- Docstrings on public classes and methods. Match the existing style —
  short summary, then `Args:` / `Returns:` / `Example:` sections.
- One provider class per file.
- No `requests-html` imports (the dep is unused; remove it if you see it).
- No new top-level configuration objects. Configuration is passed to the
  constructor explicitly.

## Logging

The package ships a tiny `Log` helper in `financial_scraper/config/utils.py`
that prints to stdout with a `[ClassName] METHOD.` prefix. Do **not** add
the stdlib `logging` module to the providers — it will break the prefix
format and conflict with users' own logging configuration. If you need
quieter output, the right path is to enhance `Log`, not to introduce a
second logger.

## Python style (canonical)

> The harness-specific `.claude/agents/python-expert.md` file points here
> for its style rules; do not duplicate them in tool-specific files.

- **Type hints** on every public method signature. Use modern syntax
  (`str | None`, `list[str]`, `dict[str, int]`) — not `Optional`, `List`,
  or `Dict` from `typing`. `from __future__ import annotations` is welcome.
- **Constructor signature** for any provider:
  `(download_path: str, filename: str | None = None, **opts) -> None`.
- **Step methods** all declare `-> None`.
- **Naming**: classes `PascalCase` (providers end in `Provider`); methods
  and functions `snake_case`; constants `UPPER_SNAKE` and underscore-
  prefixed when class-level (`_URL`, `_DEFAULT_FILENAME`); booleans use
  `is_` / `has_` / `show_` / `wait_` prefixes when helpful.
- **One provider class per file** in `financial_scraper/providers/`.
- **Imports**: stdlib, third-party, local — separated by blank lines.
  Absolute imports inside the package.
- **Avoid** mutable default arguments, bare `except:`, `eval`/`exec`,
  `from module import *`, shadowing builtins, magic numbers without a
  named constant, globals / module-level mutable state.
- **Prefer** comprehensions, `isinstance`, f-strings, `pathlib.Path` in
  new code, `enumerate`, `zip`, guard clauses, context managers.
- **Functions** ≤ ~30 lines of logic, ≤ 5 parameters, ≤ 3 levels of
  nesting. If you go deeper, extract helpers.
- **Error handling**: catch specific exceptions in the narrowest scope
  that makes sense. Top-level `run()` methods log + swallow so a single
  bad record doesn't kill the whole loop (see `InvestorTenProvider.run`).
- **No** `requests-html` imports — the dep is unused, ignore it.
- **No** new top-level configuration objects. Configuration belongs in
  constructors.
- **Test style**: Given-When-Then comments; `self.assert*` only inside
  `unittest.TestCase`, plain pytest functions elsewhere; use the shared
  fixtures (`download_path`, `html`, `csv_text`); mock HTTP with
  `responses`, datetime with `freezegun`, WebDriver with `pytest-mock`.

## Selenium-specific guidance

Selenium providers are the most fragile part of this codebase. When
working on them:

- The driver lifecycle is open in `_config_step` and closed in a
  `finally` block inside `_make_request`. **Keep this invariant.**
- `check_if_file_was_downloaded` in `financial_scraper/config/utils.py`
  matches by `endswith` on purpose: it ignores `.crdownload` partials
  written during the transfer. **Do not** change it to exact match —
  downloads will appear flaky.
- `Selenium.get_options(download_path, show_browser)` is the only way
  to construct `Options`. Don't re-derive the prefs dict in a provider.
- Time-based waits (`time.sleep(self.wait_time)`) are acceptable —
  the docs explicitly expose `wait_time`. Don't replace them with
  implicit waits without a real reason.

## Security

- No `eval()` / `exec()` on scraped content.
- No `pickle` / `marshal` on untrusted input.
- File writes go to `self.download_path`, never to a path constructed
  from scraped content.
- Don't shell out (`os.system`, `subprocess`) to scraped input.
- No hardcoded credentials, API keys, or tokens. The library
  authenticates nowhere.

## What NOT to do

- Do **not** add runtime AI/LLM dependencies to this package. The repo is
  intentionally scraping-only.
- Do **not** change the public class names or constructor signatures
  without a deprecation cycle and a CHANGELOG entry.
- Do **not** introduce a global config object. Configuration belongs in
  constructors.
- Do **not** write to disk outside `download_path`.
- Do **not** commit `__pycache__/`, `.coverage`, downloaded CSVs, or
  `.crdownload` partials. See `.gitignore`.
- Do **not** add a `services/` directory — `pyproject.toml` claims to
  package one but it doesn't exist. If you need shared logic, put it under
  `financial_scraper/`.

## After making changes

Run, in order:

```bash
poetry run pytest -m "not selenium"        # fast feedback
poetry run pytest                          # full suite (optional)
poetry run ruff check financial_scraper    # if ruff is available
```

If any of those fail, fix the failures before declaring the task done.

## See also

- `CONTRIBUTING.md` — human-facing contribution guide.
- `CLAUDE.md` — Claude Code project context (points here).
- `.cursorrules` — Cursor project rules (points here).
- `.github/copilot-instructions.md` — GitHub Copilot instructions (points here).
- `agents/python-expert.md` — generic Python review agent (points here for
  style rules). Harness-specific manifests (e.g.,
  `.claude/agents/python-expert.md`) wrap this file.
- `docs/architecture.md` — provider template and pipeline diagram.
- `examples/usage.py` — end-to-end usage of every provider.

**Single source of truth**: this file. All other AI-instruction files in
the repo are thin pointers to it. If you find duplicated rules elsewhere,
fix them — they will drift.

**Generic agents directory**: `agents/`. Agent role descriptions that any
harness can consume live there. Harness-specific manifests in
`.claude/`, `.github/`, etc. are thin wrappers that add only the
frontmatter each tool requires.