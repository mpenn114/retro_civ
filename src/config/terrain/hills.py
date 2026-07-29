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
)

__all__ = [HillsTerrain]
