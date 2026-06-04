---
name: create-new-skill
description: >
  Use this skill to dynamically create a new skill for the Hermes Agent. 
  When the user asks you to learn a new task or perform a complex activity that is not currently part of your skills, you should execute this skill to write a new SKILL.md file and save it to the skills directory.
version: 1.0.0
author: Hermes Finance Agent
license: MIT
required_environment_variables: []
tags:
  - meta
  - learning
  - dynamic
---

## Overview

This skill allows you to program yourself. When you realize a user has asked for a complex workflow that you might need to repeat, or when the user explicitly asks you to "learn" or "create a skill" for a task you just completed, you can write a new skill definition.

## Procedure

### Step 1 — Analyze the Request
- Understand the steps required to complete the new task.
- Determine the required inputs, outputs, and any tools or APIs needed.
- Write a clear, step-by-step procedure.

### Step 2 — Create the SKILL.md Content
You must generate a valid YAML frontmatter and Markdown body for the skill, following the exact same format as this file. 
The YAML must contain: `name`, `description`, `version`, `author`, `license`, `tags`.
The body must contain: `## Overview` and `## Procedure`.

### Step 3 — Save the Skill
Use your `execute_code` or `write_file` tool to create a new directory inside `/root/.hermes/skills/` (e.g., `/root/.hermes/skills/my-new-skill/`) and write the generated Markdown content to `SKILL.md` inside that directory.

Example python code to execute:
```python
import os

skill_name = "my-new-skill"
skill_dir = f"/root/.hermes/skills/{skill_name}"
os.makedirs(skill_dir, exist_ok=True)

content = """---
name: my-new-skill
...
"""
with open(f"{skill_dir}/SKILL.md", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Skill {skill_name} created successfully!")
```

### Step 4 — Acknowledge
Tell the user that the new skill has been learned and is now available in your repertoire.
