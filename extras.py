from typing import Any

sampleRate = 48000
sampleBits = 32
sampleMax = 2**sampleBits / 2 - 1

class Time:
    def __init__(self, start_seconds: float = 0, start_pcm_frames: int = 0):
        global sampleRate
        self._time = int(start_seconds * sampleRate) + start_pcm_frames
    def __call__(self, *args, **kwds):
        return self.seconds()
    def seconds(self):
        global sampleRate
        return self._time / sampleRate
    def pcm_frames(self):
        return self._time
    def increment(self, step = 1):
        self._time += step

class LinearInterpolator:
    def __init__(self, start_value: int, end_value: int, frames: int) -> None:
        self.start = start_value
        self.end = end_value
        self.frames = frames
    
    def __call__(self, x: int) -> Any:
        if self.start <= 0 and self.end <= 0:
            return self.interpolate_same_polarity(x)
        elif self.start > 0:
            return self.interpolate_positive_to_negative(x)
        else:
            return self.interpolate_negative_to_positive(x)
    
    def easeInSine(self, x: float):
        from math import cos, pi
        return 1 - cos((x * pi) / 2)
    def easeOutSine(self, x: float):
        from math import sin, pi
        return sin((x * pi) / 2)
    
    def interpolate_same_polarity(self, x: int):
        diff = self.end - self.start
        return self.start + int(x / self.frames * diff)
    def interpolate_positive_to_negative(self, x: int):
        diff = self.end - self.start
        return self.start + int(self.easeInSine(x/self.frames) * diff)
    def interpolate_negative_to_positive(self, x: int):
        diff = self.end - self.start
        return self.start + int(self.easeOutSine(x/self.frames) * diff)

def mod_or_one(a, b):
    if a == b*2:
        return sampleRate
    else:
        return a % (b*2)
def safe_division(a: float, b: float):
    if(b == 0):
        return 0
    else:
        return a / b