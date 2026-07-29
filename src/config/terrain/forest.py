from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


ForestTerrain = BaseTerrain(
    name="Forest",
    movement_cost=2,
    defensive_multiplier=1.25,
    is_land=True,
    base_yield=AdditiveYield(food=1, production=1),
    base_image=TERRAIN_IMAGES.forest,
)

ForestRiverTerrain = BaseTerrain(
    name="Forest (River)",
    movement_cost=1,
    defensive_multiplier=1.5,
    is_land=True,
    base_yield=AdditiveYield(food=2, production=2, gold=1),
    base_image=TERRAIN_IMAGES.forest_river,
)

__all__ = [ForestTerrain, ForestRiverTerrain]
