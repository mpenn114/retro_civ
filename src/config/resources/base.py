from pydantic import BaseModel
from src.config.base_yield.base import AdditiveYield
from src.config.requirements.base import BaseRequirement


class BaseResource(BaseModel):
    """
    Define the base class for resources
    """

    # Define the human-readable name of the resource
    name: str

    # Define the additional yield that this resource defines
    additional_yield: AdditiveYield

    # Define the requirement for this resource to be visible
    requirement: BaseRequirement
