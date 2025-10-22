# Analyze — static site + CI

This repository contains a small static site and a Python script used in CI to generate a JSON file (result.json) from a CSV dataset.

Purpose
- Fix and commit execute.py so it runs on Python 3.11 with pandas 2.3.
- Convert the provided data.xlsx into data.csv and commit it.
- Add a GitHub Actions workflow that runs ruff, executes execute.py to generate result.json, and publishes result.json via GitHub Pages.

Files added
- index.html — static viewer that fetches result.json from the Pages site.
- execute.py — robust script that reads data.csv and writes JSON to stdout.
- data.csv — CSV converted from the provided data.xlsx (committed here).
- .github/workflows/ci.yml — CI workflow that runs ruff, runs execute.py > result.json, and publishes result.json to Pages.
- LICENSE — MIT license.
- .gitignore — ignores result.json

Notes
- result.json is intentionally NOT committed; it is generated during the GitHub Actions run and published by the Pages deployment step.
- The workflow installs ruff and pandas==2.3.0; adjust the python-version in the workflow if you need a different interpreter.

How CI publishes result.json
1. On push, the workflow installs dependencies and runs `ruff check .` (output is shown in the build log).
2. It executes `python execute.py > result.json` to create the file.
3. The workflow uploads result.json as the Pages artifact and calls the deploy action, which publishes the artifact to GitHub Pages.

Viewing results
After CI completes and Pages deploys, result.json will be available at:

https://<your-username>.github.io/<your-repo>/result.json

The index.html in this repository will also attempt to fetch `result.json` from the same location so you can preview it.

License
MIT
