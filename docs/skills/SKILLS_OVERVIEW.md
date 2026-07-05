# AI OS Skill System Specification

This document details the modular **Skill System** architecture of the Personal AI OS, allowing extensibility without requiring modifications to the Kernel.

---

## 1. Overview & Architecture

The Skill System transitions the Personal AI OS from a monolithic command runner into a modular operating system. All operational capabilities (agents, commands, prompt templates, and tools) are packaged as standalone "Skills" loaded dynamically at bootstrap.

```
                  +----------------------------------+
                  |           CommandRegistry        |
                  +-----------------+----------------+
                                    | Registers / Unregisters Commands
                                    v
+-----------------+       +---------+--------+       +-------------------+
|     Kernel      |------>|   SkillManager   |<----->|   SkillRegistry   |
+-----------------+       +---------+--------+       +-------------------+
                                    | Loads
                                    v
                          +---------+--------+
                          |   skills/        | (Local Workspace Root)
                          |   ├── developer/ |
                          |   ├── career/    |
                          |   └── ...        |
                          +------------------+
```

---

## 2. Directory Layout

Every Skill occupies a subdirectory inside `skills/` and must adhere to the following structure:

```
skills/<skill_id>/
├── skill.toml       # Required: Skill Metadata definitions
├── README.md        # Required: User manual and specifications
├── commands.py      # Required: Python module implementing register_commands()
├── prompts/         # Optional: Folder containing Markdown prompt templates
└── agent.py         # Optional: Custom logic or agent specifications
```

### skill.toml schema
```toml
[skill]
id = "developer"
name = "Developer Mode Skill"
version = "1.0.0"
author = "Personal AI OS"
description = "Repository scanning and developer mode tools."
category = "Developer"
commands = ["review repository", "explain file"]
required_tools = ["filesystem", "git"]
required_models = ["claude-3-5-sonnet"]
required_memory = []
prompt_directory = "prompts"
```

---

## 3. Skill Lifecycle

The `SkillManager` supports a complete lifecycle:

1. **Discovery**: Scans the workspace `skills/` directory at startup and loads `skill.toml`.
2. **Installation**: Copies a skill directory to `skills/` and registers its metadata.
3. **Enablement**: Registers the skill's commands in `CommandRegistry`.
4. **Disablement**: Unregisters the skill's commands from `CommandRegistry`.
5. **Uninstallation**: Unregisters commands, removes metadata, and deletes the skill folder.
6. **Reload**: Dynamically updates metadata and re-registers commands.

---

## 4. Extension Guide

To create a new skill (e.g. `finance`):
1. Create directory `skills/finance/`.
2. Write `skill.toml` defining commands (e.g. `analyze expenses`).
3. Implement `commands.py` with:
   ```python
   from aios.services.command.metadata import CommandCategory, CommandMetadata

   def register_commands(registry, kernel, conv_manager) -> None:
       registry.register_command(
           CommandMetadata(
               name="analyze expenses",
               description="Analyze transaction history.",
               category=CommandCategory.AUTOMATION,
               required_agent="None",
               required_tools=["filesystem"],
               example_usage="analyze expenses statements.csv",
           ),
           lambda args: print("Analyzing expenses...")
       )
   ```
4. Place prompt templates in `skills/finance/prompts/`.
5. Start AI OS; the skill will load and register automatically.
