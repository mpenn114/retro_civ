from .base import BaseTerrain
from src.config.base_yield.base import BaseYield
from src.art import TERRAIN_IMAGES


MountainTerrain = BaseTerrain(
    name="Mountain",
    movement_cost=4,
    defensive_multiplier=2.0,
    is_land=True,
    base_yield=BaseYield(production=3, gold=1),
    base_image=TERRAIN_IMAGES.mountain,
)

__all__ = [MountainTerrain]
