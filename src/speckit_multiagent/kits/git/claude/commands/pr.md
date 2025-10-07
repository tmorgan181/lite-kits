---
description: Create pull request with smart description generation
---

# Create Pull Request

**Purpose**: Generate PR description from commits and create pull request using GitHub CLI.

## Prerequisites

- `gh` CLI installed and authenticated
- Current branch pushed to remote
- Git commits on current branch

## Execution Steps

### 1. Verify Prerequisites

```bash
# Check if gh CLI is available
gh --version

# Check if authenticated
gh auth status

# Check current branch
git branch --show-current

# Check if branch has remote tracking
git rev-parse --abbrev-ref --symbolic-full-name @{u}
```

**If not authenticated**:
```
GitHub CLI not authenticated.

Run: gh auth login
Follow the prompts to authenticate.
```

**If branch not pushed**:
```
Current branch not pushed to remote.

Run: git push -u origin <branch-name>
Then try /pr again.
```

### 2. Analyze Commits Since Base Branch

Determine the base branch (usually `main` or `master`):

```bash
# Try common base branches
for base in main master develop; do
  if git show-ref --verify --quiet refs/heads/$base; then
    BASE_BRANCH=$base
    break
  fi
done

# Get commits since divergence
git log $BASE_BRANCH..HEAD --oneline

# Get full commit messages
git log $BASE_BRANCH..HEAD --format="%s%n%b"

# Get file changes
git diff $BASE_BRANCH...HEAD --stat
```

### 3. Detect Multi-Agent Collaboration

Check commit attributions to see if multiple agents contributed:

```bash
# Extract agent attributions from commits
git log $BASE_BRANCH..HEAD --format="%b" | grep "via.*@" || echo "No attributions found"
```

**If multiple agents detected**:
- Note which agents contributed (e.g., "claude-code" and "github-copilot-cli")
- Highlight collaboration in PR description

### 4. Generate PR Description

Create a comprehensive PR description:

**Format**:
```markdown
## Summary

[1-3 sentence overview of what this PR accomplishes]

## Changes

[Bullet points of major changes, grouped by commit type]

- feat: [Features added]
- fix: [Bugs fixed]
- refactor: [Code improvements]
- docs: [Documentation updates]

## Testing

- [ ] Manual testing performed
- [ ] Existing tests pass
- [ ] New tests added (if applicable)

## Multi-Agent Collaboration

[If multiple agents detected]
This PR was developed collaboratively:
- **Claude Code** (claude-sonnet-4.5): [their contributions]
- **GitHub Copilot** (gpt-4): [their contributions]

See commit history for detailed attributions.

---
🤖 Generated with [agent-name]
```

**Example**:
```markdown
## Summary

Implements Phase 1 MVP with `/orient` command and modular kit system for multi-agent coordination.

## Changes

### Features
- Add `/orient` command for agent orientation (project-kit)
- Implement kit-aware installer with --kit flag support
- Add modular kit structure (project, git, multiagent)
- Auto-dependency inclusion (multiagent → project + git)

### Documentation
- Complete audit against WORKFLOW-PATHWAYS.md
- Implementation status matrix
- Phase roadmap documentation

## Testing

- [x] Manual testing performed
- [x] Dry-run installation preview works
- [x] Actual installation to vanilla project succeeds
- [x] Kit detection and validation functional

## Version Safety

✓ Zero vanilla files modified
✓ Additive-only pattern maintained
✓ Namespace separation enforced

---
🤖 Generated with Claude Code (https://claude.com/claude-code)
```

### 5. Analyze Recent Activity

Check for collaboration indicators:

```bash
# Check for collaboration directory
if [ -d "specs/*/collaboration/active" ]; then
  echo "✓ Multi-agent collaboration structure detected"

  # List active sessions
  find specs/*/collaboration/active/sessions -name "*.md" 2>/dev/null

  # List decisions
  find specs/*/collaboration/active/decisions -name "*.md" 2>/dev/null
fi
```

### 6. Present PR Details

Show the generated PR information:

