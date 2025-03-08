"""
Data Collection Agent Module

This module defines the DataCollectionAgent class, which is responsible for
gathering and organizing project data from Trello.
"""

import logging
from typing import List, Dict, Any, Optional

from src.agents.base_agent import BaseAgent
from src.tools.trello_tools import BoardDataFetcherTool, CardDataFetcherTool

# Set up logging
logger = logging.getLogger(__name__)


class DataCollectionAgent(BaseAgent):
    """
    Agent responsible for collecting and organizing project data from Trello.

    This agent fetches data from Trello boards, organizes it, identifies gaps,
    and prepares it for analysis.
    """

    def __init__(
        self,
        role: str = "Senior Data Collection Specialist",
        goal: str = "Methodically gather and organize all relevant project data from the Trello board.",
        backstory: str = "You are an experienced data scientist with a background in project management.",
        verbose: bool = True,
        allow_delegation: bool = False,
        llm: Optional[Any] = None
    ):
        """
        Initialize the data collection agent.

        Args:
            role: The role of the agent.
            goal: The goal the agent is trying to achieve.
            backstory: The backstory of the agent.
            verbose: Whether to enable verbose logging.
            allow_delegation: Whether to allow the agent to delegate tasks.
            llm: Language model to use for the agent.
        """
        tools = [BoardDataFetcherTool(), CardDataFetcherTool()]

        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=allow_delegation,
            tools=tools,
            llm=llm
        )

        logger.info("Initialized DataCollectionAgent")

    def process_trello_data(self, board_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw Trello board data into a structured format.

        Args:
            board_data: Raw board data from Trello.

        Returns:
            Processed and structured board data.
        """
        logger.info("Processing Trello data")

        if not board_data or "error" in board_data:
            error_msg = board_data.get("error", "Unknown error retrieving board data")
            logger.error(f"Error in board data: {error_msg}")
            return {"error": error_msg}

        try:
            cards = board_data.get("cards", [])
            lists = board_data.get("lists", [])
            members = board_data.get("members", [])

            logger.info(f"Processing {len(cards)} cards, {len(lists)} lists, and {len(members)} members")

            # Create maps for easier lookups
            list_map = {list_data["id"]: list_data for list_data in lists}
            member_map = {member["id"]: member for member in members}

            # Process cards
            processed_cards = []
            for card in cards:
                processed_card = self._process_card(card, list_map, member_map)
                processed_cards.append(processed_card)

            # Group cards by list
            cards_by_list = {}
            for list_data in lists:
                list_name = list_data["name"]
                cards_by_list[list_name] = []

            for card in processed_cards:
                list_name = card.get("listName", "Unknown")
                if list_name in cards_by_list:
                    cards_by_list[list_name].append(card)

            # Sort lists by position
            sorted_lists = sorted(lists, key=lambda x: x.get("pos", 0))

            result = {
                "board_id": board_data.get("board_id"),
                "cards": processed_cards,
                "lists": sorted_lists,
                "members": members,
                "cards_by_list": cards_by_list,
                "timestamp": board_data.get("timestamp")
            }

            logger.info("Successfully processed Trello data")
            return result

        except Exception as e:
            logger.error(f"Error processing board data: {str(e)}")
            return {"error": f"Error processing board data: {str(e)}"}

    def _process_card(
        self,
        card: Dict[str, Any],
        list_map: Dict[str, Dict[str, Any]],
        member_map: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a single Trello card.

        Args:
            card: Raw card data from Trello.
            list_map: Map of list IDs to list data.
            member_map: Map of member IDs to member data.

        Returns:
            Processed card data.
        """
        # Get list name
        list_id = card.get("idList")
        list_name = "Unknown"
        if list_id and list_id in list_map:
            list_name = list_map[list_id]["name"]

        # Process members
        members = []
        for member_id in card.get("idMembers", []):
            if member_id in member_map:
                member = member_map[member_id]
                members.append({
                    "id": member_id,
                    "name": member.get("fullName", member.get("username", "Unknown"))
                })

        # Process comments
        comments = []
        if "actions" in card:
            for action in card["actions"]:
                if action["type"] == "commentCard":
                    comments.append({
                        "id": action["id"],
                        "text": action["data"]["text"],
                        "date": action["date"],
                        "memberCreator": action.get("memberCreator", {})
                    })

        # Check for blockers
        is_blocker = False
        blocker_reason = None

        # Check for red labels
        for label in card.get("labels", []):
            if label.get("color") == "red":
                is_blocker = True
                blocker_reason = f"Red label: {label.get('name', 'Blocker')}"
                break

        # Check for blocker keywords in comments
        if not is_blocker:
            for comment in comments:
                if "blocker" in comment.get("text", "").lower():
                    is_blocker = True
                    blocker_reason = f"Blocker mentioned in comment: {comment['text'][:50]}..."
                    break

        return {
            "id": card.get("id"),
            "name": card.get("name"),
            "desc": card.get("desc"),
            "url": card.get("url"),
            "idList": list_id,
            "listName": list_name,
            "due": card.get("due"),
            "dueComplete": card.get("dueComplete", False),
            "dateLastActivity": card.get("dateLastActivity"),
            "labels": card.get("labels", []),
            "members": members,
            "comments": comments,
            "attachments": card.get("attachments", []),
            "isComplete": list_name == "Done",
            "isBlocker": is_blocker,
            "blockerReason": blocker_reason
        }

    def identify_data_gaps(self, processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify gaps or missing information in the collected data.

        Args:
            processed_data: Processed Trello data.

        Returns:
            List of identified data gaps.
        """
        gaps = []

        try:
            cards = processed_data.get("cards", [])

            for card in cards:
                card_gaps = []

                # Check for missing due dates on cards not in Done
                if not card.get("isComplete") and not card.get("due"):
                    card_gaps.append("Missing due date")

                # Check for missing descriptions
                if not card.get("desc"):
                    card_gaps.append("Missing description")

                # Check for missing members
                if not card.get("members"):
                    card_gaps.append("No assigned members")

                # If gaps were found for this card, add to the list
                if card_gaps:
                    gaps.append({
                        "card_id": card.get("id"),
                        "card_name": card.get("name"),
                        "list_name": card.get("listName"),
                        "gaps": card_gaps
                    })

            logger.info(f"Identified {len(gaps)} cards with data gaps")
            return gaps

        except Exception as e:
            logger.error(f"Error identifying data gaps: {str(e)}")
            return [{"error": f"Error identifying data gaps: {str(e)}"}]