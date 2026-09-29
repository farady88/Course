from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from src.models import IngredientStr, InstructionStr, Recipe, RecipeList
from src.storage import store

app = FastAPI()


class RecipeCreate(BaseModel):
    """POST /recipes request body (R12, R13, R16)."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    ingredients: list[IngredientStr] = Field(min_length=1)
    instructions: list[InstructionStr] = Field(min_length=1)
    prep_minutes: int = Field(ge=0, le=1440)
    servings: int = Field(ge=1, le=100)


class RecipePatch(BaseModel):
    """PATCH /recipes/{id} request body (R17, R19, R20)."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    ingredients: list[IngredientStr] | None = Field(default=None, min_length=1)
    instructions: list[InstructionStr] | None = Field(default=None, min_length=1)
    prep_minutes: int | None = Field(default=None, ge=0, le=1440)
    servings: int | None = Field(default=None, ge=1, le=100)


MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 20
MIN_OFFSET = 0
DEFAULT_OFFSET = 0


def _parse_pagination_param(raw: str | None, *, default: int, minimum: int, maximum: int | None) -> int:
    """Parse a limit/offset query param, raising 400 per R8 on any bad value."""
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="must be an integer") from None
    if value < minimum or (maximum is not None and value > maximum):
        raise HTTPException(status_code=400, detail="out of allowed range")
    return value


@app.get("/recipes", response_model=RecipeList)
def list_recipes(
    limit: str | None = Query(default=None),
    offset: str | None = Query(default=None),
) -> RecipeList:
    limit_value = _parse_pagination_param(limit, default=DEFAULT_LIMIT, minimum=MIN_LIMIT, maximum=MAX_LIMIT)
    offset_value = _parse_pagination_param(offset, default=DEFAULT_OFFSET, minimum=MIN_OFFSET, maximum=None)

    recipes = store.list()
    page = recipes[offset_value : offset_value + limit_value]
    return RecipeList(items=page, limit=limit_value, offset=offset_value, total=len(recipes))


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: str) -> Recipe:
    recipe = store.get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404)
    return recipe


@app.post("/recipes", response_model=Recipe, status_code=201)
def create_recipe(payload: RecipeCreate) -> Recipe:
    return store.create(
        title=payload.title,
        ingredients=payload.ingredients,
        instructions=payload.instructions,
        prep_minutes=payload.prep_minutes,
        servings=payload.servings,
    )


@app.patch("/recipes/{recipe_id}", response_model=Recipe)
def patch_recipe(recipe_id: str, payload: RecipePatch) -> Recipe:
    recipe = store.get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404)

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        if value is None:
            raise HTTPException(status_code=422, detail=f"{field_name} must not be null")
    if not updates:
        return recipe

    updated = store.update(recipe_id, **updates)
    assert updated is not None
    return updated
