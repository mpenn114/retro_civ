from .base import BaseTerrain, TerrainGeography
from src.config.base_yield.base import AdditiveYield
from src.art import TERRAIN_IMAGES


TundraTerrain = BaseTerrain(
    name="Tundra",
    movement_cost=1,
    defensive_multiplier=1.0,
    is_land=True,
    base_yield=AdditiveYield(food=1),
    base_image=TERRAIN_IMAGES.tundra,
    geography=TerrainGeography(temperature=5, rainfall=0.2)
)

__all__ = [TundraTerrain]
