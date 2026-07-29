from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


PlainsTerrain = BaseTerrain(
    name="Plains",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=AdditiveYield(food=1, production=1),
    base_image=TERRAIN_IMAGES.plains,
)

PlainsRiverTerrain = BaseTerrain(
    name="Plains (River)",
    movement_cost=0.5,
    defensive_multiplier=1.25,
    is_land=True,
    base_yield=AdditiveYield(food=2, production=2, gold=1),
    base_image=TERRAIN_IMAGES.plains_river,
)

__all__ = [PlainsTerrain, PlainsRiverTerrain]
