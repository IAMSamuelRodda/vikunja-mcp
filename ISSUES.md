# Vikunja MCP Server - Issues & Flagged Items

This document tracks flagged items, required spikes, risks, and blockers identified during blueprint planning.

---

## Active Bugs

### BUG-001: Lazy-MCP Reports Incorrect Tool Count (27 actual vs 23 reported)

**Status**: 🔴 Open
**Priority**: P2 - Medium
**Discovered**: 2025-12-17
**Affects**: Tool accessibility via lazy-mcp proxy

**Description:**
When this Vikunja MCP server is accessed through the lazy-mcp-proxy, the hierarchy system incorrectly reports 23 tools instead of the actual 27 tools registered by the server.

**Evidence:**
- Server correctly registers 27 tools (verified via `FastMCP.list_tools()`)
- All 27 tools defined with `@mcp.tool` decorators in `src/server.py`
- Lazy-mcp hierarchy reports "vikunja: 23 tools"
- Systematic review of 10 other MCP servers shows NO similar discrepancy
- Issue is specific to vikunja-mcp, not a systemic lazy-mcp bug

**Missing Tools (4):**
Need to identify which 4 of the 27 tools are not being discovered by lazy-mcp.

**All 27 Tools (Verified in Server):**
```
vikunja_add_label_to_task, vikunja_add_reminder, vikunja_assign_task,
vikunja_create_label, vikunja_create_project, vikunja_create_relation,
vikunja_create_task, vikunja_delete_label, vikunja_delete_project,
vikunja_delete_relation, vikunja_delete_reminder, vikunja_delete_task,
vikunja_get_project_tasks, vikunja_get_relations, vikunja_get_task,
vikunja_get_tasks_by_label, vikunja_get_team_members, vikunja_list_labels,
vikunja_list_projects, vikunja_list_reminders, vikunja_list_tasks,
vikunja_list_teams, vikunja_move_task_to_project, vikunja_remove_label_from_task,
vikunja_share_project, vikunja_update_project, vikunja_update_task
```

**Impact:**
- 4 tools may be inaccessible via lazy-mcp proxy
- Inaccurate tool count in hierarchy overview
- Potential "tool not found" errors for missing tools

**Root Cause Hypotheses:**
1. Tool name length/pattern unique to these 4 tools
2. Tool description or parameter complexity triggers discovery filter
3. Specific tool decorator pattern not recognized by lazy-mcp
4. Timeout during discovery fetches only first 23 tools alphabetically

**Investigation Steps:**
1. Query lazy-mcp to list all vikunja tools it knows about
2. Compare against all 27 to identify which 4 are missing
3. Analyze common patterns in missing tools (name, params, description)
4. Test if issue persists with direct MCP protocol connection (bypass lazy-mcp)

**Workaround:**
Use direct MCP connection to vikunja server (not through lazy-mcp proxy) until resolved.

**Related:**
- vikunja-mcp server: `/home/x-forge/.claude/mcp-servers/vikunja/src/server.py`
- MCP Server Review: `/home/x-forge/repos/2-areas/lazy-mcp-preload/MCP_SERVER_REVIEW.md`

---

## Flagged Items Requiring Attention

### High-Complexity Items (>3.0)

#### 1. Feature 6.1: Attachment Operations (Complexity: 3.2)

**Status**: ⚠️ Needs Decomposition
**Reason**: High technical complexity (4) for multipart upload handling and high uncertainty (4) around binary data streaming in MCP context
**Action Required**: Complete spike task 6.1.1 before attempting implementation

**Subtasks**:
- Task 6.1.1: Research MCP file/binary data handling (3.0, uncertainty 4) - **SPIKE REQUIRED**
- Task 6.1.2: Implement upload_attachment (3.5) - **HIGH COMPLEXITY**
- Task 6.1.3: Implement list/delete attachments (2.5)

**Spike Suggestion**: Create `BLUEPRINT-spike-mcp-file-handling-20251216.yaml`

---

#### 2. Task 6.1.1: Research MCP File/Binary Data Handling (Complexity: 3.0, Uncertainty: 4)

**Status**: ⚠️ Spike Required
**Type**: Research/Investigation
**Time-box**: 1 day
**Reason**: Unclear how to handle file uploads in MCP tool context - need to verify SDK capabilities

**Investigation Questions**:
1. Does the MCP Python SDK support binary data in tool responses?
2. What's the recommended pattern for file uploads (base64, streaming, external storage)?
3. Are there existing MCP servers with file handling we can reference?
4. What are the token limits for binary data in MCP responses?
5. Should attachments be downloaded to local disk or returned as data URIs?

**Deliverables**:
- Research report documenting MCP file handling patterns
- Decision on implementation approach (base64, URLs, external storage)
- POC demonstrating feasibility with small file upload/download
- Updated complexity scores for Task 6.1.2 and 6.1.3

**Success Criteria**:
- Uncertainty reduced from 4 → 2 or lower
- Clear implementation path for upload_attachment tool
- Technical feasibility validated

---

#### 3. Task 6.1.2: Implement Upload Attachment (Complexity: 3.5)

**Status**: ⚠️ High Complexity, Blocked by 6.1.1
**Reason**: Multipart/form-data handling, binary data streaming, token limits
**Action Required**: Wait for spike 6.1.1 completion, may need further decomposition

