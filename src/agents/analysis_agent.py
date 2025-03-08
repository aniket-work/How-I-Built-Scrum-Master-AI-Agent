"""
Analysis Agent Module

This module defines the AnalysisAgent class, which is responsible for
analyzing project data and identifying issues, blockers, and trends.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from src.agents.base_agent import BaseAgent
from src.utils.data_utils import (
    calculate_sprint_metrics,
    analyze_team_performance,
    identify_process_bottlenecks
)

# Set up logging
logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):
    """
    Agent responsible for analyzing sprint data and identifying issues.

    This agent analyzes collected project data to identify blockers, delays,
    team performance issues, and process bottlenecks.
    """

    def __init__(
            self,
            role: str = "Scrum Process Analysis Expert",
            goal: str = "Thoroughly analyze the collected project data to identify sprint issues.",
            backstory: str = "You have extensive experience as a Scrum Master for high-performing software teams.",
            verbose: bool = True,
            allow_delegation: bool = False,
            llm: Optional[Any] = None
    ):
        """
        Initialize the analysis agent.

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

        logger.info("Initialized AnalysisAgent")

    def analyze_sprint_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze processed sprint data to identify issues and patterns.

        Args:
            processed_data: Processed Trello data.

        Returns:
            Analysis results.
        """
        logger.info("Analyzing sprint data")

        if not processed_data or "error" in processed_data:
            error_msg = processed_data.get("error", "Unknown error in processed data")
            logger.error(f"Error in processed data: {error_msg}")
            return {"error": error_msg}

        try:
            cards = processed_data.get("cards", [])
            lists = processed_data.get("lists", [])
            members = processed_data.get("members", [])

            logger.info(f"Analyzing {len(cards)} cards, {len(lists)} lists, and {len(members)} members")

            # Calculate metrics
            sprint_metrics = calculate_sprint_metrics(cards, lists)
            team_performance = analyze_team_performance(cards, members)
            process_bottlenecks = identify_process_bottlenecks(cards, lists)

            # Calculate days until sprint end (assuming 2-week sprints)
            sprint_end_date = None
            days_remaining = None

            # Calculate burn down data
            burn_down_data = self._calculate_burn_down(cards, lists)

            # Calculate velocity data
            velocity_data = self._calculate_velocity(cards)

            # Identify risks
            risks = self._identify_risks(cards, sprint_metrics, team_performance, process_bottlenecks)

            # Generate recommendations
            recommendations = self._generate_recommendations(risks, sprint_metrics, team_performance,
                                                             process_bottlenecks)

            analysis_results = {
                "timestamp": datetime.now().isoformat(),
                "sprint_metrics": sprint_metrics,
                "team_performance": team_performance,
                "process_bottlenecks": process_bottlenecks,
                "burn_down": burn_down_data,
                "velocity": velocity_data,
                "risks": risks,
                "recommendations": recommendations,
                "sprint_end_date": sprint_end_date.isoformat() if sprint_end_date else None,
                "days_remaining": days_remaining
            }

            logger.info("Successfully analyzed sprint data")
            return analysis_results

        except Exception as e:
            logger.error(f"Error analyzing sprint data: {str(e)}")
            return {"error": f"Error analyzing sprint data: {str(e)}"}

    def _calculate_burn_down(self, cards: List[Dict[str, Any]], lists: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate burn down chart data.

        Args:
            cards: List of cards from Trello.
            lists: List of lists from Trello.

        Returns:
            Burn down chart data.
        """
        # Simple implementation - in a real scenario, this would use historical data
        total_points = len(cards)
        completed_points = sum(1 for card in cards if card.get("isComplete", False))
        remaining_points = total_points - completed_points

        # Calculate ideal burn down (assuming 10 days in a sprint)
        ideal_burn_down = []
        for day in range(11):
            ideal_burn_down.append({
                "day": day,
                "ideal": total_points - (total_points * day / 10)
            })

        # Estimate actual burn down based on completion rate
        actual_burn_down = []
        completion_rate = completed_points / total_points if total_points > 0 else 0
        estimated_day = 5  # Assuming we're in the middle of the sprint

        for day in range(estimated_day + 1):
            actual_burn_down.append({
                "day": day,
                "actual": total_points - (completed_points * day / estimated_day)
            })

        return {
            "total_points": total_points,
            "completed_points": completed_points,
            "remaining_points": remaining_points,
            "ideal_burn_down": ideal_burn_down,
            "actual_burn_down": actual_burn_down,
            "projected_completion": remaining_points / completion_rate if completion_rate > 0 else "Cannot estimate"
        }

    def _calculate_velocity(self, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate velocity metrics.

        Args:
            cards: List of cards from Trello.

        Returns:
            Velocity metrics.
        """
        # Simple implementation - in a real scenario, this would use data from multiple sprints
        total_story_points = len(cards)
        completed_story_points = sum(1 for card in cards if card.get("isComplete", False))

        return {
            "current_sprint": {
                "total_points": total_story_points,
                "completed_points": completed_story_points,
                "completion_percentage": (
                            completed_story_points / total_story_points * 100) if total_story_points > 0 else 0
            },
            "historical": [
                # Placeholder for historical data
                {"sprint": "Sprint -1", "completed_points": completed_story_points - 2},
                {"sprint": "Sprint -2", "completed_points": completed_story_points - 5},
                {"sprint": "Sprint -3", "completed_points": completed_story_points - 3}
            ]
        }

    def _identify_risks(
            self,
            cards: List[Dict[str, Any]],
            sprint_metrics: Dict[str, Any],
            team_performance: Dict[str, Any],
            process_bottlenecks: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify risks in the sprint.

        Args:
            cards: List of cards from Trello.
            sprint_metrics: Sprint metrics.
            team_performance: Team performance metrics.
            process_bottlenecks: Process bottleneck information.

        Returns:
            List of identified risks.
        """
        risks = []

        # Check for completion rate risks
        completion_rate = sprint_metrics.get("completion_rate", 0)
        if completion_rate < 70:
            risks.append({
                "category": "completion_rate",
                "severity": "high" if completion_rate < 50 else "medium",
                "description": f"Low sprint completion rate ({completion_rate:.1f}%)",
                "impact": "Sprint goals may not be met by the end of the sprint"
            })

        # Check for blocker risks
        blockers = sprint_metrics.get("blockers", [])
        if blockers:
            risks.append({
                "category": "blockers",
                "severity": "high" if len(blockers) > 2 else "medium",
                "description": f"{len(blockers)} blockers identified in the sprint",
                "impact": "Blocking issues are preventing team progress"
            })

        # Check for approaching deadline risks
        approaching_deadlines = sprint_metrics.get("approaching_deadlines", [])
        if approaching_deadlines:
            risks.append({
                "category": "approaching_deadlines",
                "severity": "medium",
                "description": f"{len(approaching_deadlines)} tasks with approaching deadlines",
                "impact": "Tasks may not be completed by their due dates"
            })

        # Check for overdue risks
        overdue_cards = sprint_metrics.get("overdue_cards", [])
        if overdue_cards:
            risks.append({
                "category": "overdue",
                "severity": "high" if len(overdue_cards) > 3 else "medium",
                "description": f"{len(overdue_cards)} overdue tasks",
                "impact": "Tasks have already missed their deadlines"
            })

        # Check for workload imbalance risks
        members_with_high_workload = team_performance.get("members_with_high_workload", [])
        if members_with_high_workload:
            risks.append({
                "category": "workload_imbalance",
                "severity": "medium",
                "description": f"{len(members_with_high_workload)} team members have high workloads",
                "impact": "Uneven workload distribution may lead to burnout and delays"
            })

        # Check for process bottleneck risks
        bottlenecks = process_bottlenecks.get("bottlenecks", [])
        if bottlenecks:
            risks.append({
                "category": "process_bottlenecks",
                "severity": "high" if any(b.get("ratio_to_avg", 0) > 2 for b in bottlenecks) else "medium",
                "description": f"{len(bottlenecks)} process bottlenecks identified",
                "impact": "Tasks are piling up in specific stages of the process"
            })

        logger.info(f"Identified {len(risks)} risks in the sprint")
        return risks

    def _generate_recommendations(
            self,
            risks: List[Dict[str, Any]],
            sprint_metrics: Dict[str, Any],
            team_performance: Dict[str, Any],
            process_bottlenecks: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on identified risks.

        Args:
            risks: List of identified risks.
            sprint_metrics: Sprint metrics.
            team_performance: Team performance metrics.
            process_bottlenecks: Process bottleneck information.

        Returns:
            List of recommendations.
        """
        recommendations = []

        # Generate recommendations for each risk category
        risk_categories = set(risk["category"] for risk in risks)

        if "completion_rate" in risk_categories:
            recommendations.append({
                "category": "completion_rate",
                "priority": "high",
                "description": "Review sprint scope and consider reducing the number of tasks",
                "action_items": [
                    "Conduct a mid-sprint scope review",
                    "Identify and remove non-essential tasks",
                    "Focus team efforts on highest priority items"
                ]
            })

        if "blockers" in risk_categories:
            recommendations.append({
                "category": "blockers",
                "priority": "high",
                "description": "Address blocking issues immediately",
                "action_items": [
                    "Schedule a blocker resolution session",
                    "Escalate blockers to relevant stakeholders if needed",
                    "Assign owners to each blocker with clear resolution timelines"
                ]
            })

        if "approaching_deadlines" in risk_categories or "overdue" in risk_categories:
            recommendations.append({
                "category": "deadlines",
                "priority": "high",
                "description": "Review and adjust task deadlines",
                "action_items": [
                    "Re-evaluate overdue and approaching deadline tasks",
                    "Adjust timelines or reassign resources as needed",
                    "Communicate changes to stakeholders"
                ]
            })

        if "workload_imbalance" in risk_categories:
            recommendations.append({
                "category": "workload",
                "priority": "medium",
                "description": "Balance team workload",
                "action_items": [
                    "Redistribute tasks from overloaded team members",
                    "Pair team members on complex tasks",
                    "Consider bringing in additional resources if available"
                ]
            })

        if "process_bottlenecks" in risk_categories:
            recommendations.append({
                "category": "process",
                "priority": "medium",
                "description": "Address process bottlenecks",
                "action_items": [
                    "Focus team efforts on clearing bottlenecked stages",
                    "Review process flow and identify improvement opportunities",
                    "Consider temporary process adjustments for the current sprint"
                ]
            })

        # Add general recommendations if needed
        if not recommendations:
            recommendations.append({
                "category": "general",
                "priority": "low",
                "description": "Continue monitoring sprint progress",
                "action_items": [
                    "Maintain daily stand-ups and communications",
                    "Keep the board updated with the latest status",
                    "Ensure team members are aware of their responsibilities"
                ]
            })

        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations