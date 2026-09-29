from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Ticket:
    id: str
    customer: str
    subject: str
    priority: str  # "Normal" or "Urgent"
    status: str  # "open" or "closed"
    created_at: datetime
    last_customer_reply_at: datetime
    reply_deadline: datetime
    closed_by: Optional[str] = None
    escalated_to: Optional[str] = None
    duplicate_note: Optional[str] = None

    @property
    def days_since_last_reply(self) -> int:
        return (datetime.now() - self.last_customer_reply_at).days

    @property
    def days_since_created(self) -> int:
        return (datetime.now() - self.created_at).days

    @property
    def needs_escalation(self) -> bool:
        """True once an open ticket has missed the 5-day response target."""
        return self.status == "open" and self.days_since_created > 5

    @property
    def reply_window_status(self) -> str:
        """"closed" once the last customer reply is 14 days old or more, else "open".

        Urgent tickets are exempt and always report "open", regardless of age.
        """
        if self.priority == "Urgent":
            return "open"
        return "closed" if self.days_since_last_reply >= 14 else "open"

    def apply_reply_window_status(self) -> None:
        """Sync status with reply_window_status, marking system-driven closures."""
        if self.reply_window_status == "closed" and self.status != "closed":
            self.status = "closed"
            self.closed_by = "system"

    def apply_escalation(self) -> None:
        """Escalate to the senior customer service manager, once, if overdue."""
        if self.needs_escalation and self.escalated_to is None:
            self.escalated_to = "senior customer service manager"


def find_duplicate_groups(tickets: List[Ticket]) -> List[List[Ticket]]:
    """Group tickets sharing (customer, subject, created_at); keep only groups of 2+."""
    groups: dict = {}
    for ticket in tickets:
        key = (ticket.customer, ticket.subject, ticket.created_at)
        groups.setdefault(key, []).append(ticket)
    return [group for group in groups.values() if len(group) >= 2]


def merge_duplicates(tickets: List[Ticket]) -> None:
    """Close every duplicate but the most-recently-replied-to survivor in each group."""
    for group in find_duplicate_groups(tickets):
        survivor = max(group, key=lambda t: t.last_customer_reply_at)
        for loser in group:
            if loser is survivor:
                continue
            loser.duplicate_note = f"Ticket closed due to duplicating {survivor.id}"
            if loser.status != "closed":
                loser.status = "closed"
                loser.closed_by = "system"


def _days_ago(n: int) -> datetime:
    return datetime.now() - timedelta(days=n)


def load_sample_tickets() -> List[Ticket]:
    """Return a fresh list of sample tickets, dated relative to today."""
    return [
        Ticket(
            id="HD-1001",
            customer="Priya Shah",
            subject="Invoice PDF won't download",
            priority="Normal",
            status="open",
            created_at=_days_ago(20),
            last_customer_reply_at=_days_ago(14),
            reply_deadline=_days_ago(-2),
        ),
        Ticket(
            id="HD-1002",
            customer="Callum Reid",
            subject="Can't reset account password",
            priority="Normal",
            status="open",
            created_at=_days_ago(15),
            last_customer_reply_at=_days_ago(13),
            reply_deadline=_days_ago(-4),
        ),
        Ticket(
            id="HD-1003",
            customer="Aiswarya Menon",
            subject="Production integration returning 500s",
            priority="Urgent",
            status="open",
            created_at=_days_ago(45),
            last_customer_reply_at=_days_ago(40),
            reply_deadline=_days_ago(30),
        ),
        Ticket(
            id="HD-1004",
            customer="Ben Okafor",
            subject="Question about billing cycle",
            priority="Normal",
            status="closed",
            created_at=_days_ago(60),
            last_customer_reply_at=_days_ago(35),
            reply_deadline=_days_ago(20),
            closed_by="Jamie Ochieng",
        ),
        Ticket(
            id="HD-1005",
            customer="Freya Lindqvist",
            subject="Export button does nothing",
            priority="Normal",
            status="open",
            created_at=_days_ago(33),
            last_customer_reply_at=_days_ago(30),
            reply_deadline=_days_ago(18),
        ),
        Ticket(
            id="HD-1006",
            customer="Marcus Tan",
            subject="Feature request: dark mode",
            priority="Normal",
            status="open",
            created_at=_days_ago(10),
            last_customer_reply_at=_days_ago(2),
            reply_deadline=_days_ago(-5),
        ),
        Ticket(
            id="HD-1007",
            customer="Nadia Hassan",
            subject="Login page intermittently blank",
            priority="Urgent",
            status="open",
            created_at=_days_ago(6),
            last_customer_reply_at=_days_ago(5),
            reply_deadline=_days_ago(-1),
        ),
    ]
