from pydantic import BaseModel, model_validator
from .rural import BaseRural
from .city import BaseCity
from src.config.units import BaseUnit


class BaseTile(BaseModel):
    """
    Define the base class for a tile, which contains all the
        information about the contents of a tile on the map
    """

    # Determine whether or not the tile is a city
    is_city: bool = False

    # Add the city details if relevant
    city_details: BaseCity | None = None

    # Add the unit details if relevant
    unit_details: BaseUnit | None = None

    # Add the rural details (always relevant)
    rural_details: BaseRural

    @model_validator(mode="after")
    def validate_worked_tiles(self) -> "BaseTile":
        """
        Ensure that city details are supplied if required

        Args:
            None.

        Returns:
            The validated tile instance.

        Raises:
            ValueError: If city details needed but not available
        """
        if self.is_city and self.city_details is None:
            raise ValueError("City details must be provided for cities")

        return self

    def describe(self):
        """
        Desribe the tile

        Returns:
            str: A description of the tile
        """
        return f"""
            Tile:
                {self.city_details.describe() if self.city_details is not None else "Rural"}
                {self.unit_details.describe() if self.unit_details is not None else "Unoccupied"}
                {self.rural_details.describe()}

        """
