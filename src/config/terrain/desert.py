from .base import BaseTerrain, TerrainGeography
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


# Leave the desert yielding nothing at all, so it is only worth working once a resource or an
# improvement is placed on it
DesertTerrain = BaseTerrain(
    name="Desert",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=AdditiveYield(),
    base_image=TERRAIN_IMAGES.desert,
    geography=TerrainGeography(temperature=25, rainfall=0.0)
)

__all__ = [DesertTerrain]
