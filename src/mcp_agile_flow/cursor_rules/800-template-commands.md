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
- Create documents in the correct location
- Apply the appropriate template based on command
- Maintain proper file structure
- Ensure consistent document formatting
- Track document status appropriately

## Command Processing

### Document Creation Commands

#### PRD Commands
- "Create a new PRD for {project-name}"
- "Initialize PRD for {project-name}"
- "Generate Product Requirements Document for {project-name}"

#### Architecture Commands
- "Create architecture document for {project}"
- "Initialize architecture for {project}"
- "Generate technical architecture for {project}"

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
- "Add Epic {epic-title} to PRD"
- "Add technology {technology} to architecture"
- "Mark task {task} as complete in story {story-id}"
- "Add task {task} to story {story-id}"

## Directory Structure

```
ai-docs/
├── prd.md                 # Product Requirements Document
├── arch.md                # Architecture Document
├── epic-1-user-auth/      # Epic directory with descriptive suffix
│   ├── story-1-login-flow.story.md   # Story files with descriptive suffixes
│   ├── story-2-signup-form.story.md
│   └── ...
├── epic-2-task-core/      # Another epic with descriptive suffix
│   └── ...
└── ...
```

## Examples
<example>
User: "Create a new PRD for TaskMaster App"

AI Action:
1. Create `ai-docs` directory if it doesn't exist
2. Create `prd.md` file in `ai-docs` directory
3. Apply PRD template
4. Add project-specific details
5. Confirm creation with: "Created Product Requirements Document for TaskMaster App in `ai-docs/prd.md`"

User: "Create a story for Epic-1-user-auth: User Authentication with suffix login-flow"

AI Action:
1. Verify PRD exists in `ai-docs/prd.md`
2. Create `ai-docs/epic-1-user-auth` directory if it doesn't exist
3. Create `story-1-login-flow.story.md` file in `ai-docs/epic-1-user-auth` directory
4. Apply Story template
5. Add story-specific details
6. Confirm creation with: "Created Story-1-login-flow for Epic-1-user-auth: User Authentication in `ai-docs/epic-1-user-auth/story-1-login-flow.story.md`"
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
- Commands must be recognized correctly based on intent
- Documents must be created in the correct directory structure
- Templates must be applied consistently
- References between documents must be maintained
- Status progression must be enforced
- File naming must follow the established conventions
- Always confirm successful command execution 