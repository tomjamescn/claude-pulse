# Data Model: Claude Usage Monitor

**Date**: 2025-10-19
**Feature**: Claude Usage Monitor
**Phase**: 1 - Data Model Design

## Overview

This document defines the data models for the Claude Usage Monitor tool. All models use **Pydantic v2** for validation and type safety. Models are organized by domain: usage data, configuration, alerts, and snapshots.

---

## 1. UsageData (使用量数据)

**Purpose**: Represents current usage data for a billing period

**Source**: Fetched from Claude API (`/api/organizations/{org_id}/usage`)

**Location**: `src/claude_pulse/models/usage.py`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `billing_period` | `str` | Yes | Billing period identifier (e.g., "2025-10") |
| `period_start` | `datetime` | Yes | Start of billing period (ISO 8601) |
| `period_end` | `datetime` | Yes | End of billing period (ISO 8601) |
| `input_tokens_used` | `int` | Yes | Number of input tokens consumed |
| `input_tokens_quota` | `int` | Yes | Input token quota for period |
| `output_tokens_used` | `int` | Yes | Number of output tokens consumed |
| `output_tokens_quota` | `int` | Yes | Output token quota for period |
| `total_messages` | `int` | Yes | Total messages sent in period |
| `messages_quota` | `int \| None` | No | Message quota (if applicable) |
| `fetched_at` | `datetime` | Yes | Timestamp when data was fetched |

### Computed Properties

| Property | Type | Description |
|----------|------|-------------|
| `input_usage_percent` | `float` | Percentage of input quota used (0-100) |
| `output_usage_percent` | `float` | Percentage of output quota used (0-100) |
| `overall_usage_percent` | `float` | Average of input and output percentages |
| `days_remaining` | `int` | Days until period reset |

### Validation Rules

- `input_tokens_used` must be <= `input_tokens_quota`
- `output_tokens_used` must be <= `output_tokens_quota`
- `period_start` must be < `period_end`
- `fetched_at` must be between `period_start` and current time + 24h (grace period)

### Example JSON

```json
{
  "billing_period": "2025-10",
  "period_start": "2025-10-01T00:00:00Z",
  "period_end": "2025-10-31T23:59:59Z",
  "input_tokens_used": 1500000,
  "input_tokens_quota": 5000000,
  "output_tokens_used": 750000,
  "output_tokens_quota": 2500000,
  "total_messages": 320,
  "messages_quota": null,
  "fetched_at": "2025-10-19T10:30:00Z"
}
```

### Pydantic Model Stub

```python
from datetime import datetime
from pydantic import BaseModel, Field, computed_field

class UsageData(BaseModel):
    billing_period: str = Field(..., description="Billing period (e.g., 2025-10)")
    period_start: datetime
    period_end: datetime
    input_tokens_used: int = Field(ge=0)
    input_tokens_quota: int = Field(gt=0)
    output_tokens_used: int = Field(ge=0)
    output_tokens_quota: int = Field(gt=0)
    total_messages: int = Field(ge=0)
    messages_quota: int | None = None
    fetched_at: datetime

    @computed_field
    @property
    def input_usage_percent(self) -> float:
        return (self.input_tokens_used / self.input_tokens_quota) * 100

    @computed_field
    @property
    def output_usage_percent(self) -> float:
        return (self.output_tokens_used / self.output_tokens_quota) * 100
```

---

## 2. UsageSnapshot (使用量快照)

**Purpose**: Historical point-in-time usage record

**Source**: Created from `UsageData` and stored in SQLite

**Location**: `src/claude_pulse/models/usage.py`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `int \| None` | No | Database primary key (auto-increment) |
| `timestamp` | `datetime` | Yes | When snapshot was taken |
| `usage_data` | `UsageData` | Yes | Full usage data at this point |
| `source` | `SnapshotSource` | Yes | How snapshot was created (manual/auto) |

### Enum: SnapshotSource

```python
from enum import Enum

class SnapshotSource(str, Enum):
    MANUAL = "manual"       # User explicitly ran command
    AUTOMATIC = "automatic" # Scheduled/background task
```

### Relationships

- One-to-one with `UsageData` (embedded)
- Stored in SQLite table `usage_snapshots`

### Example JSON

