from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


MountainTerrain = BaseTerrain(
    name="Mountain",
    movement_cost=4,
    defensive_multiplier=2.0,
    is_land=True,
    base_yield=AdditiveYield(production=3, gold=1),
    base_image=TERRAIN_IMAGES.mountain,
    blocks=True,
    geography=None
)

__all__ = [MountainTerrain]
