from .base import BaseTerrain
from src.config.base_yield.base import BaseYield
from src.art import TERRAIN_IMAGES


TundraTerrain = BaseTerrain(
    name="Tundra",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=BaseYield(food=1),
    base_image=TERRAIN_IMAGES.tundra,
)

__all__ = [TundraTerrain]
