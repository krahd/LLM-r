# Safety Policy

Capability safety levels:

- `safe`: no extra approval required.
- `confirm`: destructive actions requiring explicit execution approval.

Current destructive operations include stop-all-clips, track delete, scene delete, and clip delete.

Execution controls:

- `dry_run=true` for payload simulation.
- `approved=true` to execute plans containing destructive actions.
