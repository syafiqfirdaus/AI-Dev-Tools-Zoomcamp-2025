# Git Instructions for AI

When helping with git commands, please follow these guidelines:

1. **Commit Messages**: Use conventional commits (e.g., `feat: add websocket support`, `fix: resolve connection issue`).
2. **Granularity**: Commit often. Each logical change should be a separate commit.
3. **Branching**: If working on a new feature, suggest creating a new branch.
4. **Safety**: Always check `git status` before adding files.

## Example Workflow

1. Check status: `git status`
2. Add files: `git add .` (or specific files)
3. Commit: `git commit -m "feat: implement initial frontend"`
4. Push: `git push origin main`
