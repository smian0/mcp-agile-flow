<!-- 
description: Windsurf Rules Template - Master file containing all rules for Windsurf IDE
version: 1.0.0
created_at: 2023-09-15
updated_at: 2023-09-15
-->

# Windsurf Rules

This file contains all rules for the Windsurf IDE, organized by rule type and priority.

## 000-cursor-rules

### Context
- When creating or updating rule files
- When establishing rule structure and style
- When the user requests a new rule or modification

### Requirements
- Follow the rule file structure in this document
- Maintain proper formatting with appropriate sections
- Include HTML comments for metadata
- Organize rules by number prefix and logical grouping

### Examples
<example>
<!-- 
description: Use when writing TypeScript components
applies_to: src/**/*.tsx
always_apply: false
-->

## Rule Title

### Context
- When to apply this rule
- Prerequisites or conditions

### Requirements
- Concise, actionable items
- Each requirement must be testable

### Examples
<example>
Good example
</example>

### Critical Rules
  - Always do X
  - Never do Y
</example>

### Critical Rules
  - Keep rule descriptions under 120 characters
  - Use HTML comments for metadata (not YAML frontmatter)
  - Use standard heading hierarchy (## for rule name, ### for sections)
  - Keep rules concise and specific
  - Include valid and invalid examples for clarity
  - Use XML tags for examples: <example>...</example>
  - Each rule must have Context, Requirements, Examples, and Critical Rules sections

## 001-emoji-communication

### Context
- When responding to user queries in conversations
- When emphasizing important points or status updates
- When making technical communication more engaging and human-friendly

### Requirements
- Use emojis purposefully to enhance meaning, but feel free to be creative and fun
- Place emojis at the end of statements or sections
- Maintain professional tone while surprising users with clever choices
- Limit emoji usage to 1-2 per major section

### Examples
<example>
✅ "I've optimized your database queries 🏃‍♂️💨"
✅ "Your bug has been squashed 🥾🐛"
✅ "I've cleaned up the legacy code 🧹✨"
✅ "Fixed the performance issue 🐌➡️🐆"
</example>

### Critical Rules
  - Never use more than one emoji per statement
  - Choose emojis that are both fun and contextually appropriate
  - Place emojis at the end of statements, not at the beginning or middle
  - Skip emoji usage when discussing serious issues or errors
  - Don't be afraid to tell a mini-story with your emoji choice

## 400-md-docs

### Context
- When creating or modifying any Markdown documentation
- When establishing documentation structure and style
- When including diagrams, code blocks, or special elements in documentation

### Requirements
- Follow the official Markdown Guide for all basic and extended syntax
- Maintain clear document structure with proper heading hierarchy
- Include appropriate HTML comments for metadata when required
- Use Mermaid diagrams for visual documentation where appropriate
- Properly format code blocks, tables, and special elements
- Maximum heading depth: 4 levels
- Indent content within XML tags by 2 spaces
- Keep tables simple and readable with proper alignment

### Examples
<example>
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
</example>

### Critical Rules
  - Use ATX-style headings with space after hash: `# Heading`
  - Maintain proper heading hierarchy (don't skip levels)
  - Add blank line before and after headings and blocks
  - Specify language in code blocks using triple backticks
  - Use blockquotes with emoji for different types of callouts
  - Include clear titles for Mermaid diagrams
  - Keep table structure clean with proper alignment indicators
  - Format Mermaid diagrams with descriptive node labels and comments
  - Close XML tags on their own line at the parent indentation level 