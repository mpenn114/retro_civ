from pydantic import BaseModel, model_validator
from .rural import BaseRural
from .city import BaseCity
from .coordinates import BaseCoordinates


class BaseTile(BaseModel):
    """
    Define the base class for a tile, which contains all the
        information about the contents of a tile on the map
    """

    # Determine whether or not the tile is a city
    is_city: bool = False

    # Add the city details if relevant
    city_details: BaseCity | None

    # Add the rural details (always relevant)
    rural_details: BaseRural

    # Determine the coordinates on the map
    coordinates: BaseCoordinates

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
