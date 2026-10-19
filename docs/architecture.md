# Architecture

A single-page map of how `financial-scraper` fits together. Read this if
you are new to the codebase, adding a new provider, or onboarding an AI
coding assistant (Claude Code, OpenCode, Cursor, Copilot, …).

## Pipeline

Every provider runs the same four-step pipeline:

```
┌──────────────────┐
│  __init__(...)   │  stores download_path, filename, options
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ _config_step     │  (Selenium only) builds Options, opens WebDriver
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ _make_request    │  fetches HTML: requests.get(...) or driver.get(...)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ _read_page_and   │  parses HTML with BeautifulSoup, extracts rows
│ _get_data        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ _transform_data  │  writes CSV to self.download_path
│ _into_csv        │
└────────┬─────────┘
         │
         ▼
        run()         public method that wires the steps together
```

The four step methods are the contract. `run(...)` is the only public
entry point users call.

## Provider template

A new provider is a file in `financial_scraper/providers/` that follows
this shape:

```python
from __future__ import annotations

from financial_scraper.config.utils import Log


class XProvider:
    """Short docstring describing what the provider scrapes."""

    _URL: str = "https://example.com/data"
    _DEFAULT_FILENAME: str = "x.csv"
    _HEADERS: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 ...",
    }

    def __init__(
        self,
        download_path: str,
        filename: str | None = None,
        # extra opts go here, all keyword-only with defaults
    ) -> None:
        self.download_path = download_path
        self.filename = filename if filename else self._DEFAULT_FILENAME

    def _config_step(self) -> None:
        """Selenium providers: build Options, open WebDriver."""
        Log.log("Start")

    def _make_request(self) -> None:
        """Fetch HTML into self.html_content / self.response / self.page."""
        Log.log("Start")

    def _read_page_and_get_data(self) -> None:
        """Parse HTML into self.rows / self.df / self.lines."""
        Log.log("Start")

    def _transform_data_into_csv(self) -> None:
        """Write self.<data> into {download_path}/{filename}."""
        Log.log("Start")

    def run(self, **kwargs: object) -> None:
        """Public entry point. Compose the four steps."""
        self._config_step()
        self._make_request()
        self._read_page_and_get_data()
        self._transform_data_into_csv()
```

For requests-based providers, drop `_config_step`. For Selenium providers
keep it and close the driver in a `finally` block inside `_make_request`.

## Provider matrix

| Provider                   | Backend       | Year filter | Sector filter |
| -------------------------- | ------------- | ----------- | ------------- |
| `FundamentusProvider`      | requests+BS4  | no          | no            |
| `TradingViewProvider`      | requests+BS4  | no          | n/a           |
| `InvestorTenProvider`      | requests+BS4  | yes (`year`)| n/a           |
| `StatusInvestProvider`     | Selenium      | no          | yes (`Sector`)|
| `FundsExplorerProvider`    | Selenium      | no          | n/a           |
| `MarketDataProvider`       | Selenium      | no          | n/a           |

## Supporting modules

- `financial_scraper/config/selenium.py` — `Selenium.get_options(...)`
  builds Chrome `Options` with download dir + headless flags. **Use it.**
- `financial_scraper/config/utils.py`
  - `Log.log(msg)` / `Log.log_error(msg, exc)` — stdout printer with a
    `[ClassName] METHOD.` prefix. The only sanctioned logger.
  - `check_if_file_was_downloaded(filename, timeout, download_path)` —
    polling helper. Matches by `endswith`, so it ignores `.crdownload`
    partials.

## Where to start reading

1. `examples/usage.py` — end-to-end usage of every provider.
2. `financial_scraper/providers/fundamentus.py` — cleanest reference
   implementation (requests, no Selenium).
3. `financial_scraper/providers/funds_explorer.py` — cleanest Selenium
   reference implementation.
4. `tests/unit/test_fundamentus.py` — canonical test pattern.
5. `AGENTS.md` — the contract every AI assistant should follow.