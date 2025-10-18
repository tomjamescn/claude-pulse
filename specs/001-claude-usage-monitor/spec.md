# Feature Specification: Claude Usage Monitor

**Feature Branch**: `001-claude-usage-monitor`
**Created**: 2025-10-19
**Status**: Draft
**Input**: User description: "开发一个能够监控claude usage的命令行工具,claude usage的具体数据通过claude官网:https://claude.ai/settings/usage 可以得到。这个页面加载后,会通过一个异步的请求获取实际用量数据。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Current Usage (Priority: P1)

用户希望快速查看当前的 Claude 使用情况,包括已使用量和剩余量,以便了解自己的账户状态。

Users want to quickly check their current Claude usage, including consumed and remaining quota, to understand their account status.

**Why this priority**: 这是工具的核心价值 - 让用户无需打开浏览器即可查看使用情况。这是最基础且最常用的功能。

This is the core value of the tool - allowing users to check usage without opening a browser. It's the most fundamental and frequently used feature.

**Independent Test**: 运行命令后能显示当前使用量数据,包括文本输入/输出的 token 数量和消息数。

Running the command displays current usage data, including token counts for text input/output and message counts.

**Acceptance Scenarios**:

1. **Given** 用户已配置认证凭据, **When** 用户运行查看使用量命令, **Then** 系统显示当前计费周期的使用情况(输入tokens、输出tokens、总消息数)
2. **Given** 用户首次使用工具, **When** 用户运行命令但未配置凭据, **Then** 系统提示用户如何配置认证信息
3. **Given** 用户已登录 Claude 账户, **When** 数据获取成功, **Then** 显示格式化的使用量表格,包含百分比和进度条
4. **Given** 网络连接正常, **When** 用户请求使用量数据, **Then** 响应时间在5秒内完成

---

### User Story 2 - Authentication Management (Priority: P1)

用户需要安全地配置和管理 Claude 账户的认证信息,以便工具能够访问使用量数据。

Users need to securely configure and manage authentication credentials for their Claude account so the tool can access usage data.

**Why this priority**: 没有认证就无法获取数据,这是使用工具的前提条件。必须在 P1 完成。

Without authentication, no data can be fetched. This is a prerequisite for using the tool and must be completed in P1.

**Independent Test**: 用户可以通过交互式命令配置认证,配置成功后能够正常获取使用量数据。

Users can configure authentication through an interactive command, and after successful configuration, they can fetch usage data normally.

**Acceptance Scenarios**:

1. **Given** 用户首次使用, **When** 运行配置命令, **Then** 系统引导用户输入认证信息并安全存储
2. **Given** 用户已配置凭据, **When** 用户运行登录测试命令, **Then** 系统验证凭据有效性并显示结果
3. **Given** 认证凭据已过期, **When** 用户尝试获取数据, **Then** 系统提示重新认证
4. **Given** 用户想要登出, **When** 运行清除凭据命令, **Then** 本地凭据被安全删除

---

### User Story 3 - Usage History Tracking (Priority: P2)

用户希望查看历史使用趋势,了解不同时间段的使用模式。

Users want to view historical usage trends to understand usage patterns over different time periods.

**Why this priority**: 虽然有用,但不是核心功能。用户首先需要能看到当前状态(P1),历史趋势是增强功能。

While useful, it's not a core feature. Users first need to see current status (P1); historical trends are an enhancement.

**Independent Test**: 用户可以查询特定时间范围的使用记录,并以图表或表格形式展示。

Users can query usage records for a specific time range and view them as charts or tables.

**Acceptance Scenarios**:

1. **Given** 系统已存储历史数据, **When** 用户请求最近7天的使用记录, **Then** 显示按天分组的使用统计
2. **Given** 用户查看历史数据, **When** 数据超过屏幕宽度, **Then** 系统适配终端宽度自动调整显示格式
3. **Given** 无历史数据, **When** 用户首次查询, **Then** 提示开始记录并建议稍后再查看

---

### User Story 4 - Usage Alerts and Notifications (Priority: P3)

用户希望在接近使用限额时收到提醒,避免超出配额。

Users want to receive alerts when approaching usage limits to avoid exceeding quota.

**Why this priority**: 这是锦上添花的功能。基本的监控(P1)和历史(P2)更重要。

This is a nice-to-have feature. Basic monitoring (P1) and history (P2) are more important.

**Independent Test**: 当使用量达到设定阈值(如80%)时,系统发送通知或在下次运行时显示警告。

When usage reaches a set threshold (e.g., 80%), the system sends a notification or displays a warning on next run.

**Acceptance Scenarios**:

1. **Given** 用户设置了80%的警告阈值, **When** 使用量超过阈值, **Then** 下次运行命令时显示醒目警告
2. **Given** 用户配置了通知, **When** 达到警告条件, **Then** 系统通过系统通知机制提醒用户
3. **Given** 使用量恢复正常, **When** 新的计费周期开始, **Then** 警告状态自动重置

---

### Edge Cases

