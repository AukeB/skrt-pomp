"""Module for custom exceptions raised by skrt_pomp."""


class InvalidNoteNameError(ValueError):
    """Raised when a note name cannot be parsed."""


class InvalidAudioParameterError(ValueError):
    """Raised when a duration or sample rate is out of range."""
