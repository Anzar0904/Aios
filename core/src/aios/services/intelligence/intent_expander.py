from aios.services.intent import Intent


class IntentExpander:
    def __init__(self) -> None:
        pass

    def expand(self, intent: Intent) -> str:
        action = intent.action
        raw_query = intent.parameters.get("raw_query", "")
        
        if action == "ReviewRepository":
            return (
                "Perform a senior software engineering review focusing on architecture, "
                "maintainability, security, testing, dependency management, and technical debt."
            )
        elif action == "ReviewArchitecture":
            return (
                "Conduct a software architecture review analyzing separation of concerns, "
                "coupling, modularity, package dependencies, and SOLID design compliance."
            )
        elif action == "ReviewSecurity":
            return (
                "Execute a security review identifying potential vulnerabilities like "
                "command injection, path traversal, weak inputs validation, or dependency risks."
            )
        elif action == "AnalyzeDependencies":
            return (
                "Perform a dependency analysis inspecting package configurations, version "
                "requirements, library pinning, and duplicate or bloated package references."
            )
        elif action == "GitReview" or action == "ReviewGitChanges":
            return (
                "Perform an in-depth review of staged and unstaged code modifications, "
                "explaining their purpose, highlighting potential issues, and matching them "
                "against recent commit logs."
            )
        elif action == "GenerateCommitMessage":
            return (
                "Analyze the uncommitted code diff to generate a concise, standardized, "
                "and detailed Git commit message following conventional commits format."
            )
        elif action == "GenerateReleaseNotes":
            return (
                "Summarize git commits and active uncommitted developments to draft a "
                "structured release notes changelog detailing features, fixes, and migrations."
            )
        
        return raw_query if raw_query else f"Execute {action} developer command."
