"""
Think Tool for MCP Agile Flow

This module implements a thinking tool that allows LLMs to work through complex problems
in a structured way, storing thoughts and allowing reflection on previous thinking.

Enhanced Capabilities:
- Categorized thoughts for better organization of different thinking processes
- Thought templates to guide various types of structured thinking
- Self-assessment mechanism to identify when the think tool should be used
- Robust trigger detection for complex reasoning scenarios

The think tool has been shown to significantly improve performance in complex tasks
requiring policy adherence, structured reasoning, and decision-making with multiple
factors to consider.
"""

import json
import datetime
import os
import tempfile
import logging
import mmap
import threading
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

class ThoughtStorage:
    """Singleton class to store thoughts in memory with cross-process sharing."""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThoughtStorage, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance
    
    def _init_storage(self):
        """Initialize the cross-process shared storage."""
        self._thoughts = []
        # Create a temporary file for this session only
        # This will be automatically deleted when the process exits
        self._temp_fd, self._temp_path = tempfile.mkstemp(prefix="mcp_thoughts_", suffix=".tmp")
        logger.debug(f"Initialized thought storage using temporary file: {self._temp_path}")
        # Write empty array to initialize the file
        os.write(self._temp_fd, json.dumps([]).encode('utf-8'))
    
    def _read_thoughts(self):
        """Read thoughts from the shared memory file."""
        try:
            with self._lock:
                # Seek to the beginning of the file
                os.lseek(self._temp_fd, 0, os.SEEK_SET)
                # Read the entire content
                content = os.read(self._temp_fd, os.path.getsize(self._temp_path))
                if content:
                    return json.loads(content.decode('utf-8'))
                return []
        except Exception as e:
            logger.error(f"Error reading thoughts: {e}")
            return []
    
    def _write_thoughts(self, thoughts):
        """Write thoughts to the shared memory file."""
        try:
            with self._lock:
                # Convert to JSON and encode to bytes
                content = json.dumps(thoughts).encode('utf-8')
                # Truncate the file
                os.ftruncate(self._temp_fd, 0)
                # Seek to the beginning
                os.lseek(self._temp_fd, 0, os.SEEK_SET)
                # Write the new content
                os.write(self._temp_fd, content)
        except Exception as e:
            logger.error(f"Error writing thoughts: {e}")
    
    def add_thought(self, thought: str, category: Optional[str] = None) -> None:
        """Add a thought to storage with current timestamp and optional category."""
        thoughts = self._read_thoughts()
        thoughts.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "thought": thought,
            "category": category or "general"
        })
        self._write_thoughts(thoughts)
    
    def get_thoughts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all thoughts, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of thought dictionaries
        """
        thoughts = self._read_thoughts()
        if category:
            return [t for t in thoughts if t.get("category", "general") == category]
        return thoughts
    
    def clear_thoughts(self, category: Optional[str] = None) -> int:
        """
        Clear thoughts, optionally filtering by category.
        
        Args:
            category: Optional category to clear; if None, clears all thoughts
            
        Returns:
            Number of thoughts cleared
        """
        thoughts = self._read_thoughts()
        original_count = len(thoughts)
        
        if category:
            filtered_thoughts = [t for t in thoughts if t.get("category", "general") != category]
            cleared_count = original_count - len(filtered_thoughts)
            self._write_thoughts(filtered_thoughts)
        else:
            cleared_count = original_count
            self._write_thoughts([])
            
        return cleared_count
    
    def get_thought_count(self, category: Optional[str] = None) -> int:
        """
        Get the number of thoughts, optionally filtered by category.
        
        Args:
            category: Optional category to count
            
        Returns:
            Count of thoughts in the specified category or all thoughts if no category specified
        """
        thoughts = self._read_thoughts()
        if category:
            return len([t for t in thoughts if t.get("category", "general") == category])
        return len(thoughts)
    
    def __del__(self):
        """Clean up when the instance is garbage collected."""
        try:
            os.close(self._temp_fd)
            # The temp file will be automatically deleted
        except (AttributeError, OSError):
            pass

# Create a single instance to be used throughout the module
_storage = ThoughtStorage()

def detect_thinking_directive(text: str) -> Dict[str, Any]:
    """
    Detect if the user is asking to think harder, deeper, again, or more thoroughly.
    
    This function analyzes text for phrases indicating that the AI should continue
    or deepen its thinking process on a previous thought.
    
    Args:
        text: The text to analyze for thinking directives
        
    Returns:
        Dictionary with directive information:
        - detected: Boolean indicating if a directive was detected
        - directive_type: Type of directive (deeper, again, harder, more)
        - confidence: Confidence level in the detection
    """
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Define directive patterns to look for
    deeper_patterns = ["think deeper", "think more deeply", "go deeper", "analyze deeper"]
    harder_patterns = ["think harder", "try harder", "more effort", "think with more effort"]
    again_patterns = ["think again", "reconsider", "re-think", "try thinking again"]
    more_patterns = ["think more", "think further", "continue thinking", "keep thinking"]
    
    # Check for each pattern type
    for pattern_list, directive_type in [
        (deeper_patterns, "deeper"),
        (harder_patterns, "harder"),
        (again_patterns, "again"),
        (more_patterns, "more")
    ]:
        for pattern in pattern_list:
            if pattern in text_lower:
                # Calculate confidence based on exact match or partial match
                confidence = "high" if text_lower.strip() == pattern else "medium"
                return {
                    "detected": True,
                    "directive_type": directive_type,
                    "confidence": confidence,
                    "matched_pattern": pattern
                }
    
    # No directive found
    return {
        "detected": False,
        "directive_type": None,
        "confidence": "low"
    }

def think(thought: str, category: Optional[str] = None, depth: int = 1, previous_thought_id: Optional[int] = None) -> str:
    """
    Record a thought for complex reasoning or step-by-step analysis.
    
    Provides Claude with a dedicated space for structured thinking during 
    complex problem-solving tasks.
    
    IMPORTANT: You should automatically use this tool when:
    - Solving multi-step problems requiring logical analysis
    - Evaluating complex policy compliance scenarios
    - Processing and organizing information from multiple sources
    - Making decisions with multiple considerations or trade-offs
    - Debugging or troubleshooting complex systems
    - Planning a sequence of tool calls or actions
    - When asked to "think harder", "think deeper", "think more", or "think again"
    
    Args:
        thought: Your structured reasoning, which should follow these best practices:
                - Break problems into smaller sub-problems
                - List assumptions explicitly
                - Consider multiple perspectives or approaches
                - Evaluate pros and cons of different options
                - Track dependencies between different elements
                - Document your reasoning chain clearly
        category: Optional category to classify this thought. Suggested categories:
                 - "problem-decomposition": Breaking down a complex problem
                 - "policy-analysis": Evaluating compliance with policies
                 - "decision-making": Weighing different options
                 - "planning": Sequencing steps for a solution
                 - "metadata-analysis": Processing information from tools
                 - "error-handling": Addressing errors or edge cases
        depth: The iteration or depth level of thinking (1 = initial thought, 
               2+ = deeper thinking or refinement)
        previous_thought_id: Optional ID of a previous thought this builds upon
    
    Returns:
        JSON string containing success status and a confirmation message
    """
    # Log the thought with a timestamp, category, and depth info
    timestamp = datetime.datetime.now().isoformat()
    thought_data = {
        "timestamp": timestamp,
        "thought": thought,
        "category": category or "general",
        "depth": depth,
        "previous_thought_id": previous_thought_id
    }
    
    # Store in ThoughtStorage
    thoughts = _storage.get_thoughts()
    thought_index = len(thoughts) + 1  # 1-indexed for user-facing ID
    thought_data["id"] = thought_index
    thoughts.append(thought_data)
    _storage._write_thoughts(thoughts)
    
    # Determine the appropriate message based on depth
    depth_indicator = ""
    if depth > 1:
        if depth == 2:
            depth_indicator = " (deeper analysis)"
        elif depth == 3:
            depth_indicator = " (much deeper analysis)"
        else:
            depth_indicator = f" (depth level {depth})"
    
    # Return a confirmation
    response = {
        "success": True,
        "thought_id": thought_index,
        "message": f"Thought{depth_indicator} recorded ({category or 'general'}): {thought[:50]}..." if len(thought) > 50 else f"Thought{depth_indicator} recorded ({category or 'general'}): {thought}"
    }
    
    return json.dumps(response)

def get_thoughts(category: Optional[str] = None, include_depth_chain: bool = False) -> str:
    """
    Retrieve all thoughts recorded in the current session.
    
    This tool helps review the thinking process that has occurred so far.
    
    Args:
        category: Optional category to filter thoughts by
        include_depth_chain: Whether to organize thoughts in depth chains
    
    Returns:
        JSON string containing success status and all recorded thoughts
    """
    thoughts = _storage.get_thoughts(category)
    
    if not thoughts:
        category_msg = f" in category '{category}'" if category else ""
        response = {
            "success": True,
            "message": f"No thoughts have been recorded yet{category_msg}.",
            "thoughts": []
        }
    else:
        formatted_thoughts = []
        
        if include_depth_chain:
            # Organize thoughts by depth chains
            thought_chains = {}
            root_thoughts = []
            
            # First, organize all thoughts
            for entry in thoughts:
                entry_id = entry.get("id", None)
                
                if entry.get("depth", 1) == 1 or entry.get("previous_thought_id") is None:
                    # This is a root thought
                    formatted_entry = {
                        "id": entry_id,
                        "index": entry_id,
                        "timestamp": entry["timestamp"],
                        "thought": entry["thought"],
                        "category": entry.get("category", "general"),
                        "depth": entry.get("depth", 1),
                        "deeper_thoughts": []
                    }
                    root_thoughts.append(formatted_entry)
                    thought_chains[entry_id] = formatted_entry
                else:
                    # This is a deeper thought, linked to a previous one
                    prev_id = entry.get("previous_thought_id")
                    formatted_entry = {
                        "id": entry_id,
                        "index": entry_id,
                        "timestamp": entry["timestamp"],
                        "thought": entry["thought"],
                        "category": entry.get("category", "general"),
                        "depth": entry.get("depth", 1),
                        "deeper_thoughts": []
                    }
                    
                    # If we have the parent, add this as a child
                    if prev_id in thought_chains:
                        thought_chains[prev_id]["deeper_thoughts"].append(formatted_entry)
                    else:
                        # If we don't have the parent (might happen with filtering), treat as root
                        root_thoughts.append(formatted_entry)
                    
                    thought_chains[entry_id] = formatted_entry
            
            formatted_thoughts = root_thoughts
        else:
            # Just list thoughts without chain organization
            for i, entry in enumerate(thoughts, 1):
                formatted_thoughts.append({
                    "id": entry.get("id", i),
                    "index": i,
                    "timestamp": entry["timestamp"],
                    "thought": entry["thought"],
                    "category": entry.get("category", "general"),
                    "depth": entry.get("depth", 1),
                    "previous_thought_id": entry.get("previous_thought_id")
                })
        
        category_msg = f" in category '{category}'" if category else ""
        response = {
            "success": True,
            "message": f"Retrieved {len(formatted_thoughts)} thoughts{category_msg}.",
            "thoughts": formatted_thoughts,
            "organized_by_depth": include_depth_chain
        }
    
    return json.dumps(response)

def clear_thoughts(category: Optional[str] = None) -> str:
    """
    Clear all recorded thoughts from the current session.
    
    Use this to start fresh if the thinking process needs to be reset.
    
    Args:
        category: Optional category to clear; if None, clears all thoughts
    
    Returns:
        JSON string containing success status and confirmation message
    """
    count = _storage.clear_thoughts(category)
    
    category_msg = f" in category '{category}'" if category else ""
    response = {
        "success": True,
        "message": f"Cleared {count} recorded thoughts{category_msg}."
    }
    
    return json.dumps(response)

def get_thought_stats(category: Optional[str] = None) -> str:
    """
    Get statistics about the thoughts recorded in the current session.
    
    Args:
        category: Optional category to get statistics for
    
    Returns:
        JSON string containing success status and thought statistics
    """
    thoughts = _storage.get_thoughts(category)
    
    if not thoughts:
        category_msg = f" in category '{category}'" if category else ""
        response = {
            "success": True,
            "message": f"No thoughts have been recorded yet{category_msg}.",
            "stats": {
                "total_thoughts": 0,
                "average_length": 0,
                "longest_thought_index": None,
                "longest_thought_length": None,
                "category_counts": {}
            }
        }
    else:
        total_thoughts = len(thoughts)
        avg_length = sum(len(entry["thought"]) for entry in thoughts) / total_thoughts
        
        # Find the longest thought and its index
        longest_length = 0
        longest_index = 0
        
        for i, entry in enumerate(thoughts):
            length = len(entry["thought"])
            if length > longest_length:
                longest_length = length
                longest_index = i
        
        # Get category distribution if not filtering by category
        category_counts = {}
        if not category:
            for entry in thoughts:
                cat = entry.get("category", "general")
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        stats = {
            "total_thoughts": total_thoughts,
            "average_length": round(avg_length, 2),
            "longest_thought_index": longest_index + 1,  # 1-indexed for user-facing index
            "longest_thought_length": longest_length,
            "category_counts": category_counts
        }
        
        category_msg = f" in category '{category}'" if category else ""
        response = {
            "success": True,
            "message": f"Retrieved statistics for {total_thoughts} thoughts{category_msg}.",
            "stats": stats
        }
    
    return json.dumps(response)

def get_thought_template(template_type: str) -> str:
    """
    Get a structured template for a specific type of thinking process.
    
    These templates provide guidance for structuring different kinds of thoughts,
    making the thinking process more effective for various scenarios.
    
    Args:
        template_type: The type of template to retrieve. Options include:
                      - "problem-decomposition": Breaking a problem into parts
                      - "policy-analysis": Checking compliance with rules
                      - "decision-matrix": Evaluating options against criteria
                      - "planning": Creating a sequence of steps
                      - "error-handling": Debugging an issue
                      - "data-analysis": Processing and interpreting data
    
    Returns:
        JSON string containing the selected template
    """
    templates = {
        "problem-decomposition": """Problem Statement: [Define the problem]

