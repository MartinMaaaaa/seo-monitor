"""
Tests for the configuration module.
"""

import pytest
from pydantic import ValidationError

from seo_monitor.config import Settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    """
    Ensure each test runs in an isolated environment without .env file.
    """
    # Switch to an empty temporary directory to avoid picking up any local .env
    monkeypatch.chdir(tmp_path)

    # Clear all related env vars to start from a clean state
    related_vars = [
        "TARGET_SITE_URL",
        "SITEMAP_PATH",
        "CRAWLER_CONCURRENCY",
        "CRAWLER_TIMEOUT",
        "CRAWLER_USER_AGENT",
        "DATABASE_PATH",
        "FEISHU_WEBHOOK_URL",
        "LOG_LEVEL",
    ]
    for key in related_vars:
        monkeypatch.delenv(key, raising=False)


def test_valid_settings_load(monkeypatch):
    """
    Test that Settings loads correctly when all required fields are provided.
    """
    monkeypatch.setenv("TARGET_SITE_URL", "https://example.com")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("CRAWLER_CONCURRENCY", "10")

    config = Settings()
    assert str(config.target_site_url).startswith("https://example.com")
    assert config.log_level == "DEBUG"
    assert config.crawler_concurrency == 10
    assert config.sitemap_path == "/sitemap.xml"  # Default value


def test_missing_required_field_raises():
    """
    Test that missing TARGET_SITE_URL raises a ValidationError.
    """
    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "target_site_url" in str(excinfo.value)


def test_invalid_log_level_raises(monkeypatch):
    """
    Test that an invalid LOG_LEVEL raises a ValidationError.
    """
    monkeypatch.setenv("TARGET_SITE_URL", "https://example.com")
    monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")

    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "log_level" in str(excinfo.value)


def test_concurrency_out_of_range(monkeypatch):
    """
    Test that CRAWLER_CONCURRENCY out of [1, 20] range raises a ValidationError.
    """
    monkeypatch.setenv("TARGET_SITE_URL", "https://example.com")
    monkeypatch.setenv("CRAWLER_CONCURRENCY", "50")

    with pytest.raises(ValidationError) as excinfo:
        Settings()
    assert "crawler_concurrency" in str(excinfo.value)


def test_database_url_computed(monkeypatch, tmp_path):
    """
    Test that database_url is correctly computed and starts with the protocol.
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("TARGET_SITE_URL", "https://example.com")
    monkeypatch.setenv("DATABASE_PATH", str(db_file))

    config = Settings()
    # Check for the async sqlite protocol
    assert config.database_url.startswith("sqlite+aiosqlite:///")
    # Robust check for path inclusion without worrying about OS-specific separators
    assert "test.db" in config.database_url
