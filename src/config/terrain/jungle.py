from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


JungleTerrain = BaseTerrain(
    name="Jungle",
    movement_cost=3,
    defensive_multiplier=1.25,
    is_land=True,
    base_yield=AdditiveYield(food=2, production=1, gold=1),
    base_image=TERRAIN_IMAGES.jungle,
    blocks=True,
)

JungleRiverTerrain = BaseTerrain(
    name="Jungle (River)",
    movement_cost=1.5,
    defensive_multiplier=1.5,
    is_land=True,
    base_yield=AdditiveYield(food=3, production=2, gold=2),
    base_image=TERRAIN_IMAGES.jungle_river,
    blocks=True,
)

__all__ = [JungleTerrain, JungleRiverTerrain]
