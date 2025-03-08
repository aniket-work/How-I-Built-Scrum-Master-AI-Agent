"""
Base Agent Module

This module provides the BaseAgent class that all specialized agents extend.
It defines common functionality and interfaces for all agents in the system.
"""

import logging
from typing import List, Dict, Any, Optional
from crewai import Agent

# Set up logging
logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all agents in the Scrum Master AI system.

    This class provides common functionality and interfaces that all specialized
    agents should implement or inherit.
    """

    def __init__(
            self,
            role: str,
            goal: str,
            backstory: str,
            verbose: bool = True,
            allow_delegation: bool = False,
            tools: List[Any] = None,
            llm: Optional[Any] = None
    ):
        """
        Initialize the base agent.

        Args:
            role: The role of the agent.
            goal: The goal the agent is trying to achieve.
            backstory: The backstory of the agent.
            verbose: Whether to enable verbose logging.
            allow_delegation: Whether to allow the agent to delegate tasks.
            tools: List of tools available to the agent.
            llm: Language model to use for the agent.
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.tools = tools or []
        self.llm = llm

        logger.debug(f"Initialized agent with role: {role}")

    def to_crewai_agent(self) -> Agent:
        """
        Convert to a CrewAI Agent object.

        Returns:
            CrewAI Agent object.
        """
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation,
            tools=self.tools,
            llm=self.llm
        )

    def get_tools(self) -> List[Any]:
        """
        Get the tools available to the agent.

        Returns:
            List of tools.
        """
        return self.tools

    def add_tool(self, tool: Any) -> None:
        """
        Add a tool to the agent.

        Args:
            tool: Tool to add.
        """
        self.tools.append(tool)
        logger.debug(f"Added tool {tool.name} to agent {self.role}")

    def add_tools(self, tools: List[Any]) -> None:
        """
        Add multiple tools to the agent.

        Args:
            tools: List of tools to add.
        """
        self.tools.extend(tools)
        tool_names = [tool.name for tool in tools]
        logger.debug(f"Added tools {tool_names} to agent {self.role}")

    def set_llm(self, llm: Any) -> None:
        """
        Set the language model for the agent.

        Args:
            llm: Language model to use.
        """
        self.llm = llm
        logger.debug(f"Set LLM for agent {self.role}")