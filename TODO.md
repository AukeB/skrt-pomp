# TODO

## Pitch (`skrt_pomp/pitch.py`)

Parse names like `C#4` or `Bb3` into Hz, using A4 = 440 Hz and 12-tone equal temperament. This is pure math, so it is easy to test against known values like C4 ≈ 261.63.

- [x] 1. Parse the letter and the octave, for example `A4` → letter `A`, octave `4`.
- [x] 2. Map the letter to a semitone offset within the octave: C=0, D=2, E=4, F=5, G=7, A=9, B=11.
- [x] 3. Handle accidentals: `#` adds 1 semitone and `b` subtracts 1, so `C#4` → 1 and `Bb3` → 10.
- [x] 4. Convert a semitone count to a frequency: `freq = 440 × 2^((midi − 69) / 12)`, where `midi` is the note's MIDI number (A4 = 69).
- [x] 5. Convert a note name to its MIDI number, for example `A4` → 69 and `C#5` → 73. Names whose MIDI number falls outside 0 to 127 are rejected.
- [x] 6. Return a clear error for an invalid name, using an exception in the `errors` module.

## Waveform (`skrt_pomp/waveform.py`)

Functions that turn a frequency and a number of samples into an array, starting with the pulse wave with a duty cycle, then triangle and noise. This is the code we already wrote, moved into tested functions.

- [x] 7. `make_time_axis(duration, sample_rate)` builds the time of each sample. It takes no frequency; each waveform applies its own frequency to the time axis.
- [x] 8. A pulse wave with a duty-cycle argument, tested on the fraction of high samples (for example 25% duty gives about 25% high).
- [x] 9. A triangle wave, tested on its peak values staying within −1 to 1.
- [x] 10. A noise generator with a fixed seed, so tests are repeatable. Later this becomes the LFSR version.

## Score model (`skrt_pomp/score.py`)

- [ ] `Note`, `Track`, and `Score` as dataclasses, with times in integer ticks.

## Grid parser (`skrt_pomp/grid.py`)

- [ ] Reads the tracker text format into a `Score`. This needs the exact column spec, so settle that before writing it.

## Renderer and playback

- [ ] Mix the tracks into one array and play or export it.
