# Vikunja MCP Server - Progress Tracker

**Project**: Python-based MCP server for Vikunja task management integration
**Architecture**: Layered (client/, tools/, schemas/, utils/)
**Workflow**: Simple (main branch only, worktrees for parallel work)
**Tracking**: Document-based (this file + ISSUES.md)

**Vikunja Instance**: do-vps-prod
**Authentication**: Bearer token for samuel@arcforge.au

---

## Legend

- 🔴 Not Started
- 🟡 In Progress
- 🟢 Completed
- ⚠️ Blocked/Flagged

---

## Milestone 1: v0.1.0 - Foundation & Core Task Management (2-3 weeks)

### Epic 1: Project Setup & Infrastructure

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 1.1** | **Project scaffolding and dependency setup** | 1.8 | 🔴 |
| Task 1.1.1 | Create project directory structure (src/, tests/, evaluations/) | 1.3 | 🔴 |
| Task 1.1.2 | Initialize requirements.txt with mcp, httpx, pydantic | 1.5 | 🔴 |
| Task 1.1.3 | Create .env.example with VIKUNJA_URL and VIKUNJA_TOKEN | 1.3 | 🔴 |
| Task 1.1.4 | Initialize README.md with project description | 1.5 | 🔴 |
| **Feature 1.2** | **Vikunja API client foundation** | 2.5 | 🔴 |
| Task 1.2.1 | Implement VikunjiaClient class with httpx async client | 2.3 | 🔴 |
| Task 1.2.2 | Add bearer token authentication headers | 1.8 | 🔴 |
| Task 1.2.3 | Create base request method with error handling and rate limiting | 2.8 | 🔴 |
| Task 1.2.4 | Add unit tests for client initialization and auth | 2.3 | 🔴 |
| **Feature 1.3** | **Shared utilities and formatters** | 2.2 | 🔴 |
| Task 1.3.1 | Create response formatters for JSON and Markdown output | 2.5 | 🔴 |
| Task 1.3.2 | Implement pagination helper with page/limit parameters | 2.0 | 🔴 |
| Task 1.3.3 | Build error handler with LLM-friendly messages | 2.3 | 🔴 |
| Task 1.3.4 | Add character limit enforcement (25k tokens) | 2.0 | 🔴 |

### Epic 2: Core Task Management Tools

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 2.1** | **Task creation tool** | 2.8 | 🔴 |
| Task 2.1.1 | Define Pydantic schema for task creation | 2.3 | 🔴 |
| Task 2.1.2 | Implement create_task tool with POST endpoint | 2.8 | 🔴 |
| Task 2.1.3 | Add comprehensive tool description with examples | 2.0 | 🔴 |
| Task 2.1.4 | Create unit tests for task creation | 2.5 | 🔴 |
| **Feature 2.2** | **Task retrieval and listing tools** | 2.5 | 🔴 |
| Task 2.2.1 | Implement get_task tool for single task by ID | 2.0 | 🔴 |
| Task 2.2.2 | Implement list_tasks with pagination and filtering | 3.0 | 🔴 |
| Task 2.2.3 | Add response format options (detailed vs concise) | 2.3 | 🔴 |
| **Feature 2.3** | **Task update and delete tools** | 2.3 | 🔴 |
| Task 2.3.1 | Implement update_task with PATCH support | 2.5 | 🔴 |
| Task 2.3.2 | Implement delete_task with confirmation pattern | 2.0 | 🔴 |
| Task 2.3.3 | Add destructiveHint and idempotentHint annotations | 1.8 | 🔴 |

---

## Milestone 2: v0.2.0 - Project & Label Management (2 weeks)

### Epic 3: Project/List Management

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 3.1** | **Project CRUD operations** | 2.5 | 🔴 |
| Task 3.1.1 | Define project schema with hierarchy support | 2.0 | 🔴 |
| Task 3.1.2 | Implement create_project and list_projects tools | 2.5 | 🔴 |
| Task 3.1.3 | Implement update_project and delete_project tools | 2.3 | 🔴 |
| Task 3.1.4 | Add tests for project hierarchy and nested structures | 2.8 | 🔴 |
| **Feature 3.2** | **Project-task relationship tools** | 2.2 | 🔴 |
| Task 3.2.1 | Implement get_project_tasks to list all tasks in project | 2.0 | 🔴 |
| Task 3.2.2 | Add move_task_to_project tool for relocating tasks | 2.5 | 🔴 |

