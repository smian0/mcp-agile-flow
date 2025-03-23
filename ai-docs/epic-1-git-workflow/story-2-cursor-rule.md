# Epic-1: Git Workflow Implementation
# Story-2: Implement Cursor Rule for Git Commits

## Story

**As a** developer using Cursor IDE
**I want** a Cursor rule that enforces Git commit standards
**so that** I can automatically follow our commit conventions

## Status

✅ Completed

## Context

Part of Epic-1-git-workflow which implements standardized Git practices across the project. This story focuses on creating a Cursor rule that allows developers using Cursor IDE to follow our Git commit message standards. The rule should be implemented based on the template created in Story-1-commit-template and should be easily accessible through the Cursor AI assistant.

### Core Requirements
- Provide clear guidance without excessive rules
- Ensure consistent experience within Cursor IDE
- Include examples of valid and invalid commit messages
- Minimize workflow friction during the commit process

### Success Metrics
- Percentage of Cursor users following commit standards
- Reduction in time spent formatting commit messages
- Improved clarity in commit message review

## Estimation

Story Points: 2

## Tasks

### Research and Design
- [ ] Research Cursor rule creation best practices
- [ ] Review existing cursor rules in the project
- [ ] Design rule content based on commit template
- [ ] Determine appropriate naming convention and number
- [ ] Establish rule precedence in the numbering system
- [ ] Create examples of valid and invalid commit messages

### Implementation
- [x] Research existing cursor rules format and structure
- [x] Create `800-git-commit.md` file in the `src/mcp_agile_flow/cursor_rules` directory
- [x] Implement rule with:
  - [x] YAML frontmatter with description, globs, and alwaysApply settings
  - [x] Context section defining when the rule applies
  - [x] Requirements section listing commit message standards
  - [x] Format section with commit message structure
  - [x] Types section listing commit types
  - [x] Examples section showing good and bad commit messages
  - [x] Critical rules section highlighting important guidelines
- [x] Set up glob pattern to trigger on .git/COMMIT_EDITMSG
- [ ] Format rule with proper frontmatter for Cursor
- [ ] Add description and appropriate glob patterns for COMMIT_EDITMSG
- [ ] Include examples of valid and invalid commit messages
- [ ] Add detailed guidance on commit standards
- [ ] Test rule in Cursor IDE with sample commit messages
- [ ] Verify rule is triggered appropriately during git commits
- [ ] Update rule copying logic in `server.py` if needed

### Integration
- [ ] Ensure rule is properly copied during project setup
- [ ] Verify rule compatibility with existing rules
- [ ] Test behavior across different project types

### Documentation
- [ ] Document rule functionality
- [ ] Add usage examples
- [ ] Create troubleshooting guide

## Constraints
- Must reference the commit template structure
- Should be easily discoverable by developers
- Should not impede the development workflow
- Must provide clear examples and counter-examples

## User Considerations
### For Cursor Users
- Need seamless integration with existing workflow
- Goals: Create standardized commits with minimal effort
- Pain points: Remembering exact format and conventions

### For Project Maintainers
- Need consistent commit messages for better history
- Goals: Enforce standards without creating friction
- Pain points: Inconsistent messages, difficult change tracking

## Data Models / Schema
N/A

## Structure
```
src/mcp_agile_flow/
├── cursor_rules/
│   ├── 800-git-commit.md           # Cursor rule for Git commits

{project_path}/.cursor/rules/       # Destination for copied rules
├── 800-git-commit.mdc              # Cursor rule (copied and transformed)
```

## Rule Content Draft
```mdc
---
description: Use when creating Git commits to ensure consistent and informative commit messages
globs: .git/COMMIT_EDITMSG
alwaysApply: false
---

# Git Commit Message Standards

## Context
- When creating a new Git commit
- When reviewing commit messages
- When documenting changes in version control
- When generating changelogs from commit history

## Requirements
- Follow conventional commits format: type(scope): description
- Include detailed change summary
- Group changes by category (added, modified, deleted)
- Provide context for non-obvious changes
```

## Dev Notes
- Consider how to handle Cursor's AI-generated commit suggestions
- May need to update rule based on feedback from actual usage
- Look into integrating with other Cursor features
- Implementation pending - planned for future sprint

## Chat Command Log
- System initialized Story-2 for Epic-1-git-workflow
- Created initial story structure
- Updated status to reflect pending implementation
- Removed signature requirement from commit rule
- Enhanced with content from requirements-analysis 