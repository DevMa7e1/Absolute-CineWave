from numpy.fft import fft, ifft
from audio_functions import limit

class EQ:
    def __init__(self, wave: list) -> None:
       self.wave = wave 
    def apply_eq(self, start_freq: int, end_freq: int, amplitude: float):
        X = fft(self.wave)
        for i in range(start_freq//2, end_freq//2):
            X[i] *= amplitude
        self.wave = ifft(X).real.tolist()
        for i in range(len(self.wave)):
            self.wave[i] = limit(int(self.wave[i]), 1)
    def __call__(self) -> list:
        return self.wave