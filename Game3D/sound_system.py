"""Sound manager: auto-generates WAV assets if missing, then plays via Ursina Audio."""
import os, wave, struct, math
from ursina import Audio

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')

def _ensure_dir():
    os.makedirs(ASSET_DIR, exist_ok=True)

def _generate_sine_wav(path, freq=440.0, duration=0.2, volume=0.5):
    _ensure_dir()
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            sample = volume * math.sin(2 * math.pi * freq * t)
            packed = struct.pack('<h', int(sample * 32767))
            wf.writeframesraw(packed)
        wf.close()

class SoundManager:
    def __init__(self, master_volume=0.8):
        self.master_volume = master_volume
        self.sounds = {}
        self._ensure_sounds()

    def _ensure_sounds(self):
        # Map: sound_name -> (filename, freq, duration, vol_frac)
        specs = {
            'shoot'      : ('gunshot.wav',   880, 0.08, 0.4),
            'explosion'  : ('explosion.wav', 110, 0.5,  0.6),
            'hit'        : ('hit.wav',       440, 0.12, 0.3),
            'coin'       : ('coin.wav',      1200, 0.1,  0.5),
            'jump'       : ('jump.wav',      660, 0.15, 0.4),
            'footstep'   : ('footstep.wav',  100, 0.05, 0.2),
            'boss_hit'   : ('boss_hit.wav',  330, 0.25, 0.5),
            'portal'     : ('portal.wav',    660, 0.5,  0.5),
            'ambient'    : ('ambient.wav',   110, 2.0,  0.3),
            'alert'      : ('alert.wav',     1760,0.3,  0.4),
            'meteor'     : ('meteor.wav',    220, 0.4,  0.6),
            'anomaly'    : ('anomaly.wav',   880, 0.6,  0.5),
            'trader'     : ('trader.wav',    1320,0.3,  0.5),
        }
        for name, (fname, freq, dur, vol_frac) in specs.items():
            fpath = os.path.join(ASSET_DIR, fname)
            if not os.path.exists(fpath):
                _generate_sine_wav(fpath, freq=freq, duration=dur, volume=vol_frac)
            try:
                self.sounds[name] = Audio(fpath, loop=False, volume=self.master_volume)
            except Exception:
                self.sounds[name] = None

    def play(self, name):
        s = self.sounds.get(name)
        if s:
            try:
                s.volume = self.master_volume
                s.play()
            except Exception:
                pass

    def set_volume(self, vol):
        self.master_volume = max(0.0, min(1.0, vol))
        for s in self.sounds.values():
            if s:
                try:
                    s.volume = self.master_volume
                except Exception:
                    pass
