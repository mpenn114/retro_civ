from pydantic import BaseModel, Field, model_validator, ConfigDict
from src.config.requirements.base import BaseRequirement
from src.config.civs import BaseCiv, Barbarians
import pygame


class BaseCombatStrength(BaseModel):
    """
    Define the combat strength of a unit
    """

    # Define the strength of the unit
    ranged_strength: int = Field(ge=0, le=100, default=0)
    melee_strength: int = Field(ge=0, le=100, default=0)
    defence_strength: int = Field(ge=0, le=100)

    # Define the range of the unit (0 if not ranged)
    range: int = Field(ge=0, le=4, default=0)


class BaseUnitCapabilities(BaseModel):
    """
    Define the capabailities of a unit
    """

    # Determine if a unit can settle a city
    can_settle: bool = False

    # Determine if a unit can initiate combat
    can_initiate_combat: bool = False

    # Determine if a unit can fortify
    can_fortify: bool = False

    # Determine if a unit can be captured
    can_be_captured: bool = True


class BaseUnitStatus(BaseModel):
    """
    Define a base class for the status of the unit
    """

    # Determine the civilization that the unit belongs to
    civilization: BaseCiv = Barbarians

    # Define the health of the unit
    health: int = Field(ge=0, le=100, default=100)

    # Define whether the unit is currently fortified
    fortified: bool = False

    # Define whether the unit is currently asleep
    asleep: bool = False

    # Define the number of movement points remaining
    remaining_movement: int = Field(ge=0, le=10, default=0)

    @model_validator(mode="after")
    def validate_status(self) -> "BaseUnitStatus":
        """
        Ensure the unit is not both fortified and asleep

        Args:
            None.

        Returns:
            The validated unit instance.

        Raises:
            ValueError: If the unit is both fortified and asleep
        """
        if self.fortified and self.asleep:
            raise ValueError("Unit cannot be both fortified and asleep")

        return self


class BaseUnit(BaseModel):
    """
    Define a base class for units
    """

    # Define the human-readable name
    name: str

    # Define the unit status
    unit_status: BaseUnitStatus = BaseUnitStatus()

    # Define the image for the unit
    image: pygame.Surface

    # Define the number of tiles if can move
    max_movement: int = Field(ge=1, le=10)

    # Define the sight range
    sight_range: int = Field(ge=1, le=4)

    # Define the combat strength
    combat_strength: BaseCombatStrength

    # Define the unit capabilities
    capabilities: BaseUnitCapabilities

    # Define the requirement for the unit
    requirement: BaseRequirement = BaseRequirement()

    # Define the obsolecence requirement for the unit
    obsolecence_requirement: BaseRequirement | None = None

    # Accept the pygame surface holding the sprite, which pydantic cannot validate itself
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def describe(self) -> str:
        """
        Desribe the unit

        Returns:
            str: The unit description
        """
        return f"""
            Unit:
                Name: {self.name}
                Civilization: {self.unit_status.civilization}
                Health: {self.unit_status.health}
        """
