# Repository Discovery Spec
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the algorithms and interfaces for automatically identifying repository boundaries and staging version control adapters.
* **Scope**: Governs Git and mercurial root detection, submodule boundaries, and VCS registries.
* **Audience**: Backend Developers, Systems Architects, and AI developers.
* **Related Documents**:
  * [workspace/README.md](file:///Users/anzarakhtar/aios/docs/workspace/README.md) - Workspace Foundation hub.
  * [workspace/project_discovery/README.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/README.md) - Project Discovery navigation hub.

---

## 1. Automatic Root Boundary Discovery

A user's workspace directory can contain multiple separate code repositories, git submodules, or unversioned project directories. The AI OS must locate these boundaries to establish the logical context for execution.

The discovery logic uses the **Boundary Parent Walk** algorithm:
1. **Target Folder Scanning**: Start at a given path (e.g. workspace root).
2. **Indicator Detection**: Look for specific folders/files signifying repository roots:
   * **Git**: `.git` directory or `.git` link file (submodules).
   * **Mercurial**: `.hg` directory.
   * **Subversion**: `.svn` directory.
3. **Submodule Isolation**: If a subfolder contains a `.git` indicator, it is registered as a child repository nested under the parent workspace, preventing root-level tools from executing actions on it without explicit target flags.

```
[Workspace Directory Root] (Scan Start)
           |
           +---> project_a/ (Contains .git/) ===> Register GitRepository A
           |
           +---> project_b/ (Contains .git/ & sub_module_x/.git)
           |       |
           |       +---> project_b/ ===> Register GitRepository B
           |       +---> sub_module_x/ ===> Register Nested GitRepository C
           |
           +---> project_c/ (No VCS folder) ===> Register unversioned Project folder
```

---

## 2. VCS Adapter Interface

To support multiple version control systems, the AI OS defines a unified **`VCSAdapter`** interface:

```python
class VCSAdapter(ABC):
    @abstractmethod
    def get_vcs_type(self) -> str:
        """Return identifier (e.g. 'git', 'hg')."""
        pass

    @abstractmethod
    def get_root_path(self) -> str:
        """Return the absolute path to the repository root directory."""
        pass

    @abstractmethod
    def get_current_branch(self) -> str:
        """Fetch active branch or revision name."""
        pass

    @abstractmethod
    def get_last_commit_hash(self) -> str:
        """Fetch the latest revision hash string."""
        pass
```

* **Concrete Implementations**: The system defaults to `GitAdapter` using local command line processes (e.g. `git rev-parse --show-toplevel`) or Python git packages.
* **Fallback Behavior**: If no version control directory is found, the system binds the project to the `NullVCSAdapter`, allowing files to be edited locally but disabling Git-specific capabilities like commits or logs.
