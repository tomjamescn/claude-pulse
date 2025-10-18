# MCP Protocol Contract: Playwright Chrome Extension

**Date**: 2025-10-19
**Contract Version**: 1.0.0
**MCP Extension**: microsoft/playwright-mcp (Chrome Extension)

## Overview

This document defines the expected behavior and contract for interacting with the Playwright MCP Chrome Extension. The extension provides an MCP (Model Context Protocol) server that allows programmatic control of Chrome browser sessions while **reusing existing authentication state** (cookies, sessions, etc.).

---

## Extension Setup

### Prerequisites

1. **Chrome/Chromium Browser**: Version 100+
2. **Playwright MCP Extension**: Installed from Chrome Web Store or loaded unpacked
3. **Extension Enabled**: Must be active in Chrome extensions page

### Installation

```bash
# Option 1: Chrome Web Store (if published)
# Visit: https://chrome.google.com/webstore/...

# Option 2: Load Unpacked (Development)
git clone https://github.com/microsoft/playwright-mcp
cd playwright-mcp/extension
# In Chrome: chrome://extensions → Enable Developer Mode → Load Unpacked → Select 'extension' folder
```

### Verification

After installation, the extension should:
- Show icon in Chrome toolbar
- Be listed in `chrome://extensions/`
- Start MCP server automatically (default: `http://localhost:3000`)

---

## MCP Server Connection

### Endpoint

- **Default URL**: `http://localhost:3000`
- **Protocol**: HTTP with JSON-RPC 2.0
- **Connection Type**: WebSocket or HTTP long-polling

### Connection Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `string` | `http://localhost:3000` | MCP server endpoint |
| `timeout` | `int` | `10` | Connection timeout (seconds) |
| `retry_attempts` | `int` | `3` | Number of connection retries |

### Connection Sequence

```python
from claude_agent_sdk import MCPClient

# 1. Create MCP client
client = MCPClient(url="http://localhost:3000", timeout=10)

# 2. Connect to server
await client.connect()

# 3. Verify extension is active
status = await client.get_status()
assert status["extension_active"] == True

# 4. Get browser context (with existing session)
context = await client.get_browser_context()
```

---

## Browser Context Contract

### `get_browser_context()`

**Purpose**: Retrieve an active browser context that reuses the existing Chrome session

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "browser.getContext",
  "params": {
    "profile": null  // Use default profile; or specify profile name
  },
  "id": 1
}
```

**Response** (Success):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "context_id": "ctx_abc123",
    "profile_name": "Default",
    "cookies_loaded": true,
    "session_active": true
  },
  "id": 1
}
```

**Response** (Failure - Browser Not Running):
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Chrome browser not running",
    "data": {
      "hint": "Please open Chrome and ensure extension is enabled"
    }
  },
  "id": 1
}
```

### `navigate(url)`

**Purpose**: Navigate to a URL in the browser context

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "page.navigate",
  "params": {
    "context_id": "ctx_abc123",
    "url": "https://claude.ai/settings/usage",
    "wait_until": "networkidle"  // Options: load, domcontentloaded, networkidle
  },
  "id": 2
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "url": "https://claude.ai/settings/usage",
    "status_code": 200
  },
  "id": 2
}
```

### `execute_script(script)`

**Purpose**: Execute JavaScript in the browser context

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "page.evaluate",
  "params": {
    "context_id": "ctx_abc123",
    "script": "return document.title;"
  },
  "id": 3
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "value": "Usage - Claude"
  },
  "id": 3
}
```

### `wait_for_network()`

**Purpose**: Wait for specific network request (e.g., usage API call)

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "page.waitForRequest",
  "params": {
    "context_id": "ctx_abc123",
    "url_pattern": "**/api/organizations/*/usage",
    "timeout": 10000  // milliseconds
  },
  "id": 4
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "matched": true,
    "request": {
      "url": "https://claude.ai/api/organizations/org_abc123/usage",
      "method": "GET",
      "headers": {...}
    },
    "response": {
      "status": 200,
      "body": "{\"billing_period\": \"2025-10\", ...}"
    }
  },
  "id": 4
}
```

---

## Session Reuse Behavior

### Expected Behavior

When using the MCP extension:

