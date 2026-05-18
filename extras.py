from typing import Any
import numpy as np
from scipy.interpolate import make_interp_spline
import copy

frameRate = 48000
frameBits = 32
frameMax = 2**frameBits / 2 - 1
bufferSize = 2048*2

class Time:
    def __init__(self, start_seconds: float = 0, start_pcm_frames: int = 0):
        global frameRate
        self._time = int(start_seconds * frameRate) + start_pcm_frames
    def __call__(self, *args, **kwds):
        return self.seconds()
    def seconds(self):
        global frameRate
        return self._time / frameRate
    def pcm_frames(self):
        return self._time
    def increment(self, step: int = 1):
        self._time += step

class BasicInterpolator:
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

class AudioInterpolator:
    def __init__(self, data: list, input_framerate: int = frameRate) -> None:
        self.processed_data = None
        self.frame_rate = input_framerate
        seconds_length = len(data) / self.frame_rate
        self.seconds = seconds_length
        self.data = copy.copy(data)
    def stretch_or_squish(self, factor: float):
        self.seconds *= factor
    def stretch_or_squish_to_length(self, seconds_length: float):
        self.seconds = seconds_length
    def get(self) -> Any:
        if self.processed_data != None:
            return self.processed_data
        else:
            x = np.arange(0, self.seconds, self.seconds / len(self.data))
            spline = make_interp_spline(x, self.data, k=1)
            self.processed_data = spline(np.arange(0, self.seconds, 1 / frameRate)).astype(int).tolist()
            return self.processed_data
    def clear(self):
        self.processed_data = None

class AudioData:
    def __init__(self, data: bytes, frame_width: int, multiply_by: int = 1) -> None:
        native_data = []
        i = 0
        while i * frame_width/8 < len(data):
            raw_frame = int.from_bytes(data[i * frame_width // 8 : (i+1) * frame_width // 8], 'little', signed=True)
            native_data.append(int(raw_frame // 2**(frame_width-frameBits)) * multiply_by)
            i += 1
        self.data = native_data
    def read(self):
        return self.data

def safe_division(a: float, b: float):
    if(b == 0):
        return 0
    else:
        return a / b
def map(x: int, in_min: int, in_max: int, out_min: int, out_max: int):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)