```json
{
  "id": 42,
  "timestamp": "2025-10-19T10:30:00Z",
  "source": "manual",
  "usage_data": {
    "billing_period": "2025-10",
    "input_tokens_used": 1500000,
    ...
  }
}
```

---

## 3. AlertConfiguration (告警配置)

**Purpose**: User-configurable alert thresholds and settings

**Source**: Stored in `config.toml`

**Location**: `src/claude_pulse/models/alert.py`

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `enabled` | `bool` | Yes | `false` | Whether alerts are enabled |
| `warning_threshold` | `int` | Yes | `80` | Warning threshold percentage (0-100) |
| `critical_threshold` | `int` | Yes | `95` | Critical threshold percentage (0-100) |
| `notify_system` | `bool` | Yes | `false` | Send OS notifications (P3 feature) |
| `notify_on_reset` | `bool` | Yes | `true` | Notify when new period starts |

### Validation Rules

- `warning_threshold` must be < `critical_threshold`
- Both thresholds must be in range [0, 100]
- If `notify_system` is true, require platform notification support

### Example TOML

```toml
[alerts]
enabled = true
warning_threshold = 80
critical_threshold = 95
notify_system = false
notify_on_reset = true
```

### Pydantic Model Stub

```python
from pydantic import BaseModel, Field, model_validator

class AlertConfiguration(BaseModel):
    enabled: bool = False
    warning_threshold: int = Field(default=80, ge=0, le=100)
    critical_threshold: int = Field(default=95, ge=0, le=100)
    notify_system: bool = False
    notify_on_reset: bool = True

    @model_validator(mode='after')
    def validate_thresholds(self):
        if self.warning_threshold >= self.critical_threshold:
            raise ValueError("warning_threshold must be < critical_threshold")
        return self
```

---

## 4. AppConfig (应用配置)

**Purpose**: Global application configuration

**Source**: Loaded from `~/.config/claude-pulse/config.toml`

**Location**: `src/claude_pulse/models/config.py`

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `general` | `GeneralConfig` | Yes | - | General settings |
| `alerts` | `AlertConfiguration` | Yes | - | Alert settings |
| `history` | `HistoryConfig` | Yes | - | History tracking settings |

### Nested: GeneralConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `default_output_format` | `OutputFormat` | `"table"` | Default output format |
| `color_enabled` | `bool` | `true` | Enable colored output |
| `log_level` | `str` | `"INFO"` | Logging level (DEBUG/INFO/WARNING/ERROR) |

### Enum: OutputFormat

```python
from enum import Enum

class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"
    PLAIN = "plain"
```

### Nested: HistoryConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `retention_days` | `int` | `30` | Days to keep snapshots |
| `auto_snapshot` | `bool` | `false` | Auto-save on every fetch (P2 feature) |
| `database_path` | `Path \| None` | `None` | Custom DB path (default: platform data dir) |

### Example TOML

```toml
[general]
default_output_format = "table"
color_enabled = true
log_level = "INFO"

[alerts]
enabled = false
warning_threshold = 80
critical_threshold = 95
notify_system = false
notify_on_reset = true

[history]
retention_days = 30
auto_snapshot = false
```

### Pydantic Model Stub

```python
from pathlib import Path
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    general: GeneralConfig
    alerts: AlertConfiguration
    history: HistoryConfig

    class Config:
        toml_file = "config.toml"
```

---

## 5. MCPConnectionInfo (MCP 连接信息)

**Purpose**: Connection details for Playwright MCP extension

**Source**: Auto-discovered or user-configured

**Location**: `src/claude_pulse/models/config.py`

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `mcp_server_url` | `str` | No | `"http://localhost:3000"` | MCP server endpoint |
| `chrome_profile` | `str \| None` | No | `None` | Chrome profile name (if specific) |
| `connection_timeout` | `int` | Yes | `10` | Connection timeout (seconds) |

### Example TOML

```toml
[mcp]
mcp_server_url = "http://localhost:3000"
chrome_profile = null
connection_timeout = 10
```

---

## 6. FetchResult (获取结果)

**Purpose**: Result wrapper for usage fetch operations

**Source**: Returned by `UsageFetcher` service

