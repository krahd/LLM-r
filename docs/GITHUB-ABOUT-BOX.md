# GitHub About Box — Suggested copy

Short description (one line):

LLM-r is an Ableton Live LLM bridge (AbletonOSC automation)

Long description (2–3 sentences):

LLM-r bridges Ableton Live and large language models to automate music-production workflows via OSC and Modelito. It provides a local FastAPI server, an optional PyQt GUI scaffold, a macro system, and a planner to safely generate and execute action sequences.

Suggested topics (copy into GitHub topics):

- llm
- ableton
- modelito
- osc
- music
- automation
- plugin
- python

Usage (quick): paste the short description into the repository About box. To set programmatically with the GitHub CLI:

```bash
gh repo edit --description "LLM-r is an Ableton Live LLM bridge"
gh repo edit --add-topic llm --add-topic ableton --add-topic modelito --add-topic osc --add-topic music --add-topic automation --add-topic plugin
```
# GitHub About Box

This document stores copy-ready metadata for the repository's **GitHub About** section.

## Short description

`LLM-r bridges Ableton Live and LLM agents via AbletonOSC + Modelito for safe music-production automation.`

## Website

If you publish docs or demos, add the primary URL in the About box website field.

Suggested default while no public site exists:

`https://github.com/<org-or-user>/LLM-r`

## Suggested topics

- ableton-live
- abletonosc
- llm
- ai-music
- music-production
- automation
- fastapi
- python
- modelito
- agent-tools

## Maintainer checklist

When releasing a new version, verify the About box still matches current capabilities:

1. Confirm description reflects the latest release scope.
2. Update topics if capabilities significantly expand (e.g., GUI plugin release).
3. Ensure website field points to the canonical docs/demo page.
4. Keep this file and `README.md` metadata guidance in sync.
