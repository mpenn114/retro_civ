from pydantic import BaseModel, field_validator
import re


class BaseCiv(BaseModel):
    """
    Define a base class for the civilization
    """

    # Define the human-readable name
    name: str

    # Define the colour of the civilization
    colour: str

    # Determine whether the civilization is AI or human controlled
    human_controlled: bool

    @field_validator("colour")
    @classmethod
    def validate_hex_colour(cls, value: str) -> str:
        """
        Validate that a colour is a hex colour.

        Args:
            value: Colour string to validate.

        Returns:
            Validated hex colour string.
        """
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError("Colour must be a 6-digit hex colour (e.g. #FF0000)")
        return value.upper()
