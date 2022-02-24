"""types used across atlas-* packages"""
from typing import TYPE_CHECKING

# pylint: disable=invalid-name
# spack uses numpy 1.19, which doesn't have typing; so we make an alias here
#   so we can ignore the problem for now, and change to `from numpy.typing import NDArray`
#   in the future
if TYPE_CHECKING:
    from typing import Union

    import numpy as np
    from numpy.typing import NDArray

    FloatArray = NDArray[np.floating]

    BoolArray = NDArray[np.bool_]
    SignedIntArray = NDArray[np.signedinteger]
    UnsignedIntArray = NDArray[np.unsignedinteger]
    NumericArray = Union[BoolArray, NDArray[np.number]]

    AnnotationT = NDArray[np.integer]
else:
    FloatArray = None

    BoolArray = None
    SignedIntArray = None
    UnsignedIntArray = None
    NumericArray = None

    AnnotationT = None
# pylint: enable=invalid-name
