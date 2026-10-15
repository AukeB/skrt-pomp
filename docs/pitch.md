# pitch

The `pitch` module turns note names that musicians write, such as `A4` or `C#5`, into frequencies in hertz (Hz), which is what a speaker needs to play them. Its single public function is `name_to_frequency`. The other functions in the module are private steps that the public function calls in order:

1. `_parse_note_name` splits the name into a letter, an optional accidental, and an octave, and rejects names that don't have that shape.
2. `_get_semitone_offset` converts the letter into how many semitones it sits above C in its octave.
3. `_get_accidental_offset` converts `#` and `b` into a shift of +1 or -1 semitone.
4. `_name_to_midi` combines the octave, offset, and accidental into a MIDI note number, and rejects numbers outside 0 to 127.
5. `_midi_to_frequency` converts the MIDI number into a frequency, with A4 at 440 Hz.

The goal is that a caller only needs to pass in a readable name, and gets back a frequency it can use to generate a waveform.

### Musical context

**Note names.** Western music names the twelve pitch classes with the letters A to G, with sharps (`#`) and flats (`b`) in between. The letters go up in pitch from C: C, D, E, F, G, A, B, then back to C. Between most neighbouring letters there is a black key on a piano. The black key between C and D can be called C# or Db, which is why the parser accepts both spellings. In this module, `C#4` and `Db4` give the same frequency.

A semitone is the distance between two adjacent keys on a piano, including black keys. E to F and B to C are also one semitone apart, with no black key between them. Sharp raises a note by one semitone and flat lowers it by one. This is why `B#3` and `C4` are the same pitch, and `Cb4` and `B3` are the same pitch.

**Octaves.** The number after the letter is the octave. Each octave runs from C up to the next C, which is twelve semitones. `C4` is the C in the middle of a piano, often called middle C. The module accepts octaves from -1 to 9, which covers the whole MIDI range.

**Pitch and frequency.** A sound is a pressure wave in the air. Its frequency is how many full cycles of that wave happen per second, measured in hertz (Hz). Higher frequency sounds higher. The time for one cycle is the period, which is the inverse of the frequency. A note at 440 Hz completes 440 cycles per second, which is a period of about 2.27 ms.

Pitch is how high or low we hear a sound. Loudness is a different property, set by the amplitude of the wave (how far the pressure swings), and that is not handled in this module. Humans hear roughly 20 Hz to 20 kHz.

Pitch perception is logarithmic. Doubling the frequency raises the note by one octave, so going from 220 Hz to 440 Hz sounds the same distance as going from 440 Hz to 880 Hz, even though the frequency gap is different. Equal-tempered tuning divides the octave into twelve equal ratios, and each semitone multiplies the frequency by 2^(1/12), about 1.0595.

**MIDI.** MIDI (Musical Instrument Digital Interface) is a standard from 1983 for describing musical notes. Its key idea is that every note is identified by an integer from 0 to 127. Each integer is one semitone, so the numbers count up through the keys of a piano. MIDI itself is used to send note events between instruments and software. Here we only use the numbering.

The mapping between names and numbers is:

```
MIDI number = (octave + 1) * 12 + semitone offset + accidental offset
```

For example, `A4` is `(4 + 1) * 12 + 9 + 0 = 69`, and `C#5` is `(5 + 1) * 12 + 0 + 1 = 73`. MIDI 0 is C-1 and MIDI 127 is G9. Middle C, `C4`, is MIDI 60, and A4 is MIDI 69 at 440 Hz.

Some software labels middle C as C3 instead of C4, so the octave number of the same note differs between tools. This module follows the convention where middle C is C4.

**Why go through MIDI numbers.** Integers make music operations simple. Transposing a melody up a fifth is adding 7 to every number, and two spellings of the same key, such as `C#5` and `Db5`, are exactly equal. Chords and intervals are lists of offsets added to a root number. Frequencies are floats, so comparing them is unreliable and repeated multiplication drifts. Converting to Hz is therefore the last step, done once, when the sound is generated.

**Frequency from a MIDI number.** The conversion is:

```
frequency = 440 * 2 ** ((midi_number - 69) / 12)
```

A4 (MIDI 69) is 440 Hz by definition. Each semitone above multiplies the frequency by 2^(1/12), and each semitone below divides it by that amount.
