"""Test finding of grains."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import numpy as np
import numpy.typing as npt
import pytest

from topostats.grains import Grains
from topostats.io import dict_almost_equal

# Pylint returns this error for from skimage.filters import gaussian
# pylint: disable=no-name-in-module
# pylint: disable=too-many-arguments
# pylint: disable=too-many-lines

LOGGER = logging.getLogger(__name__)
LOGGER.propagate = True

# Specify the absolute and relattive tolerance for floating point comparison
TOLERANCE = {"atol": 1e-07, "rtol": 1e-07}


grain_array = np.array(
    [
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 0, 0, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [0, 3, 3, 0, 0, 0, 0, 0, 2, 2],
        [3, 3, 3, 3, 3, 0, 0, 2, 2, 2],
    ]
)

grain_array2 = np.array(
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 2, 2, 0, 0, 0, 0, 0, 1, 1],
        [2, 2, 2, 2, 2, 0, 0, 1, 1, 1],
    ]
)

grain_array3 = np.array(
    [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
)

grain_array4 = np.array(
    [
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
)


@pytest.mark.parametrize(
    ("area_thresh_nm", "expected"),
    [([None, None], grain_array), ([None, 32], grain_array2), ([12, 24], grain_array3), ([32, 44], grain_array4)],
)
def test_known_array_threshold(area_thresh_nm, expected) -> None:
    """Tests that arrays are thresholded on size as expected."""
    grains = Grains(image=np.zeros((10, 6)), filename="xyz", pixel_to_nm_scaling=2)
    assert (grains.area_thresholding(grain_array, area_thresh_nm) == expected).all()


# def test_random_grains(random_grains: Grains, caplog) -> None:
#     """Test errors raised when processing images without grains."""
#     # FIXME : I can see for myself that the error message is logged but the assert fails as caplog.text is empty?
#     # assert "No gains found." in caplog.text
#     assert True


def test_remove_small_objects():
    """Test the remove_small_objects method of the Grains class."""
    grains_object = Grains(
        image=None,
        filename="",
        pixel_to_nm_scaling=1.0,
    )

    test_img = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 3, 3, 0],
            [0, 0, 1, 0, 3, 3, 0],
            [0, 0, 0, 0, 0, 3, 0],
            [0, 2, 0, 2, 0, 3, 0],
            [0, 2, 2, 2, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )

    expected = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )

    grains_object.minimum_grain_size = 5
    result = grains_object.remove_small_objects(test_img)

    np.testing.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    ("binary_image", "minimum_size_px", "minimum_bbox_size_px", "expected_image"),
    [
        pytest.param(
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0],
                    [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    [0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                    [0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            8,
            4,
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
        )
    ],
)
def test_remove_objects_too_small_to_process(
    binary_image: npt.NDArray, minimum_size_px: int, minimum_bbox_size_px: int, expected_image: npt.NDArray
) -> None:
    """Test the remove_objects_too_small_to_process method of the Grains class."""
    grains_object = Grains(
        image=np.array([[0, 0], [0, 0]]),
        filename="",
        pixel_to_nm_scaling=1.0,
    )

    result = grains_object.remove_objects_too_small_to_process(
        image=binary_image, minimum_size_px=minimum_size_px, minimum_bbox_size_px=minimum_bbox_size_px
    )

    np.testing.assert_array_equal(result, expected_image)


@pytest.mark.parametrize(
    ("test_labelled_image", "area_thresholds", "expected"),
    [
        (
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 0, 3, 3, 0],
                    [0, 0, 1, 0, 3, 3, 0],
                    [0, 0, 0, 0, 0, 3, 0],
                    [0, 2, 0, 2, 0, 3, 0],
                    [0, 2, 2, 2, 0, 3, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            [4.0, 6.0],
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 0, 1, 0, 0, 0],
                    [0, 1, 1, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                ]
            ),
        ),
        (
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 0, 3, 3, 0],
                    [0, 0, 1, 0, 3, 3, 0],
                    [0, 0, 0, 0, 0, 3, 0],
                    [0, 2, 0, 2, 0, 3, 0],
                    [0, 2, 2, 2, 0, 3, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            [None, None],
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 0, 3, 3, 0],
                    [0, 0, 1, 0, 3, 3, 0],
                    [0, 0, 0, 0, 0, 3, 0],
                    [0, 2, 0, 2, 0, 3, 0],
                    [0, 2, 2, 2, 0, 3, 0],
                    [0, 0, 0, 0, 0, 0, 0],
                ]
            ),
        ),
    ],
)
def test_area_thresholding(test_labelled_image, area_thresholds, expected):
    """Test the area_thresholding() method of the Grains class."""
    grains_object = Grains(
        image=None,
        filename="",
        pixel_to_nm_scaling=1.0,
    )

    result = grains_object.area_thresholding(test_labelled_image, area_thresholds=area_thresholds)

    np.testing.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    ("remove_edge_intersecting_grains", "expected_number_of_grains"),
    [
        (True, 6),
        (False, 9),
    ],
)
def test_remove_edge_intersecting_grains(
    grains_config: dict, remove_edge_intersecting_grains: bool, expected_number_of_grains: int
) -> None:
    """Test that Grains successfully does and doesn't remove edge intersecting grains."""
    # Ensure that a sensible number of grains are found
    grains_config["remove_edge_intersecting_grains"] = remove_edge_intersecting_grains
    grains_config["threshold_absolute"]["above"] = 1.0
    grains_config["threshold_method"] = "absolute"
    grains_config["smallest_grain_size_nm2"] = 20
    grains_config["absolute_area_threshold"]["above"] = [20, 10000000]

    grains = Grains(
        image=np.load("./tests/resources/minicircle_cropped_flattened.npy"),
        filename="minicircle_cropped_flattened",
        pixel_to_nm_scaling=0.4940029296875,
        **grains_config,
    )
    grains.find_grains()
    number_of_grains = len(grains.region_properties["above"])

    assert number_of_grains == expected_number_of_grains


