# Natural Language Router Guide

This document describes how user natural language inputs are routed to target system CLI commands.

## 1. Overview
The Natural Language Router acts as the parser and gateway for all plain English command operations. It intercepts user queries, expands pronouns, extracts arguments, and maps the request to the exact system CLI command.

## 2. Command Translation Mapping
The router maps input phrases to CLI commands using direct matches, regular expressions, and LLM translations:

| Plain English Input | Translated Command | Subsystem |
|---|---|---|
| "Show open GitHub PRs" | `aios github prs` | GitHub Intelligence |
| "Deploy the lead generation workflow" | `aios workflow deploy` | Automation Intelligence |
| "Create a project for hackathon" | `aios project create hackathon` | Project Intelligence |
| "Show today's priorities" | `aios today` | Personal Intelligence |
| "Create agency lead" | `aios agency leads create` | Agency Intelligence |
| "Generate proposal" | `aios agency proposals generate` | Agency Intelligence |
| "Analyze repository" | `aios project status` | Project Intelligence |
| "Create reminder" | `aios reminders create` | Personal Intelligence |
| "Start research project" | `aios research learn` | Research Intelligence |

## 3. Translation Layer Details
1. **Case Preservation**: Argument values (e.g. project name `"AI_Tutor"`) are extracted preserving original casing to prevent filesystem or metadata mismatches.
2. **Context Fallback**: If a command parameter is missing in the query, the router attempts to extract it from the persistent context engine before failing or prompting.
3. **Execution**: Once routed, the CLI commands run directly inside the kernel context using the command dispatcher, printing styled output to the terminal.