1. **Cookies Preserved**: Existing cookies from the Chrome profile are accessible
2. **Session Active**: If user is logged into Claude web, session persists
3. **No Re-Auth Required**: Tool should NOT prompt for login if session is valid
4. **Session Expiry Detection**: If session expired, tool should detect and prompt user to log in manually

### Session Validation

```python
async def check_session_valid(context):
    """Check if Claude session is active"""
    await context.navigate("https://claude.ai/settings/usage")

    # Wait for page load
    await context.wait_for_selector("body", timeout=5000)

    # Check if redirected to login
    current_url = await context.evaluate("window.location.href")

    if "login" in current_url or "auth" in current_url:
        return False  # Not logged in

    # Check for usage data presence (indicates logged in)
    has_usage_section = await context.evaluate(
        "!!document.querySelector('[data-testid=\"usage-section\"]')"
    )

    return has_usage_section
```

---

## Error Handling Contract

### Error Codes

| Code | Name | Description | Actionable Hint |
|------|------|-------------|-----------------|
| `-32001` | BrowserNotRunning | Chrome is not running | Open Chrome with MCP extension enabled |
| `-32002` | ExtensionNotFound | MCP extension not installed | Install Playwright MCP extension |
| `-32003` | ExtensionDisabled | MCP extension disabled | Enable extension in chrome://extensions |
| `-32004` | ConnectionTimeout | Connection timed out | Check if MCP server is running on localhost:3000 |
| `-32005` | SessionExpired | Claude session expired | Log in manually at https://claude.ai |

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32005,
    "message": "Claude session expired",
    "data": {
      "url": "https://claude.ai/login",
      "hint": "Please log in at https://claude.ai and try again"
    }
  },
  "id": 5
}
```

---

## Usage Flow: Fetching Claude Data

### Complete Sequence

```python
from claude_agent_sdk import MCPClient

async def fetch_usage_data():
    # 1. Connect to MCP server
    client = MCPClient(url="http://localhost:3000")
    await client.connect()

    # 2. Get browser context (reuses existing session)
    context = await client.get_browser_context()

    # 3. Navigate to usage page
    await context.navigate("https://claude.ai/settings/usage")

    # 4. Wait for usage API request
    api_response = await context.wait_for_request(
        url_pattern="**/api/organizations/*/usage",
        timeout=10000
    )

    # 5. Extract usage data from API response
    usage_json = api_response["response"]["body"]
    usage_data = UsageData.model_validate_json(usage_json)

    return usage_data
```

---

## Testing Contract Compliance

### Manual Test: Connection

```bash
# 1. Start Chrome with MCP extension
# 2. Run connection test
python -m claude_pulse auth check

# Expected output:
# ✓ MCP server reachable at http://localhost:3000
# ✓ Browser context available
# ✓ Claude session active
```

### Automated Test: Integration

```python
# tests/integration/test_mcp_connection.py
import pytest
from claude_pulse.services.browser import MCPBrowserService

@pytest.mark.integration
async def test_mcp_connection():
    """Test MCP extension connection"""
    service = MCPBrowserService()

    # Should connect without errors
    await service.connect()

    # Should get valid browser context
    context = await service.get_context()
    assert context is not None
    assert context.session_active == True

    await service.disconnect()
```

---

## Fallback Strategy

If MCP extension is not available or fails:

1. **Detection**: Tool detects connection failure
2. **User Prompt**:
   ```
   ❌ Error: Could not connect to Playwright MCP extension

   This tool requires the Playwright MCP Chrome Extension to access
   your Claude usage data without storing credentials.

   Setup Instructions:
   1. Install extension: https://github.com/microsoft/playwright-mcp
   2. Open Chrome and ensure extension is enabled
   3. Run: claude-pulse auth check

   Alternative (not recommended):
   - Manual cookie export: claude-pulse auth manual-setup
   ```

3. **No Fallback Implementation in MVP**: P1 requires MCP extension
4. **Future (P4+)**: Could add manual cookie export/import

---

## References

- **Playwright MCP Repository**: https://github.com/microsoft/playwright-mcp
- **MCP Extension README**: https://github.com/microsoft/playwright-mcp/blob/main/extension/README.md
- **Claude Agent SDK**: https://github.com/anthropics/claude-agent-sdk-python
- **MCP Specification**: https://modelcontextprotocol.io/

