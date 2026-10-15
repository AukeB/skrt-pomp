# NES sound

The Nintendo Entertainment System made its music and effects with a sound chip called the 2A03 (the RP2A03 in NTSC consoles), which is built into the same chip as the processor. It has five sound channels. Each one is a simple circuit that produces one kind of sound, and the composer's job was to combine them within the limits of the hardware. This document explains each channel and how the output is mixed, so the `waveform` module can imitate it.

## The five channels

| Channel | Produces | Controls |
|---------|----------|----------|
| Pulse 1 | Square-like tones | Pitch, duty cycle, volume envelope, pitch sweep |
| Pulse 2 | Square-like tones | Same as Pulse 1 |
| Triangle | Soft, flute-like tones | Pitch only, fixed volume |
| Noise | Hiss, crashes, drums | Period, mode, volume envelope |
| DPCM | Recorded samples | Sample address, length, rate |

Pulse 1 and Pulse 2 are nearly identical, so composers used them for melody and harmony. The triangle usually carried the bassline, and noise and DPCM handled percussion and effects.

## Clock and pitch

Every channel is driven by a timer, and the timer is counted down by the CPU clock. On NTSC consoles that clock runs at about 1.79 MHz. A channel's timer has a period value, and the output frequency follows from it:

- **Pulse:** `frequency = CPU / (16 * (period + 1))`
- **Triangle:** `frequency = CPU / (32 * (period + 1))`

The period is an 11-bit number, so the pulse and triangle timers can take values from 0 to 2047. This is why the chip can only play a limited set of frequencies: the note has to fall on a whole-number period, so the pitch is slightly off for many notes. Composers accepted that, and some games tuned their notes by hand to hide it.

## Pulse channels

Each pulse channel is a square wave with the four duty values described in [waveform.md](waveform.md). The channel has three extra features:

- **Volume envelope.** Each channel has a 4-bit volume, from 0 to 15. The envelope can hold the volume at a fixed level or decay it slowly over time. This gave notes a natural start and fade, which is why many NES melodies sound plucked or punchy.
- **Length counter.** A note can be set to end after a fixed time, which avoids having to silence the channel by hand.
- **Sweep unit.** The sweep changes the period over time, so the pitch slides up or down. It's used for laser sounds, falls, and the bends in some melodies. Both pulse channels have one. The only difference is how a downward sweep is calculated: Pulse 1 subtracts one more than Pulse 2 does, so the same settings drop slightly further on Pulse 1.

## Triangle channel

The triangle does not produce a square or sawtooth. It steps through a 32-step pattern that rises in a straight line from the lowest value to the highest and back down. That makes a soft, rounded sound with few harmonics, close to a sine wave.

The triangle has no volume control. It is either on or off, and when it is off the output holds at its last level. Composers used it for bass, where the lack of harmonics keeps the low notes clear, and for melodies that needed a softer sound.

## Noise channel

The noise channel makes its sound with a 15-bit linear-feedback shift register (LFSR). An LFSR is a small circuit that shifts bits along and feeds some of them back into the start, producing a sequence that looks random but repeats after a fixed number of steps.

- **Long mode** repeats after 32,767 steps. It sounds like white noise, the hiss you get from a radio between stations, and it is used for crashes and broad percussion.
- **Short mode** repeats after 93 steps (NTSC). The short cycle is heard as a buzzy, metallic tone with a clear pitch. It is used for metallic hits and some bass effects.

The period of the noise is chosen from a table of 16 values, so the composer picks how fast the shift register runs. A lower period gives a higher, brighter hiss.

## DPCM channel

The DPCM channel plays back recorded samples. Its name stands for delta pulse-code modulation: the sample is stored as a series of up or down steps, and the channel adds or subtracts one step at a time to a 7-bit output level. This is slower and lower quality than full PCM, but it fits in very little memory.

Games used DPCM for drum samples, voice clips, and bass drum thumps. Because the samples had to fit in the cartridge, developers stored them compactly and shared them between songs.

## Frame counter

The envelopes, the sweep, and the length counters are not updated on every CPU cycle. A frame counter runs at 240 Hz and steps these units at a few fixed points within each video frame, which is about 60 Hz. This is why the envelope decays at a steady rate and why note lengths are multiples of a frame.

## Mixing

The five channels are added together, but not in a straight line. The mixer is nonlinear, so the total output is not a simple sum of the channel levels. The pulse channels are combined in one formula and the triangle, noise, and DPCM in another. Each combination has a limit: adding more of a channel gives less extra volume than the last one did. This is one reason NES mixes sound distinctive, since loud channels can push the others down.

## What this means for our code

- The pulse wave with its four duty values is a direct copy of Pulse 1 and Pulse 2.
- The triangle is a 32-step rising and falling wave, not an analog triangle.
- The noise channel can use the LFSR directly, with the short and long modes.
- The envelope and the sweep are per-note behaviour and belong in the note or track layer, not in the basic waveform functions.
- Mixing is a separate step from waveform generation, which matches how the planned renderer will work.
