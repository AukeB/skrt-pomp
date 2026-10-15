"""Module for testing waveform.py"""

import numpy as np
import pytest

from src.skrt_pomp.errors import InvalidAudioParameterError
from src.skrt_pomp.waveform import (
    NES_DUTY_12_5,
    NES_DUTY_25,
    NES_DUTY_50,
    NES_DUTY_75,
    make_pulse_wave,
    make_time_axis,
    make_noise_wave,
    make_triangle_wave,
)


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


# Testing the "make_pulse_wave" function.


@pytest.mark.parametrize(
    "duty", [NES_DUTY_12_5, NES_DUTY_25, NES_DUTY_50, NES_DUTY_75]
)
def test_make_pulse_wave_fraction_high_matches_duty(duty: float) -> None:
    """Over whole cycles, the share of high samples equals the duty."""
    time_axis = make_time_axis(1.0, 8000)
    samples = make_pulse_wave(100.0, time_axis, duty)
    high_fraction = np.mean(samples > 0)
    assert high_fraction == pytest.approx(duty, abs=0.001)


def test_make_pulse_wave_only_takes_two_values() -> None:
    """Every sample is either +1 or -1."""
    time_axis = make_time_axis(0.1, 44100)
    samples = make_pulse_wave(440.0, time_axis, NES_DUTY_50)
    np.testing.assert_array_equal(np.unique(samples), [-1.0, 1.0])


def test_make_pulse_wave_starts_high() -> None:
    """Each cycle begins high, so the first sample is +1."""
    time_axis = make_time_axis(0.01, 44100)
    samples = make_pulse_wave(440.0, time_axis, NES_DUTY_25)
    assert samples[0] == 1.0


def test_make_pulse_wave_has_one_sample_per_time_point() -> None:
    """The output has the same length as the time axis."""
    time_axis = make_time_axis(0.5, 44100)
    samples = make_pulse_wave(220.0, time_axis, NES_DUTY_50)
    assert samples.size == time_axis.size


@pytest.mark.parametrize(("frequency", "duty"), [(0.0, 0.5), (-440.0, 0.5), (440.0, -0.1), (440.0, 1.1)])
def test_make_pulse_wave_rejects_invalid_parameters(frequency: float, duty: float) -> None:
    """A frequency that is not above zero, or a duty outside 0 to 1, raises an error."""
    time_axis = make_time_axis(0.1, 44100)
    with pytest.raises(InvalidAudioParameterError):
        make_pulse_wave(frequency, time_axis, duty)


# Testing the "make_triangle_wave" function.


def test_make_triangle_wave_stays_within_plus_minus_one() -> None:
    """Every sample lies between -1 and +1."""
    time_axis = make_time_axis(1.0, 8000)
    samples = make_triangle_wave(100.0, time_axis)
    assert np.all(samples >= -1.0)
    assert np.all(samples <= 1.0)


def test_make_triangle_wave_hits_peaks_and_trough() -> None:
    """The wave starts at +1, reaches -1 halfway through, and crosses zero at a quarter cycle."""
    time_axis = make_time_axis(0.01, 8000)
    samples = make_triangle_wave(100.0, time_axis)
    assert samples[0] == pytest.approx(1.0)
    assert samples[40] == pytest.approx(-1.0)
    assert samples[20] == pytest.approx(0.0)


@pytest.mark.parametrize("frequency", [0.0, -440.0])
def test_make_triangle_wave_rejects_invalid_frequency(frequency: float) -> None:
    """A frequency that is not above zero raises an error."""
    time_axis = make_time_axis(0.1, 44100)
    with pytest.raises(InvalidAudioParameterError):
        make_triangle_wave(frequency, time_axis)


# Testing the "make_noise_wave" function.


def test_make_noise_wave_has_one_sample_per_time_point() -> None:
    """The output has the same length as the time axis."""
    time_axis = make_time_axis(0.5, 44100)
    samples = make_noise_wave(time_axis, seed=1)
    assert samples.size == time_axis.size


def test_make_noise_wave_is_repeatable_for_same_seed() -> None:
    """Two calls with the same seed give identical samples."""
    time_axis = make_time_axis(0.1, 44100)
    first = make_noise_wave(time_axis, seed=7)
    second = make_noise_wave(time_axis, seed=7)
    np.testing.assert_array_equal(first, second)


def test_make_noise_wave_differs_for_different_seeds() -> None:
    """Different seeds give different samples."""
    time_axis = make_time_axis(0.1, 44100)
    first = make_noise_wave(time_axis, seed=1)
    second = make_noise_wave(time_axis, seed=2)
    assert not np.array_equal(first, second)


def test_make_noise_wave_stays_within_plus_minus_one() -> None:
    """Every sample lies between -1 and +1."""
    time_axis = make_time_axis(1.0, 44100)
    samples = make_noise_wave(time_axis, seed=3)
    assert np.all(samples >= -1.0)
    assert np.all(samples <= 1.0)


def test_make_noise_wave_has_roughly_zero_mean_and_uniform_spread() -> None:
    """Over a second of noise, the mean is near zero and the spread matches a uniform distribution."""
    time_axis = make_time_axis(1.0, 44100)
    samples = make_noise_wave(time_axis, seed=4)
    assert np.mean(samples) == pytest.approx(0.0, abs=0.01)
    assert np.std(samples) == pytest.approx(1 / np.sqrt(3), abs=0.01)
