# Agent guidance

## Running the project

- Before starting or rebuilding the app, check whether it is already running in Docker or on a local port.
- Reuse the existing instance for inspection and interaction. Do not start a duplicate server in another terminal.
- Start a new process only when no usable instance exists or the task explicitly requires a fresh build or isolated run.

## Implementation

- Make the smallest production-ready change that fully meets the task requirement.
- Follow existing project patterns and keep code, files, and structure focused and uncluttered.
- Avoid speculative abstractions, duplicate logic, unnecessary dependencies, and unrelated refactors.
- Preserve existing behavior outside the requested scope, and verify the change with the relevant checks.
