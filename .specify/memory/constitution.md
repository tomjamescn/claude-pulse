<!--
Sync Impact Report:
- Version: N/A → 1.0.0
- Change Type: Initial constitution ratification
- Modified Principles: All principles are new
- Added Sections: All sections are new
- Templates Status:
  ✅ plan-template.md: Constitution Check section aligned
  ✅ spec-template.md: Requirements structure aligned
  ✅ tasks-template.md: Task categorization aligned
- Follow-up: None
-->

# Claude Pulse Constitution

## Core Principles

### I. Simplicity First (简单优先)

**English**: Every feature must start with the simplest possible implementation that delivers value.
Complexity must be justified before introduction. Follow YAGNI (You Aren't Gonna Need It) principles.
Prefer composition over inheritance. Avoid premature optimization.

**中文**: 每个功能必须从能够交付价值的最简单实现开始。引入复杂性之前必须证明其必要性。
遵循 YAGNI (你不会需要它) 原则。优先使用组合而非继承。避免过早优化。

**Rationale**: Simple code is easier to understand, test, maintain, and debug. Complexity should
only be added when there's a clear, documented need.

### II. User Experience Excellence (卓越用户体验)

**English**: Command-line interfaces must be intuitive and helpful:
- Clear, consistent command naming and arguments
- Helpful error messages with actionable guidance
- Interactive prompts with sensible defaults
- Comprehensive help documentation (--help)
- Progress indicators for long-running operations
- Graceful error handling with meaningful exit codes

**中文**: 命令行界面必须直观且有用:
- 清晰、一致的命令命名和参数
- 提供可操作指导的有用错误消息
- 带有合理默认值的交互式提示
- 全面的帮助文档 (--help)
- 长时间运行操作的进度指示器
- 优雅的错误处理和有意义的退出码

**Rationale**: Users should never feel lost or frustrated. Good UX reduces support burden and
increases adoption.

### III. Visual Excellence (视觉卓越)

**English**: Terminal output must be clean, readable, and aesthetically pleasing:
- Consistent use of colors for different message types (errors, warnings, success, info)
- Proper alignment and spacing in tables and lists
- Use Unicode box-drawing characters for visual structure
- Support both colored and plain text output (--no-color flag)
- Respect terminal width and handle text wrapping gracefully
- Use symbols and icons where appropriate (✓, ✗, ⚠, →)

**中文**: 终端输出必须整洁、可读且美观:
- 对不同消息类型(错误、警告、成功、信息)统一使用颜色
- 表格和列表中适当的对齐和间距
- 使用 Unicode 边框字符构建视觉结构
- 支持彩色和纯文本输出(--no-color 标志)
- 尊重终端宽度并优雅处理文本换行
- 在适当的地方使用符号和图标 (✓, ✗, ⚠, →)

**Rationale**: Beautiful terminal output improves user engagement and makes information easier to
parse quickly.

### IV. Cross-Platform Compatibility (跨平台兼容性)

**English**: Programs MUST work consistently across major platforms:
- Support Linux, macOS, and Windows
- Use platform-agnostic path handling (pathlib or equivalent)
- Handle platform-specific line endings correctly
- Test on all target platforms before release
- Document any platform-specific requirements or limitations
- Use platform detection only when absolutely necessary

**中文**: 程序必须在主要平台上一致工作:
- 支持 Linux、macOS 和 Windows
- 使用平台无关的路径处理(pathlib 或等效工具)
- 正确处理平台特定的行尾符
- 发布前在所有目标平台上测试
- 记录任何平台特定的要求或限制
- 仅在绝对必要时使用平台检测

**Rationale**: Users should have the same excellent experience regardless of their operating
system.

### V. Robustness & Reliability (健壮性与可靠性)

**English**: Programs must be stable and predictable:
- Validate all inputs before processing
- Handle edge cases and boundary conditions explicitly
- Never lose user data (use atomic writes, backups, confirmations)
- Provide clear rollback/undo mechanisms where applicable
- Log errors with sufficient context for debugging
- Exit gracefully under all conditions (including Ctrl+C)
- Include comprehensive test coverage (unit, integration, contract tests)

**中文**: 程序必须稳定且可预测:
- 处理前验证所有输入
- 明确处理边界情况和边界条件
- 永不丢失用户数据(使用原子写入、备份、确认)
- 在适用的地方提供清晰的回滚/撤销机制
- 记录错误时包含足够的调试上下文
- 在所有条件下优雅退出(包括 Ctrl+C)
- 包含全面的测试覆盖(单元、集成、契约测试)

**Rationale**: Users must trust the tool with their work. Data loss or unexpected crashes destroy
that trust.

## Development Standards

### Code Quality Requirements

- **Linting**: All code must pass configured linters without warnings
- **Formatting**: Consistent code formatting using automated tools (prettier, black, rustfmt, etc.)
- **Type Safety**: Use static typing where available (TypeScript, Python type hints, Rust types)
- **Documentation**: Public APIs must have clear docstrings/comments
- **Dependencies**: Minimize external dependencies; justify each addition
- **Security**: No hardcoded secrets, validate untrusted input, follow OWASP guidelines

### Testing Requirements

**Tests are MANDATORY for all features unless explicitly waived**:
- **Unit Tests**: Test individual functions and modules in isolation
- **Integration Tests**: Test component interactions and workflows
- **Contract Tests**: Verify API contracts and data schemas
- **Platform Tests**: Verify functionality on all supported platforms

Test requirements may be adjusted based on feature scope, but the default is comprehensive coverage.

### Documentation Requirements

- **README.md**: Clear project description, installation, quick start
- **CHANGELOG.md**: Semantic versioning with clear release notes
- **API Documentation**: Auto-generated where possible, manually maintained otherwise
- **User Guide**: For complex features, provide usage examples and tutorials
- **中英文双语**: Key documentation should be available in both Chinese and English

## Configuration & Extensibility

### Configuration Principles

- **Sensible Defaults**: Work out of the box without configuration
- **Environment Variables**: Support standard env vars (e.g., NO_COLOR, TERM)
- **Config Files**: Support standard formats (TOML, YAML, JSON)
- **CLI Overrides**: Command-line flags override config files override env vars
- **Config Discovery**: Check current dir, home dir, standard config locations

### Plugin/Extension Support

- Where beneficial, provide clean extension points
- Document extension APIs clearly
- Maintain backward compatibility in extension interfaces
- Version extension APIs separately from core

## Governance

### Amendment Process

1. Propose amendment with clear rationale and impact analysis
2. Review impact on existing templates and workflows
3. Update constitution and increment version appropriately
4. Update all dependent templates and documentation
5. Announce changes to team/users

### Version Semantics

- **MAJOR**: Breaking changes to core principles or governance
- **MINOR**: New principles added or substantial expansions
- **PATCH**: Clarifications, typos, non-semantic improvements

### Compliance

- All new features MUST comply with this constitution
- Deviations require explicit justification in planning documents
- Complexity violations must be documented in implementation plans
- Regular reviews ensure ongoing compliance

### Conflict Resolution

When principles appear to conflict:
1. **Simplicity** trumps features (do less, better)
2. **User Experience** guides implementation choices
3. **Robustness** cannot be sacrificed for speed
4. **Cross-Platform** is non-negotiable for core features
5. **Visual Excellence** enhances but doesn't block delivery

**Version**: 1.0.0 | **Ratified**: 2025-10-19 | **Last Amended**: 2025-10-19
