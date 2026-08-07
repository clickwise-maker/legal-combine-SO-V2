# FRAMEWORK PLACEHOLDER
# DO NOT DELETE
# IMPLEMENT IN FUTURE PHASE: Phase 7

"""
Base AI Agent Module

Provides base class for all AI agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentContext:
    """Context for agent execution."""
    user_id: str
    session_id: str
    metadata: Dict[str, Any]


@dataclass
class AgentResponse:
    """Response from agent execution."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class BaseAgent(ABC):
    """
    Base class for all AI agents.
    
    Each agent implements specific legal tasks:
    - Document Review
    - Legal Research
    - Compliance Checking
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, context: AgentContext, input_data: Dict) -> AgentResponse:
        """
        Execute the agent task.
        
        Args:
            context: Execution context
            input_data: Input data for the task
            
        Returns:
            AgentResponse with result or error
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict) -> bool:
        """
        Validate input data.
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        return {
            "name": self.name,
            "description": self.description,
        }
