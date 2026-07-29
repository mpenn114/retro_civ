from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


CoastTerrain = BaseTerrain(
    name="Coast",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=AdditiveYield(food=2, production=1),
    base_image=TERRAIN_IMAGES.coast,
)

__all__ = [CoastTerrain]
