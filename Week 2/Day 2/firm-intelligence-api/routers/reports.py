"""Reports API — handed over by a contractor. Not reviewed.

SYNTHETIC PLACEHOLDER DATA ONLY.
"""

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/reports", tags=["reports"])

#The data being in the router file may cause unintended changes to be made to the data
REPORTS: list[dict[str, Any]] = [
    {"id": 1, "title": "UK Market Outlook", "firm_id": 1, "revisions": ["v1"]},
    {"id": 2, "title": "US Partner Compensation", "firm_id": 2, "revisions": ["v1"]},
]

_view_counts: dict[int, int] = {}


class NewReport(BaseModel):
    title: str = Field(min_length=1)
    firm_id: int


def get_report_or_404(report_id: int) -> dict:
    for report in REPORTS:
        if report["id"] == report_id:
            return report
    raise HTTPException(status_code=404, detail=f"No report with id {report_id}")


@router.get("")
def list_reports():
    return REPORTS


#2.GET /reports/{id} 
@router.get("/{report_id}")
async def get_report(report_id: int):
    report = get_report_or_404(report_id)
    _view_counts[report_id] = _view_counts.get(report_id, 0) + 1
    return {**report, "views": _view_counts[report_id]}

#4.Validate firm_id so reports of none existing firms cannnot be made
@router.post("", status_code=201)
def create_report(new: NewReport):
    #get_firm_or_404(new.firm_id) # raises a 404 here if the firm doesn't exist
    new_id = max(report["id"] for report in REPORTS) + 1
    report = {
        "id": new_id,
        "title": new.title,
        "firm_id": new.firm_id,
        "revisions": ["v1"],
    }
    REPORTS.append(report)
    return report


@router.put("/{report_id}")
def update_report(report_id: int, new: NewReport):
    report = get_report_or_404(report_id)
    report["title"] = new.title
    report["firm_id"] = new.firm_id
    report["revisions"].append(f"v{len(report['revisions']) + 1}")
    return report


#1.expoort_report blocks the servers event loop and could make unrelated requests hang unneccessarily 
@router.get("/{report_id}/export")
async def export_report(report_id: int):
    report = get_report_or_404(report_id)
    await asyncio.sleep(3)
    return {"id": report["id"], "title": report["title"], "format": "pdf"}


@router.delete("/{report_id}", status_code=204)
def delete_report(report_id: int):
    report = get_report_or_404(report_id)
    REPORTS.remove(report)
    return
