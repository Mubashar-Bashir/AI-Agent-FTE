# Claude Code Skill Creation Guide

This guide provides a comprehensive approach to creating skills following Claude Code standards and best practices.

## Understanding Claude Code Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools. They transform Claude from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

### What Skills Provide
1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### 1. Concise is Key
The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

- Default assumption: Claude is already very smart
- Only add context Claude doesn't already have
- Challenge each piece of information: "Does Claude really need this explanation?"
- Prefer concise examples over verbose explanations

### 2. Set Appropriate Degrees of Freedom
Match the level of specificity to the task's fragility and variability:

- **High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach
- **Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior
- **Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### 3. Progressive Disclosure Design Principle
Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

## Skill Anatomy

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

### SKILL.md Structure

#### Frontmatter (YAML)
Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.

```yaml
---
name: skill-name
description: Comprehensive description of what the skill does and when to use it. Include specific triggers/contexts for when to use it.
---
```

**Description Guidelines:**
- Include both what the Skill does and specific triggers/contexts for when to use it
- Include all "when to use" information here - Not in the body
- Example: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

#### Body (Markdown)
Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

## Bundled Resources

### Scripts (`scripts/`)
Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

### References (`references/`)
Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both

### Assets (`assets/`)
Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

## Progressive Disclosure Patterns

### Pattern 1: High-level guide with references
```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

### Pattern 2: Domain-specific organization
```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

### Pattern 3: Conditional details
```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

**Important guidelines:**
- **Avoid deeply nested references** - Keep references one level deep from SKILL.md
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents

## Skill Creation Process

### Step 1: Understanding the Skill with Concrete Examples
To create an effective skill, clearly understand concrete examples of how the skill will be used.

**Sample questions:**
- "What functionality should the skill support?"
- "Can you give some examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

### Step 2: Planning the Reusable Skill Contents
Analyze each example by:
1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

**Examples:**
- PDF rotation: A `scripts/rotate_pdf.py` script would be helpful
- Frontend webapp: An `assets/hello-world/` template containing boilerplate
- BigQuery queries: A `references/schema.md` file documenting schemas

### Step 3: Initializing the Skill
Use the `init_skill.py` script to create the template:

```bash
python .claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:
- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

### Step 4: Editing the Skill
Remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Claude.

#### Learn Proven Design Patterns
- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats**: See references/output-patterns.md for template and example patterns

#### Start with Reusable Skill Contents
Begin implementation with reusable resources: `scripts/`, `references/`, and `assets/` files.

- Added scripts must be tested by actually running them
- Delete example files and directories not needed for the skill

#### Update SKILL.md
Always use imperative/infinitive form in writing.

### Step 5: Packaging a Skill
Once development is complete, package the skill:

```bash
python .claude/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:
```bash
python .claude/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:
1. **Validate** the skill automatically
2. **Package** the skill if validation passes, creating a .skill file

### Step 6: Iterate
**Iteration workflow:**
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

## Design Patterns

### Sequential Workflows
For complex tasks, break operations into clear, sequential steps:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

### Conditional Workflows
For tasks with branching logic, guide Claude through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

### Template Pattern
Provide templates for output format:

```markdown
## Report structure

ALWAYS use this exact template structure:

# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```

### Examples Pattern
Provide input/output pairs for quality output:

```markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

Follow this style: type(scope): brief description, then detailed explanation.
```

## Quality Assurance

### What to Not Include in a Skill
- README.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, CHANGELOG.md
- Auxiliary context about the creation process
- Setup and testing procedures
- User-facing documentation

### Validation Checklist
- [ ] YAML frontmatter has `name` and `description` fields
- [ ] Description includes specific triggers/contexts
- [ ] SKILL.md is under 500 lines
- [ ] Detailed information moved to reference files
- [ ] Scripts tested and functional
- [ ] All necessary resources included
- [ ] No unnecessary documentation files

## Common Skill Categories

### Development Skills
- Code linting and formatting
- Testing frameworks
- Build and deployment tools
- Version control operations

### Data Skills
- File format processing (JSON, CSV, XML, etc.)
- Database operations
- API integration
- Data transformation

### Documentation Skills
- Report generation
- API documentation
- Technical writing
- Content management

### System Skills
- File operations
- Process management
- Environment setup
- Configuration management

Following this guide will ensure your skills are well-structured, efficient, and follow Claude Code standards for maximum effectiveness.