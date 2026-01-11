# Using Superpowers - Workflow Reference

## Overview
Establishes how to find and use skills, requiring Skill tool invocation before ANY response including clarifying questions.

## Core Rule
Invoke relevant or requested skills BEFORE any response or action. Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

## Decision Flow
```
User message received
         ↓
Might any skill apply? → YES → Invoke Skill tool
         ↓ NO
Continue with response
```

## How to Access Skills
- **In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.
- **In other environments:** Check your platform's documentation for how skills are loaded.

## Key Principles
- If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.
- IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.
- This is not negotiable. This is not optional. You cannot rationalize your way out of this.

## Skill Invocation Process
1. Assess if any skill applies to the current task
2. Use the Skill tool to invoke the relevant skill
3. Follow the skill's instructions directly
4. Integrate the skill's output into your response