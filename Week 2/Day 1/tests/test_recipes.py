"""Acceptance tests for the Recipe Box API, written directly from SPEC.md.

Written before src/main.py has any routes wired up (Task 2 of SPEC.md).
Every test is expected to fail at this point -- that failure is the point:
these tests define what "done" means before the implementation exists.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

REQUIRED_FIELDS = ["title", "ingredients", "instructions", "prep_minutes", "servings"]


def make_recipe(**overrides: object) -> dict:
    """A valid recipe payload (R1), with optional field overrides."""
    payload: dict = {
        "title": "Pancakes",
        "ingredients": ["flour", "milk", "eggs"],
        "instructions": ["Mix ingredients", "Cook on a griddle"],
        "prep_minutes": 15,
        "servings": 4,
    }
    payload.update(overrides)
    return payload


def create_recipe(**overrides: object) -> dict:
    """POST a valid recipe and return the parsed response body."""
    response = client.post("/recipes", json=make_recipe(**overrides))
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# POST /recipes
# ---------------------------------------------------------------------------


def test_post_success_returns_full_recipe() -> None:
    # R14: success -> 201 Created with full Recipe object, including id.
    # R1: response contains all resource-model fields with correct values.
    # R2: id is a non-empty, opaque, server-generated string.
    body = make_recipe()
    response = client.post("/recipes", json=body)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], str)
    assert data["id"] != ""
    assert data["title"] == body["title"]
    assert data["ingredients"] == body["ingredients"]
    assert data["instructions"] == body["instructions"]
    assert data["prep_minutes"] == body["prep_minutes"]
    assert data["servings"] == body["servings"]


def test_post_response_has_no_extra_fields() -> None:
    # R28: recipes have no owner field and are not scoped per-user.
    # R3: there is no created_at field.
    data = create_recipe()
    assert set(data.keys()) == {
        "id",
        "title",
        "ingredients",
        "instructions",
        "prep_minutes",
        "servings",
    }


def test_post_requires_no_authentication() -> None:
    # R29: no authentication or authorization is required.
    response = client.post("/recipes", json=make_recipe())
    assert response.status_code == 201


@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
def test_post_missing_required_field_is_422(missing_field: str) -> None:
    # R12: any of the five required fields missing -> 422.
    body = make_recipe()
    del body[missing_field]
    response = client.post("/recipes", json=body)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": ""},  # below min length 1
        {"title": "a" * 121},  # above max length 120
        {"title": 123},  # wrong type
        {"ingredients": []},  # below min 1 entry
        {"ingredients": [""]},  # entry below min length 1
        {"ingredients": ["a" * 201]},  # entry above max length 200
        {"ingredients": "flour"},  # wrong type (not a list)
        {"instructions": []},  # below min 1 entry
        {"instructions": [""]},  # entry below min length 1
        {"instructions": ["a" * 501]},  # entry above max length 500
        {"instructions": "mix it"},  # wrong type (not a list)
        {"prep_minutes": -1},  # below min 0
        {"prep_minutes": 1441},  # above max 1440
        {"prep_minutes": "fifteen"},  # wrong type
        {"servings": 0},  # below min 1
        {"servings": 101},  # above max 100
        {"servings": "four"},  # wrong type
    ],
)
def test_post_field_validation_failure_is_422(overrides: dict) -> None:
    # R13: a field failing R1's validation -> 422.
    response = client.post("/recipes", json=make_recipe(**overrides))
    assert response.status_code == 422


def test_post_duplicate_title_allowed() -> None:
    # R15: duplicate title values across different recipes are permitted.
    first = create_recipe(title="Waffles")
    second = create_recipe(title="Waffles")
    assert first["id"] != second["id"]
    assert first["title"] == second["title"] == "Waffles"


def test_post_unknown_field_is_422() -> None:
    # R16: a request body field not in R1's field list -> 422.
    body = make_recipe()
    body["category"] = "breakfast"
    response = client.post("/recipes", json=body)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /recipes/{id}
# ---------------------------------------------------------------------------


def test_get_recipe_by_id_found() -> None:
    # R10: {id} found -> 200 OK with the full Recipe object.
    created = create_recipe()
    response = client.get(f"/recipes/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_recipe_by_id_not_found() -> None:
    # R11: {id} not found -> 404 Not Found.
    response = client.get("/recipes/does-not-exist")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /recipes
# ---------------------------------------------------------------------------


def test_list_recipes_default_pagination_and_shape() -> None:
    # R6: success -> 200 OK with items, limit, offset, and total.
    # R9: items contain the full Recipe object, not a summary.
    # R4/R5: defaults are limit=20, offset=0.
    created = create_recipe()
    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert data["total"] >= 1
    assert created in data["items"]


def test_list_recipes_insertion_order() -> None:
    # R3: GET /recipes orders results by insertion order, oldest first.
    first = create_recipe(title="First")
    second = create_recipe(title="Second")
    third = create_recipe(title="Third")
    response = client.get("/recipes", params={"limit": 100, "offset": 0})
    ids_in_order = [item["id"] for item in response.json()["items"]]
    assert ids_in_order.index(first["id"]) < ids_in_order.index(second["id"])
    assert ids_in_order.index(second["id"]) < ids_in_order.index(third["id"])


def test_list_recipes_explicit_limit_and_offset() -> None:
    # R4: limit query param is honoured.
    # R5: offset query param is honoured.
    for i in range(5):
        create_recipe(title=f"Recipe {i}")
    response = client.get("/recipes", params={"limit": 2, "offset": 1})
    data = response.json()
    assert response.status_code == 200
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["items"]) == 2


def test_list_recipes_offset_past_end_is_empty_not_error() -> None:
    # R7: offset at or beyond total -> 200 OK with items: [], not an error.
    create_recipe()
    response = client.get("/recipes", params={"limit": 20, "offset": 1_000_000})
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},  # below min 1
        {"limit": 101},  # above max 100
        {"limit": -1},  # negative
        {"limit": "abc"},  # non-integer
        {"offset": -1},  # below min 0
        {"offset": "abc"},  # non-integer
    ],
)
def test_list_recipes_invalid_pagination_is_400(params: dict) -> None:
    # R8: limit/offset outside bounds, or non-integer -> 400 Bad Request.
    response = client.get("/recipes", params=params)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /recipes/{id}
# ---------------------------------------------------------------------------


def test_patch_success_updates_only_given_fields() -> None:
    # R21: success -> 200 OK with full updated object; omitted fields unchanged.
    created = create_recipe()
    response = client.patch(f"/recipes/{created['id']}", json={"servings": 6})
    assert response.status_code == 200
    data = response.json()
    assert data["servings"] == 6
    assert data["title"] == created["title"]
    assert data["ingredients"] == created["ingredients"]
    assert data["instructions"] == created["instructions"]
    assert data["prep_minutes"] == created["prep_minutes"]
    assert data["id"] == created["id"]


def test_patch_not_found() -> None:
    # R18: {id} not found -> 404 Not Found.
    response = client.patch("/recipes/does-not-exist", json={"servings": 6})
    assert response.status_code == 404


def test_patch_empty_body_is_noop() -> None:
    # R20: an empty body ({}) -> 200 OK, recipe returned unchanged.
    created = create_recipe()
    response = client.patch(f"/recipes/{created['id']}", json={})
    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.parametrize(
    "body",
    [
        {"id": "client-supplied-id"},
        {"category": "breakfast"},
        {"created_at": "2024-01-01"},
    ],
)
def test_patch_unknown_field_is_422(body: dict) -> None:
    # R17: only title/ingredients/instructions/prep_minutes/servings may
    # appear in the body; any other key -> 422 Unprocessable Entity.
    created = create_recipe()
    response = client.patch(f"/recipes/{created['id']}", json=body)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "body",
    [
        {"title": ""},
        {"prep_minutes": -1},
        {"servings": 0},
        {"ingredients": []},
        {"instructions": []},
    ],
)
def test_patch_field_validation_failure_is_422(body: dict) -> None:
    # R19: any field present must pass the same validation as R13.
    created = create_recipe()
    response = client.patch(f"/recipes/{created['id']}", json=body)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /recipes/{id}
# ---------------------------------------------------------------------------


def test_delete_not_found() -> None:
    # R22: {id} not found -> 404 Not Found.
    response = client.delete("/recipes/does-not-exist")
    assert response.status_code == 404


def test_delete_success_is_hard_delete() -> None:
    # R23: success -> 204 No Content, empty body; deletion is a hard delete.
    created = create_recipe()
    response = client.delete(f"/recipes/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/recipes/{created['id']}")
    assert get_response.status_code == 404

    list_response = client.get("/recipes", params={"limit": 100, "offset": 0})
    ids = [item["id"] for item in list_response.json()["items"]]
    assert created["id"] not in ids


def test_delete_twice_is_404_not_soft_delete() -> None:
    # R24: deleting an id that was already deleted -> 404, no tombstone.
    created = create_recipe()
    first = client.delete(f"/recipes/{created['id']}")
    assert first.status_code == 204
    second = client.delete(f"/recipes/{created['id']}")
    assert second.status_code == 404


# ---------------------------------------------------------------------------
# Boundaries
# ---------------------------------------------------------------------------


def test_no_ui_or_static_page_at_root() -> None:
    # R30: no UI, HTML page, or static file serving is added.
    response = client.get("/")
    assert response.status_code == 404


def test_no_endpoints_beyond_the_five() -> None:
    # R32: no bulk operations, search/filter, categories, tags, or ratings.
    # A path/method combination that isn't one of the five either matches no
    # route (404) or matches a path template on a different method (405) --
    # SPEC.md doesn't mandate which, only that the endpoint doesn't exist.
    assert client.post("/recipes/search").status_code in (404, 405)
    assert client.get("/recipes/categories").status_code == 404
    assert client.delete("/recipes").status_code in (404, 405)
