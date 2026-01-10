#!/bin/bash

# Helper script to update SDD spec metadata
# Usage: ./update_sdd_metadata.sh <path_to_spec_file> <step_name> <percent_value> <next_command>

SPEC_FILE="$1"
STEP_NAME="$2"
PERCENT_VALUE="$3"
NEXT_COMMAND="$4"
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

if [[ -z "$SPEC_FILE" || -z "$STEP_NAME" || -z "$PERCENT_VALUE" || -z "$NEXT_COMMAND" ]]; then
    echo "Usage: $0 <path_to_spec_file> <step_name> <percent_value> <next_command>"
    echo "Example: $0 specs/myfeature/spec.md 'Specification' 25 '/sp.plan'"
    exit 1
fi

if [[ ! -f "$SPEC_FILE" ]]; then
    echo "Error: File $SPEC_FILE does not exist"
    exit 1
fi

# Create backup
cp "$SPEC_FILE" "${SPEC_FILE}.bak"

# Update the YAML frontmatter
sed -i.bak -e "
/---/,/---/ {
  /current_step:/ s/current_step:.*/current_step: \"$STEP_NAME\"/
  /percent:/ s/percent:.*/percent: $PERCENT_VALUE/
  /next_step:/ s/next_step:.*/next_step: \"$NEXT_COMMAND\"/
  /last_cmd:/ s/last_cmd:.*/last_cmd: \"$NEXT_COMMAND\"/
  /status:/ s/status:.*/status: \"🔄 In Progress\"/
}
" "$SPEC_FILE"

echo "Updated $SPEC_FILE"
echo "  - current_step: $STEP_NAME"
echo "  - percent: $PERCENT_VALUE"
echo "  - next_step: $NEXT_COMMAND"
echo "  - last_cmd: $NEXT_COMMAND"
echo "  - status: 🔄 In Progress"