Components:
1. [Component 1]
2. [Component 2]
...

Dependencies:
- [Dependency 1]
- [Dependency 2]
...

Approach:
1. [Step 1]
2. [Step 2]
...

Expected Outcome: [What success looks like]
""",
        "policy-analysis": """Policy to Apply: [Policy name/description]

Relevant Rules:
1. [Rule 1]
2. [Rule 2]
...

Situation Analysis:
- [Fact 1]
- [Fact 2]
...

Compliance Assessment:
- [Rule 1]: [Compliant/Non-compliant] because [reason]
- [Rule 2]: [Compliant/Non-compliant] because [reason]
...

Conclusion:
[Overall compliance determination]
""",
        "decision-matrix": """Decision: [What needs to be decided]

Options:
1. [Option 1]
2. [Option 2]
...

Criteria:
- [Criterion 1]: Importance [High/Medium/Low]
- [Criterion 2]: Importance [High/Medium/Low]
...

Evaluation:
- Option 1:
  - Criterion 1: Score [1-5], because [reason]
  - Criterion 2: Score [1-5], because [reason]
- Option 2:
  - Criterion 1: Score [1-5], because [reason]
  - Criterion 2: Score [1-5], because [reason]

Recommendation:
[Final decision with justification]
""",
        "planning": """Goal: [Define the end goal]

