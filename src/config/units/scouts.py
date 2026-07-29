from .base import BaseUnit, BaseCombatStrength, BaseUnitCapabilities
from src.art import UNIT_IMAGES

Scout = BaseUnit(
    name="Scout",
    image=UNIT_IMAGES.scout,
    max_movement=3,
    sight_range=2,
    combat_strength=BaseCombatStrength(defence_strength=1),
    capabilities=BaseUnitCapabilities(),
)

__all__ = [Scout]
