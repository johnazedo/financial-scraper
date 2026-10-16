"""
Unit tests for ``financial_scraper.config``.

Covers:

- ``Selenium.get_options`` — pure builder of ``selenium.webdriver.chrome.options.Options``.
  We assert on the produced Options object, *not* on a real Chrome driver.
- ``check_if_file_was_downloaded`` — polling helper used by the Selenium providers.
- ``Log`` — minimal coverage of ``log`` / ``log_error`` via ``capsys``.
"""

from __future__ import annotations

import pytest
from selenium.webdriver.chrome.options import Options

from financial_scraper.config.selenium import Selenium
from financial_scraper.config.utils import Log, check_if_file_was_downloaded


# ---------------------------------------------------------------------------
# Selenium.get_options
# ---------------------------------------------------------------------------


class TestSeleniumGetOptions:
    """Pure tests on the Options builder — no Chrome process is started."""

    def test_returns_selenium_options_instance(self, download_path: str) -> None:
        options = Selenium.get_options(download_path=download_path)
        assert isinstance(options, Options)

    def test_uses_headless_by_default(self, download_path: str) -> None:
        options = Selenium.get_options(download_path=download_path)
        assert any("--headless" in arg for arg in options.arguments)

    def test_omits_headless_when_show_browser_true(self, download_path: str) -> None:
        options = Selenium.get_options(
            download_path=download_path, show_browser=True
        )
        assert not any("--headless" in arg for arg in options.arguments)
        # Sanity: other stability flags should still be set
        assert any(arg == "--no-sandbox" for arg in options.arguments)

    def test_sets_download_directory_preference(self, download_path: str) -> None:
        options = Selenium.get_options(download_path=download_path)
        prefs = options.experimental_options["prefs"]
        assert prefs["download.default_directory"] == download_path

    def test_disables_pdf_viewer_and_popups(self, download_path: str) -> None:
        options = Selenium.get_options(download_path=download_path)
        prefs = options.experimental_options["prefs"]
        assert prefs["download.prompt_for_download"] is False
        assert prefs["profile.default_content_settings.popups"] == 0

    def test_sets_user_agent(self, download_path: str) -> None:
        options = Selenium.get_options(download_path=download_path)
        assert any(arg.startswith("user-agent=") for arg in options.arguments)


# ---------------------------------------------------------------------------
# check_if_file_was_downloaded
# ---------------------------------------------------------------------------


class TestCheckIfFileWasDownloaded:
    """Tiny polling helper used by every Selenium-based provider."""

    def test_returns_true_when_file_present(self, tmp_path) -> None:
        (tmp_path / "report.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        assert check_if_file_was_downloaded(
            filename="report.csv", timeout=2, download_path=str(tmp_path)
        )

    def test_returns_false_when_file_missing(self, tmp_path) -> None:
        # timeout=1 keeps the test fast; one iteration, one sleep
        assert not check_if_file_was_downloaded(
            filename="nope.csv", timeout=1, download_path=str(tmp_path)
        )

    def test_match_is_via_endswith(self, tmp_path) -> None:
        # The implementation uses str.endswith(filename); a prefixed file still matches.
        (tmp_path / "x-statusinvest.csv").write_text("h", encoding="utf-8")
        assert check_if_file_was_downloaded(
            filename="statusinvest.csv",
            timeout=1,
            download_path=str(tmp_path),
        )

    def test_partial_files_are_ignored(self, tmp_path) -> None:
        # Files that don't end with the target filename must not match.
        (tmp_path / "statusinvest-busca-avancada.csv.crdownload").write_text(
            "h", encoding="utf-8"
        )
        assert not check_if_file_was_downloaded(
            filename="busca-avancada.csv",
            timeout=1,
            download_path=str(tmp_path),
        )


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------


class TestLog:
    """``Log`` is a thin printer. We assert on the captured stream, not its prefix."""

    def test_log_writes_msg_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        Log.log("hello world")
        captured = capsys.readouterr()
        assert captured.out.endswith(": hello world\n")

    def test_log_error_writes_msg_and_root_cause_to_stdout(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        try:
            raise ValueError("boom")
        except ValueError as exc:
            Log.log_error("operation failed", exc)

        captured = capsys.readouterr()
        assert ": operation failed\n" in captured.out
        assert "Root cause: boom" in captured.out
