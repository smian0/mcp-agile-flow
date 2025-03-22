<!-- 
description: IDE Rules Template - Master file containing all rules for IDE integration
created_at: 2023-09-15
updated_at: 2023-03-20
-->

# IDE Rules

This file contains all rules for IDE integration, organized by rule type and priority.

## Document Generation Process

### Context
- When creating or updating project documentation
- When generating structured documents from templates
- When implementing document standards

### Requirements
- Use the shared .ai-templates directory for all document templates
- Output all generated documents to the ai-docs directory
- Maintain consistent structure
- Follow the standard template formats and document hierarchy

### Document Flow
1. **Templates Source**: All document templates are stored in the `.ai-templates` directory
2. **Output Location**: All AI-produced documents are stored in the `ai-docs` directory
3. **Available Templates**:
   - `template-brd.md`: Business Requirements Document template
   - `template-prd.md`: Product Requirements Document template
   - `template-arch.md`: Architecture Document template
   - `template-story.md`: User Story template
   - `template-epic-summary.md`: Epic Summary template
4. **Document Structure**: Follow the hierarchical structure defined below for all generated documents

### Directory Structure
```
.ai-templates/               # Templates directory
├── template-brd.md          # BRD template
├── template-prd.md          # PRD template
├── template-arch.md         # Architecture template
├── template-story.md        # Story template
└── template-epic-summary.md # Epic Summary template

ai-docs/                     # Documents directory
├── brd.md                   # Business Requirements Document
├── prd.md                   # Product Requirements Document
├── arch.md                  # Architecture Document
├── epic-1-user-auth/        # Epic directory with descriptive suffix
│   ├── epic-summary.md      # Epic Summary file
│   ├── story-1-login-flow.md # Story files with descriptive suffixes
│   ├── story-2-signup-form.md
│   └── ...
├── epic-2-task-core/        # Another epic with descriptive suffix
│   ├── epic-summary.md      # Epic Summary file
│   └── ...
└── ...
```

### Document Creation Commands
#### BRD Commands
- "Create a new BRD for {project-name}"
- "Initialize BRD for {project-name}"
- "Generate Business Requirements Document for {project-name}"
- "Add business objective {objective} to BRD"
- "Add market problem {problem} to BRD"
- "Add success metric {metric} to BRD"
- "Update BRD status to {status}"

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

#### Epic Summary Updates
- "Update epic summary status to {status} for Epic-{N}-{epic-suffix}"
- "Add objective {objective} to Epic-{N}-{epic-suffix}"
- "Update epic description for Epic-{N}-{epic-suffix}: {description}"
- "Refresh stories list for Epic-{N}-{epic-suffix}"
- "Add technical consideration {consideration} to Epic-{N}-{epic-suffix}"
- "Set acceptance criteria for Epic-{N}-{epic-suffix}: {criteria}"
- "Add dependency {dependency} to Epic-{N}-{epic-suffix}"

#### Git Workflow Commands
- "How do I format a Git commit message?"
- "What is the correct commit format?"
- "Help me write a commit message for {changes}"
- "Review my commit message"
- "Generate a commit message for {changes}"

### Examples
<example>
User: "Create a new PRD for TaskMaster App"

AI Action:
1. Identify template to use: `.ai-templates/template-prd.md`
2. Create `ai-docs` directory if it doesn't exist
3. Create `prd.md` file in `ai-docs` directory using the template
4. Add project-specific details
5. Confirm creation with: "Created Product Requirements Document for TaskMaster App in `ai-docs/prd.md`"

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

<example>
User: "Help me write a commit message for adding user authentication"

AI Action:
1. Identify the commit message format: conventional commits
2. Apply the template from template-git-commit.md
3. Prompt for file changes if not provided
4. Generate a structured commit message:
```
feat(auth): add user authentication system

Changes made in this commit:
- Modified: src/auth/services.js, src/components/Login.js
- Added: src/auth/oauth.js, src/auth/jwt.js

Key changes:
- Implement JWT token-based authentication
- Add Google OAuth integration
- Create login form components

Relates to #45
```
</example>

### Critical Rules
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

## Document Standards

### Product Requirements Document (PRD) Standards

#### Context
- When creating a new Product Requirements Document
- When updating an existing PRD
- When reviewing PRD approval status
- When defining project scope and requirements

