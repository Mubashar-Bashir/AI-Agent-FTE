# Standardized Claude Code Skill Template

This document provides a standardized template for creating skills according to Claude Code standards.

## Skill Structure

Every skill follows this directory structure:

```
skill-name/
├── SKILL.md (required)
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation and reference materials
└── assets/           # Optional: files used in output
```

## SKILL.md Template

```markdown
---
name: skill-name
description: Comprehensive description of what the skill does and when to use it. Include specific triggers/contexts for when to use it.
---

# Skill Name

Brief overview of what the skill does.

## Overview

More detailed explanation of the skill's purpose and functionality.

## Usage

When to use this skill and what problems it solves.

## Implementation Details

Specific details about how the skill works, including examples, code snippets, or reference material.
```

## Key Components Explained

### 1. YAML Frontmatter
- `name`: The skill name (lowercase, hyphenated)
- `description`: Primary triggering mechanism; include what the skill does and specific contexts for use

### 2. Required Sections
- **Overview**: What the skill does
- **Usage**: When to use the skill
- **Implementation Details**: How to use the skill effectively

### 3. Optional Directories

#### scripts/
- For executable code (Python, Bash, etc.)
- Use when the same code is repeated frequently
- Include testing for scripts to ensure they work

#### references/
- For documentation and reference materials
- Use when Claude needs to reference information while working
- Keep detailed information here to keep SKILL.md lean
- Include grep search patterns for large files

#### assets/
- For files used in output (templates, icons, boilerplate code)
- Files not intended to be loaded into context but used in final output
- Examples: HTML templates, logo files, configuration templates

## Best Practices

### 1. Concise is Key
- Default assumption: Claude is already smart
- Only add context Claude doesn't already have
- Prefer concise examples over verbose explanations
- Keep SKILL.md under 500 lines to minimize context bloat

### 2. Progressive Disclosure
- Metadata (name + description): Always in context (~100 words)
- SKILL.md body: When skill triggers (<5k words)
- Bundled resources: As needed by Claude

### 3. Appropriate Degrees of Freedom
- **High freedom**: When multiple approaches are valid
- **Medium freedom**: When a preferred pattern exists
- **Low freedom**: When operations are fragile and error-prone

### 4. Proper Organization
- Move detailed information to reference files
- Link to references from SKILL.md
- Avoid deeply nested references (keep one level deep)
- Include table of contents for long reference files (>100 lines)

### 5. What NOT to Include
- README.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, CHANGELOG.md
- Only include essential files that directly support functionality
- No auxiliary context about the creation process

## Skill Creation Process

1. **Understand**: Gather concrete examples of how the skill will be used
2. **Plan**: Identify reusable scripts, references, and assets needed
3. **Initialize**: Use init_skill.py to create the template structure
4. **Develop**: Add content to SKILL.md and bundled resources
5. **Package**: Use package_skill.py to validate and package the skill
6. **Iterate**: Improve based on real usage

## Example: Creating a New Skill

```bash
# 1. Initialize the skill
python .claude/skills/skill-creator/scripts/init_skill.py my-new-skill --path .claude/skills/

# 2. Edit the SKILL.md file
# 3. Add scripts, references, or assets as needed
# 4. Test the skill
# 5. Package the skill
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/my-new-skill/
```

## Common Skill Types

### Data Processing Skills
- Description: Handle specific data formats (CSV, JSON, etc.)
- Use when: Working with structured data files
- Resources: Parsing scripts, validation tools, format references

### Documentation Skills
- Description: Generate specific document types (API docs, reports, etc.)
- Use when: Creating standardized documentation
- Resources: Templates, style guides, example documents

### Development Skills
- Description: Support specific development tasks (linting, testing, etc.)
- Use when: Performing development operations
- Resources: Scripts, configuration files, best practices guides

### Integration Skills
- Description: Connect Claude to external tools or services
- Use when: Interfacing with APIs, databases, or external systems
- Resources: Authentication scripts, API references, connection templates
```
