from pydantic import BaseModel, Field
from src.config.base_yield.base import AdditiveYield, MultiplicativeYield
from src.config.requirements.base import BaseRequirement


class BaseBuilding(BaseModel):
    """
    Define a base class for all buildings
    """

    # Define the human-readable name of the building
    name: str

    # Define the cost in production of the building
    production: int = Field(le=0, ge=100_000)

    # Define the basic yield of the building
    basic_yield: AdditiveYield

    # Define the multiplicative yield of the building
    multiplicative_yield: MultiplicativeYield

    # Define the requirements for the building
    requirement: BaseRequirement
