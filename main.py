#!/usr/bin/env python
"""
Scrum Master AI Agent - Main Application Entry Point

This script serves as the main entry point for the Scrum Master AI Agent application.
It provides command-line interface for running the agent in different modes.
"""

import argparse
import os
import sys
import warnings
import logging
import yaml
from datetime import datetime

# Suppress syntax warnings from pysbd
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.crew.scrum_master_crew import ScrumMasterCrew
from src.utils.logging_utils import setup_logging


def load_settings():
    """Load application settings from configuration files."""
    config_path = os.path.join(os.path.dirname(__file__), "config", "settings.yaml")
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}


def run(args):
    """
    Run the crew in standard mode.

    Args:
        args: Command line arguments
    """
    try:
        crew = ScrumMasterCrew()
        print("Starting Scrum Master AI Agent...")
        print(f"Board ID: {os.getenv('TRELLO_BOARD_ID', 'Not set')}")
        print(f"Output file: {args.output if args.output else 'Default (sprint_report_<date>.md)'}")

        if args.output:
            crew.set_output_file(args.output)

        crew.crew().kickoff()
        print("Scrum Master AI Agent completed successfully.")
    except Exception as e:
        print(f"An error occurred while running the crew: {e}")
        sys.exit(1)


def train(args):
    """
    Train the crew for a given number of iterations.

    Args:
        args: Command line arguments
    """
    inputs = {
        "sprint_name": args.sprint_name if args.sprint_name else "Current Sprint",
        "team_name": args.team_name if args.team_name else "Development Team"
    }

    try:
        crew = ScrumMasterCrew()
        print(f"Training Scrum Master AI Agent for {args.iterations} iterations...")
        crew.crew().train(
            n_iterations=args.iterations,
            filename=args.output,
            inputs=inputs
        )
        print("Training completed successfully.")
    except Exception as e:
        print(f"An error occurred while training the crew: {e}")
        sys.exit(1)


def replay(args):
    """
    Replay the crew execution from a specific task.

    Args:
        args: Command line arguments
    """
    try:
        crew = ScrumMasterCrew()
        print(f"Replaying execution from task: {args.task_id}")
        crew.crew().replay(task_id=args.task_id)
        print("Replay completed successfully.")
    except Exception as e:
        print(f"An error occurred while replaying the crew: {e}")
        sys.exit(1)


def test(args):
    """
    Test the crew execution and returns the results.

    Args:
        args: Command line arguments
    """
    inputs = {
        "sprint_name": args.sprint_name if args.sprint_name else "Test Sprint",
        "team_name": args.team_name if args.team_name else "Test Team"
    }

    try:
        crew = ScrumMasterCrew()
        print(f"Testing Scrum Master AI Agent with {args.model} for {args.iterations} iterations...")
        results = crew.crew().test(
            n_iterations=args.iterations,
            openai_model_name=args.model,
            inputs=inputs
        )
        print("Test completed successfully.")
        print(f"Results: {results}")
    except Exception as e:
        print(f"An error occurred while testing the crew: {e}")
        sys.exit(1)


def setup_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description="Scrum Master AI Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the Scrum Master AI Agent")
    run_parser.add_argument("-o", "--output", help="Output file for the report")
    run_parser.set_defaults(func=run)

    # Train command
    train_parser = subparsers.add_parser("train", help="Train the Scrum Master AI Agent")
    train_parser.add_argument("-i", "--iterations", type=int, default=3, help="Number of training iterations")
    train_parser.add_argument("-o", "--output", required=True, help="Output file for training results")
    train_parser.add_argument("-s", "--sprint-name", help="Name of the sprint")
    train_parser.add_argument("-t", "--team-name", help="Name of the team")
    train_parser.set_defaults(func=train)

    # Replay command
    replay_parser = subparsers.add_parser("replay", help="Replay execution from a specific task")
    replay_parser.add_argument("task_id", help="ID of the task to replay from")
    replay_parser.set_defaults(func=replay)

    # Test command
    test_parser = subparsers.add_parser("test", help="Test the Scrum Master AI Agent")
    test_parser.add_argument("-i", "--iterations", type=int, default=1, help="Number of test iterations")
    test_parser.add_argument("-m", "--model", default="gpt-4", help="OpenAI model to use for testing")
    test_parser.add_argument("-s", "--sprint-name", help="Name of the sprint")
    test_parser.add_argument("-t", "--team-name", help="Name of the team")
    test_parser.set_defaults(func=test)

    return parser


def main():
    """Main entry point for the application."""
    # Load settings
    settings = load_settings()

    # Set up logging
    log_settings = settings.get("logging", {})
    setup_logging(
        log_file=log_settings.get("file", "./logs/scrum_master_ai.log"),
        log_level=log_settings.get("level", "INFO")
    )

    # Parse command line arguments
    parser = setup_parser()
    args = parser.parse_args()

    # Execute the appropriate command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()