# Find grains without unet
@pytest.mark.parametrize(
    (
        "image",
        "pixel_to_nm_scaling",
        "threshold_method",
        "otsu_threshold_multiplier",
        "threshold_std_dev",
        "threshold_absolute",
        "absolute_area_threshold",
        "direction",
        "smallest_grain_size_nm2",
        "remove_edge_intersecting_grains",
        "expected_grain_mask",
        "expected_labelled_regions",
    ),
    [
        pytest.param(
            np.array(
                [
                    [0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2],
                    [0.2, 1.1, 1.0, 1.2, 0.2, 0.1, 1.5, 1.6, 1.7, 0.1],
                    [0.1, 1.1, 0.2, 1.0, 0.1, 0.2, 1.6, 0.2, 1.6, 0.2],
                    [0.2, 1.0, 1.1, 1.1, 0.2, 0.1, 1.6, 1.5, 1.5, 0.1],
                    [0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2],
                    [1.5, 1.5, 0.2, 1.5, 1.5, 0.1, 2.0, 1.9, 1.8, 0.1],
                    [0.1, 0.1, 0.2, 0.0, 0.0, 0.2, 0.1, 0.2, 1.7, 0.2],
                    [0.2, 1.5, 1.5, 0.1, 0.2, 0.1, 0.2, 0.1, 1.6, 0.1],
                    [0.1, 0.1, 1.5, 0.1, 1.5, 0.2, 1.3, 1.4, 1.5, 0.2],
                    [0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
                ]
            ),
            1.0,
            "absolute",
            None,
            None,
            {"above": 0.9, "below": 0.0},
            {"above": [1, 10000000], "below": [1, 10000000]},
            "above",
            1,
            True,
            # Move axis required to force a (10, 10, 2) shape
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
                            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
                            [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 1, 0, 6, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ],
                    ),
                ],
                axis=-1,
            ).astype(bool),
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 0, 2, 0, 1, 1, 0, 3, 0, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 0, 2, 2, 2, 0],
                            [0, 1, 0, 1, 0, 0, 2, 0, 2, 0],
                            [0, 1, 1, 1, 0, 0, 2, 2, 2, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 3, 3, 0, 4, 4, 4, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
                            [0, 5, 5, 0, 0, 0, 0, 0, 4, 0],
                            [0, 0, 5, 0, 6, 0, 4, 4, 4, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ],
                    ),
                ],
                axis=-1,
            ).astype(np.int32),
            id="absolute, above 0.9, remove edge, smallest grain 1",
        ),
        pytest.param(
            np.array(
                [
                    [0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2],
                    [0.2, 1.1, 1.0, 1.2, 0.2, 0.1, 1.5, 1.6, 1.7, 0.1],
                    [0.1, 1.1, 0.2, 1.0, 0.1, 0.2, 1.6, 0.2, 1.6, 0.2],
                    [0.2, 1.0, 1.1, 1.1, 0.2, 0.1, 1.6, 1.5, 1.5, 0.1],
                    [0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2],
                    [1.5, 1.5, 0.2, 1.5, 1.5, 0.1, 2.0, 1.9, 1.8, 0.1],
                    [0.1, 0.1, 0.2, 0.0, 0.0, 0.2, 0.1, 0.2, 1.7, 0.2],
                    [0.2, 1.5, 1.5, 0.1, 0.2, 0.1, 0.2, 0.1, 1.6, 0.1],
                    [0.1, 0.1, 1.5, 0.1, 1.5, 0.2, 1.3, 1.4, 1.5, 0.2],
                    [0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.1],
                ]
            ),
            1.0,
            "absolute",
            None,
            None,
            {"above": 0.9, "below": 0.0},
            {"above": [1, 10000000], "below": [1, 10000000]},
            "above",
            2,
            False,
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
                            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
                            [0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [1, 1, 0, 1, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 1, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ],
                    ),
                ],
                axis=-1,
            ).astype(bool),
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 0, 2, 0, 1, 1, 0, 3, 0, 1],
                            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 0, 1],
                            [1, 1, 0, 1, 1, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 0, 2, 2, 2, 0],
                            [0, 1, 0, 1, 0, 0, 2, 0, 2, 0],
                            [0, 1, 1, 1, 0, 0, 2, 2, 2, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [3, 3, 0, 4, 4, 0, 5, 5, 5, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 5, 0],
                            [0, 6, 6, 0, 0, 0, 0, 0, 5, 0],
                            [0, 0, 6, 0, 0, 0, 5, 5, 5, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ],
                    ),
                ],
                axis=-1,
            ).astype(np.int32),
            id="absolute, above 0.9, no remove edge, smallest grain 2",
        ),
    ],
)
def test_find_grains(
    image: npt.NDArray[np.float32],
    pixel_to_nm_scaling: float,
    threshold_method: str,
    otsu_threshold_multiplier: float,
    threshold_std_dev: dict,
    threshold_absolute: dict,
    absolute_area_threshold: dict,
    direction: str,
    smallest_grain_size_nm2: int,
    remove_edge_intersecting_grains: bool,
    expected_grain_mask: npt.NDArray[np.int32],
    expected_labelled_regions: npt.NDArray[np.int32],
) -> None:
    """Test the find_grains method of the Grains class."""
    # Initialise the grains object
    grains_object = Grains(
        image=image,
        filename="test_image",
        pixel_to_nm_scaling=pixel_to_nm_scaling,
        unet_config=None,
        threshold_method=threshold_method,
        otsu_threshold_multiplier=otsu_threshold_multiplier,
        threshold_std_dev=threshold_std_dev,
        threshold_absolute=threshold_absolute,
        absolute_area_threshold=absolute_area_threshold,
        direction=direction,
        smallest_grain_size_nm2=smallest_grain_size_nm2,
        remove_edge_intersecting_grains=remove_edge_intersecting_grains,
    )

    # Override grains' minimum grain size just for this test to allow for small grains in the test image
    grains_object.minimum_grain_size_px = 1
    grains_object.minimum_bbox_size_px = 1

    grains_object.find_grains()

    result_removed_small_objects = grains_object.directions[direction]["removed_small_objects"]
    result_labelled_regions = grains_object.directions[direction]["labelled_regions_02"]

    assert result_removed_small_objects.shape == expected_grain_mask.shape
    assert result_removed_small_objects.dtype == expected_grain_mask.dtype
    np.testing.assert_array_equal(result_removed_small_objects, expected_grain_mask)

    assert result_labelled_regions.shape == expected_labelled_regions.shape
    assert result_labelled_regions.dtype == expected_labelled_regions.dtype
    np.testing.assert_array_equal(result_labelled_regions, expected_labelled_regions)


