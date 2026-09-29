# Week 2 Day 1 PM: build the Library API

- `starter/`  distribute this. It is stage 0: one endpoint, gate-clean.
- `stages/`   trainer reference. One snapshot per stage, so you can jump to any point.
- `w2d1-PM-BUILD-GUIDE.md`  the second-by-second guide.

Stage files: stage0 (20 lines) -> stage1 (29) -> stage2 (43) -> stage3 (67)
-> stage4 (89) -> stage5/6 (129), plus stage6_tests.py (86) and FINAL_api.py.

Setup, from inside starter/:
    uv venv .venv --python 3.12
    uv pip install --python .venv/bin/python -r requirements.txt
    PYTHONPATH=src .venv/bin/python -m uvicorn api:app --reload
