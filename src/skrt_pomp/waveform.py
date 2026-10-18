"""Module for generating waveforms as arrays of audio samples.

Every waveform is built from a time axis, which is made once per sound and
shared by the waveforms that use it. The public functions are:

- make_time_axis(duration, sample_rate): the time of each sample, for example
  make_time_axis(0.5, 44100) gives 22,050 times from 0 to just under 0.5 s.
- make_pulse_wave(frequency, time_axis, duty): a square-like wave that is high
  for the fraction `duty` of each cycle. Use the NES_DUTY_* constants.
- make_triangle_wave(frequency, time_axis): a wave that rises and falls linearly
  once per cycle.
- make_noise_wave(time_axis, seed): random values with no pitch. The same seed
  gives the same samples.

Example:
    >>> time_axis = make_time_axis(0.5, 44100)
    >>> samples = make_pulse_wave(440.0, time_axis, NES_DUTY_50)
"""

import numpy as np

from skrt_pomp.errors import InvalidAudioParameterError

NES_DUTY_12_5 = 0.125
NES_DUTY_25 = 0.25
NES_DUTY_50 = 0.5
NES_DUTY_75 = 0.75


def _validate_frequency(frequency: float) -> None:
    """Check that a frequency is above zero.

    Args:
        frequency (float): The pitch of the wave in Hz.

    Raises:
        InvalidAudioParameterError: If the frequency is not above zero.
    """

    if frequency <= 0:
        raise InvalidAudioParameterError(f"Frequency must be above zero: {frequency}")


def make_time_axis(duration: float, sample_rate: int) -> np.ndarray:
    """Build the time, in seconds, of each sample in a sound.

    Args:
        duration (float): The length of the sound in seconds, zero or more.
        sample_rate (int): The number of samples per second, above zero.

    Returns:
        time_axis (np.ndarray): The time of each sample, starting at 0 and
            spaced 1 / sample_rate apart.

    Raises:
        InvalidAudioParameterError: If the duration is negative or the sample
            rate is not above zero.

    Example:
        >>> make_time_axis(0.5, 4)
        array([0.  , 0.25])
    """

    if duration < 0:
        raise InvalidAudioParameterError(f"Duration must not be negative: {duration}")

    if sample_rate <= 0:
        raise InvalidAudioParameterError(
            f"Sample rate must be above zero: {sample_rate}"
        )

    num_samples = round(duration * sample_rate)
    indices = np.arange(num_samples)
    time_axis = indices / sample_rate

    return time_axis


def make_pulse_wave(frequency: float, time_axis: np.ndarray, duty: float) -> np.ndarray:
    """Build a pulse wave that is high for a fraction of each cycle.

    Args:
        frequency (float): The pitch of the wave in Hz, above zero.
        time_axis (np.ndarray): The time of each sample in seconds, as made by
            make_time_axis.
        duty (float): The fraction of each cycle spent high, from 0 to 1.

    Returns:
        samples (np.ndarray): The wave values, +1 while high and -1 while low.

    Raises:
        InvalidAudioParameterError: If the frequency is not above zero or the
            duty is outside 0 to 1.
    """

    _validate_frequency(frequency)

    if not 0 <= duty <= 1:
        raise InvalidAudioParameterError(f"Duty must be from 0 to 1: {duty}")

    phase = (time_axis * frequency) % 1.0
    high = phase < duty
    samples = np.where(high, 1.0, -1.0)

    return samples


def make_triangle_wave(frequency: float, time_axis: np.ndarray) -> np.ndarray:
    """Build a triangle wave that rises and falls linearly once per cycle.

    Args:
        frequency (float): The pitch of the wave in Hz, above zero.
        time_axis (np.ndarray): The time of each sample in seconds, as made by
            make_time_axis.

    Returns:
        samples (np.ndarray): The wave values from -1 to +1. The wave starts at
            +1, reaches -1 halfway through the cycle, and returns to +1.

    Raises:
        InvalidAudioParameterError: If the frequency is not above zero.
    """

    _validate_frequency(frequency)

    phase = (time_axis * frequency) % 1.0
    samples = 2 * np.abs(2 * phase - 1) - 1

    return samples


def make_noise_wave(time_axis: np.ndarray, seed: int) -> np.ndarray:
    """Build random noise, the hiss used for drums and crashes.

    The same seed always gives the same samples, so the output is repeatable.

    Args:
        time_axis (np.ndarray): The time of each sample in seconds, as made by
            make_time_axis. Only its length is used.
        seed (int): The seed for the random number generator.

    Returns:
        samples (np.ndarray): Random values evenly spread from -1 to +1.
    """

    rng = np.random.default_rng(seed)
    samples = rng.uniform(-1.0, 1.0, time_axis.size)

    return samples