# Find grains with unet - needs mocking
@pytest.mark.parametrize(
    ("image", "expected_removed_small_objects_tensor", "expected_labelled_regions_tensor"),
    [
        pytest.param(
            # Image
            np.array(
                [
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.2, 0.2, 0.1],
                    [0.1, 1.1, 1.2, 1.0, 0.1, 1.1, 0.2, 1.1, 0.2],
                    [0.2, 1.2, 1.1, 1.3, 0.2, 1.2, 0.1, 0.2, 0.2],
                    [0.1, 1.0, 1.2, 1.2, 0.1, 1.1, 1.2, 1.1, 0.1],
                    [0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
                ]
            ),
            # Expected removed small objects tensor
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 1, 0, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 1, 0, 1, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0],
                            [0, 1, 1, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            # Expected labelled regions tensor
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 1, 0, 1],
                            [1, 0, 2, 0, 1, 0, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 2, 0, 3, 0],
                            [0, 1, 0, 1, 0, 2, 0, 0, 0],
                            [0, 1, 1, 1, 0, 2, 2, 2, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(int),
            id="unet, 5x5, multi class, 3 grains",
        ),
        pytest.param(
            # Image
            np.array(
                [
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.2, 0.2, 0.1],
                    [0.1, 0.1, 0.2, 0.0, 0.1, 0.1, 0.2, 0.1, 0.2],
                    [0.2, 0.2, 0.1, 0.3, 0.2, 0.2, 0.1, 0.2, 0.2],
                    [0.1, 0.0, 0.2, 0.2, 0.1, 0.1, 0.2, 0.1, 0.1],
                    [0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
                ]
            ),
            # Expected removed small objects tensor
            np.stack(
                [
                    np.ones((9, 9)),
                    np.zeros((9, 9)),
                ],
                axis=-1,
            ).astype(bool),
            # Expected labelled regions tensor
            np.stack(
                [
                    np.ones((9, 9)),
                    np.zeros((9, 9)),
                ],
                axis=-1,
            ),
            id="unet, 5x5, no grains",
        ),
    ],
)
def test_find_grains_unet(
    mock_model_5_by_5_single_class: MagicMock,
    image: npt.NDArray[np.float32],
    expected_removed_small_objects_tensor: npt.NDArray[np.bool_],
    expected_labelled_regions_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the find_grains method of the Grains class with a unet model."""
    with patch("keras.models.load_model") as mock_load_model:
        mock_load_model.return_value = mock_model_5_by_5_single_class

        # Initialise the grains object
        grains_object = Grains(
            image=image,
            filename="test_image",
            pixel_to_nm_scaling=1.0,
            unet_config={
                "model_path": "dummy_model_path",
                "confidence": 0.5,
                "model_input_shape": (None, 5, 5, 1),
                "upper_norm_bound": 1.0,
                "lower_norm_bound": 0.0,
                "grain_crop_padding": 1,
            },
            threshold_method="absolute",
            threshold_absolute={"above": 0.9, "below": 0.0},
            absolute_area_threshold={"above": [1, 10000000], "below": [1, 10000000]},
            direction="above",
            smallest_grain_size_nm2=1,
            remove_edge_intersecting_grains=True,
        )

        # Override grains' minimum grain size just for this test to allow for small grains in the test image
        grains_object.minimum_grain_size_px = 1
        grains_object.minimum_bbox_size_px = 1

        grains_object.find_grains()

        result_removed_small_objects = grains_object.directions["above"]["removed_small_objects"]
        result_labelled_regions = grains_object.directions["above"]["labelled_regions_02"]

        assert expected_removed_small_objects_tensor.shape == (9, 9, 2)
        assert expected_labelled_regions_tensor.shape == (9, 9, 2)

        assert result_removed_small_objects.shape == expected_removed_small_objects_tensor.shape
        assert result_labelled_regions.shape == expected_labelled_regions_tensor.shape

        np.testing.assert_array_equal(result_removed_small_objects, expected_removed_small_objects_tensor)
        np.testing.assert_array_equal(result_labelled_regions, expected_labelled_regions_tensor)


@pytest.mark.parametrize(
    (
        "image",
        "unet_config",
        "traditional_threshold_labelled_regions",
        "expected_boolean_mask_tensor",
        "expected_labelled_regions_tensor",
    ),
    [
        pytest.param(
            # Image
            np.array(
                [
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.2, 0.2, 0.1],
                    [0.1, 1.1, 1.2, 1.0, 0.1, 1.1, 0.2, 1.1, 0.2],
                    [0.2, 1.2, 1.1, 1.3, 0.2, 1.2, 0.1, 0.2, 0.2],
                    [0.1, 1.0, 1.2, 1.2, 0.1, 1.1, 1.2, 1.1, 0.1],
                    [0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
                    [0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
                ]
            ),
            # Unet config
            {
                "model_path": "dummy_model_path",
                "confidence": 0.5,
                "model_input_shape": (None, 5, 5, 1),
                "upper_norm_bound": 1.0,
                "lower_norm_bound": 0.0,
                "grain_crop_padding": 1,
            },
            # Traditional thresholding labelled regions
            # This has the centre pixel filled in, representing a feature that is impossible to segment
            # with just thresholding. The U-Net is simulated to be able to recognise that there should be a
            # hole in the grain and thus improves the mask.
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0, 2, 0, 3, 0],
                    [0, 1, 1, 1, 0, 2, 0, 0, 0],
                    [0, 1, 1, 1, 0, 2, 2, 2, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            # Expected boolean mask tensor
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 1, 0, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 1, 0, 1, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0],
                            [0, 1, 1, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(np.bool_),
            # Expected labelled regions tensor
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 1, 0, 1],
                            [1, 0, 2, 0, 1, 0, 1, 1, 1],
                            [1, 0, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 2, 0, 3, 0],
                            [0, 1, 0, 1, 0, 2, 0, 0, 0],
                            [0, 1, 1, 1, 0, 2, 2, 2, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(np.int32),
            id="unet, 5x5, multi class, 3 grains",
        ),
        pytest.param(
            # Image
            np.array(
                [
                    [0.1, 0.2, 0.1, 0.2, 0.1],
                    [0.2, 0.1, 1.1, 0.1, 0.2],
                    [0.1, 1.1, 1.1, 1.1, 0.1],
                    [0.2, 0.1, 1.1, 0.1, 0.2],
                    [0.1, 0.2, 0.1, 0.2, 0.1],
                ]
            ),
            # U-Net config
            {
                "model_path": "dummy_model_path",
                "confidence": 0.5,
                "model_input_shape": (None, 5, 5, 1),
                "upper_norm_bound": 1.0,
                "lower_norm_bound": 0.0,
                "grain_crop_padding": 1,
            },
            # Traditional thresholding labelled regions
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
            # Expected boolean mask tensor
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            # Expected labelled regions tensor
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            id="unet, 5x5, traditional detects grains but unet doesn't. tests for empty unet predictions.",
        ),
    ],
)
def test_improve_grain_segmentation_unet(
    mock_model_5_by_5_single_class: MagicMock,
    image: npt.NDArray[np.float32],
    unet_config: dict[str, str | int | float | tuple[int | None, int, int, int]],
    traditional_threshold_labelled_regions: npt.NDArray[np.int32],
    expected_boolean_mask_tensor: npt.NDArray[np.bool_],
    expected_labelled_regions_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the improve_grain_segmentation method of the Grains class with a unet model."""
    with patch("keras.models.load_model") as mock_load_model:
        mock_load_model.return_value = mock_model_5_by_5_single_class

        result_boolean_masks_tensor, result_labelled_regions_tensor = Grains.improve_grain_segmentation_unet(
            filename="test_image",
            direction="above",
            unet_config=unet_config,
            image=image,
            labelled_grain_regions=traditional_threshold_labelled_regions,
        )

        assert result_boolean_masks_tensor.shape == expected_boolean_mask_tensor.shape
        assert result_labelled_regions_tensor.shape == expected_labelled_regions_tensor.shape
        np.testing.assert_array_equal(result_boolean_masks_tensor, expected_boolean_mask_tensor)
        np.testing.assert_array_equal(result_labelled_regions_tensor, expected_labelled_regions_tensor)


@pytest.mark.parametrize(
    ("labelled_image", "expected_labelled_image"),
    [
        pytest.param(
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            id="empty array",
        ),
        pytest.param(
            np.array(
                [
                    [0, 1, 1, 1, 0, 2, 2, 0],
                    [0, 1, 1, 1, 0, 2, 2, 0],
                    [0, 0, 0, 0, 0, 2, 2, 0],
                    [0, 3, 3, 3, 0, 2, 2, 0],
                    [0, 3, 3, 3, 0, 0, 0, 0],
                    [0, 3, 3, 0, 0, 4, 4, 0],
                    [0, 0, 3, 0, 0, 4, 4, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0, 0, 0, 0],
                    [0, 1, 1, 0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ).astype(np.bool_),
            id="simple",
        ),
    ],
)
def test_keep_largest_labelled_region(
    labelled_image: npt.NDArray[np.int32], expected_labelled_image: npt.NDArray[np.int32]
) -> None:
    """Test the keep_largest_labelled_region method of the Grains class."""
    result = Grains.keep_largest_labelled_region(labelled_image)

    np.testing.assert_array_equal(result, expected_labelled_image)


@pytest.mark.parametrize(
    ("multi_class_image", "expected_flattened_mask"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 1, 0, 1, 1],
                            [1, 0, 0, 0, 1],
                            [1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 1, 0, 1, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
            id="two class plus background, no overlap in classes",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 1, 0, 1, 1],
                            [1, 0, 0, 0, 1],
                            [1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0],
                            [0, 1, 1, 1, 0],
                            [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
            id="two class plus background, overlap in class 1 and 2",
        ),
    ],
)
def test_flatten_multi_class_tensor(
    multi_class_image: npt.NDArray[np.int32], expected_flattened_mask: npt.NDArray[np.int32]
) -> None:
    """Test the flatten_multi_class_image method of the Grains class."""
    result = Grains.flatten_multi_class_tensor(multi_class_image)
    np.testing.assert_array_equal(result, expected_flattened_mask)


@pytest.mark.parametrize(
    ("grain_mask_tensor", "expected_bounding_boxes"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 0, 1, 1, 0, 1, 1],
                            [1, 1, 1, 0, 0, 1, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            {0: (0, 0, 3, 3), 1: (0, 2, 4, 6), 2: (0, 5, 5, 10)},
        )
    ],
)
def test_get_multi_class_grain_bounding_boxes(grain_mask_tensor: npt.NDArray, expected_bounding_boxes: dict) -> None:
    """Test the get_multi_class_grain_bounding_boxes method of the Grains class."""
    result = Grains.get_multi_class_grain_bounding_boxes(grain_mask_tensor)
    assert dict_almost_equal(result, expected_bounding_boxes, abs_tol=1e-12)


@pytest.mark.parametrize(
    ("grain_mask_tensor", "expected_updated_background_class_image_tensor"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 1, 1, 0, 1, 0, 0, 1, 1, 1],
                            [1, 1, 1, 0, 1, 0, 0, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 0, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 0, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 0, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 1, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
        )
    ],
)
def test_update_background_class(
    grain_mask_tensor: npt.NDArray[np.int32], expected_updated_background_class_image_tensor: npt.NDArray[np.int32]
) -> None:
    """Test the update_background_class method of the Grains class."""
    result = Grains.update_background_class(grain_mask_tensor)
    np.testing.assert_array_equal(result, expected_updated_background_class_image_tensor)


