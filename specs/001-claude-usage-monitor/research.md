# Research: Claude Usage Monitor

**Date**: 2025-10-19
**Feature**: Claude Usage Monitor
**Phase**: 0 - Technical Research & Decision Making

## Overview

This document consolidates research findings for building a CLI tool to monitor Claude usage. Key decisions focus on leveraging **claude-agent-sdk-python** and **Playwright MCP Chrome Extension** to simplify implementation while meeting all constitution requirements.

---

## Decision 1: Agent Framework - claude-agent-sdk-python

**Decision**: Use [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) as the foundation

**Rationale**:
- Official Anthropic SDK for building Python agents
- Provides built-in MCP (Model Context Protocol) server support
- Integrates seamlessly with Playwright MCP extension
- Simplifies agent orchestration and state management
- Active maintenance by Anthropic team

**Alternatives Considered**:
1. **Plain Python with requests** - Rejected because:
   - Requires manual MCP implementation
   - No agent orchestration patterns
   - More boilerplate code
2. **LangChain** - Rejected because:
   - Heavier dependency (overkill for this use case)
   - Adds unnecessary abstraction layers
   - Constitution principle: Simplicity First

**Implementation Notes**:
- SDK handles MCP server lifecycle
- Provides async/await patterns for browser automation
- Built-in error handling and retry logic

**References**:
- GitHub: https://github.com/anthropics/claude-agent-sdk-python
- Documentation: https://github.com/anthropics/claude-agent-sdk-python/blob/main/README.md

---

## Decision 2: Browser Automation - Playwright MCP Chrome Extension

