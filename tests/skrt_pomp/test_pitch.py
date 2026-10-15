"""Module for testing pitch.py"""

import pytest

from src.skrt_pomp.errors import InvalidNoteNameError
from src.skrt_pomp.pitch import (
    _get_accidental_offset,
    _get_semitone_offset,
    name_to_frequency,
)


# Testing the "name_to_frequency" function.


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("A4", 440.0),
        ("C4", 261.6255653),
        ("A0", 27.5),
        ("C-1", 8.1757989),
        ("G9", 12543.8539514),
        ("C#5", 554.3653),
        ("Bb3", 233.0819),
        ("Cb4", 246.9417),
        ("B#3", 261.6255653),
    ],
)
def test_name_to_frequency_returns_frequency(name: str, expected: float) -> None:
    """Note names map to their equal-tempered frequencies, including accidentals."""
    assert name_to_frequency(name) == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    "name",
    [
        "H4",
        "A",
        "4A",
        "a4",
        "A4x",
        "",
        "C-2",
        "C10",
        "C##4",
        "Cb",
        "bb3",
        "B9",
        "G#9",
        "Cb-1",
    ],
)
def test_name_to_frequency_rejects_invalid_names(name: str) -> None:
    """Invalid names, and names whose MIDI number is outside 0 to 127, raise an error."""
    with pytest.raises(InvalidNoteNameError):
        name_to_frequency(name)


# Testing the "_get_semitone_offset" function.


@pytest.mark.parametrize(
    ("letter", "expected"),
    [("C", 0), ("D", 2), ("E", 4), ("F", 5), ("G", 7), ("A", 9), ("B", 11)],
)
def test_get_semitone_offset_returns_offset_from_c(letter: str, expected: int) -> None:
    """Each letter maps to its semitone offset above C."""
    assert _get_semitone_offset(letter) == expected


@pytest.mark.parametrize("letter", ["H", "a", ""])
def test_get_semitone_offset_rejects_invalid_letters(letter: str) -> None:
    """Anything other than the letters A to G raises an error."""
    with pytest.raises(InvalidNoteNameError):
        _get_semitone_offset(letter)


# Testing the "_get_accidental_offset" function.


@pytest.mark.parametrize(
    ("accidental", "expected"),
    [("", 0), ("#", 1), ("b", -1)],
)
def test_get_accidental_offset_returns_offset(accidental: str, expected: int) -> None:
    """Sharp raises by one semitone, flat lowers by one, and none leaves it alone."""
    assert _get_accidental_offset(accidental) == expected


@pytest.mark.parametrize("accidental", ["x", "##", "B"])
def test_get_accidental_offset_rejects_invalid_accidentals(accidental: str) -> None:
    """Anything other than "#", "b", or "" raises an error."""
    with pytest.raises(InvalidNoteNameError):
        _get_accidental_offset(accidental)
