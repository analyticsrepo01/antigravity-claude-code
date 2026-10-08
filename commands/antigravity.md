---
description: Delegate an autonomous coding task, refactoring, or test execution to Google Antigravity with Gemini (BYOK)
allowedTools:
  - antigravity_task
  - antigravity_consult
  - antigravity_review
  - antigravity_status
---

# Antigravity Task Orchestrator

You have access to the Antigravity engine powered by Google Gemini (BYOK) through the `antigravity` MCP tools.

The user has requested the following task:
"$ARGUMENTS"

### Execution Instructions:
1. Check if the task is an actionable coding assignment, an architectural inquiry, or a code review request.
2. If it is an actionable coding task (e.g. creating files, refactoring, fixing bugs):
   - Call `antigravity_task` with `task="$ARGUMENTS"`.
3. If it is an architectural question or algorithmic inquiry:
   - Call `antigravity_consult` with `question="$ARGUMENTS"`.
4. If it asks to review current changes or a diff:
   - Call `antigravity_review` with the target scope.
5. After the tool returns, provide a clean executive synthesis:
   - What Antigravity accomplished
   - Which files were modified or created
   - Commands executed and tests run
   - Any follow-up steps recommended for the user
