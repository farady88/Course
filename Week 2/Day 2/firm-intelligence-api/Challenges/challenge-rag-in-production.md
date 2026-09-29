# Challenge: taking RAG into production

**60 minutes. Pairs. Laptops for research. Whiteboard for the deliverable.**

**Nothing in this challenge touches your codebase.** You are not debugging, reviewing, or
fixing anything you built today. You are going away and finding out what real companies have
learned the hard way about running RAG in a live system that already has real users - then
bringing that back and putting it on a whiteboard.

---

## The framing

What you built today is a working prototype. Plenty of real companies have shipped exactly
that far and stopped, then spent the following six months rectifying. Your job for the next hour is to go find out what that "everything"
actually is, before we implement it together.

---

## Pick two

Each pair picks **two** of the five topics below. Research it properly - read more than one
source - then be ready to explain it to someone who didn't research it, in plain terms.

**1. Keeping the index honest**
Your corpus doesn't sit still in a real system - documents change, get deleted, get added.
What actually happens to a vector index when the thing it was built from changes underneath
it? What do production teams do about it?

**2. Who's allowed to see what**
Semantic search doesn't know about permissions the way a normal database query does. What
goes wrong when RAG is bolted onto a system where different users are meant to see different
data? Find a real example of this failing.

**3. How do you know it's actually working**
Once it's live, how do teams measure whether retrieval is any good - and whether it's quietly
getting worse over time - without just eyeballing a few answers?

**4. What it costs at real scale**
Eight documents costs nothing. What does the same architecture cost once it's eight million,
and what do teams actually do to control that?

**5. Putting it in front of real users without breaking things**
How do you introduce a new capability like this into a system that already has live traffic
and existing users, without risking what's already working?

---

## Deliverable - one whiteboard, two topics

For each topic you researched, put up:
- **What you found** - 3 to 4 bullet points, plain language, no jargon you can't explain
- **Where it came from** - at least one source you'd point someone to
- **What it would actually mean for a service like the one you built today** - one or two
  sentences, thinking generally about a small internal API with a handful of documents versus
  a real system with real users, not about your specific code

---

## At the end

Be ready to spend two minutes explaining your two topics to a pair who researched different
ones. By the end of the session the room should collectively know something about all five,
even though no individual pair researched all five themselves.
