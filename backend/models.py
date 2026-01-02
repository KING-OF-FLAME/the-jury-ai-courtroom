from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from .database import Base

class CaseDB(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    
    # Config
    proposer_model = Column(String(255))
    critic_model = Column(String(255))
    judge_model = Column(String(255))
    
    # Personas
    proposer_persona = Column(String(255), default="Senior Solutions Architect")
    critic_persona = Column(String(255), default="Security Research Lead")
    judge_persona = Column(String(255), default="Chief Justice")

    # Outputs
    proposer_output = Column(Text, nullable=True)
    critic_output = Column(Text, nullable=True)
    final_verdict = Column(Text, nullable=True)
    
    # Metrics
    proposer_time = Column(Float, default=0.0)
    critic_time = Column(Float, default=0.0)
    judge_time = Column(Float, default=0.0)
    
    proposer_tokens = Column(Integer, default=0)
    critic_tokens = Column(Integer, default=0)
    judge_tokens = Column(Integer, default=0)
    
    total_time = Column(Float, default=0.0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    judge_confidence = Column(Float, default=0.0)
    
    debate_log = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_rating = Column(Integer, nullable=True)
    user_feedback = Column(Text, nullable=True)

# --- API Models ---
class CaseRequest(BaseModel):
    query: str
    proposer_model: str = "nvidia/nemotron-3-nano-30b-a3b:free"
    critic_model: str = "allenai/olmo-3.1-32b-think:free"
    judge_model: str = "meta-llama/llama-3.1-405b-instruct:free"
    proposer_persona: Optional[str] = "Senior Solutions Architect"
    critic_persona: Optional[str] = "Security Research Lead"
    judge_persona: Optional[str] = "Chief Justice"

class CaseResponse(BaseModel):
    id: Optional[int]
    query: str
    proposer_model: Optional[str]
    critic_model: Optional[str]
    judge_model: Optional[str]
    proposer_persona: Optional[str]
    critic_persona: Optional[str]
    judge_persona: Optional[str]
    
    proposer: Optional[str]
    critic: Optional[str]
    verdict: Optional[str]
    
    logs: Optional[List[Dict[str, Any]]] = []
    estimated_cost: Optional[float] = 0.0
    confidence_score: Optional[float] = 0.0
    total_time: Optional[float] = 0.0
    
    class Config: from_attributes = True

class CaseHistoryItem(BaseModel):
    id: int
    query: str
    verdict: Optional[str]
    timestamp: str
    estimated_cost: Optional[float] = 0.0
    confidence: Optional[float] = 0.0
    class Config: from_attributes = True