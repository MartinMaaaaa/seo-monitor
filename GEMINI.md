# Project: SEO Health Monitor

## Overview

A self-hosted SEO health monitoring tool for WordPress sites.
The system periodically crawls target sites, extracts SEO-related
fields, detects issues using rule-based checks, stores historical
snapshots, and sends alerts on anomalies.

**Primary target**: subli-star.com (~500 URLs)
**Secondary target** (future): support.subli-star.com

## Core Principle

This project is **deterministic and rule-based**. No AI/LLM calls
in runtime logic. Every check must be explainable and reproducible.
AI is used only during development (via this assistant), not at runtime.

## Stack

### Runtime
- **Python**: 3.13+
- **HTTP client**: `httpx` (async)
- **HTML parser**: `selectolax` (fast, Rust-based)
- **Database**: SQLite via `SQLAlchemy 2.0` (async engine)
- **CLI**: `typer`
- **Config**: `pydantic-settings` + `.env`
- **Terminal output**: `rich`
- **Retries**: `tenacity`

### Development
- **Package manager**: `uv` (do not use pip/poetry commands)
- **Linter + formatter**: `ruff`
- **Testing**: `pytest` + `pytest-asyncio`
- **Type checking**: `mypy` (strict mode)

### NOT in stack (do NOT introduce without approval)
- No AI/LLM libraries in runtime code
- No web framework until Phase 2 (dashboard)
- No Docker until deployment phase
- No Alembic until schema stabilizes
- No Redis / Celery (cron is enough)
- No ORM migrations; use raw SQLAlchemy metadata

## Project Structure

```
seo-monitor/
├── src/seo_monitor/
│   ├── __init__.py
│   ├── cli.py           # Typer CLI entry point
│   ├── config.py        # Pydantic settings from .env
│   ├── crawler.py       # Sitemap + URL fetching (async)
│   ├── parser.py        # HTML parsing, SEO field extraction
│   ├── checker.py       # Rule-based issue detection
│   ├── storage.py       # SQLAlchemy models + DB ops
│   ├── differ.py        # Snapshot comparison, change detection
│   └── alerts.py        # Notification dispatch (Feishu)
├── tests/
├── docs/designs/        # Design docs per feature (write BEFORE code)
├── scripts/             # One-off maintenance scripts
├── data/                # SQLite files (gitignored)
├── GEMINI.md            # This file
├── README.md
├── pyproject.toml
└── uv.lock
```

## Coding Conventions

### Style
- All code comments and docstrings in **English**
- User-facing CLI messages can be in English too
- Use **type hints** everywhere, including return types
- Use modern syntax: `str | None` not `Optional[str]`, `list[str]` not `List[str]`
- Line length: 100 chars (enforced by ruff)

### Patterns
- Prefer `async` for all I/O operations
- Use `pathlib.Path`, never `os.path`
- Use `httpx.AsyncClient`, never `requests`
- Use `logging` module, not `print` (except `rich.console` for CLI UX)
- Use `dataclass` or `pydantic.BaseModel` for structured data, not raw dicts

### Error handling
- Never use bare `except:` — always catch specific exceptions
- Raise domain-specific exceptions (e.g., `CrawlerError`, `ParserError`)
- Log with context: URL, stage, retry count
- Fail loud in dev; retry gracefully in prod

### Functions
- Keep functions under 50 lines
- One function, one responsibility
- Pure functions (no side effects) where possible — especially in `parser.py` and `checker.py`

## Data Model (initial)

Tables are defined in `storage.py`. Initial schema:

### `pages`
Latest known state of each URL.
- `url` (PK), `title`, `meta_description`, `h1`, `canonical`,
  `status_code`, `content_hash`, `first_seen`, `last_crawled`

### `snapshots`
Historical record, one row per crawl per URL.
- `id` (PK), `url` (FK), `crawled_at`, `status_code`, `content_hash`,
  `raw_fields_json` (all extracted fields as JSON)

### `issues`
Detected problems per snapshot.
- `id` (PK), `snapshot_id` (FK), `rule_code`, `severity`, `message`,
  `detected_at`

**Severity Levels:**
- `critical`: Complete failure (e.g., `PARSE_FAILED`, 4xx/5xx status codes).
- `warning`: Critical SEO field missing (e.g., `MISSING_TITLE`, `MISSING_H1`).
- `info`: Field exists but sub-optimal (e.g., `TITLE_TOO_LONG`, `DUPLICATE_CONTENT`).

## Workflow Expectations

### Crawler Logic
- **Sitemap**: Must support recursive parsing of `sitemap_index.xml`.
- **Recursion**: Hard limit of 3 levels deep to prevent infinite loops.
- **Formats**: Support standard `.xml` and gzipped `.xml.gz`.
- **Fault Tolerance**: Single page failures (parsing or network) must not stop the batch; log as `critical` issues and continue.

### Database Strategy
- **Initialization**: Use an explicit `seo-monitor init-db` command.
- **No Auto-create**: Runtime commands (like `crawl`) must fail loud if the database schema is not initialized.
- **Migrations**: No Alembic for now; schema changes require manual `reset-db` during MVP.

### Before writing any module:
1. Check if `docs/designs/<module>.md` exists
2. If not, **write the design doc first** (goal, I/O, signatures, constraints)
3. Get user approval on design before implementation
4. Then implement

### Per feature:
- One feature = one commit with clear message (conventional commits style)
- Message format: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`
- Example: `feat(crawler): add sitemap index recursive parsing`

### Before ending each coding session:
- Run `uv run ruff check --fix` and `uv run ruff format`
- Run `uv run pytest` (if tests exist for modified areas)
- Update `docs/designs/<module>.md` if design changed during implementation
- Commit

## Out of Scope (explicitly excluded for MVP)

- Multi-site support (build for one site, refactor when needed)
- Web dashboard (Phase 2)
- AI-powered content suggestions (explicitly excluded, forever in this codebase)
- User authentication / multi-user (single-user tool)
- Real-time monitoring (batch runs only)
- JavaScript-rendered content (server-side HTML only, no Playwright)
- robots.txt compliance (own site, not needed)

## Dependencies Policy

- **New dependencies require explicit approval from user**
- Prefer stdlib solutions where reasonable
- Justify each new dep: what problem it solves, why stdlib isn't enough
- Pin major versions in `pyproject.toml`
- Commit `uv.lock` after any dependency change

## Commands Reference

```bash
# Install/update dependencies
uv sync

# Add a new dependency (runtime)
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Run Python with project env
uv run python <args>

# Run tests
uv run pytest

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check
uv run mypy src

# Run the CLI
uv run seo-monitor <command>
```

## Anti-Patterns to Avoid

When generating code, **do not**:

- Add configuration options "just in case" — only add config for things that actually vary
- Create abstract base classes without at least 2 concrete implementations in mind
- Wrap simple operations in multiple layers (e.g., don't create `URLService` that wraps a function)
- Swallow exceptions silently
- Use global state except for singletons that are genuinely global (logger, settings)
- Import heavy optional deps eagerly (use lazy imports where it matters)
- Write "clever" code over clear code
- Generate >500 lines in a single response without checkpoint commits

## How to Ask for Help

When implementation is ambiguous, **ask the user** rather than guessing. Examples of questions to ask:
- "Should this behavior be configurable or hardcoded for now?"
- "What should happen if the sitemap is missing / malformed?"
- "Do you want to skip or retry on 5xx errors?"
- "Should the alert fire on first detection or after N consecutive failures?"

Good questions beat wrong implementations.