# Cursor Rules: Advanced Configuration & Best Practices

## Introduction

This document provides comprehensive guidance on effectively leveraging Cursor AI's rule system based on the latest updates. Cursor's rule framework has undergone significant enhancements to offer developers greater control over AI agent behavior through a flexible, context-aware system.

## Rule Type Classification

Cursor now supports four distinct rule types, each serving specific use cases:

1. **Agent Selected** (`always_apply: false` with description and no glob pattern)
   - Agent examines the description without loading the entire rule
   - Only loads the complete rule when deemed relevant
   - Requires precise, detailed descriptions for optimal selection

2. **Always** (`always_apply: true`)
   - Applied universally to every chat agent window and Command-K request
   - Most similar to legacy root.cursor behavior
   - Description field not editable in this mode

3. **Auto Select** (`always_apply: false` with glob patterns, description optional)
   - Automatically applies when working with specified file types
   - Configured through glob patterns (e.g., "*.ts", "*.env")
   - Can function with minimal description field content

4. **Manual/Macro** (`always_apply: false` with no description or glob pattern)
   - Explicitly invoked by referencing the rule name
   - Functions as command shortcuts for common operations
   - Example use case: Git operations via "@git-push" command

## Organizational Structure

The rule system now supports hierarchical organization:

```
.cursor/
└── rules/
    ├── core/
    │   ├── behavior.mdc
    │   └── formatting.mdc
    ├── languages/
    │   ├── typescript.mdc
    │   └── python.mdc
    └── tools/
        ├── git-push.mdc
        └── research.mdc
```

This organization enhances maintainability as projects scale, replacing previous numeric prefix conventions with logical grouping.

## Configuration Optimization

### Editor Configuration Fix

To resolve issues with agent rule generation, configure VS Code settings:

```json
{
  "workbench.EditorAssociations": {
    "*.mdc": "default"
  }
}
```

This setting prevents conflicts by using the standard text editor rather than the specialized MDC viewer, significantly improving rule creation reliability.

## Effective Rule Design

### Description Field Importance

For agent-selected rules, the description field serves as the primary selection mechanism:

- Be explicit about when the rule should apply
- Include key trigger phrases or contexts
- Ensure the description clearly communicates the rule's purpose

### Rule Structure Components

Well-formed rules typically include:

1. **Front Matter** (YAML configuration)
2. **Description** (Agent selection criteria)
3. **Context** (Background information)
4. **Critical Rules** (Core behavioral directives)
5. **Examples** (Positive demonstrations)
6. **Anti-Patterns** (Negative examples to avoid)

## Implementation Recommendations

Based on empirical observations:

1. **Minimize Rule Quantity**: Rely on the LLM's inherent knowledge for common patterns and frameworks before creating explicit rules.

2. **Iterative Refinement**: Implement self-correction by creating rules when problematic patterns emerge.

3. **Temporal Considerations**: Rules should evolve with your project—remove unnecessary constraints as conventions become established in the codebase.

4. **Expect Non-Determinism**: LLM behavior maintains some variability despite rules; continuous refinement is necessary.

5. **Macro Utilization**: For frequently used commands, consider manual/macro rules activated by explicit invocation rather than complex instructional patterns.