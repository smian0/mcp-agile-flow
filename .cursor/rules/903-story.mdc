---
description: Use when creating or updating User Stories to ensure proper structure, tracking, and implementation
globs: ai-docs/epic-*/story-*.md
alwaysApply: false
---

# User Story Standards

## Context
- When creating a new user story
- When updating an existing story
- When tracking story implementation progress
- When reviewing story completion status
- When breaking down work into tasks

## Requirements
- Follow standardized story structure
- Include all required sections
- Maintain proper status progression
- Link to parent epic
- Include task breakdown and status tracking
- Follow Test-Driven Development principles

## Template Structure

### Required Sections

#### 1. Header
- Format: Epic-{N}: {Epic Title}
- Format: Story-{M}: {Story Title}

#### 2. Story Description
- Format: **As a** {role} **I want** {action} **so that** {benefit}
- Clear user-focused description
- Specific, measurable action
- Clear benefit or value

#### 3. Status
- Valid values: Draft, In Progress, Complete, Cancelled
- Must follow proper progression
- No skipping states

#### 4. Context
- Background information
- Current state
- Story justification
- Technical context
- Business drivers
- Relevant history from previous stories

#### 5. Estimation
**Story Points**: {story_points} (1 SP = 1 day of Human Development = 10 minutes of AI development)

**Implementation Time Estimates**:
- **Human Development**: {story_points} days
- **AI-Assisted Development**: {story_points/60} days (~{story_points*10} minutes)

#### 6. Tasks
- Organized in task groups
- Use checkbox format: - [ ] for incomplete, - [x] for complete
- Start with testing tasks (TDD approach)
- Use nested lists for subtasks

#### 7. Additional Sections (as needed)
- Constraints
- Data Models / Schema
- Structure
- Diagrams
- Dev Notes
- Chat Command Log

## Commands
- "Create a story for Epic-{N}": Generates a new story file
- "Update story status to {status}": Updates story status
- "Mark task {task} as complete": Updates task status
- "Add task {task} to story": Adds a new task to the story

## Update Mechanisms

### Automatic Updates
- **Test Completion**: When tests are run and pass, the corresponding test task should be automatically marked as complete
- **Code Implementation**: When code is committed or saved, the corresponding implementation task can be updated
- **Dependency Changes**: When a dependency changes status, related tasks should be reviewed

### Manual Updates
- **Story Progress Command**: Use "update story progress" to refresh all story components at once
- **Periodic Updates**: Story should be updated at the end of each development session
- **Milestone Completion**: Story should be comprehensively updated when significant milestones are reached

### TDD Verification Requirements
- Test tasks must have passing tests before being marked complete
- Implementation tasks should not be marked complete until their tests pass
- The complete story should have full test coverage before marking as Complete

### Chat Command Log Maintenance
- Record all significant user instructions and agent responses
- Document key decisions and technical choices
- Maintain a chronological history of the implementation process
- Note any challenges or blockers encountered during implementation

## Examples
<example>
# Epic-1: Basic Chess Game
# Story-2: Implement Chessboard UI

## Story

**As a** chess player
**I want** to see a clear and interactive chessboard
**so that** I can play chess in the web browser

## Status

In Progress

## Context

Part of Epic-1 which implements the core 2-player chess game. This story focuses on the visual and interactive aspects of the chessboard. The project setup (Story-1) is complete, providing the foundation for UI implementation.

## Estimation

Story Points: 2

## Tasks

1. - [x] Create Chessboard Grid
   1. - [x] Implement 8x8 board layout
   2. - [x] Add square coloring
   3. - [x] Write grid tests
2. - [ ] Add Chess Pieces
   1. - [ ] Create piece components
   2. - [ ] Add piece images
   3. - [ ] Write piece tests
3. - [ ] Implement Basic Interaction
   1. - [ ] Add click handlers
   2. - [ ] Highlight selected square
   3. - [ ] Write interaction tests

## Dev Notes

- Using React for UI components
- Chess piece SVGs from open-source library
- Implementing responsive design for various screen sizes

## Chat Command Log

- User: Let's implement the chessboard UI
- AI: Reviewing the design requirements. Should we use SVG or PNG for pieces?
  - User: Let's use SVG for better scaling
- AI: Grid implementation complete, proceeding with piece placement
</example>

<example type="invalid">
Chess UI Story

todo:

- make board
- add pieces
- make it work
</example>

## Critical Rules
- Stories must have a clear user-focused description
- Tasks must follow TDD principles (tests first)
- Status must follow proper progression (Draft → In Progress → Complete)
- Epic reference must be maintained
- Story Points must be specified
- Tasks must use proper checkbox format
- All required sections must be included
- Stories must be organized in the correct directory structure 