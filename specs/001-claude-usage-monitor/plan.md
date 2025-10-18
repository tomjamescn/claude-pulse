# Implementation Plan: Claude Usage Monitor

**Branch**: `001-claude-usage-monitor` | **Date**: 2025-10-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-claude-usage-monitor/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a cross-platform CLI tool to monitor Claude usage data fetched from https://claude.ai/settings/usage. The tool will use **claude-agent-sdk-python** as the foundation framework and **Playwright MCP Chrome Extension** for browser automation, leveraging existing browser sessions to bypass complex authentication (users must already be logged in to Claude web).

**Core P1 Features**:
- View current usage (tokens, messages, quotas, percentages)
- Authentication via browser session reuse (Playwright MCP)

**P2/P3 Features**:
- Historical usage tracking with local storage
- Usage alerts when approaching limits

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- **claude-agent-sdk-python**: Agent framework foundation (https://github.com/anthropics/claude-agent-sdk-python)
- **Playwright MCP Chrome Extension**: Browser automation with session reuse (https://github.com/microsoft/playwright-mcp)
- **Rich**: Terminal formatting and tables (color, progress bars, alignment)
- **Click**: CLI framework (commands, arguments, help generation)
- **Pydantic**: Data validation and settings management

**Storage**:
- Configuration: JSON/TOML files (~/.config/claude-pulse/)
- Historical data: SQLite or JSON files for usage snapshots
- No external database required

**Testing**:
- pytest for unit and integration tests
- Contract tests for API data structure validation
- Platform tests using GitHub Actions (Linux, macOS, Windows)

**Target Platform**:
- Linux (Ubuntu 20.04+), macOS (11+), Windows (10+)
- Cross-platform CLI application

**Project Type**: Single project (CLI tool)

**Performance Goals**:
- Data fetch: <5 seconds (90th percentile)
- CLI startup: <1 second
- Table rendering: <100ms

**Constraints**:
- Browser session dependency: Requires Chrome/Chromium with active Claude session
- No headless mode for initial MVP (uses actual browser via MCP)
- Network dependent (no offline mode for live data)

**Scale/Scope**:
- Single-user tool (personal usage monitoring)
- ~2000 lines of Python code estimated
- Support for 1 organization per user (multi-org is P4+)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [Claude Pulse Constitution](../../.specify/memory/constitution.md):

- [x] **Simplicity First**: Yes - leverages Playwright MCP to avoid complex auth implementation. Uses standard libraries (Click, Rich) without reinventing wheels. Browser session reuse is simplest auth approach.
- [x] **User Experience**: Yes - Click provides --help automatically, Rich enables progress indicators, spec requires actionable error messages with guidance.
- [x] **Visual Excellence**: Yes - Rich library for colored tables, progress bars, and terminal formatting. --no-color flag planned. Unicode symbols for status indicators.
- [x] **Cross-Platform**: Yes - Python 3.11+ works on all platforms. pathlib for path handling. Playwright supports Chrome on Linux/macOS/Windows. Config paths use platform-appropriate directories.
- [x] **Robustness**: Yes - Pydantic for input validation. Spec requires Ctrl+C handling, error logging, atomic writes for config. Edge cases documented.
- [x] **Testing**: Yes - pytest for unit/integration tests. Contract tests for Claude API responses. Platform-specific GitHub Actions planned.
- [x] **Documentation**: Yes - README with installation/quickstart. Click auto-generates command help. Bilingual docs (中英文) in README and key error messages.

**Pre-Design Gate: PASSED** ✅ - No violations, proceed to Phase 0

*Any violations must be justified in the Complexity Tracking section below*

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/claude_pulse/
├── __init__.py
├── __main__.py              # Entry point: python -m claude_pulse
├── cli/
│   ├── __init__.py
│   ├── main.py              # Click app root
│   ├── usage.py             # Usage viewing commands
│   ├── auth.py              # Auth check commands (MCP connection)
│   └── history.py           # Historical tracking commands (P2)
├── models/
│   ├── __init__.py
│   ├── usage.py             # UsageData, UsageSnapshot models
│   ├── config.py            # Configuration models
│   └── alert.py             # AlertConfiguration model (P3)
├── services/
│   ├── __init__.py
│   ├── browser.py           # Playwright MCP integration
│   ├── usage_fetcher.py     # Fetch usage from Claude website
│   ├── storage.py           # Local data persistence
│   └── formatter.py         # Rich table formatting
└── utils/
    ├── __init__.py
    ├── config.py            # Config file management
    └── logging.py           # Logging setup

tests/
├── contract/
│   └── test_claude_api_structure.py  # Validate API response format
├── integration/
│   ├── test_usage_flow.py            # End-to-end usage viewing
│   └── test_browser_integration.py   # MCP connection tests
└── unit/
    ├── test_models.py
    ├── test_services.py
    └── test_formatters.py

pyproject.toml               # Poetry/setuptools config
README.md                    # Installation & quickstart
```

**Structure Decision**: Single-project Python CLI application. Using modern Python packaging with `src/` layout to avoid import issues. Click for CLI routing, Rich for formatting, Playwright MCP for browser automation. Models use Pydantic for validation. Services layer separates concerns (fetching, storage, formatting).

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

