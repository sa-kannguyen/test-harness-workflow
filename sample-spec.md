# Sample Spec - US0001

## Feature
User can create a task from quick add box on dashboard.

## Context
Current dashboard only shows existing tasks. Users need a fast way to capture tasks without opening a separate page.

## Functional Requirements
1. Show quick-add input on dashboard header.
2. User enters title and presses Enter to create task.
3. On success, new task appears on top of task list.
4. Empty title should show validation error.
5. API should require authenticated user.

## Non-functional
- Response under 500ms for create task API.
- Clear error messages for validation and auth failure.

## Out of Scope
- Editing/deleting task.
- Due date and tagging.
