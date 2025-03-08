"""
Data Utilities Module

This module provides utility functions for processing and analyzing Trello data.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)


def calculate_sprint_metrics(cards: List[Dict[str, Any]], lists: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate sprint metrics from Trello data.

    Args:
        cards: List of cards from Trello.
        lists: List of lists from Trello.

    Returns:
        Dictionary containing sprint metrics.
    """
    try:
        # Map list IDs to names for easier reference
        list_map = {list_data["id"]: list_data["name"] for list_data in lists}

        # Count cards by list
        cards_by_list = {}
        for list_data in lists:
            list_name = list_data["name"]
            cards_by_list[list_name] = 0

        for card in cards:
            list_id = card.get("idList")
            if list_id and list_id in list_map:
                list_name = list_map[list_id]
                cards_by_list[list_name] = cards_by_list.get(list_name, 0) + 1

        # Calculate completion rate
        total_cards = len(cards)
        completed_cards = cards_by_list.get("Done", 0)
        completion_rate = (completed_cards / total_cards) * 100 if total_cards > 0 else 0

        # Find blockers (cards with red labels or "blocker" in comments)
        blockers = []
        for card in cards:
            is_blocker = False

            # Check for red labels
            for label in card.get("labels", []):
                if label.get("color") == "red":
                    is_blocker = True
                    break

            # Check for blocker keywords in comments
            if not is_blocker:
                for comment in card.get("comments", []):
                    if "blocker" in comment.get("text", "").lower():
                        is_blocker = True
                        break

            if is_blocker:
                blockers.append({
                    "id": card.get("id"),
                    "name": card.get("name"),
                    "url": card.get("url"),
                    "list": list_map.get(card.get("idList"), "Unknown")
                })

        # Calculate cards with approaching deadlines (due in the next 3 days)
        approaching_deadlines = []
        now = datetime.now()
        three_days_from_now = now + timedelta(days=3)

        for card in cards:
            due_date_str = card.get("due")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    if now < due_date <= three_days_from_now and not card.get("dueComplete", False):
                        approaching_deadlines.append({
                            "id": card.get("id"),
                            "name": card.get("name"),
                            "due": due_date_str,
                            "list": list_map.get(card.get("idList"), "Unknown")
                        })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing due date for card {card.get('name')}: {e}")

        # Calculate overdue cards
        overdue_cards = []
        for card in cards:
            due_date_str = card.get("due")
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                    if due_date < now and not card.get("dueComplete", False):
                        overdue_cards.append({
                            "id": card.get("id"),
                            "name": card.get("name"),
                            "due": due_date_str,
                            "list": list_map.get(card.get("idList"), "Unknown")
                        })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing due date for card {card.get('name')}: {e}")

        # Build the metrics object
        metrics = {
            "total_cards": total_cards,
            "cards_by_list": cards_by_list,
            "completion_rate": completion_rate,
            "blockers": blockers,
            "approaching_deadlines": approaching_deadlines,
            "overdue_cards": overdue_cards,
            "blockers_count": len(blockers),
            "approaching_deadlines_count": len(approaching_deadlines),
            "overdue_count": len(overdue_cards)
        }

        return metrics

    except Exception as e:
        logger.error(f"Error calculating sprint metrics: {e}")
        return {
            "error": str(e),
            "total_cards": 0,
            "cards_by_list": {},
            "completion_rate": 0,
            "blockers": [],
            "approaching_deadlines": [],
            "overdue_cards": [],
            "blockers_count": 0,
            "approaching_deadlines_count": 0,
            "overdue_count": 0
        }


