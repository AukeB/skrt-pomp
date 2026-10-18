"""Module for running the main repository workflow."""

import numpy as np
import sounddevice as sd

from skrt_pomp.pitch import name_to_frequency
from skrt_pomp.waveform import (
    NES_DUTY_50,
    make_noise_wave,
    make_pulse_wave,
    make_time_axis,
    make_triangle_wave,
)

SAMPLE_RATE = 44100
BPM = 100
SIXTEENTH_NOTE_SECONDS = 60 / BPM / 4
SAMPLES_PER_SIXTEENTH = round(SIXTEENTH_NOTE_SECONDS * SAMPLE_RATE)
RIFF_NOTES = ["F#2"] * 16 + ["C#2"] * 16 + ["E2"] * 16 + ["B1"] * 16
LEAD_VOLUME = 0.25
BASS_VOLUME = 1
SNARE_VOLUME = 0.5
SNARE_OFFSET = 4
SNARE_PERIOD = 8
SNARE_DURATION_SECONDS = 0.1
SNARE_DECAY = 25
SNARE_SEED = 0
FADE_SECONDS = 0.003


def _apply_fade(samples: np.ndarray) -> np.ndarray:
    """
    Ramp a note in and out so neighbouring notes join without a click.

    Args:
        samples (np.ndarray): The note as audio samples.

    Returns:
        faded (np.ndarray): The note with a short fade at each end.
    """

    fade_samples = round(FADE_SECONDS * SAMPLE_RATE)
    ramp = np.linspace(0.0, 1.0, fade_samples)
    faded = samples.copy()
    faded[:fade_samples] *= ramp
    faded[-fade_samples:] *= ramp[::-1]

    return faded


def _render_note(name: str) -> np.ndarray:
    """
    Render one sixteenth note as a pulse wave.

    Args:
        name (str): The note name, such as "F#4".

    Returns:
        samples (np.ndarray): The note as audio samples.
    """

    frequency = name_to_frequency(name)
    time_axis = make_time_axis(SIXTEENTH_NOTE_SECONDS, SAMPLE_RATE)
    samples = LEAD_VOLUME * make_pulse_wave(frequency, time_axis, NES_DUTY_50)
    faded = _apply_fade(samples)

    return faded


def _render_bass_note(name: str) -> np.ndarray:
    """
    Render one sixteenth note of bass as a triangle wave.

    Args:
        name (str): The note name, such as "F#2".

    Returns:
        samples (np.ndarray): The note as audio samples.
    """

    frequency = name_to_frequency(name)
    time_axis = make_time_axis(SIXTEENTH_NOTE_SECONDS, SAMPLE_RATE)
    samples = BASS_VOLUME * make_triangle_wave(frequency, time_axis)
    faded = _apply_fade(samples)

    return faded


def _render_snare_hit() -> np.ndarray:
    """
    Render one snare hit as noise that decays quickly.

    Returns:
        hit (np.ndarray): The snare hit as audio samples.
    """

    time_axis = make_time_axis(SNARE_DURATION_SECONDS, SAMPLE_RATE)
    noise = make_noise_wave(time_axis, seed=SNARE_SEED)
    envelope = np.exp(-SNARE_DECAY * time_axis)
    hit = SNARE_VOLUME * noise * envelope

    return hit


def _render_snare(total_samples: int) -> np.ndarray:
    """
    Place a snare hit on the backbeat of every bar.

    Args:
        total_samples (int): The length of the whole riff in samples.

    Returns:
        snare (np.ndarray): The snare track, the same length as the riff.
    """

    snare = np.zeros(total_samples)
    hit = _render_snare_hit()

    for index in range(len(RIFF_NOTES)):
        if index % SNARE_PERIOD == SNARE_OFFSET:
            start = index * SAMPLES_PER_SIXTEENTH
            snare[start : start + hit.size] = hit

    return snare


def _render_riff() -> np.ndarray:
    """
    Render the lead, bass, and snare tracks and mix them together.

    Returns:
        riff (np.ndarray): The whole riff as audio samples.
    """

    lead_notes = [_render_note(name) for name in RIFF_NOTES]
    lead = np.concatenate(lead_notes)
    bass_notes = [_render_bass_note(name) for name in RIFF_NOTES]
    bass = np.concatenate(bass_notes)
    snare = _render_snare(lead.size)
    riff = lead + bass + snare

    return riff


def main() -> None:
    """Play the opening riff of Dean Town through the speakers."""
    riff = _render_riff()

    sd.play(riff, SAMPLE_RATE)
    sd.wait()


if __name__ == "__main__":
    main()
