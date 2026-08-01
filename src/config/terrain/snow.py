from .base import BaseTerrain, TerrainGeography
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


SnowTerrain = BaseTerrain(
    name="Snow",
    movement_cost=2,
    defensive_multiplier=1.5,
    is_land=True,
    base_yield=AdditiveYield(),
    base_image=TERRAIN_IMAGES.snow,
    geography=TerrainGeography(temperature=0, rainfall=0.2)
)

__all__ = [SnowTerrain]
