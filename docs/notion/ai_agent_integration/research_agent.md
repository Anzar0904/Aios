# Notion Intelligence — Research Agent Integration
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Research Agent's interface mappings, background query tools, and workspace document templates.
* **Scope**: Governs prompt templates and execution flows for research workflows.
* **Audience**: AI Prompt Engineers, System Architects, and Integration Testers.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Page capabilities.
  * [notion/ai_agent_integration/agent_integration.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/agent_integration.md) - Agent frameworks.

---

## 1. Research Agent Execution Scope

The **Research Agent** gathers technical details, scrapes API specifications, parses documentation, and summarizes complex topics. The agent uses Notion as a central repository for research tasks:

```
 [User: REPL Command] ===> Spawns Research Agent
                                 |
                        [Read Research Database] ===> Fetch tickets & requirements
                                 |
                       [Execute Search Plans] ===> Run local scripts, read web documentation
                                 |
                     [Compile Research Report]
                                 |
                      [Publish to Notion Page] ===> Save under shared research workspace
```

---

## 2. Research Template Specification

When the Research Agent publishes findings to a Notion page, it structures the content using a standardized format:

```markdown
# [Research Topic Name]
**Status**: Completed · **Created**: [Date] · **Author**: [ResearchAgent]

---

## 1. Executive Summary
[Brief, high-level summary of the findings...]

## 2. Technical Specifications
[Detailed API endpoints, database structures, or code architecture notes...]

## 3. Analysis & Evaluation
* **Advantage A**: [Pros...]
* **Limitation B**: [Cons...]

## 4. Source Citations
* [Source Title](URL) - Key takeaways.
```

---

## 3. Tool Calls Sequence

```python
class ResearchAgentRunner:
    def run_research(self, topic: str, target_page_id: str) -> None:
        # Step 1: Query local vector memory for existing knowledge
        local_context = self.query_local_vector_memory(topic)
        
        # Step 2: Query active Notion pages to gather user notes
        notion_context = notion_tools.query_notion_search(topic, limit=3)
        
        # Step 3: Run web search using system tools
        web_context = system_tools.web_search(topic)
        
        # Step 4: Compile report using local LLM provider
        compiled_report = self.generate_report(topic, local_context, notion_context, web_context)
        
        # Step 5: Write the compiled Markdown to the target Notion page
        notion_tools.write_page_content(target_page_id, compiled_report)
```
