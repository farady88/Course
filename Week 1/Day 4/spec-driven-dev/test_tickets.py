from datetime import datetime, timedelta

from tickets import Ticket, find_duplicate_groups, load_sample_tickets, merge_duplicates


def make_ticket(**overrides) -> Ticket:
    """Build a Ticket with sensible defaults, overridable per test."""
    now = datetime.now()
    defaults = dict(
        id="HD-TEST",
        customer="Test Customer",
        subject="Test subject",
        priority="Normal",
        status="open",
        created_at=now,
        last_customer_reply_at=now,
        reply_deadline=now,
    )
    defaults.update(overrides)
    return Ticket(**defaults)


# --- escalation-spec.md ---------------------------------------------------


class TestNeedsEscalation:
    def test_open_and_more_than_5_days_old_needs_escalation(self):
        ticket = make_ticket(status="open", created_at=datetime.now() - timedelta(days=6))
        assert ticket.needs_escalation is True

    def test_open_and_4_days_old_does_not_need_escalation(self):
        ticket = make_ticket(status="open", created_at=datetime.now() - timedelta(days=4))
        assert ticket.needs_escalation is False

    def test_closed_and_10_days_old_does_not_need_escalation(self):
        ticket = make_ticket(status="closed", created_at=datetime.now() - timedelta(days=10))
        assert ticket.needs_escalation is False


class TestApplyEscalation:
    def test_escalates_ticket_more_than_5_days_old_and_open(self):
        ticket = make_ticket(status="open", created_at=datetime.now() - timedelta(days=6))
        ticket.apply_escalation()
        assert ticket.escalated_to == "senior customer service manager"

    def test_idempotent_on_repeated_calls(self):
        ticket = make_ticket(status="open", created_at=datetime.now() - timedelta(days=6))
        ticket.apply_escalation()
        ticket.apply_escalation()
        assert ticket.escalated_to == "senior customer service manager"

    def test_urgent_priority_is_not_exempt(self):
        ticket = make_ticket(
            status="open", priority="Urgent", created_at=datetime.now() - timedelta(days=10)
        )
        ticket.apply_escalation()
        assert ticket.escalated_to == "senior customer service manager"

    def test_does_not_overwrite_existing_escalation(self):
        ticket = make_ticket(status="open", created_at=datetime.now() - timedelta(days=6))
        ticket.escalated_to = "someone else"
        ticket.apply_escalation()
        assert ticket.escalated_to == "someone else"

    def test_closed_ticket_is_never_escalated(self):
        ticket = make_ticket(status="closed", created_at=datetime.now() - timedelta(days=10))
        ticket.apply_escalation()
        assert ticket.escalated_to is None


class TestEscalationOnSampleTickets:
    def test_only_open_tickets_older_than_5_days_get_escalated(self):
        tickets = load_sample_tickets()
        for ticket in tickets:
            ticket.apply_escalation()

        for ticket in tickets:
            should_be_escalated = ticket.status == "open" and ticket.days_since_created > 5
            if should_be_escalated:
                assert ticket.escalated_to == "senior customer service manager", ticket.id
            else:
                assert ticket.escalated_to is None, ticket.id


# --- duplicate-merge-spec.md -----------------------------------------------


class TestFindDuplicateGroups:
    def test_finds_one_group_of_exact_matches(self):
        now = datetime.now()
        a = make_ticket(id="A", customer="X", subject="S", created_at=now)
        b = make_ticket(id="B", customer="X", subject="S", created_at=now)
        c = make_ticket(id="C", customer="X", subject="Different", created_at=now)

        groups = find_duplicate_groups([a, b, c])

        assert groups == [[a, b]]

    def test_no_matches_returns_empty_list(self):
        now = datetime.now()
        a = make_ticket(id="A", customer="X", subject="S", created_at=now)
        b = make_ticket(id="B", customer="Y", subject="S", created_at=now)

        assert find_duplicate_groups([a, b]) == []

    def test_group_of_one_is_not_a_duplicate(self):
        now = datetime.now()
        a = make_ticket(id="A", customer="X", subject="S", created_at=now)

        assert find_duplicate_groups([a]) == []

    def test_groups_are_ordered_by_first_occurrence(self):
        now = datetime.now()
        a = make_ticket(id="A", customer="X", subject="S1", created_at=now)
        b = make_ticket(id="B", customer="X", subject="S2", created_at=now)
        c = make_ticket(id="C", customer="X", subject="S1", created_at=now)
        d = make_ticket(id="D", customer="X", subject="S2", created_at=now)

        groups = find_duplicate_groups([a, b, c, d])

        assert groups == [[a, c], [b, d]]


