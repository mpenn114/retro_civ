from .base import BaseTerrain
from src.config.base_yield.base import BaseYield
from src.art import TERRAIN_IMAGES


GrassTerrain = BaseTerrain(
    name="Grassland",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=BaseYield(food=2),
    base_image=TERRAIN_IMAGES.grass,
)

GrassRiverTerrain = BaseTerrain(
    name="Grassland (River)",
    movement_cost=0.5,
    defensive_multiplier=1.25,
    is_land=True,
    base_yield=BaseYield(food=3, production=1, gold=1),
    base_image=TERRAIN_IMAGES.grass_river,
)

__all__ = [GrassTerrain, GrassRiverTerrain]