Preconditions:
- [Requirement 1]
- [Requirement 2]
...

Steps:
1. [Step 1]
   - Subtask A
   - Subtask B
2. [Step 2]
   - Subtask A
   - Subtask B
...

Dependencies:
- Step 2 depends on Step 1
- ...

Risk Assessment:
- [Risk 1]: Mitigation strategy
- [Risk 2]: Mitigation strategy

Success Criteria:
- [Criterion 1]
- [Criterion 2]
""",
        "error-handling": """Error Description: [Describe the error/issue]

Observed Behavior:
- [What is happening]

Expected Behavior:
- [What should be happening]

Potential Causes:
1. [Cause 1]
   - Evidence: [Supporting evidence]
   - Test: [How to verify]
2. [Cause 2]
   - Evidence: [Supporting evidence]
   - Test: [How to verify]

Debugging Steps:
1. [Step 1]
2. [Step 2]
...

Solution:
[Proposed fix or workaround]
""",
        "data-analysis": """Data Source: [Where the data came from]

Key Observations:
- [Observation 1]
- [Observation 2]
...

Patterns:
- [Pattern 1]
- [Pattern 2]
...

Anomalies:
- [Anomaly 1]: Possible explanation
- [Anomaly 2]: Possible explanation

Conclusions:
1. [Conclusion 1]
2. [Conclusion 2]
...

