import math
import os
import random
from collections.abc import Callable
from pathlib import Path

import pygame
from pydantic import BaseModel

# Give the type alias used for all colours in this module
RGB = tuple[int, int, int]

# Give the resolution the tiles are drawn at before upscaling
TILE_PIXELS = 32

# Give the integer factor the drawn tile is upscaled by to keep hard pixel edges
TILE_SCALE = 4

# Give the half-width of a river channel in drawing pixels
RIVER_HALF_WIDTH = 2

# Give the amplitude of the river meander in drawing pixels
RIVER_MEANDER = 5

# Give the row and column the shoreline sits at, so coast tiles join up along their edges
SHORE_LINE = 20

# Give the radius the shoreline is rounded by where it turns a corner
SHORE_CORNER_RADIUS = 5


class TilePalette(BaseModel):
    """
    Store the colours used to draw a single terrain tile
    """

    # Give the dominant colour of the tile
    base: RGB

    # Give the darker colour used for shadows and texture
    shade: RGB

    # Give the lighter colour used for highlights and texture
    highlight: RGB

    # Give the accent colour used for the terrain feature drawn on top
    detail: RGB


class TileSpec(BaseModel):
    """
    Describe a single terrain tile to be generated
    """

    # Give the file-safe name of the terrain
    name: str

    # Give the colours the tile is drawn with
    palette: TilePalette

    # Give the name of the feature drawing routine to apply over the base
    feature: str

    # Determine whether a river variant of the tile should also be generated
    has_river_variant: bool = False


