from pydantic import BaseModel, Field


class BaseTech(BaseModel):
    """
    Define the base class for technologies
    """

    # Define the human-readable name of the technology
    name: str

    # Define the description for display in the app
    description: str

    # Define the cost in science for this technology
    cost: int = Field(ge=0, le=1_000_000)

    # Define the dependencies for this technology
    dependencies: frozenset["BaseTech"] = frozenset()
