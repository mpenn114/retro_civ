from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


HillsTerrain = BaseTerrain(
    name="Hills",
    movement_cost=2,
    defensive_multiplier=1.5,
    is_land=True,
    base_yield=AdditiveYield(food=1, production=2, gold=1),
    base_image=TERRAIN_IMAGES.hills,
    blocks=True,
    geography=None,
)

# Spring a river in the hills, which is where rivers on the map start before running downhill
HillsRiverSourceTerrain = BaseTerrain(
    name="Hills (River Source)",
    movement_cost=1,
    defensive_multiplier=1.75,
    is_land=True,
    base_yield=AdditiveYield(food=2, production=2, gold=2),
    base_image=TERRAIN_IMAGES.hills_river_source,
    blocks=True,
    geography=None,
)

__all__ = [HillsTerrain, HillsRiverSourceTerrain]
