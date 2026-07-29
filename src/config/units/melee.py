from .base import BaseUnit, BaseCombatStrength, BaseUnitCapabilities
from src.art import UNIT_IMAGES

Warrior = BaseUnit(
    name="Warrior",
    image=UNIT_IMAGES.warrior,
    max_movement=2,
    sight_range=2,
    combat_strength=BaseCombatStrength(melee_strength=1, defence_strength=1),
    capabilities=BaseUnitCapabilities(can_fortify=True, can_initiate_combat=True),
)

__all__ = [Warrior]
