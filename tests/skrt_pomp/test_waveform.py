"""Module for testing waveform.py"""

import numpy as np
import pytest

from src.skrt_pomp.errors import InvalidAudioParameterError
from src.skrt_pomp.waveform import make_time_axis


# Testing the "make_time_axis" function.


def test_make_time_axis_has_one_entry_per_sample() -> None:
    """A half-second sound at 44100 Hz has 22050 samples."""
    time_axis = make_time_axis(0.5, 44100)
    assert time_axis.size == 22050


def test_make_time_axis_starts_at_zero_and_steps_by_sample_period() -> None:
    """The first sample is at time 0, and each step is one sample period."""
    time_axis = make_time_axis(0.5, 4)
    np.testing.assert_allclose(time_axis, [0.0, 0.25])


def test_make_time_axis_rounds_sample_count() -> None:
    """A duration that is not a whole number of samples is rounded to the nearest."""
    time_axis = make_time_axis(1 / 3, 10)
    assert time_axis.size == 3


def test_make_time_axis_zero_duration_is_empty() -> None:
    """A zero-length sound has no samples."""
    time_axis = make_time_axis(0.0, 44100)
    assert time_axis.size == 0


@pytest.mark.parametrize(("duration", "sample_rate"), [(-0.1, 44100), (0.5, 0), (0.5, -44100)])
def test_make_time_axis_rejects_invalid_parameters(duration: float, sample_rate: int) -> None:
    """A negative duration, or a sample rate that is not above zero, raises an error."""
    with pytest.raises(InvalidAudioParameterError):
        make_time_axis(duration, sample_rate)