**Potential Decomposition** (after spike):
- Subtask: Implement file validation and size limits
- Subtask: Handle multipart upload to Vikunja API
- Subtask: Return attachment metadata to LLM
- Subtask: Error handling for upload failures

---

#### 4. Task 7.1.4: Circular Dependency Prevention Tests (Complexity: 3.2)

**Status**: ⚠️ High Complexity
**Reason**: Testing graph traversal, edge case coverage
**Action**: May benefit from decomposition during implementation if proving difficult

**Considerations**:
- Need to test various circular patterns (direct, indirect, chain)
- Graph traversal algorithm testing
- Performance testing with large relationship graphs

---

#### 5. Task 9.1.2: Create 10+ Complex Evaluation Questions (Complexity: 3.2)

**Status**: ⚠️ High Complexity
**Reason**: Requires understanding full API surface, designing comprehensive scenarios
**Action**: May need breakdown into evaluation categories during implementation

**Potential Categories**:
- Basic CRUD operations (tasks, projects)
- Advanced filtering and search
- Multi-step workflows (create task → add labels → set reminder)
- Error handling scenarios
- Edge cases (empty results, invalid IDs, rate limits)

---

#### 6. Task 9.2.2: Integration Test Workflows (Complexity: 3.2)

**Status**: ⚠️ High Complexity
**Reason**: Requires test Vikunja instance, multiple tool orchestration, state management
**Action**: Consider decomposition by workflow type

**Potential Workflows**:
- Complete task lifecycle (create → update → complete → delete)
- Project organization (create project → add tasks → apply labels)
- Team collaboration (share project → assign tasks)
- Attachment workflow (if implemented)
- Relationship management (parent-child tasks)

---

## At-Threshold Items (=3.0) - Marked Manageable

These items are at the 3.0 complexity threshold but deemed manageable. Monitor during implementation:

| ID | Task | Complexity | Note |
|----|------|------------|------|
| Task 2.2.2 | list_tasks with filtering | 3.0 | Straightforward query parameter logic |
| Task 4.2.1 | Label filtering AND/OR | 3.0 | Query parameter combination logic |
| Feature 9.1 | Evaluation scenario creation | 3.0 | Parent of 9.1.2 |
| Task 9.1.3 | Manual verification | 3.0 | Time-consuming but not technically complex |

---

## Risk Register

### R1: Vikunja API Version Compatibility
- **Impact**: Medium
- **Probability**: Low
- **Mitigation**: Target v0.24.0+ as baseline, document version requirements, version-check on initialization

### R2: File Attachment Handling Complexity (🔴 HIGH PRIORITY)
- **Impact**: High
- **Probability**: Medium
- **Mitigation**: **Spike task 6.1.1 created** - research MCP file handling patterns before implementation
- **Status**: ⚠️ Blocking Feature 6.1

### R3: Rate Limiting on Vikunja API
- **Impact**: Medium
- **Probability**: Medium
- **Mitigation**: Implement exponential backoff in client, rate limit detection, clear error messages

### R4: Large Dataset Responses Exceeding Character Limits
- **Impact**: Medium
- **Probability**: High
- **Mitigation**: 25k token limit enforced in utils, mandatory pagination for list operations, concise format option

### R5: Circular Task Dependency Creation
- **Impact**: High
- **Probability**: Low
- **Mitigation**: Dedicated test (Task 7.1.4), validate relationship graph before creation

---

## Dependencies & Blockers

### External Dependencies
- **Vikunja Instance**: do-vps-prod (accessible via HTTPS)
- **Authentication**: Bearer token for samuel@arcforge.au
- **API Version**: v0.24.0+ required

### Internal Dependencies
- VikunjiaClient must be completed before tool development (Epic 1 → Epic 2+)
- Response formatters needed for all list/get operations (Feature 1.3 → Epic 2+)
- Spike 6.1.1 must complete before Feature 6.1 implementation

---

## Spike Tasks Required

### 1. MCP File Handling Research (Task 6.1.1)
- **Blueprint**: `BLUEPRINT-spike-mcp-file-handling-20251216.yaml` (not yet created)
- **Time-box**: 1 day
- **Blocks**: Feature 6.1 (all attachment operations)
- **Priority**: Medium (only needed for Milestone 3)

**Action**: Create spike blueprint when approaching Milestone 3

---

## Configuration Notes

### Vikunja Instance Details
- **Instance**: do-vps-prod
- **URL**: (to be configured in .env)
- **Authentication Method**: Bearer token
- **User Account**: samuel@arcforge.au
- **API Version**: v0.24.0+

### Security Considerations
- Use `saving-secrets` or `using-openbao` skill for token management
- Never commit VIKUNJA_TOKEN to version control
- Store in .env (local) or OpenBao (production)

---

## Next Actions

1. ✅ Blueprint created and assessed
2. ✅ Tracking documents created (PROGRESS.md, ISSUES.md)
3. 🔴 Begin implementation with Milestone 1, Epic 1
4. 🔴 Create spike blueprint for MCP file handling before Milestone 3
5. 🔴 Monitor at-threshold items (2.2.2, 4.2.1, 9.1.3) during implementation
6. 🔴 Decompose high-complexity items (6.1.2, 7.1.4, 9.1.2, 9.2.2) if needed during implementation

---

**Last Updated**: 2025-12-16
**Blueprint**: `specs/archive/BLUEPRINT-project-vikunja-mcp-20251216.yaml` (to be archived)
