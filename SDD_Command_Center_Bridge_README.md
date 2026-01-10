# SDD Command Center Bridge

This project implements the SDD (Spec-Driven Development) Command Center Bridge as requested. The system provides tracking and monitoring capabilities for FTE features through Obsidian integration.

## Components Created

### 1. SDD Tracker (`30_Specifications/SDD_Tracker.md`)
- Contains Dataview tables to monitor all files with `#FTE-Feature` tag
- Shows status, current step, percentage completion, and next steps

### 2. Spec Template (`30_Specifications/spec_template.md`)
- Pre-formatted template with required YAML frontmatter
- Includes all required fields: tags, status, current_step, percent, next_step, last_cmd

### 3. Dashboard Integration (`00_Workspace/Dashboard.md`)
- Added magic link at the top: `![[30_Specifications/SDD_Tracker#Active Feature Tracking]]`
- Connects the main dashboard to the SDD tracking system

### 4. Sample Feature Spec (`30_Specifications/sample_feature_spec.md`)
- Example specification file demonstrating the required format
- Includes the YAML frontmatter with #FTE-Feature tag

### 5. Metadata Update Scripts
- `update_sdd_metadata.sh` - Bash script to update YAML frontmatter
- `update_sdd_metadata.py` - Python script to update YAML frontmatter (more robust)
- Enhanced `sync_to_obsidian.sh` to include 30_Specifications directory

## Usage

When running SDD commands like `/sp.specify`, the system will update the spec file's metadata:

```bash
# Example: After running /sp.specify, the spec file gets updated
./update_sdd_metadata.py specs/myfeature/spec.md "Specification" 25 "/sp.plan"
```

This will update the YAML frontmatter to reflect:
- status: "🔄 In Progress"
- current_step: "Specification"
- percent: 25
- next_step: "/sp.plan"
- last_cmd: "/sp.plan"

The Dataview table in the SDD Tracker will automatically reflect these changes in Obsidian.