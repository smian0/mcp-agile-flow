# Epic-1: Git Workflow Implementation
# Story-1: Create Git Commit Message Template

## Story

**As a** developer
**I want** a standardized Git commit message template
**so that** I can create consistent, informative commit messages

## Status

✅ Completed

## Context

Part of Epic-1-git-workflow which implements standardized Git practices across the project. This story focuses on creating the core commit message template that will be used as the foundation for the entire workflow. The template needs to follow conventional commits standards while incorporating the specific requirements identified in the existing template.

### Core Requirements
- Follow conventional commits format: `type(scope): description`
- Include detailed change summaries with modified/added/deleted files
- Maximum subject line length of 72 characters
- Clear separation between subject and body with blank line
- Detailed body content for complex changes
- Support for GitHub and GitLab specific references
- Compatibility with CI/CD systems in both platforms

### Success Metrics
- Percentage of commits following standard format
- Reduction in commit message issues in code reviews
- Time spent on commit message formatting

## Estimation

Story Points: 1
Planned Sprint: TBD

## Tasks

### Research and Design
- [x] Research conventional commit standards
- [ ] Review existing `git-push-command.md` template
- [ ] Research GitHub and GitLab specific commit conventions
- [ ] Define commit types appropriate for our project
- [ ] Design template format with required sections

### Implementation
- [x] Create `template-git-commit.md` file in the `src/mcp_agile_flow/ai-templates` directory
- [x] Define template structure including:
  - [x] Header with requirements and context
  - [x] Format section with commit message structure
  - [x] Types section listing commit types (feat, fix, etc.)
  - [x] Examples section showing proper and improper commit messages
  - [x] Critical rules section
- [x] Ensure template includes support for both GitHub and GitLab issue references
- [x] Document integration with CI/CD processes

### Configuration
- [ ] Update template copying logic in the server initialization code
- [ ] Test template deployment across different IDEs
- [ ] Document how to override the template
- [ ] Create setup script for new developers

### Documentation
- [ ] Create basic usage documentation
- [ ] Add examples of good commit messages
- [ ] Document commit types and their meanings
- [ ] Explain how to handle edge cases
- [ ] Include platform-specific sections for GitHub and GitLab
- [ ] Document issue/MR/PR linking conventions

## Constraints
- Must follow conventional commits standard
- Should be easy to use without extensive training
- Must not significantly slow down the development process
- Must work with Git's native capabilities
- Should accommodate rapid iteration cycles

## User Considerations
### For Team Members
- Needs clear guidance without excessive rules
- Goals: Make consistent commits without slowing down development
- Pain points: Complex rules, lack of examples

### For New Developers
- Needs simple onboarding and clear documentation
- Goals: Quickly adopt team practices without errors
- Pain points: Implicit knowledge, complex setup processes

## Data Models / Schema
N/A

## Structure
```
src/mcp_agile_flow/
├── ai-templates/
│   ├── template-git-commit.md       # Git commit template source

.ai-templates/                       # Destination for copied templates
├── template-git-commit.md           # Copied Git commit template

.git/
├── hooks/                           # Git hooks directory for local template usage
```

## Dev Notes
- Consider how to handle merge commits
- Look at how companies like Angular and Google structure their commit messages
- Evaluate different formats for the change summary section
- Implementation pending - planned for future sprint
- GitLab uses `#123` for issue references and `!123` for merge requests
- GitHub uses `#123` for PRs and issues, with additional keywords like `fixes`, `closes`, etc.
- Both platforms support `[skip ci]` directives, but may have different variations

## Chat Command Log
- System initialized Story-1 for Epic-1-git-workflow
- Created initial story structure
- Updated status to reflect pending implementation
- Removed signature requirement from commit template
- Enhanced with content from requirements-analysis
- Updated to include GitLab and GitHub specific requirements 