---
description: Use when tracking progress, updating story status, and maintaining project history across the agile workflow
globs: ai-docs/epic-*/story-*.md, ai-docs/prd.md, ai-docs/arch.md
alwaysApply: false
---

# Progress Tracking Standards

## Context
- When implementing a story and tracking progress
- When updating task/subtask completion status
- When documenting implementation history
- When generating progress reports
- When transitioning between workflow phases

## Requirements
- Maintain accurate and up-to-date progress information
- Document the implementation process thoroughly
- Follow TDD principles for task completion
- Ensure comprehensive history through Chat Command Logs
- Generate meaningful progress reports when requested

## Progress Tracking Components

### Status Tracking

#### Document Status Progression
- **PRD/Architecture**: Draft → Approved
- **Epics**: Future → Current → Complete
- **Stories**: Draft → In Progress → Complete

#### Status Transition Requirements
- **Draft to In Progress**: Requires explicit approval
- **In Progress to Complete**: Requires all tasks complete and tests passing
- **Story Completion**: Marks parent Epic as Complete when all Stories are Complete
- **Status Rollback**: Requires documentation of reason in Chat Command Log

### Task Tracking

#### Task Completion Criteria
- Tests must be written before implementation (TDD)
- Tests must pass before marking task complete
- All tests for a story must pass before marking the story Complete
- Implementation notes should be added for complex tasks

#### Task Status Visualization
- Use checkboxes for clear visual progress indication
- `-[ ]` for incomplete tasks
- `-[x]` for completed tasks
- Use strikethrough (`~~task~~`) for cancelled tasks

### Implementation History

#### Chat Command Log
- Record all significant instructions and responses
- Document key technical decisions
- Note any challenges or workarounds
- Maintain chronological order of implementation

#### Dev Notes
- Add implementation details for non-obvious solutions
- Document architectural decisions
- Note performance considerations
- Reference external resources used

## Progress Update Process

### Automatic Updates
- Test completion should automatically update test tasks
- Code implementation should update related tasks
- Epic status should update when all stories are complete

### Manual Updates
- Use "update story progress" for comprehensive updates
- Update at the end of each development session
- Document all changes in Chat Command Log
- Include timestamp for significant updates

### Update Triggers
- Test completion/failure
- Code completion milestones
- End of development session
- Blockers encountered
- Significant decisions made

## Progress Reporting

### Story Progress Report
- Lists all tasks with completion status
- Shows percentage complete
- Highlights blockers or issues
- Includes time spent vs. estimation

### Epic Progress Report
- Shows completion status of all stories
- Displays overall epic completion percentage
- Highlights active story
- Lists completed and pending stories

### Project Overview Report
- Shows status of all epics
- Highlights current active work
- Provides completion timeline
- Lists upcoming work

## Commands

- "update story progress": Updates all aspects of the current story
- "track implementation notes for {task}": Adds notes for specific task
- "generate progress report for {epic|story}": Creates progress summary
- "verify task completion for {task}": Ensures tests pass before completing
- "document decision on {topic}": Adds decision to Chat Command Log

## Examples

<example>
User: "update story progress"

AI Action:
1. Reviews all tasks and subtasks in the current story
2. Updates checkbox status for tasks with passing tests
3. Adds recent commands to Chat Command Log
4. Generates summary of current progress
5. Reports: "Updated Story-2: 4/10 tasks complete (40%). Latest update: Added form validation."

User: "generate progress report for epic-1"

AI Action:
1. Analyzes all stories in Epic-1
2. Calculates completion statistics
3. Produces report:
   "Epic-1 Progress: 2/5 stories complete (40%)
    - Story-1: Complete
    - Story-2: In Progress (40% complete)
    - Story-3: In Progress (10% complete)
    - Story-4: Draft
    - Story-5: Draft"
</example>

<example type="invalid">
User: "is it done yet?"

AI Action:
Gives vague response without checking actual progress or updating any tracking.

User: "mark this as done"

AI Action:
Changes story status to Complete without verifying all tasks are complete or tests pass.
</example>

## Critical Rules
- Never mark a task complete without verifying its tests pass
- Never mark a story complete until all tasks are complete
- Always maintain the Chat Command Log during implementation
- Status must progress in the defined sequence
- Progress updates must be accurate and detailed
- TDD principles must be followed for all implementation
- Only one Epic can be Current at a time
- Only one Story can be In Progress at a time 