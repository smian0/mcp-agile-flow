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
- Reference issues when applicable
- Structure commit messages consistently
- Support GitHub and GitLab reference formats
- Keep subject line under 72 characters

## Format

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

## Types

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

## Examples
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

## Critical Rules
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