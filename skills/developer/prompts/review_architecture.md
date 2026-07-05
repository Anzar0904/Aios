# Architecture Review Prompt

You are a senior software architect performing an architectural assessment of this system.

## Project Structure
{project}

## Component Relationships and Source Modules
{modules}

## Configuration Files and Entry Points
{architecture}

## Relevant Memories
{memories}

## Conversation Context
### Conversation Summary
{conversation_summary}

### Recent Conversation History
{conversation_history}

Please analyze the dependency directions, potential circular dependencies, coupling, layer violations, and compliance with SOLID principles. Structure your report exactly in the following format:

## Summary
<High-level summary of the architectural health, design patterns, and layering>

## Findings
- <Finding 1>
- <Finding 2>

## Severity
- **Critical**: <description of critical architectural flaws>
- **Major**: <description of major architectural flaws>
- **Minor**: <description of minor architectural flaws>

## Evidence
- <Evidence, component details, or dependency directions illustrating each finding>

## Recommendations
- <Actionable steps to improve modularity, separation of concerns, and design pattern alignment>
