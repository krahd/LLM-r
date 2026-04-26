# GUI Plugin Planning

## Goals
- Provide a user-friendly GUI for LLM-r, focused on composition and automation workflows.
- Allow users to send prompts, select macros, review plans, and approve/execute actions.
- Integrate with Ableton Live (as a device, Max for Live, or standalone desktop app).

## Options

### 1. Ableton Device (Max for Live)
- Pros: Native to Ableton, direct access to Live API, familiar to users.
- Cons: Limited UI flexibility, requires Max for Live license, more complex deployment.

### 2. Standalone Desktop App (Electron, PyQt, etc.)
- Pros: Full UI flexibility, cross-platform, can communicate with LLM-r API over localhost.
- Cons: Separate from Ableton, requires window management.

### 3. Hybrid
- Max for Live device for basic control, desktop app for advanced features.

## Requirements
- Display available macros and allow selection.
- Input box for prompts (with validation).
- Plan review/approval UI (show actions, destructive flag, etc.).
- Execution controls (dry-run, approve, execute).
- Status/log output.

## Next Steps
- Decide on initial platform (Max for Live vs. desktop app).
- Create wireframes for core UI.
- Define API endpoints needed for GUI.
- Prototype basic GUI (e.g., Electron + React, or Max for Live patch).

---

*Contributions and feedback welcome!*
