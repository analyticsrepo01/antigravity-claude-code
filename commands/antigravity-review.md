---
description: Run an in-depth code and security review on your active changes using Antigravity and Gemini
allowedTools:
  - antigravity_review
  - Bash(git diff *)
---

# Antigravity Autonomous Code Review

Please conduct a rigorous code and security review using Antigravity powered by Google Gemini.

1. Inspect active git changes using `git diff HEAD`.
2. Invoke `antigravity_review` with the active diff, passing focus parameter if specified in: "$ARGUMENTS" (e.g. security, performance, logic).
3. Present the review findings categorized into:
   - 🚨 **Critical Bugs & Logic Errors**
   - 🛡️ **Security Concerns (OWASP, injections, leaks)**
   - ⚡ **Performance & Optimization Opportunities**
   - 💡 **Actionable Recommendations**
