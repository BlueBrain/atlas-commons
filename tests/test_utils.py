"""test utils"""
from pathlib import Path

TEST_PATH = Path(Path(__file__).parent)

import numpy as np
import numpy.testing as npt
import pytest
from voxcell import RegionMap

import atlas_commons.utils as tested
from atlas_commons.exceptions import AtlasCommonsError


@pytest.fixture
def region_map_1():
    return RegionMap.load_json(str(Path(TEST_PATH, "1.json")))


@pytest.fixture
def annotation():
    return np.arange(27).reshape((3, 3, 3))


@pytest.fixture
def expected_region_mask():
    expected = np.zeros((3, 3, 3), dtype=bool)
    expected[0, 0, 2] = True  # label 2, "SSp-m6b"
    expected[1, 0, 0] = True  # label 9, "SSp-tr6a"
    expected[2, 1, 1] = True  # label 22, "SSp-tr6a"

    return expected


def test_query_region_mask(region_map_1, annotation, expected_region_mask):
    region = {
        "query": "Isocortex",
        "attribute": "acronym",
        "with_descendants": True,
    }
    mask = tested.query_region_mask(region, annotation, region_map_1)
    npt.assert_array_equal(mask, expected_region_mask)


def test_get_region_mask(region_map_1, annotation, expected_region_mask):
    mask = tested.get_region_mask("Isocortex", annotation, region_map_1)
    npt.assert_array_equal(mask, expected_region_mask)


def test_split_into_halves():
    volume = np.array(
        [
            [[0, 1, 2], [2, 3, 4]],
            [[4, 5, 6], [7, 8, 9]],
        ],
        dtype=np.int64,
    )
    halves = tested.split_into_halves(volume)
    npt.assert_array_equal(
        halves[0],
        np.array(
            [
                [[0, 0, 0], [2, 0, 0]],
                [[4, 0, 0], [7, 0, 0]],
            ],
            dtype=np.int64,
        ),
    )
    npt.assert_array_equal(
        halves[1],
        np.array(
            [
                [[0, 1, 2], [0, 3, 4]],
                [[0, 5, 6], [0, 8, 9]],
            ]
        ),
    )


def get_hierarchy_excerpt():
    return {
        "id": 315,
        "acronym": "Isocortex",
        "name": "Isocortex",
        "children": [
            {
                "id": 500,
                "acronym": "MO",
                "name": "Somatomotor areas",
                "children": [
                    {
                        "id": 107,
                        "acronym": "MO1",
                        "name": "Somatomotor areas, Layer 1",
                        "children": [],
                    },
                    {
                        "id": 219,
                        "acronym": "MO2/3",
                        "name": "Somatomotor areas, Layer 2/3",
                        "children": [],
                    },
                    {
                        "id": 299,
                        "acronym": "MO5",
                        "name": "Somatomotor areas, layer 5",
                        "children": [],
                    },
                ],
            },
            {
                "id": 453,
                "acronym": "SS",
                "name": "Somatosensory areas",
                "children": [
                    {"id": 12993, "acronym": "SS1", "name": "Somatosensory areas, layer 1"}
                ],
            },
        ],
    }


def get_metadata(region_fullname="Isocortex"):
    return {
        "region": {
            "name": region_fullname,
            "query": region_fullname,
            "attribute": "name",
            "with_descendants": True,
        },
        "layers": {
            "names": ["layer_1", "layer_23", "layer_5"],
            "queries": ["@.*1$", "@.*2/3$", "@.*5$"],
            "attribute": "acronym",
            "with_descendants": True,
        },
    }


@pytest.fixture
def region_map():
    return RegionMap.from_dict(get_hierarchy_excerpt())


@pytest.fixture
def annotated_volume():
    return np.array([[[107, 107, 107, 12993, 219, 219, 219, 299, 299, 299]]], dtype=np.uint32)


