# Spec: Escalate tickets that miss the 5-day response target

## Why

Tickets that sit open for days with no staff response risk breaching customer
expectations, and nobody currently gets flagged when that happens. This
feature marks a ticket as escalated once it has been open too long, so a
senior customer service manager can be pointed at it.

## What

- Add a computed value `days_since_created`: the number of whole days between
  `created_at` and now, using the same `(datetime.now() - x).days` pattern as
  `days_since_last_reply`.
- A ticket **needs escalation** when both are true:
  - `status == "open"`
  - `days_since_created > 5` (more than 5 days)
- This check applies to every ticket regardless of `priority` — `Urgent`
  tickets are **not** exempt here (unlike `reply_window_status`, which does
  exempt them).
- Escalating a ticket sets `escalated_to = "senior customer service manager"`
  on that ticket. `"senior customer service manager"` is a fixed string
  constant, the same value every time — not a lookup, not configurable per
  ticket.
- Escalation is one-way and idempotent: once `escalated_to` is set, applying
  the escalation check again does nothing, even if the ticket is still open
  and still past 5 days. It is never cleared or overwritten by this feature.
- A ticket whose `status` is `"closed"` — whether closed by a person, or by
  `apply_reply_window_status()` — is never escalated, even if it was open
  past 5 days before it closed.

## Context

- Files: `tickets.py` only. No other files exist in this project.
- Pattern to match: `apply_reply_window_status()` (a method that mutates
  state on the `Ticket` in place, checks a computed condition, and is a
  no-op if the outcome already holds — e.g. it does nothing if `status` is
  already `"closed"`). The new `apply_escalation()` method follows the same
  shape: compute-then-mutate, safe to call repeatedly.
- Pattern to match: `days_since_last_reply` / `reply_window_status`, a pair of
  `@property` methods where one computes a day count and the other derives a
  status from it. `days_since_created` / `needs_escalation` follow the same
  pair shape.
- Settled: `escalated_to` is a new `Optional[str] = None` field on `Ticket`,
  directly analogous to the existing `closed_by: Optional[str] = None`.
- Settled: the 5-day target is measured from `created_at`, not from
  `reply_deadline`. The existing `reply_deadline` field is unrelated to this
  feature and is not read or changed by it.
- Settled: no new libraries. No new module-level state — the escalation
  target string lives as a constant in `tickets.py`.

## Constraints

- Do not touch `reply_deadline`, `last_customer_reply_at`,
  `reply_window_status`, or `apply_reply_window_status()` — this feature is
  additive, not a change to the existing reply-window behaviour.
- Do not exempt `Urgent` tickets from escalation.
- Out of scope: sending any notification, email, or message to the senior
  customer service manager. `escalated_to` is a data field only — nothing
  reads it or acts on it beyond this spec.
- Out of scope: any UI, CLI output, or logging.
- Out of scope: a way to un-escalate a ticket, or to escalate to anyone other
  than the fixed "senior customer service manager" string.
- Out of scope: changing `load_sample_tickets()` or adding new sample data.

## Tasks

1. **Add the field and computed properties.**
   Touches: `tickets.py` (`Ticket` class)
   - Add `escalated_to: Optional[str] = None` to the `Ticket` dataclass,
     placed after `closed_by`.
   - Add `@property days_since_created(self) -> int`, mirroring
     `days_since_last_reply` but measured from `created_at`.
   - Add `@property needs_escalation(self) -> bool`, returning `True` only
     when `status == "open"` and `days_since_created > 5`.
   - Verify: a ticket with `created_at` more than 5 days ago and `status="open"` has
     `needs_escalation == True`. One with `created_at` 4 days ago and
     `status="open"` has `needs_escalation == False`. One with `created_at`
     10 days ago and `status="closed"` has `needs_escalation == False`.

2. **Apply the escalation.**
   Touches: `tickets.py` (`Ticket` class)
   - Add `apply_escalation(self) -> None`: if `needs_escalation` is `True`
     and `escalated_to` is `None`, set
     `escalated_to = "senior customer service manager"`. Otherwise do
     nothing.
   - Verify: a ticket more than 5 days old and open gets `escalated_to ==
     "senior customer service manager"` after calling `apply_escalation()`.
     Calling `apply_escalation()` a second time on that same ticket leaves
     `escalated_to` unchanged at `"senior customer service manager"`. A
     ticket 10 days old with `priority="Urgent"` and `status="open"` still
     gets escalated.

## Done

After both tasks: for every ticket in `load_sample_tickets()`, calling
`apply_escalation()` results in `escalated_to == "senior customer service
manager"` on exactly the tickets that are `status == "open"` and more than 5
days old, and `escalated_to == None` on every other ticket — regardless of
`priority`.