class TestMergeDuplicates:
    def test_survivor_is_untouched_and_loser_is_closed(self):
        now = datetime.now()
        a = make_ticket(
            id="A", customer="X", subject="S", created_at=now,
            status="open", last_customer_reply_at=now,
        )
        b = make_ticket(
            id="B", customer="X", subject="S", created_at=now,
            status="open", last_customer_reply_at=now - timedelta(days=1),
        )

        merge_duplicates([a, b])

        assert a.status == "open"
        assert a.closed_by is None
        assert a.duplicate_note is None

        assert b.status == "closed"
        assert b.closed_by == "system"
        assert b.duplicate_note == "Ticket closed due to duplicating A"

    def test_already_closed_loser_keeps_its_status_and_closed_by(self):
        now = datetime.now()
        a = make_ticket(
            id="A", customer="X", subject="S", created_at=now,
            status="open", last_customer_reply_at=now,
        )
        b = make_ticket(
            id="B", customer="X", subject="S", created_at=now,
            status="closed", closed_by="Jamie Ochieng",
            last_customer_reply_at=now - timedelta(days=1),
        )

        merge_duplicates([a, b])

        assert b.status == "closed"
        assert b.closed_by == "Jamie Ochieng"
        assert b.duplicate_note == "Ticket closed due to duplicating A"

    def test_tie_break_prefers_earliest_in_input_list(self):
        now = datetime.now()
        same_reply_time = now
        a = make_ticket(
            id="A", customer="X", subject="S", created_at=now,
            status="open", last_customer_reply_at=same_reply_time,
        )
        b = make_ticket(
            id="B", customer="X", subject="S", created_at=now,
            status="open", last_customer_reply_at=same_reply_time,
        )

        merge_duplicates([a, b])

        assert a.status == "open"
        assert a.duplicate_note is None
        assert b.status == "closed"
        assert b.duplicate_note == "Ticket closed due to duplicating A"

    def test_does_not_change_list_length_or_delete_tickets(self):
        now = datetime.now()
        a = make_ticket(id="A", customer="X", subject="S", created_at=now)
        b = make_ticket(
            id="B", customer="X", subject="S", created_at=now,
            last_customer_reply_at=now - timedelta(days=1),
        )
        c = make_ticket(id="C", customer="Y", subject="S", created_at=now)
        tickets = [a, b, c]

        merge_duplicates(tickets)

        assert len(tickets) == 3
        assert tickets == [a, b, c]

    def test_no_duplicates_leaves_everything_unchanged(self):
        tickets = load_sample_tickets()
        snapshot = [
            (t.status, t.closed_by, t.duplicate_note) for t in tickets
        ]

        merge_duplicates(tickets)

        after = [(t.status, t.closed_by, t.duplicate_note) for t in tickets]
        assert after == snapshot


class TestMergeDuplicatesOnSampleTickets:
    def test_added_duplicate_of_hd1001_is_closed_and_others_are_untouched(self):
        tickets = load_sample_tickets()
        hd1001 = next(t for t in tickets if t.id == "HD-1001")

        duplicate = make_ticket(
            id="HD-1008",
            customer=hd1001.customer,
            subject=hd1001.subject,
            created_at=hd1001.created_at,
            last_customer_reply_at=hd1001.last_customer_reply_at - timedelta(days=1),
        )
        tickets.append(duplicate)

        before = {
            t.id: (t.status, t.closed_by, t.duplicate_note)
            for t in tickets
            if t.id != "HD-1008"
        }

        merge_duplicates(tickets)

        assert duplicate.status == "closed"
        assert duplicate.closed_by == "system"
        assert duplicate.duplicate_note == "Ticket closed due to duplicating HD-1001"

        for ticket in tickets:
            if ticket.id == "HD-1008":
                continue
            assert (ticket.status, ticket.closed_by, ticket.duplicate_note) == before[ticket.id]


# --- shared field default ---------------------------------------------------


def test_duplicate_note_defaults_to_none():
    ticket = make_ticket()
    assert ticket.duplicate_note is None
