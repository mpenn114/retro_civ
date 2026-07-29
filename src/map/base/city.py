from pydantic import BaseModel, Field, model_validator
from .rural import BaseRural
from src.config.buildings.base import BaseBuilding


class BaseCity(BaseModel):
    """
    Define a base class to contain all the information about a city
    """

    # Human-readable city name
    name: str

    # Total population
    population: int = Field(ge=0)

    # Total stored food
    food_storage: int = Field(ge=0)

    # Worked tiles
    worked_tiles: set[BaseRural] = set()

    # Buildings
    buildings: set[BaseBuilding] = set()

    @model_validator(mode="after")
    def validate_worked_tiles(self) -> "BaseCity":
        """
        Ensure the number of worked tiles does not exceed population.

        Args:
            None.

        Returns:
            The validated city instance.

        Raises:
            ValueError: If worked tiles exceed population.
        """
        if len(self.worked_tiles) > self.population:
            raise ValueError("Number of worked tiles cannot exceed population")

        return self
