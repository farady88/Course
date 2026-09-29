# Helpdesk ticket starter

A small Python data model for a helpdesk's support tickets, with a handful of
sample tickets to build against. This is the whole starting point: no
behaviour, no tests, no framework. Everything else gets added as each brief
asks for it.

## What's here

- `tickets.py` - the `Ticket` data class and `load_sample_tickets()`, which
  returns a fresh list of sample tickets dated relative to today, so the ages
  work whenever you run it.

## Using it

Copy this folder into your own project, `git init`, and commit it as your
starting point before you build anything on top of it. Requires Python 3.9 or
later, for the type hints used in `tickets.py`. No other dependencies.

Keep building in the same project for the rest of the day. Each new feature
goes on top of the last.