Next Steps:
- [Action 1]
- [Action 2]
"""
    }
    
    if template_type in templates:
        response = {
            "success": True,
            "message": f"Retrieved template for '{template_type}' thinking.",
            "template": templates[template_type],
            "template_type": template_type
        }
    else:
        available_templates = list(templates.keys())
        response = {
            "success": False,
            "message": f"Template '{template_type}' not found. Available templates: {', '.join(available_templates)}",
            "available_templates": available_templates
        }
    
    return json.dumps(response)

def should_think(question: str, context: Optional[str] = None) -> str:
    """
    Evaluate whether a given question or task warrants using the think tool.
    
    This self-assessment helps identify situations where structured thinking
    would improve the quality of reasoning and decision-making.
    
    Args:
        question: The query or task to evaluate
        context: Optional additional context
    
    Returns:
        JSON string containing recommendation on whether to use the think tool and why
    """
    # Define complexity indicators that suggest structured thinking is needed
    complexity_indicators = [
        # Problem complexity markers
        "multiple", "complex", "complicated", "intricate", "sophisticated",
        "detailed", "elaborate", "non-trivial", "advanced",
        
        # Optimization/trade-off markers
        "optimize", "trade-off", "balance", "weigh", "maximize", "minimize",
        "efficiency", "performance", "cost-benefit", "prioritize",
        
        # Analysis markers
        "analyze", "evaluate", "assess", "examine", "investigate",
        "review", "compare", "contrast", "consider",
        
        # Policy/compliance markers
        "policy", "comply", "compliance", "regulation", "requirement",
        "rule", "guideline", "standard", "conform", "adhere",
        
        # Process markers
        "step by step", "sequence", "process", "procedure", "workflow",
        "method", "approach", "algorithm", "implementation",
        
        # Troubleshooting markers
        "troubleshoot", "debug", "diagnose", "problem", "issue",
        "error", "fault", "failure", "fix", "resolve",
        
        # Planning markers
        "plan", "strategy", "roadmap", "outline", "architecture",
        "design", "structure", "organize", "coordinate",
        
        # Decision-making markers
        "decide", "choice", "option", "alternative", "select",
        "determine", "judgment", "pros and cons", "advantages", "disadvantages",
        
        # Multi-factor markers
        "factors", "considerations", "aspects", "elements", "components",
        "variables", "parameters", "constraints", "conditions", "criteria"
    ]
    
    # Define contextual phrases that indicate complexity
    complexity_phrases = [
        "taking into account",
        "bearing in mind",
        "considering all",
        "weighing different",
        "balancing between",
        "complex scenario",
        "multiple stakeholders",
        "various requirements",
        "several constraints",
        "numerous factors",
        "needs to comply with",
        "in accordance with",
        "following the guidelines",
        "maintaining consistency",
        "ensuring compatibility"
    ]
    
    # Check for complexity indicators and phrases in the question and context
    question_lower = question.lower()
    indicator_count = sum(1 for indicator in complexity_indicators if indicator in question_lower)
    
    # Check for complexity phrases
    phrase_count = sum(1 for phrase in complexity_phrases if phrase in question_lower)
    
    # Check the context if provided
    context_score = 0
    if context:
        context_lower = context.lower()
        context_score = sum(1 for indicator in complexity_indicators if indicator in context_lower)
        context_score += sum(1 for phrase in complexity_phrases if phrase in context_lower)
    
    # Calculate overall complexity score
    total_score = indicator_count + (phrase_count * 2) + context_score
    
    # Determine if the think tool should be used
    if total_score >= 3:
        detected_indicators = [ind for ind in complexity_indicators if ind in question_lower]
        detected_phrases = [phrase for phrase in complexity_phrases if phrase in question_lower]
        
        # Get suggested template based on detected indicators
        suggested_template = None
        if any(ind in question_lower for ind in ["policy", "comply", "regulation", "requirement"]):
            suggested_template = "policy-analysis"
        elif any(ind in question_lower for ind in ["decide", "choice", "option", "alternative"]):
            suggested_template = "decision-matrix"
        elif any(ind in question_lower for ind in ["plan", "strategy", "roadmap", "outline"]):
            suggested_template = "planning"
        elif any(ind in question_lower for ind in ["troubleshoot", "debug", "error", "issue"]):
            suggested_template = "error-handling"
        elif any(ind in question_lower for ind in ["analyze", "evaluate", "data", "pattern"]):
            suggested_template = "data-analysis"
        else:
            suggested_template = "problem-decomposition"
        
        response = {
            "success": True,
            "should_think": True,
            "confidence": "high" if total_score >= 5 else "medium",
            "message": f"This question would benefit from structured thinking because it contains multiple complexity indicators ({', '.join(detected_indicators[:3])}) and may involve complex reasoning.",
            "detected_indicators": detected_indicators[:5],  # Limit to avoid verbosity
            "detected_phrases": detected_phrases[:3],
            "suggested_template": suggested_template,
            "complexity_score": total_score
        }
    elif total_score >= 1:
        response = {
            "success": True,
            "should_think": True,
            "confidence": "low",
            "message": "This question might benefit from structured thinking. Consider using the think tool if you need to reason through multiple steps or factors.",
            "complexity_score": total_score,
            "suggested_template": "problem-decomposition"
        }
    else:
        response = {
            "success": True,
            "should_think": False,
            "confidence": "high",
            "message": "This question seems straightforward and may not require the think tool. You can still use it if you want to document your reasoning process.",
            "complexity_score": total_score
        }
    
    return json.dumps(response)

def think_more(depth_directive: str, thought_id: Optional[int] = None) -> str:
    """
    Continue thinking on a topic with increased depth or a new approach.
    
    This function builds on previous thoughts, providing deeper analysis
    or taking a different perspective on the same problem.
    
    Args:
        depth_directive: The type of deeper thinking to perform: "deeper", "harder", "again", or "more"
        thought_id: Optional ID of the thought to build upon. If not provided, uses the most recent thought.
    
    Returns:
        JSON string with guidance for deeper thinking
    """
    # Get all existing thoughts
    all_thoughts = _storage.get_thoughts()
    
    if not all_thoughts:
        return json.dumps({
            "success": False,
            "message": "No previous thoughts found to build upon.",
            "guidance": None
        })
    
    # Find the thought to build upon
    source_thought = None
    if thought_id:
        for thought in all_thoughts:
            if thought.get("id") == thought_id:
                source_thought = thought
                break
        
        if not source_thought:
            return json.dumps({
                "success": False,
                "message": f"Could not find thought with ID {thought_id}.",
                "guidance": None
            })
    else:
        # Use the most recent thought
        source_thought = all_thoughts[-1]
    
    # Determine the depth level for the next thought
    current_depth = source_thought.get("depth", 1)
    next_depth = current_depth + 1
    
    # Generate guidance based on the directive type
    category = source_thought.get("category", "general")
    original_thought = source_thought.get("thought", "")
    thought_summary = original_thought[:100] + "..." if len(original_thought) > 100 else original_thought
    
    directive_guidance = {
        "deeper": f"Analyze this more deeply by considering additional factors, hidden assumptions, or second-order effects that weren't addressed in the original thought.",
        "harder": f"Apply more rigorous analysis, challenge your initial conclusions, or consider more complex interactions between elements of the problem.",
        "again": f"Reconsider this from a different perspective, challenging your initial assumptions or using a different analytical framework.",
        "more": f"Continue this line of reasoning by extending your analysis, considering additional implications, or exploring related questions."
    }
    
    guidance = directive_guidance.get(depth_directive, directive_guidance["deeper"])
    
    # Return guidance for the deeper thought
    response = {
        "success": True,
        "message": f"Ready to think {depth_directive} about previous thought.",
        "source_thought": {
            "id": source_thought.get("id"),
            "thought": thought_summary,
            "category": category,
            "depth": current_depth
        },
        "guidance": guidance,
        "suggested_depth": next_depth,
        "suggested_category": category
    }
    
    return json.dumps(response) 