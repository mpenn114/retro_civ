import os
from pathlib import Path

import pygame
from pydantic import BaseModel

RGB = tuple[int, int, int]

UNIT_PIXELS = 24
UNIT_SCALE = 3


class UnitSpec(BaseModel):
    """
    Describe a single unit sprite to be generated
    """

    name: str
    draw_func: str


class UnitSpriteGenerator:
    """
    Generate simple pixel-art unit sprites as PNG assets
    """

    def __init__(self, output_directory: Path) -> None:
        """
        Prepare the generator and its headless drawing surface

        Args:
            output_directory (Path): The directory the PNG sprites are written to
        """
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()

        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)

        self._unit_renderers = {
            "settler": self._draw_settler,
            "warrior": self._draw_warrior,
            "scout": self._draw_scout,
        }

    def generate_all(self) -> list[Path]:
        """
        Generate every unit sprite

        Returns:
            list[Path]: The paths of every PNG written
        """
        written_paths: list[Path] = []

        for spec in self._build_unit_specs():
            written_paths.append(self._render_and_save(spec))

        return written_paths

    def _build_unit_specs(self) -> list[UnitSpec]:
        """
        Build the specification for every unit sprite in the game

        Returns:
            list[UnitSpec]: The specification for each unit type
        """
        return [
            UnitSpec(name="settler", draw_func="settler"),
            UnitSpec(name="warrior", draw_func="warrior"),
            UnitSpec(name="scout", draw_func="scout"),
        ]

    def _render_and_save(self, spec: UnitSpec) -> Path:
        """
        Render a single unit sprite and write it to disk as a PNG

        Args:
            spec (UnitSpec): The unit sprite to render

        Returns:
            Path: The path of the PNG written
        """
        surface = pygame.Surface((UNIT_PIXELS, UNIT_PIXELS), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        self._unit_renderers[spec.draw_func](surface)

        scaled_surface = pygame.transform.scale(
            surface, (UNIT_PIXELS * UNIT_SCALE, UNIT_PIXELS * UNIT_SCALE)
        )

        output_path = self.output_directory / f"{spec.name}.png"
        pygame.image.save(scaled_surface, str(output_path))

        return output_path

    def _draw_settler(self, surface: pygame.Surface) -> None:
        """
        Draw a settler unit (builder with a hammer)

        Args:
            surface (pygame.Surface): The sprite surface being drawn
        """
        skin_colour: RGB = (212, 188, 140)
        shirt_colour: RGB = (140, 100, 60)
        pants_colour: RGB = (80, 60, 40)
        hair_colour: RGB = (100, 80, 50)
        hammer_head: RGB = (200, 140, 80)
        hammer_handle: RGB = (120, 90, 60)

        pygame.draw.circle(surface, hair_colour, (12, 4), 2)
        pygame.draw.circle(surface, skin_colour, (12, 6), 3)
        pygame.draw.rect(surface, shirt_colour, pygame.Rect(10, 9, 4, 4))
        pygame.draw.rect(surface, skin_colour, pygame.Rect(10, 9, 4, 1))

        pygame.draw.line(surface, skin_colour, (11, 11), (11, 15), 1)
        pygame.draw.line(surface, pants_colour, (11, 15), (11, 21), 1)

        pygame.draw.line(surface, skin_colour, (13, 11), (13, 15), 1)
        pygame.draw.line(surface, pants_colour, (13, 15), (13, 21), 1)

        pygame.draw.rect(surface, hammer_handle, pygame.Rect(15, 6, 1, 6))
        pygame.draw.rect(surface, hammer_head, pygame.Rect(14, 5, 3, 2))

    def _draw_warrior(self, surface: pygame.Surface) -> None:
        """
        Draw a warrior unit (armed with sword and shield)

        Args:
            surface (pygame.Surface): The sprite surface being drawn
        """
        skin_colour: RGB = (212, 188, 140)
        armour_colour: RGB = (180, 180, 180)
        tunic_colour: RGB = (120, 80, 60)
        hair_colour: RGB = (100, 80, 50)
        metal_shine: RGB = (220, 220, 220)
        sword_colour: RGB = (200, 100, 80)

        pygame.draw.circle(surface, hair_colour, (12, 4), 2)
        pygame.draw.circle(surface, skin_colour, (12, 6), 3)
        pygame.draw.rect(surface, armour_colour, pygame.Rect(10, 9, 4, 5))
        pygame.draw.circle(surface, metal_shine, (12, 10), 1)

        pygame.draw.line(surface, skin_colour, (11, 12), (11, 16), 1)
        pygame.draw.line(surface, tunic_colour, (11, 16), (11, 22), 1)

        pygame.draw.line(surface, skin_colour, (13, 12), (13, 16), 1)
        pygame.draw.line(surface, tunic_colour, (13, 16), (13, 22), 1)

        pygame.draw.rect(surface, armour_colour, pygame.Rect(7, 10, 2, 4))
        pygame.draw.circle(surface, metal_shine, (8, 11), 1)

        pygame.draw.line(surface, sword_colour, (16, 9), (19, 3), 2)
        pygame.draw.line(surface, metal_shine, (17, 8), (20, 2), 1)

    def _draw_scout(self, surface: pygame.Surface) -> None:
        """
        Draw a scout unit (light armour, holding spear)

        Args:
            surface (pygame.Surface): The sprite surface being drawn
        """
        skin_colour: RGB = (212, 188, 140)
        tunic_colour: RGB = (100, 140, 80)
        hair_colour: RGB = (100, 80, 50)
        leather_colour: RGB = (140, 110, 80)
        spear_metal: RGB = (200, 200, 200)

        pygame.draw.circle(surface, hair_colour, (12, 4), 2)
        pygame.draw.circle(surface, skin_colour, (12, 6), 3)
        pygame.draw.rect(surface, tunic_colour, pygame.Rect(10, 9, 4, 5))
        pygame.draw.rect(surface, leather_colour, pygame.Rect(9, 9, 1, 4))
        pygame.draw.rect(surface, leather_colour, pygame.Rect(15, 9, 1, 4))

        pygame.draw.line(surface, skin_colour, (11, 12), (11, 16), 1)
        pygame.draw.line(surface, tunic_colour, (11, 16), (11, 22), 1)

        pygame.draw.line(surface, skin_colour, (13, 12), (13, 16), 1)
        pygame.draw.line(surface, tunic_colour, (13, 16), (13, 22), 1)

        pygame.draw.line(surface, spear_metal, (17, 3), (17, 15), 1)
        pygame.draw.polygon(surface, spear_metal, [(16, 2), (18, 2), (17, 4)], 0)


def main() -> None:
    """
    Generate every unit sprite into the packaged assets directory
    """
    output_directory = Path(__file__).parent / "assets" / "units"
    generator = UnitSpriteGenerator(output_directory=output_directory)
    written_paths = generator.generate_all()

    for path in written_paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
