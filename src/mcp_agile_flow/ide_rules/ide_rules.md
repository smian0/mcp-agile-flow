<!-- 
description: Generic IDE Rules Template - Master file containing all rules for IDE integration
version: 1.0.0
created_at: 2023-09-15
updated_at: 2023-09-25
-->

# IDE Rules

This file contains all rules for IDE integration, organized by rule type and priority. It's designed to be used by multiple IDEs including Windsurf, Cline, and Copilot.

## Document Generation Process

### Context
- When creating or updating project documentation
- When generating structured documents from templates
- When implementing cross-IDE document standards

### Requirements
- Use the shared ai-templates directory for all document templates
- Output all generated documents to the ai-docs directory
- Maintain consistent structure across all IDEs
- Use identical document generation process regardless of IDE
- Follow the standard template formats and document hierarchy

### Document Flow
1. **Templates Source**: All document templates are stored in the IDE-agnostic `ai-templates` directory
2. **Output Location**: All AI-produced documents are stored in the `ai-docs` directory
3. **Cross-IDE Consistency**: The exact same document generation process is used across all IDEs
4. **Available Templates**:
   - `template-prd.md`: Product Requirements Document template
   - `template-arch.md`: Architecture Document template
   - `template-story.md`: User Story template
5. **Document Structure**: Follow the hierarchical structure defined below for all generated documents

### Directory Structure
```
ai-templates/                 # Source templates directory (not visible to user)
├── template-prd.md           # PRD template
├── template-arch.md          # Architecture template
└── template-story.md         # Story template

ai-docs/                      # Output documents directory (visible to user)
├── prd.md                    # Product Requirements Document
├── arch.md                   # Architecture Document
├── epic-1-user-auth/         # Epic directory with descriptive suffix
│   ├── story-1-login-flow.story.md   # Story files with descriptive suffixes
│   ├── story-2-signup-form.story.md
│   └── ...
├── epic-2-task-core/         # Another epic with descriptive suffix
│   └── ...
└── ...
```

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

### Examples
<example>
User: "Create a new PRD for TaskMaster App"

AI Action:
1. Identify template to use: `ai-templates/template-prd.md`
2. Create `ai-docs` directory if it doesn't exist
3. Create `prd.md` file in `ai-docs` directory using the template
4. Add project-specific details
5. Confirm creation with: "Created Product Requirements Document for TaskMaster App in `ai-docs/prd.md`"
</example>

### Critical Rules
- Process must be identical across all supported IDEs (Cursor, Windsurf, Cline, Copilot)
- Templates must always be sourced from the ai-templates directory
- Documents must always be created in the ai-docs directory
- Templates must be applied consistently
- References between documents must be maintained
- Status progression must be enforced
- File naming must follow the established conventions
- Always confirm successful command execution

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
   - Story Points format: SP: {points}
   - 1 SP = 1 day of Human Development = 10 minutes of AI development
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

| Name  | Type   | Description  |
|:------|:------:|-------------:|
| id    | number | Primary key  |
| name  | string | User's name  |

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
- When creating or updating rule files for different IDEs
- When ensuring cross-IDE compatibility of rules

### Requirements
- Maintain consistent rule implementation across all IDEs
- Follow the rule format specific to each IDE
- Ensure rules are applied in the correct context
- Rules must produce identical results across all IDEs
- Rules should be well-organized and easily maintainable

### IDE-Specific Rule Implementation

Each IDE may have a different way of implementing rules, but the core concepts and requirements should remain consistent:

#### Cursor
- Rules are implemented as separate `.md` files in the cursor_rules directory
- Each rule file follows a specific naming convention (prefix-name.md)
- Rules include YAML frontmatter with description, globs, and alwaysApply properties
- Rules are organized by category (core, templates, documentation, etc.)

#### Other IDEs (Windsurf, Cline, Copilot)
- Rules are consolidated in this single file (ide_rules.md)
- Rules are organized by sections with clear headings
- Each rule section includes context, requirements, examples, and critical rules
- The format is consistent with Cursor's rules, but consolidated for simplicity

### Critical Rules
- All rule implementations must produce identical results across IDEs
- Rule files must be properly formatted according to IDE-specific requirements
- Rules must be regularly updated to maintain consistency
- When a rule is updated in one IDE, it must be updated in all IDE implementations
- Rule format must follow the documentation standards outlined in this file