class TerrainTileGenerator:
    """
    Generate simple pixel-art terrain tiles as PNG assets
    """

    # Give the colours used for river water on land tiles
    RIVER_CORE: RGB = (111, 189, 232)
    RIVER_EDGE: RGB = (74, 158, 212)

    def __init__(self, output_directory: Path) -> None:
        """
        Prepare the generator and its headless drawing surface

        Args:
            output_directory (Path): The directory the PNG tiles are written to
        """
        # Force a headless SDL driver so tiles can be generated without a display
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()

        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Map each feature name onto the method that draws it
        self._feature_renderers = {
            "flat": self._draw_flat,
            "mountain": self._draw_mountain,
            "forest": self._draw_forest,
            "jungle": self._draw_jungle,
            "hills": self._draw_hills,
            "speckle": self._draw_speckle,
            "shore": self._draw_shore,
            "shore_corner": self._draw_shore_corner,
            "waves": self._draw_waves,
        }

    def generate_all(self) -> list[Path]:
        """
        Generate every terrain tile, including river variants where relevant

        Returns:
            list[Path]: The paths of every PNG written
        """
        written_paths: list[Path] = []

        # Draw each terrain, then its river variant if it has one
        for spec in self._build_tile_specs():
            written_paths.append(self._render_and_save(spec, with_river=False))
            if spec.has_river_variant:
                written_paths.append(self._render_and_save(spec, with_river=True))

        return written_paths

    def _build_tile_specs(self) -> list[TileSpec]:
        """
        Build the specification for every terrain tile in the game

        Returns:
            list[TileSpec]: The specification for each terrain type
        """
        return [
            TileSpec(
                name="mountain",
                feature="mountain",
                palette=TilePalette(
                    base=(107, 107, 99),
                    shade=(72, 72, 66),
                    highlight=(150, 150, 140),
                    detail=(232, 238, 242),
                ),
            ),
            TileSpec(
                name="plains",
                feature="flat",
                has_river_variant=True,
                palette=TilePalette(
                    base=(201, 185, 106),
                    shade=(172, 156, 84),
                    highlight=(222, 208, 137),
                    detail=(138, 154, 74),
                ),
            ),
            TileSpec(
                name="grass",
                feature="flat",
                has_river_variant=True,
                palette=TilePalette(
                    base=(106, 168, 79),
                    shade=(92, 150, 70),
                    highlight=(134, 191, 104),
                    detail=(88, 145, 66),
                ),
            ),
            TileSpec(
                name="forest",
                feature="forest",
                has_river_variant=True,
                palette=TilePalette(
                    base=(88, 140, 68),
                    shade=(70, 114, 55),
                    highlight=(112, 165, 88),
                    detail=(43, 90, 52),
                ),
            ),
            TileSpec(
                name="jungle",
                feature="jungle",
                has_river_variant=True,
                palette=TilePalette(
                    base=(63, 122, 58),
                    shade=(44, 94, 42),
                    highlight=(96, 158, 78),
                    detail=(29, 71, 34),
                ),
            ),
            TileSpec(
                name="hills",
                feature="hills",
                palette=TilePalette(
                    base=(126, 160, 84),
                    shade=(86, 116, 55),
                    highlight=(176, 205, 126),
                    detail=(96, 128, 62),
                ),
            ),
            TileSpec(
                name="tundra",
                feature="speckle",
                palette=TilePalette(
                    base=(168, 165, 131),
                    shade=(140, 137, 106),
                    highlight=(196, 193, 164),
                    detail=(125, 138, 106),
                ),
            ),
            TileSpec(
                name="snow",
                feature="speckle",
                palette=TilePalette(
                    base=(238, 243, 247),
                    shade=(206, 219, 230),
                    highlight=(255, 255, 255),
                    detail=(222, 234, 243),
                ),
            ),
            TileSpec(
                name="coast",
                feature="shore",
                palette=TilePalette(
                    base=(217, 201, 143),
                    shade=(192, 173, 116),
                    highlight=(235, 224, 180),
                    detail=(127, 201, 217),
                ),
            ),
            TileSpec(
                name="coast_corner",
                feature="shore_corner",
                palette=TilePalette(
                    base=(217, 201, 143),
                    shade=(192, 173, 116),
                    highlight=(235, 224, 180),
                    detail=(127, 201, 217),
                ),
            ),
            TileSpec(
                name="shallow_ocean",
                feature="waves",
                palette=TilePalette(
                    base=(61, 134, 181),
                    shade=(47, 112, 156),
                    highlight=(122, 186, 219),
                    detail=(90, 163, 204),
                ),
            ),
            TileSpec(
                name="deep_ocean",
                feature="waves",
                palette=TilePalette(
                    base=(27, 74, 122),
                    shade=(19, 55, 95),
                    highlight=(79, 138, 187),
                    detail=(45, 105, 160),
                ),
            ),
        ]

    def _render_and_save(self, spec: TileSpec, with_river: bool) -> Path:
        """
        Render a single tile and write it to disk as a PNG

        Args:
            spec (TileSpec): The terrain tile to render
            with_river (bool): Whether a river channel is drawn across the tile

        Returns:
            Path: The path of the PNG written
        """
        # Seed the randomness from the file name so the output is reproducible
        file_stem = f"{spec.name}_river" if with_river else spec.name
        rng = random.Random(file_stem)

        surface = pygame.Surface((TILE_PIXELS, TILE_PIXELS))

        # Lay down the textured ground, the terrain feature, then any river on top
        self._draw_base_texture(surface, spec.palette, rng)
        self._feature_renderers[spec.feature](surface, spec.palette, rng, with_river)
        if with_river:
            self._draw_river(surface)

        # Upscale with nearest-neighbour sampling to preserve the pixel-art look
        scaled_surface = pygame.transform.scale(
            surface, (TILE_PIXELS * TILE_SCALE, TILE_PIXELS * TILE_SCALE)
        )

        output_path = self.output_directory / f"{file_stem}.png"
        pygame.image.save(scaled_surface, str(output_path))

        return output_path

    def _draw_base_texture(
        self, surface: pygame.Surface, palette: TilePalette, rng: random.Random
    ) -> None:
        """
        Fill the tile with its base colour and scatter light and dark texture pixels

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
        """
        surface.fill(palette.base)

        # Scatter single-pixel noise so flat colours do not look sterile
        for _ in range(140):
            x = rng.randrange(TILE_PIXELS)
            y = rng.randrange(TILE_PIXELS)
            surface.set_at(
                (x, y), palette.shade if rng.random() < 0.5 else palette.highlight
            )

    @staticmethod
    def _darken(colour: RGB, factor: float) -> RGB:
        """
        Scale a colour towards black

        Args:
            colour (RGB): The colour to darken
            factor (float): The multiplier applied to each channel

        Returns:
            RGB: The darkened colour
        """
        return (
            int(colour[0] * factor),
            int(colour[1] * factor),
            int(colour[2] * factor),
        )

    @staticmethod
    def _blend(colour_from: RGB, colour_to: RGB, ratio: float) -> RGB:
        """
        Mix two colours together

        Args:
            colour_from (RGB): The colour returned at a ratio of zero
            colour_to (RGB): The colour returned at a ratio of one
            ratio (float): The position between the two colours

        Returns:
            RGB: The mixed colour
        """
        clamped_ratio = min(max(ratio, 0.0), 1.0)

        return (
            int(colour_from[0] + (colour_to[0] - colour_from[0]) * clamped_ratio),
            int(colour_from[1] + (colour_to[1] - colour_from[1]) * clamped_ratio),
            int(colour_from[2] + (colour_to[2] - colour_from[2]) * clamped_ratio),
        )

    def _river_centre(self, y: int) -> float:
        """
        Give the horizontal centre of the river channel at a given row

        Args:
            y (int): The row of the tile

        Returns:
            float: The horizontal centre of the river channel
        """
        return TILE_PIXELS / 2 + RIVER_MEANDER * math.sin(y / TILE_PIXELS * 2 * math.pi)

    def _is_clear_of_river(
        self, x: int, y: int, with_river: bool, margin: int = 3
    ) -> bool:
        """
        Determine whether a feature may be placed without overlapping the river

        Args:
            x (int): The horizontal position of the feature
            y (int): The vertical position of the feature
            with_river (bool): Whether the tile carries a river
            margin (int): The extra clearance required either side of the channel

        Returns:
            bool: True when the position is far enough from the river channel
        """
        if not with_river:
            return True

        return abs(x - self._river_centre(y)) > RIVER_HALF_WIDTH + margin

    def _draw_river(self, surface: pygame.Surface) -> None:
        """
        Draw a meandering river channel from the top to the bottom of the tile

        Args:
            surface (pygame.Surface): The tile being drawn
        """
        # Colour each row of the channel, using a lighter core and darker banks
        for y in range(TILE_PIXELS):
            centre = self._river_centre(y)
            for offset in range(-RIVER_HALF_WIDTH, RIVER_HALF_WIDTH + 1):
                x = int(round(centre)) + offset
                if 0 <= x < TILE_PIXELS:
                    is_core = abs(offset) < RIVER_HALF_WIDTH
                    surface.set_at(
                        (x, y), self.RIVER_CORE if is_core else self.RIVER_EDGE
                    )

    def _draw_flat(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
        tuft_count: int = 26,
    ) -> None:
        """
        Scatter small grass tufts across an otherwise flat tile

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
            tuft_count (int): The number of tufts to attempt to place
        """
        # Plant a tuft as a short vertical stroke with two splayed blades
        for _ in range(tuft_count):
            x = rng.randrange(2, TILE_PIXELS - 2)
            y = rng.randrange(3, TILE_PIXELS - 2)
            if not self._is_clear_of_river(x, y, with_river, margin=1):
                continue
            surface.set_at((x, y), palette.detail)
            surface.set_at((x, y - 1), palette.detail)
            surface.set_at((x - 1, y), palette.detail)
            surface.set_at((x + 1, y), palette.detail)

    def _draw_speckle(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Scatter small patches over the tile to suggest frost or sparse ground cover

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        # Dab small two-by-two patches of the accent colour across the tile
        for _ in range(22):
            x = rng.randrange(1, TILE_PIXELS - 2)
            y = rng.randrange(1, TILE_PIXELS - 2)
            if not self._is_clear_of_river(x, y, with_river, margin=1):
                continue
            pygame.draw.rect(surface, palette.detail, pygame.Rect(x, y, 2, 2))

    def _draw_mountain(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw a range of snow-capped peaks filling the tile

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        outline_colour = self._darken(palette.shade, 0.6)
        base_y = TILE_PIXELS - 1

        # Raise a broad central peak first, then two overlapping foreground peaks
        peaks = [(15, 3, 14), (5, 13, 10), (26, 11, 11)]
        for peak_x, peak_y, half_width in peaks:
            apex = (peak_x, peak_y)
            left = (peak_x - half_width, base_y)
            right = (peak_x + half_width, base_y)

            # Block in the rock, keeping the right face in shadow
            pygame.draw.polygon(surface, palette.base, [left, apex, right])
            pygame.draw.polygon(surface, palette.shade, [apex, right, (peak_x, base_y)])

            # Light the leading edge and outline the shaded edge to separate the peaks
            pygame.draw.line(surface, palette.highlight, apex, left)
            pygame.draw.line(surface, outline_colour, apex, right)

            # Cap the summit with snow
            pygame.draw.polygon(
                surface, palette.detail, self._snow_cap_points(apex, half_width, base_y)
            )

    @staticmethod
    def _snow_cap_points(
        apex: tuple[int, int], half_width: int, base_y: int
    ) -> list[tuple[int, int]]:
        """
        Build the outline of a snow cap covering the upper half of a peak

        Args:
            apex (tuple[int, int]): The summit of the peak
            half_width (int): The half-width of the peak at its base
            base_y (int): The row the peak stands on

        Returns:
            list[tuple[int, int]]: The polygon points of the snow cap
        """
        peak_x, peak_y = apex
        height = base_y - peak_y

        # Take the cap down half the peak, following the slope out to the snow line
        cap_depth = max(5, height // 2)
        cap_half = max(3, int(half_width * cap_depth / height))

        # Zigzag the snow line so the snow interlocks with the rock below it
        points = [apex]
        for step in range(0, cap_half * 2 + 1, 2):
            notch = 2 if (step // 2) % 2 == 1 else 0
            points.append((peak_x - cap_half + step, peak_y + cap_depth - notch))

        return points

    def _draw_hills(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw rounded mounds with shaded flanks to suggest rolling hills

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        # Raise broad, flattened mounds back to front so the nearer ones overlap those behind
        mounds = [(19, 9, 12, 7), (8, 19, 13, 8), (25, 24, 14, 9), (16, 31, 17, 10)]
        for centre_x, base_y, radius_x, radius_y in mounds:
            # Build each mound as a half-ellipse, wider than it is tall so it reads as a slope
            for height_offset in range(radius_y):
                y = base_y - height_offset
                if not 0 <= y < TILE_PIXELS:
                    continue

                slope_ratio = height_offset / radius_y
                half = int(radius_x * math.sqrt(max(1 - slope_ratio**2, 0.0)))

                # Ramp smoothly from a shaded foot up to a sunlit crest so the mound looks round
                row_colour = self._blend(palette.shade, palette.highlight, slope_ratio)
                pygame.draw.line(
                    surface, row_colour, (centre_x - half, y), (centre_x + half, y)
                )

                # Turn the right flank away from the light
                pygame.draw.line(
                    surface,
                    self._darken(row_colour, 0.85),
                    (centre_x + half // 2, y),
                    (centre_x + half, y),
                )

            # Settle the mound onto the ground with a contact shadow
            pygame.draw.line(
                surface,
                self._darken(palette.shade, 0.75),
                (centre_x - radius_x + 1, base_y),
                (centre_x + radius_x - 1, base_y),
            )

        # Dust the slopes with a light scatter of vegetation
        self._draw_flat(surface, palette, rng, with_river, tuft_count=10)

    def _draw_forest(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw a scatter of conifers across the tile

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        trunk_colour: RGB = (74, 53, 36)

        # Place trees back to front so nearer trees overlap those behind them
        positions = [
            (x, y)
            for y in range(11, TILE_PIXELS + 5, 8)
            for x in range(3, TILE_PIXELS + 3, 7)
        ]

        # Keep the lit edge close to the canopy colour so dense stands do not read as stripes
        lit_edge_colour = self._blend(palette.detail, palette.highlight, 0.45)
        for base_x, base_y in positions:
            jittered_x = base_x + rng.randint(-1, 1)
            jittered_y = base_y + rng.randint(-1, 1)
            if not self._is_clear_of_river(jittered_x, jittered_y, with_river):
                continue

            # Stand the trunk on the ground point, then stack two canopy tiers above it
            pygame.draw.rect(
                surface, trunk_colour, pygame.Rect(jittered_x, jittered_y, 1, 3)
            )
            for half_width, lift in [(4, 0), (3, 4)]:
                bottom_y = jittered_y - lift
                apex_y = bottom_y - 5
                pygame.draw.polygon(
                    surface,
                    palette.detail,
                    [
                        (jittered_x, apex_y),
                        (jittered_x - half_width, bottom_y),
                        (jittered_x + half_width, bottom_y),
                    ],
                )
                pygame.draw.line(
                    surface,
                    lit_edge_colour,
                    (jittered_x, apex_y),
                    (jittered_x - half_width, bottom_y),
                )

    def _draw_jungle(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw a dense canopy of overlapping broadleaf crowns

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        # Pack rounded crowns together so almost no ground shows through
        positions = [
            (x, y) for y in range(4, TILE_PIXELS, 6) for x in range(4, TILE_PIXELS, 6)
        ]
        for base_x, base_y in positions:
            jittered_x = base_x + rng.randint(-1, 1)
            jittered_y = base_y + rng.randint(-1, 1)
            if not self._is_clear_of_river(
                jittered_x, jittered_y, with_river, margin=2
            ):
                continue

            radius = rng.randint(3, 4)
            pygame.draw.circle(
                surface, palette.detail, (jittered_x, jittered_y), radius
            )
            pygame.draw.circle(
                surface,
                palette.highlight,
                (jittered_x - 1, jittered_y - 1),
                max(1, radius - 2),
            )

    @staticmethod
    def _is_straight_shore_water(x: int, y: int) -> bool:
        """
        Determine whether a pixel lies seaward of a shoreline running along the bottom edge

        Args:
            x (int): The horizontal position in the tile
            y (int): The vertical position in the tile

        Returns:
            bool: True when the pixel is water
        """
        # Complete one full wave across the tile so the shoreline meets both side edges at
        # SHORE_LINE and tiles laid side by side join up
        wobble = 2 * math.sin(x / (TILE_PIXELS - 1) * 2 * math.pi)

        return y >= SHORE_LINE + wobble

    @staticmethod
    def _is_corner_shore_water(x: int, y: int) -> bool:
        """
        Determine whether a pixel lies in the sea wrapping the bottom-right corner of a landmass

        Args:
            x (int): The horizontal position in the tile
            y (int): The vertical position in the tile

        Returns:
            bool: True when the pixel is water
        """
        # Wobble each shoreline so it meets SHORE_LINE exactly at the tile border, letting the
        # tile sit against a straight coast on its left edge and a quarter-turned one above
        horizontal_wobble = 1.5 * math.sin(x / SHORE_LINE * math.pi)
        vertical_wobble = 1.5 * math.sin(y / SHORE_LINE * math.pi)
        is_land = (
            y < SHORE_LINE + horizontal_wobble and x < SHORE_LINE + vertical_wobble
        )

        # Round the headland off so the two shorelines meet in a curve rather than a right angle
        corner_centre = SHORE_LINE - SHORE_CORNER_RADIUS
        if is_land and x > corner_centre and y > corner_centre:
            is_land = (
                math.dist((x, y), (corner_centre, corner_centre)) <= SHORE_CORNER_RADIUS
            )

        return not is_land

    def _draw_shore(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw a sandy shoreline washed by shallow water along the bottom edge

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        self._flood_shore(surface, palette, rng, self._is_straight_shore_water)

    def _draw_shore_corner(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw a sandy shoreline wrapping around the bottom-right corner of the tile

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        self._flood_shore(surface, palette, rng, self._is_corner_shore_water)

    def _flood_shore(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        water_mask: Callable[[int, int], bool],
    ) -> None:
        """
        Flood the seaward side of a shoreline with water and dress both sides of it

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            water_mask (Callable[[int, int], bool]): Reports whether a pixel is water
        """
        # Fill every seaward pixel with shallow water
        for y in range(TILE_PIXELS):
            for x in range(TILE_PIXELS):
                if water_mask(x, y):
                    surface.set_at((x, y), palette.detail)

        # Trace every water pixel that touches land so the shoreline reads as a crisp edge
        for y in range(TILE_PIXELS):
            for x in range(TILE_PIXELS):
                if not water_mask(x, y):
                    continue

                neighbours = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                touches_land = any(
                    not water_mask(nx, ny)
                    for nx, ny in neighbours
                    if 0 <= nx < TILE_PIXELS and 0 <= ny < TILE_PIXELS
                )
                if touches_land:
                    surface.set_at((x, y), palette.highlight)

        # Break up the water with a few foam dashes set back from the waterline
        for _ in range(8):
            x = rng.randrange(1, TILE_PIXELS - 2)
            y = rng.randrange(1, TILE_PIXELS - 1)
            if water_mask(x, y) and water_mask(x, y - 3):
                pygame.draw.line(surface, (225, 240, 248), (x, y), (x + 1, y))

        # Litter the dry sand with a scatter of pebbles
        for _ in range(20):
            x = rng.randrange(TILE_PIXELS)
            y = rng.randrange(TILE_PIXELS)
            if not water_mask(x, y + 2):
                surface.set_at((x, y), palette.shade)

    def _draw_waves(
        self,
        surface: pygame.Surface,
        palette: TilePalette,
        rng: random.Random,
        with_river: bool,
    ) -> None:
        """
        Draw rows of short wave crests over open water

        Args:
            surface (pygame.Surface): The tile being drawn
            palette (TilePalette): The colours of the tile
            rng (random.Random): The seeded random source for the tile
            with_river (bool): Whether the tile carries a river
        """
        # Stagger short crests row by row so the water reads as moving
        for row_index, y in enumerate(range(3, TILE_PIXELS - 2, 6)):
            for x in range(2 + (row_index % 2) * 5, TILE_PIXELS - 5, 10):
                pygame.draw.line(surface, palette.highlight, (x, y), (x + 3, y))
                pygame.draw.line(
                    surface, palette.detail, (x + 3, y + 1), (x + 5, y + 1)
                )


def main() -> None:
    """
    Generate every terrain tile into the packaged assets directory
    """
    output_directory = Path(__file__).parent / "assets" / "terrain"
    generator = TerrainTileGenerator(output_directory=output_directory)
    written_paths = generator.generate_all()

    # Report what was written so the run is easy to verify
    for path in written_paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
