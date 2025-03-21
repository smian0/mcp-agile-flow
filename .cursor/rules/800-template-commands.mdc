---
description: Use when processing template-related commands to create or manage project artifacts
globs: 
alwaysApply: true
---

# Template Command Handling

## Context
- When user requests creation of a project document
- When user requests updating a project document
- When user requests status changes in documents
- When working with agile workflow artifacts

## Requirements
- Recognize and process template-related commands
- Create documents in the correct location (ai-docs directory)
- Apply the appropriate template from .ai-templates directory
- Maintain proper file structure
- Ensure consistent document formatting
- Track document status appropriately
- Ensure output is identical regardless of which IDE is used

## Document Flow Process

1. **Templates Source**: All document templates are stored in the IDE-agnostic `.ai-templates` directory
2. **Output Location**: All AI-produced documents are stored in the `ai-docs` directory
3. **Cross-IDE Consistency**: The exact same document generation process is used across all IDEs
4. **Available Templates**:
   - `template-brd.md`: Business Requirements Document template
   - `template-prd.md`: Product Requirements Document template
   - `template-arch.md`: Architecture Document template
   - `template-story.md`: User Story template
   - `template-epic-summary.md`: Epic Summary template
5. **Document Structure**: Follow the hierarchical structure defined below for all generated documents

## Command Processing

### Document Creation Commands

#### BRD Commands
- "Create a new BRD for {project-name}"
- "Initialize BRD for {project-name}"
- "Generate Business Requirements Document for {project-name}"

#### PRD Commands
- "Create a new PRD for {project-name}"
- "Initialize PRD for {project-name}"
- "Generate Product Requirements Document for {project-name}"

#### Architecture Commands
- "Create architecture document for {project}"
- "Initialize architecture for {project}"
- "Generate technical architecture for {project}"

#### Epic Summary Commands
- "Create epic summary for Epic-{N}-{epic-suffix}"
- "Initialize epic summary for Epic-{N}-{epic-suffix} with title {epic-title}"
- "Generate epic overview for Epic-{N}-{epic-suffix}"

#### Story Commands
- "Create a story for Epic-{N}-{epic-suffix}"
- "Add story to Epic-{N}-{epic-suffix}: {story-title} with suffix {story-suffix}"
- "Generate user story for {epic-name} with suffix {story-suffix}"

### Document Update Commands

#### Status Updates
- "Update {document-type} status to {status}"
- "Mark {document-type} as {status}"
- "Change {document-type} status to {status}"

#### Content Updates
- "Add business objective {objective} to BRD"
- "Add market problem {problem} to BRD"
- "Add success metric {metric} to BRD"
- "Add Epic {epic-title} to PRD"
- "Add technology {technology} to architecture"
- "Mark task {task} as complete in story {story-id}"
- "Add task {task} to story {story-id}"

#### Epic Summary Updates
- "Update epic summary status to {status} for Epic-{N}-{epic-suffix}"
- "Add objective {objective} to Epic-{N}-{epic-suffix}"
- "Update epic description for Epic-{N}-{epic-suffix}: {description}"
- "Refresh stories list for Epic-{N}-{epic-suffix}"
- "Add technical consideration {consideration} to Epic-{N}-{epic-suffix}"
- "Set acceptance criteria for Epic-{N}-{epic-suffix}: {criteria}"
- "Add dependency {dependency} to Epic-{N}-{epic-suffix}"

### Progress Tracking Commands

#### Story Progress Updates
- "Update story progress": Refreshes status, tasks, and chat log for current story
- "Track implementation notes for {story}": Adds implementation details to Dev Notes
- "Document commands for story {story}": Updates Chat Command Log with recent interactions
- "Verify task completion for {task}": Checks if tests pass before marking as complete

#### Progress Reporting
- "Generate progress report": Creates a summary of work completed across stories
- "Summarize epic progress": Shows completion status for all stories in an epic
- "Show current blockers": Lists incomplete tasks that are blocking progress
- "Create sprint summary": Summarizes all work completed in current sprint

## Directory Structure

