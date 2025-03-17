"""
Templates for Agile documentation generation.
"""

# Project document template
PROJECT_TEMPLATE = """# Project: {project_name}

## Overview
{project_description}

## Project Metadata
- Start Date: {start_date}
- Status: {status}
- Priority: {priority}

## Project Goals
{project_goals}

## Key Metrics
{key_metrics}

## Team
{team_members}
"""

# Epic document template
EPIC_TEMPLATE = """# Epic: {epic_name}

## Overview
{epic_description}

## Epic Metadata
- Status: {status}
- Priority: {priority}
- Created: {created_date}
- Updated: {updated_date}

## Acceptance Criteria
{acceptance_criteria}

## Stories
{story_references}

## Notes
{notes}
"""

# Story document template
STORY_TEMPLATE = """# Story: {story_name}

## Overview
{story_description}

## Story Metadata
- Epic: [{epic_name}](../../../epics/{epic_filename})
- Status: {status}
- Story Points: {story_points}
- Created: {created_date}
- Updated: {updated_date}

## Acceptance Criteria
{acceptance_criteria}

## Tasks
{tasks}

## Notes
{notes}
"""

# Task document template
TASK_TEMPLATE = """# Task: {task_name}

## Overview
{task_description}

## Task Metadata
- Story: [{story_name}](../../stories/{epic_path}/{story_filename})
- Epic: [{epic_name}](../../epics/{epic_filename})
- Status: {status}
- Assigned To: {assigned_to}
- Created: {created_date}
- Updated: {updated_date}

## Checklist
{checklist}

## Notes
{notes}
"""

# Progress document template
PROGRESS_TEMPLATE = """# Project Progress: {project_name}

## Summary
{progress_summary}

## Epic Status
{epic_status_table}

## Recent Updates
{recent_updates}

## Upcoming Work
{upcoming_work}

## Blockers
{blockers}
"""


class TemplateManager:
    """
    Manages templates for Agile documentation.
    """
    
    def __init__(self):
        """
        Initialize the TemplateManager with default templates.
        """
        self.templates = {
            "project": PROJECT_TEMPLATE,
            "epic": EPIC_TEMPLATE,
            "story": STORY_TEMPLATE,
            "task": TASK_TEMPLATE,
            "progress": PROGRESS_TEMPLATE
        }
        
    def render_template(self, template_name: str, context: dict) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template to render.
            context: Dictionary of values to substitute in the template.
            
        Returns:
            Rendered template as a string.
            
        Raises:
            ValueError: If the template name is invalid.
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
            
        # Replace template variables with context values
        result = template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
            
        return result
