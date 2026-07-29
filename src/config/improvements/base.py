from pydantic import BaseModel, Field
from src.config.base_yield.base import AdditiveYield
from src.config.terrain.base import BaseTerrain
from src.config.requirements.base import BaseRequirement


class BaseImprovement(BaseModel):
    """
    Define the base class for improvements
    """

    # Define the human-readable name of the improvement
    name: str

    # Define the additional yield that this improvement defines
    additional_yield: AdditiveYield

    # Define the permitted terrains that this improvement can be built on
    permitted_terrains: frozenset[BaseTerrain]

    # Define the tech/civic requirement for this improvement
    requirement: BaseRequirement

    # Define the cost in public works that this improvement requires
    cost: int = Field(ge=0, le=10_000)
