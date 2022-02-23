"""Generic atlas tools"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import voxcell

from atlas_commons.exceptions import AtlasCommonsError
from atlas_commons.typing import AnnotationT, BoolArray, FloatArray, NumericArray


def query_region_mask(
    region: dict, annotation: AnnotationT, region_map: voxcell.RegionMap
) -> BoolArray:
    """
    Create a mask for the region defined by `query`.

    Args:
        query: dict of the form
            {
                "query": "@.*layer 1",
                "attribute": "name",
                "with_descendants": True,  # Optional, defaults to False.
            }
            Each key corresponds to an argument of the function `RegionMap.find` that will be
            called to create the mask.
        annotation: 3D array of region ids containing the region to mask.
        region_map: a RegionMap object.

    Returns:
       3D boolean array of the same shape as annotation.
    """
    ids = region_map.find(
        region["query"], region["attribute"], with_descendants=region.get("with_descendants", False)
    )

    return np.isin(annotation, list(ids))


def get_region_mask(
    acronym: str, annotation: AnnotationT, region_map: voxcell.RegionMap
) -> BoolArray:
    """
    Create a mask for the region defined by `acronym`.

    Args:
        acronym: the acronym of the region to mask. If it starts with @
                 the remainder is interprereted as a regexp.
        annotation: 3D array of region ids containing the region to mask.
        region_map: a RegionMap object.

    Returns:
       3D boolean array of the same shape as annotation.

    """
    region = {"query": acronym, "attribute": "acronym", "with_descendants": True}

    return query_region_mask(region, annotation, region_map)


def split_into_halves(
    volume: NumericArray,
    halfway_offset: int = 0,
) -> Tuple[NumericArray, NumericArray]:
    """
    Split input 3D volume into two halves using the middle plane orthogonal to the z-axis.

    Args:
        volume: 3D numeric array.
            halfway_offset: Optional offset used for the splitting along the z-axis.
    Returns:
        tuple(left_volume, right_volume), the two halves of the input volume. Each has the same
        shape as `volume`. Voxels are zeroed for the z-values above, respectively below, the half
        of the z-dimension.
    """
    z_halfway = volume.shape[2] // 2 + halfway_offset
    left_volume = volume.copy()
    left_volume[..., z_halfway:] = 0
    right_volume = volume.copy()
    right_volume[..., :z_halfway] = 0

    return left_volume, right_volume


def assert_metadata_content(metadata: dict) -> None:
    """
    Raise an error if some mandatory key is missing in `metadata`.

    Args:
        metadata: dict of the form
            {
                "region" : {
                    "name": "aibs_isocortex",
                    "query": "Isocortex",
                    "attribute": "acronym"
                }
                "layers": {
                    "names": ["layer 1", "layer 2", "layer3", "layer 4", "layer 5", "layer 6"],
                    "queries": ["@.*;L1$", "@.*;L2$", "@.;L3*$", "@.*;L4$", "@.*;L5$", "@.*;L6$"],
                    "attribute": "acronym"
                }
            }
            Queries in "query" or "queries" should be compliant with the interface of
            voxcell.RegionMap.find interface. The value of "attribute" can be "acronym" or "name".

    Raise:
        AtlasCommonsError if a mandatory key is missing or if the length of
        layer names and queries are different.
    """

    if "region" not in metadata:
        raise AtlasCommonsError('Missing "region" key')

    metadata_region = metadata["region"]

    missing = {"name", "query", "attribute"} - set(metadata_region.keys())
    if missing:
        err_msg = (
            'The "region" dictionary has the following mandatory keys: '
            '"name", "query" and "attribute".'
            f" Missing: {missing}."
        )
        raise AtlasCommonsError(err_msg)

    if "layers" not in metadata:
        raise AtlasCommonsError('Missing "layers" key')

    metadata_layers = metadata["layers"]

    missing = {"names", "queries", "attribute"} - set(metadata_layers.keys())
    if missing:
        err_msg = (
            'The "layers" dictionary has the following mandatory keys: '
            '"names", "queries" and "attribute".'
            f" Missing: {missing}."
        )
        raise AtlasCommonsError(err_msg)

    if not (
        isinstance(metadata_layers["names"], list)
        and isinstance(metadata_layers["queries"], list)
        and len(metadata_layers["names"]) == len(metadata_layers["queries"])
    ):
        raise AtlasCommonsError(
            'The values of "names" and "queries" must be lists of the same length.'
        )


def create_layered_volume(
    annotated_volume: AnnotationT,
    region_map: voxcell.RegionMap,
    metadata: dict,
):
    """
    Create a 3D volume whose voxels are labeled by 1-based layer indices.

    Args:
        annotated_volume: integer numpy array of shape (W, H, D) where
            W, H and D are the integer dimensions of the volume domain.
        region_map: RegionMap object used to navigate the brain regions hierarchy.
        metadata: dict, see :fun:`atlas_commons.utils.assert_metadata`.
            This dict contains the definitions of the layers to be built.

    Returns:
        A numpy array of the same shape as the input volume, i.e., (W, H, D). Voxels are labeled by
        the 1-based indices of the layers defined in `metadata`. Voxels out of the region defined in
        `metadata` are labeled with the 0 index.

    Raises:
        AtlasBuildingErrors if `metadata` has an incorrect format.
    """

    assert_metadata_content(metadata)

    metadata_layers = metadata["layers"]
    layers = np.zeros_like(annotated_volume, dtype=np.uint8)
    region_ids = region_map.find(
        metadata["region"]["query"],
        attr=metadata["region"]["attribute"],
        with_descendants=metadata["region"].get("with_descendants", False),
    )
    for (index, query) in enumerate(metadata_layers["queries"], 1):
        layer_ids = region_map.find(
            query,
            attr=metadata_layers["attribute"],
            with_descendants=metadata_layers.get("with_descendants", False),
        )
        layers[np.isin(annotated_volume, list(layer_ids & region_ids))] = index

    return layers


def get_layer_masks(
    annotated_volume: AnnotationT,
    region_map: voxcell.RegionMap,
    metadata: dict,
) -> Dict[str, BoolArray]:
    """
    Create a 3D boolean mask of each layer in `metadata`.

    Args:
        annotated_volume: int array of shape (W, H, D) where W, H and D are integer dimensions;
            this array is the annotated volume of the brain region of interest.
        region_map: RegionMap object to navigate the brain regions hierarchy.
        metadata: dict describing the region of interest and its layers. See `data/metadata`
            for examples.

    Returns: dict whose keys are the regions names from `metadata` and whose values
        are boolean masks of the corresponding regions in `annotated_volume`.
    """
    layers = create_layered_volume(annotated_volume, region_map, metadata)

    return {name: layers == i for (i, name) in enumerate(metadata["layers"]["names"], 1)}


def zero_to_nan(field: FloatArray) -> None:
    """
    Turns, in place, the zero vectors of a vector field into NaN vectors.

    Zero vectors are replaced, in place, by vectors with np.nan coordinates.

    Note: This function is used to invalidate zero vectors or zero quaternions as a zero vector
    cannot be used to define a direction or an orientation.
    In addition, it allows the multiplication of an invalid quaternion, i.e., a quaternion with
     NaN coorinates with a vector (the output is a NaN vector) without raising exception.

    Args:
        field: N-dimensional vector field, i.e., numerical array of shape (..., N).
    Raises:
        ValueError if the input field is not of floating point type.
    """
    if not np.issubdtype(field.dtype, np.floating):
        raise ValueError(f"The input field must be of floating point type. Got {field.dtype}.")
    norms = np.linalg.norm(field, axis=-1)
    # pylint: disable=unsupported-assignment-operation
    field[norms == 0] = np.nan


def normalize(vector_field: FloatArray):
    """
    Normalize in place a vector field wrt to the Euclidean norm.

    Zero vectors are turned into vectors with np.nan coordinates
    silently.
    NaN vectors are unchanged and warnings are kept silent.

    Args:
        vector_field: vector field of floating point type and of shape (..., N)
         where N is the number of vector components.
    """
    norm = np.linalg.norm(vector_field, axis=-1)
    with np.errstate(invalid="ignore"):  # NaNs are expected
        norm = np.where(norm > 0, norm, 1.0)
    vector_field /= norm[..., np.newaxis]
    zero_to_nan(vector_field)


def normalized(vector_field: NumericArray):
    """
    Normalize a vector field wrt to the Euclidean norm.

    Zero vectors are turned into vectors with np.nan coordinates
    silently.

    Args:
        vector_field: vector field of floating point type and of shape (..., N)
         where N is the number of vector components.
    Return:
        normalized_:
            vector field of unit vectors of the same shape and the same type as `vector_field`.
    """
    with np.errstate(invalid="ignore"):
        normalized_ = voxcell.math_utils.normalize(vector_field)
        zero_to_nan(normalized_)
        return normalized_
