"""Module for generating waveforms as arrays of audio samples."""

import numpy as np

from src.skrt_pomp.errors import InvalidAudioParameterError


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
