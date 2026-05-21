# Process rule for future LLM-r Copilot prompts

Use this block at the top of every future Copilot prompt:

```md
# Prompt N — LLM-r 0.6.9 release-candidate <title>

Repository: `krahd/LLM-r`  
Branch: `release/0.6.9`  
Prompt number: **Prompt N**

You do not have memory of previous prompts. You must read the repository state directly.

Before editing, read:

- `STATUS.md`
- any files explicitly relevant to this prompt

In your final response, begin with:

```text
Completed Prompt N: <title>
```

Report:

- files changed
- tests run
- exact results
- limitations
- whether `STATUS.md` was updated
```
