from typing import Annotated

from pydantic import BaseModel, Field

IngredientStr = Annotated[str, Field(min_length=1, max_length=200)]
InstructionStr = Annotated[str, Field(min_length=1, max_length=500)]


class Recipe(BaseModel):
    """The Recipe resource (SPEC.md R1)."""

    id: str
    title: str = Field(min_length=1, max_length=120)
    ingredients: list[IngredientStr] = Field(min_length=1)
    instructions: list[InstructionStr] = Field(min_length=1)
    prep_minutes: int = Field(ge=0, le=1440)
    servings: int = Field(ge=1, le=100)


class RecipeList(BaseModel):
    """A page of recipes (GET /recipes response, SPEC.md R6/R9)."""

    items: list[Recipe]
    limit: int
    offset: int
    total: int
