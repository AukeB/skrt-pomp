"""Module for converting note names to pitches."""

import re

from skrt_pomp.errors import InvalidNoteNameError

_NOTE_NAME_PATTERN = re.compile(r"([A-G])([#b]?)(-?\d+)")
_MIN_OCTAVE = -1
_MAX_OCTAVE = 9
_SEMITONE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACCIDENTAL_OFFSETS = {"": 0, "#": 1, "b": -1}
_A4_MIDI_NUMBER = 69
_A4_FREQUENCY = 440.0
_MIN_MIDI_NUMBER = 0
_MAX_MIDI_NUMBER = 127


def _get_semitone_offset(letter: str) -> int:
    """Return how many semitones a note letter sits above C in its octave.

    Args:
        letter (str): A note letter from A to G.

    Returns:
        offset (int): The semitone offset, such as 9 for "A".

    Raises:
        InvalidNoteNameError: If the letter is not from A to G.
    """

    if letter not in _SEMITONE_OFFSETS:
        raise InvalidNoteNameError(f"Invalid note letter: {letter!r}")

    offset = _SEMITONE_OFFSETS[letter]

    return offset


def _get_accidental_offset(accidental: str) -> int:
    """Return how many semitones an accidental raises or lowers a note.

    Args:
        accidental (str): "#" for sharp, "b" for flat, or "" for none.

    Returns:
        offset (int): 1 for sharp, -1 for flat, and 0 for none.

    Raises:
        InvalidNoteNameError: If the accidental is not "#", "b", or "".
    """

    if accidental not in _ACCIDENTAL_OFFSETS:
        raise InvalidNoteNameError(f"Invalid accidental: {accidental!r}")

    offset = _ACCIDENTAL_OFFSETS[accidental]

    return offset


def _parse_note_name(name: str) -> tuple[str, str, int]:
    """Split a note name into its letter, accidental, and octave.

    Args:
        name (str): A note name such as "A4", "C#4", or "Bb3".

    Returns:
        parts (tuple[str, str, int]): The letter, accidental, and octave, such
            as ("C", "#", 4). The accidental is "" when there is none.

    Raises:
        InvalidNoteNameError: If the name is not a letter followed by an octave,
            or if the octave is outside the MIDI range of -1 to 9.
    """

    match = _NOTE_NAME_PATTERN.fullmatch(name)

    if match is None:
        raise InvalidNoteNameError(f"Invalid note name: {name!r}")

    letter = match.group(1)
    accidental = match.group(2)
    octave_text = match.group(3)
    octave = int(octave_text)

    if not _MIN_OCTAVE <= octave <= _MAX_OCTAVE:
        raise InvalidNoteNameError(
            f"Octave {octave} is outside {_MIN_OCTAVE} to {_MAX_OCTAVE}: {name!r}"
        )

    parts = (letter, accidental, octave)

    return parts


def _name_to_midi(name: str) -> int:
    """Convert a note name to its MIDI note number.

    Args:
        name (str): A note name such as "A4", "C#5", or "Bb3".

    Returns:
        midi_number (int): The MIDI note number, such as 69 for "A4".

    Raises:
        InvalidNoteNameError: If the name is invalid or its MIDI number falls
            outside 0 to 127.
    """

    letter, accidental, octave = _parse_note_name(name)
    semitone_offset = _get_semitone_offset(letter)
    accidental_offset = _get_accidental_offset(accidental)
    midi_number = (octave + 1) * 12 + semitone_offset + accidental_offset

    if not _MIN_MIDI_NUMBER <= midi_number <= _MAX_MIDI_NUMBER:
        raise InvalidNoteNameError(f"Note {name!r} is outside the MIDI range")

    return midi_number


def _midi_to_frequency(midi_number: int) -> float:
    """Convert a MIDI note number to its frequency in Hz.

    Uses 12-tone equal temperament with A4 (MIDI 69) at 440 Hz.

    Args:
        midi_number (int): The MIDI note number, from 0 to 127.

    Returns:
        frequency (float): The frequency of the note in Hz.
    """

    semitones_from_a4 = midi_number - _A4_MIDI_NUMBER
    frequency = _A4_FREQUENCY * 2 ** (semitones_from_a4 / 12)

    return frequency


def name_to_frequency(name: str) -> float:
    """Convert a note name such as "A4" or "C#5" to its frequency in Hz.

    Args:
        name (str): A note name with a letter, an optional # or b, and an
            octave.

    Returns:
        frequency (float): The frequency of the note in Hz, such as 440.0 for
            "A4".

    Raises:
        InvalidNoteNameError: If the name is invalid or its MIDI number falls
            outside 0 to 127.

    Example:
        >>> name_to_frequency("A4")
        440.0
        >>> round(name_to_frequency("C4"), 2)
        261.63
    """

    midi_number = _name_to_midi(name)
    frequency = _midi_to_frequency(midi_number)

    return frequency