```
.ai-templates/                 # Source templates directory (not visible to user)
├── template-brd.md           # BRD template
├── template-prd.md           # PRD template
├── template-arch.md          # Architecture template
├── template-story.md         # Story template
└── template-epic-summary.md  # Epic Summary template

ai-docs/                      # Output documents directory (visible to user)
├── brd.md                    # Business Requirements Document
├── prd.md                    # Product Requirements Document
├── arch.md                   # Architecture Document
├── epic-1-user-auth/         # Epic directory with descriptive suffix
│   ├── epic-summary.md         # Epic Summary file
│   ├── story-1-login-flow.md   # Story files with descriptive suffixes
│   ├── story-2-signup-form.md
│   └── ...
├── epic-2-task-core/         # Another epic with descriptive suffix
│   ├── epic-summary.md         # Epic Summary file
│   └── ...
└── ...
```

## Examples
<example>
User: "Create a new BRD for TaskMaster App"

AI Action:
1. Identify template to use: `.ai-templates/template-brd.md`
2. Create `ai-docs` directory if it doesn't exist
3. Create `brd.md` file in `ai-docs` directory using the template
4. Add project-specific details
5. Confirm creation with: "Created Business Requirements Document for TaskMaster App in `ai-docs/brd.md`"

User: "Create a new PRD for TaskMaster App"

AI Action:
1. Identify template to use: `.ai-templates/template-prd.md`
2. Create `ai-docs` directory if it doesn't exist
3. Create `prd.md` file in `ai-docs` directory using the template
4. Add project-specific details
5. Confirm creation with: "Created Product Requirements Document for TaskMaster App in `ai-docs/prd.md`"

User: "Create a story for Epic-1-user-auth: User Authentication with suffix login-flow"

AI Action:
1. Identify template to use: `.ai-templates/template-story.md`
2. Verify PRD exists in `ai-docs/prd.md`
3. Create `ai-docs/epic-1-user-auth` directory if it doesn't exist
4. Create `story-1-login-flow.md` file in `ai-docs/epic-1-user-auth` directory using the template
5. Add story-specific details
6. Confirm creation with: "Created Story-1-login-flow for Epic-1-user-auth: User Authentication in `ai-docs/epic-1-user-auth/story-1-login-flow.md`"

User: "Create epic summary for Epic-1-user-auth with title User Authentication System"

AI Action:
1. Identify template to use: `.ai-templates/template-epic-summary.md`
2. Verify that the epic directory exists: `ai-docs/epic-1-user-auth`
3. Create `epic-summary.md` file in `ai-docs/epic-1-user-auth` directory using the template
4. Replace placeholders with provided information:
   - {N} → 1
   - {epic-title} → User Authentication System
   - {status} → Planning (default)
   - Other placeholders with default values
5. Confirm creation with: "Created Epic Summary for Epic-1-user-auth in `ai-docs/epic-1-user-auth/epic-summary.md`"

User: "Refresh stories list for Epic-1-user-auth"

AI Action:
1. Scan the `ai-docs/epic-1-user-auth` directory for story files
2. For each story file:
   - Extract story title and status
   - Create a link to the story file
3. Update the Stories section in `epic-summary.md` with the formatted list
4. Confirm update with: "Updated stories list in Epic Summary for Epic-1-user-auth"
</example>

<example type="invalid">
User: "Make me a project document"

AI Action:
Creates a generic document without following the template structure or putting it in the right location.

User: "Add a new story"

AI Action:
Creates a story file but doesn't link it to an epic or follow the proper format.
</example>

## Critical Rules
- Process must be identical across all supported IDEs (Cursor, Windsurf, Cline, Copilot)
- Templates must always be sourced from the .ai-templates directory
- Documents must always be created in the ai-docs directory
- Templates must be applied consistently
- References between documents must be maintained
- Status progression must be enforced
- File naming must follow the established conventions
- Always confirm successful command execution 
- When creating a new epic, automatically create an epic summary file
- When creating/updating stories, refresh the epic summary's stories list
- Epic summaries must accurately reflect the current state of all stories 