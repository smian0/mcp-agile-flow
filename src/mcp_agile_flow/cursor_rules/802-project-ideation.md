---
description: Use when the user wants to start a new project or transform an initial idea into a structured project outline
globs: null
alwaysApply: false
---

# Project Ideation Guide

## Context
- When a user wants to start a new project from an initial idea
- When transforming unstructured project concepts into a structured outline
- When kicking off the agile workflow process
- When establishing the foundation for further documentation (BRD/PRD)

## Requirements
- Elicit key project information through a conversational approach
- Generate a structured project ideation document using the template
- Guide users from initial idea to more detailed project planning
- Capture core project elements: overview, audience, features, impact, criteria
- Ensure all sections of the template are appropriately addressed
- Provide clear direction on next steps in the workflow
- Use the project-ideation template as the foundation for the document

## Examples
<example>
User: "I have an idea for a new e-commerce platform focusing on handmade crafts."

AI: "That sounds interesting! Let's structure this idea into a project. I'll help you create a project ideation document to capture the key elements of your concept.

What specific problem or opportunity are you addressing with this handmade crafts e-commerce platform?"

User: "Existing marketplaces take too large a commission and don't provide good tools for artisans to tell their stories."

AI: "Great insight. And who would be the primary audience for this platform?"

[After gathering key information]

AI: "I've created a project ideation document for your handmade crafts marketplace. It captures your core idea, target audience, key features, and success criteria. I've also outlined the next steps in developing this project, including creating a Business Requirements Document.

Would you like me to make any adjustments to this project outline before we proceed?"
</example>

<example type="invalid">
User: "I have an idea for a new e-commerce platform."

AI: "Here's a BRD document for your e-commerce platform."

[AI skips the project ideation phase and jumps directly to creating formal documentation without gathering sufficient information or using the proper template]
</example>

## Critical Rules
  - ALWAYS use the project-ideation template as the foundation for new projects
  - NEVER skip directly to BRD/PRD creation before completing a project ideation
  - Elicit information conversationally rather than requesting the user fill in a form
  - Ensure all sections have meaningful content before considering the ideation complete
  - Guide the user to the next step (typically BRD creation) after project ideation
  - Store project ideation documents in the ai-docs directory
  - Document should be named "project-ideation.md" in the ai-docs root directory 