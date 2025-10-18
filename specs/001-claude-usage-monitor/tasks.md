# Tasks: Claude Usage Monitor

**Input**: Design documents from `/specs/001-claude-usage-monitor/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY for this feature (specified in spec.md and constitution requirements).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan (src/, tests/, pyproject.toml)
- [ ] T002 Initialize Python project with Poetry in pyproject.toml
- [ ] T003 [P] Configure linting (ruff/flake8) and formatting (black) tools
- [ ] T004 [P] Setup .gitignore for Python project (venv/, __pycache__/, .pytest_cache/, *.pyc)
- [ ] T005 [P] Create README.md with installation and quickstart guide (bilingual 中英文)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Install core dependencies in pyproject.toml (claude-agent-sdk-python, click, rich, pydantic, platformdirs)
- [ ] T007 [P] Create src/claude_pulse/__init__.py and src/claude_pulse/__main__.py
- [ ] T008 [P] Implement logging setup in src/claude_pulse/utils/logging.py (structlog configuration)
- [ ] T009 [P] Implement config management in src/claude_pulse/utils/config.py (platform-specific paths using platformdirs)
- [ ] T010 [P] Create base CLI app structure in src/claude_pulse/cli/main.py (Click group with --help, --version, --no-color)
- [ ] T011 [P] Create Pydantic base models in src/claude_pulse/models/__init__.py (import organization)
- [ ] T012 Create tests/conftest.py with pytest fixtures (mock MCP client, temp config dirs)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Current Usage (Priority: P1) 🎯 MVP

**Goal**: Users can run a command to view their current Claude usage (tokens, messages, quotas, percentages) in a beautiful formatted table

**Independent Test**: Run `claude-pulse usage show` and verify it displays current usage data with colored table, progress bars, and percentage calculations

### Tests for User Story 1 ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Contract test for Claude API response structure in tests/contract/test_claude_api_structure.py
- [ ] T014 [P] [US1] Integration test for full usage viewing flow in tests/integration/test_usage_flow.py
- [ ] T015 [P] [US1] Unit tests for UsageData model in tests/unit/test_models.py

### Implementation for User Story 1

**Models**:
- [ ] T016 [P] [US1] Create UsageData model in src/claude_pulse/models/usage.py (all fields from data-model.md)
- [ ] T017 [P] [US1] Create FetchResult and FetchError models in src/claude_pulse/models/usage.py (error handling wrapper)
- [ ] T018 [US1] Add computed properties to UsageData in src/claude_pulse/models/usage.py (input_usage_percent, output_usage_percent, overall_usage_percent, days_remaining)
- [ ] T019 [US1] Add Pydantic validators to UsageData in src/claude_pulse/models/usage.py (quota checks, date validations)

**Services**:
- [ ] T020 [US1] Implement MCP browser service in src/claude_pulse/services/browser.py (connect to Playwright MCP extension)
- [ ] T021 [US1] Implement usage fetcher in src/claude_pulse/services/usage_fetcher.py (navigate to claude.ai/settings/usage, wait for API request, parse response)
- [ ] T022 [US1] Add error handling to usage fetcher in src/claude_pulse/services/usage_fetcher.py (network errors, session expiry, API changes)
- [ ] T023 [P] [US1] Implement Rich table formatter in src/claude_pulse/services/formatter.py (colored tables, progress bars, Unicode symbols)

**CLI Commands**:
- [ ] T024 [US1] Create usage command group in src/claude_pulse/cli/usage.py (Click group for usage subcommands)
- [ ] T025 [US1] Implement `usage show` command in src/claude_pulse/cli/usage.py (fetch + format + display, --json and --no-color flags)
- [ ] T026 [US1] Add progress indicator to usage show in src/claude_pulse/cli/usage.py (Rich Progress during fetch)

**Integration**:
- [ ] T027 [US1] Wire usage commands into main CLI app in src/claude_pulse/cli/main.py
- [ ] T028 [US1] Add error message localization (中英文) in src/claude_pulse/cli/usage.py (actionable hints for common errors)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can run `claude-pulse usage show` to see their current usage.

---

## Phase 4: User Story 2 - Authentication Management (Priority: P1) 🎯 MVP

**Goal**: Users can check MCP connection status and verify their Claude session is active, with clear guidance if not logged in

**Independent Test**: Run `claude-pulse auth check` and verify it reports MCP connection status, browser context availability, and Claude session validity

### Tests for User Story 2 ⚠️

- [ ] T029 [P] [US2] Integration test for MCP connection in tests/integration/test_browser_integration.py
- [ ] T030 [P] [US2] Unit tests for browser service in tests/unit/test_services.py

### Implementation for User Story 2

**Models**:
- [ ] T031 [P] [US2] Create MCPConnectionInfo model in src/claude_pulse/models/config.py (server URL, timeout, chrome profile)

**Services**:
- [ ] T032 [US2] Add session validation to browser service in src/claude_pulse/services/browser.py (check_session_valid method)
- [ ] T033 [US2] Add MCP connection diagnostics in src/claude_pulse/services/browser.py (detect extension not installed, browser not running, etc.)

**CLI Commands**:
- [ ] T034 [US2] Create auth command group in src/claude_pulse/cli/auth.py (Click group for auth subcommands)
- [ ] T035 [US2] Implement `auth check` command in src/claude_pulse/cli/auth.py (MCP connection + session validation + status display)
- [ ] T036 [US2] Implement `auth status` command in src/claude_pulse/cli/auth.py (show connection details: URL, profile, session state)
- [ ] T037 [P] [US2] Add actionable error messages to auth commands in src/claude_pulse/cli/auth.py (installation guides, troubleshooting links)

**Integration**:
- [ ] T038 [US2] Wire auth commands into main CLI app in src/claude_pulse/cli/main.py
- [ ] T039 [US2] Update usage show command to check auth status first in src/claude_pulse/cli/usage.py (fail early with helpful message if not authenticated)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can check their auth status and view usage data.

---

## Phase 5: User Story 3 - Usage History Tracking (Priority: P2)

**Goal**: Users can save usage snapshots locally and query historical usage data for trend analysis

**Independent Test**: Run `claude-pulse history snapshot` to save current usage, then `claude-pulse history show --days 7` to view historical data

### Tests for User Story 3 ⚠️

- [ ] T040 [P] [US3] Unit tests for UsageSnapshot model in tests/unit/test_models.py
- [ ] T041 [P] [US3] Unit tests for storage service in tests/unit/test_services.py
- [ ] T042 [US3] Integration test for history tracking flow in tests/integration/test_history_flow.py

### Implementation for User Story 3

**Models**:
- [ ] T043 [P] [US3] Create UsageSnapshot model in src/claude_pulse/models/usage.py (timestamp, source, usage_data)
- [ ] T044 [P] [US3] Create HistoryConfig model in src/claude_pulse/models/config.py (retention_days, auto_snapshot, database_path)

**Services**:
- [ ] T045 [US3] Implement SQLite storage service in src/claude_pulse/services/storage.py (create tables, save/load snapshots, retention cleanup)
- [ ] T046 [US3] Add snapshot querying to storage service in src/claude_pulse/services/storage.py (query by date range, billing period)
- [ ] T047 [P] [US3] Implement history formatter in src/claude_pulse/services/formatter.py (historical table view, trend indicators)

**CLI Commands**:
- [ ] T048 [US3] Create history command group in src/claude_pulse/cli/history.py (Click group for history subcommands)
- [ ] T049 [US3] Implement `history snapshot` command in src/claude_pulse/cli/history.py (fetch + save current usage)
- [ ] T050 [US3] Implement `history show` command in src/claude_pulse/cli/history.py (--days, --from, --to filters, formatted display)
- [ ] T051 [P] [US3] Add auto-snapshot option to usage show in src/claude_pulse/cli/usage.py (save snapshot if config.history.auto_snapshot=true)

**Integration**:
- [ ] T052 [US3] Wire history commands into main CLI app in src/claude_pulse/cli/main.py
- [ ] T053 [US3] Add retention policy background task in src/claude_pulse/services/storage.py (cleanup old snapshots based on retention_days)

**Checkpoint**: At this point, all P1 and P2 user stories work independently. Users can track usage history over time.

---

## Phase 6: User Story 4 - Usage Alerts (Priority: P3)

**Goal**: Users can configure usage thresholds and receive warnings when approaching limits

**Independent Test**: Set threshold to 80%, verify warning appears when usage exceeds threshold

### Tests for User Story 4 ⚠️

- [ ] T054 [P] [US4] Unit tests for AlertConfiguration model in tests/unit/test_models.py
- [ ] T055 [P] [US4] Unit tests for alert logic in tests/unit/test_services.py

### Implementation for User Story 4

**Models**:
- [ ] T056 [P] [US4] Create AlertConfiguration model in src/claude_pulse/models/alert.py (enabled, warning_threshold, critical_threshold, notify_system)

**Services**:
- [ ] T057 [US4] Implement alert checker in src/claude_pulse/services/usage_fetcher.py (evaluate thresholds against current usage)
- [ ] T058 [US4] Add alert display to formatter in src/claude_pulse/services/formatter.py (warning/critical banners with Unicode symbols)

**CLI Commands**:
- [ ] T059 [US4] Add alert configuration commands to config CLI in src/claude_pulse/cli/main.py (config set alerts.enabled true, etc.)
- [ ] T060 [US4] Integrate alert display into usage show in src/claude_pulse/cli/usage.py (show warnings/alerts if thresholds exceeded)

**Checkpoint**: All user stories (P1-P3) now independently functional. Full feature set complete.

---

## Phase 7: Configuration Management (Cross-Cutting)

**Purpose**: Enable users to customize tool behavior via configuration file

- [ ] T061 [P] Create AppConfig and GeneralConfig models in src/claude_pulse/models/config.py (all config sections from data-model.md)
- [ ] T062 [P] Implement config file loading in src/claude_pulse/utils/config.py (TOML parsing with defaults)
- [ ] T063 [P] Implement config file writing in src/claude_pulse/utils/config.py (atomic writes, tomli-w library)
- [ ] T064 Create config command group in src/claude_pulse/cli/main.py (config show, config edit, config reset, config set)
- [ ] T065 Add --config flag to main CLI app in src/claude_pulse/cli/main.py (override default config path)
- [ ] T066 Create default config.toml template in src/claude_pulse/utils/config.py (embedded default config)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Constitution Compliance

Per [Claude Pulse Constitution](../../.specify/memory/constitution.md):

- [ ] T067 [P] **User Experience**: Verify all commands have comprehensive --help documentation
- [ ] T068 [P] **User Experience**: Ensure all error messages include actionable guidance (review all error paths)
- [ ] T069 [P] **Visual Excellence**: Validate color usage consistency across all commands (red/yellow/green/blue for error/warning/success/info)
- [ ] T070 [P] **Visual Excellence**: Test --no-color flag works for all output commands
- [ ] T071 [P] **Visual Excellence**: Check table/list alignment and terminal width handling in all formatters
- [ ] T072 **Cross-Platform**: Test on Linux (Ubuntu 20.04+), macOS (11+), and Windows (10+)
- [ ] T073 [P] **Robustness**: Verify input validation in all Pydantic models (add missing validators)
- [ ] T074 [P] **Robustness**: Test Ctrl+C graceful exit in long-running operations (usage fetch, history queries)
- [ ] T075 [P] **Robustness**: Review error logging coverage (ensure all exceptions logged with context)
- [ ] T076 [P] **Simplicity**: Code review for unnecessary complexity (refactor if found)

### Documentation & Quality

- [ ] T077 [P] Update README.md with complete usage examples (all commands)
- [ ] T078 [P] Add bilingual error messages (中英文) to all critical error paths
- [ ] T079 [P] Create CHANGELOG.md with initial v1.0.0 release notes
- [ ] T080 [P] Add docstrings to all public APIs (models, services, CLI commands)
- [ ] T081 Code cleanup and refactoring (remove debug code, optimize imports)
- [ ] T082 Performance optimization if needed (caching, lazy loading)
- [ ] T083 [P] Add unit tests for untested edge cases in tests/unit/
- [ ] T084 Security review (no hardcoded secrets, proper file permissions for config)
- [ ] T085 Run quickstart.md validation (follow guide end-to-end, update if needed)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can proceed in parallel after Foundation
  - US3 (P2) depends on US1 completion (needs UsageData model)
  - US4 (P3) depends on US1 completion (needs usage fetching logic)
- **Configuration (Phase 7)**: Can run in parallel with user stories (independent feature)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (independent auth checking)
- **User Story 3 (P2)**: Depends on User Story 1 (needs UsageData model to save snapshots)
- **User Story 4 (P3)**: Depends on User Story 1 (needs usage fetching to evaluate thresholds)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (T013-T015 before T016-T028)
- Models before services (T016-T019 before T020-T023)
- Services before CLI commands (T020-T023 before T024-T026)
- Core implementation before integration (T024-T026 before T027-T028)
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T003-T005) can run in parallel
- All Foundational tasks marked [P] (T007-T011) can run in parallel within Phase 2
- **US1 and US2 can start in parallel** after Foundation completes
- Within US1: Tests (T013-T015), models (T016-T017), and formatter (T023) can run in parallel
- Within US2: Tests (T029-T030), model (T031), and error messages (T037) can run in parallel
- Within US3: Tests (T040-T042), models (T043-T044), and formatter (T047) can run in parallel
- Within US4: Tests (T054-T055) and model (T056) can run in parallel
- Configuration tasks (T061-T063) can run in parallel with user story implementation
- Polish tasks (T067-T084) can run in parallel after user stories complete

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T013: Contract test in tests/contract/test_claude_api_structure.py
Task T014: Integration test in tests/integration/test_usage_flow.py
Task T015: Unit test in tests/unit/test_models.py

# After tests fail, launch models in parallel:
Task T016: UsageData model in src/claude_pulse/models/usage.py
Task T017: FetchResult model in src/claude_pulse/models/usage.py

# Launch formatter in parallel with services:
Task T023: Rich formatter in src/claude_pulse/services/formatter.py
Task T020: Browser service in src/claude_pulse/services/browser.py
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T013-T028) - View usage
4. Complete Phase 4: User Story 2 (T029-T039) - Auth checking
5. **STOP and VALIDATE**: Test both stories independently
6. Deploy/demo MVP (P1 features only)

**MVP Deliverable**: Users can check auth status and view current Claude usage with beautiful terminal output.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 (P1) → Test independently → Deploy/Demo (MVP! ✅)
3. Add Configuration (Phase 7) → Test → Deploy/Demo (Enhanced configurability)
4. Add User Story 3 (P2) → Test independently → Deploy/Demo (Historical tracking)
5. Add User Story 4 (P3) → Test independently → Deploy/Demo (Alerts)
6. Polish (Phase 8) → Final QA → Deploy/Demo (Production-ready)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T012)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T013-T028) - View usage
   - **Developer B**: User Story 2 (T029-T039) - Auth management
   - **Developer C**: Configuration (T061-T066) - Config system
3. After P1 complete:
   - **Developer A**: User Story 3 (T040-T053) - History tracking
   - **Developer B**: User Story 4 (T054-T060) - Alerts
   - **Developer C**: Polish tasks (T067-T085) - Quality & docs
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests written FIRST (TDD) - verify they fail before implementing
- Commit after each task or logical group of parallel tasks
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Statistics

**Total Tasks**: 85
- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 7 tasks (BLOCKS all user stories)
- **Phase 3 (US1 - P1)**: 16 tasks (MVP core feature)
- **Phase 4 (US2 - P1)**: 11 tasks (MVP auth feature)
- **Phase 5 (US3 - P2)**: 14 tasks
- **Phase 6 (US4 - P3)**: 7 tasks
- **Phase 7 (Configuration)**: 6 tasks
- **Phase 8 (Polish)**: 19 tasks

**Tests**: 16 test tasks (contract, integration, unit) distributed across user stories
**Parallel Opportunities**: 44 tasks marked [P] can run concurrently
**MVP Scope**: Phases 1-4 (39 tasks) = ~46% of total work

