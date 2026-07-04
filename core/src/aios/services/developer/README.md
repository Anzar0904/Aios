# Developer Agent v2: Intelligent Repository Analysis

This package upgrades the `DeveloperAgent` from a simple prompt-forwarding agent into a rich repository context-aware agent.

---

## 1. Components

### RepositoryScanner
The `RepositoryScanner` is responsible for inspecting the workspace root path and retrieving:
- Project Name, Root Path, and Active Git Branch.
- Git Status and the last 10 commit logs.
- A configurable depth directory tree.
- README file contents (capped to avoid context limit overflow).
- Ecosystem details (package manager, languages, frameworks, build systems, test frameworks).

### CodeIndex
The `CodeIndex` performs a lightweight, non-embedding index of codebase structure, collecting:
- Core source and test directories.
- Known entry points (`main.py`, `cli.py`, etc.).
- Active configuration files (`pyproject.toml`, `package.json`, etc.).
- Largest files in the repository.
- A list of open `TODO` and `FIXME` comments from files of supported programming languages.

### WorkspaceSummary
Synthesizes the results of `RepositoryScanner` and `CodeIndex` into a clean, structured `WorkspaceSummary` object containing the following top-level categories:
- **Project**
- **Languages**
- **Frameworks**
- **Architecture**
- **Modules**
- **Dependencies**
- **Tests**
- **Git Status**
- **Recent Activity**
- **Open TODOs**

### PromptBuilder
Loads prompt templates from `.md` files dynamically, formats the structured `WorkspaceSummary` categories, user intent details, and relevant retrieved memories, and interpolates them safely into the template before querying the LLM adapter.

---

## 2. Dynamic Prompt Templates
Prompt templates are located under `prompts/developer/`:
- **[analyze_repository.md](file:///Users/anzarakhtar/aios/prompts/developer/analyze_repository.md)**: Used when executing the `AnalyzeRepository` action.
- **[summarize_architecture.md](file:///Users/anzarakhtar/aios/prompts/developer/summarize_architecture.md)**: Used when executing `SummarizeArchitecture`.
- **[git_review.md](file:///Users/anzarakhtar/aios/prompts/developer/git_review.md)**: Used when executing `GitReview`.
- **[explain_file.md](file:///Users/anzarakhtar/aios/prompts/developer/explain_file.md)**: Used when executing `ExplainFile`.