#### Requirements
- Follow standardized PRD structure
- Include all required sections
- Maintain proper documentation hierarchy
- Use consistent formatting
- Define clear project goals and features
- Include epic structure and story outlines

#### Document Structure
1. **Header**: "Product Requirements Document (PRD) for {project-name}"
2. **Status**: Draft or Approved
3. **Introduction**:
   - Clear description of project
   - Project scope overview
   - Business context and drivers
   - Target users/stakeholders
4. **Goals**:
   - Clear measurable objectives
   - Success criteria
   - Key performance indicators (KPIs)
5. **Features and Requirements**:
   - Functional requirements
   - Non-functional requirements
   - User experience requirements
   - Integration requirements
6. **Epic Structure**:
   - Format: Epic-{N}-{descriptive-suffix}: {Title} ({Status})
   - {N} is the sequential number
   - {descriptive-suffix} is 1-3 meaningful words separated by hyphens
   - Example: Epic-1-user-auth, Epic-2-task-management

#### Critical Rules
- PRD must have clear, measurable goals
- All sections must be included and properly formatted
- Epic structure must be defined and follow the correct format
- PRD must progress through appropriate status stages
- Introduction must clearly define the project scope and users

### Architecture Documentation Standards

#### Context
- When creating a new Architecture Document
- When updating existing architecture documentation
- When making significant technical decisions
- When defining project structure and technology choices

#### Requirements
- Document architectural decisions clearly
- Maintain a Changelog for updates
- Use diagrams to illustrate system components and interactions
- Define technology stack and justifications
- Outline project structure
- Include data models and API specifications

#### Document Structure
1. **Title**: "Architecture for {project}"
2. **Status**: Draft or Approved
3. **Technical Summary**:
   - Architectural approach overview
   - Key design patterns and principles
   - High-level system description
4. **Technology Table**:
   - Technology choices (languages, libraries, infrastructure)
   - Justification for each choice
5. **Architectural Diagrams**:
   - System component diagrams
   - Data flow diagrams
   - Use Mermaid syntax for diagrams
6. **Data Models, API Specs, Schemas**:
   - Key database schema definitions
   - API endpoints
   - Data structures
7. **Project Structure**:
   - Folder and file organization
   - Component relationships
8. **Change Log**:
   - Table of changes after approval
   - Change title, story ID, and description

#### Critical Rules
- Architecture document must define clear technology choices with justifications
- Diagrams must be included to illustrate system components and interactions
- Data models must be defined for key entities
- Project structure must be clearly documented
- Changes must be tracked in the changelog after approval
- Technical decisions must be clearly explained

### User Story Standards

#### Context
- When creating a new user story
- When updating an existing story
- When tracking story implementation progress
- When reviewing story completion status
- When breaking down work into tasks

#### Requirements
- Follow standardized story structure
- Include all required sections
- Maintain proper status progression
- Link to parent epic
- Include task breakdown and status tracking
- Follow Test-Driven Development principles

#### Document Structure
1. **Header**:
   - Epic-{N}: {Epic Title}
   - Story-{M}: {Story Title}
2. **Story Description**:
   - Format: **As a** {role} **I want** {action} **so that** {benefit}
   - User-focused description
   - Specific, measurable action
   - Clear benefit
3. **Status**:
   - Valid values: Draft, In Progress, Complete, Cancelled
   - Must follow proper progression
4. **Context**:
   - Background information
   - Current state
   - Story justification
5. **Estimation**:
   - Story Points: {story_points} (1 story_point = 1 day of Human Development is equal to 10 minutes of AI development)
   - Implementation Time Estimates:
     - Human Development: {story_points} days
     - AI-Assisted Development: {story_points/60} days (~{story_points*10} minutes)
6. **Tasks**:
   - Checkbox format: - [ ] for incomplete, - [x] for complete
   - Start with testing tasks (TDD approach)
   - Use nested lists for subtasks

#### Critical Rules
- Stories must have a clear user-focused description
- Tasks must follow TDD principles (tests first)
- Status must follow proper progression (Draft → In Progress → Complete)
- Epic reference must be maintained
- Story Points must be specified
- Tasks must use proper checkbox format
- All required sections must be included
- Stories must be organized in the correct directory structure