def analyze_team_performance(cards: List[Dict[str, Any]], members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze team performance based on Trello card assignments.

    Args:
        cards: List of cards from Trello.
        members: List of members from Trello.

    Returns:
        Dictionary containing team performance metrics.
    """
    try:
        # Create a map of member IDs to names
        member_map = {member["id"]: member.get("fullName", member.get("username", "Unknown"))
                      for member in members}

        # Count cards by member
        cards_by_member = {}
        for card in cards:
            card_members = card.get("idMembers", [])
            for member_id in card_members:
                member_name = member_map.get(member_id, "Unknown")
                if member_name not in cards_by_member:
                    cards_by_member[member_name] = {
                        "total": 0,
                        "completed": 0,
                        "overdue": 0,
                        "cards": []
                    }

                cards_by_member[member_name]["total"] += 1
                cards_by_member[member_name]["cards"].append({
                    "id": card.get("id"),
                    "name": card.get("name"),
                    "due": card.get("due"),
                    "listName": card.get("listName", "Unknown")
                })

                # Check if card is in the Done list
                if card.get("listName") == "Done":
                    cards_by_member[member_name]["completed"] += 1

                # Check if card is overdue
                due_date_str = card.get("due")
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                        if due_date < datetime.now() and not card.get("dueComplete", False):
                            cards_by_member[member_name]["overdue"] += 1
                    except (ValueError, TypeError):
                        pass

        # Calculate completion rate per member
        for member_name, stats in cards_by_member.items():
            total = stats["total"]
            completed = stats["completed"]
            stats["completion_rate"] = (completed / total) * 100 if total > 0 else 0

        # Identify members with high workload (more than 50% more cards than average)
        total_assignments = sum(stats["total"] for stats in cards_by_member.values())
        avg_assignments = total_assignments / len(cards_by_member) if cards_by_member else 0
        high_workload_threshold = avg_assignments * 1.5

        members_with_high_workload = []
        for member_name, stats in cards_by_member.items():
            if stats["total"] > high_workload_threshold:
                members_with_high_workload.append({
                    "name": member_name,
                    "cards_count": stats["total"],
                    "avg_ratio": stats["total"] / avg_assignments if avg_assignments > 0 else 0
                })

        return {
            "cards_by_member": cards_by_member,
            "avg_cards_per_member": avg_assignments,
            "members_with_high_workload": members_with_high_workload,
            "member_count": len(cards_by_member)
        }

    except Exception as e:
        logger.error(f"Error analyzing team performance: {e}")
        return {
            "error": str(e),
            "cards_by_member": {},
            "avg_cards_per_member": 0,
            "members_with_high_workload": [],
            "member_count": 0
        }


def identify_process_bottlenecks(cards: List[Dict[str, Any]], lists: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify process bottlenecks based on card movement through lists.

    Args:
        cards: List of cards from Trello.
        lists: List of lists from Trello.

    Returns:
        Dictionary containing bottleneck information.
    """
    try:
        # Map list IDs to names and positions
        list_map = {}
        for list_data in lists:
            list_map[list_data["id"]] = {
                "name": list_data["name"],
                "pos": list_data.get("pos", 0)
            }

        # Sort lists by position
        sorted_lists = sorted(lists, key=lambda x: x.get("pos", 0))
        list_order = [list_data["id"] for list_data in sorted_lists]

        # Count cards in each list
        cards_by_list = {}
        for list_id, list_info in list_map.items():
            cards_by_list[list_info["name"]] = 0

        for card in cards:
            list_id = card.get("idList")
            if list_id and list_id in list_map:
                list_name = list_map[list_id]["name"]
                cards_by_list[list_name] = cards_by_list.get(list_name, 0) + 1

        # Identify bottlenecks (lists with disproportionately many cards)
        bottlenecks = []
        avg_cards_per_list = sum(cards_by_list.values()) / len(cards_by_list) if cards_by_list else 0

        for list_name, count in cards_by_list.items():
            if count > avg_cards_per_list * 1.5:
                bottlenecks.append({
                    "list_name": list_name,
                    "card_count": count,
                    "ratio_to_avg": count / avg_cards_per_list if avg_cards_per_list > 0 else 0
                })

        return {
            "cards_by_list": cards_by_list,
            "avg_cards_per_list": avg_cards_per_list,
            "bottlenecks": bottlenecks
        }

    except Exception as e:
        logger.error(f"Error identifying process bottlenecks: {e}")
        return {
            "error": str(e),
            "cards_by_list": {},
            "avg_cards_per_list": 0,
            "bottlenecks": []
        }