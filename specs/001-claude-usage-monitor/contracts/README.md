# API Contracts: Claude Usage Monitor

**Date**: 2025-10-19
**Feature**: Claude Usage Monitor
**Phase**: 1 - Contract Definitions

## Overview

This directory contains API contract definitions for the Claude Usage Monitor. Since Claude does not provide a public API for usage data, these contracts are based on **reverse-engineered browser requests** from https://claude.ai/settings/usage.

**Important Notes**:
- These contracts are **unofficial** and may change without notice
- The tool includes **contract tests** to detect API changes
- If API structure changes, the tool will fail gracefully with actionable error messages

---

## Contracts

1. **[claude-usage-api.json](./claude-usage-api.json)** - JSON Schema for Claude usage API response
2. **[mcp-protocol.md](./mcp-protocol.md)** - MCP protocol expectations for Playwright extension

---

## Discovery Process

To discover/update the Claude API endpoint:

1. Open Chrome and navigate to https://claude.ai/settings/usage
2. Open DevTools (F12) → Network tab
3. Filter by XHR/Fetch
4. Look for requests to `/api/organizations/*/usage` or similar
5. Inspect request headers and response JSON
6. Update `claude-usage-api.json` with actual structure

---

## Versioning

- **Contract Version**: 1.0.0 (Initial reverse-engineering on 2025-10-19)
- **Last Verified**: 2025-10-19
- **Claude Web Version**: Unknown (no public version API)

When Claude updates their web interface, contract tests will fail. Update process:
1. Re-run discovery process (above)
2. Update JSON schema in `claude-usage-api.json`
3. Increment contract version
4. Update contract tests in `tests/contract/`

---

## Contract Testing

Contract tests validate that Claude API responses match the expected structure:

```python
# tests/contract/test_claude_api_structure.py
import pytest
from jsonschema import validate
from claude_pulse.services.usage_fetcher import UsageFetcher

def test_usage_response_structure():
    """Validate Claude API response matches contract"""
    # This test uses a real browser session (manual trigger)
    # Fails if API structure changes

    fetcher = UsageFetcher()
    result = fetcher.fetch_current()

    assert result.success, "Fetch failed - cannot validate contract"

    # Load schema
    with open("specs/001-claude-usage-monitor/contracts/claude-usage-api.json") as f:
        schema = json.load(f)

    # Validate response structure
    raw_response = result.data.model_dump()
    validate(instance=raw_response, schema=schema)
```

---

## Failure Handling

If contract validation fails:

```python
# src/claude_pulse/services/usage_fetcher.py
try:
    validate_response(response_json, contract_schema)
except ValidationError as e:
    return FetchResult(
        success=False,
        error=FetchError(
            code=ErrorCode.PARSE_ERROR,
            message="Claude API structure changed",
            details={"validation_error": str(e)},
            actionable_hint=(
                "The Claude API structure has changed. "
                "Please report this issue: "
                "https://github.com/<org>/claude-pulse/issues"
            )
        ),
        duration_ms=elapsed_ms
    )
```

