"""
The Project Intelligence Hub is an event-driven, serverless web application. Unlike traditional project management tools that require manual updates, this system acts as an "AI Observer." It listens to project signals (uploaded meeting notes, requirements docs, code pushes), structures them into actionable data, and uses Vector Search to correlate plans with execution.
"""
# Contract/ rules between python and LLM

"""
Uses of pydantic
1. Validate correct data types
2. Prevent hallucination
3. Prevent injection attacks
4. LLM Steering: description acts as soft prompt
"""
from typing import List, Optional 
from pydantic import BaseModel // validate correct data types
from datetime import datetime

# Pydantic Class Objects
# ==========================================
# 1. The Core Task Model
# ==========================================
class TaskItem(BaseModel):
    """
    Represents a single actionable unit of work extracted from a document.
    """
    
    title: str = Field(
        ..., 
        description="A concise, action-oriented summary of the task (e.g., 'Update API Schema')."
    )
    
    description: Optional[str] = Field(
        default="", 
        description="Detailed context, requirements, or acceptance criteria found in the text."
    )
    
    # We default to 'pending' because a newly extracted task is never 'done' yet.
    status: str = Field(
        default="pending", 
        description="Current workflow state. Options: 'pending', 'in-progress', 'completed'."
    )
    
    priority: str = Field(
        default="medium", 
        description="Urgency level inferred from the text. Options: 'high', 'medium', 'low'."
    )
    
    # 'Optional' handles cases where the AI cannot find an owner. 
    # 'Unassigned' is a safer database default than Null/None.
    owner: Optional[str] = Field(
        default="Unassigned", 
        description="Name of the person responsible for this task."
    )
    
    deadline: Optional[str] = Field(
        default=None, 
        description="The due date in strictly YYYY-MM-DD format. If vague (e.g., 'next Friday'), convert to concrete date."
    )
    
    # CRITICAL FOR RAG:
    # This field proves the AI didn't hallucinate. It stores the exact quote.
    source_evidence: Optional[str] = Field(
        default=None, 
        description="The specific text snippet or quote from the document that justifies this task."
    )

    # Technical metadata (Not extracted by AI, but used by System)
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp when this task was ingested."
    )

# ==========================================
# 2. The AI Extraction Output
# ==========================================
class ExtractionResult(BaseModel):
    """
    The strict structure we force the AI to return.
    This prevents the AI from returning conversational filler like "Here are your tasks..."
    """
    
    project_name: Optional[str] = Field(
        description="The name of the project inferred from the document header or context."
    )
    
    meeting_date: Optional[str] = Field(
        description="The date of the meeting/document in YYYY-MM-DD format."
    )
    
    summary: str = Field(
        description="A high-level executive summary (2-3 sentences) of the entire document."
    )
    
    # This list allows the AI to return multiple tasks in one pass.
    tasks: List[TaskItem] = Field(
        description="A list of all action items identified in the text."
    )

# ==========================================
# 3. The GitHub Integration Model (Phase 2)
# ==========================================
class GitHubCommit(BaseModel):
    """
    Represents a code change event. Used for Semantic Linking (Phase 2).
    """
    commit_hash: str = Field(description="The unique SHA identifier of the commit.")
    author: str = Field(description="The username of the developer.")
    message: str = Field(description="The commit message content.")
    timestamp: str = Field(description="ISO 8601 timestamp of the push.")
    branch: str = Field(default="main", description="The branch where code was pushed.")
    
    # We will use this later to generate vector embeddings
    def to_embedding_text(self) -> str:
        """Helper to format commit for the Embedding Model."""
        return f"Commit by {self.author}: {self.message}"
