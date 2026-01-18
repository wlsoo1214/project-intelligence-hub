from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TaskItem(BaseModel):
    # Title is required. We use description to guide the AI.
    title: str = Field(description="A concise, action-oriented summary of the task")
    
    description: Optional[str] = Field(default="", description="Detailed context")
    
    status: str = Field(default="pending", description="pending, in-progress, or completed")
    
    priority: str = Field(default="medium", description="high, medium, or low")
    
    owner: Optional[str] = Field(default="Unassigned", description="Name of person responsible")
    
    deadline: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD format")
    
    source_evidence: Optional[str] = Field(default=None, description="The specific quote that justified this task")

class ExtractionResult(BaseModel):
    project_name: Optional[str] = Field(description="Inferred name of the project")
    meeting_date: Optional[str] = Field(description="Date of the meeting")
    summary: str = Field(description="Executive summary of the document")
    tasks: List[TaskItem] = Field(description="List of extracted action items")

class GitHubCommit(BaseModel):
    commit_hash: str
    author: str
    message: str
    timestamp: str