## Communication Standards

### Emoji Usage Guidelines

#### Context
- When responding to user queries in conversations
- When emphasizing important points or status updates
- When making technical communication more engaging and human-friendly

#### Requirements
- Use emojis purposefully to enhance meaning, but feel free to be creative and fun
- Place emojis at the end of statements or sections
- Maintain professional tone while surprising users with clever choices
- Limit emoji usage to 1-2 per major section

#### Examples
- ✅ "I've optimized your database queries 🏃‍♂️💨"
- ✅ "Your bug has been squashed 🥾🐛"
- ✅ "I've cleaned up the legacy code 🧹✨"
- ✅ "Fixed the performance issue 🐌➡️🐆"

#### Invalid Examples
- ❌ "Multiple 🎉 emojis 🎊 in 🌟 one message"
- ❌ "Using irrelevant emojis 🥑"
- ❌ "Placing the emoji in the middle ⭐️ of a sentence"

#### Critical Rules
- Never use more than one emoji per statement
- Choose emojis that are both fun and contextually appropriate
- Place emojis at the end of statements, not at the beginning or middle
- Skip emoji usage when discussing serious issues or errors
- Don't be afraid to tell a mini-story with your emoji choice

## Documentation Standards

### Markdown Formatting Standards

#### Context
- When creating or modifying any Markdown documentation
- When establishing documentation structure and style
- When including diagrams, code blocks, or special elements in documentation

#### Requirements
- Follow the official Markdown Guide for all basic and extended syntax
- Maintain clear document structure with proper heading hierarchy
- Include appropriate YAML front matter for metadata when required
- Use Mermaid diagrams for visual documentation where appropriate
- Properly format code blocks, tables, and special elements
- Maximum heading depth: 4 levels
- Indent content within XML tags by 2 spaces
- Keep tables simple and readable with proper alignment

#### Examples
```markdown
# Document Title

## Section Heading

Content with **bold text** and *italics*.

```typescript
function example(): void {
  console.log('Hello, Universe!');
}
```

| Name | Type | Description |
|:-----|:----:|------------:|
| id | number | Primary key |
| name | string | User's name |

> 💡 **Tip:** Helpful suggestion.
```

#### Invalid Examples
```markdown
#Incorrect Heading
content without proper spacing

```
function withoutLanguageSpecified() {
}
```

| No | alignment | markers |
| or | proper | formatting |
```

