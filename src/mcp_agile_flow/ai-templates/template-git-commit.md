# Git Commit Message Template

<version>1.0.0</version>

## Requirements

- Follow conventional commits format
- Include all required sections
- Provide clear and descriptive commit messages

## Commit Message Structure

### Format

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

### Types
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

### Scope

The scope is optional and represents the section of the codebase affected:
- **api**: API-related changes
- **ui**: User interface changes
- **data**: Data model changes
- **auth**: Authentication-related changes
- **config**: Configuration changes
- etc.

### Description Guidelines

- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Keep under 72 characters
- Be specific and clear
- Reference issues when applicable

### GitHub and GitLab Integration

#### GitHub Issue References

- Use `Fixes #123` to automatically close an issue
- Use `Relates to #123` for related issues without closing
- Supports keywords: close, closes, closed, fix, fixes, fixed, resolve, resolves, resolved

#### GitLab Issue and Merge Request References

- Use `Closes #123` to automatically close an issue
- Use `Relates to #123` for related issues without closing
- Use `!123` to reference merge requests

### CI/CD Integration

- Use `[skip ci]` or `[ci skip]` in the commit message to skip CI/CD pipelines when appropriate
- For GitLab, you can also use `[skip gitlab-ci]`

## Examples

### Feature Addition
```
feat(auth): add login with Google OAuth

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
```

### Bug Fix
```
fix(ui): correct button alignment on mobile

Changes made in this commit:
- Modified: src/components/Button.css

Key changes:
- Fix flex layout for small screens
- Adjust padding for touch targets

Fixes the issue where buttons were overlapping on
mobile devices smaller than 375px width.

Fixes #78
```

### Documentation Update
```
docs: update README with setup instructions

Changes made in this commit:
- Modified: README.md

Key changes:
- Add development environment setup section
- Clarify prerequisites
- Add troubleshooting guide

Makes it easier for new contributors to get started.
```

## Critical Rules

- Always follow the conventional commits format
- Keep the subject line under 72 characters
- Use the appropriate commit type
- Be specific about what changes were made
- Reference issues when applicable
- Use imperative mood in the description
- Separate subject from body with a blank line
- When in doubt, provide more detail rather than less 