def test_create_layered_volume(region_map, annotated_volume):
    metadata = get_metadata("Isocortex")
    expected_layers_volume = np.array([[[1, 1, 1, 1, 2, 2, 2, 3, 3, 3]]], dtype=np.uint8)
    actual = tested.create_layered_volume(annotated_volume, region_map, metadata)
    npt.assert_array_equal(expected_layers_volume, actual)

    metadata = get_metadata("Somatomotor areas")
    expected_layers_volume = np.array([[[1, 1, 1, 0, 2, 2, 2, 3, 3, 3]]], dtype=np.uint8)
    actual = tested.create_layered_volume(annotated_volume, region_map, metadata)
    npt.assert_array_equal(expected_layers_volume, actual)


def test_get_layer_masks(region_map, annotated_volume):
    metadata = get_metadata("Isocortex")
    expected_layer_masks = {
        "layer_1": np.array([[[1, 1, 1, 1, 0, 0, 0, 0, 0, 0]]], dtype=bool),
        "layer_23": np.array([[[0, 0, 0, 0, 1, 1, 1, 0, 0, 0]]], dtype=bool),
        "layer_5": np.array([[[0, 0, 0, 0, 0, 0, 0, 1, 1, 1]]], dtype=bool),
    }
    actual = tested.get_layer_masks(annotated_volume, region_map, metadata)
    for layer_name in expected_layer_masks:
        npt.assert_array_equal(expected_layer_masks[layer_name], actual[layer_name])


def test_assert_metadata_content(region_map, annotated_volume):
    with pytest.raises(AtlasCommonsError):
        metadata = get_metadata("Isocortex")
        del metadata["layers"]
        tested.assert_metadata_content(metadata)

    with pytest.raises(AtlasCommonsError):
        metadata = get_metadata("Isocortex")
        del metadata["region"]
        tested.assert_metadata_content(metadata)

    with pytest.raises(AtlasCommonsError):
        metadata = get_metadata("Isocortex")
        del metadata["layers"]["attribute"]
        tested.assert_metadata_content(metadata)

    with pytest.raises(AtlasCommonsError):
        metadata = get_metadata("Isocortex")
        del metadata["layers"]["names"]
        tested.assert_metadata_content(metadata)

    with pytest.raises(AtlasCommonsError):
        metadata = get_metadata("Isocortex")
        del metadata["layers"]["queries"]
        tested.assert_metadata_content(metadata)


def test_zero_to_nan():
    # 3D unit vectors
    field = np.ones((2, 2, 2, 3), dtype=np.float32)
    field[0, 0, 0] = 0
    field[1, 1, 1] = 0
    expected = np.ones((2, 2, 2, 3), dtype=float)
    expected[0, 0, 0] = np.nan
    expected[1, 1, 1] = np.nan
    tested.zero_to_nan(field)
    npt.assert_array_equal(field, expected)

    # Quaternions
    field = np.ones((2, 2, 2, 4), dtype=np.float64)
    field[0, 1, 0] = 0
    field[1, 0, 1] = 0
    expected = np.ones((2, 2, 2, 4), dtype=float)
    expected[0, 1, 0] = np.nan
    expected[1, 0, 1] = np.nan
    tested.zero_to_nan(field)
    npt.assert_array_equal(field, expected)

    # Wrong input type
    field = np.ones((2, 2, 2, 4), dtype=int)
    with pytest.raises(ValueError):
        tested.zero_to_nan(field)


def test_normalized():
    # A 3D vector field of integer type
    vector_field = np.ones((2, 2, 2, 3), dtype=np.int32)
    normalized = tested.normalized(vector_field)
    npt.assert_array_almost_equal(normalized, np.full((2, 2, 2, 3), 1.0 / np.sqrt(3.0)))
    # A 4D vector field with some zero vectors
    vector_field = np.zeros((2, 2, 2, 4), dtype=np.float32)
    vector_field[0, 0, 0] = np.array([1, 1.0, 0.0, 0.0])
    vector_field[1, 1, 1] = np.array([0, 1, 1, 1])
    normalized = tested.normalized(vector_field)
    expected = np.full(normalized.shape, np.nan)
    expected[0, 0, 0] = np.array([1.0, 1.0, 0.0, 0.0]) / np.sqrt(2.0)
    expected[1, 1, 1] = np.array([0.0, 1.0, 1.0, 1.0]) / np.sqrt(3.0)
    npt.assert_array_almost_equal(normalized, expected)
