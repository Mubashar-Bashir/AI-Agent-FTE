# Subagent-Driven Development - Workflow Reference

## Overview
Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

## Decision Tree
Use when:
- Have implementation plan? ✓
- Tasks mostly independent? ✓
- Stay in this session? ✓

## Step-by-Step Process

### 1. Initialization
- Read plan file once
- Extract all tasks with full text and context
- Create TodoWrite with all tasks

### 2. Per-Task Execution Loop
For each task:

#### A. Dispatch Implementer Subagent
- Provide full task text + context to subagent
- Allow subagent to ask questions
- Answer questions with complete context
- Wait for implementation, testing, committing

#### B. Spec Compliance Review
- Dispatch spec reviewer subagent
- Confirm code matches spec requirements
- If not compliant: Implementer fixes spec gaps, repeat review
- If compliant: Continue to quality review

#### C. Code Quality Review
- Dispatch code quality reviewer subagent
- Review code quality and best practices
- If not approved: Implementer fixes quality issues, repeat review
- If approved: Mark task complete

#### D. Task Completion
- Mark task complete in TodoWrite
- Check if more tasks remain
- If yes: Return to step A
- If no: Proceed to final review

### 3. Finalization
- Dispatch final code reviewer subagent for entire implementation
- Complete development using superpowers:finishing-a-development-branch

## Prompt Templates
- `./implementer-prompt.md` - Dispatch implementer subagent
- `./spec-reviewer-prompt.md` - Dispatch spec compliance reviewer subagent
- `./code-quality-reviewer-prompt.md` - Dispatch code quality reviewer subagent

## Quality Gates
- Self-review catches issues before handoff
- Two-stage review: spec compliance, then code quality
- Review loops ensure fixes actually work
- Spec compliance prevents over/under-building
- Code quality ensures implementation is well-built

## Red Flags
**Never:**
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Dispatch multiple implementation subagents in parallel
- Skip scene-setting context
- Ignore subagent questions
- Accept "close enough" on spec compliance
- Skip review loops
- **Start code quality review before spec compliance is ✅**