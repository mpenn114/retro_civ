from .base import BaseTerrain
from src.config.base_yield.base import BaseYield
from src.art import TERRAIN_IMAGES


HillsTerrain = BaseTerrain(
    name="Hills",
    movement_cost=2,
    defensive_multiplier=1.5,
    is_land=True,
    base_yield=BaseYield(food=1, production=2, gold=1),
    base_image=TERRAIN_IMAGES.hills,
)

__all__ = [HillsTerrain]
