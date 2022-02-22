"""types used across atlas-* packages"""

from typing import Union

import numpy as np
from numpy.typing import NDArray

# pylint: disable=invalid-name
FloatArray = NDArray[np.floating]
BoolArray = NDArray[np.bool_]
NumericArray = Union[BoolArray, NDArray[np.number]]
AnnotationT = NDArray[np.integer]
# pylint: enable=invalid-name
