from src.config.terrain import (
    BaseTerrain,
    CoastCornerTerrain,
    CoastRiverTerrain,
    CoastTerrain,
    DeepOceanTerrain,
    DesertTerrain,
    ForestRiverCornerTerrain,
    ForestRiverTerrain,
    ForestTerrain,
    GrassRiverCornerTerrain,
    GrassRiverTerrain,
    GrassTerrain,
    HillsRiverSourceTerrain,
    HillsTerrain,
    JungleRiverCornerTerrain,
    JungleRiverTerrain,
    JungleTerrain,
    MountainTerrain,
    PlainsRiverCornerTerrain,
    PlainsRiverTerrain,
    PlainsTerrain,
    ShallowOceanTerrain,
    SnowTerrain,
    TundraTerrain,
)
from src.map.base.coordinates import BaseCoordinates
from src.map.base.rural import BaseRural
from src.map.utils.land_classifier import ClassifiedTiles
import numpy as np
from scipy.ndimage import distance_transform_edt
from .params import StandardMapParameters

# Alias the coordinate and direction types used throughout the model
Coordinate = tuple[int, int]
Direction = tuple[int, int]

# Define the orthogonal directions and their clockwise rotation from north
NORTH: Direction = (0, 1)
EAST: Direction = (1, 0)
SOUTH: Direction = (0, -1)
WEST: Direction = (-1, 0)
ORTHOGONAL_DIRECTIONS: tuple[Direction, ...] = (NORTH, EAST, SOUTH, WEST)
DIRECTION_ROTATIONS: dict[Direction, int] = {NORTH: 0, EAST: 90, SOUTH: 180, WEST: 270}


