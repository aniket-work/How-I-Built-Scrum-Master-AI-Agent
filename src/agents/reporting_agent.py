"""
Reporting Agent Module

This module defines the ReportingAgent class, which is responsible for
generating comprehensive sprint reports based on analyzed data.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.models.report_models import SprintReportData
from src.utils.formatting_utils import fill_report_template

# Set up logging
logger = logging.getLogger(__name__)


class ReportingAgent(BaseAgent):
    """
    Agent responsible for generating comprehensive sprint reports.

    This agent transforms analyzed data into clear, well-formatted reports
    suitable for both technical team members and executive stakeholders.
    """

    def __init__(
            self,
            role: str = "Executive Communication Specialist",
            goal: str = "Transform complex project data into clear, actionable reports.",
            backstory: str = "With a background in technical writing and executive communications, you've mastered distilling complex information into compelling narratives.",
            verbose: bool = True,
            allow_delegation: bool = False,
            llm: Optional[Any] = None
    ):
        """
        Initialize the reporting agent.

        Args:
            role: The role of the agent.
            goal: The goal the agent is trying to achieve.
            backstory: The backstory of the agent.
            verbose: Whether to enable verbose logging.
            allow_delegation: Whether to allow the agent to delegate tasks.
            llm: Language model to use for the agent.
        """
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=allow_delegation,
            tools=[],
            llm=llm
        )

        logger.info("Initialized ReportingAgent")

    def generate_sprint_report(
            self,
            processed_data: Dict[str, Any],
            analysis_results: Dict[str, Any],
            sprint_name: str = "Current Sprint",
            team_name: str = "Development Team",
            template_path: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive sprint report.

        Args:
            processed_data: Processed Trello data.
            analysis_results: Analysis results from the analysis agent.
            sprint_name: Name of the sprint.
            team_name: Name of the team.
            template_path: Path to the report template. If None, uses the default template.

        Returns:
            Markdown formatted sprint report.
        """
        logger.info(f"Generating sprint report for {sprint_name}")

        if "error" in processed_data or "error" in analysis_results:
            error_msg = processed_data.get("error", analysis_results.get("error", "Unknown error"))
            logger.error(f"Error generating sprint report: {error_msg}")
            return f"# Error Generating Sprint Report\n\n{error_msg}"

        try:
            # Create a SprintReportData object
            report_data = self._prepare_report_data(processed_data, analysis_results, sprint_name, team_name)

            # Use default template if not specified
            if not template_path:
                template_path = os.path.join("templates", "report_template.md")

            # Fill the template with data
            report_content = fill_report_template(template_path, report_data.to_template_context())

            logger.info("Successfully generated sprint report")
            return report_content

        except Exception as e:
            logger.