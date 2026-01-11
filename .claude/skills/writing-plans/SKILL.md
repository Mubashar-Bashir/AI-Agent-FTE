---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code. Creates comprehensive implementation plans with bite-sized tasks for engineers with zero context. DRY. YAGNI. TDD. Frequent commits.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

## Usage

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

For detailed workflow steps, see [references/workflows.md](./references/workflows.md).
