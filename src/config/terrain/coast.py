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
    geography=None,
)

CoastCornerTerrain = CoastTerrain.with_image(TERRAIN_IMAGES.coast_corner)

CoastRiverTerrain = BaseTerrain(
    name="Coast (River Mouth)",
    movement_cost=0.5,
    defensive_multiplier=1.25,
    is_land=True,
    base_yield=AdditiveYield(food=3, production=1, gold=2),
    base_image=TERRAIN_IMAGES.coast_river,
)

__all__ = [CoastTerrain, CoastCornerTerrain, CoastRiverTerrain]
