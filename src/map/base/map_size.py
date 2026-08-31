from pydantic import BaseModel, Field


class BaseMapSize(BaseModel):
    """
    Define the configuration around the size and orientation of the map
    """

    # Determine the size
    size_x: int = Field(ge=0, le=1_000)
    size_y: int = Field(ge=0, le=1_000)

    # Determine the wrapping
    wrap_x: bool = True
    wrap_y: bool = False

    @property
    def size(self) -> tuple[int, int]:
        """Generate a tuple of the map size"""
        return (self.size_x, self.size_y)
