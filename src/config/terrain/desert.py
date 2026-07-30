from .base import BaseTerrain
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
)

__all__ = [DesertTerrain]
