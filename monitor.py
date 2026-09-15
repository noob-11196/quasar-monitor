name: Hot Deal Crawler

on:
  schedule:
    - cron: '*/20 * * * *'
  workflow_dispatch:

jobs:
  run-crawler:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          playwright install chromium --with-deps

      - name: Run script
        env:
          DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
        run: python monitor.py
