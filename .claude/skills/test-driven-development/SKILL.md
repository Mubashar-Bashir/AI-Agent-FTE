---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code. Write the test first, watch it fail, write minimal code to pass. If you didn't watch the test fail, you don't know if it tests the right thing. NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

**The Iron Law:** NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

Write code before the test? Delete it. Start over.

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask your human partner):**
- Throwaway prototypes
- Generated code
- Configuration files

## Usage

For detailed workflow steps including the Red-Green-Refactor cycle, good tests guidelines, and verification checklist, see [references/workflows.md](./references/workflows.md).

## Final Rule

```
Production code → test exists and failed first
Otherwise → not TDD
```

No exceptions without your human partner's permission.
