"""
Pydantic specification models representing the parsed structure of a specification.
"""

import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ADRSpec(BaseModel):
    title: str
    status: str = "Proposed"
    date: datetime.date = Field(default_factory=datetime.date.today)
    context: str = "Describe the context and problem we are facing."
    decision: str = "Describe the decision and how we solve it."
    consequences: str = "Describe the consequences (both good and bad) of this decision."

class BeaconSpec(BaseModel):
    project_name: str = Field(default="MyBeaconProject")
    adr: Optional[ADRSpec] = None
    modules: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