- **网络故障**: 当无法连接到 Claude API 时,如何处理?应提供清晰的错误信息和重试建议。
- **认证失效**: Session cookies 过期时如何检测和提示?需要友好的重新认证流程。
- **数据格式变化**: Claude 官网 API 返回格式变化时如何兼容?需要错误处理和版本检测。
- **并发请求**: 多个终端同时运行工具时,凭据存储是否安全?需要文件锁机制。
- **跨平台路径**: Windows、macOS、Linux 的配置文件存储路径如何统一管理?
- **大数据量**: 历史记录过多时如何分页或限制显示?需要合理的数据清理策略。
- **时区处理**: 不同地区用户的时间显示如何处理?应使用本地时区。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统必须能够从 Claude 官网 (https://claude.ai/settings/usage) 获取使用量数据
- **FR-002**: 系统必须支持通过命令行参数或配置文件提供认证凭据
- **FR-003**: 系统必须能够解析 Claude 使用量页面的异步请求,提取实际用量数据
- **FR-004**: 用户必须能够通过单个命令查看当前计费周期的使用情况
- **FR-005**: 系统必须显示以下使用量指标:输入 tokens、输出 tokens、总消息数、使用百分比
- **FR-006**: 系统必须以表格形式展示使用量数据,包含清晰的列标题和对齐
- **FR-007**: 系统必须提供认证配置命令,引导用户输入和存储凭据
- **FR-008**: 系统必须安全存储认证凭据(加密或使用系统密钥链)
- **FR-009**: 系统必须提供清除/登出功能,删除本地存储的凭据
- **FR-010**: 系统必须验证认证凭据的有效性,并在失效时提示用户
- **FR-011**: 系统必须支持查询历史使用记录(可选时间范围参数)
- **FR-012**: 系统必须能够本地存储使用量快照用于历史趋势分析
- **FR-013**: 系统必须支持配置使用量警告阈值(如 80%, 90%)
- **FR-014**: 系统必须在使用量超过阈值时显示警告信息
- **FR-015**: 系统必须提供 `--json` 输出格式选项,支持脚本集成

### Constitution-Mandated Requirements

The following requirements are mandated by the [Claude Pulse Constitution](../../.specify/memory/constitution.md):

**User Experience**:
- **FR-UX-001**: CLI 必须提供 `--help` 参数,显示所有命令和选项的详细说明
- **FR-UX-002**: 错误消息必须包含可操作的指导(如"请运行 `claude-pulse auth login` 配置认证")
- **FR-UX-003**: 数据获取操作必须显示进度指示器(如 "正在获取使用量数据...")
- **FR-UX-004**: 交互式配置必须提供合理的默认值和清晰的提示

**Visual Excellence**:
- **FR-VIS-001**: 输出必须使用一致的颜色:错误(红色)、警告(黄色)、成功(绿色)、信息(蓝色)
- **FR-VIS-002**: CLI 必须支持 `--no-color` 参数用于纯文本输出
- **FR-VIS-003**: 表格和列表必须正确对齐,使用 Unicode 边框字符美化显示

**Cross-Platform**:
- **FR-CP-001**: 程序必须在 Linux、macOS 和 Windows 上正常工作
- **FR-CP-002**: 配置文件路径必须使用平台无关的处理方式
- **FR-CP-003**: 行尾符必须根据平台正确处理

**Robustness**:
- **FR-ROB-001**: 所有用户输入(认证凭据、阈值等)必须在处理前验证
- **FR-ROB-002**: 程序必须优雅处理 Ctrl+C 中断
- **FR-ROB-003**: 错误必须记录到日志文件,包含足够的调试上下文
- **FR-ROB-004**: 凭据存储必须使用原子写入,防止数据损坏

### Key Entities

- **Usage Data**: 使用量数据实体,包含以下属性:
  - 计费周期(billing period)
  - 输入 tokens 数量和配额
  - 输出 tokens 数量和配额
  - 消息总数和配额
  - 使用百分比
  - 重置日期

- **Authentication Credential**: 认证凭据实体,包含:
  - 认证类型(session cookie 或 API key)
  - 凭据值(加密存储)
  - 过期时间
  - 上次验证时间

- **Usage Snapshot**: 使用量快照实体,用于历史记录:
  - 快照时间戳
  - 使用量数据(引用 Usage Data)
  - 数据来源(manual/automatic)

- **Alert Configuration**: 告警配置实体:
  - 阈值百分比
  - 告警类型(warning/critical)
  - 是否启用系统通知

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户能够在 5 秒内获取并查看当前使用量数据(90% 的情况下)
- **SC-002**: 首次配置认证的用户能够在 2 分钟内完成设置并成功获取数据
- **SC-003**: 工具在 Linux、macOS 和 Windows 三个平台上的功能表现一致,无平台特定错误
- **SC-004**: 用户在使用量接近限额(80%)时能够及时收到警告,避免意外超额
- **SC-005**: 95% 的常见错误场景(网络故障、认证失效等)都有清晰的错误提示和解决建议
- **SC-006**: 历史使用量数据能够准确记录并在查询时在 3 秒内显示
- **SC-007**: 工具的命令和参数命名直观易懂,80% 的用户无需查看文档即可完成基本操作
- **SC-008**: 认证凭据存储安全,通过基本的安全审计(无明文存储、正确的文件权限)

### Assumptions

以下假设用于填补需求中的未明确部分:

1. **认证方式**: 假设使用 session cookie 作为主要认证方式,因为用户描述提到"从官网获取数据",这暗示需要模拟浏览器会话。

2. **数据更新频率**: 假设使用量数据每次运行时实时获取,不做缓存(除非用于历史记录)。

3. **配置存储位置**:
   - Linux/macOS: `~/.config/claude-pulse/`
   - Windows: `%APPDATA%\claude-pulse\`

4. **默认警告阈值**: 默认在使用量达到 80% 时发出警告。

5. **历史数据保留**: 默认保留最近 30 天的快照数据。

6. **输出格式**: 默认使用彩色表格输出,可通过参数切换为 JSON 或纯文本。

7. **API 端点**: 假设 Claude 官网的异步请求端点为 `/api/organizations/{org_id}/usage` 或类似路径(需要在实现阶段通过浏览器开发者工具确认)。

