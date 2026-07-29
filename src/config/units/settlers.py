from .base import BaseUnit, BaseCombatStrength, BaseUnitCapabilities
from src.art import UNIT_IMAGES

Settler = BaseUnit(
    name="Settler",
    image=UNIT_IMAGES.settler,
    max_movement=2,
    sight_range=2,
    combat_strength=BaseCombatStrength(defence_strength=1),
    capabilities=BaseUnitCapabilities(can_settle=True, can_be_captured=True),
)

__all__ = [Settler]
