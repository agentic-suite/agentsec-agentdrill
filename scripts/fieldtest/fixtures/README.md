# Field-test fixtures

Version-tagged, secret-scanned fixtures the field-test drivers read inside the
SUT container at `/ft/fixtures/`.

Layout mirrors `scripts/fieldtest/cases/`: one directory per fixture kind, each
with a `manifest.json` and its data files. Fixtures are **read-only** at runtime
(bind-mounted `:ro`).

Nothing here yet — drivers that need a fixture declare its `kind` explicitly, and
a missing fixture is a hard failure (never a silent pass). Add fixtures here as
the cases that need them land.
