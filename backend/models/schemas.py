"""Database schema definitions"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Customer(Base):
    """Customer profile table"""
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True, index=True)
    customer_type = Column(String, default="new")
    total_calls = Column(Integer, default=0)
    satisfaction_avg = Column(Float, default=0.0)
    resolution_rate = Column(Float, default=0.0)
    preferred_persona = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    call_history = relationship("CallHistory", back_populates="customer")


class CallHistory(Base):
    """Call history table"""
    __tablename__ = "call_history"
    
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    agent_id = Column(String, nullable=True)
    persona_used = Column(String, nullable=True)
    intent = Column(String, nullable=True)
    satisfaction_score = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False)
    outcome = Column(JSON, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="call_history")


class PersonaPerformance(Base):
    """Persona performance metrics table"""
    __tablename__ = "persona_performance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_type = Column(String, nullable=False, index=True)
    persona_type = Column(String, nullable=False, index=True)
    success_rate = Column(Float, default=0.5)
    satisfaction_avg = Column(Float, default=0.5)
    resolution_rate = Column(Float, default=0.5)
    call_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        {"extend_existing": True},
    )


class ConversationState(Base):
    """Real-time conversation state (cached in Redis, persisted here for analysis)"""
    __tablename__ = "conversation_states"
    
    id = Column(String, primary_key=True, index=True)
    call_id = Column(String, nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    current_intent = Column(String, nullable=True)
    current_sentiment = Column(JSON, nullable=True)
    selected_persona = Column(String, nullable=True)
    conversation_context = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

