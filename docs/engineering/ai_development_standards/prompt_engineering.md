# Prompt Engineering & Compaction Standards
**Engineering Bible — Milestone 6**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Prompt Template Isolation

To keep code decoupled from model prompts, all prompt templates must reside in external files under the appropriate directories.

### Isolation Rules
* **No Inline Prompts**: Defining system prompts or templates as inline Python string literals is prohibited.
* **Storage Paths**: System-wide prompts are saved in [prompts/](file:///Users/anzarakhtar/aios/prompts/). Skill-specific prompts are saved in the skill's `prompts/` directory (e.g. `skills/my_skill/prompts/`).
* **Markdown Formatting**: Prompts must be saved as Markdown files (`.md`) to make them easy to read and maintain.

---

## 2. Structured Prompt Engineering

Prompt templates must use a structured layout that includes the following sections:
1. **Objective**: A clear statement of what the model must accomplish.
2. **Context**: Placeholders for dynamic data (e.g. active workspace files or git status output).
3. **Constraints**: Limits on the output format (e.g., "Output only the code diff, omitting markdown explanations").
4. **Examples (Few-Shot)**: Structured examples of inputs and expected outputs to improve model accuracy.

---

## 3. Dialogue Compaction Rules

To manage token usage and prevent context window overflow:
* **The 10-Turn Threshold**: The system monitors dialogue lengths during interactive sessions. If a conversation exceeds **10 turns**, compaction is triggered.
* **Pruning Logic**:
  * The system keeps the **last 4 messages** verbatim to maintain immediate conversation context.
  * The preceding 6 or more messages are sent to the model to generate a summary block.
* **Summary Schema**: The generated summary captures key decisions, action items, and open questions, replacing the pruned messages in the active dialogue entity.

---

*Engineering Bible AI Development Standards · Personal AI OS · Sprint 8 M6 · Governed by [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md)*
