"""test app_utils"""

import logging
from pathlib import Path

import click
import pytest as pt
from click.testing import CliRunner
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


def test_common_atlas_options():
    @click.command()
    @tested.common_atlas_options
    def fun(annotation_path, hierarchy_path):
        assert Path(annotation_path).name == "annotation.nrrd"
        assert Path(hierarchy_path).name == "hierarchy.json"

    runner = CliRunner()
    with runner.isolated_filesystem():
        open("annotation.nrrd", "w")
        open("hierarchy.json", "w")
        result = runner.invoke(
            fun, ["--annotation-path", "annotation.nrrd", "--hierarchy-path", "hierarchy.json"]
        )
        assert result.exit_code == 0, str(result.output)


def test_set_verbose():
    L = logging.getLogger(__name__)
    tested.set_verbose(L, 0)
    assert L.level == logging.WARNING
    tested.set_verbose(L, 1)
    assert L.level == logging.INFO
    tested.set_verbose(L, 2)
    assert L.level == logging.DEBUG
    tested.set_verbose(L, 3)
    assert L.level == logging.DEBUG


def test_verbose_option():
    @click.command()
    @tested.verbose_option
    def fun(verbose):
        assert verbose == 2, verbose

    runner = CliRunner()
    result = runner.invoke(fun, ["-vv"])
    assert result.exit_code == 0, str(result.output)
