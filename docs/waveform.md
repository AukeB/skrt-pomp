# waveform

A waveform is the shape of a sound over one cycle. The shape decides the timbre, which is the quality that tells a flute from a trumpet playing the same note. The `waveform` module will turn a frequency and a number of samples into an array of values between -1 and 1, one value per sample. The first waveform is the pulse wave, and its main control is the duty cycle.

## Phase

Every waveform is built from a phase, a number that counts through one cycle. Phase runs from 0 to 1 and then starts again. For a frequency `f`, at time `t` in seconds, the phase is:

```
phase = (t * f) % 1.0
```

At 440 Hz the phase goes through the full range 440 times per second. A waveform is just a rule that turns phase into a value. Everything else in this document follows from that rule.

## Pulse wave

A pulse wave is a square wave that doesn't have to be split evenly. It is high for part of the cycle and low for the rest:

```
value = +1 if phase < duty else -1
```

## Duty cycle

The duty cycle is the fraction of one cycle that the wave spends high. A duty of 0.5 means high for half the cycle and low for half, which is a plain square wave. A duty of 0.25 means high for a quarter of the cycle and low for three quarters.

The NES pulse channels offered four duty values, which are the ones to start with:

| Duty | High for | Sound |
|------|----------|-------|
| 12.5% | 1/8 of each cycle | Thin, nasal, reedy |
| 25% | 1/4 of each cycle | Bright, slightly hollow |
| 50% | 1/2 of each cycle | Full, hollow, the classic square sound |
| 75% | 3/4 of each cycle | Same sound as 25% |

Changing the duty doesn't change the pitch. The frequency sets how often the cycle repeats, and the duty only changes what happens within each cycle.

### Why the duty changes the sound

A repeating wave is a sum of sine waves at whole-number multiples of the fundamental frequency, called harmonics. The duty decides how strong each harmonic is. For a pulse wave with values +1 and -1, the amplitude of harmonic `n` is:

```
amplitude(n) = 4 * |sin(n * pi * duty)| / (n * pi)
```

This formula explains the table:

- **50%:** `sin(n * pi * 0.5)` is zero for every even `n`, so only the odd harmonics remain, with amplitudes of 1/n. This is the classic square wave.
- **25%:** `sin(n * pi * 0.25)` is zero for every multiple of 4, so the 4th, 8th, and so on are missing. The spectrum is different, which gives the brighter, hollower sound.
- **12.5%:** the zeros fall on multiples of 8, so more harmonics are present at similar strength. That spreads energy into the higher frequencies, which sounds thinner and reedier.
- **75%:** `|sin(n * pi * 0.75)|` equals `|sin(n * pi * 0.25)|` for every whole `n`, so 75% has exactly the same harmonics as 25%. The only difference is that the wave is flipped upside down, which your ear doesn't hear. That's why the two sound the same.

## Why the NES had these four values

The hardware produced the duty by stepping through an 8-step pattern of high and low bits, and only four of those patterns were built in: one high step in eight, two in eight, four in eight, and six in eight. Composers used them as timbres, and switching between them was one of the main ways to make a melody sound different from the bassline in the same game. Some games also changed the duty over time, which gives a shimmering sound.

## Duty in code

The pulse wave in our code will compute the phase, and then compare it to the duty:

```python
phase = (t * frequency) % 1.0
high = phase < duty
value = np.where(high, 1.0, -1.0)
```

The `high` array is `True` for the samples in the first part of each cycle. `np.where` turns those samples into +1 and the rest into -1.
