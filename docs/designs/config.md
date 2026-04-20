# Design: Config Module

## Goal
Provide a centralized, type-safe configuration management system that loads settings from environment variables and `.env` files.

## Requirements
- Use `pydantic-settings` for validation and loading.
- Support all variables defined in `.env.example`.
- Provide sensible defaults for optional settings.
- Ensure `DATABASE_PATH` is automatically converted to an absolute path or a valid SQLAlchemy connection string.

## I/O
- **Input**: Environment variables, `.env` file.
- **Output**: A singleton `settings` object accessible by other modules.

## Schema

### Settings Class
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `target_site_url` | `AnyHttpUrl` | `required` | Base URL of the site to monitor. |
| `sitemap_path` | `str` | `/sitemap.xml` | Path to the sitemap. |
| `crawler_concurrency` | `int (Field ge=1, le=20)` | `5` | Max concurrent requests. |
| `crawler_timeout` | `int (Field ge=1, le=60)` | `10` | Timeout in seconds. |
| `crawler_user_agent` | `str` | `SEO-Monitor/0.1` | User-Agent string. |
| `database_path` | `Path` | `data/seo_monitor.db` | Path to SQLite file. |
| `feishu_webhook_url` | `SecretStr | None` | `None` | Optional Feishu webhook. |
| `log_level` | `Literal["DEBUG", "INFO", "WARNING", "ERROR"]` | `INFO` | Logging level. |

## Validation Rules

### Required fields (fail loud if missing)
- `target_site_url`: Must be provided via env or .env. If missing, application
  exits with a clear error message at startup, not at runtime.

### Numeric ranges (validated by pydantic at load time)
- `crawler_concurrency`: 1-20 (via `Field(ge=1, le=20)`)
- `crawler_timeout`: 1-60 seconds (via `Field(ge=1, le=60)`)

### Enumerated values
- `log_level`: Must be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`
  (enforced via `Literal` type, invalid values fail at load time)

### .env file behavior
- Missing `.env` file is NOT an error (system env vars may provide config)
- Missing required fields IS an error (pydantic raises ValidationError at startup)

### Computed Properties
- `database_url`: Returns the SQLAlchemy async connection string (e.g., `sqlite+aiosqlite:///./data/seo_monitor.db`).

## Implementation Details
- Use `SettingsConfigDict` to specify `.env` file loading.
- Use `pydantic.SecretStr` for `FEISHU_WEBHOOK_URL` to prevent accidental logging.
- Directory creation: On settings initialization, if the parent directory of
  `database_path` does not exist, create it via
  `Path(database_path).parent.mkdir(parents=True, exist_ok=True)`.
  This is the ONLY place in the codebase where automatic directory creation
  is allowed. All other modules must fail loud on missing directories.
- Required field handling: Use `Field(...)` (ellipsis) for truly required
  fields without defaults. Pydantic will raise ValidationError at import time
  if they are missing from both env and .env.

## Usage Example
```python
from seo_monitor.config import settings

print(settings.target_site_url)
print(settings.database_url)
```
