from pydantic import BaseModel, Field


class BaseCivic(BaseModel):
    """
    Define the base class for civics
    """

    # Define the human-readable name of the civic
    name: str

    # Define the description for display in the app
    description: str

    # Define the cost in culture for this civic
    cost: int = Field(ge=0, le=1_000_000)

    # Define the dependencies for this civic
    dependencies: frozenset["BaseCivic"] = frozenset()
