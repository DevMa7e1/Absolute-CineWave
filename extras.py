sampleRate = 48000
sampleBits = 16
sampleMax = 2**sampleBits / 2 - 1

wave = []

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