class StandardLandTerrainModel:
    def __init__(
        self,
        max_river_length: int = 50,
        randomise_tile_rotation: bool = True,
    ):
        """
        Create a model to assign land to different parts of an island

        Args:
            max_river_length (int): The maximum number of tiles a single river may occupy before
                it is abandoned as unroutable
            randomise_tile_rotation (bool): Whether non-directional tiles (flat land, hills,
                mountains, ocean) are given a random orthogonal rotation for visual variety
        """
        self.max_river_length = max_river_length
        self.randomise_tile_rotation = randomise_tile_rotation
        self.flat_land_types = [
            DesertTerrain,
            ForestTerrain,
            GrassTerrain,
            JungleTerrain,
            PlainsTerrain,
            SnowTerrain,
            TundraTerrain,
        ]
        self.river_tile_map = {
            ForestTerrain.name: ForestRiverTerrain,
            GrassTerrain.name: GrassRiverTerrain,
            JungleTerrain.name: JungleRiverTerrain,
            PlainsTerrain.name: PlainsRiverTerrain,
        }
        self.river_corner_tile_map = {
            ForestTerrain.name: ForestRiverCornerTerrain,
            GrassTerrain.name: GrassRiverCornerTerrain,
            JungleTerrain.name: JungleRiverCornerTerrain,
            PlainsTerrain.name: PlainsRiverCornerTerrain,
        }
        self.river_tile_names = set(self.river_tile_map.keys())
        self.hills = HillsTerrain
        self.mountains = MountainTerrain

    def create_tiles(
        self, classified_tiles: ClassifiedTiles, map_params: StandardMapParameters
    ) -> set[BaseRural]:
        """
        Assign a terrain type and rotation to every tile on the map

        Args:
            classified_tiles (ClassifiedTiles): The interior, coastal, shallow ocean and deep ocean
                masks for the map
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            set[BaseRural]: A tile for every interior, coastal and ocean coordinate on the map
        """
        # Derive a temperature for every tile
        tile_temperatures = self._create_tile_temperature(
            classified_tiles.is_interior, map_params
        )

        # Assign flat terrain to the island interiors
        terrain_map = self._assign_flat_terrain(
            classified_tiles.is_interior, tile_temperatures
        )

        # Overwrite the interior with mountains, then hills
        terrain_map = self._assign_mountains(
            classified_tiles.is_interior, map_params, terrain_map
        )
        terrain_map = self._assign_hills(
            classified_tiles.is_interior, map_params, terrain_map
        )

        # Route rivers from hill sources down to the coast
        river_tiles, river_coordinates = self._assign_rivers(
            classified_tiles, map_params, terrain_map
        )

        # Combine the river tiles with the remaining land, coast and ocean tiles
        all_tiles = set(river_tiles)
        all_tiles |= self._create_land_tiles(terrain_map, river_coordinates)
        all_tiles |= self._create_coast_tiles(
            classified_tiles, map_params, river_coordinates
        )
        all_tiles |= self._create_ocean_tiles(classified_tiles)

        return all_tiles

    def _assign_flat_terrain(
        self, interior_mask: np.ndarray, tile_temperatures: np.ndarray
    ) -> dict[Coordinate, BaseTerrain]:
        """
        Assign a flat terrain land type to each interior tile

        Args:
            interior_mask (np.ndarray): Determining whether a tile is on the interior of an
                island (as coastal terrains do not need to be assigned)
            tile_temperatures (np.ndarray): The temperature of each tile

        Returns:
            dict[Coordinate, BaseTerrain]: Mapping each interior coordinate to its terrain type
        """
        # Get unscaled probabilities for each flat terrain in each tile
        terrain_probabilities = {
            terrain: self._get_terrain_tile_prob(tile_temperatures, terrain)
            for terrain in self.flat_land_types
        }

        # Stack the probabilities into a single array with terrain on the final axis
        probabilities = np.stack(
            [terrain_probabilities[terrain] for terrain in self.flat_land_types],
            axis=-1,
        )

        # Restrict sampling to interior tiles only
        flat_probabilities = probabilities[interior_mask]

        # Normalise the probabilities per tile
        flat_probabilities = flat_probabilities / flat_probabilities.sum(
            axis=1, keepdims=True
        )

        # Draw one uniform value per tile
        random_values = np.random.random(flat_probabilities.shape[0])

        # Pick the first terrain whose cumulative probability exceeds the random value
        cumulative = np.cumsum(flat_probabilities, axis=1)
        terrain_indices = (cumulative > random_values[:, None]).argmax(axis=1)

        # Map each interior coordinate to its sampled terrain type
        terrain_map = {
            (int(tile_x), int(tile_y)): self.flat_land_types[terrain_index]
            for (tile_x, tile_y), terrain_index in zip(
                np.argwhere(interior_mask), terrain_indices
            )
        }

        return terrain_map

    def _assign_mountains(
        self,
        interior_mask: np.ndarray,
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
    ) -> dict[Coordinate, BaseTerrain]:
        """
        Assign mountains to the land, overwriting any existing terrain

        Args:
            interior_mask (np.ndarray): The mask determining whether a tile is in the interior of an island
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current flat terrain type

        Returns:
            dict[Coordinate, BaseTerrain]: An updated dictionary containing mountains (and orthogonal hills)
        """
        # Seed the mountain ranges
        seed_coordinates = self._get_seed_coordinates(
            interior_mask, map_params.mountain_range_seed_prob
        )

        # Grow a range from each seed
        for seed in seed_coordinates:
            # Skip seeds that an earlier range has already claimed
            if tile_assignments[seed].name == self.mountains.name:
                continue

            # Walk the range, blocking tiles that are already mountains
            range_coordinates = self._grow_range(
                start=seed,
                terrain=self.mountains,
                interior_mask=interior_mask,
                map_params=map_params,
                tile_assignments=tile_assignments,
                continue_prob=map_params.mountain_range_continue_prob,
                blocked_names={self.mountains.name},
            )

            # Skirt the range with hills
            self._assign_orthogonal_hills(
                range_coordinates, interior_mask, map_params, tile_assignments
            )

        return tile_assignments

    def _assign_hills(
        self,
        interior_mask: np.ndarray,
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
    ) -> dict[Coordinate, BaseTerrain]:
        """
        Assign hills to the land, overwriting any existing terrain except for mountains

        Args:
            interior_mask (np.ndarray): The mask determining whether a tile is in the interior of an island
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current flat terrain type

        Returns:
            dict[Coordinate, BaseTerrain]: An updated dictionary containing hills
        """
        # Seed the hill ranges
        seed_coordinates = self._get_seed_coordinates(
            interior_mask, map_params.hill_range_seed_prob
        )

        # Grow a range from each seed
        for seed in seed_coordinates:
            # Skip seeds that are already mountains or hills
            if tile_assignments[seed].name in {self.mountains.name, self.hills.name}:
                continue

            # Walk the range, blocking tiles that are already mountains or hills
            self._grow_range(
                start=seed,
                terrain=self.hills,
                interior_mask=interior_mask,
                map_params=map_params,
                tile_assignments=tile_assignments,
                continue_prob=map_params.hill_range_continue_prob,
                blocked_names={self.mountains.name, self.hills.name},
            )

        return tile_assignments

    def _assign_orthogonal_hills(
        self,
        range_coordinates: list[Coordinate],
        interior_mask: np.ndarray,
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
    ) -> None:
        """
        Assign hills to the interior tiles orthogonally adjacent to a mountain range

        Args:
            range_coordinates (list[Coordinate]): The coordinates making up the mountain range
            interior_mask (np.ndarray): The mask determining whether a tile is in the interior of an island
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current terrain type, updated in place

        Returns:
            None. Updates the tile assignments in place.
        """
        # Consider every neighbour of every mountain in the range
        for mountain_coordinates in range_coordinates:
            for hill_candidate in self._get_adjacent_coordinates(
                mountain_coordinates, map_params
            ):
                # Limit to interior tiles that are not already mountains or hills
                if not interior_mask[hill_candidate]:
                    continue
                if tile_assignments[hill_candidate].name in {
                    self.mountains.name,
                    self.hills.name,
                }:
                    continue

                # Assign the hill if the roll succeeds
                if np.random.random() < map_params.hill_orthogonal_prob:
                    tile_assignments[hill_candidate] = self.hills

    def _assign_rivers(
        self,
        classified_tiles: ClassifiedTiles,
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
    ) -> tuple[set[BaseRural], set[Coordinate]]:
        """
        Route rivers from hill sources to the coast and build their tiles

        Args:
            classified_tiles (ClassifiedTiles): The interior, coastal and ocean masks for the map
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current terrain type

        Returns:
            tuple[set[BaseRural], set[Coordinate]]: The river tiles (including their coastal mouths)
                and the set of coordinates they occupy
        """
        river_tiles: set[BaseRural] = set()
        river_coordinates: set[Coordinate] = set()

        # Attempt a river from each hill tile
        for coordinates, terrain in tile_assignments.items():
            # Limit sources to hills that no other river has claimed
            if terrain.name != self.hills.name or coordinates in river_coordinates:
                continue

            # Roll for a river seed
            if np.random.random() >= map_params.river_seed_prob:
                continue

            # Trace a path to the sea, discarding the river if it cannot get there
            river_path = self._trace_river_path(
                coordinates,
                classified_tiles,
                map_params,
                tile_assignments,
                river_coordinates,
            )
            if river_path is None:
                continue

            # Convert the path into tiles and reserve its coordinates
            river_tiles |= self._create_river_tiles(
                river_path, map_params, tile_assignments
            )
            river_coordinates |= set(river_path)

        return river_tiles, river_coordinates

    def _trace_river_path(
        self,
        source: Coordinate,
        classified_tiles: ClassifiedTiles,
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
        used_coordinates: set[Coordinate],
    ) -> list[Coordinate] | None:
        """
        Trace the coordinates of a single river from a hill source to a coastal mouth

        Args:
            source (Coordinate): The hill tile the river rises from
            classified_tiles (ClassifiedTiles): The interior, coastal and ocean masks for the map
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current terrain type
            used_coordinates (set[Coordinate]): Coordinates already claimed by other rivers

        Returns:
            list[Coordinate] | None: The path from source to coastal mouth, or None if the river
                could not reach the sea
        """
        river_path = [source]

        # Extend the river one tile at a time
        while len(river_path) < self.max_river_length:
            # Get the candidate neighbours in random order, excluding tiles already in use
            blocked_coordinates = used_coordinates | set(river_path)
            candidates = [
                candidate
                for candidate in self._get_adjacent_coordinates(
                    river_path[-1], map_params
                )
                if candidate not in blocked_coordinates
            ]

            # Finish at the coast as soon as one is reachable
            coastal_candidates = [
                candidate
                for candidate in candidates
                if classified_tiles.is_coastal[candidate]
            ]
            if coastal_candidates:
                river_path.append(coastal_candidates[0])
                return river_path

            # Otherwise continue through terrain that supports a river
            inland_candidates = [
                candidate
                for candidate in candidates
                if tile_assignments.get(candidate) is not None
                and tile_assignments[candidate].name in self.river_tile_names
            ]
            if not inland_candidates:
                return None

            river_path.append(inland_candidates[0])

        return None

    def _create_river_tiles(
        self,
        river_path: list[Coordinate],
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
    ) -> set[BaseRural]:
        """
        Convert a traced river path into source, straight, corner and mouth tiles

        Args:
            river_path (list[Coordinate]): The path from hill source to coastal mouth
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current terrain type

        Returns:
            set[BaseRural]: The tiles making up the river
        """
        river_tiles: set[BaseRural] = set()

        for path_index, coordinates in enumerate(river_path):
            # Work out which way the river enters and leaves this tile
            direction_in = (
                self._get_direction(river_path[path_index - 1], coordinates, map_params)
                if path_index > 0
                else None
            )
            direction_out = (
                self._get_direction(coordinates, river_path[path_index + 1], map_params)
                if path_index + 1 < len(river_path)
                else None
            )

            # Raise an error if both inwards and outwards directions are none
            if direction_out is None and direction_in is None:
                raise ValueError("One of the in and out directions must be defined")

            # Place a hill source facing the way the river leaves
            if direction_in is None:
                river_tiles.add(
                    self._create_tile(
                        HillsRiverSourceTerrain,
                        coordinates,
                        DIRECTION_ROTATIONS[direction_out],  # ty: ignore
                    )
                )
                continue

            # Place a coastal mouth facing back towards the inland tile that feeds it
            if direction_out is None:
                river_tiles.add(
                    self._create_tile(
                        CoastRiverTerrain,
                        coordinates,
                        DIRECTION_ROTATIONS[self._reverse(direction_in)],
                    )
                )
                continue

            # Place a straight tile, rotated for east-west flow
            if direction_in == direction_out:
                terrain = self.river_tile_map[tile_assignments[coordinates].name]
                rotation = 0 if direction_in[0] == 0 else 90
                river_tiles.add(self._create_tile(terrain, coordinates, rotation))
                continue

            # Place a corner tile joining the inflow and outflow edges
            terrain = self.river_corner_tile_map[tile_assignments[coordinates].name]
            rotation = self._get_corner_rotation(
                self._reverse(direction_in), direction_out
            )
            river_tiles.add(self._create_tile(terrain, coordinates, rotation))

        return river_tiles

    def _create_land_tiles(
        self,
        tile_assignments: dict[Coordinate, BaseTerrain],
        river_coordinates: set[Coordinate],
    ) -> set[BaseRural]:
        """
        Build the tiles for every interior coordinate not already occupied by a river

        Args:
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current terrain type
            river_coordinates (set[Coordinate]): Coordinates already claimed by rivers

        Returns:
            set[BaseRural]: The interior land tiles
        """
        # Create a tile for each unclaimed interior coordinate
        return {
            self._create_tile(terrain, coordinates, self._get_tile_rotation())
            for coordinates, terrain in tile_assignments.items()
            if coordinates not in river_coordinates
        }

    def _create_coast_tiles(
        self,
        classified_tiles: ClassifiedTiles,
        map_params: StandardMapParameters,
        river_coordinates: set[Coordinate],
    ) -> set[BaseRural]:
        """
        Build the tiles for every coastal coordinate not already occupied by a river mouth

        Args:
            classified_tiles (ClassifiedTiles): The interior, coastal and ocean masks for the map
            map_params (StandardMapParameters): The parameters for the map
            river_coordinates (set[Coordinate]): Coordinates already claimed by rivers

        Returns:
            set[BaseRural]: The coastal tiles, using corner variants where the coast turns
        """
        coast_tiles: set[BaseRural] = set()

        # Treat both ocean depths as water for orientation purposes
        water_mask = classified_tiles.is_shallow_ocean | classified_tiles.is_deep_ocean

        for tile_x, tile_y in np.argwhere(classified_tiles.is_coastal):
            coordinates = (int(tile_x), int(tile_y))

            # Skip coastal tiles that a river mouth already occupies
            if coordinates in river_coordinates:
                continue

            # Find which edges of the tile face water
            water_directions = {
                direction
                for direction in ORTHOGONAL_DIRECTIONS
                if (
                    neighbour := self._move_orthogonally(
                        coordinates, direction, map_params
                    )
                )
                is not None
                and water_mask[neighbour[1], neighbour[0]]
            }

            # Choose the straight or corner variant and its rotation
            terrain, rotation = self._get_coast_terrain(water_directions)
            coast_tiles.add(self._create_tile(terrain, coordinates, rotation))

        return coast_tiles

    def _create_ocean_tiles(self, classified_tiles: ClassifiedTiles) -> set[BaseRural]:
        """
        Build the tiles for every shallow and deep ocean coordinate

        Args:
            classified_tiles (ClassifiedTiles): The interior, coastal and ocean masks for the map

        Returns:
            set[BaseRural]: The ocean tiles
        """
        ocean_tiles: set[BaseRural] = set()

        # Create a tile for each coordinate at each ocean depth
        for ocean_mask, terrain in (
            (classified_tiles.is_shallow_ocean, ShallowOceanTerrain),
            (classified_tiles.is_deep_ocean, DeepOceanTerrain),
        ):
            for tile_x, tile_y in np.argwhere(ocean_mask):
                ocean_tiles.add(
                    self._create_tile(
                        terrain, (int(tile_x), int(tile_y)), self._get_tile_rotation()
                    )
                )

        return ocean_tiles

    def _get_coast_terrain(
        self, water_directions: set[Direction]
    ) -> tuple[BaseTerrain, int]:
        """
        Choose the coast terrain variant and rotation implied by the water around a tile

        A tile with water on two adjacent edges is a corner; anything else is treated as a
        straight coast facing a single edge.

        Args:
            water_directions (set[Direction]): The directions from the tile that contain water

        Returns:
            tuple[BaseTerrain, int]: The coast terrain variant and its clockwise rotation
        """
        # Collect the adjacent direction pairs that both face water
        corner_pairs = [
            (first, second)
            for first, second in zip(
                ORTHOGONAL_DIRECTIONS,
                ORTHOGONAL_DIRECTIONS[1:] + ORTHOGONAL_DIRECTIONS[:1],
            )
            if first in water_directions and second in water_directions
        ]

        # Prefer a corner tile, picking at random where a spit offers more than one
        if corner_pairs:
            first, second = corner_pairs[np.random.randint(len(corner_pairs))]
            return CoastCornerTerrain, self._get_corner_rotation(first, second)

        # Otherwise face the single water edge
        if water_directions:
            facing_directions = sorted(
                water_directions, key=lambda direction: DIRECTION_ROTATIONS[direction]
            )
            return CoastTerrain, DIRECTION_ROTATIONS[facing_directions[0]]

        # Fall back to an arbitrary rotation for a coast tile with no water neighbour
        return CoastTerrain, self._get_random_orthogonal_rotation()

    def _grow_range(
        self,
        start: Coordinate,
        terrain: BaseTerrain,
        interior_mask: np.ndarray,
        map_params: StandardMapParameters,
        tile_assignments: dict[Coordinate, BaseTerrain],
        continue_prob: float,
        blocked_names: set[str],
    ) -> list[Coordinate]:
        """
        Grow a range of a single terrain type by random walking from a seed tile

        Args:
            start (Coordinate): The seed coordinate for the range
            terrain (BaseTerrain): The terrain to assign along the range
            interior_mask (np.ndarray): The mask determining whether a tile is in the interior of an island
            map_params (StandardMapParameters): The parameters for the map
            tile_assignments (dict[Coordinate, BaseTerrain]): A dictionary containing a map from each
                coordinate to its current terrain type, updated in place
            continue_prob (float): The probability the range extends by a further tile
            blocked_names (set[str]): Terrain names the range may not walk onto

        Returns:
            list[Coordinate]: The coordinates assigned to the range
        """
        # Claim the seed tile
        tile_assignments[start] = terrain
        range_coordinates = [start]

        # Extend the range while the rolls succeed
        while np.random.random() < continue_prob:
            next_coordinates = None

            # Look for an adjacent interior tile that is not blocked
            for candidate in self._get_adjacent_coordinates(
                range_coordinates[-1], map_params
            ):
                if not interior_mask[candidate]:
                    continue
                if tile_assignments[candidate].name in blocked_names:
                    continue

                next_coordinates = candidate
                break

            # Stop the range if it is boxed in
            if next_coordinates is None:
                break

            # Claim the tile and continue from it
            tile_assignments[next_coordinates] = terrain
            range_coordinates.append(next_coordinates)

        return range_coordinates

    def _get_terrain_tile_prob(
        self, temperature: np.ndarray, terrain: BaseTerrain
    ) -> np.ndarray:
        """
        Get the unscaled probability of each tile being each terrain

        We model this as simply 1/(squared difference)

        Args:
            temperature (np.ndarray): The by-tile temperature
            terrain (BaseTerrain): The terrain type

        Returns:
            np.ndarray: The unscaled probability of the terrain in each tile
        """
        if terrain.geography is None:
            raise ValueError(
                f"This method can only be called on cases where terrain has geography: got {terrain}."
            )
        return 1 / np.clip(
            np.square(temperature - terrain.geography.temperature), 0.25, np.inf
        )

    def _create_tile_temperature(
        self, interior_mask: np.ndarray, map_params: StandardMapParameters
    ) -> np.ndarray:
        """
        Create a tile-level temperature

        Args:
            interior_mask (np.ndarray): Determining whether a tile is on the interior of an
                island (as coastal terrains do not need to be assigned)
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            np.ndarray: Containing the temperature of each tile
        """
        # Assign a baseline temperature for each x coordinate, peaking at the equator
        map_size_x = map_params.map_size.size_x
        baseline_temperature = (
            np.sin(np.pi * np.arange(map_size_x) / map_size_x)
            * map_params.world_temperature_amplitude
            + map_params.world_temperature_centre
        )

        # Cool the land nearest the coast
        distance_to_water = self._get_distance_to_water(interior_mask, map_params)
        coastal_cooling = map_params.water_cooling_max * np.exp(
            -distance_to_water / map_params.water_cooling_scale
        )

        # Combine the baseline, the cooling and per-tile noise
        temperature_noise = np.random.normal(
            scale=np.sqrt(map_params.world_temperature_variance),
            size=interior_mask.shape,
        )
        overall_tile_temperature = (
            baseline_temperature[np.newaxis, :] - coastal_cooling + temperature_noise
        )

        return overall_tile_temperature

    def _get_adjacent_coordinates(
        self, coordinates: Coordinate, map_params: StandardMapParameters
    ) -> list[Coordinate]:
        """
        Get the on-map orthogonal neighbours of a coordinate in a random order

        Args:
            coordinates (Coordinate): The coordinate to look around
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            list[Coordinate]: The neighbouring coordinates, shuffled
        """
        # Collect the neighbours that fall on the map
        adjacent_coordinates = []
        for direction in self._get_random_orthogonal_order():
            neighbour = self._move_orthogonally(coordinates, direction, map_params)
            if neighbour is not None:
                adjacent_coordinates.append(neighbour)

        return adjacent_coordinates

    def _get_tile_rotation(self) -> int:
        """
        Get the rotation to apply to a non-directional tile

        Returns:
            int: A random orthogonal rotation, or zero if rotation randomisation is disabled
        """
        return (
            self._get_random_orthogonal_rotation()
            if self.randomise_tile_rotation
            else 0
        )

    @staticmethod
    def _create_tile(
        terrain: BaseTerrain, coordinates: Coordinate, rotation: int
    ) -> BaseRural:
        """
        Build a single tile

        Args:
            terrain (BaseTerrain): The terrain type for the tile
            coordinates (Coordinate): The coordinates of the tile
            rotation (int): The clockwise rotation of the tile, in {0,90,180,270}

        Returns:
            BaseRural: The constructed tile
        """
        return BaseRural(
            terrain=terrain,
            coordinates=BaseCoordinates(x=coordinates[0], y=coordinates[1]),
            rotation=rotation,
        )

    @staticmethod
    def _get_seed_coordinates(
        interior_mask: np.ndarray, seed_prob: float
    ) -> list[Coordinate]:
        """
        Sample seed coordinates from the interior of the islands

        Args:
            interior_mask (np.ndarray): The mask determining whether a tile is in the interior of an island
            seed_prob (float): The per-tile probability of being a seed

        Returns:
            list[Coordinate]: The sampled seed coordinates
        """
        # Sample the seeds within the interior only
        is_seed = (
            np.random.random(size=interior_mask.shape) < seed_prob
        ) & interior_mask

        return [(int(tile_x), int(tile_y)) for tile_x, tile_y in np.argwhere(is_seed)]

    @staticmethod
    def _get_distance_to_water(
        interior_mask: np.ndarray, map_params: StandardMapParameters
    ) -> np.ndarray:
        """
        Get the Euclidean distance between each land tile and the water (i.e. the nearest coastal tile)

        Args:
            interior_mask (np.ndarray): Determining whether a tile is on the interior of an
                island (as coastal terrains do not need to be assigned)
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            np.ndarray: An array containing the distance to water for each tile
        """
        # Tile the mask across any wrapping axis so distances can cross the map edge
        padded = interior_mask
        if map_params.map_size.wrap_x:
            padded = np.concatenate([padded, padded, padded], axis=0)
        if map_params.map_size.wrap_y:
            padded = np.concatenate([padded, padded, padded], axis=1)

        # Measure the distance from each interior tile to the nearest non-interior tile
        distance = distance_transform_edt(padded)

        # Trim the padding back off
        if map_params.map_size.wrap_x:
            size_x = interior_mask.shape[0]
            distance = distance[size_x : 2 * size_x]
        if map_params.map_size.wrap_y:
            size_y = interior_mask.shape[1]
            distance = distance[:, size_y : 2 * size_y]

        return distance

    @staticmethod
    def _get_random_orthogonal_order() -> list[Direction]:
        """
        Get a random ordering of the orthogonal directions

        Returns:
            list[Direction]: The directions, shuffled
        """
        # Permute the fixed direction tuple
        order = np.random.permutation(len(ORTHOGONAL_DIRECTIONS))

        return [ORTHOGONAL_DIRECTIONS[index] for index in order]

    @staticmethod
    def _get_random_orthogonal_rotation() -> int:
        """
        Get a random orthogonal rotation

        Returns:
            int: The random rotation, in {0,90,180,270}
        """
        return int(np.random.choice([0, 90, 180, 270]))

    @staticmethod
    def _move_orthogonally(
        coordinates: Coordinate, direction: Direction, map_params: StandardMapParameters
    ) -> Coordinate | None:
        """
        Add an orthogonal move to a set of coordinates, respecting the map wrapping

        Args:
            coordinates (Coordinate): The coordinates of the current point
            direction (Direction): The direction we want to move in
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            Coordinate | None: The new coordinates, or None if the move leaves a non-wrapping map
        """
        # Wrap or reject the move on each axis independently
        moved_x = coordinates[0] + direction[0]
        if map_params.map_size.wrap_x:
            moved_x %= map_params.map_size.size_x
        elif not 0 <= moved_x < map_params.map_size.size_x:
            return None

        moved_y = coordinates[1] + direction[1]
        if map_params.map_size.wrap_y:
            moved_y %= map_params.map_size.size_y
        elif not 0 <= moved_y < map_params.map_size.size_y:
            return None

        return (moved_x, moved_y)

    @classmethod
    def _get_direction(
        cls, start: Coordinate, end: Coordinate, map_params: StandardMapParameters
    ) -> Direction:
        """
        Get the orthogonal direction from one coordinate to an adjacent coordinate

        Args:
            start (Coordinate): The coordinate being moved from
            end (Coordinate): The adjacent coordinate being moved to
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            Direction: The direction of travel

        Raises:
            ValueError: If the two coordinates are not orthogonally adjacent
        """
        # Match the move against each orthogonal direction, allowing for wrapping
        for direction in ORTHOGONAL_DIRECTIONS:
            if cls._move_orthogonally(start, direction, map_params) == end:
                return direction

        raise ValueError(f"Coordinates {start} and {end} are not orthogonally adjacent")

    @staticmethod
    def _reverse(direction: Direction) -> Direction:
        """
        Reverse an orthogonal direction

        Args:
            direction (Direction): The direction to reverse

        Returns:
            Direction: The opposite direction
        """
        return (-direction[0], -direction[1])

    @staticmethod
    def _get_corner_rotation(first: Direction, second: Direction) -> int:
        """
        Get the rotation of a corner tile joining two adjacent edges

        The unrotated corner tile is assumed to join its north and east edges, so the rotation is
        that of whichever of the two directions is 90 degrees anticlockwise of the other.

        Args:
            first (Direction): One of the two edges the corner joins
            second (Direction): The other edge the corner joins

        Returns:
            int: The clockwise rotation, in {0,90,180,270}

        Raises:
            ValueError: If the two directions are not adjacent
        """
        first_rotation = DIRECTION_ROTATIONS[first]
        second_rotation = DIRECTION_ROTATIONS[second]

        # Reject opposite or identical edges, which no corner tile can represent
        if (second_rotation - first_rotation) % 360 not in {90, 270}:
            raise ValueError(f"Directions {first} and {second} do not form a corner")

        # Take the direction that the other sits clockwise of
        return (
            first_rotation
            if (second_rotation - first_rotation) % 360 == 90
            else second_rotation
        )
