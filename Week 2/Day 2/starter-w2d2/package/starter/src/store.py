"""In-memory data store. SYNTHETIC PLACEHOLDER DATA ONLY.

A list of dicts standing in for a database. Deliberately small enough to hold
in your head: twelve books, six authors, two books each.
"""

BOOKS: list[dict[str, object]] = [
    {"id": 1, "title": "The Long Way Round", "author": "A. Sterling",
     "year": 1998, "borrowed_by": None},
    {"id": 2, "title": "Quiet Machines", "author": "A. Sterling",
     "year": 2004, "borrowed_by": None},
    {"id": 3, "title": "Nothing Doing", "author": "B. Okafor",
     "year": 2011, "borrowed_by": "sam"},
    {"id": 4, "title": "Salt and Iron", "author": "B. Okafor",
     "year": 2015, "borrowed_by": None},
    {"id": 5, "title": "The Cartographer", "author": "C. Lindqvist",
     "year": 2019, "borrowed_by": None},
    {"id": 6, "title": "Winter Harbour", "author": "C. Lindqvist",
     "year": 2001, "borrowed_by": "rana"},
    {"id": 7, "title": "Glass Hours", "author": "D. Mwangi",
     "year": 2007, "borrowed_by": None},
    {"id": 8, "title": "A Field Guide to Nowhere", "author": "D. Mwangi",
     "year": 2013, "borrowed_by": None},
    {"id": 9, "title": "Thirteen Ways Home", "author": "E. Ferreira",
     "year": 2017, "borrowed_by": None},
    {"id": 10, "title": "The Undersong", "author": "E. Ferreira",
     "year": 2020, "borrowed_by": "kit"},
    {"id": 11, "title": "Paper Moths", "author": "F. Adeyemi",
     "year": 2022, "borrowed_by": None},
    {"id": 12, "title": "Last Light on the Pier", "author": "F. Adeyemi",
     "year": 2024, "borrowed_by": None},
]
