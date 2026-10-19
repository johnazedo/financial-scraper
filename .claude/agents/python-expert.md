---
name: python-expert
description: Python style and review agent for the financial-scraper library. Generic role lives in agents/python-expert.md; this file is the Claude Code harness manifest.
tools: Read Grep Glob Bash Edit Write
---

# Claude Code manifest — python-expert

> **Canonical role**: [`../../agents/python-expert.md`](../../agents/python-expert.md).
> **Canonical style rules**: [`../../AGENTS.md`](../../AGENTS.md).
>
> This file exists only to give Claude Code the frontmatter it requires
> (name, description, tools). All role guidance lives in the canonical
> agent; all style rules live in `AGENTS.md`.

When Claude Code invokes the `python-expert` sub-agent, it loads the
canonical role from `agents/python-expert.md` and follows `AGENTS.md`
for style.

Do not add rules here that duplicate `AGENTS.md` — they will drift.