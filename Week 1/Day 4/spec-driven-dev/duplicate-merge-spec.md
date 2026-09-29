# Spec: Detect and merge duplicate tickets

## Why

The same issue sometimes gets logged as more than one ticket for the same
customer, which splits attention across records that should be one
conversation. This feature finds those duplicates and closes the redundant
copies, leaving a clear trail back to the ticket that survives.

## What

- Two tickets are **duplicates** of each other when all three match exactly:
  `customer`, `subject`, and `created_at`. No fuzzy or partial matching.
- Duplicates are found by grouping *all* tickets (any `status`, including
  already-closed or already-escalated ones) by the
  `(customer, subject, created_at)` triple. Any group with 2 or more tickets
  is a duplicate group. A group of exactly 1 is not a duplicate and is left
  untouched.
- Within a duplicate group, exactly one ticket **survives**: the one with the
  most recent `last_customer_reply_at`. Every other ticket in the group is a
  **loser**.
  - Tie-break: if two or more tickets in the group have the same
    `last_customer_reply_at` (down to the microsecond), the one that appears
    **earliest in the input list** survives.
  - The survivor is not modified in any way by this feature.
- Each loser is updated in place:
  - `duplicate_note` is set to the exact string
    `f"Ticket closed due to duplicating {survivor.id}"`, e.g.
    `"Ticket closed due to duplicating HD-1002"`.
  - If the loser's `status` is not already `"closed"`, set `status =
    "closed"` and `closed_by = "system"` — the same convention
    `apply_reply_window_status()` already uses for automatic closures.
  - If the loser is **already** `"closed"` (by a person or by
    `apply_reply_window_status()`), its `status` and `closed_by` are left
    exactly as they are. Only `duplicate_note` is set. A human or system
    closer is never overwritten or relabelled by this feature.
  - `duplicate_note` is always set for a loser, regardless of its `status`.

## Context

- Files: `tickets.py` only. No other files exist in this project.
- Pattern to match: `apply_reply_window_status()` and `apply_escalation()` —
  both are idempotent, mutate a `Ticket` in place, and use `closed_by =
  "system"` for automatic closures. This feature reuses that same
  `closed_by = "system"` convention, but only when it is the one actually
  closing the ticket.
- Settled: `duplicate_note` is a new `Optional[str] = None` field on
  `Ticket`, placed after `escalated_to`.
- Settled: this feature is the first one that compares *multiple* tickets
  against each other, so it cannot be a `Ticket` method. It is two new
  module-level functions in `tickets.py`, alongside `load_sample_tickets()`.
- Settled: no new libraries. Grouping is done with a plain dict keyed by the
  `(customer, subject, created_at)` tuple.

## Constraints

- Do not delete any ticket from the list, or change the length of the list
  returned by anything. Losers stay in the list, closed, with a
  `duplicate_note`.
- Do not modify the survivor. Its `status`, `closed_by`, and every other
  field are untouched, even if it was itself already closed.
- Do not overwrite `status` or `closed_by` on a loser that is already closed.
  `duplicate_note` is the only field touched on an already-closed loser.
- Do not do fuzzy, case-insensitive, or partial matching on `customer` or
  `subject`. Exact equality only, on all three of `customer`, `subject`, and
  `created_at`.
- Out of scope: any notification, email, or message about the merge.
- Out of scope: merging or copying any field *from* a loser *onto* the
  survivor (e.g. no field of the survivor changes because of a loser).
- Out of scope: any UI, CLI output, or logging.
- Out of scope: changing `load_sample_tickets()` or adding new sample data.
- Out of scope: handling duplicate groups larger than what plain equality
  grouping produces (e.g. no "fuzzy chains" where A duplicates B duplicates
  C but A and C don't match each other directly).

## Tasks

1. **Add the field.**
   Touches: `tickets.py` (`Ticket` class)
   - Add `duplicate_note: Optional[str] = None` to the `Ticket` dataclass,
     placed after `escalated_to`.
   - Verify: a `Ticket` constructed without passing `duplicate_note` has
     `duplicate_note is None`.

2. **Find duplicate groups.**
   Touches: `tickets.py` (new module-level function)
   - Add `find_duplicate_groups(tickets: List[Ticket]) -> List[List[Ticket]]`.
     Groups tickets by `(customer, subject, created_at)` and returns only
     the groups with 2 or more tickets, in the order their key was first
     seen in the input list.
   - Verify: given three tickets where two share the same `customer`,
     `subject`, and `created_at`, and a third has a different `subject`,
     `find_duplicate_groups` returns one group containing exactly the two
     matching tickets. An input list with no matching triples returns `[]`.

3. **Merge duplicates.**
   Touches: `tickets.py` (new module-level function)
   - Add `merge_duplicates(tickets: List[Ticket]) -> None`. Uses
     `find_duplicate_groups`. For each group, picks the survivor (most
     recent `last_customer_reply_at`, earliest-in-list on a tie) and, for
     every other ticket in the group, sets `duplicate_note` and — only if
     not already `"closed"` — sets `status = "closed"` and `closed_by =
     "system"`.
   - Verify: two duplicate tickets, both `status="open"`, where ticket A has
     a more recent `last_customer_reply_at` than ticket B — after
     `merge_duplicates`, A is unchanged (`status="open"`, `closed_by=None`,
     `duplicate_note=None`) and B has `status="closed"`,
     `closed_by="system"`, `duplicate_note=f"Ticket closed due to
     duplicating {A.id}"`.
   - Verify (already-closed loser): same as above but B starts with
     `status="closed"`, `closed_by="Jamie Ochieng"` — after
     `merge_duplicates`, B still has `status="closed"`,
     `closed_by="Jamie Ochieng"` (unchanged), and `duplicate_note` is now
     set to reference A.

## Done

After all three tasks: running `merge_duplicates` on
`load_sample_tickets()` plus one added ticket that duplicates `HD-1001`
(same `customer`, `subject`, `created_at`, but an older
`last_customer_reply_at`) results in the added ticket being `status="closed"`,
`closed_by="system"`, with `duplicate_note` referencing `HD-1001` — and every
other ticket, including `HD-1001` itself, is unchanged.
