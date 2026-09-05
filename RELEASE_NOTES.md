# Anomstack 0.0.20

Maintenance release to refresh dependencies and restore a repeatable local development workflow.

## Changes

- Add `make setup-local`, `make stack`, and `make test-local` for Python 3.12 development.
- Start an isolated dashboard and Dagster instance with 72 hours of synthetic DuckDB data. Production maintenance jobs are excluded, dotenv loading is disabled, and example schedules start stopped.
- Resolve and lock compatible runtime and development dependencies across platforms in `constraints.txt`; use the same constraints in local setup, CI, and Docker builds.
- Update Dagster to 1.13.21, PyOD to 3.6.5, scikit-learn to 1.9.0, NumPy to 2.5.2, FastHTML to 0.14.13, MonsterUI to 1.0.47, and Plotly to 7.0.0. Replace PyOD's moving Git reference with its stable package and remove the obsolete `dagit` dependency.
- Match the browser's Plotly JavaScript version to the installed Python package and fix negative pagination labels for small metric batches.
- Update Docusaurus to 3.10.2 and React to 19.2.8, standardize docs on npm, and refresh transitive dependencies. Use Node.js 24 LTS for docs.
- Update GitHub Actions and pre-commit hooks, apply repository formatting, fix recursive pytest collection, and make LLM tests independent of local provider settings.
- Unify package and dashboard version reporting, repair source-distribution packaging, and correct the Docker build target.

## Upgrade

Run `make setup-local`, then `make stack`. See [Local development](LOCAL_DEVELOPMENT.md).
Existing trained model artifacts should be retrained with the upgraded NumPy/scikit-learn/PyOD stack before scoring production metrics.

## Validation

- Python CI-mode suite: 209 passed, 13 skipped (live external API tests and an existing skip).
- Full repository pre-commit checks passed.
- Real local ingest, PCA/KNN training for five metrics, and scoring completed successfully.
- Dashboard health, metric charts, and Dagster code-location loading verified locally.
- Python source archive and wheel built successfully.
- Docs production build passed; npm audit is down to 18 high findings, all originating from the unpatched `image-size` dependency.
- Linux ARM dashboard Docker image built successfully.

## Known limitations

- CoinDesk's live example endpoint returned HTTP 401 without API credentials. The CI-mode test suite skips live external API checks; those integrations have not all been verified against live services.
- npm reports upstream `image-size` parser denial-of-service advisories, with no patched release available at the time of this update. This dependency belongs to the docs image-processing/build toolchain. Only build trusted documentation assets. See [GHSA-w3rx-r6r6-pgpr](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr) and [GHSA-5p2g-fcmc-qvqq](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq).
