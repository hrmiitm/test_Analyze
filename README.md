# Analysis repo

This repository contains:

- execute.py — analysis script (reads data.csv and writes a JSON summary to stdout).
- data.csv — dataset converted from the provided Excel attachment.
- .github/workflows/ci.yml — GitHub Actions workflow that:
  - runs ruff (outputs lint results to the CI log),
  - runs `python execute.py > result.json`, and
  - publishes `result.json` to GitHub Pages using the Pages artifact flow.

Notes:
- Do NOT commit result.json; it is generated in CI and deployed to Pages.
- The CI workflow is configured to run on push and will publish result.json to Pages, making it available at the Pages site root.
