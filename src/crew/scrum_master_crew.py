"""
Scrum Master Crew Module

This module defines the ScrumMasterCrew class, which orchestrates the interactions
between the different agents and tasks for the Scrum Master AI system.
"""

import os
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.tools.trello_tools import BoardDataFetcherTool, CardDataFetcherTool

# Set up logging
logger = logging.getLogger(__name__)


@CrewBase
class ScrumMasterCrew:
    """
    ScrumMasterCrew orchestrates the Scrum Master AI system.

    This crew is responsible for collecting data from Trello, analyzing it,
    and generating reports for sprint retrospectives.
    """

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the ScrumMasterCrew.

        Args:
            config_dir: Directory containing configuration files.
        """
        self.config_dir = config_dir
        self.agents_config = self._load_yaml_config("agents.yaml")
        self.tasks_config = self._load_yaml_config("tasks.yaml")
        self.settings = self._load_yaml_config("settings.yaml")
        self.constants = self._load_json_config("constants.json")
        self.output_file = None

        logger.info("ScrumMasterCrew initialized")

    def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration from a file.

        Args:
            filename: Name of the YAML file.

        Returns:
            Dictionary containing the configuration.
        """
        try:
            config_path = os.path.join(self.config_dir, filename)
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}

    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration from a file.

        Args:
            filename: Name of the JSON file.

        Returns:
            Dictionary containing the configuration.
        """
        try:
            config_path = os.path.join(self.config_dir, filename)
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}

    def set_output_file(self, output_file: str) -> None:
        """
        Set the output file for the report.

        Args:
            output_file: Path to the output file.
        """
        self.output_file = output_file
        logger.info(f"Set output file to {output_file}")

    @agent
    def data_collection_agent(self) -> Agent:
        """
        Create a data collection agent.

        Returns:
            Agent for data collection.
        """
        agent_config = self.agents_config.get("data_collection_agent", {})
        model_config = self.settings.get("models", {}).get("default", "gpt-4")

        return Agent(
            role=agent_config.get("role", "Data Collection Specialist"),
            goal=agent_config.get("goal", "Gather all relevant data from the Trello board."),
            backstory=agent_config.get("backstory", "You are responsible for collecting project data."),
            verbose=agent_config.get("verbose", True),
            allow_delegation=agent_config.get("allow_delegation", False),
            tools=[BoardDataFetcherTool(), CardDataFetcherTool()],
            llm=model_config
        )

    @agent
    def analysis_agent(self) -> Agent:
        """
        Create an analysis agent.

        Returns:
            Agent for data analysis.
        """
        agent_config = self.agents_config.get("analysis_agent", {})
        model_config = self.settings.get("models", {}).get("default", "gpt-4")

        return Agent(
            role=agent_config.get("role", "Project Analysis Expert"),
            goal=agent_config.get("goal", "Analyze the collected data to identify issues."),
            backstory=agent_config.get("backstory", "You have a keen eye for detail."),
            verbose=agent_config.get("verbose", True),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=model_config
        )

    @agent
    def reporting_agent(self) -> Agent:
        """
        Create a reporting agent.

        Returns:
            Agent for report generation.
        """
        agent_config = self.agents_config.get("reporting_agent", {})
        model_config = self.settings.get("models", {}).get("default", "gpt-4")

        return Agent(
            role=agent_config.get("role", "Executive Communication Specialist"),
            goal=agent_config.get("goal", "Generate clear, actionable reports."),
            backstory=agent_config.get("backstory", "You excel at executive communications."),
            verbose=agent_config.get("verbose", True),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=model_config
        )

    @task
    def data_collection_task(self) -> Task:
        """
        Create a data collection task.

        Returns:
            Task for data collection.
        """
        task_config = self.tasks_config.get("data_collection", {})

        return Task(
            description=task_config.get("description", "Collect data from Trello."),
            expected_output=task_config.get("expected_output", "A data report."),
            agent=self.data_collection_agent,
            context=task_config.get("context", [])
        )

    @task
    def data_analysis_task(self) -> Task:
        """
        Create a data analysis task.

        Returns:
            Task for data analysis.
        """
        task_config = self.tasks_config.get("data_analysis", {})

        return Task(
            description=task_config.get("description", "Analyze the collected data."),
            expected_output=task_config.get("expected_output", "An analysis report."),
            agent=self.analysis_agent,
            context=task_config.get("context", []),
            async_execution=False
        )

    @task
    def report_generation_task(self) -> Task:
        """
        Create a report generation task.

        Returns:
            Task for report generation.
        """
        task_config = self.tasks_config.get("report_generation", {})

        # Set output file with date if not specified
        if not self.output_file:
            date_str = datetime.now().strftime("%Y%m%d")
            output_file = task_config.get("output_file", "sprint_report_{date}.md").format(date=date_str)
        else:
            output_file = self.output_file

        return Task(
            description=task_config.get("description", "Generate a sprint report."),
            expected_output=task_config.get("expected_output", "A sprint report."),
            agent=self.analysis_agent,
            context=task_config.get("context", []),
            output_file=output_file
        )

    @crew
    def crew(self) -> Crew:
        """
        Create the Scrum Master crew.

        Returns:
            Configured Crew object.
        """
        # Get process type from settings
        process_type = self.settings.get("crew", {}).get("default_process", "sequential")
        process = Process.sequential
        if process_type == "hierarchical":
            process = Process.hierarchical
        elif process_type == "parallel":
            process = Process.parallel

        verbose = self.settings.get("crew", {}).get("default_verbose", True)

        return Crew(
            agents=[
                self.data_collection_agent,
                self.analysis_agent,
                self.reporting_agent
            ],
            tasks=[
                self.data_collection_task,
                self.data_analysis_task,
                self.report_generation_task
            ],
            process=process,
            verbose=verbose,
            memory=True,
            cache=self.settings.get("crew", {}).get("cache_enabled", True)
        )