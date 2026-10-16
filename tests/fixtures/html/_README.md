# Test fixtures

This directory stores:

- `html/<provider>_<context>.html` — raw HTML snapshots captured from the
  source websites. Use them as canned input to assert parser behavior without
  hitting the network.
- `csv/<provider>_<context>.csv` — expected outputs produced by the providers
  on the captured HTML. Use them as expected-output references for parser
  tests.

These files are committed alongside the code so the suite is reproducible
offline.

## Refreshing

Run the script below *manually* after a site redesign to refresh the
fixtures. Do not run it as part of the test suite.

```
poetry run python tests/scripts/capture_fixtures.py
```

The capture script walks the live sites, so it requires network access and,
for the Selenium-based providers, a working Chrome install.
