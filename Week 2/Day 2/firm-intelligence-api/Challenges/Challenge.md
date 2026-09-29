#### Key concerns

1. time.sleep(3) is inside an async endpoint. time.sleep(3) blocks for three seconds. Because the endpoint is async, that can stop the server from handling other requests on the same event loop while it waits.

So one export request could make unrelated users wait too.

2. PUT /reports/{id} adds a new revision every time.

If the same update is sent twice, it creates another revision even if nothing actually changed. This is a concern because clients sometimes retry requests when a network response is lost, so one intended update could accidentally create multiple revisions.

3. POST /reports
- It hasnt validated the firm_id, so it can create a report for a non-existent firm. It also does not check for duplicate titles.


4. GET /reports/{id} increases the view count.

A GET request is normally expected to just read data, but this one changes _view_counts every time it is called. That means calling the same URL twice changes the server state and gives a different result the second time.




1. how to fix concern 1 - I would replace time.sleep(3) with await asyncio.sleep(3). Because the endpoint is async, time.sleep blocks the event loop, whereas asyncio.sleep yields control back to the event loop so other requests can continue being handled.

@router.get("/{report_id}/export")
async def export_report(report_id: int):
    report = get_report_or_404(report_id)
    await asyncio.sleep(3)
    return {"id": report["id"], "title": report["title"], "format": "pdf"}



we confirmed this change by sending these requests:

curl -s -w "Request 1: %{time_total}s\n" http://127.0.0.1:8000/reports/1/export &
curl -s -w "Request 2: %{time_total}s\n" http://127.0.0.1:8000/reports/1/export &
wait

Before the fix, the second request could be delayed behind the first; after the fix, both should complete in roughly three seconds rather than around six.



We didnt fix the missing firm_id validation, the non-idempotent PUT, or the GET side effect. To fix those properly, we’d need to validate the firm exists before creating a report, define how duplicate or repeated updates should be detected before creating a revision, and decide whether view tracking should be moved out of the GET path.
Message Kamile Raubaite