### Epic 4: Label System

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 4.1** | **Label management tools** | 2.3 | 🔴 |
| Task 4.1.1 | Implement create_label with title, description, color | 2.0 | 🔴 |
| Task 4.1.2 | Implement list_labels and delete_label tools | 1.8 | 🔴 |
| Task 4.1.3 | Add label application tools (add/remove from task) | 2.5 | 🔴 |
| Task 4.1.4 | Create tests for label operations and edge cases | 2.5 | 🔴 |
| **Feature 4.2** | **Label-based filtering** | 2.8 | 🔴 |
| Task 4.2.1 | Extend list_tasks to support label filtering (AND/OR) | 3.0 | 🔴 |
| Task 4.2.2 | Add get_tasks_by_label convenience tool | 2.3 | 🔴 |

---

## Milestone 3: v0.3.0 - Advanced Features (3 weeks)

### Epic 5: Reminders & Notifications

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 5.1** | **Reminder management tools** | 2.7 | 🔴 |
| Task 5.1.1 | Define reminder schema with reminder_date and relative_to | 2.5 | 🔴 |
| Task 5.1.2 | Implement add_reminder_to_task with datetime validation | 2.8 | 🔴 |
| Task 5.1.3 | Implement list_reminders and delete_reminder tools | 2.3 | 🔴 |

### Epic 6: Attachments & Files

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 6.1** | **Attachment operations** | 3.2 | ⚠️ Flagged |
| Task 6.1.1 | Research MCP file/binary data handling patterns | 3.0 | ⚠️ Spike Required |
| Task 6.1.2 | Implement upload_attachment with multipart/form-data | 3.5 | ⚠️ High Complexity |
| Task 6.1.3 | Implement list_attachments and delete_attachment tools | 2.5 | 🔴 |

### Epic 7: Task Relationships

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 7.1** | **Relationship management tools** | 2.8 | 🔴 |
| Task 7.1.1 | Implement create_task_relation with relation_kind | 2.8 | 🔴 |
| Task 7.1.2 | Implement get_task_relations to view relationship graph | 2.5 | 🔴 |
| Task 7.1.3 | Implement delete_task_relation tool | 2.3 | 🔴 |
| Task 7.1.4 | Add tests for circular dependency prevention | 3.2 | ⚠️ High Complexity |

### Epic 8: Team Collaboration

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 8.1** | **Team and user tools** | 2.5 | 🔴 |
| Task 8.1.1 | Implement list_teams and get_team_members tools | 2.3 | 🔴 |
| Task 8.1.2 | Implement assign_task to assign users to tasks | 2.5 | 🔴 |
| Task 8.1.3 | Implement share_project with permission levels | 2.8 | 🔴 |

---

## Milestone 4: v1.0.0 - Testing, Documentation & Release (2 weeks)

### Epic 9: Evaluation & Testing

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 9.1** | **Evaluation scenario creation** | 3.0 | 🔴 |
| Task 9.1.1 | Explore Vikunja API with read-only tools | 2.5 | 🔴 |
| Task 9.1.2 | Create 10+ complex evaluation questions | 3.2 | ⚠️ High Complexity |
| Task 9.1.3 | Manually verify answers for each question | 3.0 | 🔴 |
| Task 9.1.4 | Format evaluations in XML and run harness | 2.5 | 🔴 |
| **Feature 9.2** | **Unit and integration testing** | 2.8 | 🔴 |
| Task 9.2.1 | Write unit tests for all client methods | 2.8 | 🔴 |
| Task 9.2.2 | Write integration tests for tool workflows | 3.2 | ⚠️ High Complexity |
| Task 9.2.3 | Achieve 90%+ code coverage and fix gaps | 2.5 | 🔴 |

### Epic 10: Documentation & Deployment

| ID | Task | Complexity | Status |
|----|------|------------|--------|
| **Feature 10.1** | **Comprehensive documentation** | 2.3 | 🔴 |
| Task 10.1.1 | Write README with setup and usage examples | 2.3 | 🔴 |
| Task 10.1.2 | Document all tool descriptions with parameter details | 2.0 | 🔴 |
| Task 10.1.3 | Create DEPLOYMENT.md with Claude Code and lazy-mcp | 2.5 | 🔴 |
| **Feature 10.2** | **Deployment configuration** | 2.0 | 🔴 |
| Task 10.2.1 | Create example ~/.claude.json configuration | 1.8 | 🔴 |
| Task 10.2.2 | Create lazy-mcp hierarchy file if targeting lazy-mcp | 2.3 | 🔴 |
| Task 10.2.3 | Test deployment in Claude Code and verify tools | 2.0 | 🔴 |

---

## Summary

- **Total Features**: 22
- **Total Tasks**: 60
- **Completed**: 0
- **In Progress**: 0
- **Not Started**: 56
- **Flagged**: 4

**Next Steps**:
1. Review ISSUES.md for flagged items requiring spikes or decomposition
2. Begin implementation with Milestone 1, Epic 1 (Project Setup)
3. Create spike blueprint for MCP file handling (Task 6.1.1)
