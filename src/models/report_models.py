"""
Trello Models Module

This module defines Pydantic models for Trello data structures used throughout the application.
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


class TrelloLabel(BaseModel):
    """Model for Trello card label."""
    id: str
    name: Optional[str] = ""
    color: Optional[str] = None

    @validator('name', pre=True)
    def validate_empty_name(cls, v):
        """Set empty string to label color if name is empty."""
        if not v and hasattr(cls, 'color') and cls.color:
            return cls.color.capitalize()
        return v or ""


class TrelloAttachment(BaseModel):
    """Model for Trello card attachment."""
    id: str
    name: str
    url: str
    date: Optional[str] = None
    bytes: Optional[int] = None
    mimeType: Optional[str] = None

    @property
    def datetime(self) -> Optional[datetime]:
        """Convert date string to datetime object."""
        if self.date:
            try:
                return datetime.fromisoformat(self.date.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return None
        return None


class TrelloComment(BaseModel):
    """Model for Trello card comment."""
    id: str
    text: str
    date: str
    memberCreator: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @property
    def datetime(self) -> datetime:
        """Convert date string to datetime object."""
        return datetime.fromisoformat(self.date.replace("Z", "+00:00"))

    @property
    def creator_name(self) -> str:
        """Get the name of the comment creator."""
        if self.memberCreator:
            return self.memberCreator.get('fullName',
                                          self.memberCreator.get('username', 'Unknown'))
        return "Unknown"


class TrelloMember(BaseModel):
    """Model for Trello board member."""
    id: str
    fullName: Optional[str] = None
    username: str
    avatarUrl: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get the display name of the member."""
        return self.fullName or self.username


class TrelloCustomField(BaseModel):
    """Model for Trello custom field."""
    id: str
    idCustomField: str
    idValue: Optional[str] = None
    value: Optional[Dict[str, Any]] = None

    @property
    def field_value(self) -> Any:
        """Get the value of the custom field."""
        if not self.value:
            return None

        if 'number' in self.value:
            return self.value['number']
        elif 'text' in self.value:
            return self.value['text']
        elif 'date' in self.value:
            return self.value['date']
        elif 'checked' in self.value:
            return self.value['checked']

        return None


class TrelloList(BaseModel):
    """Model for Trello list."""
    id: str
    name: str
    closed: bool = False
    pos: Optional[float] = None


class TrelloCard(BaseModel):
    """Model for Trello card."""
    id: str
    name: str
    desc: Optional[str] = ""
    idList: Optional[str] = None
    idBoard: Optional[str] = None
    due: Optional[str] = None
    dueComplete: bool = False
    dateLastActivity: Optional[str] = None
    labels: List[TrelloLabel] = Field(default_factory=list)
    url: Optional[str] = None
    attachments: List[TrelloAttachment] = Field(default_factory=list)
    comments: List[TrelloComment] = Field(default_factory=list)
    members: List[Dict[str, Any]] = Field(default_factory=list)
    customFields: List[TrelloCustomField] = Field(default_factory=list)
    listName: Optional[str] = None

    @property
    def due_date(self) -> Optional[datetime]:
        """Convert due string to datetime object."""
        if self.due:
            try:
                return datetime.fromisoformat(self.due.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return None
        return None

    @property
    def last_activity_date(self) -> Optional[datetime]:
        """Convert last activity string to datetime object."""
        if self.dateLastActivity:
            try:
                return datetime.fromisoformat(self.dateLastActivity.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return None
        return None

    @property
    def is_overdue(self) -> bool:
        """Check if the card is overdue."""
        if not self.due_date or self.dueComplete:
            return False
        return self.due_date < datetime.now()

    @property
    def member_names(self) -> List[str]:
        """Get the names of the card members."""
        return [member.get('fullName', member.get('username', 'Unknown'))
                for member in self.members]

    @property
    def label_names(self) -> List[str]:
        """Get the names of the card labels."""
        return [label.name for label in self.labels if label.name]

    @property
    def label_colors(self) -> List[str]:
        """Get the colors of the card labels."""
        return [label.color for label in self.labels if label.color]

    @property
    def has_red_label(self) -> bool:
        """Check if the card has a red label."""
        return 'red' in self.label_colors

    @property
    def has_blocker_comment(self) -> bool:
        """Check if the card has a comment mentioning a blocker."""
        return any('blocker' in comment.text.lower() for comment in self.comments)

    @property
    def is_blocker(self) -> bool:
        """Check if the card is a blocker."""
        return self.has_red_label or self.has_blocker_comment


class TrelloBoard(BaseModel):
    """Model for Trello board data."""
    board_id: str
    cards: List[TrelloCard] = Field(default_factory=list)
    lists: List[TrelloList] = Field(default_factory=list)
    members: List[TrelloMember] = Field(default_factory=list)
    timestamp: float
    status: str

    @property
    def cards_by_list(self) -> Dict[str, List[TrelloCard]]:
        """Group cards by list name."""
        result = {}
        for card in self.cards:
            list_name = card.listName or "Unknown"
            if list_name not in result:
                result[list_name] = []
            result[list_name].append(card)
        return result

    @property
    def cards_by_member(self) -> Dict[str, List[TrelloCard]]:
        """Group cards by member name."""
        result = {}
        for card in self.cards:
            for member_name in card.member_names:
                if member_name not in result:
                    result[member_name] = []
                result[member_name].append(card)
        return result

    @property
    def blockers(self) -> List[TrelloCard]:
        """Get all blocker cards."""
        return [card for card in self.cards if card.is_blocker]

    @property
    def overdue_cards(self) -> List[TrelloCard]:
        """Get all overdue cards."""
        return [card for card in self.cards if card.is_overdue]