@pytest.mark.parametrize(
    ("single_grain_mask_tensor", "keep_largest_labelled_regions_classes", "expected_result_grain_tensor"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 1, 0, 1, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 1, 0],
                            [0, 1, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 1, 0],
                            [0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [1],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1],
                            [1, 1, 0, 0, 0, 1],
                            [1, 1, 0, 0, 0, 1],
                            [1, 1, 0, 1, 0, 1],
                            [1, 1, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 1, 0],
                            [0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1],
                            [1, 1, 0, 1, 1, 1],
                            [1, 1, 0, 1, 1, 1],
                            [1, 1, 0, 1, 0, 1],
                            [1, 1, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 1, 0],
                            [0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [1],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1],
                            [1, 1, 0, 1, 1, 1],
                            [1, 1, 0, 1, 1, 1],
                            [1, 1, 0, 1, 0, 1],
                            [1, 1, 1, 1, 0, 1],
                            [1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 1, 0],
                            [0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            id="no regions to keep",
        ),
    ],
)
def test_keep_largest_labelled_region_classes(
    single_grain_mask_tensor: npt.NDArray[np.int32],
    keep_largest_labelled_regions_classes: list,
    expected_result_grain_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the keep_largest_labelled_regions method of the Grains class."""
    result = Grains.keep_largest_labelled_region_classes(
        single_grain_mask_tensor=single_grain_mask_tensor,
        keep_largest_labelled_regions_classes=keep_largest_labelled_regions_classes,
    )

    np.testing.assert_array_equal(result, expected_result_grain_tensor)


@pytest.mark.parametrize(
    ("grain_mask_tensor", "padding", "expected_result_grain_crops", "expected_bounding_boxes", "expected_padding"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 0, 1, 0, 0, 0, 0, 1, 1],
                            [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
                            [1, 1, 0, 0, 0, 0, 1, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 1, 1, 1, 1, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 1, 1, 1, 1, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            1,
            [
                np.stack(
                    [
                        np.array(
                            [
                                [1, 1, 1, 1, 1, 1, 1],
                                [1, 0, 0, 1, 1, 1, 1],
                                [1, 0, 0, 1, 1, 1, 1],
                                [1, 0, 0, 1, 1, 1, 1],
                                [1, 1, 0, 0, 0, 0, 1],
                                [1, 1, 1, 1, 1, 1, 1],
                            ]
                        ),
                        np.array(
                            [
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 1, 1, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0, 0],
                                [0, 0, 1, 1, 1, 1, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                            ]
                        ),
                        np.array(
                            [
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                            ],
                        ),
                    ],
                    axis=-1,
                ).astype(bool),
                np.stack(
                    [
                        np.array(
                            [
                                [1, 1, 1, 1, 1, 1, 1],
                                [1, 0, 0, 0, 0, 1, 1],
                                [1, 1, 1, 1, 0, 1, 1],
                                [1, 1, 1, 1, 0, 0, 1],
                                [1, 1, 1, 1, 0, 0, 1],
                                [1, 1, 1, 1, 0, 0, 1],
                                [1, 1, 1, 1, 0, 1, 1],
                                [1, 1, 1, 1, 0, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1],
                            ]
                        ),
                        np.array(
                            [
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 1, 1, 1, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                            ]
                        ),
                        np.array(
                            [
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 1, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0, 0, 0],
                            ]
                        ),
                    ],
                    axis=-1,
                ).astype(bool),
            ],
            [np.array([0, 0, 6, 7]), np.array([1, 3, 10, 10])],
            1,
        ),
    ],
)
def test_get_individual_grain_crops(
    grain_mask_tensor: npt.NDArray[np.int32],
    padding: int,
    expected_result_grain_crops: list[npt.NDArray[np.int32]],
    expected_bounding_boxes: list[npt.NDArray[np.int32]],
    expected_padding: int,
) -> None:
    """Test the get_individual_grain_crops method of the Grains class."""
    result_grain_crops, result_bounding_boxes, result_padding = Grains.get_individual_grain_crops(
        grain_mask_tensor, padding
    )
    np.testing.assert_equal(result_grain_crops, expected_result_grain_crops)
    np.testing.assert_equal(result_bounding_boxes, expected_bounding_boxes)
    np.testing.assert_equal(result_padding, expected_padding)


@pytest.mark.parametrize(
    ("single_grain_mask_tensor", "class_region_number_thresholds", "expected_grain_mask_tensor", "expected_passed"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [[1, 2, None]],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            False,
            id="too few regions in class 1",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [[1, None, 1], [2, 1, 1]],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            False,
            id="too many regions in class 1",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [[1, 2, 2], [2, 1, 1]],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            True,
            id="correct number of regions in all classes",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [[1, None, None], [2, None, None]],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            True,
            id="none bounds",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            True,
            id="no thresholds provided",
        ),
    ],
)
def test_vet_numbers_of_regions_single_grain(
    single_grain_mask_tensor: npt.NDArray[np.int32],
    class_region_number_thresholds: dict,
    expected_grain_mask_tensor: npt.NDArray[np.int32],
    expected_passed: bool,
) -> None:
    """Test the vet_numbers_of_regions method of the Grains class."""
    result_crop, result_passed = Grains.vet_numbers_of_regions_single_grain(
        single_grain_mask_tensor, class_region_number_thresholds
    )
    np.testing.assert_array_equal(result_crop, expected_grain_mask_tensor)
    assert result_passed == expected_passed


@pytest.mark.parametrize(
    ("grain_mask_tensor", "classes_to_convert", "class_touching_threshold", "expected_result_grain_mask_tensor"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            [(2, 1)],
            1,
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                            [0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            [(2, 1)],
            1,
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            id="empty class to convert",
        ),
    ],
)
def test_convert_classes_to_nearby_classes(
    grain_mask_tensor: npt.NDArray[np.int32],
    classes_to_convert: list[tuple[int, int]],
    class_touching_threshold: int,
    expected_result_grain_mask_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the convert_classes_to_nearby_classes method of the Grains class."""
    result_grain_mask_tensor = Grains.convert_classes_to_nearby_classes(
        grain_mask_tensor, classes_to_convert, class_touching_threshold
    )

    np.testing.assert_array_equal(result_grain_mask_tensor, expected_result_grain_mask_tensor)


@pytest.mark.parametrize(
    (
        "grain_mask_tensor",
        "classes",
        "expected_num_connection_regions",
        "expected_intersection_labels",
        "expected_intersection_points",
    ),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            (1, 2),
            3,
            np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                ]
            ),
            {
                1: np.array([[1, 3], [2, 3]]),
                2: np.array([[4, 3], [5, 3]]),
                3: np.array([[7, 3], [8, 3]]),
            },
        )
    ],
)
def test_calculate_region_connection_regions(
    grain_mask_tensor: npt.NDArray[np.int32],
    classes: tuple[int, int],
    expected_num_connection_regions: int,
    expected_intersection_labels: npt.NDArray[np.int32],
    expected_intersection_points: list[tuple[int, int]],
) -> None:
    """Test the calculate_region_connection_regions method of the Grains class."""
    (result_num_connection_regions, result_intersection_labels, result_intersection_points) = (
        Grains.calculate_region_connection_regions(grain_mask_tensor, classes)
    )

    assert result_num_connection_regions == expected_num_connection_regions
    np.testing.assert_array_equal(result_intersection_labels, expected_intersection_labels)
    np.testing.assert_equal(result_intersection_points, expected_intersection_points)


