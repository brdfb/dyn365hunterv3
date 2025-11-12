# Auto Documentation Updater Agent

## Role
Automatically updates documentation when code changes are detected.

## Triggers

### Automatic (Always Active)
1. **After code changes**: When new files are created in `app/api/`, `app/core/`, `tests/`
2. **After phase completion**: When TODO status changes to "Completed"
3. **After new endpoints**: When new API endpoints are added
4. **After new tests**: When new test files are created

## Workflow

### When API Endpoints Added
1. Detect new files in `app/api/`
2. Update README.md API Endpoints section
3. Add example usage if needed
4. Update CHANGELOG.md under "Added" section

### When Tests Added
1. Detect new files in `tests/`
2. Update CHANGELOG.md with test coverage info
3. Update README.md Testing section if needed

### When Phase Completed
1. Detect TODO status = "Completed"
2. Run full phase completion workflow:
   - Archive TODO
   - Update CHANGELOG.md
   - Update README.md Features
   - Update docs/README.md

## Rules

1. **Always run automatically** - No manual trigger needed
2. **Check git status** - Only update if files changed
3. **Preserve existing content** - Append, don't replace
4. **Ask before major changes** - Only for critical updates

## Implementation

This agent should be **always active** in the AI assistant's context. When you see:
- New API files created → Auto-update README
- New test files created → Auto-update CHANGELOG
- TODO completed → Run phase completion workflow

