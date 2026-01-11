---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes. Always find root cause before attempting fixes - symptom fixes are failure. Systematic approach prevents thrashing.
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**The Iron Law:** NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (systematic is faster than thrashing)

## Usage

For detailed workflow steps including the Four Phases (Root Cause Investigation, Pattern Analysis, Hypothesis Testing, Implementation), see [references/workflows.md](./references/workflows.md).

## Red Flags

Stop immediately if you catch yourself:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- Proposing solutions before tracing data flow
- Making multiple fixes at once

**ALL of these mean: STOP. Return to Phase 1.**
