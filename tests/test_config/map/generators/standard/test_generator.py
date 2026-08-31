from src.map.generators.standard.generator import StandardMapGenerator
from src.map.generators.standard.params import StandardMapParameters
from src.map.base.map_size import BaseMapSize
from src.map.base.map import BaseMap


def test_standard_generator():
    generated_map = StandardMapGenerator(
        StandardMapParameters(map_size=BaseMapSize(size_x=50, size_y=30))
    ).generate()

    assert isinstance(generated_map, BaseMap)

    # Check tile number
    assert len(generated_map.tiles) == 50 * 30

    # Check multiple terrain types
    assert len({tile.rural_details.terrain.name for tile in generated_map.tiles}) > 1

    assert False