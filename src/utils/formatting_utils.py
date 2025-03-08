"""
Formatting Utilities Module

This module provides utility functions for formatting data for reports and other outputs.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)


def format_date(date_str: Optional[str], format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date string to a human-readable format.

    Args:
        date_str: ISO format date string.
        format_str: Output format string.

    Returns:
        Formatted date string.
    """
    try:
        if not date_str:
            return "Not set"

        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date_obj.strftime(format_str)
    except (ValueError, TypeError) as e:
        logger.warning(f"Error formatting date {date_str}: {e}")
        return "Invalid date"


def generate_status_table(cards_by_list: Dict[str, int], total_cards: int) -> str:
    """
    Generate a markdown table showing card status distribution.

    Args:
        cards_by_list: Dictionary mapping list names to card counts.
        total_cards: Total number of cards.

    Returns:
        Markdown formatted table rows.
    """
    table_rows = []
    for list_name, count in cards_by_list.items():
        if total_cards > 0:
            percentage = (count / total_cards) * 100
        else:
            percentage = 0

        table_rows.append(f"| {list_name} | {count} | {percentage:.1f}% |")

    return "\n".join(table_rows)


def format_blocker_list(blockers: List[Dict[str, Any]]) -> str:
    """
    Format a list of blockers as markdown.

    Args:
        blockers: List of blocker dictionaries.

    Returns:
        Markdown formatted list of blockers.
    """
    if not blockers:
        return "No blockers identified."

    blocker_items = []
    for blocker in blockers:
        name = blocker.get("name", "Unnamed card")
        list_name = blocker.get("list", "Unknown list")
        url = blocker.get("url", "#")

        blocker_items.append(f"- **[{name}]({url})** - In list: *{list_name}*")

    return "\n".join(blocker_items)


def format_approaching_deadlines(approaching_deadlines: List[Dict[str, Any]]) -> str:
    """
    Format a list of cards with approaching deadlines as markdown.

    Args:
        approaching_deadlines: List of card dictionaries with approaching deadlines.

    Returns:
        Markdown formatted list of cards with approaching deadlines.
    """
    if not approaching_deadlines:
        return "No tasks approaching deadlines."

    deadline_items = []
    for card in approaching_deadlines:
        name = card.get("name", "Unnamed card")
        list_name = card.get("list", "Unknown list")
        due_date = format_date(card.get("due"))

        deadline_items.append(f"- **{name}** - Due: *{due_date}* - In list: *{list_name}*")

    return "\n".join(deadline_items)


def format_overdue_tasks(overdue_cards: List[Dict[str, Any]]) -> str:
    """
    Format a list of overdue cards as markdown.

    Args:
        overdue_cards: List of overdue card dictionaries.

    Returns:
        Markdown formatted list of overdue cards.
    """
    if not overdue_cards:
        return "No overdue tasks."

    overdue_items = []
    for card in overdue_cards:
        name = card.get("name", "Unnamed card")
        list_name = card.get("list", "Unknown list")
        due_date = format_date(card.get("due"))

        overdue_items.append(f"- **{name}** - Due: *{due_date}* - In list: *{list_name}*")

    return "\n".join(overdue_items)


def format_workload_distribution(cards_by_member: Dict[str, Dict[str, Any]]) -> str:
    """
    Format team workload distribution as markdown.

    Args:
        cards_by_member: Dictionary mapping member names to their stats.

    Returns:
        Markdown formatted workload distribution.
    """
    if not cards_by_member:
        return "No team member data available."

    table_header = "| Team Member | Total Tasks | Completed | Completion Rate | Overdue |\n"
    table_divider = "|------------|-------------|-----------|----------------|--------|\n"

    table_rows = []
    for member_name, stats in cards_by_member.items():
        total = stats.get("total", 0)
        completed = stats.get("completed", 0)
        completion_rate = stats.get("completion_rate", 0)
        overdue = stats.get("overdue", 0)

        table_rows.append(
            f"| {member_name} | {total} | {completed} | {completion_rate:.1f}% | {overdue} |"
        )

    return table_header + table_divider + "\n".join(table_rows)


def format_bottlenecks(bottlenecks: List[Dict[str, Any]]) -> str:
    """
    Format process bottlenecks as markdown.

    Args:
        bottlenecks: List of bottleneck dictionaries.

    Returns:
        Markdown formatted list of bottlenecks.
    """
    if not bottlenecks:
        return "No process bottlenecks identified."

    bottleneck_items = []
    for bottleneck in bottlenecks:
        list_name = bottleneck.get("list_name", "Unknown list")
        card_count = bottleneck.get("card_count", 0)
        ratio = bottleneck.get("ratio_to_avg", 0)

        bottleneck_items.append(
            f"- **{list_name}** - {card_count} tasks ({ratio:.1f}x average)"
        )

    return "\n".join(bottleneck_items)


def fill_report_template(template_path: str, template_data: Dict[str, Any]) -> str:
    """
    Fill a report template with data.

    Args:
        template_path: Path to the template file.
        template_data: Dictionary of data to fill the template with.

    Returns:
        Filled report template.
    """
    try:
        with open(template_path, "r") as f:
            template = f.read()

        # Basic string formatting for placeholder replacement
        for key, value in template_data.items():
            placeholder = "{" + key + "}"
            template = template.replace(placeholder, str(value))

        return template

    except Exception as e:
        logger.error(f"Error filling report template: {e}")
        return f"Error generating report: {str(e)}"