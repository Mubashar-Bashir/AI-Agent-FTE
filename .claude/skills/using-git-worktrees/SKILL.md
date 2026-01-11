---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans. Creates isolated git worktrees with smart directory selection and safety verification. Systematic directory selection + safety verification = reliable isolation.
---

# Using Git Worktrees

## Overview

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Usage

For detailed workflow steps including directory selection, safety verification, and creation steps, see [references/workflows.md](./references/workflows.md).

## Integration

**Called by:**
- **brainstorming** (Phase 4) - REQUIRED when design is approved and implementation follows
- Any skill needing isolated workspace

**Pairs with:**
- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
- **executing-plans** or **subagent-driven-development** - Work happens in this worktree