@pytest.mark.parametrize(
    ("grain_mask_tensor", "pixel_to_nm_scaling", "class_conversion_size_thresholds", "expected_grain_mask_tensor"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            1.0,
            [[(1, None, 2), (2, 3)], [(2, None, 1), (2, 3)]],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 1, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            id="switch classes 1 and 2",
        ),
    ],
)
def test_convert_classes_when_too_big_or_small(
    grain_mask_tensor: npt.NDArray[np.int32],
    pixel_to_nm_scaling: float,
    class_conversion_size_thresholds: list[tuple[tuple[int, int], tuple[int, int]]],
    expected_grain_mask_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the convert_classes_when_too_big_or_small method of the Grains class."""
    result_grain_mask_tensor = Grains.convert_classes_when_too_big_or_small(
        grain_mask_tensor, pixel_to_nm_scaling, class_conversion_size_thresholds
    )

    np.testing.assert_array_equal(result_grain_mask_tensor, expected_grain_mask_tensor)


@pytest.mark.parametrize(
    ("grain_mask_tensor", "class_connection_point_thresholds", "expected_pass"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [((1, 2), (4, 5))],
            False,
            id="not enough connection regions",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [((1, 2), (1, 2))],
            False,
            id="too many connection regions",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [((1, 2), (2, 4))],
            True,
            id="correct number of connection regions",
        ),
    ],
)
def test_vet_class_connection_points(
    grain_mask_tensor: npt.NDArray[np.int32],
    class_connection_point_thresholds: dict[tuple[int, int], tuple[int, int]],
    expected_pass: bool,
) -> None:
    """Test the vet_class_connection_points method of the Grains class."""
    result_pass = Grains.vet_class_connection_points(grain_mask_tensor, class_connection_point_thresholds)

    assert result_pass == expected_pass


@pytest.mark.parametrize(
    ("grain_mask_tensor_shape", "grain_crops_dicts", "expected_grain_mask_tensor"),
    [
        pytest.param(
            np.array([12, 12, 3]),
            [
                {
                    "grain_tensor": np.stack(
                        [
                            np.array(
                                [
                                    [1, 1, 1, 1, 1, 1],
                                    [1, 0, 0, 0, 0, 1],
                                    [1, 0, 0, 0, 0, 1],
                                    [1, 0, 0, 0, 0, 1],
                                    [1, 0, 0, 0, 0, 1],
                                    [1, 1, 1, 1, 1, 1],
                                ]
                            ),
                            np.array(
                                [
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 1, 0, 0, 1, 0],
                                    [0, 1, 0, 0, 1, 0],
                                    [0, 1, 1, 1, 1, 0],
                                    [0, 1, 1, 1, 1, 0],
                                    [0, 0, 0, 0, 0, 0],
                                ]
                            ),
                            np.array(
                                [
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 1, 1, 0, 0],
                                    [0, 0, 1, 1, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                ]
                            ),
                        ],
                        axis=-1,
                    ).astype(bool),
                    "bounding_box": (0, 0, 6, 6),
                    "padding": 1,
                },
                {
                    "grain_tensor": np.stack(
                        [
                            np.array(
                                [
                                    [1, 1, 1, 1],
                                    [1, 0, 0, 1],
                                    [1, 0, 0, 1],
                                    [1, 1, 1, 1],
                                ]
                            ),
                            np.array(
                                [
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                    [0, 1, 1, 0],
                                    [0, 0, 0, 0],
                                ]
                            ),
                            np.array(
                                [
                                    [0, 0, 0, 0],
                                    [0, 1, 1, 0],
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                ]
                            ),
                        ],
                        axis=-1,
                    ).astype(bool),
                    "bounding_box": (6, 6, 10, 10),
                    "padding": 1,
                },
            ],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
        )
    ],
)
def test_assemble_grain_mask_tensor_from_crops(
    grain_mask_tensor_shape: npt.NDArray[np.int32],
    grain_crops_dicts: list[dict[str, np.ndarray]],
    expected_grain_mask_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the assemble_grain_mask_tensor_from_crops method of the Grains class."""
    result_grain_mask_tensor = Grains.assemble_grain_mask_tensor_from_crops(grain_mask_tensor_shape, grain_crops_dicts)

    np.testing.assert_array_equal(result_grain_mask_tensor, expected_grain_mask_tensor)


@pytest.mark.parametrize(
    ("grain_mask_tensor", "classes_to_merge", "expected_result_grain_mask_tensor"),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 1, 1, 0, 1, 0],
                            [0, 1, 0, 0, 1, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0],
                            [0, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
            [(1, 2)],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 1, 1, 0, 1, 0],
                            [0, 1, 0, 0, 1, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0],
                            [0, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ),
        )
    ],
)
def test_merge_classes(
    grain_mask_tensor: npt.NDArray[np.int32],
    classes_to_merge: list[tuple[int, int]],
    expected_result_grain_mask_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the merge_classes method of the Grains class."""
    result_grain_mask_tensor = Grains.merge_classes(grain_mask_tensor, classes_to_merge)

    np.testing.assert_array_equal(result_grain_mask_tensor, expected_result_grain_mask_tensor)


@pytest.mark.parametrize(
    (
        "grain_mask_tensor",
        "pixel_to_nm_scaling",
        "class_conversion_size_thresholds",
        "class_size_thresholds",
        "class_region_number_thresholds",
        "nearby_conversion_classes_to_convert",
        "class_touching_threshold",
        "keep_largest_labelled_regions_classes",
        "class_connection_point_thresholds",
        "expected_grain_mask_tensor",
    ),
    [
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            1.0,
            # Class conversion size thresholds - coulndn't come up with a set of params would propagate through
            None,
            # Class size thresholds
            [[1, 3, 1000000]],
            # Class region number thresholds
            [[1, 1, 100]],
            # Nearby conversion classes to convert
            [(2, 3)],
            # Class touching threshold
            1,
            # Keep largest labelled regions classes
            [1, 2, 3],
            # Class connection point thresholds
            [[[1, 2], [1, 1]], [[1, 3], [1, 1]], [[2, 3], [1, 1]]],
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            id="Parameters supplied",
        ),
        pytest.param(
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            1.0,
            # Class conversion size thresholds
            None,
            # Class size thresholds
            None,
            # Class region number thresholds
            None,
            # Nearby conversion classes to convert
            None,
            # Class touching threshold
            1,
            # Keep largest labelled regions classes
            None,
            # Class connection point thresholds
            None,
            np.stack(
                [
                    np.array(
                        [
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                    np.array(
                        [
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        ]
                    ),
                ],
                axis=-1,
            ).astype(bool),
            id="no parameters supplied",
        ),
    ],
)
def test_vet_grains(
    grain_mask_tensor: npt.NDArray[np.int32],
    pixel_to_nm_scaling: float,
    class_conversion_size_thresholds: list[list[int, int, int]] | None,
    class_size_thresholds: list[list[int, int, int]] | None,
    class_region_number_thresholds: list[list[int, int, int]] | None,
    nearby_conversion_classes_to_convert: list[tuple[int, int]] | None,
    class_touching_threshold: int,
    keep_largest_labelled_regions_classes: list[int] | None,
    class_connection_point_thresholds: list[list[int, int, int, int]] | None,
    expected_grain_mask_tensor: npt.NDArray[np.int32],
) -> None:
    """Test the vet_grains function."""
    grain_mask_tensor = Grains.vet_grains(
        grain_mask_tensor=grain_mask_tensor,
        pixel_to_nm_scaling=pixel_to_nm_scaling,
        class_conversion_size_thresholds=class_conversion_size_thresholds,
        class_size_thresholds=class_size_thresholds,
        class_region_number_thresholds=class_region_number_thresholds,
        nearby_conversion_classes_to_convert=nearby_conversion_classes_to_convert,
        class_touching_threshold=class_touching_threshold,
        keep_largest_labelled_regions_classes=keep_largest_labelled_regions_classes,
        class_connection_point_thresholds=class_connection_point_thresholds,
    )

    np.testing.assert_array_equal(grain_mask_tensor, expected_grain_mask_tensor)
