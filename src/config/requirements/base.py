from pydantic import BaseModel
from src.config.civics.base import BaseCivic
from src.config.techs.base import BaseTech


class BaseRequirement(BaseModel):
    """
    Define the base class for technology and civic requirements
    """

    # Define the technology that is required, if any
    tech_requirement: BaseTech | None = None

    # Define the civic that is required, if any
    civic_requirement: BaseCivic | None = None