```
═══════════════════════════════════════════════════════════
Pull Request Preview:
═══════════════════════════════════════════════════════════

Title: feat: Implement Phase 1 MVP - /orient and kit system

Base: main
Head: dev/001-starter-kits

Commits: 3
Files changed: 10 (+1456, -132)

Description:
[Generated description from step 4]

═══════════════════════════════════════════════════════════
```

### 7. Confirm and Create PR

**Ask user**:
- **y** - Create PR
- **n** - Cancel
- **e** - Edit title or description

**If confirmed, create PR**:
```bash
# Create PR using gh CLI
gh pr create \
  --base $BASE_BRANCH \
  --title "$PR_TITLE" \
  --body "$PR_DESCRIPTION"
```

**Alternative method if gh CLI not available**:
```
Open PR manually:
https://github.com/[owner]/[repo]/compare/[base]...[head]

Use the generated description above.
```

### 8. Post-Creation Actions

After PR is created:

```bash
# Get PR URL
PR_URL=$(gh pr view --json url -q .url)

echo "✓ Pull Request created: $PR_URL"

# Show PR number and status
gh pr view
```

**Suggest next steps**:
- "PR created. Add reviewers with: `gh pr edit --add-reviewer <username>`"
- "Mark as draft with: `gh pr ready --undo`"
- "View PR: `gh pr view --web`"

## Important Notes

- **Review before creating**: Always show PR description for user approval
- **Don't auto-merge**: Never create and merge in one step
- **Check CI status**: Mention if there are failing checks
- **Link related issues**: If this closes an issue, add "Closes #123" to description
- **Draft PRs**: For work-in-progress, create as draft: `gh pr create --draft`

## Error Handling

**gh CLI not installed**:
```
GitHub CLI not found.

Install from: https://cli.github.com/

Or create PR manually at:
https://github.com/[owner]/[repo]/compare/[base]...[head]
```

**Not authenticated**:
```
Not authenticated with GitHub.

Run: gh auth login
```

**No commits**:
```
No commits to create PR from.

Current branch is up to date with base branch.
Make some commits first.
```

**PR already exists**:
```
Pull request already exists: #42
https://github.com/[owner]/[repo]/pull/42

Update it with: gh pr edit 42 --body "new description"
```

## Multi-Agent PR Workflow

When multiple agents collaborate:

1. **Detect collaboration**:
   - Check commit attributions for multiple agents
   - Look for collaboration/ directory structure
   - Check for handoff documents

2. **Highlight contributions**:
   ```markdown
   ## Multi-Agent Collaboration

   This PR was developed collaboratively:

   ### Claude Code (claude-sonnet-4.5)
   - Implemented core /orient command
   - Created kit-aware installer
   - Wrote documentation and audit

   ### GitHub Copilot (gpt-4)
   - Added PowerShell script variants
   - Implemented error handling
   - Created test cases

   See individual commit messages for detailed attributions.
   ```

3. **Link to collaboration docs**:
   - Reference session logs from specs/*/collaboration/
   - Link to decision documents
   - Mention any unresolved handoffs

## Example Workflow

```bash
# User: /pr

# Agent checks prerequisites
$ gh auth status
✓ Logged in to github.com as username

# Agent analyzes commits
$ git log main..HEAD --oneline
53dd4ef feat: Implement Phase 1 MVP
0ad76b3 refactor: Move vanilla reference
81fdc9d docs: Add workflow pathways

# Agent generates description
[Shows generated PR description]

# Agent asks for confirmation
Create pull request? (y/n/e): y

# Agent creates PR
$ gh pr create --base main --title "..." --body "..."
https://github.com/owner/repo/pull/123

✓ Pull Request created: #123
View: gh pr view --web
```

## Advanced Options

**Create draft PR**:
```bash
gh pr create --draft \
  --base main \
  --title "WIP: Feature in progress" \
  --body "..."
```

**Add reviewers**:
```bash
gh pr create ... --reviewer username1,username2
```

**Add labels**:
```bash
gh pr create ... --label "feature,multiagent"
```

**Auto-fill from template** (if .github/pull_request_template.md exists):
```bash
# gh CLI will automatically use template
gh pr create
```