#### Critical Rules
- Use ATX-style headings with space after hash: `# Heading`
- Maintain proper heading hierarchy (don't skip levels)
- Add blank line before and after headings and blocks
- Specify language in code blocks using triple backticks
- Use blockquotes with emoji for different types of callouts
- Include clear titles for Mermaid diagrams using the `---` syntax
- Keep table structure clean with proper alignment indicators
- Format Mermaid diagrams with descriptive node labels and comments
- Close XML tags on their own line at the parent indentation level

## Rule Implementation Guidelines

### Context
- When implementing IDE-specific rule implementations
- When creating or updating rule files
- When ensuring compatibility of rules

### Requirements
- Maintain consistent rule implementation 
- Follow the rule format specific to each IDE
- Ensure rules are applied in the correct context
- Rules must produce identical results
- Rules should be well-organized

#### Rule Implementation
- Rules are consolidated in this single file
- Rules are organized by sections with clear headings
- Each rule section includes context, requirements, examples, and critical rules

### Critical Rules
- Files must be properly formatted for the IDE to read and follow

## Build and Automation Standards

### Makefile Usage Standards

#### Context
- When working with projects that have build, test, or deployment automation
- When setting up a new project that requires task automation
- When executing project commands or workflows
- When maintaining or updating build processes
- When documenting project setup and usage

#### Requirements
- Always look for and use existing Makefiles for project commands
- Follow proper Makefile syntax and conventions
- Document all Makefile targets clearly with comments
- Organize targets by category (build, test, run, clean, deploy)
- Maintain backward compatibility when updating Makefiles
- Ensure all commands are properly escaped and portable
- Provide descriptive help targets for self-documentation

#### Makefile Structure
1. **Components**:
   - Variables: Define variables at the top
   - Phony Targets: Mark non-file targets as .PHONY
   - Default Target: First target is default
   - Dependencies: Specify target dependencies
   - Help: Include help target
   - Comments: Document each target

#### Examples
- ✅ Check for Makefile first: "You can run the tests using `make test`"
- ✅ Reference existing targets: "The Makefile includes these commands: `make build`, `make install`"
- ✅ Add to Makefile: "I'll add a new target to the Makefile for this operation"

#### Invalid Examples
- ❌ Ignoring Makefile: Suggesting direct commands when equivalent make targets exist
- ❌ Creating duplicate functionality: Adding scripts instead of extending the Makefile
- ❌ Using incorrect syntax: Indenting command lines with spaces instead of tabs

#### Critical Rules
- Always check for the existence of a Makefile before suggesting command-line instructions
- Use `make` commands instead of direct shell commands when equivalent targets exist
- When adding functionality, extend the Makefile rather than creating separate scripts
- Preserve existing Makefile structure and conventions when making updates
- Document all Makefile changes clearly with comments
- Ensure Makefile targets are properly categorized
- Use tab indentation (not spaces) for command lines
- Keep commands portable across environments (avoid system-specific commands)
- Ensure all targets have clear, descriptive names that reflect their purpose

### Document Types

#### BRD - Business Requirements Document

The Business Requirements Document (BRD) establishes the business context and rationale for a project. It sits above the PRD in the documentation hierarchy and focuses on:

1. Executive Summary - Concise overview of the business need and solution approach
2. Business Objectives - Clear, measurable business goals driving the project
3. Market Problem Analysis - Detailed examination of market gaps and customer pain points
4. Success Metrics - Quantifiable measures of project success with baseline and target values
5. Customer Needs - Segmented analysis of user requirements
6. Business Constraints - Limitations on budget, time, resources, technology, and regulations
7. Assumptions - Explicit business, market, technical, and resource assumptions
8. Stakeholders - Key stakeholders with roles, responsibilities, and decision authority
9. Related Documents - Links to supporting documents, particularly the PRD

The BRD follows a defined status progression:
1. Draft - Initial creation and iteration
2. In Review - Shared with stakeholders for feedback
3. Approved - Finalized and accepted by key stakeholders
4. Superseded - When replaced by a newer version

#### PRD - Product Requirements Document

The Product Requirements Document (PRD) defines the product's purpose, features, functionality, and behavior. It follows the BRD in the documentation hierarchy and focuses on:

1. Introduction - Clear description of the project, scope, and context
2. Goals - Measurable objectives and success criteria for the product
3. Features and Requirements - Detailed functional and non-functional requirements
4. Epic Structure - Organized breakdown of major feature sets
5. Story List - User stories organized under Epics
6. Tech Stack - High-level overview of technologies to be used
7. Future Enhancements - Potential features for future consideration

The PRD follows a defined status progression:
1. Draft - Initial creation and iteration
2. Approved - Finalized and accepted by stakeholders

#### Architecture Document

The Architecture Document defines the technical approach, system components, and implementation strategy. It follows the PRD in the documentation hierarchy and focuses on:

1. Technical Summary - Overview of the architectural approach
2. Technology Stack - Detailed list of technologies with justifications
3. Architectural Diagrams - Visual representations of system components and data flows
4. Data Models - Database schema and data structure definitions
5. API Specifications - Endpoint definitions and interaction patterns
6. Project Structure - Organization of code and resources
7. Non-functional Requirements - Performance, security, and operational considerations

The Architecture Document follows a defined status progression:
1. Draft - Initial creation and iteration
2. Approved - Finalized and accepted by stakeholders
3. Updated - When changes are made after approval

#### User Story

User Stories define specific pieces of functionality from the user's perspective. They are organized under Epics and focus on:

1. Story Description - In the format "As a [role] I want [action] so that [benefit]"
2. Context - Background information and justification
3. Acceptance Criteria - Requirements for story completion
4. Tasks - Specific implementation tasks with checkboxes for tracking progress
5. Implementation Notes - Technical details and approach
6. Dev Notes - Notes made during implementation
7. Test Strategy - Approach for testing the functionality

Stories follow a defined status progression:
1. Draft - Initial creation
2. In Progress - During active development
3. Complete - When all tasks are finished
4. Cancelled - When the story is no longer needed

## Version Control Standards

### Git Commit Message Standards

#### Context
- When creating a new Git commit
- When reviewing commit messages
- When documenting changes in version control
- When generating changelogs from commit history

#### Requirements
- Follow conventional commits format: type(scope): description
- Include detailed change summary
- Group changes by category (added, modified, deleted)
- Provide context for non-obvious changes
- Reference issues when applicable
- Structure commit messages consistently
- Support GitHub and GitLab reference formats
- Keep subject line under 72 characters

#### Format
```
type(scope): brief description

Changes made in this commit:
- Modified: [list of modified files]
- Added: [list of added files]
- Deleted: [list of deleted files]

Key changes:
- [specific change 1]
- [specific change 2]
...

[Detailed explanation if needed]

Closes #issue_number (if applicable)
```

#### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Changes that don't affect code functionality (formatting, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or correcting tests
- **chore**: Changes to the build process or auxiliary tools
- **ci**: Changes to CI configuration
- **revert**: Revert a previous commit

#### GitHub and GitLab Integration
##### GitHub Issue References
- Use `Fixes #123` to automatically close an issue
- Use `Relates to #123` for related issues without closing
- Supports keywords: close, closes, closed, fix, fixes, fixed, resolve, resolves, resolved

##### GitLab Issue and Merge Request References
- Use `Closes #123` to automatically close an issue
- Use `Relates to #123` for related issues without closing
- Use `!123` to reference merge requests

#### CI/CD Integration
- Use `[skip ci]` or `[ci skip]` in the commit message to skip CI/CD pipelines when appropriate
- For GitLab, you can also use `[skip gitlab-ci]`

#### Examples
<example>
✅ feat(auth): add login with Google OAuth

Changes made in this commit:
- Modified: src/auth/providers.js, src/components/Login.js
- Added: src/auth/google.js

Key changes:
- Add GoogleAuthProvider class
- Integrate OAuth flow in login component
- Add configuration options for Google client ID

Implements the Google authentication option requested in the
product requirements document.

Closes #42
</example>

<example>
✅ fix(ui): correct button alignment on mobile

Changes made in this commit:
- Modified: src/components/Button.css

Key changes:
- Fix flex layout for small screens
- Adjust padding for touch targets

Fixes the issue where buttons were overlapping on
mobile devices smaller than 375px width.

Fixes #78
</example>

<example type="invalid">
❌ Added login feature

This adds the login feature we discussed yesterday. It seems to be working
but might need more testing. I also changed some CSS.
</example>

<example type="invalid">
❌ feat(auth) - Added Google login feature and fixed the CSS bug with the dropdown menu that was reported by the QA team last week. Also did some refactoring of the auth module to make it cleaner.
</example>

#### Critical Rules
- Always use the conventional commits format (type(scope): description)
- Keep the subject line under 72 characters
- Include a list of modified/added/deleted files
- Use imperative mood in descriptions ("add" not "added")
- Don't capitalize the first letter of the description
- No period at the end of the subject line
- Separate subject from body with a blank line
- Reference issues when applicable using the correct format
- Be specific about what was changed and why
- When combining multiple changes, consider splitting into separate commits

### Project Ideation Standards

#### Context
- When a user wants to start a new project from an initial idea
- When transforming unstructured project concepts into a structured outline
- When kicking off the agile workflow process

#### Requirements
- Generate a structured project ideation document using the template
- Capture core project elements: overview, audience, features, impact, criteria
- Elicit information conversationally rather than requesting form completion
- Guide users to BRD creation after project ideation is complete

#### Document Structure
1. **Header**: "Project Ideation for {project-name}"
2. **Status**: Draft
3. **Project Overview**: Problem/opportunity description
4. **Core Idea**: Central concept in 2-3 sentences
5. **Target Audience**: Primary and secondary users
6. **Key Features**: Bullet list of primary features
7. **Potential Impact**: Anticipated benefits and importance
8. **Success Criteria**: Measurable indicators of success
9. **Next Steps**: Guidance to BRD/PRD/Architecture creation

#### Critical Rules
- Always use project ideation before proceeding to BRD/PRD
- Store project ideation documents in the ai-docs directory
- Ensure all sections have meaningful content
- Guide the user to the next step (typically BRD creation) after completion
- Document should be named "project-ideation.md" in the ai-docs root directory