**Decision**: Use [Playwright MCP Chrome Extension](https://github.com/microsoft/playwright-mcp/blob/main/extension/README.md) for browser session reuse

**Rationale**:
- **Session reuse**: Leverages existing Chrome browser session (cookies, auth state)
- **No auth complexity**: Users must already be logged into Claude web - tool simply connects to existing session
- **MCP native**: Designed to work with claude-agent-sdk-python MCP server
- **Cross-platform**: Works on Linux, macOS, Windows (wherever Chrome runs)
- **Maintained by Microsoft**: Active development and support

**Alternatives Considered**:
1. **Manual cookie extraction** - Rejected because:
   - Requires parsing browser profile files (platform-specific, fragile)
   - Cookie encryption varies by platform
   - Security concerns (direct cookie access)
2. **Selenium** - Rejected because:
   - Heavier than Playwright
   - No MCP integration
   - Less modern API
3. **Headless browser with manual login** - Rejected because:
   - Complex auth flow (email, 2FA, etc.)
   - User would need to store credentials
   - Violates Constitution: Simplicity First

**Implementation Notes**:
- Extension must be installed in Chrome
- Tool connects via MCP protocol to extension
- Extension provides browser context with existing session
- If user not logged in, tool prompts to log in manually in browser

**References**:
- GitHub: https://github.com/microsoft/playwright-mcp
- Extension README: https://github.com/microsoft/playwright-mcp/blob/main/extension/README.md

---

## Decision 3: CLI Framework - Click

**Decision**: Use **Click** for CLI command structure

**Rationale**:
- Industry standard for Python CLIs
- Auto-generates `--help` documentation (Constitution requirement)
- Supports nested command groups (e.g., `claude-pulse usage show`, `claude-pulse auth status`)
- Type validation and error messages built-in
- Excellent documentation and community support

**Alternatives Considered**:
1. **argparse** (stdlib) - Rejected because:
   - More verbose
   - Manual help text formatting
   - Less elegant command grouping
2. **Typer** - Rejected because:
   - Newer, less battle-tested
   - Similar to Click but less ecosystem support
3. **Fire** - Rejected because:
   - Too magical (violates explicit > implicit)
   - Less control over help formatting

**Implementation Notes**:
- Main CLI group: `claude-pulse`
- Command groups: `usage`, `auth`, `history`, `config`
- Rich integration for colored help text

**References**:
- Documentation: https://click.palletsprojects.com/

---

## Decision 4: Terminal UI - Rich

**Decision**: Use **Rich** library for terminal formatting

**Rationale**:
- Beautiful tables, progress bars, colored output (Constitution: Visual Excellence)
- Built-in `--no-color` support via `Console(force_terminal=False)`
- Unicode box-drawing characters for tables
- Handles terminal width adaptation automatically
- Progress indicators for long operations
- Supports emojis and symbols (✓, ✗, ⚠, →)

**Alternatives Considered**:
1. **Colorama + tabulate** - Rejected because:
   - Requires multiple libraries
   - Manual color management
   - Less sophisticated formatting
2. **Textual** - Rejected because:
   - Too heavy (full TUI framework)
   - Overkill for simple table display
3. **ANSI codes directly** - Rejected because:
   - Manual cross-platform handling
   - No --no-color abstraction

**Implementation Notes**:
- Use `Console()` for all output
- `Table()` for usage data display
- `Progress()` for data fetching indicator
- `Panel()` for warnings/alerts

**References**:
- Documentation: https://rich.readthedocs.io/

---

## Decision 5: Data Models - Pydantic

**Decision**: Use **Pydantic v2** for data validation and configuration

**Rationale**:
- Type-safe data models with runtime validation (Constitution: Robustness)
- Automatic JSON serialization/deserialization
- Built-in validation error messages
- Settings management for config files
- Excellent IDE support (type hints)

**Alternatives Considered**:
1. **dataclasses** (stdlib) - Rejected because:
   - No built-in validation
   - Manual JSON handling
   - No config file integration
2. **attrs** - Rejected because:
   - Less ecosystem integration
   - Pydantic is standard in Python ecosystem

**Implementation Notes**:
- Models: `UsageData`, `UsageSnapshot`, `AlertConfiguration`, `AppConfig`
- Use `BaseSettings` for configuration file management
- Validation for user inputs (thresholds, dates, etc.)

**References**:
- Documentation: https://docs.pydantic.dev/latest/

---

## Decision 6: Storage - SQLite + JSON

**Decision**: Use **SQLite** for historical snapshots, **JSON** for config

**Rationale**:
- SQLite: Built into Python, no external dependencies
- Efficient queries for historical data (date ranges, aggregations)
- JSON: Human-readable config files (easy debugging)
- Both are cross-platform and file-based (no server required)

**Alternatives Considered**:
1. **Pure JSON for everything** - Rejected because:
   - Inefficient for time-series queries
   - No indexing for date ranges
2. **PostgreSQL/MySQL** - Rejected because:
   - External server requirement
   - Overkill for single-user tool
   - Violates Constitution: Simplicity First
3. **CSV files** - Rejected because:
   - No structured querying
   - Manual parsing required

**Implementation Notes**:
- SQLite database: `~/.local/share/claude-pulse/usage.db`
- Config file: `~/.config/claude-pulse/config.toml`
- Use `platformdirs` library for cross-platform path resolution

**Schema**:
```sql
CREATE TABLE usage_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_messages INTEGER,
    input_quota INTEGER,
    output_quota INTEGER,
    source TEXT DEFAULT 'manual'
);
```

**References**:
- Python sqlite3: https://docs.python.org/3/library/sqlite3.html
- platformdirs: https://github.com/platformdirs/platformdirs

---

## Decision 7: Configuration Management - TOML

**Decision**: Use **TOML** format for configuration files

**Rationale**:
- Human-readable, less verbose than JSON
- Standard in Python ecosystem (pyproject.toml)
- Supports comments for user guidance
- Built-in Python support via `tomllib` (3.11+)

**Alternatives Considered**:
1. **JSON** - Rejected because:
   - No comments
   - More verbose
2. **YAML** - Rejected because:
   - Requires external dependency (PyYAML)
   - More complex parsing
3. **INI** - Rejected because:
   - Limited nested structure support

**Implementation Notes**:
- Use `tomllib` for reading (stdlib 3.11+)
- Use `tomli-w` for writing (lightweight library)
- Pydantic BaseSettings with TOML backend

**Example Config**:
```toml
[general]
default_output_format = "table"  # Options: table, json
color_enabled = true

[alerts]
enabled = false
warning_threshold = 80  # Percentage
critical_threshold = 95

[history]
retention_days = 30
auto_snapshot = false
```

---

## Decision 8: Testing Strategy

**Decision**: Pytest with contract, integration, and unit test layers

**Rationale**:
- **Contract tests**: Validate Claude API response structure (resilient to API changes)
- **Integration tests**: Test MCP connection and browser automation flow
- **Unit tests**: Test models, formatters, utilities in isolation
- **Platform tests**: GitHub Actions matrix for Linux/macOS/Windows

**Alternatives Considered**:
1. **unittest** (stdlib) - Rejected because:
   - More verbose
   - pytest has better fixtures and plugins
2. **Manual testing only** - Rejected because:
   - Constitution requires comprehensive tests
   - No regression protection

**Implementation Notes**:
- Use `pytest-asyncio` for async test support
- Use `pytest-mock` for MCP connection mocking
- Contract tests use JSON schema validation
- Integration tests require real browser session (optional, manual trigger)

**References**:
- pytest: https://pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/

---

## Decision 9: Claude API Endpoint Discovery

**Decision**: Use browser DevTools to inspect API endpoint at https://claude.ai/settings/usage

**Rationale**:
- Official Claude API is not public/documented for usage data
- Web interface makes async request to internal API
- Endpoint likely: `/api/organizations/{org_id}/usage` or similar
- Response format needs to be reverse-engineered

**Alternatives Considered**:
1. **Official API** - Rejected because:
   - No public API for usage data (as of 2025-10-19)
2. **Screen scraping HTML** - Rejected because:
   - Data loads via JS/async (not in initial HTML)
   - Fragile (HTML structure changes frequently)

**Implementation Notes**:
- During implementation, use DevTools Network tab to:
  1. Navigate to https://claude.ai/settings/usage
  2. Filter for XHR/Fetch requests
  3. Identify usage data endpoint
  4. Document request headers (cookies, auth tokens)
  5. Document response JSON structure
- Create contract test with captured response structure
- Handle API version changes gracefully (fail with clear error message)

**Contingency Plan**:
- If API endpoint changes, contract test will fail
- Tool should display actionable error: "Claude API structure changed. Please report issue at <github_url>"

---

## Decision 10: Cross-Platform Path Handling

**Decision**: Use **pathlib** (stdlib) + **platformdirs** library

**Rationale**:
- pathlib: Modern, cross-platform path handling (Constitution requirement)
- platformdirs: Standard config/data directories per OS
- Avoids manual `os.path` string concatenation

**Platform-Specific Paths**:
- **Linux**:
  - Config: `~/.config/claude-pulse/`
  - Data: `~/.local/share/claude-pulse/`
  - Logs: `~/.local/state/claude-pulse/`
- **macOS**:
  - Config: `~/Library/Application Support/claude-pulse/`
  - Data: `~/Library/Application Support/claude-pulse/`
  - Logs: `~/Library/Logs/claude-pulse/`
- **Windows**:
  - Config: `%APPDATA%\claude-pulse\`
  - Data: `%LOCALAPPDATA%\claude-pulse\`
  - Logs: `%LOCALAPPDATA%\claude-pulse\logs\`

**Implementation Notes**:
```python
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir, user_log_dir

config_dir = Path(user_config_dir("claude-pulse"))
data_dir = Path(user_data_dir("claude-pulse"))
log_dir = Path(user_log_dir("claude-pulse"))
```

**References**:
- platformdirs: https://platformdirs.readthedocs.io/

---

## Decision 11: Error Handling & Logging

**Decision**: Use **structlog** for structured logging + actionable error messages

**Rationale**:
- structlog: JSON-structured logs for debugging (Constitution: Robustness)
- Separate log file for troubleshooting
- User-facing errors use Rich for formatting
- All errors include actionable guidance

**Alternatives Considered**:
1. **Standard logging** (stdlib) - Rejected because:
   - Less structured output
   - Manual formatting required
2. **Print statements** - Rejected because:
   - No log levels
   - No file output

**Implementation Notes**:
- Log file: `~/.local/state/claude-pulse/app.log` (or platform equivalent)
- Rotation: Keep last 7 days
- Levels:
  - DEBUG: API requests/responses, browser automation steps
  - INFO: User actions (commands run, data fetched)
  - WARNING: Non-critical issues (cached data used, slow network)
  - ERROR: Actionable failures (browser not found, API error)

**Error Message Examples**:
```
❌ Error: Could not connect to Chrome browser

Possible causes:
  • Chrome is not running
  • Playwright MCP extension not installed
  • MCP server not started

To fix:
  1. Open Chrome and install MCP extension: https://github.com/microsoft/playwright-mcp
  2. Ensure extension is enabled
  3. Run: claude-pulse auth check

For detailed logs: ~/.local/state/claude-pulse/app.log
```

**References**:
- structlog: https://www.structlog.org/

---

## Decision 12: Packaging & Distribution

**Decision**: Use **Poetry** for dependency management, publish to **PyPI**

**Rationale**:
- Poetry: Modern Python packaging, lock file for reproducible builds
- PyPI: Standard distribution channel (pip install claude-pulse)
- Simplifies installation (Constitution: User Experience)

**Alternatives Considered**:
1. **setuptools** - Rejected because:
   - More manual configuration
   - No built-in lock file
2. **Conda** - Rejected because:
   - Additional ecosystem complexity
   - PyPI is more universal

**Installation Methods**:
```bash
# PyPI (primary)
pip install claude-pulse

# From source (development)
git clone <repo>
cd claude-pulse
poetry install
```

**Entry Point**:
```toml
[tool.poetry.scripts]
claude-pulse = "claude_pulse.cli.main:app"
```

**References**:
- Poetry: https://python-poetry.org/

---

## Summary of Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Language | Python 3.11+ | Cross-platform, rich ecosystem |
| Agent Framework | claude-agent-sdk-python | Official Anthropic SDK, MCP support |
| Browser Automation | Playwright MCP Extension | Session reuse, no auth complexity |
| CLI Framework | Click | Auto --help, nested commands |
| Terminal UI | Rich | Beautiful tables, colors, progress |
| Data Models | Pydantic v2 | Validation, type safety |
| Storage | SQLite + TOML | Embedded, no server, cross-platform |
| Testing | pytest | Contract/integration/unit layers |
| Logging | structlog | Structured logs, debugging |
| Packaging | Poetry + PyPI | Modern packaging, easy install |

**All decisions align with Claude Pulse Constitution principles: Simplicity, UX Excellence, Visual Excellence, Cross-Platform, Robustness.**

