# SEO Monitor

Self-hosted SEO health monitoring tool for WordPress sites.
Periodically crawls target sites, detects SEO issues via rule-based
checks, stores historical data, and sends alerts on anomalies.

## Status

🚧 Under active development. Not production-ready.

## Features (planned)

- [ ] Sitemap-based URL discovery
- [ ] Async batch crawling with concurrency control
- [ ] SEO field extraction (title, meta, H1, canonical, schema, etc.)
- [ ] Rule-based issue detection
- [ ] Historical snapshots with change detection
- [ ] Feishu webhook notifications
- [ ] CLI for manual runs and queries

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

```bash
# Clone the repository
git clone REPO_URL_HERE
cd seo-monitor

# Install dependencies
uv sync

# Copy environment template and fill in values
cp .env.example .env

# (Edit .env with your target site and config)
```

## Usage

TBD — will be documented as CLI commands are implemented.

## Project Structure

```
seo-monitor/
├── src/seo_monitor/   # Main package
├── tests/             # Unit tests
├── docs/designs/      # Per-feature design documents
├── scripts/           # One-off utility scripts
├── data/              # SQLite database (gitignored)
├── GEMINI.md          # AI assistant project guide
└── pyproject.toml     # Project config and dependencies
```

## License

Private project. All rights reserved.