**Location**: `src/claude_pulse/models/usage.py`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `success` | `bool` | Yes | Whether fetch succeeded |
| `data` | `UsageData \| None` | No | Usage data (if successful) |
| `error` | `FetchError \| None` | No | Error details (if failed) |
| `duration_ms` | `int` | Yes | Fetch duration in milliseconds |

### Nested: FetchError

| Field | Type | Description |
|-------|------|-------------|
| `code` | `ErrorCode` | Error category |
| `message` | `str` | Human-readable error message |
| `details` | `dict[str, Any]` | Additional context |
| `actionable_hint` | `str` | Suggested fix for user |

### Enum: ErrorCode

```python
from enum import Enum

class ErrorCode(str, Enum):
    BROWSER_NOT_FOUND = "browser_not_found"
    MCP_CONNECTION_FAILED = "mcp_connection_failed"
    NOT_LOGGED_IN = "not_logged_in"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
    TIMEOUT = "timeout"
```

### Example

```python
# Success
FetchResult(
    success=True,
    data=UsageData(...),
    error=None,
    duration_ms=3420
)

# Failure
FetchResult(
    success=False,
    data=None,
    error=FetchError(
        code=ErrorCode.NOT_LOGGED_IN,
        message="Not logged into Claude",
        details={"url": "https://claude.ai/settings/usage"},
        actionable_hint="Please log in at https://claude.ai and try again"
    ),
    duration_ms=1200
)
```

---

## Database Schema (SQLite)

**File**: `~/.local/share/claude-pulse/usage.db` (or platform equivalent)

### Table: `usage_snapshots`

```sql
CREATE TABLE IF NOT EXISTS usage_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,                -- ISO 8601 datetime
    source TEXT NOT NULL CHECK(source IN ('manual', 'automatic')),

    -- Usage data fields (denormalized for simplicity)
    billing_period TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    input_tokens_used INTEGER NOT NULL,
    input_tokens_quota INTEGER NOT NULL,
    output_tokens_used INTEGER NOT NULL,
    output_tokens_quota INTEGER NOT NULL,
    total_messages INTEGER NOT NULL,
    messages_quota INTEGER,
    fetched_at TEXT NOT NULL,

    -- Indexes for common queries
    UNIQUE(timestamp, billing_period)
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_billing_period ON usage_snapshots(billing_period);
```

### Queries

```sql
-- Get all snapshots for current billing period
SELECT * FROM usage_snapshots
WHERE billing_period = ?
ORDER BY timestamp DESC;

-- Get snapshots in date range
SELECT * FROM usage_snapshots
WHERE timestamp >= ? AND timestamp <= ?
ORDER BY timestamp ASC;

-- Delete old snapshots (retention policy)
DELETE FROM usage_snapshots
WHERE timestamp < datetime('now', '-30 days');
```

---

## Entity Relationships

```
┌──────────────────┐
│   AppConfig      │
├──────────────────┤
│ general          │──┐
│ alerts           │  │
│ history          │  │
└──────────────────┘  │
                      │
                      │ loads
                      ▼
       ┌──────────────────────────┐
       │   config.toml            │
       └──────────────────────────┘

┌──────────────────┐
│   UsageFetcher   │
├──────────────────┤
│ fetch_current()  │──┐
└──────────────────┘  │
                      │ returns
                      ▼
       ┌──────────────────────────┐
       │   FetchResult            │
       ├──────────────────────────┤
       │ data: UsageData          │
       └──────────────────────────┘

┌──────────────────┐
│   UsageSnapshot  │──┐
├──────────────────┤  │
│ usage_data       │  │ stores
└──────────────────┘  │
                      ▼
       ┌──────────────────────────┐
       │   SQLite: usage.db       │
       └──────────────────────────┘
```

---

## Validation Summary

All models enforce:
- **Type safety**: Pydantic validates types at runtime
- **Range constraints**: `ge`, `le`, `gt` validators
- **Required fields**: Explicit `...` or defaults
- **Cross-field validation**: Custom validators (@model_validator)
- **Computed properties**: Derived fields (@computed_field)

**Constitution Compliance**:
- ✅ **Robustness**: Input validation prevents invalid states
- ✅ **Simplicity**: Models are flat, no deep nesting
- ✅ **Cross-Platform**: Uses `pathlib.Path` and platform-aware defaults

