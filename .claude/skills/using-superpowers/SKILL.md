---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions. If there's even a 1% chance a skill might apply, you ABSOLUTELY MUST invoke it.
---

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.

**In other environments:** Check your platform's documentation for how skills are loaded.

## The Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

## Usage

For detailed workflow steps including the skill invocation process, decision flow, and priority guidelines, see [references/workflows.md](./references/workflows.md).

## Red Flags

These thoughts mean STOP—you're rationalizing:
- "This is just a simple question" → Questions are tasks. Check for skills.
- "I need more context first" → Skill check comes BEFORE clarifying questions
- "Let me explore the codebase first" → Skills tell you HOW to explore. Check first
- "I can check git/files quickly" → Files lack conversation context. Check for skills
- "This doesn't need a formal skill" → If a skill exists, use it
