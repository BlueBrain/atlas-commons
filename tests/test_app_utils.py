"""test app_utils"""

from pathlib import Path

import pytest as pt
from voxcell import VoxelData

import atlas_commons.app_utils as tested
from atlas_commons.exceptions import AtlasCommonsError

NRRDS = Path(Path(__file__).parent) / "nrrds"


def load_nrrds(filename_list):
    return [VoxelData.load_nrrd(Path(NRRDS, filename)) for filename in filename_list]


def test_assert_meta_properties_all_same():
    atlases = load_nrrds(["1.nrrd", "1.nrrd"])
    tested.assert_meta_properties(atlases)


def test_assert_meta_properties_numpy_shape_mismatch():
    atlases = load_nrrds(["1.nrrd", "1_direction_vectors.nrrd"])
    tested.assert_meta_properties(atlases)


def test_assert_meta_properties_shape_mismatch():
    atlases = load_nrrds(["1.nrrd", "1_shape.nrrd"])
    with pt.raises(AtlasCommonsError):
        tested.assert_meta_properties(atlases)


def test_assert_meta_properties_voxel_dimensions_mismatch():
    atlases = load_nrrds(["1.nrrd", "1_voxel_dimensions.nrrd"])
    with pt.raises(AtlasCommonsError):
        tested.assert_meta_properties(atlases)


def test_assert_meta_properties_offset_mismatch():
    atlases = load_nrrds(["1.nrrd", "1_offset.nrrd"])
    with pt.raises(AtlasCommonsError):
        tested.assert_meta_properties(atlases)


def test_assert_properties_1():
    atlases = load_nrrds(["1.nrrd", "1.nrrd"])
    tested.assert_properties(atlases)


def test_assert_properties_1():
    atlases = load_nrrds(["1.nrrd", "1_shape.nrrd"])
    with pt.raises(AtlasCommonsError):
        tested.assert_properties(atlases)


def test_assert_properties_2():
    atlases = load_nrrds(["1.nrrd", "1_voxel_dimensions.nrrd"])
    with pt.raises(AtlasCommonsError):
        tested.assert_properties(atlases)


def test_assert_properties_3():
    atlases = load_nrrds(["1.nrrd", "1_offset.nrrd"])
    with pt.raises(AtlasCommonsError):
        tested.assert_properties(atlases)
