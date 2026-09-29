import uuid

from src.models import Recipe


class RecipeStore:
    """In-memory recipe store, preserving insertion order (R3, R26, R31)."""

    def __init__(self) -> None:
        self._recipes: dict[str, Recipe] = {}

    def create(
        self,
        *,
        title: str,
        ingredients: list[str],
        instructions: list[str],
        prep_minutes: int,
        servings: int,
    ) -> Recipe:
        recipe_id = uuid.uuid4().hex
        recipe = Recipe(
            id=recipe_id,
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            prep_minutes=prep_minutes,
            servings=servings,
        )
        self._recipes[recipe_id] = recipe
        return recipe

    def get(self, recipe_id: str) -> Recipe | None:
        return self._recipes.get(recipe_id)

    def list(self) -> list[Recipe]:
        return list(self._recipes.values())

    def update(self, recipe_id: str, **fields: object) -> Recipe | None:
        existing = self._recipes.get(recipe_id)
        if existing is None:
            return None
        updated = existing.model_copy(update=fields)
        self._recipes[recipe_id] = updated
        return updated

    def delete(self, recipe_id: str) -> bool:
        return self._recipes.pop(recipe_id, None) is not None


store = RecipeStore()
