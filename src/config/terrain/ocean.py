from .base import BaseTerrain
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


DeepOceanTerrain = BaseTerrain(
    name="Deep Ocean",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=AdditiveYield(food=2),
    base_image=TERRAIN_IMAGES.deep_ocean,
    geography=None,
)

ShallowOceanTerrain = BaseTerrain(
    name="Shallow Ocean",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=AdditiveYield(food=2),
    base_image=TERRAIN_IMAGES.shallow_ocean,
    geography=None,
)

__all__ = [DeepOceanTerrain, ShallowOceanTerrain]
