# Data Analysis - CI Generated Result

This repository demonstrates a small data analysis pipeline designed to run in GitHub Actions and publish its output as a GitHub Pages site.

Summary
- Fixed and committed execute.py (compatible with Python 3.11 and pandas 2.3+).
- Converted data.xlsx into data.csv and committed it.
- CI workflow runs ruff, executes execute.py to produce result.json, and publishes result.json to GitHub Pages.
- result.json is intentionally not committed — it is generated in CI and deployed.

Files
- execute.py: main analysis script. Reads data.xlsx and writes a JSON summary to stdout.
- data.csv: CSV version of the spreadsheet data (committed for convenience).
- .github/workflows/ci.yml: GitHub Actions workflow that lints, runs the analysis, and publishes the artifact to Pages.
- index.html: simple page that fetches and displays result.json when available.

Usage
1. Locally reproduce output:
   - Ensure you have Python 3.11+ and pandas (2.3+).
   - Install requirements: pip install pandas openpyxl
   - Run: python execute.py > result.json
   - View result.json locally or serve with a static server.

2. CI / GitHub Actions
   - Push to the `main` branch; the workflow will run, show ruff output in logs, run execute.py, and deploy result.json to GitHub Pages.

Notes
- Do not commit result.json — the CI will generate it per push and publish to Pages.

License
This project is released under the MIT License. See LICENSE.
