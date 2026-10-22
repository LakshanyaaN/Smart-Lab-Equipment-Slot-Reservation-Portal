"""Tiny procedural sound effects (no audio files needed).

Tones are synthesised at start-up and played through pygame.mixer.
If no audio device is available the game keeps running silently.
"""
import array
import math

import pygame


class SoundManager:
    RATE = 22050

    def __init__(self):
        self.sounds = {}
        self.enabled = False
        try:
            # Re-init the mixer in a known format: 16-bit signed, mono.
            pygame.mixer.quit()
            pygame.mixer.init(frequency=self.RATE, size=-16, channels=1)
            rate, _fmt, self.channels = pygame.mixer.get_init()
            self.rate = rate
            self._build_sounds()
            self.enabled = True
        except Exception as exc:  # no audio device, etc.
            print("Sound disabled:", exc)

    # ---- synthesis -------------------------------------------------
    def _tone(self, f_start, f_end, duration, volume=0.35, wave="sine"):
        """One tone that glides from f_start to f_end Hz."""
        n = int(self.rate * duration)
        attack = max(1, int(0.01 * self.rate))
        samples = array.array("h")
        phase = 0.0
        for i in range(n):
            t = i / n
            phase += 2 * math.pi * (f_start + (f_end - f_start) * t) / self.rate
            s = math.sin(phase)
            if wave == "square":
                s = 1.0 if s >= 0 else -1.0
            envelope = min(1.0, i / attack) * (1.0 - t)   # fade in/out
            samples.append(int(s * envelope * volume * 32767))
        return samples

    def _make(self, *tones):
        mono = array.array("h")
        for tone in tones:
            mono.extend(tone)
        data = array.array("h")
        for s in mono:                      # duplicate for stereo mixers
            data.extend([s] * self.channels)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _build_sounds(self):
        # Jump: quick upward "boing"
        self.sounds["jump"] = self._make(self._tone(300, 650, 0.15))
        # Goal: rising C-E-G-C arpeggio
        self.sounds["goal"] = self._make(
            self._tone(523, 523, 0.09),
            self._tone(659, 659, 0.09),
            self._tone(784, 784, 0.09),
            self._tone(1047, 1047, 0.22),
        )
        # Death: long descending buzz
        self.sounds["die"] = self._make(
            self._tone(440, 90, 0.55, volume=0.3, wave="square"))

    # ---- playback --------------------------------------------------
    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except pygame.error:
                pass